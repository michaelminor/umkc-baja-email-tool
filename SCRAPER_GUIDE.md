# Email Scraper Agent - User Guide

## Overview

The Email Scraper Agent is a local browser automation tool that visits business websites to automatically find and extract contact email addresses. Unlike simple web scrapers, it uses a real Chrome browser to bypass anti-bot protections and navigate websites like a human would.

## Features

- **Real Browser Automation**: Uses Playwright/Chromium to act like a real person browsing
- **Smart Email Detection**: Finds emails on homepage, contact pages, and about pages
- **Anti-Bot Bypass**: Bypasses 403 errors and JavaScript-heavy sites
- **Resume Support**: Can start from any row and process in batches
- **Rate Limiting**: Configurable delays between requests to be respectful
- **Detailed Logging**: Tracks all activity with timestamps
- **CSV Integration**: Reads from and updates your existing CSV files

## Installation

### Step 1: Install Playwright

```bash
cd C:\Users\mfmin\email-automation
pip install playwright
```

### Step 2: Install Chromium Browser

```bash
python -m playwright install chromium
```

This downloads a headless Chrome browser (~100MB). It's a one-time download.

### Step 3: Verify Installation

```bash
python -m playwright --version
```

You should see the Playwright version number.

## Basic Usage

### Simple Run (All Businesses)

```bash
python email_scraper_agent.py C:\Users\mfmin\EmailOutreach\kc_businesses_websites.csv
```

This will:
- Process all 115 businesses in the CSV
- Visit each website with a 2-second delay
- Look for contact emails
- Save results to `kc_businesses_websites_scraped.csv`

### Run First 10 Businesses (Test Run)

```bash
python email_scraper_agent.py C:\Users\mfmin\EmailOutreach\kc_businesses_websites.csv --max 10
```

**Recommended for first run** to test the system.

### Resume from Row 50

```bash
python email_scraper_agent.py C:\Users\mfmin\EmailOutreach\kc_businesses_websites.csv --start 50
```

### Process 20 Businesses Starting from Row 30

```bash
python email_scraper_agent.py C:\Users\mfmin\EmailOutreach\kc_businesses_websites.csv --start 30 --max 20
```

### Run with Browser Visible (See What's Happening)

```bash
python email_scraper_agent.py C:\Users\mfmin\EmailOutreach\kc_businesses_websites.csv --visible --max 5
```

**Useful for debugging** - you'll see the browser window opening and navigating.

### Increase Delay to 5 Seconds (More Polite)

```bash
python email_scraper_agent.py C:\Users\mfmin\EmailOutreach\kc_businesses_websites.csv --delay 5
```

## Command-Line Options

| Option | Description | Default | Example |
|--------|-------------|---------|---------|
| `--start <number>` | Start from this row index | 0 | `--start 50` |
| `--max <number>` | Process maximum this many businesses | All | `--max 20` |
| `--delay <seconds>` | Delay between requests (seconds) | 2 | `--delay 3` |
| `--visible` | Show browser window (not headless) | Hidden | `--visible` |

## How It Works

### 1. Homepage Scan
- Loads the business homepage
- Scans entire page for email addresses using regex pattern
- Extracts all valid emails found

### 2. Contact Page Search
- Looks for "Contact Us", "Contact", "About Us" links
- Tries common contact page paths like `/contact`, `/contact-us`
- Navigates to contact page if found

### 3. Contact Page Scan
- Scans contact page for email addresses
- Extracts additional emails not found on homepage

### 4. Email Validation
- Filters out false positives (image URLs, example.com, etc.)
- Normalizes emails to lowercase
- Removes duplicates

### 5. CSV Update
- Updates the Email column with found addresses
- If multiple emails found, lists all (comma-separated)
- Updates Status column (Success, No Email Found, Error, etc.)
- Adds detailed notes about what was found

## Output

### Output File
Results are saved to: `<original_filename>_scraped.csv`

Example:
- Input: `kc_businesses_websites.csv`
- Output: `kc_businesses_websites_scraped.csv`

### Status Values

| Status | Meaning |
|--------|---------|
| `Success` | Email address(es) found |
| `No Email Found` | Website loaded but no emails found |
| `Timeout` | Page took too long to load (15s limit) |
| `Error` | Technical error occurred |
| `HTTP 403/404/etc` | Website returned error code |

### Log File
Detailed logs saved to: `logs/email_scraper_YYYYMMDD_HHMMSS.log`

Contains:
- Timestamp for each action
- URLs visited
- Emails found
- Errors encountered
- Progress updates

## Example Output

