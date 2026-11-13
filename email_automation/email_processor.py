"""
Main email processing orchestration.
Coordinates CSV reading, duplicate checking, and email sending.
"""

import os
import re
from typing import Dict

from .csv_handler import CSVHandler, CSVHandlerError
from .outlook_handler import OutlookHandler, OutlookError, OutlookNotAvailableError
from .duplicate_checker import DuplicateChecker
from .config import Config


class EmailProcessor:
    """Orchestrates the email automation workflow."""

    def __init__(self, config: Config, logger, dry_run: bool = False):
        """
        Initialize email processor.

        Args:
            config: Configuration object
            logger: Logger instance
            dry_run: If True, don't actually send emails (for testing)
        """
        self.config = config
        self.logger = logger
        self.dry_run = dry_run

        # Initialize components
        self.outlook = OutlookHandler()
        self.duplicate_checker = DuplicateChecker(
            config.history_file,
            config.csv_folder
        )

        # Statistics tracking
        self.stats = {
            'sent': 0,
            'failed': 0,
            'skipped': 0,
            'duplicates': 0
        }

    def initialize(self):
        """
        Initialize all components before processing.

        Raises:
            OutlookNotAvailableError: If Outlook cannot be connected
        """
        self.logger.info("Initializing email processor...")

        # Connect to Outlook
        if not self.dry_run:
            self.logger.info("Connecting to Outlook...")
            self.outlook.connect()
            self.logger.info("Successfully connected to Outlook")
        else:
            self.logger.info("DRY RUN MODE: Skipping Outlook connection")

        # Load duplicate checker
        self.logger.info("Loading email history...")
        self.duplicate_checker.load_history()
        self.logger.info(f"Loaded {self.duplicate_checker.get_sent_count()} historical emails")

        # Scan existing CSV files for sent emails
        self.logger.info("Scanning CSV files for previously sent emails...")
        self.duplicate_checker.scan_all_csv_files(self.logger)
        self.logger.info(f"Total emails to skip (duplicates): {self.duplicate_checker.get_sent_count()}")

    def validate_email(self, email: str) -> bool:
        """
        Validate email address format.

        Args:
            email: Email address to validate

        Returns:
            bool: True if email format is valid
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def read_template(self) -> str:
        """
        Read email template from file.

        Returns:
            str: Email template content

        Raises:
            Exception: If template cannot be read
        """
        try:
            with open(self.config.email_template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"Cannot read email template: {e}")

    def process_all_files(self):
        """
        Main processing method - process all CSV files in the folder.

        Returns:
            Dict: Processing statistics
        """
        # Find all CSV files
        csv_files = self._get_csv_files()

        if not csv_files:
            self.logger.error(f"No .csv files found in {self.config.csv_folder}")
            print(f"\nERROR: No .csv files found in {self.config.csv_folder}")
            print("Please add CSV files with the required format (Name, Email, Status columns)")
            return self.stats

        self.logger.info(f"Found {len(csv_files)} CSV file(s) to process")
        print(f"\nProcessing {len(csv_files)} CSV file(s)...\n")

        # Read email template once
        try:
            template = self.read_template()
        except Exception as e:
            self.logger.critical(str(e))
            print(f"\nERROR: {e}")
            return self.stats

        # Process each CSV file
        for csv_file in csv_files:
            file_path = os.path.join(self.config.csv_folder, csv_file)
            self._process_single_file(file_path, template)

        # Display final summary
        self._display_summary()

        return self.stats

    def _get_csv_files(self):
        """Get list of CSV files in the configured folder."""
        if not os.path.exists(self.config.csv_folder):
            return []

        csv_files = [
            f for f in os.listdir(self.config.csv_folder)
            if f.lower().endswith('.csv') and not f.startswith('~$')
        ]

        return sorted(csv_files)  # Process in alphabetical order

    def _process_single_file(self, file_path: str, template: str):
        """
        Process a single CSV file.

        Args:
            file_path: Path to the CSV file
            template: Email template content
        """
        file_name = os.path.basename(file_path)
        self.logger.info(f"Processing: {file_name}")
        print(f"Processing: {file_name}")

        file_stats = {'sent': 0, 'failed': 0, 'skipped': 0, 'duplicates': 0}

        try:
            # Load CSV
            handler = CSVHandler(file_path)
            handler.load()
            handler.validate_structure()

            total_rows = handler.get_row_count()
            if total_rows == 0:
                self.logger.warning(f"{file_name} has no data rows, skipping")
                print(f"  Warning: {file_name} has no data rows\n")
                return

            # Process each recipient
            for row_index, name, email, status in handler.get_recipients():
                # Skip if already sent in this file
                if status == 'Sent':
                    file_stats['skipped'] += 1
                    continue

                # Check for duplicate
                if self.duplicate_checker.is_duplicate(email):
                    self.logger.info(f"Skipping duplicate: {email}")
                    handler.update_status(row_index, "Skipped: Duplicate")
                    file_stats['duplicates'] += 1
                    continue

                # Validate email format
                if not self.validate_email(email):
                    self.logger.warning(f"Invalid email format: {email}")
                    handler.update_status(row_index, "Failed: Invalid email")
                    file_stats['failed'] += 1
                    continue

                # Send email
                success, error_msg = self._send_to_recipient(name, email, template)

                if success:
                    handler.update_status(row_index, "Sent")
                    file_stats['sent'] += 1

                    # Add to duplicate checker (only if actually sent, not in dry run)
                    if not self.dry_run:
                        self.duplicate_checker.add_to_history(email)
                else:
                    handler.update_status(row_index, f"Failed: {error_msg}")
                    file_stats['failed'] += 1

            # Save updated CSV
            handler.save()

            # Log file completion
            self.logger.info(
                f"Completed {file_name}: "
                f"{file_stats['sent']} sent, "
                f"{file_stats['failed']} failed, "
                f"{file_stats['skipped']} skipped, "
                f"{file_stats['duplicates']} duplicates"
            )
            print(
                f"  Completed: {file_stats['sent']} sent, "
                f"{file_stats['failed']} failed, "
                f"{file_stats['skipped']} skipped, "
                f"{file_stats['duplicates']} duplicates\n"
            )

            # Update global stats
            for key in file_stats:
                self.stats[key] += file_stats[key]

        except CSVHandlerError as e:
            self.logger.error(f"Error processing {file_name}: {e}")
            print(f"  ERROR: {e}\n")

        except Exception as e:
            self.logger.error(f"Unexpected error processing {file_name}: {e}")
            print(f"  ERROR: Unexpected error - {e}\n")

    def _send_to_recipient(self, name: str, email: str, template: str) -> tuple:
        """
        Send email to a single recipient.

        Args:
            name: Recipient name
            email: Recipient email address
            template: Email template content

        Returns:
            Tuple of (success: bool, error_message: str)
        """
        try:
            if self.dry_run:
                self.logger.info(f"DRY RUN: Would send email to {email}")
                print(f"  [DRY RUN] Would send to: {email}")
                return (True, "")

            # Send via Outlook
            self.outlook.send_email(
                to_address=email,
                subject=self.config.email_subject,
                body=template,
                attachment_path=self.config.attachment_path
            )

            self.logger.info(f"Sent email to {email}")
            print(f"  ✓ Sent to: {email}")
            return (True, "")

        except OutlookNotAvailableError as e:
            error_msg = "Outlook connection lost"
            self.logger.critical(error_msg)
            print(f"\n  CRITICAL: {error_msg}")
            return (False, error_msg)

        except OutlookError as e:
            error_msg = str(e)[:50]  # Truncate long error messages
            self.logger.warning(f"Failed to send to {email}: {e}")
            print(f"  ✗ Failed: {email} ({error_msg})")
            return (False, error_msg)

        except Exception as e:
            error_msg = str(e)[:50]
            self.logger.error(f"Unexpected error sending to {email}: {e}")
            return (False, error_msg)

    def _display_summary(self):
        """Display final processing summary."""
        print("\n" + "=" * 60)
        print("PROCESSING COMPLETE")
        print("=" * 60)
        print(f"Total emails sent:       {self.stats['sent']}")
        print(f"Total failed:            {self.stats['failed']}")
        print(f"Total skipped:           {self.stats['skipped']}")
        print(f"Total duplicates found:  {self.stats['duplicates']}")
        print("=" * 60)

        self.logger.info(
            f"Final stats: {self.stats['sent']} sent, "
            f"{self.stats['failed']} failed, "
            f"{self.stats['skipped']} skipped, "
            f"{self.stats['duplicates']} duplicates"
        )

    def cleanup(self):
        """Cleanup resources."""
        if self.outlook:
            self.outlook.cleanup()
