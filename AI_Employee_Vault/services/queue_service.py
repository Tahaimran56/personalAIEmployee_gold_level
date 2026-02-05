"""
Queue Service for Gold Tier AI Employee

This service manages the operation queue for graceful degradation when external
services are unavailable. It implements:
- Local JSON-based queue storage
- Exponential backoff retry logic
- 24-hour expiry alerts
- Queue health monitoring

Author: AI Employee Gold Tier
Created: 2026-02-05
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueueService:
    """
    Manages queued operations for external service failures.

    Operations are stored as individual JSON files in the Queue/ directory.
    Each operation has retry logic with exponential backoff and a 24-hour expiry.
    """

    def __init__(self, queue_dir: str = "AI_Employee_Vault/Queue"):
        """
        Initialize the QueueService.

        Args:
            queue_dir: Directory to store queued operations
        """
        self.queue_dir = Path(queue_dir)
        self.queue_dir.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.max_retries = 10
        self.expiry_hours = 24
        self.max_backoff_minutes = 30

        logger.info(f"QueueService initialized with queue directory: {self.queue_dir}")

    def create_operation(
        self,
        operation_type: str,
        target: str,
        parameters: Dict[str, Any],
        max_retries: Optional[int] = None
    ) -> str:
        """
        Create a new queued operation.

        Args:
            operation_type: Type of operation (odoo_transaction, social_post, email_send)
            target: Target service (odoo, facebook, instagram, twitter, email)
            parameters: Operation-specific parameters
            max_retries: Maximum retry attempts (default: 10)

        Returns:
            operation_id: UUID of the created operation
        """
        operation_id = str(uuid.uuid4())
        now = datetime.now()

        operation = {
            "operation_id": operation_id,
            "operation_type": operation_type,
            "target": target,
            "parameters": parameters,
            "retry_count": 0,
            "max_retries": max_retries or self.max_retries,
            "next_retry": now.isoformat(),
            "expiry": (now + timedelta(hours=self.expiry_hours)).isoformat(),
            "status": "pending",
            "created_at": now.isoformat(),
            "last_retry_at": None,
            "completed_at": None,
            "last_error": None
        }

        # Write operation to file
        operation_file = self.queue_dir / f"{operation_id}.json"
        with open(operation_file, 'w') as f:
            json.dump(operation, f, indent=2)

        logger.info(f"Created queued operation: {operation_id} ({operation_type} -> {target})")
        return operation_id

    def calculate_next_retry(self, retry_count: int) -> datetime:
        """
        Calculate next retry time using exponential backoff.

        Formula: next_retry = now + min(2^retry_count minutes, 30 minutes)

        Args:
            retry_count: Current retry attempt number

        Returns:
            datetime: When to attempt next retry
        """
        # Exponential backoff: 1min, 2min, 4min, 8min, 16min, then 30min max
        backoff_minutes = min(2 ** retry_count, self.max_backoff_minutes)
        next_retry = datetime.now() + timedelta(minutes=backoff_minutes)

        logger.debug(f"Calculated next retry: {backoff_minutes} minutes from now (retry #{retry_count})")
        return next_retry

    def process_queue(self) -> Dict[str, Any]:
        """
        Process all pending operations in the queue.

        This method should be called periodically (e.g., every 5 minutes) to:
        1. Check for operations ready to retry
        2. Attempt to execute them
        3. Update their status based on results

        Returns:
            dict: Summary of processing results
        """
        results = {
            "processed": 0,
            "succeeded": 0,
            "failed": 0,
            "expired": 0,
            "pending": 0
        }

        # Get all operation files
        operation_files = list(self.queue_dir.glob("*.json"))

        if not operation_files:
            logger.info("Queue is empty")
            return results

        logger.info(f"Processing queue: {len(operation_files)} operations")

        for operation_file in operation_files:
            try:
                with open(operation_file, 'r') as f:
                    operation = json.load(f)

                # Check if operation is ready to retry
                next_retry = datetime.fromisoformat(operation["next_retry"])
                now = datetime.now()

                if now < next_retry:
                    results["pending"] += 1
                    continue

                # Check if operation has expired
                expiry = datetime.fromisoformat(operation["expiry"])
                if now > expiry:
                    self._mark_expired(operation)
                    results["expired"] += 1
                    continue

                # Attempt to execute operation
                results["processed"] += 1
                success = self._execute_operation(operation)

                if success:
                    self._mark_succeeded(operation)
                    results["succeeded"] += 1
                else:
                    self._mark_failed(operation)
                    results["failed"] += 1

            except Exception as e:
                logger.error(f"Error processing operation {operation_file.name}: {e}")
                results["failed"] += 1

        logger.info(f"Queue processing complete: {results}")
        return results

    def _execute_operation(self, operation: Dict[str, Any]) -> bool:
        """
        Execute a queued operation.

        This is a placeholder that should be overridden or extended to actually
        execute operations by calling the appropriate service.

        Args:
            operation: Operation to execute

        Returns:
            bool: True if successful, False otherwise
        """
        # TODO: Implement actual operation execution
        # This should call OdooService, SocialMediaService, etc. based on operation_type

        logger.warning(f"Operation execution not yet implemented: {operation['operation_type']}")
        return False

    def _mark_succeeded(self, operation: Dict[str, Any]) -> None:
        """Mark operation as succeeded and remove from queue."""
        operation["status"] = "succeeded"
        operation["completed_at"] = datetime.now().isoformat()

        # Write final state
        operation_file = self.queue_dir / f"{operation['operation_id']}.json"
        with open(operation_file, 'w') as f:
            json.dump(operation, f, indent=2)

        # Remove from queue (move to completed or delete)
        operation_file.unlink()

        logger.info(f"Operation succeeded: {operation['operation_id']}")

    def _mark_failed(self, operation: Dict[str, Any]) -> None:
        """Mark operation as failed and update retry info."""
        operation["retry_count"] += 1
        operation["last_retry_at"] = datetime.now().isoformat()
        operation["status"] = "retrying"

        # Calculate next retry time
        next_retry = self.calculate_next_retry(operation["retry_count"])
        operation["next_retry"] = next_retry.isoformat()

        # Check if max retries reached
        if operation["retry_count"] >= operation["max_retries"]:
            operation["status"] = "failed"
            logger.warning(f"Operation failed after {operation['retry_count']} retries: {operation['operation_id']}")

        # Write updated state
        operation_file = self.queue_dir / f"{operation['operation_id']}.json"
        with open(operation_file, 'w') as f:
            json.dump(operation, f, indent=2)

        logger.info(f"Operation retry scheduled: {operation['operation_id']} (retry #{operation['retry_count']})")

    def _mark_expired(self, operation: Dict[str, Any]) -> None:
        """Mark operation as expired and alert user."""
        operation["status"] = "expired"

        # Write final state
        operation_file = self.queue_dir / f"{operation['operation_id']}.json"
        with open(operation_file, 'w') as f:
            json.dump(operation, f, indent=2)

        logger.error(f"Operation expired after 24 hours: {operation['operation_id']} ({operation['operation_type']} -> {operation['target']})")

        # TODO: Send user notification about expired operation

    def check_expired_operations(self) -> List[Dict[str, Any]]:
        """
        Check for operations that have been pending for 24+ hours.

        Returns:
            list: List of expired operations
        """
        expired_operations = []
        now = datetime.now()

        for operation_file in self.queue_dir.glob("*.json"):
            try:
                with open(operation_file, 'r') as f:
                    operation = json.load(f)

                expiry = datetime.fromisoformat(operation["expiry"])

                if now > expiry and operation["status"] != "expired":
                    expired_operations.append(operation)
                    self._mark_expired(operation)

            except Exception as e:
                logger.error(f"Error checking expiry for {operation_file.name}: {e}")

        if expired_operations:
            logger.warning(f"Found {len(expired_operations)} expired operations")

        return expired_operations

    def get_queue_status(self) -> Dict[str, Any]:
        """
        Get current queue health status.

        Returns:
            dict: Queue status including counts by status and oldest operation
        """
        status = {
            "total_operations": 0,
            "by_status": {
                "pending": 0,
                "retrying": 0,
                "failed": 0,
                "expired": 0
            },
            "oldest_operation": None,
            "queue_size_mb": 0
        }

        operation_files = list(self.queue_dir.glob("*.json"))
        status["total_operations"] = len(operation_files)

        oldest_date = None

        for operation_file in operation_files:
            try:
                # Get file size
                status["queue_size_mb"] += operation_file.stat().st_size / (1024 * 1024)

                with open(operation_file, 'r') as f:
                    operation = json.load(f)

                # Count by status
                op_status = operation.get("status", "pending")
                if op_status in status["by_status"]:
                    status["by_status"][op_status] += 1

                # Track oldest operation
                created_at = datetime.fromisoformat(operation["created_at"])
                if oldest_date is None or created_at < oldest_date:
                    oldest_date = created_at
                    status["oldest_operation"] = {
                        "operation_id": operation["operation_id"],
                        "created_at": operation["created_at"],
                        "operation_type": operation["operation_type"],
                        "target": operation["target"]
                    }

            except Exception as e:
                logger.error(f"Error reading operation {operation_file.name}: {e}")

        status["queue_size_mb"] = round(status["queue_size_mb"], 2)

        logger.info(f"Queue status: {status['total_operations']} operations, {status['queue_size_mb']} MB")
        return status

    def get_operation(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific operation by ID.

        Args:
            operation_id: UUID of the operation

        Returns:
            dict: Operation data or None if not found
        """
        operation_file = self.queue_dir / f"{operation_id}.json"

        if not operation_file.exists():
            return None

        with open(operation_file, 'r') as f:
            return json.load(f)

    def cancel_operation(self, operation_id: str) -> bool:
        """
        Cancel a pending operation.

        Args:
            operation_id: UUID of the operation to cancel

        Returns:
            bool: True if cancelled, False if not found
        """
        operation_file = self.queue_dir / f"{operation_id}.json"

        if not operation_file.exists():
            return False

        with open(operation_file, 'r') as f:
            operation = json.load(f)

        operation["status"] = "cancelled"
        operation["completed_at"] = datetime.now().isoformat()

        with open(operation_file, 'w') as f:
            json.dump(operation, f, indent=2)

        # Remove from queue
        operation_file.unlink()

        logger.info(f"Operation cancelled: {operation_id}")
        return True


# Example usage
if __name__ == "__main__":
    # Initialize service
    queue_service = QueueService()

    # Create a test operation
    operation_id = queue_service.create_operation(
        operation_type="odoo_transaction",
        target="odoo",
        parameters={
            "type": "invoice",
            "amount": 1500.00,
            "customer": "Test Customer"
        }
    )

    print(f"Created operation: {operation_id}")

    # Get queue status
    status = queue_service.get_queue_status()
    print(f"Queue status: {status}")

    # Process queue
    results = queue_service.process_queue()
    print(f"Processing results: {results}")
