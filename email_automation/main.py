"""
Email Automation Tool - Main Entry Point
CLI interface for automated email sending via Outlook with CSV recipient lists.
"""

import sys
import argparse

from .logger import setup_logger
from .config import Config, ConfigurationError
from .email_processor import EmailProcessor
from .outlook_handler import OutlookNotAvailableError


def main():
    """Main entry point for the email automation tool."""

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Email Automation Tool - Send bulk emails via Outlook",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m email_automation.main                    # Normal operation
  python -m email_automation.main --dry-run          # Test without sending
  python -m email_automation.main -v                 # Verbose logging
  python -m email_automation.main -c custom.json     # Use custom config

For more information, see README.md
        """
    )

    parser.add_argument(
        '-c', '--config',
        default='config/settings.json',
        help='Path to configuration file (default: config/settings.json)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Process files without actually sending emails (for testing)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging (DEBUG level)'
    )

    args = parser.parse_args()

    # Display banner
    print("=" * 60)
    print("EMAIL AUTOMATION TOOL")
    print("=" * 60)

    if args.dry_run:
        print("MODE: DRY RUN (no emails will be sent)")
    else:
        print("MODE: PRODUCTION (emails will be sent)")

    print("=" * 60)
    print()

    # Initialize logger
    logger = None
    try:
        logger = setup_logger(verbose=args.verbose)
        logger.info("Starting email automation tool")

        if args.dry_run:
            logger.info("Running in DRY RUN mode")

        # Load configuration
        logger.info(f"Loading configuration from {args.config}")
        config = Config(args.config)
        logger.info(f"Configuration loaded: {config}")

        # Validate paths
        logger.info("Validating configuration paths...")
        config.validate_paths(logger)
        logger.info("All paths validated successfully")

        # Initialize email processor
        processor = EmailProcessor(config, logger, dry_run=args.dry_run)

        # Initialize components
        processor.initialize()

        # Process all files
        stats = processor.process_all_files()

        # Cleanup
        processor.cleanup()

        # Exit with appropriate code
        if stats['failed'] > 0:
            logger.warning("Processing completed with some failures")
            sys.exit(1)
        else:
            logger.info("Processing completed successfully")
            sys.exit(0)

    except ConfigurationError as e:
        if logger:
            logger.critical(f"Configuration error: {e}")
        print(f"\nCONFIGURATION ERROR:")
        print(f"{e}\n")
        sys.exit(1)

    except OutlookNotAvailableError as e:
        if logger:
            logger.critical(f"Outlook error: {e}")
        print(f"\nOUTLOOK ERROR:")
        print(f"{e}\n")
        print("Please ensure:")
        print("  1. Microsoft Outlook is installed")
        print("  2. Outlook is configured with at least one email account")
        print("  3. You have proper permissions to send emails\n")
        sys.exit(1)

    except KeyboardInterrupt:
        if logger:
            logger.warning("Process interrupted by user")
        print("\n\nProcess interrupted by user. Exiting...\n")
        sys.exit(130)

    except Exception as e:
        if logger:
            logger.critical(f"Unexpected error: {e}", exc_info=True)
        print(f"\nUNEXPECTED ERROR:")
        print(f"{e}\n")
        print("Check the log file for detailed error information.\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
