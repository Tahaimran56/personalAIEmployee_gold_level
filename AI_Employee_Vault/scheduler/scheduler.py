"""
Scheduler - Scheduled Automation
Runs watchers and tasks automatically on schedule for hands-free operation
"""

import os
import sys
import json
import platform
import subprocess
import signal
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import schedule
import time


class Scheduler:
    """
    Scheduler for running watchers and tasks automatically.

    Features:
    - Platform detection (Windows/Linux/Mac)
    - Schedule management (add, remove, list)
    - Task execution with subprocess
    - Schedule persistence to config file
    - Execution logging
    - Graceful shutdown
    - Error handling (continue on failure)
    """

    def __init__(self, vault_path: str):
        """
        Initialize Scheduler.

        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / 'Logs'
        self.config_file = Path(__file__).parent.parent.parent / 'config' / 'scheduler_config.json'

        # Ensure directories exist
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Detect platform
        self.platform = self._detect_platform()

        # Load schedules
        self.schedules = self._load_schedules()

        # Setup logging
        self.logger = self._setup_logger()

        # Shutdown flag
        self.shutdown_requested = False

        # Setup signal handlers
        self._setup_signal_handlers()

        self.logger.info(f"Scheduler initialized on {self.platform}")

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for scheduler."""
        logger = logging.getLogger('Scheduler')
        logger.setLevel(logging.INFO)

        log_file = self.logs_dir / 'scheduler.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        return logger

    def _detect_platform(self) -> str:
        """
        Detect operating system platform.

        Returns:
            Platform name: 'windows', 'linux', or 'mac'
        """
        system = platform.system().lower()

        if system == 'windows':
            return 'windows'
        elif system == 'linux':
            return 'linux'
        elif system == 'darwin':
            return 'mac'
        else:
            return 'unknown'

    def _load_schedules(self) -> Dict:
        """
        Load schedules from config file.

        Returns:
            Dict with schedule configurations
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading schedules: {e}")
                return self._get_default_schedules()
        else:
            return self._get_default_schedules()

    def _get_default_schedules(self) -> Dict:
        """
        Get default schedule configuration.

        Returns:
            Dict with default schedules
        """
        return {
            "schedules": [
                {
                    "task_name": "Gmail Watcher",
                    "task_type": "watcher",
                    "task_command": "python AI_Employee_Vault/watchers/gmail_watcher.py AI_Employee_Vault",
                    "cron_expression": "*/5 * * * *",
                    "interval_minutes": 5,
                    "enabled": True,
                    "description": "Check Gmail inbox for new emails every 5 minutes"
                },
                {
                    "task_name": "LinkedIn Watcher",
                    "task_type": "watcher",
                    "task_command": "python AI_Employee_Vault/watchers/linkedin_watcher.py AI_Employee_Vault",
                    "cron_expression": "0 * * * *",
                    "interval_minutes": 60,
                    "enabled": False,
                    "description": "Check LinkedIn notifications every hour (optional)"
                },
                {
                    "task_name": "Process Actions",
                    "task_type": "skill",
                    "task_command": "python AI_Employee_Vault/skills/process_actions.py AI_Employee_Vault",
                    "cron_expression": "*/5 * * * *",
                    "interval_minutes": 5,
                    "enabled": True,
                    "description": "Process action files every 5 minutes"
                },
                {
                    "task_name": "Check Expired Approvals",
                    "task_type": "service",
                    "task_command": "python AI_Employee_Vault/services/approval_service.py AI_Employee_Vault --check-expired",
                    "cron_expression": "0 */6 * * *",
                    "interval_minutes": 360,
                    "enabled": True,
                    "description": "Check for expired approval requests every 6 hours"
                }
            ],
            "global_settings": {
                "max_concurrent_tasks": 1,
                "task_timeout_seconds": 300,
                "retry_on_failure": True,
                "max_retries": 3,
                "log_level": "INFO"
            }
        }

    def _save_schedules(self):
        """Save schedules to config file."""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.schedules, f, indent=2)
            self.logger.info("Schedules saved to config file")
        except Exception as e:
            self.logger.error(f"Error saving schedules: {e}")

    def add_schedule(self, task_name: str, task_command: str,
                    interval_minutes: int, task_type: str = "custom",
                    enabled: bool = True, description: str = "") -> Dict:
        """
        Add a new scheduled task.

        Args:
            task_name: Name of the task
            task_command: Command to execute
            interval_minutes: Interval in minutes
            task_type: Type of task (watcher, skill, service, custom)
            enabled: Whether task is enabled
            description: Task description

        Returns:
            Dict with schedule details
        """
        self.logger.info(f"Adding schedule: {task_name}")

        # Generate cron expression from interval
        cron_expression = self._interval_to_cron(interval_minutes)

        # Create schedule entry
        schedule_entry = {
            "task_name": task_name,
            "task_type": task_type,
            "task_command": task_command,
            "cron_expression": cron_expression,
            "interval_minutes": interval_minutes,
            "enabled": enabled,
            "description": description,
            "created_timestamp": datetime.utcnow().isoformat() + 'Z'
        }

        # Add to schedules
        if "schedules" not in self.schedules:
            self.schedules["schedules"] = []

        self.schedules["schedules"].append(schedule_entry)

        # Save to config
        self._save_schedules()

        self.logger.info(f"Schedule added: {task_name}")

        return schedule_entry

    def execute_scheduled_task(self, task_command: str, task_name: str) -> Dict:
        """
        Execute a scheduled task using subprocess.

        Args:
            task_command: Command to execute
            task_name: Name of the task

        Returns:
            Dict with execution result
        """
        self.logger.info(f"Executing task: {task_name}")

        start_time = datetime.utcnow()

        try:
            # Get timeout from global settings
            timeout = self.schedules.get('global_settings', {}).get('task_timeout_seconds', 300)

            # Execute command
            result = subprocess.run(
                task_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(Path(__file__).parent.parent.parent)
            )

            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()

            # Log execution
            execution_result = {
                'success': result.returncode == 0,
                'task_name': task_name,
                'task_command': task_command,
                'return_code': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'duration_seconds': duration,
                'start_time': start_time.isoformat() + 'Z',
                'end_time': end_time.isoformat() + 'Z'
            }

            if result.returncode == 0:
                self.logger.info(f"Task completed successfully: {task_name} ({duration:.2f}s)")
            else:
                self.logger.error(f"Task failed: {task_name} (exit code: {result.returncode})")
                self.logger.error(f"Error output: {result.stderr}")

            return execution_result

        except subprocess.TimeoutExpired:
            self.logger.error(f"Task timed out: {task_name}")
            return {
                'success': False,
                'task_name': task_name,
                'error': 'Task execution timed out',
                'start_time': start_time.isoformat() + 'Z'
            }
        except Exception as e:
            self.logger.error(f"Error executing task {task_name}: {e}")
            return {
                'success': False,
                'task_name': task_name,
                'error': str(e),
                'start_time': start_time.isoformat() + 'Z'
            }

    def run(self):
        """
        Run the scheduler (blocking).
        Executes scheduled tasks at their specified intervals.
        """
        self.logger.info("Starting scheduler...")

        # Register scheduled tasks
        for schedule_entry in self.schedules.get('schedules', []):
            if not schedule_entry.get('enabled', True):
                self.logger.info(f"Skipping disabled task: {schedule_entry['task_name']}")
                continue

            task_name = schedule_entry['task_name']
            task_command = schedule_entry['task_command']
            interval_minutes = schedule_entry['interval_minutes']

            # Schedule task
            schedule.every(interval_minutes).minutes.do(
                self.execute_scheduled_task,
                task_command=task_command,
                task_name=task_name
            )

            self.logger.info(f"Scheduled: {task_name} (every {interval_minutes} minutes)")

        # Run scheduler loop
        self.logger.info("Scheduler running. Press Ctrl+C to stop.")

        while not self.shutdown_requested:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                self.logger.info("Keyboard interrupt received")
                break
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                # Continue running on error
                time.sleep(5)

        self.logger.info("Scheduler stopped")

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down gracefully...")
            self.shutdown_requested = True

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

    def _interval_to_cron(self, interval_minutes: int) -> str:
        """
        Convert interval in minutes to cron expression.

        Args:
            interval_minutes: Interval in minutes

        Returns:
            Cron expression string
        """
        if interval_minutes < 60:
            # Every N minutes
            return f"*/{interval_minutes} * * * *"
        elif interval_minutes == 60:
            # Every hour
            return "0 * * * *"
        elif interval_minutes % 60 == 0:
            # Every N hours
            hours = interval_minutes // 60
            return f"0 */{hours} * * *"
        else:
            # Complex interval, use minutes
            return f"*/{interval_minutes} * * * *"

    def list_schedules(self) -> List[Dict]:
        """
        List all scheduled tasks.

        Returns:
            List of schedule entries
        """
        return self.schedules.get('schedules', [])

    def remove_schedule(self, task_name: str) -> bool:
        """
        Remove a scheduled task.

        Args:
            task_name: Name of task to remove

        Returns:
            True if removed, False if not found
        """
        schedules = self.schedules.get('schedules', [])
        original_count = len(schedules)

        # Filter out the task
        self.schedules['schedules'] = [
            s for s in schedules if s['task_name'] != task_name
        ]

        if len(self.schedules['schedules']) < original_count:
            self._save_schedules()
            self.logger.info(f"Removed schedule: {task_name}")
            return True
        else:
            self.logger.warning(f"Schedule not found: {task_name}")
            return False


def main():
    """Main entry point for scheduler."""
    import sys

    # Get vault path from command line or use default
    if len(sys.argv) > 1:
        vault_path = sys.argv[1]
    else:
        vault_path = Path(__file__).parent.parent

    # Create and run scheduler
    scheduler = Scheduler(str(vault_path))

    try:
        scheduler.run()
    except KeyboardInterrupt:
        print("\nScheduler stopped by user")
    except Exception as e:
        print(f"Scheduler error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
