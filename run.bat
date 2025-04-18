@echo off
echo Starting Financial Analysis Agent Application...

REM Check if Python is installed
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: Python is not installed
    exit /b 1
)

REM Check if npm is installed
where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Error: npm is not installed
    exit /b 1
)

REM Activate virtual environment if it exists
if exist .venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call .venv\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

echo Starting Python Flask backend...
start cmd /k "cd backend && python app.py"

REM Wait a moment for the backend to initialize
timeout /t 3 > nul

echo Starting Next.js frontend...
start cmd /k "cd frontend && npm run dev"

echo Services started!
echo Financial Analysis Agent is running at: http://localhost:3000 