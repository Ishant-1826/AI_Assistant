@echo off
setlocal enabledelayedexpansion

:: ==============================================================================
:: CampusMind AI - One-Click Application Launcher (Windows)
:: Automatically checks environment, manages virtualenv, installs dependencies,
:: starts backend and frontend servers in separate windows, and opens browser.
:: ==============================================================================

title CampusMind AI - Launcher
chcp 65001 >nul 2>&1

:: 1. Detect project root directory automatically
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo ============================================================
echo    CampusMind AI - Intelligent College Student Assistant
echo ============================================================
echo.

:: ------------------------------------------------------------------------------
:: 2. Check whether Python is installed
:: ------------------------------------------------------------------------------
echo [INFO] Checking system prerequisites...

set "PYTHON_CMD="
where python >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
) else (
    where py >nul 2>&1
    if not errorlevel 1 (
        set "PYTHON_CMD=py -3"
    )
)

if not defined PYTHON_CMD (
    echo.
    echo ============================================================
    echo [ERROR] Python 3 was not found in your system PATH!
    echo ============================================================
    echo Please download and install Python 3.10+ from:
    echo   https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Make sure to check the option:
    echo   "[X] Add python.exe to PATH" during installation.
    echo ============================================================
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('%PYTHON_CMD% --version 2^>^&1') do set "PY_VER=%%v"
echo [INFO] Found Python: !PY_VER!

:: ------------------------------------------------------------------------------
:: 3. Check Node.js and npm if frontend exists
:: ------------------------------------------------------------------------------
if exist "frontend\package.json" (
    where node >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ============================================================
        echo [ERROR] Node.js is required for the frontend but was not found!
        echo ============================================================
        echo Please download and install Node.js v18 or newer from:
        echo   https://nodejs.org/
        echo ============================================================
        echo.
        pause
        exit /b 1
    )
    for /f "tokens=*" %%v in ('node --version 2^>^&1') do set "NODE_VER=%%v"
    echo [INFO] Found Node.js: !NODE_VER!

    where npm >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ============================================================
        echo [ERROR] npm was not found in your system PATH!
        echo ============================================================
        echo Please install or repair your Node.js installation.
        echo ============================================================
        echo.
        pause
        exit /b 1
    )
    for /f "tokens=*" %%v in ('npm --version 2^>^&1') do set "NPM_VER=%%v"
    echo [INFO] Found npm: !NPM_VER!
)

:: ------------------------------------------------------------------------------
:: 4. Create and activate Python virtual environment
:: ------------------------------------------------------------------------------
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Creating Python virtual environment in .\venv...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo.
        echo ============================================================
        echo [ERROR] Failed to create Python virtual environment.
        echo ============================================================
        echo.
        pause
        exit /b 1
    )
    echo [SUCCESS] Python virtual environment created.
) else (
    echo [INFO] Python virtual environment detected in .\venv.
)

echo [INFO] Activating virtual environment...
call "venv\Scripts\activate.bat"
if errorlevel 1 (
    echo.
    echo ============================================================
    echo [ERROR] Failed to activate virtual environment.
    echo ============================================================
    echo.
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment activated.

:: ------------------------------------------------------------------------------
:: 5. Install / update backend dependencies from requirements.txt
:: ------------------------------------------------------------------------------
set "REQ_FILE="
if exist "requirements.txt" (
    set "REQ_FILE=requirements.txt"
) else if exist "backend\requirements.txt" (
    set "REQ_FILE=backend\requirements.txt"
)

if defined REQ_FILE (
    echo [INFO] Verifying backend dependencies from %REQ_FILE%...
    python -m pip install --upgrade pip --quiet >nul 2>&1
    pip install -r "%REQ_FILE%"
    if errorlevel 1 (
        echo.
        echo ============================================================
        echo [ERROR] Failed to install backend dependencies from %REQ_FILE%.
        echo ============================================================
        echo.
        pause
        exit /b 1
    )
    echo [SUCCESS] Backend dependencies verified.
) else (
    echo [WARNING] No requirements.txt found in root or backend directory.
)

:: ------------------------------------------------------------------------------
:: 6. Environment configuration (.env)
:: ------------------------------------------------------------------------------
if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] No .env found. Creating .env from .env.example...
        copy ".env.example" ".env" >nul
        echo [SUCCESS] Created .env configuration file.
    ) else (
        echo [WARNING] No .env or .env.example file found.
    )
) else (
    echo [INFO] Existing .env configuration file detected.
)

