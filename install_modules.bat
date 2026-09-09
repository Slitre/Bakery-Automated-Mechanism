@echo off

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b
)

REM Install the necessary modules using pip and the requirements.txt file
echo Installing required Python modules...
pip install -r requirements.txt

REM Check if the installation was successful
if %errorlevel% neq 0 (
    echo Failed to install required modules. Please check your Python and pip installation.
    exit /b
)

echo Modules installed successfully!
pause
