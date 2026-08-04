@echo off
title SymptomScope AI Launcher
cd /d "%~dp0"

setlocal enabledelayedexpansion

cls
echo ============================================
echo    SymptomScope AI - Native Startup
echo ============================================
echo.

REM Check prerequisites
where mongod >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERR] mongod not found. Please install MongoDB Community Edition.
    echo       Download from: https://www.mongodb.com/try/download/community
    pause
    exit /b 1
)

where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERR] node not found. Please install Node.js 18+.
    echo       Download from: https://nodejs.org/
    pause
    exit /b 1
)

where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERR] npm not found.
    pause
    exit /b 1
)

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    where python3 >nul 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo [ERR] python not found. Please install Python 3.11+.
        echo       Download from: https://www.python.org/downloads/
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

echo [OK] mongod found
echo [OK] node found
echo [OK] npm found
echo [OK] python found
echo.

REM ── 1. Start MongoDB ────────────────────────────────────────────────
echo [INFO] Starting MongoDB...

tasklist /FI "IMAGENAME eq mongod.exe" 2>NUL | find /I /N "mongod.exe" >NUL
if %ERRORLEVEL% EQU 0 (
    echo [WARN] MongoDB already running
) else (
    echo [INFO] Starting mongod...
    start /b mongod --logpath "%TEMP%\symptomscope-mongod.log" --fork 2>nul
    if %ERRORLEVEL% NEQ 0 (
        start /b mongod --logpath "%TEMP%\symptomscope-mongod.log" 2>nul
    )
    
    REM Wait for MongoDB
    echo [INFO] Waiting for MongoDB to be ready...
    for /l %%i in (1,1,30) do (
        %PYTHON_CMD% -c "import socket;s=socket.socket();s.settimeout(1);s.connect(('localhost',27017));s.close()" >nul 2>nul
        if !ERRORLEVEL! EQU 0 (
            echo [OK] MongoDB ready on port 27017
            goto :backend_start
        )
        timeout /t 1 /nobreak >nul
    )
    echo [ERR] MongoDB failed to start within 30 seconds
    pause
    exit /b 1
)

:backend_start
REM ── 2. Start Backend ────────────────────────────────────────────────
echo.
echo [INFO] Starting Backend...

cd backend

if not exist ".venv" (
    echo [INFO] Creating virtual environment...
    %PYTHON_CMD% -m venv .venv
)

REM Detect OS for venv paths
if exist ".venv\Scripts\python.exe" (
    set VENV_PYTHON=.venv\Scripts\python.exe
    set UVICORN=.venv\Scripts\uvicorn.exe
) else if exist ".venv\bin\python" (
    set VENV_PYTHON=.venv\bin\python
    set UVICORN=.venv\bin\uvicorn
) else (
    echo [ERR] Virtual environment not found after creation
    pause
    exit /b 1
)

echo [INFO] Installing/updating Python dependencies...
%VENV_PYTHON% -m pip install -q -r requirements.txt

echo [INFO] Starting uvicorn on port 8080...
start /b %UVICORN% main:app --host 0.0.0.0 --port 8080 --workers 1

REM Wait for backend health
echo [INFO] Waiting for backend health check...
set /a timeout=60
set /a elapsed=0
:wait_backend
timeout /t 1 /nobreak >nul
set /a elapsed+=1
curl -sf http://localhost:8080/health >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend healthy on http://localhost:8080
    curl -s http://localhost:8080/health | %PYTHON_CMD% -m json.tool 2>nul || echo [OK] Backend responded
    goto :frontend_start
)
if %elapsed% GEQ %timeout% (
    echo [ERR] Backend failed to start within %timeout% seconds
    echo       Check backend\uvicorn.log
    pause
    exit /b 1
)
echo [..] Waiting for backend... (%elapsed%s)
goto :wait_backend

:frontend_start
REM ── 3. Start Frontend ───────────────────────────────────────────────
echo.
echo [INFO] Starting Frontend...

cd ..\frontend

if not exist "node_modules" (
    echo [INFO] Installing npm dependencies...
    npm install
)

echo [INFO] Starting Next.js dev server on port 3000...
start /b npx next dev --port 3000

REM Wait for frontend
echo [INFO] Waiting for frontend to be ready...
set /a timeout=60
set /a elapsed=0
:wait_frontend
timeout /t 1 /nobreak >nul
set /a elapsed+=1
curl -sf http://localhost:3000 >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Frontend ready on http://localhost:3000
    goto :running
)
if %elapsed% GEQ %timeout% (
    echo [WARN] Frontend may still be compiling
    echo        Check manually at http://localhost:3000
    goto :running
)
echo [..] Waiting for frontend... (%elapsed%s)
goto :wait_frontend

:running
REM ── 4. Running ──────────────────────────────────────────────────────
echo.
echo ============================================
echo    SymptomScope AI is fully operational!
echo ============================================
echo.
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8080
echo   API Docs:  http://localhost:8080/docs
echo   Health:    http://localhost:8080/health
echo.
echo   Press Ctrl+C to stop all services
echo.

REM Auto-open browser
start http://localhost:3000

REM Keep window open
pause >nul
goto :eof