#!/usr/bin/env bash

# ==============================================================================
# CampusMind AI - All-in-One Setup & Startup Script
# Automatically verifies environment, manages virtualenv, installs dependencies,
# and starts both the FastAPI backend and Vite React frontend concurrently.
# ==============================================================================

# Ensure script runs from the repository root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# ANSI Color Codes for user-friendly terminal output
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

echo -e "${BOLD}${CYAN}====================================================${NC}"
echo -e "${BOLD}${CYAN}   CampusMind AI – Assistant & Algorithm Laboratory ${NC}"
echo -e "${BOLD}${CYAN}====================================================${NC}"
echo ""

# ------------------------------------------------------------------------------
# 1. ENVIRONMENT CHECKING
# ------------------------------------------------------------------------------
info "Checking system requirements..."

# Detect Python 3
PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null && python --version 2>&1 | grep -q "Python 3"; then
    PYTHON_CMD="python"
else
    error "Python 3 is required but was not found in your PATH."
    error "Please install Python 3.10+ (e.g. 'sudo apt install python3 python3-pip python3-venv')."
    exit 1
fi
info "Found Python: $($PYTHON_CMD --version)"

# Detect pip
if ! $PYTHON_CMD -m pip --version &>/dev/null; then
    error "pip is not installed for $PYTHON_CMD."
    error "Please install pip (e.g. 'sudo apt install python3-pip')."
    exit 1
fi

# Detect Node.js and npm if frontend directory exists
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    if ! command -v node &>/dev/null; then
        error "Node.js is not installed but is required for the frontend."
        error "Please install Node.js v18+ (https://nodejs.org)."
        exit 1
    fi
    info "Found Node.js: $(node --version)"

    if ! command -v npm &>/dev/null; then
        error "npm is not installed but is required for the frontend."
        error "Please install npm."
        exit 1
    fi
    info "Found npm: $(npm --version)"
fi

success "System requirements verified."

# ------------------------------------------------------------------------------
# 2. PYTHON VIRTUAL ENVIRONMENT
# ------------------------------------------------------------------------------
if [ ! -d "venv" ]; then
    info "Creating Python virtual environment in ./venv..."
    $PYTHON_CMD -m venv venv || {
        error "Failed to create virtual environment."
        error "Try installing python3-venv: 'sudo apt install python3-venv'"
        exit 1
    }
    success "Virtual environment created."
else
    info "Virtual environment already exists in ./venv."
fi

# Activate virtual environment (handles both Linux/macOS and Git Bash/WSL)
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    error "Could not find virtual environment activation script in ./venv."
    exit 1
fi
info "Virtual environment activated."

# Upgrade pip
info "Ensuring pip is up to date..."
python -m pip install --upgrade pip --quiet || warn "pip upgrade check skipped."

# ------------------------------------------------------------------------------
# 3. BACKEND DEPENDENCIES
# ------------------------------------------------------------------------------
REQ_FILE=""
if [ -f "requirements.txt" ]; then
    REQ_FILE="requirements.txt"
elif [ -f "backend/requirements.txt" ]; then
    REQ_FILE="backend/requirements.txt"
else
    error "Could not find requirements.txt in root or backend directory."
    exit 1
fi

info "Installing backend dependencies from $REQ_FILE..."
pip install -r "$REQ_FILE" || {
    error "Failed to install backend dependencies."
    exit 1
}
success "Backend dependencies installed."

# ------------------------------------------------------------------------------
# 4. ENVIRONMENT VARIABLES (.env)
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
    info "Existing .env file detected."
fi

# Check for API keys
if [ -f ".env" ]; then
    HAS_GEMINI=false
    HAS_OPENAI=false
    
    if grep -q "^GEMINI_API_KEY=" ".env" && ! grep -E -q "^GEMINI_API_KEY=(your_gemini_api_key_here|)$" ".env"; then
        HAS_GEMINI=true
    fi
    if grep -q "^OPENAI_API_KEY=" ".env" && ! grep -E -q "^OPENAI_API_KEY=(your_openai_api_key_here|)$" ".env"; then
        HAS_OPENAI=true
    fi

    if [ "$HAS_GEMINI" = false ] && [ "$HAS_OPENAI" = false ]; then
        warn "No external LLM API key detected in .env."
        warn "CampusMind AI will run seamlessly in built-in Educational Tutor mode."
        warn "To connect live Gemini or OpenAI, add GEMINI_API_KEY or OPENAI_API_KEY to .env."
    else
        success "LLM API Key configuration detected."
    fi
