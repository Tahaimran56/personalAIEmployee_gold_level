"""
Approval Service - Enhanced Approval Workflow
Manages approval requests for sensitive actions (email send, LinkedIn post, file delete)
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dotenv import load_dotenv
import logging


class ApprovalService:
    """
    Approval service for managing sensitive action approvals.

    Features:
    - Action classification (sensitive vs non-sensitive)
    - Approval request creation
    - Approval status monitoring
    - Approved action execution
    - Rejection handling
    - 24-hour timeout with auto-rejection
    - Comprehensive logging
    """

    # Sensitive action types requiring approval
    SENSITIVE_ACTIONS = {
        'email_send',
        'linkedin_post',
        'file_delete',
        'api_call_external',
        'data_export',
        'system_command'
    }

    def __init__(self, vault_path: str):
        """
        Initialize Approval Service.

        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.logs = self.vault_path / 'Logs'

        # Ensure directories exist
        self.pending_approval.mkdir(parents=True, exist_ok=True)
        self.approved.mkdir(parents=True, exist_ok=True)
        self.rejected.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = self._setup_logger()

        self.logger.info("Approval Service initialized")

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for approval service."""
        logger = logging.getLogger('ApprovalService')
        logger.setLevel(logging.INFO)

        log_file = self.logs / 'approval.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        return logger

    def classify_action(self, action_type: str, action_details: Dict) -> Dict:
        """
        Determine if action is sensitive and requires approval.

        Args:
            action_type: Type of action (email_send, linkedin_post, etc.)
            action_details: Details about the action

        Returns:
            Dict with is_sensitive, reason, approval_required
        """
        self.logger.info(f"Classifying action: {action_type}")

        # Check if action type is in sensitive list
        is_sensitive = action_type in self.SENSITIVE_ACTIONS

        # Additional checks based on action details
        reason = ""
        if is_sensitive:
            if action_type == 'email_send':
                reason = "Email sending requires approval to prevent unauthorized communication"
            elif action_type == 'linkedin_post':
                reason = "LinkedIn posting requires approval to maintain professional reputation"
            elif action_type == 'file_delete':
                reason = "File deletion requires approval to prevent data loss"
            elif action_type == 'api_call_external':
                reason = "External API calls require approval for security"
            elif action_type == 'data_export':
                reason = "Data export requires approval to protect sensitive information"
            elif action_type == 'system_command':
                reason = "System commands require approval for security"
            else:
                reason = "Action classified as sensitive"

        # Check for additional sensitivity factors
        if not is_sensitive:
            # Check for large data operations
            if action_details.get('data_size_mb', 0) > 100:
                is_sensitive = True
                reason = "Large data operation (>100MB) requires approval"

            # Check for external recipients
            if action_type == 'email_send':
                recipient = action_details.get('recipient', '')
                if not self._is_internal_email(recipient):
                    is_sensitive = True
                    reason = "Email to external recipient requires approval"

        self.logger.info(f"Action classified: sensitive={is_sensitive}, reason={reason}")

        return {
            'is_sensitive': is_sensitive,
            'reason': reason,
            'approval_required': is_sensitive
        }

    def create_approval_request(self, action_type: str, action_description: str,
                               action_details: Dict, related_entity_id: str = None) -> Dict:
        """
        Create approval request file in Pending_Approval/ folder.

        Args:
            action_type: Type of action (email_send, linkedin_post, etc.)
            action_description: Human-readable description
            action_details: Detailed action data (JSON)
            related_entity_id: ID of related entity (draft_id, post_id, etc.)

        Returns:
            Dict with request_id, request_file_path, expiry_timestamp
        """
        self.logger.info(f"Creating approval request for {action_type}")

        # Generate request ID
        request_id = f"req-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        # Calculate expiry (24 hours from now)
        created_timestamp = datetime.utcnow()
        expiry_timestamp = created_timestamp + timedelta(hours=24)

        # Create approval request file
        request_file = self.pending_approval / f"{action_type}-{request_id}.md"

        # Build frontmatter
        frontmatter = {
            'entity_type': 'approval_request',
            'request_id': request_id,
            'action_type': action_type,
            'action_description': action_description,
            'created_timestamp': created_timestamp.isoformat() + 'Z',
            'approval_status': 'pending',
            'expiry_timestamp': expiry_timestamp.isoformat() + 'Z'
        }

        if related_entity_id:
            frontmatter['related_entity_id'] = related_entity_id

        # Build body
        body = f"""
