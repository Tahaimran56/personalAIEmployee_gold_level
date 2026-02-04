"""
LinkedIn OAuth2 Authentication Setup
Handles OAuth2 flow for LinkedIn API access
"""

import os
import webbrowser
from pathlib import Path
from urllib.parse import urlencode, parse_qs, urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from dotenv import load_dotenv, set_key


# LinkedIn OAuth2 endpoints
AUTHORIZATION_URL = 'https://www.linkedin.com/oauth/v2/authorization'
TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
PROFILE_URL = 'https://api.linkedin.com/v2/userinfo'

# OAuth2 scopes
SCOPES = ['openid', 'profile', 'w_member_social']

# Redirect URI (must match LinkedIn app settings)
REDIRECT_URI = 'http://localhost:8080/callback'


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback."""

    def do_GET(self):
        """Handle GET request from OAuth callback."""
        # Parse query parameters
        query = urlparse(self.path).query
        params = parse_qs(query)

        if 'code' in params:
            # Success - got authorization code
            self.server.auth_code = params['code'][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
                <html>
                <body>
                    <h1>Authorization Successful!</h1>
                    <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
            ''')
        elif 'error' in params:
            # Error in authorization
            self.server.auth_code = None
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            error = params['error'][0]
            self.wfile.write(f'''
                <html>
                <body>
                    <h1>Authorization Failed</h1>
                    <p>Error: {error}</p>
                </body>
                </html>
            '''.encode())

    def log_message(self, format, *args):
        """Suppress log messages."""
        pass


def setup_linkedin_auth():
    """
    Set up LinkedIn OAuth2 authentication.

    This function:
    1. Opens browser for user authorization
    2. Receives authorization code via callback
    3. Exchanges code for access token
    4. Saves credentials to .env file

    Returns:
        dict: Access token and user info
    """
    print("=" * 60)
    print("LinkedIn API OAuth2 Setup")
    print("=" * 60)

    # Load environment variables
    env_path = Path(__file__).parent.parent.parent / 'config' / '.env'
    load_dotenv(env_path)

    # Get client credentials from .env
    client_id = os.getenv('LINKEDIN_CLIENT_ID')
    client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')

    if not client_id or not client_secret:
        print("\n❌ ERROR: LinkedIn credentials not found in config/.env")
        print("\nPlease follow these steps:")
        print("1. Go to https://www.linkedin.com/developers/apps")
        print("2. Create a new app")
        print("3. Request 'Share on LinkedIn' product access")
        print("4. Add redirect URL: http://localhost:8080/callback")
        print("5. Copy Client ID and Client Secret to config/.env")
        return None

    # Step 1: Build authorization URL
    auth_params = {
        'response_type': 'code',
        'client_id': client_id,
        'redirect_uri': REDIRECT_URI,
        'scope': ' '.join(SCOPES)
    }
    auth_url = f"{AUTHORIZATION_URL}?{urlencode(auth_params)}"

    print("\n⟳ Opening browser for authorization...")
    print(f"\nIf browser doesn't open, visit this URL:")
    print(auth_url)

    # Open browser
    webbrowser.open(auth_url)

    # Step 2: Start local server to receive callback
    print("\n⏳ Waiting for authorization callback...")
    server = HTTPServer(('localhost', 8080), OAuthCallbackHandler)
    server.auth_code = None
    server.handle_request()

    if not server.auth_code:
        print("\n❌ Authorization failed or was cancelled")
        return None

    print("✓ Received authorization code")

    # Step 3: Exchange authorization code for access token
    print("\n⟳ Exchanging code for access token...")

    token_params = {
        'grant_type': 'authorization_code',
        'code': server.auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': client_id,
        'client_secret': client_secret
    }

    try:
        response = requests.post(TOKEN_URL, data=token_params)
        response.raise_for_status()
        token_data = response.json()

        access_token = token_data.get('access_token')
        expires_in = token_data.get('expires_in')

        print(f"✓ Access token received (expires in {expires_in} seconds)")

        # Step 4: Get user profile info
        print("\n⟳ Fetching user profile...")

        headers = {'Authorization': f'Bearer {access_token}'}
        profile_response = requests.get(PROFILE_URL, headers=headers)
        profile_response.raise_for_status()
        profile_data = profile_response.json()

        person_id = profile_data.get('sub')
        name = profile_data.get('name', 'Unknown')

        print(f"✓ Authenticated as: {name}")
        print(f"✓ Person ID: {person_id}")

        # Step 5: Save to .env
        if env_path.exists():
            print("\n⟳ Updating config/.env with credentials...")
            set_key(str(env_path), 'LINKEDIN_ACCESS_TOKEN', access_token)
            set_key(str(env_path), 'LINKEDIN_PERSON_ID', person_id)
            print("✓ Updated config/.env")
        else:
            print("\n⚠ Warning: config/.env not found. Please create it from .env.template")

        print("\n" + "=" * 60)
        print("LinkedIn OAuth2 Setup Complete!")
        print("=" * 60)
        print("\n⚠ IMPORTANT: LinkedIn access tokens expire after 60 days")
        print("You'll need to re-run this script when the token expires.")
        print("\nYou can now use the LinkedIn Service.")

        return {
            'access_token': access_token,
            'person_id': person_id,
            'expires_in': expires_in
        }

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error exchanging code for token: {e}")
        return None


if __name__ == '__main__':
    setup_linkedin_auth()
