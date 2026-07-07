param(
    [switch]$Docker,
    [switch]$Help
)

if ($Help) {
    @"
SymptomScope AI - Run Script
============================
Usage: .\run.ps1 [options]

Options:
  -Docker     Run using docker-compose (default: local dev)
  -Help       Show this help

Examples:
  .\run.ps1              # local dev mode
  .\run.ps1 -Docker      # Docker mode
"@
    exit
}

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

if ($Docker) {
    Write-Host "=== Starting SymptomScope AI (Docker) ===" -ForegroundColor Cyan
    Set-Location -LiteralPath $Root
    docker-compose up --build
    exit
}

# --- Local Development Mode ---
Write-Host "=== Starting SymptomScope AI (Local Dev) ===" -ForegroundColor Cyan

# 1. Check MongoDB
$mongoRunning = $false
try {
    $mongo = Get-Process -Name "mongod" -ErrorAction SilentlyContinue
    if ($mongo) { $mongoRunning = $true }
} catch {}

if (-not $mongoRunning) {
    Write-Host "[!] MongoDB (mongod) is not running." -ForegroundColor Yellow
    Write-Host "    Start it manually or run with -Docker flag." -ForegroundColor Yellow
} else {
    Write-Host "[OK] MongoDB is running" -ForegroundColor Green
}

# 2. Start Backend
$backendJob = Start-Job -Name "SymptomScope-Backend" -ScriptBlock {
    param($root)
    Set-Location -LiteralPath "$root\backend"
    Write-Host "[Backend] Starting uvicorn on http://localhost:8000" -ForegroundColor Green
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
} -ArgumentList $Root

# 3. Start Frontend
$frontendJob = Start-Job -Name "SymptomScope-Frontend" -ScriptBlock {
    param($root)
    Set-Location -LiteralPath "$root\frontend"
    Write-Host "[Frontend] Starting Next.js on http://localhost:3000" -ForegroundColor Green
    npm run dev
} -ArgumentList $Root

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all services." -ForegroundColor Yellow

# Wait for either job to finish or user to press Ctrl+C
try {
    while ($true) {
        $bState = (Get-Job -Name "SymptomScope-Backend").State
        $fState = (Get-Job -Name "SymptomScope-Frontend").State
        if ($bState -eq "Failed") {
            Write-Host "[Backend] Failed. Check output above." -ForegroundColor Red
            Receive-Job -Name "SymptomScope-Backend"
            break
        }
        if ($fState -eq "Failed") {
            Write-Host "[Frontend] Failed. Check output above." -ForegroundColor Red
            Receive-Job -Name "SymptomScope-Frontend"
            break
        }
        Start-Sleep -Seconds 2
    }
} finally {
    Write-Host "`nStopping services..." -ForegroundColor Yellow
    Stop-Job -Name "SymptomScope-Backend" -ErrorAction SilentlyContinue
    Stop-Job -Name "SymptomScope-Frontend" -ErrorAction SilentlyContinue
    Remove-Job -Name "SymptomScope-Backend" -ErrorAction SilentlyContinue
    Remove-Job -Name "SymptomScope-Frontend" -ErrorAction SilentlyContinue
    Write-Host "Done." -ForegroundColor Green
}
