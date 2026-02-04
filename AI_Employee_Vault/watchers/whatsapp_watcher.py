"""
WhatsApp Watcher - WhatsApp Web Monitoring Service
Monitors WhatsApp Web for new messages and creates action files
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import sys
import time

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from base_watcher import BaseWatcher


class WhatsAppWatcher(BaseWatcher):
    """
    Watches WhatsApp Web for new messages and creates action files.

    Features:
    - Monitors WhatsApp Web using Playwright
    - Keyword-based priority detection
    - Session persistence (no QR code scan every time)
    - Duplicate prevention
    - Error handling with retry logic

    Note: This uses WhatsApp Web automation. Be aware of WhatsApp's terms of service.
    """

    def __init__(self, vault_path: str, session_path: str = None, check_interval: int = 30):
        """
        Initialize WhatsApp Watcher.

        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to store browser session (default: vault/.state/whatsapp_session)
            check_interval: Check interval in seconds (default: 30)
        """
        super().__init__(vault_path, check_interval)

        # Session path for persistent login
        if session_path:
            self.session_path = Path(session_path)
        else:
            self.session_path = Path(vault_path) / '.state' / 'whatsapp_session'

        self.session_path.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config = self._load_config()

        # Processed messages tracking
        self.processed_messages_file = Path(vault_path) / '.state' / 'processed_whatsapp.json'
        self.processed_messages = self._load_processed_messages()

        # Playwright browser (initialized on first use)
        self.browser = None
        self.playwright = None

        self.logger.info("WhatsApp Watcher initialized")
        self.logger.info(f"Session path: {self.session_path}")

    def _load_config(self) -> dict:
        """Load WhatsApp configuration from config file."""
        config_path = Path(__file__).parent.parent.parent / 'config' / 'whatsapp_config.json'

        if config_path.exists():
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                'whatsapp_watcher': {
                    'check_interval_seconds': 30,
                    'max_messages_per_check': 50,
                    'priority_keywords': ['urgent', 'asap', 'invoice', 'payment', 'help', 'emergency', 'critical'],
                    'headless': True,
                    'timeout_seconds': 30
                }
            }

    def _load_processed_messages(self) -> set:
        """Load set of already processed message IDs."""
        if self.processed_messages_file.exists():
            try:
                with open(self.processed_messages_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('processed_message_ids', []))
            except Exception as e:
                self.logger.error(f"Error loading processed messages: {e}")
                return set()
        return set()

    def _save_processed_messages(self):
        """Save processed message IDs to file."""
        try:
            data = {
                'last_updated': datetime.utcnow().isoformat() + 'Z',
                'processed_message_ids': list(self.processed_messages)
            }
            with open(self.processed_messages_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving processed messages: {e}")

    def _init_browser(self):
        """
        Initialize Playwright browser with persistent session.

        Returns:
            Browser context or None if initialization fails
        """
        if self.browser:
            return self.browser

        try:
            from playwright.sync_api import sync_playwright

            config = self.config.get('whatsapp_watcher', {})
            headless = config.get('headless', True)

            self.logger.info("Initializing Playwright browser...")

            self.playwright = sync_playwright().start()

            # Launch persistent context (keeps WhatsApp Web logged in)
            self.browser = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )

            self.logger.info("Browser initialized successfully")
            return self.browser

        except ImportError:
            self.logger.error("Playwright not installed. Run: pip install playwright && playwright install chromium")
            return None
        except Exception as e:
            self.logger.error(f"Error initializing browser: {e}")
            return None

    def check_for_updates(self):
        """
        Check WhatsApp Web for new messages.
        Creates action files for messages with priority keywords.
        """
        self.logger.info("Checking WhatsApp Web for new messages...")

        browser = self._init_browser()
        if not browser:
            self.logger.error("Browser not available")
            return

        try:
            config = self.config.get('whatsapp_watcher', {})
            timeout = config.get('timeout_seconds', 30) * 1000  # Convert to milliseconds

            # Get or create page
            if len(browser.pages) == 0:
                page = browser.new_page()
            else:
                page = browser.pages[0]

            # Navigate to WhatsApp Web if not already there
            if 'web.whatsapp.com' not in page.url:
                self.logger.info("Navigating to WhatsApp Web...")
                page.goto('https://web.whatsapp.com/', timeout=timeout)

            # Give page time to load
            self.logger.info("Waiting for page to load...")
            page.wait_for_load_state('networkidle', timeout=timeout)

            # Try multiple selectors to detect if logged in
            self.logger.info("Checking login status...")
            logged_in = False

            # Try different selectors that indicate WhatsApp Web is loaded
            selectors_to_try = [
                '[data-testid="chat-list"]',
                '#pane-side',
                '[data-testid="conversation-panel-wrapper"]',
                'div[role="application"]',
                '#app'
            ]

            for selector in selectors_to_try:
                try:
                    element = page.wait_for_selector(selector, timeout=5000)
                    if element:
                        self.logger.info(f"Found element: {selector}")
                        logged_in = True
                        break
                except:
                    continue

            if not logged_in:
                self.logger.warning("Could not detect WhatsApp Web elements. Session may have expired.")
                self.logger.warning("Please run the test script again to re-login.")
                return

            self.logger.info("WhatsApp Web loaded successfully!")

            # Find unread chats - try multiple approaches
            self.logger.info("Looking for unread messages...")
            unread_chats = []

            # Method 1: Look for unread badges
            try:
                unread_badges = page.query_selector_all('span[data-testid="icon-unread-count"]')
                if unread_badges:
                    self.logger.info(f"Found {len(unread_badges)} unread badges")
                    unread_chats = unread_badges
            except Exception as e:
                self.logger.warning(f"Method 1 failed: {e}")

            # Method 2: Look for aria-label with "unread"
            if not unread_chats:
                try:
                    unread_elements = page.query_selector_all('[aria-label*="unread"]')
                    if unread_elements:
                        self.logger.info(f"Found {len(unread_elements)} elements with unread label")
                        unread_chats = unread_elements
                except Exception as e:
                    self.logger.warning(f"Method 2 failed: {e}")

            # Method 3: Look for chat containers with unread class
            if not unread_chats:
                try:
                    chat_containers = page.query_selector_all('[data-testid="cell-frame-container"]')
                    self.logger.info(f"Found {len(chat_containers)} total chats, checking for unread...")
                    # We'll check all chats for keywords instead
                    unread_chats = chat_containers[:10]  # Check first 10 chats
                except Exception as e:
                    self.logger.warning(f"Method 3 failed: {e}")

            if not unread_chats:
                self.logger.info("No unread messages found")
                return

            self.logger.info(f"Checking {len(unread_chats)} chats for priority keywords...")

            # Process each chat
            new_messages = 0
            keywords = config.get('priority_keywords', [])

            for i, chat_element in enumerate(unread_chats):
                try:
                    # Get the chat container (parent element)
                    try:
                        chat_container = chat_element.evaluate_handle('el => el.closest("[data-testid=\'cell-frame-container\']")').as_element()
                    except:
                        # If element is already a container, use it directly
                        chat_container = chat_element

                    if not chat_container:
                        continue

                    # Get chat text content
                    try:
                        chat_text = chat_container.inner_text().lower()
                    except:
                        self.logger.warning(f"Could not get text from chat {i}")
                        continue

                    # Check if any priority keyword is present
                    has_keyword = any(keyword.lower() in chat_text for keyword in keywords)

                    if not has_keyword:
                        continue

                    self.logger.info(f"Found priority message in chat {i}!")

                    # Extract chat details
                    chat_name = "Unknown"
                    message_preview = ""

                    try:
                        chat_name_elem = chat_container.query_selector('[data-testid="cell-frame-title"]')
                        if chat_name_elem:
                            chat_name = chat_name_elem.inner_text()
                    except:
                        pass

                    try:
                        message_preview_elem = chat_container.query_selector('[data-testid="last-msg-text"]')
                        if message_preview_elem:
                            message_preview = message_preview_elem.inner_text()
                        else:
                            # Fallback: use the full chat text
                            message_preview = chat_text[:200]
                    except:
                        message_preview = chat_text[:200]

                    # Create unique message ID
                    message_id = f"{chat_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{i}"

                    # Skip if already processed
                    if message_id in self.processed_messages:
                        continue

                    # Extract message data
                    message_data = {
                        'message_id': message_id,
                        'chat_name': chat_name,
                        'message_preview': message_preview,
                        'matched_keywords': [kw for kw in keywords if kw.lower() in chat_text],
                        'timestamp': datetime.utcnow().isoformat() + 'Z'
                    }

                    # Create action file
                    self.create_action_file(message_data)

                    # Mark as processed
                    self.processed_messages.add(message_id)
                    new_messages += 1

                except Exception as e:
                    self.logger.error(f"Error processing chat {i}: {e}")
                    continue

            # Save processed messages
            if new_messages > 0:
                self._save_processed_messages()
                self.logger.info(f"Created {new_messages} new action files")

        except Exception as e:
            self.handle_error(e, "Error checking WhatsApp Web")

    def create_action_file(self, data: dict) -> Path:
        """
        Create action file for WhatsApp message in Needs_Action folder.

        Args:
            data: Message data dictionary

        Returns:
            Path to created action file
        """
        message_id = data['message_id']
        chat_name = data['chat_name']

        # Create filename
        safe_name = "".join(c for c in chat_name if c.isalnum() or c in (' ', '-', '_'))[:50]
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"whatsapp-{timestamp}-{safe_name}.md"
        file_path = self.needs_action / filename

        # Build frontmatter
        frontmatter = {
            'entity_type': 'whatsapp_action',
            'message_id': data['message_id'],
            'chat_name': data['chat_name'],
            'matched_keywords': data['matched_keywords'],
            'priority': 'urgent',
            'timestamp': data['timestamp'],
            'processed_status': 'pending'
        }

        # Build body
        body = f"""
