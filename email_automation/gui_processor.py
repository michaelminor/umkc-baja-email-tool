"""
GUI-aware Email Processor with progress callbacks.
Extends EmailProcessor to provide real-time updates to the GUI.
"""

import os
from .email_processor import EmailProcessor
from .csv_handler import CSVHandler


class GUIEmailProcessor(EmailProcessor):
    """EmailProcessor with GUI progress callbacks."""

    def __init__(self, config, logger, dry_run=False, progress_callback=None, status_callback=None):
        """
        Initialize GUI-aware email processor.

        Args:
            config: Configuration object
            logger: Logger instance
            dry_run: If True, don't actually send emails
            progress_callback: Callback for progress updates (current, total, percentage)
            status_callback: Callback for status updates (message, stats_dict)
        """
        super().__init__(config, logger, dry_run)
        self.progress_callback = progress_callback
        self.status_callback = status_callback
        self.total_emails = 0
        self.processed_emails = 0

    def process_all_files(self):
        """Process all files with GUI progress updates."""
        # Find all CSV files
        csv_files = self._get_csv_files()

        if not csv_files:
            self.logger.error(f"No .csv files found in {self.config.csv_folder}")
            if self.status_callback:
                self.status_callback(
                    f"ERROR: No .csv files found in {self.config.csv_folder}",
                    self.stats
                )
            return self.stats

        # Count total emails first
        self.total_emails = self._count_total_emails(csv_files)

        if self.status_callback:
            self.status_callback(
                f"Found {len(csv_files)} CSV file(s) with {self.total_emails} total recipients",
                self.stats
            )

        # Read email template once
        try:
            template = self.read_template()
        except Exception as e:
            self.logger.critical(str(e))
            if self.status_callback:
                self.status_callback(f"ERROR: {e}", self.stats)
            return self.stats

        # Process each CSV file
        for csv_file in csv_files:
            file_path = os.path.join(self.config.csv_folder, csv_file)
            self._process_single_file(file_path, template)

        # Final update
        if self.status_callback:
            self.status_callback("Processing complete!", self.stats)

        if self.progress_callback:
            self.progress_callback(self.total_emails, self.total_emails, 100)

        return self.stats

    def _count_total_emails(self, csv_files):
        """Count total number of emails across all CSV files."""
        total = 0
        for csv_file in csv_files:
            file_path = os.path.join(self.config.csv_folder, csv_file)
            try:
                handler = CSVHandler(file_path)
                handler.load()
                total += handler.get_row_count()
            except:
                pass  # Skip files that can't be loaded
        return total

    def _send_to_recipient(self, name, email, template):
        """Send email with progress callback."""
        # Call parent implementation
        result = super()._send_to_recipient(name, email, template)

        # Update progress
        self.processed_emails += 1

        # Calculate percentage
        percentage = int((self.processed_emails / self.total_emails) * 100) if self.total_emails > 0 else 0

        # Call progress callback
        if self.progress_callback:
            self.progress_callback(self.processed_emails, self.total_emails, percentage)

        # Call status callback
        if self.status_callback:
            status_msg = f"Processing {email}... ({self.processed_emails}/{self.total_emails})"
            self.status_callback(status_msg, self.stats)

        return result
