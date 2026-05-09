@echo off
echo Starting deployment process...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.10 or higher.
    exit /b 1
)

REM Check if venv exists, create if not
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
if not exist research_analyzer\results mkdir research_analyzer\results
if not exist research_analyzer\web\templates mkdir research_analyzer\web\templates

REM Start the services
echo Starting services...
start "Medical Research Scheduler" cmd /c "python -m research_analyzer.scheduler"
start "Medical Research Web Server" cmd /c "python -m research_analyzer.web.app"

echo Deployment complete! Services are running.
echo Web interface available at: http://localhost:5000
echo QR codes will be generated in: research_analyzer/results/
