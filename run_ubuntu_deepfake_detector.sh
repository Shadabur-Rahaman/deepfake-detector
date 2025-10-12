#!/bin/bash

# Ubuntu Deepfake Detection System Launcher
# =========================================
# 
# This script provides comprehensive commands for running the deepfake detection
# system on Ubuntu with full logging, monitoring, and management capabilities.
#
# Author: Senior ML Engineer
# Date: 2024

set -e  # Exit on any error

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
LOG_DIR="/var/log/deepfake-detector"
PYTHON_ENV="$PROJECT_DIR/venv"
PORT=8000
HOST="0.0.0.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

# Check if running as root for log directory creation
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        log_info "Running as root - full system access available"
    else
        log_warning "Not running as root - some features may be limited"
        log_info "Consider running with sudo for full system monitoring"
    fi
}

# Create log directory with proper permissions
setup_log_directory() {
    log_info "Setting up log directory: $LOG_DIR"
    
    if [[ $EUID -eq 0 ]]; then
        mkdir -p "$LOG_DIR"
        chown -R $SUDO_USER:$SUDO_USER "$LOG_DIR" 2>/dev/null || true
        chmod 755 "$LOG_DIR"
        log_success "Log directory created with proper permissions"
    else
        mkdir -p "$LOG_DIR" 2>/dev/null || {
            log_warning "Cannot create system log directory, using local logs"
            LOG_DIR="$PROJECT_DIR/logs"
            mkdir -p "$LOG_DIR"
        }
        log_success "Log directory setup completed"
    fi
}

# Check system requirements
check_system_requirements() {
    log_header "Checking System Requirements"
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log_success "Python 3 found: $PYTHON_VERSION"
    else
        log_error "Python 3 not found. Please install Python 3.8 or higher."
        exit 1
    fi
    
    # Check CUDA availability
    if command -v nvidia-smi &> /dev/null; then
        CUDA_VERSION=$(nvidia-smi | grep "CUDA Version" | awk '{print $9}')
        log_success "CUDA found: $CUDA_VERSION"
        GPU_AVAILABLE=true
    else
        log_warning "CUDA not found. System will run on CPU only."
        GPU_AVAILABLE=false
    fi
    
    # Check available memory
    TOTAL_MEMORY=$(free -h | awk '/^Mem:/ {print $2}')
    AVAILABLE_MEMORY=$(free -h | awk '/^Mem:/ {print $7}')
    log_info "Total Memory: $TOTAL_MEMORY, Available: $AVAILABLE_MEMORY"
    
    # Check disk space
    DISK_USAGE=$(df -h "$PROJECT_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$DISK_USAGE" -gt 90 ]; then
        log_warning "Disk usage is high: ${DISK_USAGE}%"
    else
        log_success "Disk usage is acceptable: ${DISK_USAGE}%"
    fi
    
    # Check network connectivity
    if ping -c 1 google.com &> /dev/null; then
        log_success "Network connectivity confirmed"
    else
        log_warning "Network connectivity issues detected"
    fi
}

