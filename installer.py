"""
UMKC Baja Racing Email Tool - Installer
========================================
Run this script to install the tool on your computer.

Installation location: Documents/UMKCBajaEmailTool/
"""

import os
import sys
import shutil
import subprocess
import json
from pathlib import Path


class Installer:
    """Handles installation of the UMKC Baja Email Tool."""

    def __init__(self):
        """Initialize installer."""
        # Source directory (where this installer is)
        self.source_dir = Path(__file__).parent.resolve()

        # Target installation directory
        self.install_dir = Path.home() / "Documents" / "UMKCBajaEmailTool"

        # Track success/failure
        self.success = True

    def run(self):
        """Run the installation process."""
        print("=" * 60)
        print("UMKC Baja Racing Email Tool - Installer")
        print("=" * 60)
        print()
        print(f"Installing to: {self.install_dir}")
        print()

        try:
            # Check Python version
            self.check_python()

            # Create installation directory
            self.create_directories()

            # Copy files
            self.copy_files()

            # Install dependencies
            self.install_dependencies()

            # Create initial configuration
            self.create_config()

            # Create desktop shortcut
            self.create_shortcut()

            # Final message
            self.show_completion()

        except KeyboardInterrupt:
            print("\n\nInstallation cancelled by user.")
            sys.exit(1)

        except Exception as e:
            print(f"\n[ERROR] Installation failed: {e}")
            self.success = False
            sys.exit(1)

    def check_python(self):
        """Check Python version."""
        if sys.version_info < (3, 7):
            print("[ERROR] Python 3.7 or higher required")
            print(f"Current version: Python {sys.version_info.major}.{sys.version_info.minor}")
            print("\nPlease install Python 3.7+ from https://www.python.org/downloads/")
            sys.exit(1)

        print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} detected")

    def create_directories(self):
        """Create installation directories."""
        print("\nCreating directories...")

        dirs = [
            self.install_dir,
            self.install_dir / "email_automation",
            self.install_dir / "templates",
            self.install_dir / "config",
            self.install_dir / "data",
            self.install_dir / "logs",
            self.install_dir / "csv_files"
        ]

        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
            print(f"  [OK] {d.name}/")

        print(f"[OK] Installation directory created")

    def copy_files(self):
        """Copy all application files."""
        print("\nCopying application files...")

        # Copy Python package
        src_pkg = self.source_dir / "email_automation"
        dst_pkg = self.install_dir / "email_automation"

        if src_pkg.exists():
            shutil.copytree(src_pkg, dst_pkg, dirs_exist_ok=True,
                          ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '*.pyo'))
            print("  [OK] email_automation/")
        else:
            raise FileNotFoundError(f"Source package not found: {src_pkg}")

        # Copy launcher
        launcher_src = self.source_dir / "launch_gui.pyw"
        if launcher_src.exists():
            shutil.copy(launcher_src, self.install_dir / "launch_gui.pyw")
            print("  [OK] launch_gui.pyw")

        # Copy email scraper agent
        scraper_src = self.source_dir / "email_scraper_agent.py"
        if scraper_src.exists():
            shutil.copy(scraper_src, self.install_dir / "email_scraper_agent.py")
            print("  [OK] email_scraper_agent.py")

        # Copy scraper launcher batch file
        scraper_bat_src = self.source_dir / "run_scraper.bat"
        if scraper_bat_src.exists():
            shutil.copy(scraper_bat_src, self.install_dir / "run_scraper.bat")
            print("  [OK] run_scraper.bat")

        # Copy templates
        template_src = self.source_dir / "templates" / "email_template.txt"
        if template_src.exists():
            shutil.copy(template_src, self.install_dir / "templates" / "email_template.txt")
            print("  [OK] email_template.txt")

        # Copy placeholder for sponsorship packet
        placeholder_src = self.source_dir / "templates" / "PLACEHOLDER_sponsorship_packet.txt"
        if placeholder_src.exists():
            shutil.copy(placeholder_src, self.install_dir / "templates" / "PLACEHOLDER_sponsorship_packet.txt")
            print("  [OK] PLACEHOLDER_sponsorship_packet.txt")

        # Copy requirements
        req_src = self.source_dir / "requirements.txt"
        if req_src.exists():
            shutil.copy(req_src, self.install_dir / "requirements.txt")
            print("  [OK] requirements.txt")

        # Copy documentation
        for doc in ["README.md", "QUICKSTART.md", "GUI_GUIDE.md", "SCRAPER_GUIDE.md"]:
            doc_src = self.source_dir / doc
            if doc_src.exists():
                shutil.copy(doc_src, self.install_dir / doc)
                print(f"  [OK] {doc}")

        print("[OK] Application files copied")

    def install_dependencies(self):
        """Install Python dependencies."""
        print("\nInstalling dependencies...")

        requirements_file = self.install_dir / "requirements.txt"

        if not requirements_file.exists():
            print("[WARNING] requirements.txt not found, skipping dependency installation")
            return

        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-r", str(requirements_file), "--quiet"],
                check=True,
                capture_output=True
            )
            print("[OK] Dependencies installed (pywin32, colorama, playwright)")

            # Install Playwright browsers
            print("\nInstalling Playwright browsers...")
            print("  (This downloads Chromium browser, ~100MB)")
            try:
                subprocess.run(
                    [sys.executable, "-m", "playwright", "install", "chromium"],
                    check=True,
                    capture_output=True
                )
                print("[OK] Chromium browser installed")
            except subprocess.CalledProcessError:
                print("[WARNING] Failed to install Chromium browser")
                print("You can install it later with: py -m playwright install chromium")

        except subprocess.CalledProcessError as e:
            print(f"[WARNING] Failed to install dependencies: {e}")
            print("You may need to install manually: py -m pip install -r requirements.txt")

    def create_config(self):
        """Create initial configuration with relative paths."""
        print("\nCreating configuration...")

        config = {
            "email_subject": "University of Missouri - Kansas City Baja Racing team sponsorship outreach",
            "email_template_path": "templates/email_template.txt",
            "attachment_path": "templates/sponsorship_packet.docx",
            "csv_folder": "csv_files",
            "log_directory": "logs",
            "history_file": "data/sent_emails_history.txt"
        }

        config_file = self.install_dir / "config" / "settings.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)

        # Create history file
        history_file = self.install_dir / "data" / "sent_emails_history.txt"
        with open(history_file, 'w', encoding='utf-8') as f:
            f.write("# Email History - One email per line\n")
            f.write("# This file tracks all emails ever sent to prevent duplicates\n")

        print("[OK] Configuration created")

    def create_shortcut(self):
        """Create desktop shortcut."""
        print("\nCreating desktop shortcut...")

        try:
            import win32com.client

            desktop = Path.home() / "Desktop"
            pythonw = sys.executable.replace("python.exe", "pythonw.exe")
            launcher = self.install_dir / "launch_gui.pyw"

            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut_path = str(desktop / "UMKC Baja Email Tool.lnk")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = pythonw
            shortcut.Arguments = f'"{launcher}"'
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.Description = "UMKC Baja Racing Email Automation Tool"

            # Set icon if available
            if os.path.exists(pythonw):
                shortcut.IconLocation = pythonw

            shortcut.save()

            print(f"[OK] Desktop shortcut created: UMKC Baja Email Tool")

        except Exception as e:
            print(f"[WARNING] Could not create shortcut: {e}")
            print(f"You can manually run: {self.install_dir / 'launch_gui.pyw'}")

    def show_completion(self):
        """Show completion message with next steps."""
        print()
        print("=" * 60)
        print("Installation Complete!")
        print("=" * 60)
        print()
        print(f"Installation Directory:")
        print(f"  {self.install_dir}")
        print()
        print("Next Steps:")
        print()
        print("1. CREATE SPONSORSHIP PACKET (Required)")
        print(f"   - Create a Word document with your sponsorship information")
        print(f"   - Save as: {self.install_dir / 'templates' / 'sponsorship_packet.docx'}")
        print(f"   - See: {self.install_dir / 'templates' / 'PLACEHOLDER_sponsorship_packet.txt'}")
        print()
        print("2. ADD RECIPIENT CSV FILES")
        print(f"   - Create CSV files with columns: Name, Email, Status")
        print(f"   - Save in: {self.install_dir / 'csv_files'}")
        print(f"   - See SAMPLE_recipients.csv for format")
        print()
        print("3. LAUNCH THE TOOLS")
        print()
        print("   Email Sender:")
        print("   - Double-click 'UMKC Baja Email Tool' on your desktop")
        print("   - Or run: launch_gui.pyw")
        print()
        print("   Email Scraper (find business contact emails):")
        print("   - Double-click: run_scraper.bat")
        print(f"   - Or run: py email_scraper_agent.py <csv_file>")
        print()
        print("Documentation:")
        print(f"  - Quick Start: {self.install_dir / 'QUICKSTART.md'}")
        print(f"  - GUI Guide: {self.install_dir / 'GUI_GUIDE.md'}")
        print(f"  - Scraper Guide: {self.install_dir / 'SCRAPER_GUIDE.md'}")
        print(f"  - Full Docs: {self.install_dir / 'README.md'}")
        print()
        print("=" * 60)


if __name__ == "__main__":
    try:
        installer = Installer()
        installer.run()

        print()
        input("Press Enter to exit...")

    except Exception as e:
        print(f"\nUnexpected error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
