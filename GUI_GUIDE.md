# GUI Guide - UMKC Baja Racing Email Tool

## Launching the GUI

### Option 1: Desktop Shortcut (Recommended)
Double-click **"UMKC Baja Email Tool"** on your desktop.

### Option 2: Manual Launch
1. Navigate to `C:\Users\mfmin\email-automation`
2. Double-click `launch_gui.pyw`

### Option 3: Python Command
```bash
cd C:\Users\mfmin\email-automation
py launch_gui.pyw
```

## GUI Overview

The GUI has 4 tabs:
- **⚙️ Setup** - Configure email settings
- **📧 Send Emails** - Send or test emails
- **📜 History** - View sent email history
- **📋 Logs** - View detailed logs

---

## ⚙️ Setup Tab

### What You Can Do:
- **Edit email subject** - Change the subject line for outreach emails
- **Select email template** - Choose your email body text file
- **Select sponsorship packet** - Choose the Word document to attach
- **Select CSV folder** - Choose where your recipient CSV files are stored

### Buttons:
- **Preview Template** - View your email template before sending
- **Save Configuration** - Save changes to `config/settings.json`

### Tips:
- Use "Browse..." buttons to select files visually
- Changes are only saved when you click "Save Configuration"
- The tool validates all paths before saving

---

## 📧 Send Emails Tab

### CSV Files Section
Shows all CSV files found in your configured folder with recipient counts.

Example:
```
Found 3 CSV file(s):

✓ batch1.csv (15 recipients)
✓ batch2.csv (8 recipients)
✓ sponsors_2024.csv (22 recipients)
```

### Progress Section
- **Progress Bar** - Visual progress indicator
- **Status** - Current operation status
- **Statistics** - Real-time counts of sent/failed/skipped/duplicates

### Buttons:

**🧪 Test Run (Dry Run)**
- Processes CSV files WITHOUT sending emails
- Updates CSV Status columns
- Shows what would happen
- **USE THIS FIRST** to test everything

**✉️ Send Emails**
- Actually sends emails via Outlook
- Updates CSV Status columns
- Adds emails to history
- Shows confirmation dialog before sending

### How Sending Works:

1. Click "Test Run (Dry Run)" first to verify everything
2. Check the statistics and CSV files
3. Click "Send Emails" when ready
4. Confirm the dialog
5. Watch the progress bar and status
6. Check Outlook Sent Items to verify

### During Sending:
- Progress bar shows percentage complete
- Status shows current email being processed
- Statistics update in real-time
- Buttons are disabled (prevents double-sending)
- You can't close the window (finish or wait)

---

## 📜 History Tab

### What It Shows:
- All emails that have ever been sent
- Total count of sent emails
- Raw content of `sent_emails_history.txt`

### Button:
- **Refresh History** - Reload the history file

### Why This Matters:
This is your **duplicate prevention system**. Emails in this file will NEVER receive a second email, even if they appear in new CSV files.

---

## 📋 Logs Tab

### What It Shows:
- Detailed logs of all operations
- Errors, warnings, and info messages
- Timestamps for everything

### Features:
- **Dropdown** - Select which log file to view
- **Refresh** - Reload the file list
- **Log files** are sorted newest first

### When to Check Logs:
- After errors occur
- To debug why emails failed
- To see detailed duplicate checking
- For audit trail of all operations

---

## Common Workflows

### First Time Setup
1. Go to **Setup** tab
2. Verify all paths are correct
3. Click "Preview Template" to check your message
4. Click "Save Configuration"

### Sending Emails for the First Time
1. **Setup** tab → Verify configuration
2. **Send Emails** tab → Click "Refresh File List"
3. Verify CSV files appear with correct counts
4. Click "🧪 Test Run (Dry Run)"
5. Check statistics look correct
6. Open CSV files → Verify Status column updated
7. Click "✉️ Send Emails"
8. Confirm dialog
9. Wait for completion
10. Check Outlook Sent Items

