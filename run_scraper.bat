@echo off
REM Quick launcher for Email Scraper Agent
REM Double-click this file to run the scraper

echo ============================================================
echo Email Scraper Agent - Quick Launcher
echo ============================================================
echo.

REM Check if Playwright is installed
py -c "import playwright" 2>nul
if errorlevel 1 (
    echo [ERROR] Playwright not installed!
    echo.
    echo Installing Playwright...
    py -m pip install playwright
    echo.
    echo Installing Chromium browser...
    py -m playwright install chromium
    echo.
    echo Installation complete!
    echo.
)

REM Default CSV path
set CSV_PATH=C:\Users\mfmin\EmailOutreach\kc_businesses_websites.csv

echo Target CSV: %CSV_PATH%
echo.

REM Ask user for options
echo Choose an option:
echo   1. Test run (first 10 businesses)
echo   2. Small batch (first 30 businesses)
echo   3. Process all businesses
echo   4. Custom (you specify start/max)
echo   5. Cancel
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo Running TEST mode - first 10 businesses...
    echo.
    py email_scraper_agent.py "%CSV_PATH%" --max 10 --visible
    goto end
)

if "%choice%"=="2" (
    echo.
    echo Running SMALL BATCH mode - first 30 businesses...
    echo.
    py email_scraper_agent.py "%CSV_PATH%" --max 30
    goto end
)

if "%choice%"=="3" (
    echo.
    echo Running FULL mode - all businesses...
    echo This may take 15-20 minutes.
    echo.
    set /p confirm="Are you sure? (Y/N): "
    if /i "%confirm%"=="Y" (
        py email_scraper_agent.py "%CSV_PATH%"
    ) else (
        echo Cancelled.
    )
    goto end
)

if "%choice%"=="4" (
    echo.
    set /p start_row="Enter start row (0 for beginning): "
    set /p max_count="Enter max businesses to process: "
    echo.
    echo Running CUSTOM mode - starting from row %start_row%, max %max_count% businesses...
    echo.
    py email_scraper_agent.py "%CSV_PATH%" --start %start_row% --max %max_count%
    goto end
)

if "%choice%"=="5" (
    echo.
    echo Cancelled.
    goto end
)

echo.
echo Invalid choice. Exiting.

:end
echo.
echo.
pause
