# Email Automation Tool

Automated email sending via Microsoft Outlook with CSV recipient lists, duplicate prevention, and attachment support.

## Features

- **CSV-based recipient management** - Simple spreadsheet format (Name, Email, Status)
- **Automatic duplicate prevention** - Multi-tier checking across files and history
- **Outlook integration** - Uses your existing Outlook configuration
- **Attachment support** - Automatically attach files (e.g., sponsorship packet)
- **Status tracking** - Updates CSV with sent/failed/skipped status
- **Multi-user safe** - Multiple people can add CSV files without causing duplicates
- **Comprehensive logging** - Both file and console logging with colored output
- **Dry run mode** - Test without sending emails

## Requirements

- Windows 10/11
- Python 3.7 or higher
- Microsoft Outlook installed and configured
- Outlook configured with at least one email account

## Installation

1. **Navigate to the project directory:**
   ```bash
   cd C:\Users\mfmin\email-automation
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python -m email_automation.main --help
   ```

## Configuration

### 1. Edit `config/settings.json`

The configuration file is already set up with proper paths:

```json
{
  "email_template_path": "templates/email_template.txt",
  "email_subject": "University of Missouri - Kansas City Baja Racing team sponsorship outreach",
  "attachment_path": "templates/sponsorship_packet.docx",
  "csv_folder": "C:\\Users\\mfmin\\EmailOutreach",
  "log_directory": "logs",
  "history_file": "data/sent_emails_history.txt"
}
```

You can edit the email subject or paths if needed.

### 2. Create Email Template

Edit the template file at `templates/email_template.txt`:

**Current template (customize for your needs):**
```
Hello,

We are reaching out regarding an exciting sponsorship opportunity...

Please find the detailed sponsorship packet attached to this email...
```

### 3. Create Sponsorship Packet

**IMPORTANT:** You need to create this file!

Create a Word document at: `templates/sponsorship_packet.docx`

This file will be attached to every email. See `templates/PLACEHOLDER_sponsorship_packet.txt` for guidance on what to include.

### 4. Prepare CSV Files

Create CSV files with the following structure:

**Required columns:** Name, Email, Status

**Example CSV:**
```csv
Name,Email,Status
John Doe,john.doe@example.com,
Jane Smith,jane.smith@company.com,
Bob Johnson,bob@business.org,
```

**Important:** Leave the Status column empty initially. The tool will fill it in.

Save CSV files in `C:\Users\mfmin\EmailOutreach\`

## Usage

### Basic Usage

```bash
# Normal operation (sends emails)
python -m email_automation.main

# Test run (doesn't send emails)
python -m email_automation.main --dry-run

# Verbose logging
python -m email_automation.main -v