# Approval Request: {action_description}

**Action Type**: {action_type}
**Status**: ⏳ Pending Approval
**Created**: {created_timestamp.strftime('%Y-%m-%d %I:%M %p')}
**Expires**: {expiry_timestamp.strftime('%Y-%m-%d %I:%M %p')} (24 hours)

## Action Details

{self._format_action_details(action_details)}

## Approval Actions

### ✅ To Approve
Move this file to the `Approved/` folder

### ❌ To Reject
Move this file to the `Rejected/` folder and add rejection reason below:

**Rejection Reason**: [Enter reason here]

---

## Important Notes

- **Automatic Expiry**: This request will automatically expire and be rejected after 24 hours
- **Review Carefully**: Ensure all details are correct before approving
- **Security**: Sensitive actions require explicit approval to prevent unauthorized operations
- **Logging**: All approvals and rejections are logged for audit purposes

## Related Entity

"""

        if related_entity_id:
            body += f"**Related Entity ID**: {related_entity_id}\n"
            body += f"**Entity Location**: Check Pending_Approval/ or Approved/ folders\n"
        else:
            body += "No related entity\n"

        # Write file
        self._create_markdown_file(request_file, frontmatter, body)

        self.logger.info(f"Approval request created: {request_file}")

        return {
            'request_id': request_id,
            'request_file_path': str(request_file),
            'expiry_timestamp': expiry_timestamp.isoformat() + 'Z',
            'status': 'pending'
        }

    def check_approval_status(self, request_id: str) -> Dict:
        """
        Check approval status by monitoring folder location.

        Args:
            request_id: Request ID to check

        Returns:
            Dict with approval_status, approver, approval_timestamp, rejection_reason
        """
        self.logger.info(f"Checking approval status for {request_id}")

        # Search for request file in all folders
        request_file = None
        status = None

        # Check Pending_Approval
        for file in self.pending_approval.glob(f"*-{request_id}.md"):
            request_file = file
            status = 'pending'
            break

        # Check Approved
        if not request_file:
            for file in self.approved.glob(f"*-{request_id}.md"):
                request_file = file
                status = 'approved'
                break

        # Check Rejected
        if not request_file:
            for file in self.rejected.glob(f"*-{request_id}.md"):
                request_file = file
                status = 'rejected'
                break

        if not request_file:
            raise FileNotFoundError(f"Approval request not found: {request_id}")

        # Parse file to get details
        request_data = self._parse_approval_file(request_file)

        # Check for expiry
        expiry_timestamp = datetime.fromisoformat(request_data.get('expiry_timestamp', '').replace('Z', ''))
        if datetime.utcnow() > expiry_timestamp and status == 'pending':
            # Auto-reject expired request
            self.logger.warning(f"Request {request_id} expired, auto-rejecting")
            self._auto_reject_expired(request_file, request_data)
            status = 'expired'

        self.logger.info(f"Request {request_id} status: {status}")

        return {
            'request_id': request_id,
            'approval_status': status,
            'approver': request_data.get('approver', 'user'),
            'approval_timestamp': request_data.get('approval_timestamp'),
            'rejection_reason': request_data.get('rejection_reason'),
            'action_type': request_data.get('action_type'),
            'action_description': request_data.get('action_description')
        }

    def execute_approved_action(self, request_id: str) -> Dict:
        """
        Execute an approved action and log the result.

        Args:
            request_id: Request ID to execute

        Returns:
            Dict with success status, execution_timestamp, log_file_path
        """
        self.logger.info(f"Executing approved action: {request_id}")

        # Check approval status
        status = self.check_approval_status(request_id)

        if status['approval_status'] != 'approved':
            raise ValueError(f"Action not approved: {request_id} (status: {status['approval_status']})")

        # Find approved file
        request_file = None
        for file in self.approved.glob(f"*-{request_id}.md"):
            request_file = file
            break

        if not request_file:
            raise FileNotFoundError(f"Approved request file not found: {request_id}")

        # Parse request data
        request_data = self._parse_approval_file(request_file)

        # Execute action based on type
        action_type = request_data.get('action_type')
        execution_timestamp = datetime.utcnow().isoformat() + 'Z'

        try:
            # Placeholder for actual execution
            # In real implementation, this would call appropriate services
            result = {
                'success': True,
                'message': f"Action {action_type} executed successfully",
                'execution_timestamp': execution_timestamp
            }

            # Log execution
            self._log_execution(request_id, action_type, result)

            # Move to Done folder
            done_folder = self.vault_path / 'Done'
            done_folder.mkdir(parents=True, exist_ok=True)
            request_file.rename(done_folder / request_file.name)

            self.logger.info(f"Action executed successfully: {request_id}")

            return {
                'success': True,
                'request_id': request_id,
                'action_type': action_type,
                'execution_timestamp': execution_timestamp,
                'log_file_path': str(self.logs / f"execution-{request_id}.log")
            }

        except Exception as e:
            self.logger.error(f"Error executing action {request_id}: {e}")
            self._log_execution(request_id, action_type, {
                'success': False,
                'error': str(e),
                'execution_timestamp': execution_timestamp
            })
            raise

    def handle_rejection(self, request_id: str, rejection_reason: str = "") -> Dict:
        """
        Handle rejected approval request.

        Args:
            request_id: Request ID that was rejected
            rejection_reason: Reason for rejection

        Returns:
            Dict with success status, rejection_timestamp
        """
        self.logger.info(f"Handling rejection for {request_id}")

        # Find rejected file
        request_file = None
        for file in self.rejected.glob(f"*-{request_id}.md"):
            request_file = file
            break

        if not request_file:
            raise FileNotFoundError(f"Rejected request file not found: {request_id}")

        # Parse request data
        request_data = self._parse_approval_file(request_file)

        # Update file with rejection details
        rejection_timestamp = datetime.utcnow().isoformat() + 'Z'

        # Log rejection
        self._log_rejection(request_id, request_data.get('action_type'), rejection_reason)

        # Archive to Done folder
        done_folder = self.vault_path / 'Done'
        done_folder.mkdir(parents=True, exist_ok=True)
        request_file.rename(done_folder / request_file.name)

        self.logger.info(f"Rejection handled: {request_id}")

        return {
            'success': True,
            'request_id': request_id,
            'rejection_timestamp': rejection_timestamp,
            'rejection_reason': rejection_reason
        }

    def check_expired_requests(self) -> List[str]:
        """
        Check for expired approval requests and auto-reject them.

        Returns:
            List of expired request IDs
        """
        self.logger.info("Checking for expired approval requests")

        expired_requests = []
        current_time = datetime.utcnow()

        # Check all pending requests
        for request_file in self.pending_approval.glob("*.md"):
            try:
                request_data = self._parse_approval_file(request_file)
                expiry_timestamp = datetime.fromisoformat(
                    request_data.get('expiry_timestamp', '').replace('Z', '')
                )

                if current_time > expiry_timestamp:
                    # Auto-reject
                    request_id = request_data.get('request_id')
                    self.logger.warning(f"Auto-rejecting expired request: {request_id}")
                    self._auto_reject_expired(request_file, request_data)
                    expired_requests.append(request_id)

            except Exception as e:
                self.logger.error(f"Error checking expiry for {request_file}: {e}")

        self.logger.info(f"Found {len(expired_requests)} expired requests")
        return expired_requests

    def _auto_reject_expired(self, request_file: Path, request_data: Dict):
        """
        Auto-reject an expired request.

        Args:
            request_file: Path to request file
            request_data: Request data
        """
        # Move to Rejected folder
        rejected_file = self.rejected / request_file.name
        request_file.rename(rejected_file)

        # Log rejection
        self._log_rejection(
            request_data.get('request_id'),
            request_data.get('action_type'),
            "Automatically rejected: 24-hour timeout expired"
        )

    def _is_internal_email(self, email: str) -> bool:
        """
        Check if email is internal (same domain).

        Args:
            email: Email address

        Returns:
            True if internal, False otherwise
        """
        # Placeholder - in real implementation, check against company domain
        # For now, consider all emails as external (requiring approval)
        return False

    def _format_action_details(self, action_details: Dict) -> str:
        """
        Format action details for display.

        Args:
            action_details: Action details dictionary

        Returns:
            Formatted string
        """
        formatted = ""
        for key, value in action_details.items():
            # Format key (convert snake_case to Title Case)
            formatted_key = key.replace('_', ' ').title()

            # Format value
            if isinstance(value, dict):
                formatted += f"**{formatted_key}**:\n"
                for k, v in value.items():
                    formatted += f"  - {k}: {v}\n"
            elif isinstance(value, list):
                formatted += f"**{formatted_key}**:\n"
                for item in value:
                    formatted += f"  - {item}\n"
            else:
                formatted += f"**{formatted_key}**: {value}\n"

        return formatted

    def _parse_approval_file(self, file_path: Path) -> Dict:
        """
        Parse approval request file.

        Args:
            file_path: Path to approval file

        Returns:
            Dict with approval data
        """
        content = file_path.read_text(encoding='utf-8')

        # Extract frontmatter
        approval_data = {}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter_text = parts[1]

                # Parse YAML frontmatter (simple parsing)
                for line in frontmatter_text.strip().split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        approval_data[key.strip()] = value.strip()

        return approval_data

    def _log_execution(self, request_id: str, action_type: str, result: Dict):
        """
        Log action execution.

        Args:
            request_id: Request ID
            action_type: Action type
            result: Execution result
        """
        log_file = self.logs / f"execution-{request_id}.log"

        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] Executed {action_type} (Request: {request_id})\n"
        log_entry += f"Result: {json.dumps(result, indent=2)}\n"

        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(log_entry)

        # Also log to main approval log
        with open(self.logs / 'approval.log', 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] EXECUTED: {request_id} ({action_type}) - Success: {result.get('success')}\n")

    def _log_rejection(self, request_id: str, action_type: str, reason: str):
        """
        Log action rejection.

        Args:
            request_id: Request ID
            action_type: Action type
            reason: Rejection reason
        """
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        with open(self.logs / 'approval.log', 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] REJECTED: {request_id} ({action_type}) - Reason: {reason}\n")

    def _create_markdown_file(self, file_path: Path, frontmatter: Dict, body: str):
        """
        Create a Markdown file with YAML frontmatter.

        Args:
            file_path: Path where file should be created
            frontmatter: Dictionary of frontmatter data
            body: Markdown body content
        """
        # Convert frontmatter to YAML
        yaml_lines = ['---']
        for key, value in frontmatter.items():
            yaml_lines.append(f'{key}: {value}')
        yaml_lines.append('---')
        yaml_lines.append('')

        # Combine frontmatter and body
        content = '\n'.join(yaml_lines) + body

        # Write file
        file_path.write_text(content, encoding='utf-8')


# Example usage
if __name__ == '__main__':
    import sys

    # Get vault path
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent

    # Create service
    service = ApprovalService(str(vault_path))

    # Example: Create approval request
    request = service.create_approval_request(
        action_type='email_send',
        action_description='Send email to client about project update',
        action_details={
            'recipient': 'client@example.com',
            'subject': 'Project Update',
            'body': 'Here is the latest update on your project...'
        },
        related_entity_id='draft-20260204120000'
    )

    print(f"Approval request created: {request['request_file_path']}")
    print(f"Expires: {request['expiry_timestamp']}")
