#!/usr/bin/env bash

# ==============================================================================
# CampusMind AI - One-Click Application Launcher (Linux / macOS)
# Automatically checks environment, manages virtualenv, installs dependencies,
# starts backend and frontend servers, and opens the default web browser.
# ==============================================================================

# Ensure script runs from the repository root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ANSI Color Codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

pause_on_error() {
    echo ""
    read -p "Press [Enter] to exit..."
    exit 1
}

echo -e "${BOLD}${CYAN}============================================================${NC}"
echo -e "${BOLD}${CYAN}    CampusMind AI - Intelligent College Student Assistant   ${NC}"
echo -e "${BOLD}${CYAN}============================================================${NC}"
echo ""

# ------------------------------------------------------------------------------
# 1. System prerequisites check (Python 3, pip, Node.js, npm)
# ------------------------------------------------------------------------------
info "Checking system requirements..."

PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null && python --version 2>&1 | grep -q "Python 3"; then
    PYTHON_CMD="python"
else
    error "Python 3 is required but was not found in your PATH."
    error "Please install Python 3.10+ (e.g. 'sudo apt install python3 python3-pip python3-venv')."
    pause_on_error
fi
info "Found Python: $($PYTHON_CMD --version)"

if ! $PYTHON_CMD -m pip --version &>/dev/null; then
    error "pip is not installed for $PYTHON_CMD."
    error "Please install pip (e.g. 'sudo apt install python3-pip')."
    pause_on_error
fi

if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    if ! command -v node &>/dev/null; then
        error "Node.js is not installed but is required for the frontend."
        error "Please install Node.js v18+ (https://nodejs.org)."
        pause_on_error
    fi
    info "Found Node.js: $(node --version)"

    if ! command -v npm &>/dev/null; then
        error "npm is not installed but is required for the frontend."
        error "Please install npm."
        pause_on_error
    fi
    info "Found npm: $(npm --version)"
fi

success "System requirements verified."

# ------------------------------------------------------------------------------
# 2. Virtual environment management
# ------------------------------------------------------------------------------
if [ ! -d "venv" ]; then
    info "Creating Python virtual environment in ./venv..."
    $PYTHON_CMD -m venv venv || {
        error "Failed to create virtual environment."
        error "Try installing python3-venv: 'sudo apt install python3-venv'"
        pause_on_error
    }
    success "Virtual environment created."
else
    info "Virtual environment already exists in ./venv."
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    error "Could not find virtual environment activation script in ./venv."
    pause_on_error
fi
info "Virtual environment activated."

info "Ensuring pip is up to date..."
python -m pip install --upgrade pip --quiet || warn "pip upgrade check skipped."

# ------------------------------------------------------------------------------
# 3. Backend dependencies
# ------------------------------------------------------------------------------
REQ_FILE=""
if [ -f "requirements.txt" ]; then
    REQ_FILE="requirements.txt"
elif [ -f "backend/requirements.txt" ]; then
    REQ_FILE="backend/requirements.txt"
else
    error "Could not find requirements.txt in root or backend directory."
    pause_on_error
fi

info "Verifying backend dependencies from $REQ_FILE..."
pip install -r "$REQ_FILE" || {
    error "Failed to install backend dependencies from $REQ_FILE."
    pause_on_error
}
success "Backend dependencies verified."

# ------------------------------------------------------------------------------
# 4. Environment configuration (.env)
# ------------------------------------------------------------------------------
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        info "No .env found. Creating .env from .env.example..."
        cp ".env.example" ".env"
        success "Created .env configuration file."
    else
        warn "No .env or .env.example found. Standard defaults will be used."
    fi
else
    info "Existing .env configuration file detected."
fi

# ------------------------------------------------------------------------------
# 5. Frontend dependencies
# ------------------------------------------------------------------------------
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    if [ ! -d "frontend/node_modules" ]; then
        info "Installing frontend dependencies (npm install)..."
        (cd frontend && npm install) || {
            error "Failed to install frontend dependencies."
            pause_on_error
        }
        success "Frontend dependencies installed."
    else
        info "Frontend dependencies already installed (node_modules present)."
    fi

    if [ ! -d "frontend/dist" ]; then
        info "Building initial production assets..."
        (cd frontend && npm run build) || warn "Frontend build skipped; development server will be used."
    fi
