"""
Duplicate email detection across multiple CSV files and historical records.
Prevents sending multiple emails to the same recipient.
"""

import os
import csv
from typing import Set


class DuplicateChecker:
    """Manages duplicate email detection across files and history."""

    def __init__(self, history_file: str, csv_folder: str):
        """
        Initialize duplicate checker.

        Args:
            history_file: Path to the master email history file
            csv_folder: Path to folder containing CSV files
        """
        self.history_file = history_file
        self.csv_folder = csv_folder
        self.sent_emails: Set[str] = set()

    def load_history(self):
        """
        Load historical sent emails from the history file.

        Creates the history file if it doesn't exist.
        Emails are stored in lowercase for case-insensitive comparison.
        """
        # Ensure the history file exists
        if not os.path.exists(self.history_file):
            # Create the file with header comments
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
            with open(self.history_file, 'w', encoding='utf-8') as f:
                f.write("# Email History - One email per line\n")
                f.write("# This file tracks all emails ever sent to prevent duplicates\n")
            return

        # Read existing history
        with open(self.history_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    self.sent_emails.add(line.lower())

    def scan_all_csv_files(self, logger=None):
        """
        Scan all CSV files in the folder and collect emails with "Sent" status.

        Args:
            logger: Optional logger for reporting progress

        Returns:
            int: Number of sent emails found in CSV files
        """
        if not os.path.exists(self.csv_folder):
            return 0

        csv_files = [
            f for f in os.listdir(self.csv_folder)
            if f.lower().endswith('.csv') and not f.startswith('~$')
        ]

        sent_count = 0
        for csv_file in csv_files:
            file_path = os.path.join(self.csv_folder, csv_file)

            try:
                # Try different encodings
                for encoding in ['utf-8-sig', 'utf-8', 'latin1']:
                    try:
                        with open(file_path, 'r', newline='', encoding=encoding) as f:
                            reader = csv.DictReader(f)

                            # Check if required columns exist
                            if 'Email' not in reader.fieldnames or 'Status' not in reader.fieldnames:
                                if logger:
                                    logger.warning(
                                        f"Skipping {csv_file}: Missing Email or Status column"
                                    )
                                break

                            # Collect emails with "Sent" status
                            for row in reader:
                                email = row.get('Email', '').strip().lower()
                                status = row.get('Status', '').strip()

                                if email and status == 'Sent':
                                    self.sent_emails.add(email)
                                    sent_count += 1
                        break  # Successfully read, exit encoding loop
                    except UnicodeDecodeError:
                        continue  # Try next encoding
            except Exception as e:
                if logger:
                    logger.warning(f"Error scanning {csv_file}: {e}")
                continue

        if logger:
            logger.info(f"Scanned {len(csv_files)} CSV files, found {sent_count} sent emails")

        return sent_count

    def is_duplicate(self, email: str) -> bool:
        """
        Check if an email has already been sent.

        Args:
            email: Email address to check (case-insensitive)

        Returns:
            bool: True if email exists in history or sent emails
        """
        return email.lower() in self.sent_emails

    def add_to_history(self, email: str):
        """
        Add an email to the history file and in-memory set.

        Args:
            email: Email address to add (will be stored in lowercase)
        """
        email_lower = email.lower()

        # Add to in-memory set
        self.sent_emails.add(email_lower)

        # Append to history file (thread-safe append mode)
        with open(self.history_file, 'a', encoding='utf-8') as f:
            f.write(f"{email_lower}\n")

    def get_sent_count(self) -> int:
        """
        Get total count of sent emails tracked.

        Returns:
            int: Number of unique sent emails
        """
        return len(self.sent_emails)

    def __repr__(self):
        """String representation of duplicate checker."""
        return f"DuplicateChecker(history={self.history_file}, sent_count={len(self.sent_emails)})"