### Regular Usage
1. Add new CSV files to `C:\Users\mfmin\EmailOutreach\`
2. Launch GUI from desktop shortcut
3. **Send Emails** tab → Click "Refresh File List"
4. Click "✉️ Send Emails"
5. Done!

### Checking What Was Sent
1. **History** tab → See all sent emails
2. **Logs** tab → See detailed operation log
3. Open Outlook → Check Sent Items folder

---

## Error Messages

### "Outlook Not Available"
**Solution:**
- Open Outlook and ensure it's working
- Send a test email manually from Outlook
- Check that Outlook is configured with an email account

### "Template file not found"
**Solution:**
- Go to **Setup** tab
- Click "Browse..." next to Email Template
- Select `templates/email_template.txt`
- Click "Save Configuration"

### "Attachment file not found"
**Solution:**
- Create `sponsorship_packet.docx` in `templates/` folder
- Or go to **Setup** tab → Browse to select existing file
- Click "Save Configuration"

### "No CSV files found"
**Solution:**
- Verify CSV files are in the correct folder
- Check **Setup** tab for configured CSV Folder path
- Ensure files have `.csv` extension (not `.xlsx`)
- Don't use temporary files like `~$filename.csv`

---

## Tips & Tricks

### ✅ Best Practices
- **Always** do a Test Run first
- **Close** CSV files in Excel before running
- **Check** Outlook Sent Items to verify
- **Review** logs after each run
- **Don't delete** `sent_emails_history.txt`

### ⚡ Keyboard Shortcuts
- `Ctrl+Tab` - Switch between tabs
- `Alt+F4` - Close GUI
- `F5` in Logs tab - Refresh (browser habit)

### 🔄 Refresh Buttons
- CSV Files: Click "Refresh File List"
- History: Click "Refresh History"
- Logs: Click "Refresh" dropdown button

### 📊 Understanding Statistics

**Sent** - Successfully sent emails
- Email was sent via Outlook
- CSV Status = "Sent"
- Email added to history

**Failed** - Could not send
- Invalid email format
- Network error
- Outlook error
- CSV Status = "Failed: [reason]"

**Skipped** - Already sent in this file
- CSV Status was already "Sent"
- Row was skipped

**Duplicates** - Found in another file or history
- Email exists in different CSV file
- Email exists in history file
- CSV Status = "Skipped: Duplicate"

---

## Troubleshooting

### GUI Won't Launch
1. Check desktop shortcut exists
2. Try: `py launch_gui.pyw` from command line
3. Check logs for errors

### Buttons Don't Work
- GUI might be processing - wait for completion
- Check status message at bottom
- Try closing and reopening

### Progress Bar Stuck
- Check status message for errors
- Check logs for detailed error info
- Ensure Outlook is responsive

### Can't Save Configuration
- Close any open CSV files
- Check file permissions
- Ensure paths exist

---

## FAQ

**Q: Can I edit CSV files while the GUI is running?**
A: No. Close files in Excel before running the tool.

**Q: Can I cancel while sending?**
A: No. The process must complete. Already-sent emails are tracked, so you can re-run safely.

**Q: How do I know an email was actually sent?**
A:
1. Check CSV Status column = "Sent"
2. Check Outlook Sent Items
3. Check History tab
4. Check logs for "Sent email to [address]"

**Q: What if I need to re-send to someone?**
A:
1. Remove their email from `sent_emails_history.txt`
2. Change their CSV Status from "Sent" to blank
3. Re-run the tool

**Q: Can multiple people use this tool?**
A: Yes! Each person can add CSV files. Duplicate prevention ensures no one gets spammed.

**Q: Where are my files?**
- **CSV files**: `C:\Users\mfmin\EmailOutreach\`
- **Email template**: `email-automation/templates/email_template.txt`
- **Sponsorship packet**: `email-automation/templates/sponsorship_packet.docx`
- **Configuration**: `email-automation/config/settings.json`
- **History**: `email-automation/data/sent_emails_history.txt`
- **Logs**: `email-automation/logs/`

---

## Support

For issues:
1. Check **Logs** tab for detailed error info
2. Check `QUICKSTART.md` for common solutions
3. Check `README.md` for full documentation

---

**Version:** 1.0.0
**Created:** 2026-02-12
**For:** UMKC Baja Racing Team
