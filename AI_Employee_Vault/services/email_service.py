"""
Email Service - Email Composition and Sending
Handles email drafting, approval workflow, and sending via MCP server
"""

import os
import json
import re
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from dotenv import load_dotenv
import logging


class EmailService:
    """
    Email service for composing and sending emails with approval workflow.

    Features:
    - Draft email composition
    - Email address validation
    - Approval workflow integration
    - MCP server communication
    - Email logging
    """

    def __init__(self, vault_path: str):
        """
        Initialize Email Service.

        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.logs = self.vault_path / 'Logs'

        # Ensure directories exist
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        self.approved.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)

        # Load configuration
        load_dotenv(Path(__file__).parent.parent.parent / 'config' / '.env')
        self.mcp_server_url = os.getenv('MCP_EMAIL_SERVER_URL', 'http://localhost:3000')

        # Setup logging
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for email service."""
        logger = logging.getLogger('EmailService')
        logger.setLevel(logging.INFO)

        log_file = self.logs / 'email_service.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        return logger

    def compose_draft_email(self, recipient: str, subject: str, body: str,
                           body_format: str = 'plain', attachments: List[Dict] = None) -> Dict:
        """
        Compose a draft email and create approval request.

        Args:
            recipient: Email address of recipient
            subject: Email subject
            body: Email body content
            body_format: 'plain' or 'html'
            attachments: List of attachment dicts with 'filename' and 'path'

        Returns:
            Dict with draft_id and draft_file_path
        """
        self.logger.info(f"Composing draft email to {recipient}")

        # Validate email address
        if not self.validate_email(recipient):
            raise ValueError(f"Invalid email address: {recipient}")

        # Validate required fields
        if not subject:
            raise ValueError("Email subject cannot be empty")
        if not body:
            raise ValueError("Email body cannot be empty")

        # Generate draft ID
        draft_id = f"draft-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # Create draft file
        draft_file = self.pending_approval / f"email-{draft_id}.md"

        # Build frontmatter
        frontmatter = {
            'entity_type': 'draft_email',
            'draft_id': draft_id,
            'recipient': recipient,
            'subject': subject,
            'body_format': body_format,
            'created_timestamp': datetime.utcnow().isoformat() + 'Z',
            'approval_status': 'pending',
            'sent_status': 'not_sent'
        }

        if attachments:
            frontmatter['attachments'] = attachments

        # Build body
        markdown_body = f"""
# Draft Email: {subject}

**To**: {recipient}
**Subject**: {subject}
**Status**: ⏳ Pending Approval

## Email Body

{body}

## Attachments
"""

        if attachments:
            for att in attachments:
                markdown_body += f"- {att['filename']} ({att.get('size', 'unknown')} bytes)\n"
        else:
            markdown_body += "None\n"

        markdown_body += """
## Approval Actions
- ✅ **Approve**: Move this file to Approved/ folder
- ❌ **Reject**: Move this file to Done/ folder with rejection reason

**Note**: Email will be sent automatically after approval.
"""

        # Write draft file
        self._create_markdown_file(draft_file, frontmatter, markdown_body)

        self.logger.info(f"Created draft email: {draft_file}")

        return {
            'draft_id': draft_id,
            'draft_file_path': str(draft_file),
            'approval_status': 'pending',
            'created_timestamp': frontmatter['created_timestamp']
        }

    def validate_email(self, email: str) -> bool:
        """
        Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        # RFC 5322 compliant regex (simplified)
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def send_email(self, draft_id: str) -> Dict:
        """
        Send an approved draft email via MCP server.

        Args:
            draft_id: Draft ID to send

        Returns:
            Dict with success status, message_id, and sent_timestamp
        """
        self.logger.info(f"Attempting to send email: {draft_id}")

        # Find draft file in Approved folder
        draft_file = self.approved / f"email-{draft_id}.md"

        if not draft_file.exists():
            raise FileNotFoundError(f"Draft not found in Approved folder: {draft_id}")

        # Parse draft file
        draft_data = self._parse_draft_file(draft_file)

        # Verify approval status
        if draft_data.get('approval_status') != 'approved':
            raise ValueError(f"Draft not approved: {draft_id}")

        # Send via MCP server
        try:
            response = self._send_via_mcp(draft_data)

            if response.get('success'):
                message_id = response.get('message_id')
                sent_timestamp = datetime.utcnow().isoformat() + 'Z'

                # Log sent email
                self._log_sent_email(draft_data, message_id, sent_timestamp)

                # Move draft to Done
                done_folder = self.vault_path / 'Done'
                done_folder.mkdir(parents=True, exist_ok=True)
                draft_file.rename(done_folder / draft_file.name)

                self.logger.info(f"Email sent successfully: {message_id}")

                return {
                    'success': True,
                    'message_id': message_id,
                    'sent_timestamp': sent_timestamp,
                    'log_file_path': str(self.logs / f"email-sent-{draft_id}.md")
                }
            else:
                error = response.get('error', 'Unknown error')
                self.logger.error(f"Failed to send email: {error}")
                return {
                    'success': False,
                    'error': error
                }

        except requests.exceptions.ConnectionError:
            self.logger.error("Cannot connect to MCP server. Is it running?")
            raise ConnectionError("MCP server not available. Start with: cd AI_Employee_Vault/mcp && npm start")
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            raise

    def _send_via_mcp(self, draft_data: Dict) -> Dict:
        """
        Send email via MCP server.

        Args:
            draft_data: Draft email data

        Returns:
            Response from MCP server
        """
        # Prepare request payload
        payload = {
            'to': draft_data['recipient'],
            'subject': draft_data['subject'],
            'body': draft_data['body'],
            'format': draft_data.get('body_format', 'plain'),
            'attachments': draft_data.get('attachments', [])
        }

        # Send request to MCP server
        response = requests.post(
            f"{self.mcp_server_url}/send-email",
            json=payload,
            timeout=30
        )

        response.raise_for_status()
        return response.json()

    def _parse_draft_file(self, file_path: Path) -> Dict:
        """
        Parse draft email file.

        Args:
            file_path: Path to draft file

        Returns:
            Dict with draft data
        """
        content = file_path.read_text(encoding='utf-8')

        # Extract frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1]
                body_text = parts[2].strip()

                # Parse YAML frontmatter (simple parsing)
                frontmatter = {}
                for line in frontmatter_text.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip()

                # Extract email body from markdown
                # Look for "## Email Body" section
                if '## Email Body' in body_text:
                    body_parts = body_text.split('## Email Body', 1)[1]
                    body_parts = body_parts.split('##', 1)[0].strip()
                    frontmatter['body'] = body_parts

                return frontmatter

        raise ValueError(f"Invalid draft file format: {file_path}")

    def _log_sent_email(self, draft_data: Dict, message_id: str, sent_timestamp: str):
        """
        Log sent email to Logs folder.

        Args:
            draft_data: Draft email data
            message_id: SMTP message ID
            sent_timestamp: When email was sent
        """
        log_file = self.logs / f"email-sent-{draft_data['draft_id']}.md"

        frontmatter = {
            'entity_type': 'sent_email_log',
            'draft_id': draft_data['draft_id'],
            'message_id': message_id,
            'recipient': draft_data['recipient'],
            'subject': draft_data['subject'],
            'sent_timestamp': sent_timestamp,
            'approved_by': 'user',
            'approval_timestamp': draft_data.get('approval_timestamp', sent_timestamp)
        }

        body = f"""
