"""
Gmail Watcher - Email Monitoring Service
Monitors Gmail inbox and creates action files for new emails
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import load_dotenv
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from base_watcher import BaseWatcher


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail inbox for new emails and creates action files.

    Features:
    - Detects new emails within 5 minutes
    - Priority detection (URGENT, ASAP, IMPORTANT)
    - Duplicate prevention
    - Attachment metadata extraction
    - Error handling with retry logic
    """

    def __init__(self, vault_path: str, check_interval: int = 300):
        """
        Initialize Gmail Watcher.

        Args:
            vault_path: Path to Obsidian vault
            check_interval: Check interval in seconds (default: 300 = 5 minutes)
        """
        super().__init__(vault_path, check_interval)

        # Load configuration
        self.config = self._load_config()
        self.processed_emails_file = Path(vault_path) / '.state' / 'processed_emails.json'
        self.processed_emails = self._load_processed_emails()

        # Gmail service (initialized on first use)
        self.service = None

        self.logger.info("Gmail Watcher initialized")

    def _load_config(self) -> dict:
        """Load Gmail configuration from config file."""
        config_path = Path(__file__).parent.parent.parent / 'config' / 'gmail_config.json'

        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                'gmail_watcher': {
                    'check_interval_seconds': 300,
                    'max_emails_per_check': 100,
                    'priority_keywords': {
                        'urgent': ['URGENT', 'ASAP', 'CRITICAL', 'EMERGENCY'],
                        'low': ['FYI', 'No rush', 'When you have time']
                    }
                }
            }

    def _load_processed_emails(self) -> set:
        """Load set of already processed email IDs."""
        if self.processed_emails_file.exists():
            try:
                with open(self.processed_emails_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('processed_email_ids', []))
            except Exception as e:
                self.logger.error(f"Error loading processed emails: {e}")
                return set()
        return set()

    def _save_processed_emails(self):
        """Save processed email IDs to file."""
        try:
            data = {
                'last_updated': datetime.utcnow().isoformat() + 'Z',
                'processed_email_ids': list(self.processed_emails)
            }
            with open(self.processed_emails_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving processed emails: {e}")

    def _get_gmail_service(self):
        """
        Get or create Gmail API service.

        Returns:
            Gmail API service object
        """
        if self.service:
            return self.service

        try:
            # Load credentials from token.json
            token_file = Path(__file__).parent.parent.parent / 'token.json'

            if not token_file.exists():
                self.logger.error("token.json not found. Run: python AI_Employee_Vault/setup/gmail_auth.py")
                return None

            creds = Credentials.from_authorized_user_file(
                str(token_file),
                ['https://www.googleapis.com/auth/gmail.readonly']
            )

            # Refresh if expired
            if creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
                token_file.write_text(creds.to_json())
                self.logger.info("Refreshed expired Gmail token")

            # Build service
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info("Gmail service initialized")
            return self.service

        except Exception as e:
            self.logger.error(f"Error initializing Gmail service: {e}")
            return None

    def check_for_updates(self):
        """
        Check Gmail inbox for new emails.
        Creates action files for unprocessed emails.
        """
        self.logger.info("Checking for new emails...")

        service = self._get_gmail_service()
        if not service:
            self.logger.error("Gmail service not available")
            return

        try:
            # Get unread messages
            config = self.config.get('gmail_watcher', {})
            max_results = config.get('max_emails_per_check', 100)

            results = service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                self.logger.info("No new emails found")
                return

            self.logger.info(f"Found {len(messages)} unread emails")

            # Process each message
            new_emails = 0
            for message in messages:
                email_id = message['id']

                # Skip if already processed
                if email_id in self.processed_emails:
                    continue

                # Get full message details
                msg = service.users().messages().get(
                    userId='me',
                    id=email_id,
                    format='full'
                ).execute()

                # Extract email data
                email_data = self._extract_email_data(msg)

                # Create action file
                self.create_action_file(email_data)

                # Mark as processed
                self.processed_emails.add(email_id)
                new_emails += 1

            # Save processed emails
            if new_emails > 0:
                self._save_processed_emails()
                self.logger.info(f"Created {new_emails} new action files")

        except HttpError as e:
            if e.resp.status == 401:
                self.logger.error("Authentication failed. Run: python AI_Employee_Vault/setup/gmail_auth.py --refresh")
            elif e.resp.status == 429:
                self.logger.warning("Rate limit hit. Backing off...")
                # Exponential backoff handled by base class
            else:
                self.logger.error(f"Gmail API error: {e}")
        except Exception as e:
            self.handle_error(e, "Error checking for emails")

    def _extract_email_data(self, message: dict) -> dict:
        """
        Extract relevant data from Gmail message.

        Args:
            message: Gmail message object

        Returns:
            Dictionary with email data
        """
        headers = {h['name']: h['value'] for h in message['payload']['headers']}

        # Extract basic info
        email_id = message['id']
        sender = headers.get('From', 'Unknown')
        subject = headers.get('Subject', 'No Subject')
        date = headers.get('Date', '')

        # Extract body preview
        snippet = message.get('snippet', '')

        # Extract attachments
        attachments = []
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part.get('filename'):
                    attachments.append({
                        'filename': part['filename'],
                        'mime_type': part.get('mimeType', 'unknown'),
                        'size': part.get('body', {}).get('size', 0)
                    })

        # Detect priority
        priority = self._detect_priority(subject, snippet)

        return {
            'email_id': email_id,
            'sender': sender,
            'subject': subject,
            'date': date,
            'body_preview': snippet,
            'attachments': attachments,
            'priority': priority,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }

    def _detect_priority(self, subject: str, body: str) -> str:
        """
        Detect email priority based on keywords.

        Args:
            subject: Email subject
            body: Email body preview

        Returns:
            Priority level: 'urgent', 'normal', or 'low'
        """
        config = self.config.get('gmail_watcher', {})
        keywords = config.get('priority_keywords', {})

        text = (subject + ' ' + body).upper()

        # Check for urgent keywords
        urgent_keywords = keywords.get('urgent', [])
        for keyword in urgent_keywords:
            if keyword.upper() in text:
                return 'urgent'

        # Check for low priority keywords
        low_keywords = keywords.get('low', [])
        for keyword in low_keywords:
            if keyword.upper() in text:
                return 'low'

        return 'normal'

    def create_action_file(self, data: dict) -> Path:
        """
        Create action file for email in Needs_Action folder.

        Args:
            data: Email data dictionary

        Returns:
            Path to created action file
        """
        email_id = data['email_id']
        subject = data['subject']

        # Create filename
        safe_subject = "".join(c for c in subject if c.isalnum() or c in (' ', '-', '_'))[:50]
        filename = f"email-{email_id[:8]}-{safe_subject}.md"
        file_path = self.needs_action / filename

        # Build frontmatter
        frontmatter = {
            'entity_type': 'email_action',
            'email_id': data['email_id'],
            'sender': data['sender'],
            'subject': data['subject'],
            'priority': data['priority'],
            'timestamp': data['timestamp'],
            'processed_status': 'pending'
        }

        if data['attachments']:
            frontmatter['attachments'] = [
                {
                    'filename': att['filename'],
                    'size': att['size'],
                    'mime_type': att['mime_type']
                }
                for att in data['attachments']
            ]

        # Build body
        priority_emoji = {
            'urgent': '🔴',
            'normal': '🟡',
            'low': '🟢'
        }

        body = f"""
# Email Action: {data['subject']}

**From**: {data['sender']}
**Received**: {data['date']}
**Priority**: {priority_emoji.get(data['priority'], '🟡')} {data['priority'].capitalize()}

## Body Preview
{data['body_preview']}

## Attachments
"""

        if data['attachments']:
            for att in data['attachments']:
                size_mb = att['size'] / (1024 * 1024)
                body += f"- {att['filename']} ({size_mb:.2f} MB)\n"
        else:
            body += "None\n"

        body += """
## Suggested Actions
1. Review email content
2. Draft response if needed
3. Mark as processed when complete
"""

        # Create file
        self.create_markdown_file(file_path, frontmatter, body)

        return file_path


def main():
    """Main entry point for Gmail Watcher."""
    import sys

    # Get vault path from command line or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent

    # Create and run watcher
    watcher = GmailWatcher(str(vault_path))

    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\nGmail Watcher stopped by user")


if __name__ == '__main__':
    main()
