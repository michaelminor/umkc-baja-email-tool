"""
Outlook COM automation handler for sending emails.
Integrates with local Outlook installation to send emails with attachments.
"""

import os
import win32com.client
import pywintypes


class OutlookError(Exception):
    """Raised when Outlook operations fail."""
    pass


class OutlookNotAvailableError(OutlookError):
    """Raised when Outlook is not available or cannot be connected."""
    pass


class OutlookHandler:
    """Manages Outlook COM automation for sending emails."""

    def __init__(self):
        """Initialize Outlook handler."""
        self.outlook = None
        self.namespace = None

    def connect(self):
        """
        Initialize COM connection to Outlook.

        Raises:
            OutlookNotAvailableError: If Outlook cannot be connected
        """
        try:
            # Create Outlook application object
            self.outlook = win32com.client.Dispatch("Outlook.Application")

            # Get MAPI namespace to verify connection
            self.namespace = self.outlook.GetNamespace("MAPI")

            # Test that Outlook is responsive
            _ = self.namespace.Folders.Count

        except pywintypes.com_error as e:
            raise OutlookNotAvailableError(
                f"Cannot connect to Outlook. Please ensure Outlook is installed and configured.\n"
                f"Error: {e}"
            )
        except Exception as e:
            raise OutlookNotAvailableError(
                f"Unexpected error connecting to Outlook: {e}"
            )

    def send_email(self, to_address: str, subject: str, body: str, attachment_path: str = None):
        """
        Send an email via Outlook.

        Args:
            to_address: Recipient email address
            subject: Email subject line
            body: Email body text
            attachment_path: Optional path to file to attach

        Raises:
            OutlookError: If email cannot be sent
            OutlookNotAvailableError: If Outlook connection is lost
        """
        if not self.outlook:
            raise OutlookNotAvailableError("Outlook not connected. Call connect() first.")

        try:
            # Create new mail item (0 = MailItem)
            mail = self.outlook.CreateItem(0)

            # Set email properties
            mail.To = to_address
            mail.Subject = subject
            mail.Body = body

            # Add attachment if provided
            if attachment_path:
                if not os.path.exists(attachment_path):
                    raise OutlookError(f"Attachment file not found: {attachment_path}")

                mail.Attachments.Add(os.path.abspath(attachment_path))

            # Send the email
            mail.Send()

        except pywintypes.com_error as e:
            # Check for specific COM errors
            error_code = e.args[0] if e.args else 0

            # RPC server unavailable - Outlook crashed/closed
            if error_code == -2147467259 or '0x800706BA' in str(e):
                raise OutlookNotAvailableError(
                    "Outlook connection lost. Please ensure Outlook is running."
                )

            # Network/offline errors
            if 'network' in str(e).lower() or 'offline' in str(e).lower():
                raise OutlookError(f"Network error: {e}")

            # Generic COM error
            raise OutlookError(f"Error sending email: {e}")

        except Exception as e:
            raise OutlookError(f"Unexpected error sending email: {e}")

    def is_running(self) -> bool:
        """
        Check if Outlook is still responsive.

        Returns:
            bool: True if Outlook is running and responsive
        """
        try:
            if self.outlook and self.namespace:
                # Simple test to verify Outlook is responsive
                _ = self.namespace.Folders.Count
                return True
        except:
            pass

        return False

    def cleanup(self):
        """Release COM objects properly."""
        try:
            if self.namespace:
                del self.namespace
            if self.outlook:
                del self.outlook
        except:
            pass  # Ignore cleanup errors

    def __del__(self):
        """Destructor to ensure COM objects are released."""
        self.cleanup()

    def __repr__(self):
        """String representation of Outlook handler."""
        status = "connected" if self.is_running() else "disconnected"
        return f"OutlookHandler(status={status})"
