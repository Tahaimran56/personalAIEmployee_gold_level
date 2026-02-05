"""
Gold Tier AI Employee - Queue Cleanup Script

This script manages the operation queue:
- Lists all queued operations
- Shows retry status and next retry time
- Removes expired operations (>24 hours)
- Manually retries specific operations
- Clears all completed operations

Author: AI Employee Gold Tier
Created: 2026-02-05
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from AI_Employee_Vault.services.queue_service import QueueService


class QueueManager:
    """Manage operation queue."""

    def __init__(self):
        self.queue_service = QueueService()
        self.queue_dir = Path("AI_Employee_Vault/Queue")

    def list_operations(self) -> List[Dict[str, Any]]:
        """List all queued operations."""
        if not self.queue_dir.exists():
            return []

        operations = []
        for file_path in self.queue_dir.glob("operation_*.json"):
            try:
                with open(file_path, 'r') as f:
                    operation = json.load(f)
                    operation['file_path'] = str(file_path)
                    operations.append(operation)
            except Exception as e:
                print(f"⚠️  Error reading {file_path}: {e}")

        return sorted(operations, key=lambda x: x.get('created_at', ''))

    def display_operations(self, operations: List[Dict[str, Any]]):
        """Display operations in a formatted table."""
        if not operations:
            print("✓ Queue is empty - no operations pending")
            return

        print(f"\n{'='*100}")
        print(f"{'ID':<20} {'Type':<15} {'Target':<15} {'Status':<12} {'Retries':<8} {'Next Retry':<20}")
        print(f"{'='*100}")

        for op in operations:
            op_id = op.get('operation_id', 'unknown')[:18]
            op_type = op.get('operation_type', 'unknown')[:13]
            target = op.get('target', 'unknown')[:13]
            status = op.get('status', 'unknown')[:10]
            retry_count = op.get('retry_count', 0)
            next_retry = op.get('next_retry', 'N/A')

            # Format next retry time
            if next_retry != 'N/A':
                try:
                    next_retry_dt = datetime.fromisoformat(next_retry.replace('Z', '+00:00'))
                    now = datetime.now(next_retry_dt.tzinfo)
                    if next_retry_dt > now:
                        time_until = next_retry_dt - now
                        minutes = int(time_until.total_seconds() / 60)
                        next_retry = f"in {minutes}m"
                    else:
                        next_retry = "ready now"
                except:
                    next_retry = next_retry[:18]

            print(f"{op_id:<20} {op_type:<15} {target:<15} {status:<12} {retry_count:<8} {next_retry:<20}")

        print(f"{'='*100}\n")
        print(f"Total operations: {len(operations)}")

    def check_expired(self) -> List[Dict[str, Any]]:
        """Check for expired operations (>24 hours)."""
        operations = self.list_operations()
        expired = []

        for op in operations:
            created_at = op.get('created_at')
            if created_at:
                try:
                    created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    now = datetime.now(created_dt.tzinfo)
                    age = now - created_dt

                    if age > timedelta(hours=24):
                        expired.append(op)
                except:
                    pass

        return expired

    def remove_expired(self) -> int:
        """Remove expired operations."""
        expired = self.check_expired()

        if not expired:
            print("✓ No expired operations found")
            return 0

        print(f"\n⚠️  Found {len(expired)} expired operation(s):")
        for op in expired:
            op_id = op.get('operation_id', 'unknown')
            op_type = op.get('operation_type', 'unknown')
            created_at = op.get('created_at', 'unknown')
            print(f"  - {op_id} ({op_type}) created at {created_at}")

        confirm = input("\nRemove these operations? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Cancelled")
            return 0

        removed = 0
        for op in expired:
            try:
                file_path = Path(op['file_path'])
                file_path.unlink()
                removed += 1
                print(f"✓ Removed: {op.get('operation_id')}")
            except Exception as e:
                print(f"❌ Error removing {op.get('operation_id')}: {e}")

        print(f"\n✓ Removed {removed} expired operation(s)")
        return removed

    def retry_operation(self, operation_id: str) -> bool:
        """Manually retry a specific operation."""
        operations = self.list_operations()
        operation = next((op for op in operations if op.get('operation_id') == operation_id), None)

        if not operation:
            print(f"❌ Operation not found: {operation_id}")
            return False

        print(f"\nRetrying operation: {operation_id}")
        print(f"  Type: {operation.get('operation_type')}")
        print(f"  Target: {operation.get('target')}")
        print(f"  Retry count: {operation.get('retry_count', 0)}")

        try:
            # Update next_retry to now
            operation['next_retry'] = datetime.now().isoformat()
            operation['status'] = 'pending'

            with open(operation['file_path'], 'w') as f:
                json.dump(operation, f, indent=2)

            print(f"✓ Operation queued for immediate retry")
            print(f"  Run queue processor to execute: python -c \"from services.queue_service import QueueService; QueueService().process_queue()\"")
            return True
        except Exception as e:
            print(f"❌ Error updating operation: {e}")
            return False

    def clear_all(self) -> int:
        """Clear all operations from queue."""
        operations = self.list_operations()

        if not operations:
            print("✓ Queue is already empty")
            return 0

        print(f"\n⚠️  WARNING: This will remove ALL {len(operations)} operation(s) from the queue!")
        print("This action cannot be undone.")
        confirm = input("\nAre you sure? Type 'DELETE ALL' to confirm: ").strip()

        if confirm != 'DELETE ALL':
            print("❌ Cancelled")
            return 0

        removed = 0
        for op in operations:
            try:
                file_path = Path(op['file_path'])
                file_path.unlink()
                removed += 1
            except Exception as e:
                print(f"❌ Error removing {op.get('operation_id')}: {e}")

        print(f"\n✓ Removed {removed} operation(s)")
        return removed

    def show_details(self, operation_id: str):
        """Show detailed information about an operation."""
        operations = self.list_operations()
        operation = next((op for op in operations if op.get('operation_id') == operation_id), None)

        if not operation:
            print(f"❌ Operation not found: {operation_id}")
            return

        print(f"\n{'='*80}")
        print(f"Operation Details: {operation_id}")
        print(f"{'='*80}")
        print(f"Type: {operation.get('operation_type')}")
        print(f"Target: {operation.get('target')}")
        print(f"Status: {operation.get('status')}")
        print(f"Created: {operation.get('created_at')}")
        print(f"Retry count: {operation.get('retry_count', 0)}")
        print(f"Next retry: {operation.get('next_retry', 'N/A')}")
        print(f"Last error: {operation.get('last_error', 'N/A')}")
        print(f"\nParameters:")
        params = operation.get('parameters', {})
        for key, value in params.items():
            if key in ['password', 'token', 'api_key', 'secret']:
                value = '***REDACTED***'
            print(f"  {key}: {value}")
        print(f"{'='*80}\n")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Gold Tier AI Employee - Queue Cleanup')
    parser.add_argument('action', choices=['list', 'expired', 'remove-expired', 'retry', 'clear', 'details'],
                        help='Action to perform')
    parser.add_argument('--operation-id', help='Operation ID (for retry/details actions)')

    args = parser.parse_args()

    manager = QueueManager()

    if args.action == 'list':
        operations = manager.list_operations()
        manager.display_operations(operations)

    elif args.action == 'expired':
        expired = manager.check_expired()
        if expired:
            print(f"\n⚠️  Found {len(expired)} expired operation(s):")
            manager.display_operations(expired)
        else:
            print("✓ No expired operations found")

    elif args.action == 'remove-expired':
        manager.remove_expired()

    elif args.action == 'retry':
        if not args.operation_id:
            print("❌ --operation-id required for retry action")
            sys.exit(1)
        manager.retry_operation(args.operation_id)

    elif args.action == 'clear':
        manager.clear_all()

    elif args.action == 'details':
        if not args.operation_id:
            print("❌ --operation-id required for details action")
            sys.exit(1)
        manager.show_details(args.operation_id)


if __name__ == "__main__":
    main()
