#!/bin/bash

################################################################################
# EduBot Complete Deployment & Launch Script
# Installs all dependencies and launches Backend + Frontend
# Usage: bash deploy.sh
################################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$SCRIPT_DIR"
BACKEND_PORT=8000
FRONTEND_PORT=3000
VENV_DIR="$APP_DIR/venv"
LOG_DIR="$APP_DIR/logs"
ADMIN_UI_DIR="$APP_DIR/admin-ui"

################################################################################
# Helper Functions
################################################################################

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[⚠]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

################################################################################
# System Check & Update
################################################################################

check_system() {
    print_header "SYSTEM CHECK"
    
    log_info "Checking system requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 not found"
        log_info "Installing Python3..."
        sudo apt update
        sudo apt install -y python3 python3-pip python3-venv
    else
        log_success "Python3 installed: $(python3 --version)"
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js not found"
        log_info "Installing Node.js..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
        sudo apt install -y nodejs
    else
        log_success "Node.js installed: $(node --version)"
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm not found"
        log_info "Installing npm..."
        sudo apt install -y npm
    else
        log_success "npm installed: $(npm --version)"
    fi
    
    # Check git
    if ! command -v git &> /dev/null; then
        log_warning "Git not found, installing..."
        sudo apt install -y git
    else
        log_success "Git installed: $(git --version)"
    fi
}

################################################################################
# Python Backend Setup
################################################################################

setup_backend() {
    print_header "BACKEND SETUP (FastAPI)"
    
    cd "$APP_DIR"
    
    log_info "Creating Python virtual environment..."
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        log_success "Virtual environment created"
    else
        log_success "Virtual environment already exists"
    fi
    
    # Activate venv
    source "$VENV_DIR/bin/activate"
    
    log_info "Upgrading pip..."
    pip install --upgrade pip setuptools wheel
    
    log_info "Installing Python dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt || {
            log_warning "Some packages failed, retrying with --no-cache-dir..."
            pip install --no-cache-dir -r requirements.txt
        }
        log_success "Backend dependencies installed"
    else
        log_error "requirements.txt not found!"
        return 1
    fi
    
    # Check for common issues
    log_info "Checking for MySQL connector..."
    if ! python3 -c "import mysql" 2>/dev/null; then
        log_warning "MySQL connector not found, installing mysql-connector-python..."
        pip install mysql-connector-python
    fi
    
    log_success "Backend setup complete"
}

################################################################################
# Frontend Setup
################################################################################

setup_frontend() {
    print_header "FRONTEND SETUP (Next.js Admin UI)"
    
    if [ ! -d "$ADMIN_UI_DIR" ]; then
        log_error "admin-ui directory not found!"
        return 1
    fi
    
    cd "$ADMIN_UI_DIR"
    
    log_info "Installing Node.js dependencies..."
    npm install || {
        log_warning "npm install failed, trying with --legacy-peer-deps..."
        npm install --legacy-peer-deps
    }
    log_success "Frontend dependencies installed"
    
    log_info "Building Next.js application..."
    npm run build || {
        log_warning "Build failed, trying with increased memory..."
        NODE_OPTIONS=--max_old_space_size=4096 npm run build
    }
    log_success "Frontend build complete"
}

################################################################################
# Environment Configuration
################################################################################

setup_environment() {
    print_header "ENVIRONMENT CONFIGURATION"
    
    cd "$APP_DIR"
    
    # Check backend .env
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            log_info "Creating .env from .env.example..."
            cp .env.example .env
            log_warning "Please update .env with your actual credentials"
            
            # Auto-fix common settings
            log_info "Auto-configuring .env..."
            if grep -q "^DEBUG=" .env; then
                sed -i 's/^DEBUG=.*/DEBUG=False/' .env
            fi
        else
            log_error ".env.example not found"
            return 1
        fi
    else
        log_success ".env already configured"
    fi
    
    # Check frontend .env
    if [ ! -f "$ADMIN_UI_DIR/.env.local" ]; then
        if [ -f "$ADMIN_UI_DIR/.env.example" ]; then
            log_info "Creating frontend .env.local..."
            cp "$ADMIN_UI_DIR/.env.example" "$ADMIN_UI_DIR/.env.local"
        fi
    fi
}

################################################################################
# Create Log Directory
################################################################################

setup_logging() {
    print_header "LOGGING SETUP"
    
    mkdir -p "$LOG_DIR"
    log_success "Log directory created: $LOG_DIR"
}

################################################################################
# Database Check
################################################################################

check_database() {
    print_header "DATABASE CHECK"
    
    log_info "Checking database connectivity..."
    
    # Extract database info from .env
    DB_URL=$(grep "^DATABASE_URL=" "$APP_DIR/.env" 2>/dev/null || echo "")
    
    if [ -z "$DB_URL" ]; then
        log_warning "DATABASE_URL not configured in .env"
        log_warning "Backend will attempt to connect when started"
        return 0
    fi
    
    # Try to connect (basic check)
    log_info "Database URL found, will test on startup"
}

