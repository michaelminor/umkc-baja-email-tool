"""
Local Email Scraper Agent
=========================
Automatically visits business websites to find contact email addresses.

Uses Playwright browser automation to:
- Navigate websites like a real person (bypasses anti-bot protections)
- Find "Contact Us" and "About" pages
- Extract email addresses using pattern matching
- Update CSV with found emails

Requirements:
    pip install playwright
    python -m playwright install chromium

Usage:
    python email_scraper_agent.py <csv_file>
    python email_scraper_agent.py C:/Users/mfmin/EmailOutreach/kc_businesses_websites.csv
"""

import csv
import re
import time
import sys
import logging
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin, urlparse

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("ERROR: Playwright not installed.")
    print("Install with: pip install playwright")
    print("Then run: python -m playwright install chromium")
    sys.exit(1)


class EmailScraperAgent:
    """Browser automation agent for scraping contact emails from business websites."""

    def __init__(self, csv_path, headless=True):
        """
        Initialize the email scraper agent.

        Args:
            csv_path: Path to CSV file with business websites
            headless: Run browser in headless mode (no visible window)
        """
        self.csv_path = Path(csv_path)
        self.headless = headless
        self.businesses = []
        self.results = []

        # Email regex pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )

        # Common contact page paths
        self.contact_paths = [
            '/contact',
            '/contact-us',
            '/contactus',
            '/about/contact',
            '/about',
            '/about-us',
            '/get-in-touch',
            '/reach-us'
        ]

        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging to file and console."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = log_dir / f"email_scraper_{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Email Scraper Agent started")
        self.logger.info(f"Log file: {log_file}")

    def load_csv(self):
        """Load businesses from CSV file."""
        if not self.csv_path.exists():
            self.logger.error(f"CSV file not found: {self.csv_path}")
            sys.exit(1)

        with open(self.csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            self.businesses = list(reader)

        self.logger.info(f"Loaded {len(self.businesses)} businesses from CSV")

    def extract_emails_from_text(self, text):
        """
        Extract email addresses from text using regex.

        Args:
            text: Text content to search

        Returns:
            Set of email addresses found
        """
        if not text:
            return set()

        emails = set(self.email_pattern.findall(text))

        # Filter out common false positives
        filtered = set()
        for email in emails:
            # Skip image file extensions, common assets
            if email.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.css', '.js')):
                continue
            # Skip example/placeholder emails
            if 'example.com' in email.lower() or 'domain.com' in email.lower():
                continue
            # Skip very generic catch-all patterns
            if email.startswith('http') or '@wordpress' in email.lower():
                continue
            filtered.add(email.lower())

        return filtered

    def find_contact_page(self, page, base_url):
        """
        Try to find and navigate to contact page.

        Args:
            page: Playwright page object
            base_url: Base URL of the website

        Returns:
            True if contact page found and navigated, False otherwise
        """
        # Look for contact links in the page
        try:
            # Try common link text
            contact_link_texts = [
                'contact us', 'contact', 'get in touch',
                'reach us', 'about', 'about us'
            ]

            for link_text in contact_link_texts:
                try:
                    # Look for links containing this text (case insensitive)
                    link = page.locator(f'a:has-text("{link_text}")').first
                    if link.count() > 0:
                        href = link.get_attribute('href')
                        if href:
                            # Construct full URL
                            full_url = urljoin(base_url, href)
                            self.logger.info(f"  Found contact link: {full_url}")
                            page.goto(full_url, wait_until='domcontentloaded', timeout=10000)
                            return True
                except Exception:
                    continue

            # Try direct paths if links not found
            for path in self.contact_paths:
                try:
                    test_url = urljoin(base_url, path)
                    response = page.goto(test_url, wait_until='domcontentloaded', timeout=10000)
                    if response and response.status == 200:
                        self.logger.info(f"  Found contact page at: {test_url}")
                        return True
                except Exception:
                    continue

        except Exception as e:
            self.logger.debug(f"  Error finding contact page: {e}")

        return False

    def scrape_website(self, page, business):
        """
        Scrape email addresses from a business website.

        Args:
            page: Playwright page object
            business: Dictionary with business info

        Returns:
            Dictionary with scraping results
        """
        name = business.get('Name', 'Unknown')
        website = business.get('Website', '').strip()

        result = {
            'Name': name,
            'Website': website,
            'Emails': set(),
            'Status': 'Not Found',
            'Notes': ''
        }

        if not website or website.startswith('http') is False:
            result['Status'] = 'No Website'
            return result

        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Scraping: {name}")
        self.logger.info(f"URL: {website}")

        try:
            # Navigate to homepage
            self.logger.info("  Loading homepage...")
            response = page.goto(website, wait_until='domcontentloaded', timeout=15000)

            if not response or response.status != 200:
                result['Status'] = f'HTTP {response.status if response else "No Response"}'
                result['Notes'] = 'Failed to load'
                self.logger.warning(f"  Failed to load: HTTP {response.status if response else 'No Response'}")
                return result

            # Wait for page to settle
            time.sleep(1)

            # Get page content
            page_text = page.content()
            emails_found = self.extract_emails_from_text(page_text)

            if emails_found:
                result['Emails'].update(emails_found)
                self.logger.info(f"  Found {len(emails_found)} email(s) on homepage")

            # Try to find and visit contact page
            self.logger.info("  Looking for contact page...")
            if self.find_contact_page(page, website):
                time.sleep(1)
                contact_text = page.content()
                contact_emails = self.extract_emails_from_text(contact_text)

                if contact_emails:
                    result['Emails'].update(contact_emails)
                    self.logger.info(f"  Found {len(contact_emails)} email(s) on contact page")

            # Update result
            if result['Emails']:
                result['Status'] = 'Success'
                email_list = ', '.join(sorted(result['Emails']))
                result['Notes'] = f"Found: {email_list}"
                self.logger.info(f"  ✓ Total emails found: {email_list}")
            else:
                result['Status'] = 'No Email Found'
                result['Notes'] = 'Website loaded but no email addresses found'
                self.logger.info("  ✗ No emails found")

        except PlaywrightTimeout:
            result['Status'] = 'Timeout'
            result['Notes'] = 'Page load timeout (15s)'
            self.logger.warning(f"  Timeout loading page")

        except Exception as e:
            result['Status'] = 'Error'
            result['Notes'] = f'Error: {str(e)[:100]}'
            self.logger.error(f"  Error: {e}")

        return result

    def run(self, start_index=0, max_businesses=None, delay=2):
        """
        Run the email scraper agent.

        Args:
            start_index: Index to start from (for resuming)
            max_businesses: Maximum number of businesses to process (None for all)
            delay: Delay in seconds between requests (default 2)
        """
        self.load_csv()

        # Determine range to process
        end_index = len(self.businesses)
        if max_businesses:
            end_index = min(start_index + max_businesses, end_index)

        to_process = self.businesses[start_index:end_index]

        self.logger.info(f"Processing businesses {start_index} to {end_index-1} ({len(to_process)} total)")
        self.logger.info(f"Delay between requests: {delay} seconds")
        self.logger.info(f"Headless mode: {self.headless}")
        print()

        # Start browser
        with sync_playwright() as p:
            self.logger.info("Launching browser...")
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()

            try:
                for idx, business in enumerate(to_process, start=start_index):
                    # Scrape website
                    result = self.scrape_website(page, business)
                    self.results.append(result)

                    # Progress
                    progress = idx - start_index + 1
                    total = len(to_process)
                    self.logger.info(f"Progress: {progress}/{total} ({progress*100//total}%)")

                    # Delay between requests (except for last one)
                    if idx < end_index - 1:
                        time.sleep(delay)

            finally:
                browser.close()

        # Save results
        self.save_results()
        self.show_summary()

    def save_results(self):
        """Save results to updated CSV file."""
        output_path = self.csv_path.parent / f"{self.csv_path.stem}_scraped.csv"

        # Merge results with original data
        updated_businesses = []

        # Create lookup for results
        results_by_name = {r['Name']: r for r in self.results}

        for business in self.businesses:
            name = business.get('Name', '')

            # If we have a result for this business, update it
            if name in results_by_name:
                result = results_by_name[name]

                # Update email field if emails were found
                if result['Emails']:
                    business['Email'] = ', '.join(sorted(result['Emails']))
                    business['Status'] = result['Status']
                else:
                    # Keep original email if no new emails found
                    business['Status'] = result['Status']

                # Update notes
                business['Notes'] = business.get('Notes', '') + ' | ' + result['Notes']
                business['Notes'] = business['Notes'].strip(' |')

            updated_businesses.append(business)

        # Write updated CSV
        if updated_businesses:
            fieldnames = list(updated_businesses[0].keys())

            with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(updated_businesses)

            self.logger.info(f"\nResults saved to: {output_path}")

    def show_summary(self):
        """Display summary of scraping results."""
        total = len(self.results)
        success = sum(1 for r in self.results if r['Status'] == 'Success')
        no_email = sum(1 for r in self.results if r['Status'] == 'No Email Found')
        errors = sum(1 for r in self.results if r['Status'] in ['Error', 'Timeout'])
        total_emails = sum(len(r['Emails']) for r in self.results)

        print("\n" + "="*60)
        print("SCRAPING SUMMARY")
        print("="*60)
        print(f"Total Businesses Processed: {total}")
        print(f"Emails Found: {success} businesses ({total_emails} total email addresses)")
        print(f"No Email Found: {no_email}")
        print(f"Errors/Timeouts: {errors}")
        print(f"Success Rate: {success*100//total if total > 0 else 0}%")
        print("="*60)

        if success > 0:
            print("\nBusinesses with emails found:")
            for result in self.results:
                if result['Emails']:
                    emails = ', '.join(sorted(result['Emails']))
                    print(f"  ✓ {result['Name']}: {emails}")


def main():
    """Main entry point."""
    print("="*60)
    print("Email Scraper Agent - Local Website Email Extractor")
    print("="*60)
    print()

    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python email_scraper_agent.py <csv_file> [options]")
        print("\nOptions:")
        print("  --start <index>     Start from this row (default: 0)")
        print("  --max <count>       Process max this many businesses (default: all)")
        print("  --delay <seconds>   Delay between requests (default: 2)")
        print("  --visible           Show browser window (not headless)")
        print("\nExample:")
        print("  python email_scraper_agent.py businesses.csv")
        print("  python email_scraper_agent.py businesses.csv --start 10 --max 20")
        print("  python email_scraper_agent.py businesses.csv --visible --delay 3")
        sys.exit(1)

    csv_path = sys.argv[1]

    # Parse options
    start_index = 0
    max_businesses = None
    delay = 2
    headless = True

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--start' and i + 1 < len(sys.argv):
            start_index = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--max' and i + 1 < len(sys.argv):
            max_businesses = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--delay' and i + 1 < len(sys.argv):
            delay = float(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--visible':
            headless = False
            i += 1
        else:
            print(f"Unknown option: {sys.argv[i]}")
            sys.exit(1)

    # Create and run agent
    try:
        agent = EmailScraperAgent(csv_path, headless=headless)
        agent.run(start_index=start_index, max_businesses=max_businesses, delay=delay)

    except KeyboardInterrupt:
        print("\n\nStopped by user. Results saved.")

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
