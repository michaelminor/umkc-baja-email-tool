@echo off
REM Creates desktop shortcut for UMKC Baja Email Tool
REM Run this if the installer didn't create the shortcut

echo ============================================================
echo Creating Desktop Shortcut
echo ============================================================
echo.

cd %USERPROFILE%\Documents\UMKCBajaEmailTool

py create_shortcut.py

echo.
echo Done!
pause
