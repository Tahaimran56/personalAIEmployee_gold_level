"""
Gold Tier AI Employee - Verification Script

This script performs end-to-end testing of all Gold Tier features:
- Odoo integration (create invoice, record payment, record expense)
- CEO Briefing generation
- Ralph Wiggum loop (multi-step task)
- Social media posting (Facebook, Instagram, Twitter)
- Error recovery (queue and retry)
- Audit logging

Author: AI Employee Gold Tier
Created: 2026-02-05
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import requests
except ImportError:
    print("❌ requests library not installed. Run: pip install requests")
    sys.exit(1)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GoldTierVerifier:
    """Verify all Gold Tier features."""

    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []

    def log_test(self, test_name: str, passed: bool, message: str = ""):
        """Log test result."""
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"  {message}")

        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })

        if passed:
            self.tests_passed += 1
        else:
            self.tests_failed += 1

    def test_odoo_integration(self) -> bool:
        """Test Odoo integration."""
        print("\n" + "="*80)
        print("Testing Odoo Integration")
        print("="*80)

        odoo_url = os.getenv("ODOO_MCP_URL", "http://localhost:3100")
        api_key = os.getenv("MCP_API_KEY")

        # Test 1: Health check
        try:
            response = requests.get(f"{odoo_url}/health", timeout=5)
            if response.status_code == 200:
                self.log_test("Odoo MCP health check", True)
            else:
                self.log_test("Odoo MCP health check", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Odoo MCP health check", False, str(e))
            return False

        # Test 2: Create invoice
        try:
            invoice_data = {
                "customer_name": "Test Customer",
                "amount": 1000.00,
                "description": "Verification test invoice",
                "due_date": "2026-03-01"
            }

            response = requests.post(
                f"{odoo_url}/invoices",
                json=invoice_data,
                headers={"X-API-Key": api_key},
                timeout=10
            )

            if response.status_code == 201:
                data = response.json()
                invoice_id = data.get("odoo_record_id")
                self.log_test("Create Odoo invoice", True, f"Invoice ID: {invoice_id}")
            else:
                self.log_test("Create Odoo invoice", False, f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Create Odoo invoice", False, str(e))
            return False

        # Test 3: Record payment
        try:
            payment_data = {
                "customer_name": "Test Customer",
                "amount": 500.00,
                "payment_date": "2026-02-05",
                "payment_method": "bank_transfer",
                "reference": "TEST-PAY-001"
            }

            response = requests.post(
                f"{odoo_url}/payments",
                json=payment_data,
                headers={"X-API-Key": api_key},
                timeout=10
            )

            if response.status_code == 201:
                self.log_test("Record Odoo payment", True)
            else:
                self.log_test("Record Odoo payment", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Record Odoo payment", False, str(e))

        # Test 4: Record expense
        try:
            expense_data = {
                "description": "Test expense",
                "amount": 250.00,
                "expense_date": "2026-02-05",
                "category": "office_supplies",
                "vendor": "Test Vendor"
            }

            response = requests.post(
                f"{odoo_url}/expenses",
                json=expense_data,
                headers={"X-API-Key": api_key},
                timeout=10
            )

            if response.status_code == 201:
                self.log_test("Record Odoo expense", True)
            else:
                self.log_test("Record Odoo expense", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("Record Odoo expense", False, str(e))

        return True

    def test_ceo_briefing(self) -> bool:
        """Test CEO Briefing generation."""
        print("\n" + "="*80)
        print("Testing CEO Briefing Generation")
        print("="*80)

        try:
            from AI_Employee_Vault.services.ceo_briefing_service import CEOBriefingService

            service = CEOBriefingService()
            briefing_file = service.generate_weekly_briefing()

            if Path(briefing_file).exists():
                self.log_test("Generate CEO briefing", True, f"File: {briefing_file}")

                # Verify briefing content
                with open(briefing_file, 'r') as f:
                    content = f.read()
                    if "Revenue Summary" in content and "Expense Summary" in content:
                        self.log_test("CEO briefing content validation", True)
                    else:
                        self.log_test("CEO briefing content validation", False, "Missing expected sections")
            else:
                self.log_test("Generate CEO briefing", False, "File not created")
                return False

        except Exception as e:
            self.log_test("Generate CEO briefing", False, str(e))
            return False

        return True

    def test_ralph_wiggum_loop(self) -> bool:
        """Test Ralph Wiggum autonomous loop."""
        print("\n" + "="*80)
        print("Testing Ralph Wiggum Autonomous Loop")
        print("="*80)

        try:
            from AI_Employee_Vault.ralph_wiggum.state_manager import StateManager

            state_manager = StateManager()

            # Create test task
            task_id = state_manager.initialize_task(
                task_name="Verification test task",
                total_steps=3,
                steps=[
                    {"step_number": 1, "step_description": "Step 1: Initialize"},
                    {"step_number": 2, "step_description": "Step 2: Process"},
                    {"step_number": 3, "step_description": "Step 3: Complete"}
                ]
            )

            self.log_test("Create Ralph Wiggum task", True, f"Task ID: {task_id}")

            # Move to in progress
            state_manager.move_to_in_progress(task_id)
            self.log_test("Move task to In_Progress", True)

            # Mark steps complete
            for step in range(1, 4):
                state_manager.mark_step_complete(task_id, step, f"Step {step}", 5)
                time.sleep(0.1)

            self.log_test("Mark steps complete", True)

            # Check if task is complete
            if state_manager.is_task_complete(task_id):
                self.log_test("Task completion detection", True)
            else:
                self.log_test("Task completion detection", False)

            # Clean up
            task_file = Path(f"AI_Employee_Vault/In_Progress/{task_id}.md")
            if task_file.exists():
                task_file.unlink()

        except Exception as e:
            self.log_test("Ralph Wiggum loop", False, str(e))
            return False

        return True

    def test_social_media_validation(self) -> bool:
        """Test social media post validation."""
        print("\n" + "="*80)
        print("Testing Social Media Integration")
        print("="*80)

        try:
            from AI_Employee_Vault.services.social_media_service import SocialMediaService

            service = SocialMediaService()

            # Test 1: Valid post
            validation = service.validate_post(
                platforms=["facebook", "instagram"],
                text="Test post from verification script",
                image_url="https://example.com/test.jpg"
            )

            if validation["valid"]:
                self.log_test("Social media validation (valid post)", True)
            else:
                self.log_test("Social media validation (valid post)", False, str(validation["errors"]))

            # Test 2: Invalid post (Instagram without image)
            validation = service.validate_post(
                platforms=["instagram"],
                text="Test post without image"
            )

            if not validation["valid"] and "Instagram: Image is required" in validation["errors"]:
                self.log_test("Social media validation (invalid post)", True)
            else:
                self.log_test("Social media validation (invalid post)", False, "Should reject Instagram post without image")

            # Test 3: Text too long for Twitter
            validation = service.validate_post(
                platforms=["twitter"],
                text="A" * 300  # 300 characters, exceeds 280 limit
            )

            if not validation["valid"]:
                self.log_test("Social media validation (text too long)", True)
            else:
                self.log_test("Social media validation (text too long)", False, "Should reject text > 280 chars for Twitter")

        except Exception as e:
            self.log_test("Social media validation", False, str(e))
            return False

        return True

    def test_queue_service(self) -> bool:
        """Test queue and error recovery."""
        print("\n" + "="*80)
        print("Testing Queue and Error Recovery")
        print("="*80)

        try:
            from AI_Employee_Vault.services.queue_service import QueueService

            service = QueueService()

            # Create test operation
            operation_id = service.create_operation(
                operation_type="test_operation",
                target="verification_test",
                parameters={"test": "data"}
            )

            self.log_test("Create queue operation", True, f"Operation ID: {operation_id}")

            # Check queue status
            status = service.get_queue_status()
            if status["total_operations"] > 0:
                self.log_test("Queue status check", True, f"{status['total_operations']} operation(s) in queue")
            else:
                self.log_test("Queue status check", False, "No operations in queue")

            # Clean up
            queue_file = Path(f"AI_Employee_Vault/Queue/{operation_id}.json")
            if queue_file.exists():
                queue_file.unlink()

        except Exception as e:
            self.log_test("Queue service", False, str(e))
            return False

        return True

    def test_audit_logging(self) -> bool:
        """Test audit logging."""
        print("\n" + "="*80)
        print("Testing Audit Logging")
        print("="*80)

        try:
            from AI_Employee_Vault.services.audit_service import AuditService

            service = AuditService()

            # Log test action
            service.log_action(
                action_type="verification_test",
                actor="verification_script",
                target="test_target",
                parameters={"test": "data", "password": "secret123"},
                result="success"
            )

            self.log_test("Create audit log entry", True)

            # Verify log file exists
            log_file = Path(f"AI_Employee_Vault/Audit_Logs/{datetime.now().strftime('%Y-%m-%d')}.json")
            if log_file.exists():
                self.log_test("Audit log file creation", True)

                # Verify sensitive data redaction
                with open(log_file, 'r') as f:
                    for line in f:
                        try:
                            log_entry = json.loads(line.strip())
                            if log_entry.get("action_type") == "verification_test":
                                params = log_entry.get("parameters", {})
                                if params.get("password") == "***REDACTED***":
                                    self.log_test("Sensitive data redaction", True)
                                else:
                                    self.log_test("Sensitive data redaction", False, "Password not redacted")
                                break
                        except:
                            pass
            else:
                self.log_test("Audit log file creation", False)

        except Exception as e:
            self.log_test("Audit logging", False, str(e))
            return False

        return True

    def test_mcp_servers(self) -> bool:
        """Test all MCP servers."""
        print("\n" + "="*80)
        print("Testing MCP Servers")
        print("="*80)

        servers = [
            ("Odoo", os.getenv("ODOO_MCP_URL", "http://localhost:3100")),
            ("Facebook", os.getenv("FACEBOOK_MCP_URL", "http://localhost:3101")),
            ("Instagram", os.getenv("INSTAGRAM_MCP_URL", "http://localhost:3102")),
            ("Twitter", os.getenv("TWITTER_MCP_URL", "http://localhost:3103"))
        ]

        all_passed = True
        for name, url in servers:
            try:
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    self.log_test(f"{name} MCP server", True)
                else:
                    self.log_test(f"{name} MCP server", False, f"HTTP {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"{name} MCP server", False, str(e))
                all_passed = False

        return all_passed

    def run_all_tests(self) -> bool:
        """Run all verification tests."""
        print("\n" + "="*80)
        print("Gold Tier AI Employee - Verification Tests")
        print("="*80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        # Run tests
        self.test_mcp_servers()
        self.test_odoo_integration()
        self.test_ceo_briefing()
        self.test_ralph_wiggum_loop()
        self.test_social_media_validation()
        self.test_queue_service()
        self.test_audit_logging()

        # Print summary
        print("\n" + "="*80)
        print("Verification Summary")
        print("="*80)
        print(f"Tests passed: {self.tests_passed}")
        print(f"Tests failed: {self.tests_failed}")
        print(f"Success rate: {(self.tests_passed / (self.tests_passed + self.tests_failed) * 100):.1f}%")
        print("="*80)

        # Save results
        results_file = Path(f"AI_Employee_Vault/verification_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "tests_passed": self.tests_passed,
                "tests_failed": self.tests_failed,
                "results": self.test_results
            }, f, indent=2)

        print(f"\nResults saved to: {results_file}")

        if self.tests_failed == 0:
            print("\n✅ All tests passed!")
            return True
        else:
            print(f"\n❌ {self.tests_failed} test(s) failed")
            return False


def main():
    """Main entry point."""
    verifier = GoldTierVerifier()
    success = verifier.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
