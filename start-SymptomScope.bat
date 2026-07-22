@echo off
title SymptomScope AI Launcher
cd /d "%~dp0"

setlocal enabledelayedexpansion

cls
echo ============================================
echo    SymptomScope AI - Startup Launcher
echo ============================================
echo.

REM Define colors using ANSI escape codes
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "NC=[0m"

call :log "CYAN" "Checking prerequisites..."

REM Check Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    call :log "RED" "Node.js not found. Please install Node.js 18+ from https://nodejs.org"
    pause
    exit /b 1
)
for /f "tokens=1,2,3 delims=." %%a in ('node --version') do set NODE_VER=%%a
call :log "GREEN" "Node.js found: %NODE_VER%"

REM Check Python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    call :log "RED" "Python not found. Please install Python 3.10+ from https://python.org"
    pause
    exit /b 1
)
for /f "tokens=1,2 delims= " %%a in ('python --version 2^>^&1') do set PYTHON_VER=%%a %%b
call :log "GREEN" "Python found: %PYTHON_VER%"

REM Check npm
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    call :log "RED" "npm not found."
    pause
    exit /b 1
)
call :log "GREEN" "npm found"

REM Check if MongoDB is running
call :log "CYAN" "Checking MongoDB connection..."
python -c "import socket; s=socket.socket(); s.settimeout(3); s.connect(('localhost', 27017)); s.close(); print('ok')" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    call :log "GREEN" "MongoDB is running on localhost:27017"
) else (
    call :log "YELLOW" "MongoDB not detected on localhost:27017"
    call :log "YELLOW" "Make sure MongoDB Atlas URI is configured in backend/.env"
    call :log "YELLOW" "or start local MongoDB and try again."
)

echo.
call :log "CYAN" "Starting SymptomScope AI services..."
echo.

REM Set working directories
set "BACKEND_DIR=%CD%\backend"
set "FRONTEND_DIR=%CD%\frontend"

REM Install backend dependencies if needed
if not exist "%BACKEND_DIR%\venv\" (
    call :log "CYAN" "Creating Python virtual environment..."
    cd /d "%BACKEND_DIR%"
    python -m venv venv
    if !ERRORLEVEL! NEQ 0 (
        call :log "RED" "Failed to create virtual environment"
        pause
        exit /b 1
    )
)

call :log "CYAN" "Installing backend dependencies..."
cd /d "%BACKEND_DIR%"
call venv\Scripts\activate.bat && pip install -q -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    call :log "YELLOW" "Some dependencies may already be installed, continuing..."
)

REM Install frontend dependencies if needed
if not exist "%FRONTEND_DIR%\node_modules\" (
    call :log "CYAN" "Installing frontend dependencies..."
    cd /d "%FRONTEND_DIR%"
    call npm install --silent
    if !ERRORLEVEL! NEQ 0 (
        call :log "RED" "Failed to install frontend dependencies"
        pause
        exit /b 1
    )
)

echo.
call :log "CYAN" "============================================"
call :log "CYAN" "  Starting Backend (FastAPI) on port 8080"
call :log "CYAN" "============================================"
echo.

REM Start backend
cd /d "%BACKEND_DIR%"
start "SymptomScope-Backend" cmd /c "title SymptomScope Backend && call venv\Scripts\activate.bat && uvicorn main:app --host 0.0.0.0 --port 8080 --reload"

REM Wait for backend to be ready
call :log "CYAN" "Waiting for backend to start..."
:wait-backend
timeout /t 2 /nobreak >nul
python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    goto wait-backend
)
call :log "GREEN" "Backend is running on http://localhost:8080"
call :log "GREEN" "API Docs: http://localhost:8080/docs"

echo.
call :log "CYAN" "============================================"
call :log "CYAN" "  Starting Frontend (Next.js) on port 3000"
call :log "CYAN" "============================================"
echo.

REM Start frontend
cd /d "%FRONTEND_DIR%"
start "SymptomScope-Frontend" cmd /c "title SymptomScope Frontend && npm run dev"

REM Wait for frontend to be ready
call :log "CYAN" "Waiting for frontend to start..."
:wait-frontend
timeout /t 3 /nobreak >nul
python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000')" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    goto wait-frontend
)
call :log "GREEN" "Frontend is running on http://localhost:3000"

echo.
call :log "GREEN" "============================================"
call :log "GREEN" "  SymptomScope AI is fully operational!"
call :log "GREEN" "============================================"
echo.
call :log "CYAN" "  Frontend:  http://localhost:3000"
call :log "CYAN" "  Backend:   http://localhost:8080"
call :log "CYAN" "  API Docs:  http://localhost:8080/docs"
echo.
call :log "CYAN" "  Press any key to open the application in your browser..."
echo.
pause >nul
start http://localhost:3000
echo.
call :log "YELLOW" "Close this window to stop all services."
echo.

REM Wait for user to close the window
pause >nul

goto :eof

:log
set "color=%~1"
set "message=%~2"
echo %~date% %~time% [%color%LOG%NC%] %message%
goto :eof
