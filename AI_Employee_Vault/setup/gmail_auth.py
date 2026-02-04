"""
Gmail OAuth2 Authentication Setup
Handles OAuth2 flow for Gmail API access
"""

import os
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv, set_key

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def setup_gmail_auth():
    """
    Set up Gmail OAuth2 authentication.

    This function:
    1. Checks for existing credentials
    2. Runs OAuth2 flow if needed
    3. Saves refresh token to .env file

    Returns:
        Credentials object
    """
    print("=" * 60)
    print("Gmail API OAuth2 Setup")
    print("=" * 60)

    # Load environment variables
    env_path = Path(__file__).parent.parent.parent / 'config' / '.env'
    load_dotenv(env_path)

    creds = None
    token_file = Path(__file__).parent.parent.parent / 'token.json'

    # Check if we have existing credentials
    if token_file.exists():
        print("\n[OK] Found existing token.json")
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    # If credentials are invalid or don't exist, run OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("\n[INFO] Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("\n[WARN] No valid credentials found. Starting OAuth flow...")

            # Check for credentials.json
            creds_file = Path(__file__).parent.parent.parent / 'credentials.json'
            if not creds_file.exists():
                print("\n[ERROR] credentials.json not found!")
                print("\nPlease follow these steps:")
                print("1. Go to https://console.cloud.google.com")
                print("2. Create a new project or select existing")
                print("3. Enable Gmail API")
                print("4. Create OAuth 2.0 credentials (Desktop app)")
                print("5. Download credentials.json to project root")
                return None

            # Run OAuth flow with local server
            print("\n[INFO] Starting OAuth flow...")
            print("[INFO] Your browser will open automatically...")
            print("[INFO] If browser doesn't open, copy the URL from above and paste in browser")

            flow = InstalledAppFlow.from_client_secrets_file(
                str(creds_file), SCOPES
            )

            # Use local server (works with Desktop app credentials)
            creds = flow.run_local_server(port=0)  # port=0 means use any available port

            print("\n[OK] OAuth flow completed successfully!")

        # Save credentials for next run
        token_file.write_text(creds.to_json())
        print(f"[OK] Saved credentials to {token_file}")

    # Extract credentials for .env
    if creds:
        # Parse credentials
        creds_data = json.loads(creds.to_json())

        # Update .env file
        if env_path.exists():
            print("\n[INFO] Updating config/.env with credentials...")
            set_key(str(env_path), 'GMAIL_REFRESH_TOKEN', creds_data.get('refresh_token', ''))
            set_key(str(env_path), 'GMAIL_CLIENT_ID', creds_data.get('client_id', ''))
            set_key(str(env_path), 'GMAIL_CLIENT_SECRET', creds_data.get('client_secret', ''))
            print("[OK] Updated config/.env")
        else:
            print("\n[WARN] Warning: config/.env not found. Please create it from .env.template")

    print("\n" + "=" * 60)
    print("Gmail OAuth2 Setup Complete!")
    print("=" * 60)
    print("\nYou can now use the Gmail Watcher.")
    print("Run: python AI_Employee_Vault/watchers/gmail_watcher.py")

    return creds


def refresh_gmail_token():
    """
    Refresh an expired Gmail OAuth2 token.

    Returns:
        Credentials object
    """
    print("Refreshing Gmail token...")

    token_file = Path(__file__).parent.parent.parent / 'token.json'

    if not token_file.exists():
        print("❌ No token.json found. Run setup first.")
        return None

    creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        token_file.write_text(creds.to_json())
        print("✓ Token refreshed successfully!")
        return creds
    else:
        print("❌ Token cannot be refreshed. Run setup again.")
        return None


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--refresh':
        refresh_gmail_token()
    else:
        setup_gmail_auth()
