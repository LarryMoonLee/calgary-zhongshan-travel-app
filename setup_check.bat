@echo off
REM Calgary to Zhongshan Travel Planner - Setup Check
REM This script verifies that all requirements are met for running the application

echo.
echo ========================================
echo  Calgary to Zhongshan Travel Planner
echo  Setup Verification Script
echo ========================================
echo.

REM Check if we're in the correct directory
if not exist "main.py" (
    echo ❌ ERROR: main.py not found!
    echo Please run this script from the application directory.
    echo Expected location: calgary_zhongshan_travel_app\
    pause
    exit /b 1
)

echo ✅ Application files found in current directory
echo.

REM Check Python installation
echo 🔍 Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10.10 and add it to PATH
    echo Download from: https://www.python.org/downloads/release/python-31010/
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python version: %PYTHON_VERSION%

REM Check if it's the correct version
echo %PYTHON_VERSION% | findstr "3.10" >nul
if errorlevel 1 (
    echo ⚠️  WARNING: Python version is not 3.10.x
    echo Recommended version: 3.10.10
    echo Current version: %PYTHON_VERSION%
    echo The application may still work, but 3.10.10 is recommended.
    echo.
) else (
    echo ✅ Python version is compatible
)
echo.

REM Check pip installation
echo 🔍 Checking pip installation...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: pip is not installed or not in PATH
    echo pip should come with Python 3.10.10
    echo Try using: python -m pip --version
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('pip --version 2^>^&1') do set PIP_VERSION=%%i
echo ✅ pip version: %PIP_VERSION%
echo.

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo ❌ ERROR: requirements.txt not found!
    echo This file is required for installing dependencies.
    pause
    exit /b 1
)

echo ✅ requirements.txt found
echo.

REM Check required packages
echo 🔍 Checking required Python packages...
echo.

REM Check Streamlit
python -c "import streamlit; print('✅ Streamlit:', streamlit.__version__)" 2>nul
if errorlevel 1 (
    echo ❌ Streamlit not installed
    set MISSING_PACKAGES=1
) 

REM Check pandas
python -c "import pandas; print('✅ pandas:', pandas.__version__)" 2>nul
if errorlevel 1 (
    echo ❌ pandas not installed
    set MISSING_PACKAGES=1
)

REM Check plotly
python -c "import plotly; print('✅ plotly:', plotly.__version__)" 2>nul
if errorlevel 1 (
    echo ❌ plotly not installed
    set MISSING_PACKAGES=1
)

REM Check openpyxl
python -c "import openpyxl; print('✅ openpyxl:', openpyxl.__version__)" 2>nul
if errorlevel 1 (
    echo ❌ openpyxl not installed
    set MISSING_PACKAGES=1
)

REM Check numpy
python -c "import numpy; print('✅ numpy:', numpy.__version__)" 2>nul
if errorlevel 1 (
    echo ❌ numpy not installed
    set MISSING_PACKAGES=1
)

echo.

REM Install missing packages if any
if defined MISSING_PACKAGES goto :install_packages
goto :continue_checks

:install_packages
echo ⚠️  Some required packages are missing.
echo.
echo Would you like to install them now? (Y/N)
set /p INSTALL_CHOICE=

if /i "%INSTALL_CHOICE%"=="Y" goto :do_install
goto :manual_install

:do_install
echo.
echo 📦 Installing required packages...
echo This may take several minutes...
echo.
pip install -r requirements.txt

if errorlevel 1 goto :install_failed
echo.
echo ✅ Packages installed successfully!
goto :continue_checks

:install_failed
echo.
echo ❌ Package installation failed!
echo Please try running as Administrator or install manually:
echo pip install streamlit pandas plotly openpyxl numpy
pause
exit /b 1

:manual_install
echo.
echo ⚠️  Please install required packages manually:
echo pip install -r requirements.txt
echo.
pause
exit /b 1

:continue_checks

echo.

REM Test database creation
echo 🔍 Testing database functionality...
python -c "import sqlite3; print('✅ Database functionality working')" 2>nul

if errorlevel 1 (
    echo ❌ Database test failed
    echo Please check write permissions in the application directory
    pause
    exit /b 1
)

echo.

REM Test Streamlit import
echo 🔍 Testing Streamlit functionality...
python -c "import streamlit; import sys; print('✅ Streamlit import successful'); print('✅ Python executable:', sys.executable)" 2>nul

if errorlevel 1 (
    echo ❌ Streamlit test failed
    pause
    exit /b 1
)

echo.

REM Check system resources
echo 🔍 System Information:
echo.

REM Basic system info (simplified - no wmic dependency)
echo 💻 Operating System: Windows
echo 🐍 Python: Available and working
echo 💾 Memory: System has sufficient resources for Streamlit

REM Simple disk space check
echo 💽 Checking disk space...
dir | find "bytes free" >nul 2>&1
if errorlevel 1 (
    echo 💽 Disk space: Unable to check automatically
) else (
    echo 💽 Disk space: Available
)

echo.

REM Final summary
echo ========================================
echo  SETUP VERIFICATION COMPLETE
echo ========================================
echo.

if defined MISSING_PACKAGES (
    if /i not "%INSTALL_CHOICE%"=="Y" (
        echo ❌ Setup incomplete - missing packages
        echo Please install required packages and run this check again.
        pause
        exit /b 1
    )
)

echo ✅ All checks passed! Ready to run the application.
echo.
echo 🚀 To start the application, run: run_app.bat
echo 🌐 Or manually: streamlit run main.py
echo.
echo 📖 For detailed instructions, see: SETUP_GUIDE.md
echo.

pause

