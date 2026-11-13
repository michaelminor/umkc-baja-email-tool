"""
Creates a portable distribution package for the UMKC Baja Email Tool.
Run this to create a zip file that can be emailed to others.

Usage: py package_for_distribution.py
"""

import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def create_distribution():
    """Create distribution package as a zip file."""

    print("=" * 60)
    print("UMKC Baja Email Tool - Distribution Packager")
    print("=" * 60)
    print()

    # Directories
    project_root = Path(__file__).parent
    dist_dir = project_root / "dist"
    timestamp = datetime.now().strftime('%Y%m%d')
    dist_name = f"UMKCBajaEmailTool_v1.0_{timestamp}"
    package_dir = dist_dir / dist_name

    # Clean and create dist directory
    if package_dir.exists():
        print(f"Cleaning existing package directory...")
        shutil.rmtree(package_dir)

    package_dir.mkdir(parents=True)
    print(f"Creating package: {dist_name}")
    print()

    # Files to include
    files_to_copy = [
        "installer.py",
        "RUN_INSTALLER.bat",
        "SETUP_CONFIG.bat",
        "requirements.txt",
        "README.md",
        "QUICKSTART.md",
        "GUI_GUIDE.md",
        "SCRAPER_GUIDE.md",
        "launch_gui.pyw",
        "email_scraper_agent.py",
        "run_scraper.bat"
    ]

    # Directories to include
    dirs_to_copy = [
        "email_automation",
        "templates"
    ]

    # Copy files
    print("Copying files...")
    for file in files_to_copy:
        src = project_root / file
        if src.exists():
            shutil.copy(src, package_dir / file)
            print(f"  [OK] {file}")
        else:
            print(f"  [SKIP] {file} (not found)")

    # Copy directories
    print("\nCopying directories...")
    for dir_name in dirs_to_copy:
        src = project_root / dir_name
        dst = package_dir / dir_name
        if src.exists():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns(
                '__pycache__', '*.pyc', '*.pyo', '.git', '.vscode'
            ))
            print(f"  [OK] {dir_name}/")
        else:
            print(f"  [SKIP] {dir_name}/ (not found)")

    # Create INSTALL.txt with instructions
    print("\nCreating installation instructions...")
    install_instructions = f"""
================================================================================
UMKC Baja Racing Email Tool - Installation Instructions
================================================================================

Thank you for using the UMKC Baja Racing Email Automation Tool!

This is a portable installer that works on any Windows computer.

REQUIREMENTS:
-------------
- Windows 10/11
- Python 3.7 or higher (download from https://www.python.org/downloads/)
- Microsoft Outlook installed and configured with an email account

INSTALLATION STEPS:
-------------------
1. Extract this entire ZIP file to any location on your computer

2. Run the installer (choose ONE method):

   METHOD A (EASIEST):
   - Double-click "RUN_INSTALLER.bat"

   METHOD B:
   - Double-click "installer.py"
   - If it opens in an editor instead, right-click → Open With → Python

   METHOD C:
   - Open Command Prompt in this folder
   - Run: py installer.py

3. The installer will:
   - Create the installation in Documents/UMKCBajaEmailTool/
   - Install required Python packages
   - Create a desktop shortcut
   - Set up the initial configuration

4. Follow the on-screen prompts

AFTER INSTALLATION:
-------------------
1. Create your sponsorship packet (Word document)
   Location: Documents/UMKCBajaEmailTool/templates/sponsorship_packet.docx

2. Add CSV files with recipient information
   Location: Documents/UMKCBajaEmailTool/csv_files/
   Format: Name,Email,Status (see SAMPLE_recipients.csv)

3. Launch the tools:

   EMAIL SENDER (send bulk emails):
   - Double-click "UMKC Baja Email Tool" on your desktop
   - Or navigate to Documents/UMKCBajaEmailTool/ and run launch_gui.pyw

   EMAIL SCRAPER (find contact emails from websites):
   - Double-click run_scraper.bat in Documents/UMKCBajaEmailTool/
   - Or run: py email_scraper_agent.py <csv_file>

DOCUMENTATION:
--------------
After installation, find these guides in your installation folder:
- QUICKSTART.md - Quick reference guide
- GUI_GUIDE.md - Complete GUI usage guide
- SCRAPER_GUIDE.md - Email scraper usage guide
- README.md - Full documentation

SUPPORT:
--------
For issues or questions:
1. Check the documentation files (listed above)
2. Check the Logs tab in the GUI for error details

SHARING THIS TOOL:
------------------
To install on another computer or share with a teammate:
1. Send them this ZIP file
2. They extract and run installer.py
3. Done! Each installation is independent

================================================================================
Package Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Version: 1.0
For: UMKC Baja Racing Team
================================================================================
"""

    with open(package_dir / "INSTALL.txt", 'w', encoding='utf-8') as f:
        f.write(install_instructions)
    print("  [OK] INSTALL.txt")

    # Create sample CSV
    print("\nCreating sample files...")
    sample_csv = package_dir / "SAMPLE_recipients.csv"
    with open(sample_csv, 'w', encoding='utf-8-sig') as f:
        f.write("Name,Email,Status\n")
        f.write("John Doe,john.doe@example.com,\n")
        f.write("Jane Smith,jane.smith@example.com,\n")
        f.write("Bob Johnson,bob.johnson@example.com,\n")
    print("  [OK] SAMPLE_recipients.csv")

    # Create zip file
    print("\nCreating ZIP archive...")
    zip_path = dist_dir / f"{dist_name}.zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in package_dir.rglob('*'):
            if file.is_file():
                arcname = file.relative_to(dist_dir)
                zipf.write(file, arcname)

    # Get zip file size
    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)

    # Clean up temp directory
    shutil.rmtree(package_dir)

    # Show summary
    print()
    print("=" * 60)
    print("Distribution Package Created Successfully!")
    print("=" * 60)
    print()
    print(f"Package: {zip_path.name}")
    print(f"Location: {zip_path}")
    print(f"Size: {zip_size_mb:.2f} MB")
    print()
    print("This ZIP file can be:")
    print("  - Emailed to teammates")
    print("  - Copied to your laptop")
    print("  - Shared via cloud storage")
    print()
    print("Recipients just need to:")
    print("  1. Extract the ZIP")
    print("  2. Run installer.py")
    print("  3. Follow the prompts")
    print()
    print("=" * 60)


if __name__ == "__main__":
    try:
        create_distribution()
        print()
        input("Press Enter to exit...")

    except Exception as e:
        print(f"\n[ERROR] Failed to create distribution: {e}")
        import traceback
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)
