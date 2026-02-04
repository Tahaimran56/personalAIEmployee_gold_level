"""
Base Watcher Class for Silver Tier
Extends Bronze tier BaseWatcher with enhanced error handling
"""

import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
import json


class BaseWatcher(ABC):
    """
    Abstract base class for all watchers in Silver tier.
    Provides common functionality for file monitoring, logging, and error handling.
    """

    def __init__(self, vault_path: str, check_interval: int = 60):
        """
        Initialize the base watcher.

        Args:
            vault_path: Path to the Obsidian vault
            check_interval: How often to check for updates (seconds)
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = self._setup_logger()

        # Ensure required directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)

    def _setup_logger(self) -> logging.Logger:
        """Set up logging for this watcher."""
        logger = logging.getLogger(self.__class__.__name__)
        logger.setLevel(logging.INFO)

        # Create logs directory if it doesn't exist
        log_dir = self.vault_path / 'Logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        # File handler
        log_file = log_dir / f'{self.__class__.__name__.lower()}.log'
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    @abstractmethod
    def check_for_updates(self):
        """
        Check for new items to process.
        Must be implemented by subclasses.
        """
        pass

    @abstractmethod
    def create_action_file(self, data: dict) -> Path:
        """
        Create an action file in Needs_Action folder.
        Must be implemented by subclasses.

        Args:
            data: Dictionary containing action file data

        Returns:
            Path to the created action file
        """
        pass

    def handle_error(self, error: Exception, context: str = ""):
        """
        Handle errors with appropriate logging and retry logic.

        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
        """
        error_type = type(error).__name__
        error_msg = str(error)

        # Log the error
        self.logger.error(f"{context} - {error_type}: {error_msg}")

        # Determine if error is retryable
        retryable_errors = [
            'ConnectionError',
            'Timeout',
            'HTTPError',  # For 429, 500, 503
            'RequestException'
        ]

        if error_type in retryable_errors:
            self.logger.info("Error is retryable. Will retry on next cycle.")
            return True
        else:
            self.logger.error("Error is not retryable. Manual intervention required.")
            return False

    def exponential_backoff(self, attempt: int, base_delay: int = 1, max_delay: int = 60) -> int:
        """
        Calculate exponential backoff delay.

        Args:
            attempt: Current attempt number (0-indexed)
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds

        Returns:
            Delay in seconds
        """
        delay = min(base_delay * (2 ** attempt), max_delay)
        self.logger.info(f"Backing off for {delay} seconds (attempt {attempt + 1})")
        return delay

    def run(self):
        """
        Main run loop for the watcher.
        Continuously checks for updates at the specified interval.
        """
        self.logger.info(f"{self.__class__.__name__} started")
        self.logger.info(f"Checking every {self.check_interval} seconds")

        while True:
            try:
                self.check_for_updates()
                time.sleep(self.check_interval)
            except KeyboardInterrupt:
                self.logger.info("Watcher stopped by user")
                break
            except Exception as e:
                retryable = self.handle_error(e, "Main loop error")
                if retryable:
                    # Wait before retrying
                    time.sleep(self.check_interval)
                else:
                    # Fatal error, exit
                    self.logger.error("Fatal error encountered. Exiting.")
                    break

    def create_markdown_file(self, file_path: Path, frontmatter: dict, body: str):
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
            if isinstance(value, list):
                yaml_lines.append(f'{key}:')
                for item in value:
                    yaml_lines.append(f'  - {item}')
            elif isinstance(value, dict):
                yaml_lines.append(f'{key}:')
                for k, v in value.items():
                    yaml_lines.append(f'  {k}: {v}')
            else:
                yaml_lines.append(f'{key}: {value}')
        yaml_lines.append('---')
        yaml_lines.append('')

        # Combine frontmatter and body
        content = '\n'.join(yaml_lines) + body

        # Write file
        file_path.write_text(content, encoding='utf-8')
        self.logger.info(f"Created action file: {file_path}")
