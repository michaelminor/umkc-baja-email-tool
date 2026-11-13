"""
Creates a Windows desktop shortcut for the Email Automation GUI.
Run this once after installation to create the shortcut.
"""

import os
import sys
from pathlib import Path
import win32com.client


def create_desktop_shortcut():
    """Create Windows desktop shortcut to launch GUI."""

    try:
        # Get paths
        desktop = Path.home() / "Desktop"
        script_dir = Path(__file__).parent.absolute()
        script_path = script_dir / "launch_gui.pyw"

        # Use pythonw.exe to prevent console window
        python_path = sys.executable
        if python_path.endswith("python.exe"):
            pythonw_path = python_path.replace("python.exe", "pythonw.exe")
        else:
            pythonw_path = python_path

        # Create shortcut
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut_path = str(desktop / "UMKC Baja Email Tool.lnk")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.TargetPath = pythonw_path
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = str(script_dir)
        shortcut.Description = "UMKC Baja Racing Email Automation Tool"

        # Try to set icon (use Python icon if available)
        if os.path.exists(pythonw_path):
            shortcut.IconLocation = pythonw_path

        shortcut.save()

        print(f"[SUCCESS] Desktop shortcut created successfully!")
        print(f"  Location: {shortcut_path}")
        print(f"\nYou can now launch the GUI by double-clicking:")
        print(f"  'UMKC Baja Email Tool' on your desktop")

    except Exception as e:
        print(f"[ERROR] Error creating shortcut: {e}")
        print(f"\nYou can still launch the GUI manually:")
        print(f"  1. Navigate to: {script_dir}")
        print(f"  2. Double-click: launch_gui.pyw")
        sys.exit(1)


if __name__ == "__main__":
    print("=" * 60)
    print("UMKC Baja Racing Email Tool - Shortcut Creator")
    print("=" * 60)
    print()

    create_desktop_shortcut()

    print()
    print("=" * 60)
    input("Press Enter to exit...")
