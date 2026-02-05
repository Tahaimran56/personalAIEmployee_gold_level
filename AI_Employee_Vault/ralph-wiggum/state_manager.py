"""
State Manager for Ralph Wiggum Autonomous Loop

This module manages task execution state for multi-step tasks.
It tracks:
- Task progress (completed steps, current step, remaining steps)
- Iteration count
- Task status (pending, in_progress, completed, blocked, failed)
- Task file location (determines state)

Author: AI Employee Gold Tier
Created: 2026-02-05
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages task execution state for Ralph Wiggum autonomous loop.

    Task state is determined by file location:
    - Needs_Action/ → pending
    - In_Progress/ → in_progress
    - Done/ → completed
    - Blocked/ → blocked
    """

    def __init__(self, vault_dir: str = "AI_Employee_Vault"):
        """
        Initialize the StateManager.

        Args:
            vault_dir: Root directory of the AI Employee vault
        """
        self.vault_dir = Path(vault_dir)

        # Task directories
        self.needs_action_dir = self.vault_dir / "Needs_Action"
        self.in_progress_dir = self.vault_dir / "In_Progress"
        self.done_dir = self.vault_dir / "Done"
        self.blocked_dir = self.vault_dir / "Blocked"

        # Ensure directories exist
        for directory in [self.needs_action_dir, self.in_progress_dir, self.done_dir, self.blocked_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        logger.info("StateManager initialized")

    def initialize_task(
        self,
        task_name: str,
        total_steps: int,
        steps: List[str],
        max_iterations: int = 10
    ) -> Dict[str, Any]:
        """
        Initialize a new task for autonomous execution.

        Args:
            task_name: Human-readable task name
            total_steps: Total number of steps in task
            steps: List of step descriptions
            max_iterations: Maximum iterations before stopping

        Returns:
            dict: Task state
        """
        task_id = f"task-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        task_state = {
            "task_id": task_id,
            "task_name": task_name,
            "status": "pending",
            "total_steps": total_steps,
            "completed_steps": [],
            "current_step": 1,
            "remaining_steps": [{"step_number": i+1, "step_description": step} for i, step in enumerate(steps)],
            "iteration_count": 0,
            "max_iterations": max_iterations,
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "blocked_reason": None,
            "error_message": None
        }

        # Create task file in Needs_Action
        task_file = self.needs_action_dir / f"{task_id}.md"
        self._write_task_file(task_file, task_state)

        logger.info(f"Initialized task: {task_id} ({task_name})")
        return task_state

    def mark_step_complete(
        self,
        task_id: str,
        step_number: int,
        step_description: str,
        duration_seconds: int
    ) -> bool:
        """
        Mark a step as complete and update task state.

        Args:
            task_id: Task identifier
            step_number: Step number that was completed
            step_description: Description of completed step
            duration_seconds: How long the step took

        Returns:
            bool: True if successful, False otherwise
        """
        task_file = self._find_task_file(task_id)

        if not task_file:
            logger.error(f"Task not found: {task_id}")
            return False

        task_state = self._read_task_file(task_file)

        # Add to completed steps
        task_state["completed_steps"].append({
            "step_number": step_number,
            "step_description": step_description,
            "completed_at": datetime.now().isoformat(),
            "duration_seconds": duration_seconds
        })

        # Remove from remaining steps
        task_state["remaining_steps"] = [
            step for step in task_state["remaining_steps"]
            if step["step_number"] != step_number
        ]

        # Update current step
        if task_state["remaining_steps"]:
            task_state["current_step"] = task_state["remaining_steps"][0]["step_number"]
        else:
            task_state["current_step"] = None

        # Increment iteration count
        task_state["iteration_count"] += 1

        # Write updated state
        self._write_task_file(task_file, task_state)

        logger.info(f"Step {step_number} completed for task {task_id}")
        return True

    def is_task_complete(self, task_id: str) -> bool:
        """
        Check if a task is complete (all steps done).

        Args:
            task_id: Task identifier

        Returns:
            bool: True if complete, False otherwise
        """
        task_file = self._find_task_file(task_id)

        if not task_file:
            return False

        task_state = self._read_task_file(task_file)

        # Task is complete if no remaining steps
        is_complete = len(task_state["remaining_steps"]) == 0

        if is_complete and task_state["status"] != "completed":
            # Move to Done and mark as completed
            self._move_task_to_done(task_id, task_state)

        return is_complete

    def get_task_state(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get current state of a task.

        Args:
            task_id: Task identifier

        Returns:
            dict: Task state or None if not found
        """
        task_file = self._find_task_file(task_id)

        if not task_file:
            return None

        return self._read_task_file(task_file)

    def move_to_in_progress(self, task_id: str) -> bool:
        """
        Move task from Needs_Action to In_Progress.

        Args:
            task_id: Task identifier

        Returns:
            bool: True if successful, False otherwise
        """
        task_file = self._find_task_file(task_id)

        if not task_file:
            logger.error(f"Task not found: {task_id}")
            return False

        # Only move if currently in Needs_Action
        if task_file.parent != self.needs_action_dir:
            logger.warning(f"Task {task_id} not in Needs_Action, skipping move")
            return False

        task_state = self._read_task_file(task_file)
        task_state["status"] = "in_progress"

        # Move file
        new_file = self.in_progress_dir / task_file.name
        self._write_task_file(new_file, task_state)
        task_file.unlink()

        logger.info(f"Moved task {task_id} to In_Progress")
        return True

    def mark_task_blocked(self, task_id: str, reason: str) -> bool:
        """
        Mark task as blocked and move to Blocked directory.

        Args:
            task_id: Task identifier
            reason: Why the task is blocked

        Returns:
            bool: True if successful, False otherwise
        """
        task_file = self._find_task_file(task_id)

        if not task_file:
            logger.error(f"Task not found: {task_id}")
            return False

        task_state = self._read_task_file(task_file)
        task_state["status"] = "blocked"
        task_state["blocked_reason"] = reason

        # Move to Blocked
        new_file = self.blocked_dir / task_file.name
        self._write_task_file(new_file, task_state)
        task_file.unlink()

        logger.warning(f"Task {task_id} marked as blocked: {reason}")
        return True

    def mark_task_failed(self, task_id: str, error_message: str) -> bool:
        """
        Mark task as failed.

        Args:
            task_id: Task identifier
            error_message: Error details

        Returns:
            bool: True if successful, False otherwise
        """
        task_file = self._find_task_file(task_id)

        if not task_file:
            logger.error(f"Task not found: {task_id}")
            return False

        task_state = self._read_task_file(task_file)
        task_state["status"] = "failed"
        task_state["error_message"] = error_message

        # Keep in current location but update status
        self._write_task_file(task_file, task_state)

        logger.error(f"Task {task_id} marked as failed: {error_message}")
        return True

    def _move_task_to_done(self, task_id: str, task_state: Dict[str, Any]) -> None:
        """Move completed task to Done directory."""
        task_file = self._find_task_file(task_id)

        if not task_file:
            return

        task_state["status"] = "completed"
        task_state["completed_at"] = datetime.now().isoformat()

        # Move to Done
        new_file = self.done_dir / task_file.name
        self._write_task_file(new_file, task_state)
        task_file.unlink()

        logger.info(f"Task {task_id} completed and moved to Done")

    def _find_task_file(self, task_id: str) -> Optional[Path]:
        """Find task file across all directories."""
        for directory in [self.needs_action_dir, self.in_progress_dir, self.done_dir, self.blocked_dir]:
            task_file = directory / f"{task_id}.md"
            if task_file.exists():
                return task_file

        return None

    def _read_task_file(self, task_file: Path) -> Dict[str, Any]:
        """Read task state from markdown file."""
        with open(task_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse frontmatter (simplified JSON parsing)
        if content.startswith('```json'):
            # Extract JSON from code block
            json_end = content.find('```', 7)
            json_str = content[7:json_end].strip()
            return json.loads(json_str)
        else:
            # Legacy format or error
            logger.warning(f"Task file {task_file.name} has unexpected format")
            return {}

    def _write_task_file(self, task_file: Path, task_state: Dict[str, Any]) -> None:
        """Write task state to markdown file."""
        content = f"""```json
{json.dumps(task_state, indent=2)}
```

# Task: {task_state['task_name']}

**Status**: {task_state['status']}
**Progress**: {len(task_state['completed_steps'])}/{task_state['total_steps']} steps completed
**Iteration**: {task_state['iteration_count']}/{task_state['max_iterations']}

## Completed Steps

"""

        for step in task_state['completed_steps']:
            content += f"- ✓ Step {step['step_number']}: {step['step_description']} (completed {step['completed_at']})\n"

        content += "\n## Remaining Steps\n\n"

        for step in task_state['remaining_steps']:
            content += f"- ☐ Step {step['step_number']}: {step['step_description']}\n"

        if task_state.get('blocked_reason'):
            content += f"\n## Blocked\n\n**Reason**: {task_state['blocked_reason']}\n"

        if task_state.get('error_message'):
            content += f"\n## Error\n\n**Message**: {task_state['error_message']}\n"

        with open(task_file, 'w', encoding='utf-8') as f:
            f.write(content)


# Example usage
if __name__ == "__main__":
    # Initialize state manager
    state_manager = StateManager()

    # Create a test task
    task_state = state_manager.initialize_task(
        task_name="Process all emails in Needs_Action",
        total_steps=3,
        steps=[
            "Read all emails from Needs_Action folder",
            "Generate responses for each email",
            "Send responses and move emails to Done"
        ]
    )

    print(f"✓ Task initialized: {task_state['task_id']}")

    # Move to In_Progress
    state_manager.move_to_in_progress(task_state['task_id'])
    print(f"✓ Task moved to In_Progress")

    # Mark first step complete
    state_manager.mark_step_complete(
        task_state['task_id'],
        step_number=1,
        step_description="Read all emails from Needs_Action folder",
        duration_seconds=30
    )
    print(f"✓ Step 1 completed")

    # Check if complete
    is_complete = state_manager.is_task_complete(task_state['task_id'])
    print(f"Task complete: {is_complete}")