# Sent Email Log: {draft_data['subject']}

**To**: {draft_data['recipient']}
**Sent**: {sent_timestamp}
**Message ID**: {message_id}
**Status**: ✅ Sent Successfully

## Email Body
{draft_data.get('body', '[Body not available]')}

## Delivery Status
- Sent via: Gmail SMTP
- Authentication: OAuth2
- Delivery: Successful
"""

        self._create_markdown_file(log_file, frontmatter, body)

    def _create_markdown_file(self, file_path: Path, frontmatter: Dict, body: str):
        """
        Create a Markdown file with YAML frontmatter.

        Args:
            file_path: Path where file should be created
            frontmatter: Dictionary of frontmatter data
            body: Markdown body content
        """
        # Convert frontmatter to YAML
        yaml_lines = ['---']
        for key, value in frontmatter.items():
            if isinstance(value, list):
                yaml_lines.append(f'{key}:')
                for item in value:
                    if isinstance(item, dict):
                        yaml_lines.append(f'  -')
                        for k, v in item.items():
                            yaml_lines.append(f'    {k}: {v}')
                    else:
                        yaml_lines.append(f'  - {item}')
            elif isinstance(value, dict):
                yaml_lines.append(f'{key}:')
                for k, v in value.items():
                    yaml_lines.append(f'  {k}: {v}')
            else:
                yaml_lines.append(f'{key}: {value}')
        yaml_lines.append('---')
        yaml_lines.append('')

        # Combine frontmatter and body
        content = '\n'.join(yaml_lines) + body

        # Write file
        file_path.write_text(content, encoding='utf-8')


# Example usage
if __name__ == '__main__':
    import sys

    # Get vault path
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent

    # Create service
    service = EmailService(str(vault_path))

    # Example: Compose draft email
    draft = service.compose_draft_email(
        recipient='example@example.com',
        subject='Test Email',
        body='This is a test email from the AI Employee.',
        body_format='plain'
    )

    print(f"Draft created: {draft['draft_file_path']}")
    print("Move to Approved/ folder to send")
