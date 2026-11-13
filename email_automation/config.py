"""
Configuration management for the email automation tool.
Handles loading and validating settings from JSON configuration file.
Supports dynamic path resolution for portable installation.
"""

import json
import os
import sys
from pathlib import Path


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class Config:
    """Configuration manager for email automation settings."""

    def __init__(self, config_path="config/settings.json"):
        """
        Load configuration from JSON file.

        Args:
            config_path: Path to the configuration JSON file

        Raises:
            ConfigurationError: If config file is missing or invalid
        """
        # Auto-detect installation directory (where email_automation package is)
        self.install_dir = Path(__file__).parent.parent.resolve()

        # Resolve config path relative to install_dir if it's not absolute
        if not Path(config_path).is_absolute():
            self.config_path = self.install_dir / config_path
        else:
            self.config_path = Path(config_path)

        self.data = {}
        self._load_config()
        self._validate_config()

    def _load_config(self):
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please create a settings.json file in the config/ directory.\n"
                f"See README.md for template."
            )

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigurationError(
                f"Invalid JSON in configuration file: {e}"
            )

        # Resolve all paths relative to install_dir
        self._resolve_paths()

    def _resolve_paths(self):
        """Resolve relative paths from installation directory."""
        path_keys = [
            'email_template_path',
            'attachment_path',
            'csv_folder',
            'log_directory',
            'history_file'
        ]

        for key in path_keys:
            if key in self.data:
                path_val = self.data[key]
                # Convert to Path object
                path_obj = Path(path_val)

                # If not absolute, resolve relative to install_dir
                if not path_obj.is_absolute():
                    resolved = self.install_dir / path_obj
                    self.data[key] = str(resolved)
                # If absolute, keep as is (for backward compatibility)
                else:
                    self.data[key] = str(path_obj)

    def _validate_config(self):
        """Validate that all required configuration keys are present."""
        required_keys = [
            'email_template_path',
            'email_subject',
            'attachment_path',
            'csv_folder',
            'log_directory',
            'history_file'
        ]

        missing_keys = [key for key in required_keys if key not in self.data]
        if missing_keys:
            raise ConfigurationError(
                f"Missing required configuration keys: {', '.join(missing_keys)}"
            )

    def validate_paths(self, logger=None):
        """
        Validate that all configured paths exist.

        Args:
            logger: Optional logger for detailed error messages

        Returns:
            bool: True if all paths are valid

        Raises:
            ConfigurationError: If any required path doesn't exist
        """
        errors = []

        # Check email template
        if not os.path.exists(self.email_template_path):
            errors.append(f"Email template not found: {self.email_template_path}")

        # Check attachment
        if not os.path.exists(self.attachment_path):
            errors.append(f"Attachment file not found: {self.attachment_path}")

        # Check CSV folder
        if not os.path.exists(self.csv_folder):
            errors.append(f"CSV folder not found: {self.csv_folder}")

        # Create log directory if it doesn't exist
        os.makedirs(self.log_directory, exist_ok=True)

        # Create data directory for history file if needed
        history_dir = os.path.dirname(self.history_file)
        if history_dir:
            os.makedirs(history_dir, exist_ok=True)

        if errors:
            error_msg = "\n".join(errors)
            if logger:
                logger.critical(f"Configuration path validation failed:\n{error_msg}")
            raise ConfigurationError(
                f"Configuration path validation failed:\n{error_msg}"
            )

        return True

    @property
    def email_template_path(self):
        """Get email template file path."""
        return self.data['email_template_path']

    @property
    def email_subject(self):
        """Get email subject line."""
        return self.data['email_subject']

    @property
    def attachment_path(self):
        """Get attachment file path."""
        return self.data['attachment_path']

    @property
    def csv_folder(self):
        """Get CSV folder path."""
        return self.data['csv_folder']

    @property
    def log_directory(self):
        """Get log directory path."""
        return self.data['log_directory']

    @property
    def history_file(self):
        """Get email history file path."""
        return self.data['history_file']

    def __repr__(self):
        """String representation of configuration."""
        return (
            f"Config(template={self.email_template_path}, "
            f"subject={self.email_subject}, "
            f"attachment={self.attachment_path}, "
            f"csv_folder={self.csv_folder})"
        )