# Setup Python virtual environment
setup_python_environment() {
    log_header "Setting up Python Environment"
    
    if [ ! -d "$PYTHON_ENV" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv "$PYTHON_ENV"
        log_success "Virtual environment created"
    else
        log_info "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source "$PYTHON_ENV/bin/activate"
    log_success "Virtual environment activated"
    
    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip
    
    # Install requirements
    if [ -f "$BACKEND_DIR/requirements.txt" ]; then
        log_info "Installing Python requirements..."
        pip install -r "$BACKEND_DIR/requirements.txt"
        log_success "Requirements installed"
    else
        log_warning "requirements.txt not found"
    fi
    
    # Install optional requirements if available
    if [ -f "$BACKEND_DIR/requirements_optional.txt" ]; then
        log_info "Installing optional requirements..."
        pip install -r "$BACKEND_DIR/requirements_optional.txt"
        log_success "Optional requirements installed"
    fi
    
    # Install CUDA requirements if GPU is available
    if [ "$GPU_AVAILABLE" = true ] && [ -f "$BACKEND_DIR/requirements_cuda_fixed.txt" ]; then
        log_info "Installing CUDA requirements..."
        pip install -r "$BACKEND_DIR/requirements_cuda_fixed.txt"
        log_success "CUDA requirements installed"
    fi
}

# Start the deepfake detection system
start_system() {
    log_header "Starting Deepfake Detection System"
    
    # Change to backend directory
    cd "$BACKEND_DIR"
    
    # Activate virtual environment
    source "$PYTHON_ENV/bin/activate"
    
    # Set environment variables
    export LOG_DIR="$LOG_DIR"
    export PYTHONPATH="$BACKEND_DIR:$PYTHONPATH"
    export CUDA_VISIBLE_DEVICES="0"  # Use first GPU if available
    
    # Start the system
    log_info "Starting server on $HOST:$PORT..."
    log_info "Logs will be written to: $LOG_DIR"
    log_info "Press Ctrl+C to stop the server"
    
    # Run with proper error handling
    python -m uvicorn app.main:app --host "$HOST" --port "$PORT" --reload --log-level info
}

# Start system with monitoring
start_with_monitoring() {
    log_header "Starting System with Full Monitoring"
    
    # Start system monitoring in background
    start_system_monitoring &
    MONITOR_PID=$!
    
    # Start the main system
    start_system
    
    # Cleanup monitoring on exit
    kill $MONITOR_PID 2>/dev/null || true
}

# System monitoring function
start_system_monitoring() {
    log_info "Starting system monitoring..."
    
    while true; do
        # Log system metrics
        echo "$(date): CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%, Memory: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')" >> "$LOG_DIR/system_monitor.log"
        
        # Check if main process is still running
        if ! pgrep -f "uvicorn app.main:app" > /dev/null; then
            log_error "Main process stopped unexpectedly"
            break
        fi
        
        sleep 30
    done
}

# View logs
view_logs() {
    log_header "Viewing System Logs"
    
    if [ -f "$LOG_DIR/deepfake_detector.log" ]; then
        log_info "Main application logs:"
        tail -f "$LOG_DIR/deepfake_detector.log"
    else
        log_warning "No main log file found"
    fi
}

# View error logs
view_errors() {
    log_header "Viewing Error Logs"
    
    if [ -f "$LOG_DIR/errors.log" ]; then
        log_info "Error logs:"
        tail -f "$LOG_DIR/errors.log"
    else
        log_info "No error logs found"
    fi
}

# View performance logs
view_performance() {
    log_header "Viewing Performance Logs"
    
    if [ -f "$LOG_DIR/performance.log" ]; then
        log_info "Performance logs:"
        tail -f "$LOG_DIR/performance.log"
    else
        log_info "No performance logs found"
    fi
}

# System status
show_status() {
    log_header "System Status"
    
    # Check if system is running
    if pgrep -f "uvicorn app.main:app" > /dev/null; then
        log_success "Deepfake Detection System is running"
        
        # Show process info
        log_info "Process information:"
        ps aux | grep "uvicorn app.main:app" | grep -v grep
        
        # Show port usage
        log_info "Port usage:"
        netstat -tlnp | grep ":$PORT " || log_warning "Port $PORT not in use"
        
    else
        log_warning "Deepfake Detection System is not running"
    fi
    
    # Show log file sizes
    log_info "Log file sizes:"
    if [ -d "$LOG_DIR" ]; then
        ls -lh "$LOG_DIR"/*.log 2>/dev/null || log_info "No log files found"
    else
        log_warning "Log directory not found"
    fi
    
    # Show system resources
    log_info "System resources:"
    echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
    echo "Memory Usage: $(free | grep Mem | awk '{printf("%.1f%%", $3/$2 * 100.0)}')"
    echo "Disk Usage: $(df -h "$PROJECT_DIR" | awk 'NR==2 {print $5}')"
    
    if [ "$GPU_AVAILABLE" = true ]; then
        echo "GPU Usage:"
        nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits
    fi
}

# Stop the system
stop_system() {
    log_header "Stopping Deepfake Detection System"
    
    # Find and kill the main process
    MAIN_PID=$(pgrep -f "uvicorn app.main:app")
    if [ -n "$MAIN_PID" ]; then
        log_info "Stopping main process (PID: $MAIN_PID)..."
        kill -TERM "$MAIN_PID"
        
        # Wait for graceful shutdown
        sleep 5
        
        # Force kill if still running
        if pgrep -f "uvicorn app.main:app" > /dev/null; then
            log_warning "Force killing process..."
            pkill -f "uvicorn app.main:app"
        fi
        
        log_success "System stopped"
    else
        log_warning "No running system found"
    fi
    
    # Stop monitoring processes
    pkill -f "system_monitor" 2>/dev/null || true
}

# Clean up logs
cleanup_logs() {
    log_header "Cleaning Up Logs"
    
    if [ -d "$LOG_DIR" ]; then
        log_info "Cleaning up log files older than 30 days..."
        find "$LOG_DIR" -name "*.log.*" -mtime +30 -delete 2>/dev/null || true
        log_success "Log cleanup completed"
    else
        log_warning "Log directory not found"
    fi
}

# Test the system
test_system() {
    log_header "Testing Deepfake Detection System"
    
    # Check if system is running
    if ! pgrep -f "uvicorn app.main:app" > /dev/null; then
        log_error "System is not running. Please start it first."
        exit 1
    fi
    
    # Test health endpoint
    log_info "Testing health endpoint..."
    if curl -s "http://localhost:$PORT/health" > /dev/null; then
        log_success "Health endpoint is responding"
    else
        log_error "Health endpoint is not responding"
    fi
    
    # Test API endpoint
    log_info "Testing API endpoint..."
    if curl -s "http://localhost:$PORT/api/health" > /dev/null; then
        log_success "API endpoint is responding"
    else
        log_error "API endpoint is not responding"
    fi
    
    # Test model status
    log_info "Testing model status..."
    if curl -s "http://localhost:$PORT/api/models/status" > /dev/null; then
        log_success "Model status endpoint is responding"
    else
        log_warning "Model status endpoint is not responding"
    fi
}

# Show help
show_help() {
    log_header "Ubuntu Deepfake Detection System Commands"
    
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start              Start the deepfake detection system"
    echo "  start-monitor      Start system with full monitoring"
    echo "  stop               Stop the running system"
    echo "  restart            Restart the system"
    echo "  status             Show system status"
    echo "  test               Test system endpoints"
    echo "  logs               View main application logs"
    echo "  errors             View error logs"
    echo "  performance        View performance logs"
    echo "  cleanup            Clean up old log files"
    echo "  setup              Setup system (first time only)"
    echo "  help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 setup           # First time setup"
    echo "  $0 start           # Start the system"
    echo "  $0 start-monitor   # Start with monitoring"
    echo "  $0 logs            # View logs in real-time"
    echo "  $0 status          # Check system status"
    echo ""
    echo "Log Directory: $LOG_DIR"
    echo "Server URL: http://$HOST:$PORT"
    echo "API Documentation: http://$HOST:$PORT/docs"
}

# Main script logic
main() {
    case "${1:-help}" in
        "setup")
            check_permissions
            setup_log_directory
            check_system_requirements
            setup_python_environment
            log_success "Setup completed successfully!"
            log_info "Run '$0 start' to start the system"
            ;;
        "start")
            check_permissions
            setup_log_directory
            start_system
            ;;
        "start-monitor")
            check_permissions
            setup_log_directory
            start_with_monitoring
            ;;
        "stop")
            stop_system
            ;;
        "restart")
            stop_system
            sleep 2
            check_permissions
            setup_log_directory
            start_system
            ;;
        "status")
            show_status
            ;;
        "test")
            test_system
            ;;
        "logs")
            view_logs
            ;;
        "errors")
            view_errors
            ;;
        "performance")
            view_performance
            ;;
        "cleanup")
            cleanup_logs
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function with all arguments
main "$@"
