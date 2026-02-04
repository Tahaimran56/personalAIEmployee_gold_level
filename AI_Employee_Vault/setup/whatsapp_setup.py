"""
WhatsApp Watcher Setup Script
Helps set up WhatsApp Web automation with Playwright
"""

import os
import sys
import subprocess
from pathlib import Path


def check_playwright_installed():
    """Check if Playwright is installed."""
    try:
        import playwright
        print("[OK] Playwright package is installed")
        return True
    except ImportError:
        print("[ERROR] Playwright package not found")
        return False


def install_playwright_browsers():
    """Install Playwright browser binaries."""
    print("\n" + "=" * 60)
    print("Installing Playwright Browsers")
    print("=" * 60)
    print("\nThis will download Chromium browser (~300MB)")
    print("This is required for WhatsApp Web automation")

    response = input("\nProceed with installation? (y/n): ")
    if response.lower() != 'y':
        print("Installation cancelled")
        return False

    try:
        print("\n[INFO] Installing Chromium browser...")
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print("[OK] Chromium browser installed successfully")
            return True
        else:
            print(f"[ERROR] Installation failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"[ERROR] Failed to install browsers: {e}")
        return False


def create_session_directory(vault_path: Path):
    """Create WhatsApp session directory."""
    session_dir = vault_path / '.state' / 'whatsapp_session'
    session_dir.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Session directory created: {session_dir}")
    return session_dir


def test_whatsapp_connection(vault_path: Path):
    """Test WhatsApp Web connection."""
    print("\n" + "=" * 60)
    print("Testing WhatsApp Web Connection")
    print("=" * 60)

    print("\n[INFO] This will open a browser window")
    print("[INFO] You will need to scan the QR code with your phone")
    print("[INFO] After scanning, the session will be saved for future use")

    response = input("\nProceed with test? (y/n): ")
    if response.lower() != 'y':
        print("Test cancelled")
        return False

    try:
        from playwright.sync_api import sync_playwright

        session_dir = vault_path / '.state' / 'whatsapp_session'

        print("\n[INFO] Opening browser...")
        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(session_dir),
                headless=False,  # Show browser for QR code scan
                args=['--disable-blink-features=AutomationControlled']
            )

            page = browser.pages[0] if browser.pages else browser.new_page()

            print("[INFO] Navigating to WhatsApp Web...")
            page.goto('https://web.whatsapp.com/')

            print("\n" + "=" * 60)
            print("SCAN QR CODE NOW")
            print("=" * 60)
            print("\n1. Open WhatsApp on your phone")
            print("2. Tap Menu (⋮) or Settings")
            print("3. Tap 'Linked Devices'")
            print("4. Tap 'Link a Device'")
            print("5. Scan the QR code in the browser window")
            print("\nWaiting for login (up to 2 minutes)...")

            try:
                # Wait for chat list (indicates successful login)
                page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
                print("\n[OK] Login successful!")
                print("[OK] Session saved for future use")

                # Keep browser open for a few seconds
                print("\n[INFO] Keeping browser open for 5 seconds...")
                page.wait_for_timeout(5000)

                browser.close()
                return True

            except Exception as e:
                print(f"\n[ERROR] Login timeout or failed: {e}")
                browser.close()
                return False

    except ImportError:
        print("[ERROR] Playwright not installed. Run: pip install playwright")
        return False
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False


def main():
    """Main setup flow."""
    print("=" * 60)
    print("WhatsApp Watcher Setup")
    print("=" * 60)

    # Get vault path
    vault_path = Path(__file__).parent.parent.parent / 'AI_Employee_Vault'

    if not vault_path.exists():
        print(f"[ERROR] Vault not found at: {vault_path}")
        return

    print(f"\n[INFO] Vault path: {vault_path}")

    # Step 1: Check Playwright installation
    print("\n" + "-" * 60)
    print("Step 1: Checking Playwright Installation")
    print("-" * 60)

    if not check_playwright_installed():
        print("\n[INFO] Installing Playwright package...")
        print("[INFO] Run: pip install playwright")
        return

    # Step 2: Install browser binaries
    print("\n" + "-" * 60)
    print("Step 2: Installing Browser Binaries")
    print("-" * 60)

    if not install_playwright_browsers():
        print("\n[ERROR] Browser installation failed")
        return

    # Step 3: Create session directory
    print("\n" + "-" * 60)
    print("Step 3: Creating Session Directory")
    print("-" * 60)

    create_session_directory(vault_path)

    # Step 4: Test connection
    print("\n" + "-" * 60)
    print("Step 4: Testing WhatsApp Web Connection")
    print("-" * 60)

    if test_whatsapp_connection(vault_path):
        print("\n" + "=" * 60)
        print("Setup Complete!")
        print("=" * 60)
        print("\nYou can now run the WhatsApp watcher:")
        print("  python AI_Employee_Vault/watchers/whatsapp_watcher.py")
        print("\nThe watcher will use the saved session (no QR code needed)")
    else:
        print("\n" + "=" * 60)
        print("Setup Incomplete")
        print("=" * 60)
        print("\nYou can retry the test later by running:")
        print("  python AI_Employee_Vault/setup/whatsapp_setup.py")


if __name__ == '__main__':
    main()
