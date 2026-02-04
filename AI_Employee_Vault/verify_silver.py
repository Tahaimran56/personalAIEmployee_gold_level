"""
Silver Tier Verification Script
Verifies all Silver tier requirements and features are properly implemented
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class SilverTierVerifier:
    """
    Verification script for Silver tier implementation.

    Checks:
    - File structure
    - Configuration files
    - Service implementations
    - Watcher implementations
    - Scheduler setup
    - Documentation completeness
    - Dependencies
    """

    def __init__(self, vault_path: str):
        """
        Initialize verifier.

        Args:
            vault_path: Path to AI_Employee_Vault
        """
        self.vault_path = Path(vault_path)
        self.project_root = self.vault_path.parent
        self.results = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def verify_all(self) -> Dict:
        """
        Run all verification checks.

        Returns:
            Dict with verification results
        """
        print("=" * 60)
        print("Silver Tier Verification")
        print("=" * 60)
        print()

        # Run all checks
        self.check_file_structure()
        self.check_configuration_files()
        self.check_service_implementations()
        self.check_watcher_implementations()
        self.check_scheduler_setup()
        self.check_documentation()
        self.check_dependencies()
        self.check_credentials()

        # Print summary
        self.print_summary()

        return {
            'passed': self.passed,
            'failed': self.failed,
            'warnings': self.warnings,
            'total': self.passed + self.failed,
            'success_rate': (self.passed / (self.passed + self.failed) * 100) if (self.passed + self.failed) > 0 else 0,
            'results': self.results
        }

    def check_file_structure(self):
        """Check required folder structure exists."""
        print("Checking file structure...")

        required_folders = [
            'Needs_Action',
            'Pending_Approval',
            'Approved',
            'Rejected',
            'In_Progress',
            'Done',
            'Plans',
            'Logs',
            '.state',
            'services',
            'watchers',
            'scheduler',
            'setup',
            '.claude/skills',
            'templates',
            'mcp'
        ]

        for folder in required_folders:
            folder_path = self.vault_path / folder
            if folder_path.exists():
                self.pass_check(f"Folder exists: {folder}")
            else:
                self.fail_check(f"Folder missing: {folder}")

    def check_configuration_files(self):
        """Check required configuration files exist."""
        print("\nChecking configuration files...")

        config_files = [
            ('config/.env.template', 'Environment template'),
            ('config/gmail_config.json', 'Gmail configuration'),
            ('config/linkedin_config.json', 'LinkedIn configuration'),
            ('config/mcp_email_server.json', 'MCP server configuration'),
            ('config/scheduler_config.json', 'Scheduler configuration')
        ]

        for file_path, description in config_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                self.pass_check(f"{description}: {file_path}")
            else:
                self.fail_check(f"{description} missing: {file_path}")

    def check_service_implementations(self):
        """Check service implementations exist and are valid."""
        print("\nChecking service implementations...")

        services = [
            ('services/email_service.py', 'EmailService', ['compose_draft_email', 'send_email', 'validate_email']),
            ('services/linkedin_service.py', 'LinkedInService', ['compose_draft_post', 'publish_post', 'validate_post_content']),
            ('services/reasoning_service.py', 'ReasoningService', ['generate_plan', 'execute_plan_step', 'validate_plan_completion']),
            ('services/approval_service.py', 'ApprovalService', ['classify_action', 'create_approval_request', 'check_approval_status'])
        ]

        for file_path, class_name, methods in services:
            full_path = self.vault_path / file_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')

                # Check class exists
                if f"class {class_name}" in content:
                    self.pass_check(f"Service class: {class_name}")

                    # Check methods exist
                    for method in methods:
                        if f"def {method}" in content:
                            self.pass_check(f"  Method: {method}()")
                        else:
                            self.fail_check(f"  Method missing: {method}()")
                else:
                    self.fail_check(f"Service class missing: {class_name}")
            else:
                self.fail_check(f"Service file missing: {file_path}")

    def check_watcher_implementations(self):
        """Check watcher implementations exist."""
        print("\nChecking watcher implementations...")

        watchers = [
            ('watchers/base_watcher.py', 'BaseWatcher'),
            ('watchers/gmail_watcher.py', 'GmailWatcher')
        ]

        for file_path, class_name in watchers:
            full_path = self.vault_path / file_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8')
                if f"class {class_name}" in content:
                    self.pass_check(f"Watcher: {class_name}")
                else:
                    self.fail_check(f"Watcher class missing: {class_name}")
            else:
                self.fail_check(f"Watcher file missing: {file_path}")

    def check_scheduler_setup(self):
        """Check scheduler implementation and setup scripts."""
        print("\nChecking scheduler setup...")

        scheduler_files = [
            ('scheduler/scheduler.py', 'Scheduler implementation'),
            ('scheduler/task_scheduler.ps1', 'Windows setup script'),
            ('scheduler/cron_setup.sh', 'Linux/Mac setup script')
        ]

        for file_path, description in scheduler_files:
            full_path = self.vault_path / file_path
            if full_path.exists():
                self.pass_check(f"{description}: {file_path}")
            else:
                self.fail_check(f"{description} missing: {file_path}")

    def check_documentation(self):
        """Check documentation completeness."""
        print("\nChecking documentation...")

        docs = [
            ('README.md', 'Main README'),
            ('Company_Handbook.md', 'Company Handbook'),
            ('Dashboard.md', 'Dashboard'),
            ('MANUAL_TASKS.md', 'Manual tasks guide'),
            ('.claude/skills/create-plan.skill.md', 'Create plan skill'),
            ('.claude/skills/post-linkedin.skill.md', 'Post LinkedIn skill'),
            ('.claude/skills/process-actions.skill.md', 'Process actions skill'),
            ('.claude/skills/schedule-task.skill.md', 'Schedule task skill')
        ]

        for file_path, description in docs:
            full_path = self.vault_path / file_path if not file_path.startswith('.claude') else self.vault_path / file_path
            if full_path.exists():
                self.pass_check(f"{description}: {file_path}")
            else:
                self.fail_check(f"{description} missing: {file_path}")

    def check_dependencies(self):
        """Check Python and Node.js dependencies."""
        print("\nChecking dependencies...")

        # Check Python dependencies
        python_deps = [
            'google-auth',
            'google-auth-oauthlib',
            'google-auth-httplib2',
            'google-api-python-client',
            'anthropic',
            'schedule',
            'requests',
            'python-dotenv'
        ]

        for dep in python_deps:
            try:
                __import__(dep.replace('-', '_'))
                self.pass_check(f"Python package: {dep}")
            except ImportError:
                self.warn_check(f"Python package not installed: {dep}")

        # Check Node.js dependencies
        package_json = self.vault_path / 'mcp' / 'package.json'
        if package_json.exists():
            self.pass_check("Node.js package.json exists")

            # Check if node_modules exists
            node_modules = self.vault_path / 'mcp' / 'node_modules'
            if node_modules.exists():
                self.pass_check("Node.js dependencies installed")
            else:
                self.warn_check("Node.js dependencies not installed (run: cd AI_Employee_Vault/mcp && npm install)")
        else:
            self.fail_check("Node.js package.json missing")

    def check_credentials(self):
        """Check if credentials are configured."""
        print("\nChecking credentials...")

        env_file = self.project_root / 'config' / '.env'

        if env_file.exists():
            self.pass_check("config/.env file exists")

            # Check for required credentials
            content = env_file.read_text(encoding='utf-8')

            credentials = [
                ('GMAIL_CLIENT_ID', 'Gmail Client ID'),
                ('GMAIL_CLIENT_SECRET', 'Gmail Client Secret'),
                ('GMAIL_REFRESH_TOKEN', 'Gmail Refresh Token'),
                ('GMAIL_USER', 'Gmail User'),
                ('LINKEDIN_CLIENT_ID', 'LinkedIn Client ID'),
                ('LINKEDIN_CLIENT_SECRET', 'LinkedIn Client Secret'),
                ('LINKEDIN_ACCESS_TOKEN', 'LinkedIn Access Token'),
                ('LINKEDIN_PERSON_ID', 'LinkedIn Person ID'),
                ('CLAUDE_API_KEY', 'Claude API Key'),
                ('MCP_EMAIL_SERVER_URL', 'MCP Server URL')
            ]

            for key, description in credentials:
                if key in content:
                    # Check if value is set (not placeholder)
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith(key):
                            value = line.split('=', 1)[1].strip() if '=' in line else ''
                            if value and not value.startswith('your_') and value != '':
                                self.pass_check(f"  {description} configured")
                            else:
                                self.warn_check(f"  {description} not configured (placeholder value)")
                            break
                else:
                    self.warn_check(f"  {description} missing from .env")
        else:
            self.warn_check("config/.env not found (copy from .env.template)")

    def pass_check(self, message: str):
        """Record a passed check."""
        print(f"  ✓ {message}")
        self.results.append(('PASS', message))
        self.passed += 1

    def fail_check(self, message: str):
        """Record a failed check."""
        print(f"  ✗ {message}")
        self.results.append(('FAIL', message))
        self.failed += 1

    def warn_check(self, message: str):
        """Record a warning."""
        print(f"  ⚠ {message}")
        self.results.append(('WARN', message))
        self.warnings += 1

    def print_summary(self):
        """Print verification summary."""
        print()
        print("=" * 60)
        print("Verification Summary")
        print("=" * 60)
        print()
        print(f"Passed:   {self.passed}")
        print(f"Failed:   {self.failed}")
        print(f"Warnings: {self.warnings}")
        print(f"Total:    {self.passed + self.failed}")
        print()

        if self.failed == 0:
            success_rate = 100.0
        else:
            success_rate = (self.passed / (self.passed + self.failed)) * 100

        print(f"Success Rate: {success_rate:.1f}%")
        print()

        if self.failed == 0 and self.warnings == 0:
            print("✅ All checks passed! Silver tier is fully implemented.")
        elif self.failed == 0:
            print("✅ All critical checks passed!")
            print("⚠️  Some warnings present (see above)")
        else:
            print("❌ Some checks failed. Review failures above.")

        print()
        print("Next Steps:")
        if self.warnings > 0:
            print("  1. Review warnings and complete manual setup tasks")
            print("  2. See MANUAL_TASKS.md for setup instructions")
        if self.failed > 0:
            print("  3. Fix failed checks before proceeding")
        print("  4. Test workflows end-to-end")
        print("  5. Start services and scheduler")
        print()


def main():
    """Main entry point."""
    import sys

    # Get vault path
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent

    # Run verification
    verifier = SilverTierVerifier(str(vault_path))
    results = verifier.verify_all()

    # Exit with appropriate code
    if results['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
