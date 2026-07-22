@echo off
title SymptomScope AI Launcher
cd /d "%~dp0"

setlocal enabledelayedexpansion

cls
echo ============================================
echo    SymptomScope AI - Docker Startup
echo ============================================
echo.

REM Check prerequisites
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERR] Docker not found. Please install Docker Desktop.
    echo       Download from: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

where docker-compose >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [WARN] docker-compose not found as separate command.
    echo        Will use 'docker compose' (Docker Compose V2).
    set "COMPOSE_CMD=docker compose"
) else (
    set "COMPOSE_CMD=docker-compose"
)

echo [INFO] Checking environment files...

if not exist "backend\.env" (
    echo [WARN] backend\.env not found. Creating from example...
    copy backend\.env.example backend\.env >nul
    echo [WARN] Edit backend\.env with your API keys (GEMINI_API_KEY, etc.)
)

if not exist "frontend\.env.local" (
    echo [WARN] frontend\.env.local not found. Creating from example...
    copy frontend\.env.example frontend\.env.local >nul
    echo [WARN] Edit frontend\.env.local with your Clerk keys
)

echo.
echo [INFO] Building and starting services...
echo.
%COMPOSE_CMD% up --build -d

if %ERRORLEVEL% NEQ 0 (
    echo [ERR] Docker Compose failed to start.
    pause
    exit /b 1
)

echo.
echo [INFO] Waiting for services to become healthy...
echo.

REM Wait for backend health
set /a timeout=120
set /a elapsed=0
:wait-backend
timeout /t 5 /nobreak >nul
set /a elapsed=elapsed+5
python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health', timeout=5)" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Backend is healthy on http://localhost:8080
    goto :frontend-wait
)
if %elapsed% GEQ %timeout% (
    echo [ERR] Backend failed to start within %timeout% seconds.
    echo       Check logs: docker compose logs backend
    pause
    exit /b 1
)
echo [..] Waiting for backend... (%elapsed%s)
goto :wait-backend

:frontend-wait
set /a elapsed=0
:wait-frontend
timeout /t 5 /nobreak >nul
set /a elapsed=elapsed+5
python -c "import urllib.request; urllib.request.urlopen('http://localhost:3000', timeout=5)" >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Frontend is ready on http://localhost:3000
    goto :launch
)
if %elapsed% GEQ %timeout% (
    echo [WARN] Frontend may still be compiling.
    echo        Check manually at http://localhost:3000
    goto :launch
)
echo [..] Waiting for frontend... (%elapsed%s)
goto :wait-frontend

:launch
echo.
echo ============================================
echo    SymptomScope AI is fully operational!
echo ============================================
echo.
echo   Frontend:  http://localhost:3000
echo   Backend:   http://localhost:8080
echo   API Docs:  http://localhost:8080/docs
echo.
echo   Press any key to open the application...
echo.
pause >nul
start http://localhost:3000
echo.
echo   Run 'docker compose down' to stop all services.
echo   Close this window to exit.
echo.
pause >nul
goto :eof
