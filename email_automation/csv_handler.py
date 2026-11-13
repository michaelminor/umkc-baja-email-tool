"""
CSV file handler for reading recipient lists and updating send status.
Handles CSV operations with proper error handling and encoding support.
"""

import csv
import os
from typing import List, Dict, Generator, Tuple


class CSVHandlerError(Exception):
    """Raised when CSV operations fail."""
    pass


class CSVHandler:
    """Manages CSV file operations for recipient lists."""

    def __init__(self, file_path: str):
        """
        Initialize CSV handler for a specific file.

        Args:
            file_path: Path to the CSV file
        """
        self.file_path = file_path
        self.data: List[Dict[str, str]] = []
        self.fieldnames: List[str] = []

    def load(self):
        """
        Load CSV file into memory.

        Raises:
            CSVHandlerError: If file cannot be read or parsed
        """
        if not os.path.exists(self.file_path):
            raise CSVHandlerError(f"CSV file not found: {self.file_path}")

        # Try different encodings for compatibility
        encodings = ['utf-8-sig', 'utf-8', 'latin1']
        last_error = None

        for encoding in encodings:
            try:
                with open(self.file_path, 'r', newline='', encoding=encoding) as f:
                    reader = csv.DictReader(f)
                    self.fieldnames = reader.fieldnames
                    self.data = list(reader)
                return  # Success
            except (UnicodeDecodeError, PermissionError) as e:
                last_error = e
                continue

        # If all encodings failed, raise the last error
        if last_error:
            if isinstance(last_error, PermissionError):
                raise CSVHandlerError(
                    f"Cannot access {self.file_path}. "
                    f"Please close the file if it's open in Excel or another application."
                )
            raise CSVHandlerError(
                f"Cannot read {self.file_path}: {last_error}"
            )

    def validate_structure(self):
        """
        Validate that CSV has required columns: Name, Email, Status.

        Raises:
            CSVHandlerError: If required columns are missing
        """
        required_columns = ['Name', 'Email', 'Status']

        if not self.fieldnames:
            raise CSVHandlerError(
                f"CSV file {self.file_path} has no header row"
            )

        missing_columns = [col for col in required_columns if col not in self.fieldnames]
        if missing_columns:
            raise CSVHandlerError(
                f"CSV file {self.file_path} is missing required columns: "
                f"{', '.join(missing_columns)}\n"
                f"Expected columns: {', '.join(required_columns)}\n"
                f"Found columns: {', '.join(self.fieldnames)}"
            )

    def get_recipients(self) -> Generator[Tuple[int, str, str, str], None, None]:
        """
        Generator that yields recipient information row by row.

        Yields:
            Tuple of (row_index, name, email, status)

        Raises:
            CSVHandlerError: If data hasn't been loaded
        """
        if not self.data:
            raise CSVHandlerError("CSV data not loaded. Call load() first.")

        for index, row in enumerate(self.data):
            name = row.get('Name', '').strip()
            email = row.get('Email', '').strip()
            status = row.get('Status', '').strip()

            yield (index, name, email, status)

    def update_status(self, row_index: int, status: str):
        """
        Update the status for a specific row.

        Args:
            row_index: Index of the row to update
            status: New status value (e.g., "Sent", "Failed: reason", "Skipped: Duplicate")

        Raises:
            CSVHandlerError: If row_index is invalid
        """
        if row_index < 0 or row_index >= len(self.data):
            raise CSVHandlerError(
                f"Invalid row index {row_index}. CSV has {len(self.data)} rows."
            )

        self.data[row_index]['Status'] = status

    def save(self):
        """
        Save updated data back to CSV file.

        Raises:
            CSVHandlerError: If file cannot be written
        """
        try:
            with open(self.file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
                writer.writerows(self.data)
        except PermissionError:
            raise CSVHandlerError(
                f"Cannot save {self.file_path}. "
                f"Please close the file if it's open in Excel or another application."
            )
        except Exception as e:
            raise CSVHandlerError(f"Error saving CSV file: {e}")

    def get_row_count(self) -> int:
        """Get total number of data rows (excluding header)."""
        return len(self.data)

    def __repr__(self):
        """String representation of CSV handler."""
        return f"CSVHandler(file={self.file_path}, rows={len(self.data)})"