### Console Output
```
============================================================
Email Scraper Agent - Local Website Email Extractor
============================================================

Processing businesses 0 to 114 (115 total)
Delay between requests: 2 seconds
Headless mode: True

============================================================
Scraping: Advantage Powersports
URL: https://www.example.com
  Loading homepage...
  Found 1 email(s) on homepage
  Looking for contact page...
  Found contact link: https://www.example.com/contact
  Found 2 email(s) on contact page
  ✓ Total emails found: info@example.com, sales@example.com
Progress: 1/115 (0%)

============================================================
Scraping: LCC Powersports
URL: https://www.lccpowersports.com
  Loading homepage...
  ✗ No emails found
Progress: 2/115 (1%)

...

============================================================
SCRAPING SUMMARY
============================================================
Total Businesses Processed: 115
Emails Found: 47 businesses (73 total email addresses)
No Email Found: 52
Errors/Timeouts: 16
Success Rate: 40%
============================================================

Businesses with emails found:
  ✓ Example Motorsports: info@example.com, sales@example.com
  ✓ Example Dealer: owner@example.org
  ✓ Example Shop: shop@example.net
  ...
```

## Best Practices

### 1. Start Small
Always test with `--max 10` first to ensure it works correctly.

### 2. Use Batches
Process in batches of 20-30 businesses:
```bash
# Batch 1: rows 0-29
python email_scraper_agent.py file.csv --start 0 --max 30

# Batch 2: rows 30-59
python email_scraper_agent.py file.csv --start 30 --max 30

# Batch 3: rows 60-89
python email_scraper_agent.py file.csv --start 60 --max 30
```

### 3. Be Respectful
- Use `--delay 2` or higher (default is 2 seconds)
- Don't scrape the same site multiple times in short succession
- Some sites may temporarily block you if you go too fast

### 4. Check Logs
If something fails, check the log file in `logs/` directory for details.

### 5. Manual Review
**Always manually review the found emails** before sending. The agent does its best but may occasionally find incorrect emails (generic support@, webmaster@, etc.).

## Troubleshooting

### "Playwright not installed"
```bash
pip install playwright
python -m playwright install chromium
```

### "Browser executable not found"
```bash
python -m playwright install chromium
```

### Page Timeouts
- Increase delay: `--delay 5`
- Try visible mode to see what's happening: `--visible`
- Some sites are just slow - the agent will skip and continue

### No Emails Found
This is common! Many businesses:
- Use contact forms instead of listing emails
- Hide emails behind JavaScript (the agent tries to handle this)
- Don't publish emails publicly

For these businesses, you'll need to:
- Call them and ask for an email
- Use the contact form on their website
- Use a paid email finder service (Hunter.io, etc.)

### Memory Issues
If processing many businesses (100+), do it in batches:
```bash
python email_scraper_agent.py file.csv --start 0 --max 50
python email_scraper_agent.py file.csv --start 50 --max 50
```

## Advanced Usage

### Combining with Manual Data
After scraping, you can:
1. Review the `_scraped.csv` file
2. Manually fill in emails for businesses where none were found
3. Use both automated and manual emails together

### Email Validation
Found emails should be validated before use:
- Check for typos
- Verify they're not generic (webmaster@, admin@)
- Test with a small batch first

### Re-running on Failed Items
Create a new CSV with only the failed businesses and re-run:
```bash
# Filter businesses where Status != "Success"
python email_scraper_agent.py failed_businesses.csv --delay 5
```

## Estimated Time

Processing time depends on:
- Website load speed
- Delay between requests
- Number of businesses

**Rough estimates** (with 2-second delay):
- 10 businesses: ~2 minutes
- 50 businesses: ~8 minutes
- 115 businesses: ~15-20 minutes

## Legal and Ethical Considerations

### ✓ Good Practices
- Scraping public contact information for legitimate business outreach
- Respecting rate limits and delays
- Using found emails for sponsorship inquiries (your use case)

### ✗ Avoid
- Harvesting emails for spam
- Scraping protected/member-only content
- Ignoring robots.txt (the agent respects it)
- Overwhelming servers with rapid requests

### Privacy Note
The agent only collects publicly visible information. It doesn't:
- Try to bypass login pages
- Access private areas
- Scrape personal data beyond business contact emails

## Support

If you encounter issues:
1. Check the log file in `logs/` directory
2. Try running with `--visible` to see what's happening
3. Reduce batch size with `--max`
4. Increase delay with `--delay`

## Next Steps

After scraping:
1. Review the `_scraped.csv` file
2. Manually verify important emails
3. Fill in missing emails where possible
4. Use the updated CSV with your email automation tool
5. Send test emails to verify addresses work
