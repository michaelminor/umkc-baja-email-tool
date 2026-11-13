#!/usr/bin/env python
"""
GUI Launcher for UMKC Baja Racing Email Automation Tool
.pyw extension prevents console window on Windows
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Change to project directory
os.chdir(project_root)

from email_automation.gui import EmailAutomationGUI

if __name__ == "__main__":
    app = EmailAutomationGUI()
    app.run()
