"""
Ralph Wiggum Autonomous Loop Implementation

This module implements the autonomous loop that allows the AI Employee to
complete multi-step tasks without stopping after each step.

It implements:
- Iteration tracking with max limit
- Graceful exit on completion or max iterations
- Error handling and task blocking
- Integration with stop hook
- Audit logging for all iterations

Author: AI Employee Gold Tier
Created: 2026-02-05
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from state_manager import StateManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RalphWiggumLoop:
    """
    Implements autonomous loop for multi-step task execution.

    The loop continues executing steps until:
    - All steps are complete
    - Max iterations reached
    - Error occurs
    - User input required
    """

    def __init__(self, config_path: str = "config/ralph_wiggum_config.json"):
        """
        Initialize the Ralph Wiggum Loop.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.state_manager = StateManager()

        # Configuration
        self.max_iterations = self.config.get("autonomous_loop", {}).get("max_iterations", 10)
        self.timeout_minutes = self.config.get("autonomous_loop", {}).get("timeout_minutes_per_iteration", 5)
        self.enabled = self.config.get("autonomous_loop", {}).get("enabled", True)

        logger.info(f"RalphWiggumLoop initialized (max_iterations={self.max_iterations})")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}, using defaults")
            return {}

        with open(self.config_path, 'r') as f:
            return json.load(f)

    def check_iteration_limit(self, task_id: str) -> bool:
        """
        Check if task has reached max iteration limit.

        Args:
            task_id: Task identifier

        Returns:
            bool: True if limit reached, False otherwise
        """
        task_state = self.state_manager.get_task_state(task_id)

        if not task_state:
            return False

        iteration_count = task_state.get("iteration_count", 0)
        max_iterations = task_state.get("max_iterations", self.max_iterations)

        if iteration_count >= max_iterations:
            logger.warning(f"Task {task_id} reached max iterations ({max_iterations})")
            return True

        return False

    def exit_gracefully(self, task_id: str, reason: str) -> None:
        """
        Exit the loop gracefully with logging.

        Args:
            task_id: Task identifier
            reason: Reason for exit
        """
        task_state = self.state_manager.get_task_state(task_id)

        if task_state:
            logger.info(f"Exiting loop for task {task_id}: {reason}")
            logger.info(f"Progress: {len(task_state['completed_steps'])}/{task_state['total_steps']} steps completed")
            logger.info(f"Iterations: {task_state['iteration_count']}/{task_state['max_iterations']}")

            # Audit log
            try:
                from services.audit_service import AuditService
                audit_service = AuditService()
                audit_service.log_action(
                    action_type="task_execution",
                    actor="ai_employee",
                    target="ralph_wiggum_loop",
                    parameters={
                        "task_id": task_id,
                        "task_name": task_state['task_name'],
                        "exit_reason": reason,
                        "steps_completed": len(task_state['completed_steps']),
                        "total_steps": task_state['total_steps'],
                        "iterations": task_state['iteration_count']
                    },
                    result="success" if reason == "task_complete" else "partial_success",
                    approval_status="not_required"
                )
            except Exception as e:
                logger.error(f"Failed to log loop exit: {e}")

    def handle_error(self, task_id: str, error: Exception) -> None:
        """
        Handle errors during task execution.

        Args:
            task_id: Task identifier
            error: Exception that occurred
        """
        error_message = str(error)
        logger.error(f"Error in task {task_id}: {error_message}")

        # Mark task as blocked
        self.state_manager.mark_task_blocked(task_id, f"Error: {error_message}")

        # Audit log
        try:
            from services.audit_service import AuditService
            audit_service = AuditService()
            audit_service.log_action(
                action_type="task_execution",
                actor="ai_employee",
                target="ralph_wiggum_loop",
                parameters={
                    "task_id": task_id,
                    "error": error_message
                },
                result="failure",
                error_message=error_message,
                approval_status="not_required"
            )
        except Exception as e:
            logger.error(f"Failed to log error: {e}")

    def get_current_task(self) -> Optional[Dict[str, Any]]:
        """
        Get the current task in progress.

        Returns:
            dict: Task state or None if no task in progress
        """
        in_progress_dir = Path("AI_Employee_Vault/In_Progress")

        if not in_progress_dir.exists():
            return None

        # Get first task file
        task_files = list(in_progress_dir.glob("*.md"))

        if not task_files:
            return None

        # Extract task_id from filename
        task_id = task_files[0].stem

        return self.state_manager.get_task_state(task_id)

    def should_continue(self) -> bool:
        """
        Check if the loop should continue.

        This is called by the stop hook to determine if Claude should stop.

        Returns:
            bool: True if loop should continue, False if should stop
        """
        if not self.enabled:
            return False

        # Check if any tasks in In_Progress
        task_state = self.get_current_task()

        if not task_state:
            logger.info("No tasks in progress - stopping loop")
            return False

        # Check iteration limit
        if self.check_iteration_limit(task_state['task_id']):
            self.exit_gracefully(task_state['task_id'], "max_iterations_reached")
            return False

        # Check if task is complete
        if self.state_manager.is_task_complete(task_state['task_id']):
            self.exit_gracefully(task_state['task_id'], "task_complete")
            return False

        # Check if task is blocked or failed
        if task_state['status'] in ['blocked', 'failed']:
            logger.warning(f"Task {task_state['task_id']} is {task_state['status']} - stopping loop")
            return False

        logger.info(f"Continuing loop for task {task_state['task_id']} (iteration {task_state['iteration_count']}/{task_state['max_iterations']})")
        return True

    def execute_step(self, task_id: str, step_number: int, step_description: str) -> bool:
        """
        Execute a single step of the task.

        This is a placeholder that should be overridden or extended to actually
        execute the step logic.

        Args:
            task_id: Task identifier
            step_number: Step number to execute
            step_description: Description of the step

        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Executing step {step_number}: {step_description}")

        # TODO: Implement actual step execution
        # This should call the appropriate service or function based on step_description

        # For now, just mark as complete
        start_time = time.time()

        # Simulate work
        time.sleep(1)

        duration_seconds = int(time.time() - start_time)

        # Mark step complete
        self.state_manager.mark_step_complete(
            task_id,
            step_number,
            step_description,
            duration_seconds
        )

        return True

    def run_task(self, task_id: str) -> bool:
        """
        Run a task through the autonomous loop.

        Args:
            task_id: Task identifier

        Returns:
            bool: True if task completed successfully, False otherwise
        """
        logger.info(f"Starting autonomous loop for task {task_id}")

        # Move task to In_Progress
        self.state_manager.move_to_in_progress(task_id)

        while True:
            # Check if should continue
            if not self.should_continue():
                break

            # Get current task state
            task_state = self.state_manager.get_task_state(task_id)

            if not task_state:
                logger.error(f"Task {task_id} not found")
                return False

            # Get next step
            if not task_state['remaining_steps']:
                logger.info(f"Task {task_id} complete - no remaining steps")
                break

            next_step = task_state['remaining_steps'][0]

            # Execute step
            try:
                success = self.execute_step(
                    task_id,
                    next_step['step_number'],
                    next_step['step_description']
                )

                if not success:
                    logger.error(f"Step {next_step['step_number']} failed")
                    self.handle_error(task_id, Exception("Step execution failed"))
                    return False

            except Exception as e:
                self.handle_error(task_id, e)
                return False

            # Check iteration limit
            if self.check_iteration_limit(task_id):
                self.exit_gracefully(task_id, "max_iterations_reached")
                return False

        # Check if task is complete
        is_complete = self.state_manager.is_task_complete(task_id)

        if is_complete:
            self.exit_gracefully(task_id, "task_complete")

        return is_complete


# Example usage
if __name__ == "__main__":
    # Initialize loop
    loop = RalphWiggumLoop()

    # Create a test task
    state_manager = StateManager()
    task_state = state_manager.initialize_task(
        task_name="Test Multi-Step Task",
        total_steps=3,
        steps=[
            "Step 1: Read data",
            "Step 2: Process data",
            "Step 3: Write results"
        ]
    )

    print(f"✓ Task created: {task_state['task_id']}")

    # Run task through autonomous loop
    success = loop.run_task(task_state['task_id'])

    if success:
        print(f"✓ Task completed successfully")
    else:
        print(f"✗ Task failed or incomplete")