fi

# ------------------------------------------------------------------------------
# 6. Process management & duplicate prevention
# ------------------------------------------------------------------------------
free_port() {
    local port=$1
    local name=$2
    python -c "
import socket, sys
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.bind(('0.0.0.0', $port))
    s.close()
except OSError:
    sys.exit(1)
sys.exit(0)
" 2>/dev/null
    if [ $? -ne 0 ]; then
        warn "Port $port ($name) is currently in use."
        if command -v lsof &>/dev/null; then
            local pids=$(lsof -ti :"$port" 2>/dev/null)
            if [ -n "$pids" ]; then
                info "Stopping existing process on port $port (PID: $pids)..."
                kill -9 $pids 2>/dev/null || true
                sleep 0.5
            fi
        elif command -v fuser &>/dev/null; then
            fuser -k "${port}/tcp" &>/dev/null || true
            sleep 0.5
        fi
    fi
}

info "Checking for port conflicts on 8000 and 5173..."
free_port 8000 "Backend"
free_port 5173 "Frontend"

# ------------------------------------------------------------------------------
# 7. Start servers and register cleanup trap
# ------------------------------------------------------------------------------
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    trap - SIGINT SIGTERM EXIT
    echo ""
    info "Shutting down CampusMind AI services..."

    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        info "Stopping FastAPI backend (PID: $BACKEND_PID)..."
        kill "$BACKEND_PID" 2>/dev/null || true
    fi

    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        info "Stopping Vite frontend (PID: $FRONTEND_PID)..."
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi

    sleep 0.5
    success "All CampusMind AI services stopped cleanly."
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

info "Starting CampusMind AI servers..."

# Start FastAPI backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
sleep 1.5

# Start Vite frontend
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    (cd frontend && npm run dev -- --host 0.0.0.0 --port 5173) &
    FRONTEND_PID=$!
    sleep 1.5
fi

# ------------------------------------------------------------------------------
# 8. Automatically open default web browser
# ------------------------------------------------------------------------------
open_browser() {
    local target_url="http://localhost:5173"
    # Wait until Vite or FastAPI is responding
    for i in {1..30}; do
        if python -c "import urllib.request, sys; sys.exit(0 if urllib.request.urlopen('$target_url', timeout=1).getcode() == 200 else 1)" 2>/dev/null; then
            break
        fi
        sleep 0.5
    done

    info "Opening CampusMind AI in your default browser ($target_url)..."
    if command -v xdg-open &>/dev/null; then
        xdg-open "$target_url" &>/dev/null &
    elif command -v open &>/dev/null; then
        open "$target_url" &>/dev/null &
    else
        python -m webbrowser "$target_url" &>/dev/null &
    fi
}

open_browser &

# ------------------------------------------------------------------------------
# 9. Live status dashboard
# ------------------------------------------------------------------------------
echo ""
echo -e "${BOLD}${GREEN}============================================================${NC}"
echo -e "${BOLD}${GREEN}           CampusMind AI is now running live!               ${NC}"
echo -e "${BOLD}${GREEN}============================================================${NC}"
echo ""
echo -e "  ${BOLD}🌐 Web Application:${NC}   ${CYAN}http://localhost:5173${NC}"
echo -e "  ${BOLD}⚡ Backend API:${NC}       ${CYAN}http://localhost:8000${NC}"
echo -e "  ${BOLD}📖 Interactive Docs:${NC}  ${CYAN}http://localhost:8000/docs${NC}"
echo ""
info "Press Ctrl+C at any time in this terminal to stop all services."
echo ""

# Wait on server background processes
if [ -n "$FRONTEND_PID" ]; then
    wait $BACKEND_PID $FRONTEND_PID
else
    wait $BACKEND_PID
fi
