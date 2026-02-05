"""
Gold Tier AI Employee - Health Check Script

This script verifies that all Gold Tier services are operational:
- Python and Node.js versions
- MCP servers (Odoo, Facebook, Instagram, Twitter)
- External service connections (Odoo, Facebook, Instagram, Twitter)
- Vault directories
- Configuration files
- Stop hook configuration

Author: AI Employee Gold Tier
Created: 2026-02-05
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

try:
    import requests
except ImportError:
    print("❌ requests library not installed. Run: pip install requests")
    sys.exit(1)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class HealthChecker:
    """Health check for Gold Tier AI Employee services."""

    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []

    def check_python_version(self) -> bool:
        """Check Python version is 3.9+"""
        version = sys.version_info
        if version.major >= 3 and version.minor >= 9:
            print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            print(f"❌ Python version: {version.major}.{version.minor}.{version.micro} (requires 3.9+)")
            return False

    def check_nodejs_version(self) -> bool:
        """Check Node.js version is 16+"""
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=5)
            version = result.stdout.strip()
            major_version = int(version.replace('v', '').split('.')[0])

            if major_version >= 16:
                print(f"✓ Node.js version: {version}")
                return True
            else:
                print(f"❌ Node.js version: {version} (requires 16+)")
                return False
        except Exception as e:
            print(f"❌ Node.js not found or error: {e}")
            return False

    def check_mcp_server(self, name: str, url: str) -> bool:
        """Check if MCP server is healthy"""
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    details = data.get('details', {})
                    connected = details.get('connected', False)
                    if connected:
                        print(f"✓ {name} MCP Server: healthy ({url})")
                        return True
                    else:
                        print(f"⚠️  {name} MCP Server: running but not connected to external service")
                        self.warnings.append(f"{name}: Not connected to external service")
                        return True
                else:
                    print(f"❌ {name} MCP Server: unhealthy")
                    return False
            else:
                print(f"❌ {name} MCP Server: HTTP {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ {name} MCP Server: not running ({url})")
            return False
        except Exception as e:
            print(f"❌ {name} MCP Server: error - {e}")
            return False

    def check_vault_directories(self) -> bool:
        """Check all required vault directories exist"""
        required_dirs = [
            'AI_Employee_Vault/CEO_Briefings',
            'AI_Employee_Vault/Queue',
            'AI_Employee_Vault/Audit_Logs',
            'AI_Employee_Vault/Needs_Action',
            'AI_Employee_Vault/In_Progress',
            'AI_Employee_Vault/Done',
            'AI_Employee_Vault/Blocked',
            'AI_Employee_Vault/Pending_Approval',
            'AI_Employee_Vault/Social_Media_Metrics'
        ]

        all_exist = True
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                print(f"❌ Directory missing: {dir_path}")
                all_exist = False

        if all_exist:
            print(f"✓ Vault directories: all present ({len(required_dirs)} directories)")
            return True
        else:
            return False

    def check_config_files(self) -> bool:
        """Check all required config files exist"""
        required_files = [
            'config/odoo_config.json',
            'config/social_media_config.json',
            'config/ralph_wiggum_config.json',
            '.env'
        ]

        all_exist = True
        for file_path in required_files:
            if not Path(file_path).exists():
                print(f"❌ Config file missing: {file_path}")
                all_exist = False

        if all_exist:
            print(f"✓ Config files: all present ({len(required_files)} files)")
            return True
        else:
            return False

    def check_stop_hook(self) -> bool:
        """Check stop hook is configured"""
        windows_hook = Path('.claude/hooks/stop.ps1')
        unix_hook = Path('.claude/hooks/stop.sh')

        if windows_hook.exists() or unix_hook.exists():
            hook_path = windows_hook if windows_hook.exists() else unix_hook
            print(f"✓ Stop hook: configured ({hook_path})")

            # Check if executable (Unix only)
            if unix_hook.exists() and os.name != 'nt':
                if os.access(unix_hook, os.X_OK):
                    print(f"  ✓ Stop hook is executable")
                else:
                    print(f"  ⚠️  Stop hook is not executable (run: chmod +x {unix_hook})")
                    self.warnings.append("Stop hook not executable")

            return True
        else:
            print(f"❌ Stop hook: not found")
            return False

    def check_environment_variables(self) -> bool:
        """Check required environment variables are set"""
        required_vars = [
            'ODOO_URL',
            'ODOO_DATABASE',
            'ODOO_USERNAME',
            'ODOO_PASSWORD',
            'MCP_API_KEY'
        ]

        optional_vars = [
            'FACEBOOK_PAGE_ACCESS_TOKEN',
            'FACEBOOK_PAGE_ID',
            'INSTAGRAM_BUSINESS_ACCOUNT_ID',
            'TWITTER_API_KEY',
            'TWITTER_API_SECRET',
            'TWITTER_ACCESS_TOKEN',
            'TWITTER_ACCESS_SECRET',
            'TWITTER_BEARER_TOKEN'
        ]

        all_set = True
        for var in required_vars:
            if not os.getenv(var):
                print(f"❌ Environment variable missing: {var}")
                all_set = False

        if all_set:
            print(f"✓ Required environment variables: all set ({len(required_vars)} variables)")

        # Check optional vars
        optional_set = sum(1 for var in optional_vars if os.getenv(var))
        if optional_set < len(optional_vars):
            print(f"⚠️  Optional environment variables: {optional_set}/{len(optional_vars)} set")
            self.warnings.append(f"Only {optional_set}/{len(optional_vars)} social media credentials configured")

        return all_set

    def run_all_checks(self) -> bool:
        """Run all health checks"""
        print("🏥 Gold Tier AI Employee - Health Check\n")

        checks = [
            ("Python version", self.check_python_version),
            ("Node.js version", self.check_nodejs_version),
            ("Environment variables", self.check_environment_variables),
            ("Odoo MCP Server", lambda: self.check_mcp_server(
                "Odoo",
                os.getenv("ODOO_MCP_URL", "http://localhost:3100")
            )),
            ("Facebook MCP Server", lambda: self.check_mcp_server(
                "Facebook",
                os.getenv("FACEBOOK_MCP_URL", "http://localhost:3101")
            )),
            ("Instagram MCP Server", lambda: self.check_mcp_server(
                "Instagram",
                os.getenv("INSTAGRAM_MCP_URL", "http://localhost:3102")
            )),
            ("Twitter MCP Server", lambda: self.check_mcp_server(
                "Twitter",
                os.getenv("TWITTER_MCP_URL", "http://localhost:3103")
            )),
            ("Vault directories", self.check_vault_directories),
            ("Config files", self.check_config_files),
            ("Stop hook", self.check_stop_hook)
        ]

        for check_name, check_func in checks:
            try:
                if check_func():
                    self.checks_passed += 1
                else:
                    self.checks_failed += 1
            except Exception as e:
                print(f"❌ {check_name}: exception - {e}")
                self.checks_failed += 1

        # Print summary
        print(f"\n{'='*60}")
        print(f"Health Check Summary:")
        print(f"  ✓ Passed: {self.checks_passed}")
        print(f"  ❌ Failed: {self.checks_failed}")
        print(f"  ⚠️  Warnings: {len(self.warnings)}")

        if self.warnings:
            print(f"\nWarnings:")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")

        print(f"{'='*60}\n")

        if self.checks_failed == 0:
            print("✅ All systems operational!")
            return True
        else:
            print(f"❌ {self.checks_failed} check(s) failed. See above for details.")
            return False


def main():
    """Main entry point"""
    checker = HealthChecker()
    success = checker.run_all_checks()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