:: ------------------------------------------------------------------------------
:: 7. Frontend dependencies (npm install)
:: ------------------------------------------------------------------------------
if exist "frontend\package.json" (
    if not exist "frontend\node_modules" (
        echo [INFO] Installing frontend dependencies [npm install]...
        pushd frontend
        call npm install
        if errorlevel 1 (
            popd
            echo.
            echo ============================================================
            echo [ERROR] Failed to install frontend dependencies.
            echo ============================================================
            echo.
            pause
            exit /b 1
        )
        popd
        echo [SUCCESS] Frontend dependencies installed.
    ) else (
        echo [INFO] Frontend dependencies already installed [node_modules present].
    )
)

:: ------------------------------------------------------------------------------
:: 8. Avoid duplicate server processes on ports 8000 and 5173
:: ------------------------------------------------------------------------------
echo [INFO] Checking for existing processes on ports 8000 and 5173...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ports = @(8000, 5173);" ^
  "foreach ($p in $ports) {" ^
  "  $conns = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue;" ^
  "  if ($conns) { foreach ($c in $conns) { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } }" ^
  "}" >nul 2>&1

:: ------------------------------------------------------------------------------
:: 9. Start Backend and Frontend in separate windows with visible logs
:: ------------------------------------------------------------------------------
echo [INFO] Starting FastAPI backend server in separate window...
start "CampusMind AI - Backend Server" cmd /k "title CampusMind AI - Backend Server && cd /d "%PROJECT_ROOT%" && call venv\Scripts\activate.bat && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"

if exist "frontend\package.json" (
    echo [INFO] Starting Vite frontend server in separate window...
    start "CampusMind AI - Frontend Server" cmd /k "title CampusMind AI - Frontend Server && cd /d "%PROJECT_ROOT%frontend" && npm run dev -- --host 127.0.0.1 --port 5173"
)

:: ------------------------------------------------------------------------------
:: 10. Wait for servers to initialize and open default browser automatically
:: ------------------------------------------------------------------------------
echo [INFO] Waiting for servers to initialize and opening application in browser...

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "for ($i=0; $i -lt 30; $i++) {" ^
  "  try {" ^
  "    $r = Invoke-WebRequest -Uri 'http://127.0.0.1:5173' -UseBasicParsing -TimeoutSec 1;" ^
  "    if ($r.StatusCode -eq 200) { break }" ^
  "  } catch { Start-Sleep -Milliseconds 500 }" ^
  "};" ^
  "Start-Process 'http://localhost:5173'" >nul 2>&1

:: ------------------------------------------------------------------------------
:: 11. Dashboard / Graceful shutdown control
:: ------------------------------------------------------------------------------
cls
echo ============================================================
echo           CampusMind AI is now running live!
echo ============================================================
echo.
echo   * Web Application:     http://localhost:5173
echo   * Backend API:         http://localhost:8000
echo   * Interactive Docs:    http://localhost:8000/docs
echo.
echo Backend and Frontend are running in separate terminal windows
echo with live streaming logs and full request inspection.
echo.
echo ============================================================
echo [COMMAND] Press any key in this window to stop both servers
echo           and close all CampusMind AI processes cleanly.
echo ============================================================
echo.
pause >nul

echo.
echo [INFO] Shutting down all CampusMind AI server processes...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ports = @(8000, 5173);" ^
  "foreach ($p in $ports) {" ^
  "  $conns = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue;" ^
  "  if ($conns) { foreach ($c in $conns) { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue } }" ^
  "}" >nul 2>&1

echo [SUCCESS] All CampusMind AI services stopped cleanly.
timeout /t 2 >nul 2>&1
exit /b 0
