@echo off
REM Creates configuration files if installer didn't create them

cd %USERPROFILE%\Documents\UMKCBajaEmailTool

echo Creating directories...
mkdir config 2>nul
mkdir data 2>nul
mkdir logs 2>nul
mkdir csv_files 2>nul

echo Creating settings.json...
(
echo {
echo   "email_subject": "University of Missouri - Kansas City Baja Racing team sponsorship outreach",
echo   "email_template_path": "templates/email_template.txt",
echo   "attachment_path": "templates/sponsorship_packet.docx",
echo   "csv_folder": "csv_files",
echo   "log_directory": "logs",
echo   "history_file": "data/sent_emails_history.txt"
echo }
) > config\settings.json

echo Creating email history file...
(
echo # Email History - One email per line
echo # This file tracks all emails ever sent to prevent duplicates
) > data\sent_emails_history.txt

echo.
echo ============================================================
echo Configuration created successfully!
echo ============================================================
echo.
echo Files created:
echo   - config\settings.json
echo   - data\sent_emails_history.txt
echo.
echo You can now launch the GUI!
echo.
pause