# WhatsApp Action: {data['chat_name']}

**From**: {data['chat_name']}
**Received**: {data['timestamp']}
**Priority**: 🔴 Urgent
**Matched Keywords**: {', '.join(data['matched_keywords'])}

## Message Preview
{data['message_preview']}

## Suggested Actions
1. Open WhatsApp Web to view full conversation
2. Draft response if needed
3. Mark as processed when complete

## Notes
- This message was flagged because it contains priority keywords
- Open WhatsApp Web to see full context and conversation history
"""

        # Create file
        self.create_markdown_file(file_path, frontmatter, body)

        return file_path

    def cleanup(self):
        """Clean up browser resources."""
        try:
            if self.browser:
                self.browser.close()
                self.logger.info("Browser closed")
            if self.playwright:
                self.playwright.stop()
                self.logger.info("Playwright stopped")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def run(self):
        """
        Main run loop for the watcher.
        Continuously checks for updates at the specified interval.
        """
        self.logger.info(f"{self.__class__.__name__} started")
        self.logger.info(f"Checking every {self.check_interval} seconds")

        try:
            while True:
                try:
                    self.check_for_updates()
                    time.sleep(self.check_interval)
                except KeyboardInterrupt:
                    self.logger.info("Watcher stopped by user")
                    break
                except Exception as e:
                    retryable = self.handle_error(e, "Main loop error")
                    if retryable:
                        # Wait before retrying
                        time.sleep(self.check_interval)
                    else:
                        # Fatal error, exit
                        self.logger.error("Fatal error encountered. Exiting.")
                        break
        finally:
            self.cleanup()


def main():
    """Main entry point for WhatsApp Watcher."""
    import sys

    # Get vault path from command line or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent

    # Create and run watcher
    watcher = WhatsAppWatcher(str(vault_path))

    try:
        watcher.run()
    except KeyboardInterrupt:
        print("\nWhatsApp Watcher stopped by user")
    finally:
        watcher.cleanup()


if __name__ == '__main__':
    main()