# Custom configuration file
python -m email_automation.main -c path/to/config.json
```

### Workflow

1. Place CSV files in the `EmailOutreach` folder
2. Run the tool: `python -m email_automation.main`
3. Monitor console output and check logs in `logs/` directory
4. Review CSV files - Status column will show "Sent", "Failed: reason", or "Skipped: Duplicate"
5. Check Outlook Sent Items to verify emails were sent

## How Duplicate Prevention Works

The tool uses **three-tier duplicate prevention** to ensure no email is sent twice:

### 1. Within-file checking
- Skips rows where Status = "Sent"

### 2. Cross-file checking
- Scans ALL CSV files in the EmailOutreach folder
- Builds a global set of emails marked "Sent"
- Skips emails that exist in ANY file

### 3. Historical tracking
- Maintains `data/sent_emails_history.txt` with all emails ever sent
- Persists across sessions and file deletions
- Prevents re-sending even if CSV files are recreated

**Result:** Even if multiple people add CSV files with overlapping emails, each recipient receives exactly ONE email.

## CSV Status Values

After processing, the Status column will contain one of:

- **Sent** - Email successfully sent
- **Skipped: Duplicate** - Email already sent (in another file or history)
- **Failed: Invalid email** - Email address format is invalid
- **Failed: Network error** - Network/connection issue
- **Failed: [error reason]** - Other error (truncated to 50 chars)

## File Structure

```
email-automation/
├── email_automation/          # Python package
│   ├── __init__.py
│   ├── main.py               # CLI entry point
│   ├── config.py             # Configuration management
│   ├── csv_handler.py        # CSV operations
│   ├── outlook_handler.py    # Outlook COM automation
│   ├── email_processor.py    # Main orchestration
│   ├── duplicate_checker.py  # Duplicate detection
│   └── logger.py             # Logging setup
├── templates/                # Email template and attachments
│   ├── email_template.txt    # Email body content
│   └── sponsorship_packet.docx  # Attachment (create this!)
├── config/
│   └── settings.json         # User configuration
├── data/
│   └── sent_emails_history.txt  # Master email history
├── logs/                     # Auto-generated log files
├── requirements.txt          # Python dependencies
├── QUICKSTART.md             # Quick reference guide
└── README.md                 # This file
```

## Logs

Log files are created in the `logs/` directory with timestamps:

- **Format:** `email_automation_YYYYMMDD_HHMMSS.log`
- **Content:** Detailed debug information, errors, email send attempts
- **Console:** Colored output showing important events (INFO level)

## Troubleshooting

### "Outlook is not available"
- Ensure Outlook is installed
- Open Outlook and configure an email account
- Check that Outlook can send emails manually

### "Configuration file not found"
- Ensure `config/settings.json` exists
- Check the path if using `-c` option

### "Email template not found"
- Check that `templates/email_template.txt` exists
- If missing, create it or verify path in settings.json

### "Attachment file not found"
- You need to create `templates/sponsorship_packet.docx`
- See `templates/PLACEHOLDER_sponsorship_packet.txt` for guidance
- Ensure it's a valid Word document (.docx)

### "Cannot access CSV file"
- Close the CSV file in Excel or any other application
- Ensure you have read/write permissions

### "No .csv files found"
- Check that CSV files are in the configured csv_folder
- Ensure files have .csv extension (not .xlsx)
- Don't include temporary files like `~$filename.csv`

### Duplicate emails being sent
- Check `data/sent_emails_history.txt` - ensure it's not deleted
- Verify CSV Status column is being updated
- Enable verbose logging (`-v`) to see duplicate checking in action

## Testing

### 1. Test with Dry Run
```bash
python -m email_automation.main --dry-run
```

This will:
- Process all CSV files
- Check for duplicates
- Update Status columns
- NOT send actual emails

### 2. Test with Small Sample
- Create a test CSV with 2-3 recipients (use your own email addresses)
- Run normally: `python -m email_automation.main`
- Check your inbox to verify emails and attachments

### 3. Test Duplicate Prevention
- Create two CSV files with the same email address
- Run the tool
- Verify only ONE email is sent
- Check Status columns: one "Sent", one "Skipped: Duplicate"

## Multi-User Scenarios

**Problem:** Multiple people are adding CSV files with potential overlapping emails.

**Solution:** The tool is designed for this! Here's how it works:

1. Person A adds `batch1.csv` with 50 recipients
2. Person B adds `batch2.csv` with 30 recipients (10 overlap with batch1)
3. Run the tool:
   - Processes `batch1.csv` first (alphabetical order)
   - Sends to all 50 unique recipients
   - Processes `batch2.csv`
   - Skips the 10 duplicates
   - Sends to the 20 new recipients

**Result:** 60 total emails sent (not 80), no duplicates.

## Security & Privacy

- **No credentials stored** - Uses Windows integrated authentication via Outlook
- **Local processing** - All operations happen on your PC
- **Email history** - Contains email addresses in `data/sent_emails_history.txt`
  - Keep this file secure
  - Treat it like sensitive data (contains PII)

## Command Reference

### Main Commands
| Command | Description |
|---------|-------------|
| `python -m email_automation.main` | Run normally (send emails) |
| `python -m email_automation.main --dry-run` | Test run (no emails sent) |
| `python -m email_automation.main -v` | Verbose logging (DEBUG level) |
| `python -m email_automation.main -c config.json` | Use custom config file |
| `python -m email_automation.main --help` | Show help message |

### Arguments
- `-c`, `--config`: Path to configuration file (default: config/settings.json)
- `--dry-run`: Process without sending emails (testing mode)
- `-v`, `--verbose`: Enable DEBUG level logging

## Exit Codes

- **0**: Success (all emails sent)
- **1**: Partial success (some failures occurred)
- **1**: Configuration error
- **1**: Outlook not available
- **130**: Interrupted by user (Ctrl+C)

## Tips & Best Practices

1. **Always test with `--dry-run` first** - Verify everything works before sending
2. **Keep email_template.txt updated** - Tool reads it fresh for each run
3. **Don't delete `sent_emails_history.txt`** - This prevents duplicates across sessions
4. **Close CSV files before running** - Excel locks files and causes errors
5. **Check logs for errors** - Detailed information in `logs/` directory
6. **Use descriptive CSV filenames** - e.g., `sponsors_batch1.csv`, `sponsors_batch2.csv`
7. **Backup your CSV files** - Before processing, keep a copy
8. **Run during low email volume times** - Avoid overwhelming your Outlook/network

## Limitations

- **Windows only** - Uses Windows COM for Outlook integration
- **One attachment per email** - All emails get the same attachment
- **Plain text emails** - No HTML formatting support
- **Outlook required** - Cannot use with other email clients
- **Sequential processing** - Processes one file at a time

## Future Enhancements

See the original plan for potential future features:
- Email personalization with placeholders ({{NAME}})
- HTML email support
- Multiple/variable attachments
- Rate limiting between sends
- GUI interface
- Automatic retry for failed sends

## License

This is a custom tool created for internal use.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review log files in `logs/` directory
3. Run with `-v` flag for detailed debugging

---

**Created:** 2026-02-11
**Version:** 1.0.0
**Author:** Custom automation tool
