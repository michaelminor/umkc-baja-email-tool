# Quick Start Guide - Email Automation Tool

## Launch Options

### 🖥️ GUI (Graphical Interface) - RECOMMENDED
Double-click **"UMKC Baja Email Tool"** on your desktop!

See [GUI_GUIDE.md](GUI_GUIDE.md) for full GUI documentation.

### ⌨️ Command Line (Advanced)
Use the commands below for CLI operation.

---

## Before You Start

You need:
1. **Email template** → `email-automation/templates/email_template.txt` ✓ (sample created)
2. **Sponsorship packet** → `email-automation/templates/sponsorship_packet.docx` ⚠️ (you need to create this)
3. **CSV files with recipients** → `C:\Users\mfmin\EmailOutreach\*.csv` ✓ (sample created)

## First Time Setup (One Time Only)

### Step 1: Create Your Sponsorship Packet
Create a Word document at: `C:\Users\mfmin\email-automation\templates\sponsorship_packet.docx`

This will be attached to every email.
See `templates/PLACEHOLDER_sponsorship_packet.txt` for guidance.

### Step 2: Edit Email Template (Optional)
Edit `templates/email_template.txt` with your actual UMKC Baja Racing message.

### Step 3: Edit Configuration (Optional)
Edit `config\settings.json` if you want to change:
- Email subject line
- File paths
- Folder locations

## Regular Usage

### 1. Prepare Recipients
Create a CSV file: `Name,Email,Status`

**Example:**
```csv
Name,Email,Status
John Doe,john@example.com,
Jane Smith,jane@company.com,
```

Save in: `C:\Users\mfmin\EmailOutreach\`

### 2. Test First (Recommended)
```bash
cd C:\Users\mfmin\email-automation
py -m email_automation.main --dry-run
```

This tests without sending emails.

### 3. Send Emails
```bash
cd C:\Users\mfmin\email-automation
py -m email_automation.main
```

### 4. Check Results
- **CSV files**: Status column updated (Sent/Failed/Skipped)
- **Logs**: Check `logs/` folder for detailed info
- **Outlook**: Check Sent Items folder

## Quick Commands

| What | Command |
|------|---------|
| Test run | `py -m email_automation.main --dry-run` |
| Send emails | `py -m email_automation.main` |
| Verbose mode | `py -m email_automation.main -v` |
| Help | `py -m email_automation.main --help` |

## Tips

✅ **Always test with `--dry-run` first**
✅ **Close CSV files before running** (Excel locks them)
✅ **Check logs if errors occur**
✅ **Don't delete `data/sent_emails_history.txt`** (prevents duplicates)

## What If...

**"Attachment file not found"**
→ Create `sponsorship_packet.docx` in `templates/` folder

**"No .csv files found"**
→ Add CSV files to `C:\Users\mfmin\EmailOutreach\`

**"Outlook is not available"**
→ Open Outlook and make sure it's working

**"Cannot access CSV file"**
→ Close the file in Excel

## Files Overview

```
email-automation/
├── templates/                   ← Email template and sponsorship packet
│   ├── email_template.txt       ← Your email message
│   └── sponsorship_packet.docx  ← Your attachment (create this!)
├── config/settings.json         ← Edit this for configuration
├── logs/                        ← Check here for detailed logs
├── data/sent_emails_history.txt ← Don't delete (tracks sent emails)
└── README.md                    ← Full documentation

C:\Users\mfmin\EmailOutreach/    ← Put your CSV files here
└── *.csv
```

---

**Need more help?** See [README.md](README.md) for full documentation.
