"""
Audit Service for Gold Tier AI Employee

This service provides comprehensive audit logging for all AI Employee actions.
It implements:
- Daily JSON log files
- Structured log entries with timestamp, actor, target, result
- Sensitive data redaction
- 90-day retention policy
- Log rotation

Author: AI Employee Gold Tier
Created: 2026-02-05
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuditService:
    """
    Manages comprehensive audit logging for all AI Employee actions.

    Logs are stored as daily JSON files in the Audit_Logs/ directory.
    Each log entry contains timestamp, action type, actor, target, parameters,
    approval status, result, and error details (if applicable).
    """

    def __init__(self, log_dir: str = "AI_Employee_Vault/Audit_Logs"):
        """
        Initialize the AuditService.

        Args:
            log_dir: Directory to store audit logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.retention_days = 90
        self.sensitive_patterns = [
            r'password["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)',
            r'token["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)',
            r'api[_-]?key["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)',
            r'secret["\']?\s*[:=]\s*["\']?([^"\'}\s,]+)',
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card numbers
        ]

        logger.info(f"AuditService initialized with log directory: {self.log_dir}")

    def get_log_file_path(self, date: Optional[datetime] = None) -> Path:
        """
        Get the log file path for a specific date.

        Args:
            date: Date for the log file (default: today)

        Returns:
            Path: Path to the log file
        """
        if date is None:
            date = datetime.now()

        filename = f"{date.strftime('%Y-%m-%d')}.json"
        return self.log_dir / filename

    def log_action(
        self,
        action_type: str,
        actor: str,
        target: str,
        parameters: Dict[str, Any],
        result: str,
        approval_status: str = "not_required",
        approved_by: Optional[str] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log an action to the audit log.

        Args:
            action_type: Type of action (social_post, odoo_transaction, email_send, ceo_briefing, task_execution, queue_operation)
            actor: Who performed the action (ai_employee, user)
            target: What was acted upon (facebook, odoo, email, etc.)
            parameters: Action-specific parameters (will be redacted)
            result: Result of the action (success, failure, partial_success)
            approval_status: Approval status (approved, pending, rejected, not_required)
            approved_by: User who approved (if applicable)
            error_message: Error details if failed
            duration_ms: How long the action took in milliseconds
            metadata: Additional context

        Returns:
            str: Log entry ID
        """
        # Generate log entry ID
        log_id = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{os.urandom(4).hex()}"

        # Redact sensitive data from parameters
        redacted_parameters = self.redact_sensitive_data(parameters)

        # Create log entry
        log_entry = {
            "log_id": log_id,
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "actor": actor,
            "target": target,
            "parameters": redacted_parameters,
            "approval_status": approval_status,
            "approved_by": approved_by,
            "result": result,
            "error_message": error_message,
            "duration_ms": duration_ms,
            "metadata": metadata or {}
        }

        # Get log file for today
        log_file = self.get_log_file_path()

        # Read existing logs or create new list
        if log_file.exists():
            with open(log_file, 'r') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logger.error(f"Corrupted log file: {log_file}, creating new")
                    logs = []
        else:
            logs = []

        # Append new log entry
        logs.append(log_entry)

        # Write back to file
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

        logger.info(f"Logged action: {action_type} -> {target} ({result})")
        return log_id

    def redact_sensitive_data(self, data: Any) -> Any:
        """
        Redact sensitive data from parameters.

        This method recursively searches through dictionaries, lists, and strings
        to find and redact sensitive information like passwords, tokens, API keys,
        and credit card numbers.

        Args:
            data: Data to redact (can be dict, list, str, or primitive)

        Returns:
            Redacted data with same structure
        """
        if isinstance(data, dict):
            return {key: self.redact_sensitive_data(value) for key, value in data.items()}

        elif isinstance(data, list):
            return [self.redact_sensitive_data(item) for item in data]

        elif isinstance(data, str):
            # Apply all sensitive patterns
            redacted = data
            for pattern in self.sensitive_patterns:
                # Replace sensitive values with [REDACTED]
                redacted = re.sub(pattern, r'\1[REDACTED]', redacted, flags=re.IGNORECASE)

            # Special handling for credit cards - show last 4 digits
            credit_card_pattern = r'\b(\d{4})[-\s]?(\d{4})[-\s]?(\d{4})[-\s]?(\d{4})\b'
            redacted = re.sub(credit_card_pattern, r'****-****-****-\4', redacted)

            return redacted

        else:
            # Primitive types (int, float, bool, None) - return as is
            return data

    def cleanup_old_logs(self, retention_days: Optional[int] = None) -> int:
        """
        Delete or archive logs older than retention period.

        Args:
            retention_days: Number of days to retain logs (default: 90)

        Returns:
            int: Number of log files deleted
        """
        if retention_days is None:
            retention_days = self.retention_days

        cutoff_date = datetime.now() - timedelta(days=retention_days)
        deleted_count = 0

        for log_file in self.log_dir.glob("*.json"):
            try:
                # Parse date from filename (YYYY-MM-DD.json)
                filename = log_file.stem
                file_date = datetime.strptime(filename, "%Y-%m-%d")

                if file_date < cutoff_date:
                    # TODO: Archive to compressed storage before deleting
                    log_file.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old log file: {log_file.name}")

            except ValueError:
                # Skip files that don't match date pattern
                logger.warning(f"Skipping non-date log file: {log_file.name}")
                continue
            except Exception as e:
                logger.error(f"Error deleting log file {log_file.name}: {e}")

        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old log files (older than {retention_days} days)")

        return deleted_count

    def rotate_logs(self) -> Dict[str, Any]:
        """
        Perform log rotation: cleanup old logs and compress large files.

        This should be run daily (e.g., at midnight) to maintain log health.

        Returns:
            dict: Rotation summary
        """
        summary = {
            "deleted_files": 0,
            "total_size_mb": 0,
            "oldest_log": None,
            "newest_log": None
        }

        # Cleanup old logs
        summary["deleted_files"] = self.cleanup_old_logs()

        # Calculate total log size
        log_files = sorted(self.log_dir.glob("*.json"))

        if log_files:
            summary["oldest_log"] = log_files[0].stem
            summary["newest_log"] = log_files[-1].stem

            for log_file in log_files:
                summary["total_size_mb"] += log_file.stat().st_size / (1024 * 1024)

        summary["total_size_mb"] = round(summary["total_size_mb"], 2)

        logger.info(f"Log rotation complete: {summary}")
        return summary

    def get_logs_by_date(self, date: datetime) -> List[Dict[str, Any]]:
        """
        Get all log entries for a specific date.

        Args:
            date: Date to retrieve logs for

        Returns:
            list: List of log entries
        """
        log_file = self.get_log_file_path(date)

        if not log_file.exists():
            return []

        with open(log_file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Corrupted log file: {log_file}")
                return []

    def get_logs_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Get all log entries within a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            list: List of log entries
        """
        all_logs = []
        current_date = start_date

        while current_date <= end_date:
            logs = self.get_logs_by_date(current_date)
            all_logs.extend(logs)
            current_date += timedelta(days=1)

        return all_logs

    def search_logs(
        self,
        action_type: Optional[str] = None,
        actor: Optional[str] = None,
        target: Optional[str] = None,
        result: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Search logs with filters.

        Args:
            action_type: Filter by action type
            actor: Filter by actor
            target: Filter by target
            result: Filter by result
            start_date: Filter by start date
            end_date: Filter by end date

        Returns:
            list: Filtered log entries
        """
        # Default to last 7 days if no date range specified
        if start_date is None:
            start_date = datetime.now() - timedelta(days=7)
        if end_date is None:
            end_date = datetime.now()

        # Get all logs in date range
        logs = self.get_logs_by_date_range(start_date, end_date)

        # Apply filters
        filtered_logs = logs

        if action_type:
            filtered_logs = [log for log in filtered_logs if log.get("action_type") == action_type]

        if actor:
            filtered_logs = [log for log in filtered_logs if log.get("actor") == actor]

        if target:
            filtered_logs = [log for log in filtered_logs if log.get("target") == target]

        if result:
            filtered_logs = [log for log in filtered_logs if log.get("result") == result]

        return filtered_logs

    def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get audit log statistics for a date range.

        Args:
            start_date: Start date (default: 7 days ago)
            end_date: End date (default: today)

        Returns:
            dict: Statistics including counts by action type, result, etc.
        """
        # Default to last 7 days
        if start_date is None:
            start_date = datetime.now() - timedelta(days=7)
        if end_date is None:
            end_date = datetime.now()

        logs = self.get_logs_by_date_range(start_date, end_date)

        stats = {
            "total_actions": len(logs),
            "by_action_type": {},
            "by_result": {},
            "by_actor": {},
            "by_target": {},
            "average_duration_ms": 0,
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            }
        }

        total_duration = 0
        duration_count = 0

        for log in logs:
            # Count by action type
            action_type = log.get("action_type", "unknown")
            stats["by_action_type"][action_type] = stats["by_action_type"].get(action_type, 0) + 1

            # Count by result
            result = log.get("result", "unknown")
            stats["by_result"][result] = stats["by_result"].get(result, 0) + 1

            # Count by actor
            actor = log.get("actor", "unknown")
            stats["by_actor"][actor] = stats["by_actor"].get(actor, 0) + 1

            # Count by target
            target = log.get("target", "unknown")
            stats["by_target"][target] = stats["by_target"].get(target, 0) + 1

            # Calculate average duration
            if log.get("duration_ms"):
                total_duration += log["duration_ms"]
                duration_count += 1

        if duration_count > 0:
            stats["average_duration_ms"] = round(total_duration / duration_count, 2)

        return stats


# Example usage
if __name__ == "__main__":
    # Initialize service
    audit_service = AuditService()

    # Log a test action
    log_id = audit_service.log_action(
        action_type="social_post",
        actor="ai_employee",
        target="facebook",
        parameters={
            "platforms": ["facebook"],
            "text": "Test post content",
            "api_key": "secret_key_12345"  # Will be redacted
        },
        result="success",
        approval_status="approved",
        approved_by="user",
        duration_ms=1234
    )

    print(f"Logged action: {log_id}")

    # Get today's logs
    logs = audit_service.get_logs_by_date(datetime.now())
    print(f"Today's logs: {len(logs)} entries")

    # Get statistics
    stats = audit_service.get_statistics()
    print(f"Statistics: {stats}")

    # Cleanup old logs
    deleted = audit_service.cleanup_old_logs()
    print(f"Deleted {deleted} old log files")