fi

# ------------------------------------------------------------------------------
# 5. FRONTEND DEPENDENCIES
# ------------------------------------------------------------------------------
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    if [ ! -d "frontend/node_modules" ]; then
        info "Installing frontend dependencies (npm install)..."
        (cd frontend && npm install) || {
            error "Failed to install frontend dependencies."
            exit 1
        }
        success "Frontend dependencies installed."
    else
        info "Frontend dependencies already installed (node_modules present)."
    fi

    # Build production frontend dist if it doesn't exist
    if [ ! -d "frontend/dist" ]; then
        info "Building production frontend assets..."
        (cd frontend && npm run build) || warn "Frontend build skipped; development server will be used."
    fi
fi

# ------------------------------------------------------------------------------
# 6. PROCESS MANAGEMENT & GRACEFUL CLEANUP
# ------------------------------------------------------------------------------
BACKEND_PID=""
FRONTEND_PID=""

# Prevent duplicate server processes on target ports (8000 and 5173)
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
        warn "Port $port ($name) is already in use by another process."
        if command -v lsof &>/dev/null; then
            local pids=$(lsof -ti :"$port" 2>/dev/null)
            if [ -n "$pids" ]; then
                info "Terminating stale process on port $port (PID: $pids)..."
                kill -9 $pids 2>/dev/null || true
                sleep 0.5
            fi
        elif command -v fuser &>/dev/null; then
            fuser -k "${port}/tcp" &>/dev/null || true
            sleep 0.5
        fi
    fi
}

cleanup() {
    # Prevent recursive trap execution
    trap - SIGINT SIGTERM EXIT
    echo ""
    info "Shutting down CampusMind AI..."

    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        info "Stopping FastAPI backend (PID: $BACKEND_PID)..."
        kill "$BACKEND_PID" 2>/dev/null || true
    fi

    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        info "Stopping Vite frontend (PID: $FRONTEND_PID)..."
        kill "$FRONTEND_PID" 2>/dev/null || true
    fi

    # Wait for child processes to exit
    sleep 0.5
    success "All CampusMind AI services stopped cleanly."
    exit 0
}

# Trap termination signals
trap cleanup SIGINT SIGTERM EXIT

# ------------------------------------------------------------------------------
# 7. START APPLICATION SERVERS
# ------------------------------------------------------------------------------
info "Checking for port conflicts..."
free_port 8000 "Backend"
free_port 5173 "Frontend"

info "Starting CampusMind AI servers..."

# Start FastAPI backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait briefly for backend port to initialize
sleep 1.5

# Start Frontend development server if frontend directory exists
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    (cd frontend && npm run dev -- --host 0.0.0.0 --port 5173) &
    FRONTEND_PID=$!
    sleep 1.5
fi

echo ""
echo -e "${BOLD}${GREEN}====================================================${NC}"
echo -e "${BOLD}${GREEN}   CampusMind AI is running!                        ${NC}"
echo -e "${BOLD}${GREEN}====================================================${NC}"
echo ""
echo -e "  ${BOLD}🌐 Backend API & Full Web App:${NC} ${CYAN}http://localhost:8000${NC}"
if [ -n "$FRONTEND_PID" ]; then
    echo -e "  ${BOLD}⚡ Vite Frontend Dev Server:${NC}   ${CYAN}http://localhost:5173${NC}"
fi
echo -e "  ${BOLD}📖 Interactive API Docs:${NC}       ${CYAN}http://localhost:8000/docs${NC}"
echo ""
info "Press Ctrl+C at any time to gracefully stop all services."
echo ""

# Wait on server background processes
if [ -n "$FRONTEND_PID" ]; then
    wait $BACKEND_PID $FRONTEND_PID
else
    wait $BACKEND_PID
fi