################################################################################
# Launch Services
################################################################################

launch_backend() {
    print_header "LAUNCHING BACKEND"
    
    cd "$APP_DIR"
    source "$VENV_DIR/bin/activate"
    
    log_info "Starting FastAPI backend on port $BACKEND_PORT..."
    
    # Check if port is already in use
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        log_warning "Port $BACKEND_PORT already in use"
        log_info "Attempting to kill existing process..."
        lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Install gunicorn if not present
    if ! pip show gunicorn &>/dev/null; then
        log_info "Installing Gunicorn..."
        pip install gunicorn
    fi
    
    # Start backend in tmux session
    tmux new-session -d -s edubot-api -c "$APP_DIR" \
        "source $VENV_DIR/bin/activate && gunicorn -w 4 -b 0.0.0.0:$BACKEND_PORT --timeout 120 --access-logfile $LOG_DIR/api_access.log --error-logfile $LOG_DIR/api_error.log main:app"
    
    log_success "Backend started in tmux session (edubot-api)"
    log_info "Logs: $LOG_DIR/api_*.log"
    
    # Wait for backend to start
    sleep 3
    
    # Check if backend is running
    if curl -s http://localhost:$BACKEND_PORT/docs > /dev/null 2>&1; then
        log_success "Backend is responding"
    else
        log_warning "Backend may not be responding yet, continue..."
    fi
}

launch_frontend() {
    print_header "LAUNCHING FRONTEND"
    
    cd "$ADMIN_UI_DIR"
    
    log_info "Starting Next.js frontend on port $FRONTEND_PORT..."
    
    # Check if port is already in use
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        log_warning "Port $FRONTEND_PORT already in use"
        log_info "Attempting to kill existing process..."
        lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Start frontend in tmux session
    tmux new-session -d -s edubot-ui -c "$ADMIN_UI_DIR" \
        "npm start 2>&1 | tee $LOG_DIR/ui.log"
    
    log_success "Frontend started in tmux session (edubot-ui)"
    log_info "Logs: $LOG_DIR/ui.log"
    
    # Wait for frontend to start
    sleep 5
}

################################################################################
# Status Check
################################################################################

check_status() {
    print_header "SERVICE STATUS"
    
    # Check API
    log_info "Checking API (http://localhost:$BACKEND_PORT/docs)..."
    if curl -s http://localhost:$BACKEND_PORT/docs > /dev/null 2>&1; then
        log_success "✓ FastAPI Backend is running"
    else
        log_warning "⚠ FastAPI Backend may be starting..."
    fi
    
    # Check Frontend
    log_info "Checking UI (http://localhost:$FRONTEND_PORT)..."
    if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        log_success "✓ Next.js Frontend is running"
    else
        log_warning "⚠ Next.js Frontend may be starting..."
    fi
    
    # Check tmux sessions
    echo ""
    log_info "Tmux sessions:"
    tmux list-sessions 2>/dev/null | grep edubot || log_warning "No tmux sessions found"
}

################################################################################
# Cleanup on Exit
################################################################################

cleanup() {
    print_header "CLEANUP"
    
    log_info "Stopping services..."
    tmux kill-session -t edubot-api 2>/dev/null || true
    tmux kill-session -t edubot-ui 2>/dev/null || true
    log_success "Services stopped"
}

trap cleanup EXIT

################################################################################
# Main Execution
################################################################################

main() {
    clear
    
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════╗"
    echo "║   EduBot - Complete Deployment Script  ║"
    echo "║   Backend + Frontend Auto-Launch       ║"
    echo "╚════════════════════════════════════════╝"
    echo -e "${NC}\n"
    
    log_info "Starting deployment at $(date)"
    
    # Execute setup steps
    check_system
    setup_environment
    setup_logging
    setup_backend
    setup_frontend
    check_database
    
    # Launch services
    launch_backend
    launch_frontend
    
    # Final status
    sleep 3
    check_status
    
    print_header "DEPLOYMENT COMPLETE"
    
    log_success "EduBot is now running!"
    echo ""
    log_info "Access the application:"
    echo "  • Admin Dashboard: http://localhost:$FRONTEND_PORT"
    echo "  • API Docs: http://localhost:$BACKEND_PORT/docs"
    echo ""
    log_info "View logs:"
    echo "  • Backend: tail -f $LOG_DIR/api_error.log"
    echo "  • Frontend: tail -f $LOG_DIR/ui.log"
    echo ""
    log_info "Manage services (tmux):"
    echo "  • Backend: tmux attach-session -t edubot-api"
    echo "  • Frontend: tmux attach-session -t edubot-ui"
    echo "  • Kill Backend: tmux kill-session -t edubot-api"
    echo "  • Kill Frontend: tmux kill-session -t edubot-ui"
    echo ""
    log_warning "Press Ctrl+C to stop all services"
    
    # Keep script running
    while true; do
        sleep 60
    done
}

# Run main
main "$@"
