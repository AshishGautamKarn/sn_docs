#!/bin/bash

# ServiceNow Advanced Visual Documentation - SSL-Enhanced Automated Startup Script
# This script automatically sets up SSL, configures security, and starts the ServiceNow documentation app

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DEFAULT_PORT=8501
SSL_PORT=8501
SSL_DIR="ssl"
CERT_FILE="$SSL_DIR/cert.pem"
KEY_FILE="$SSL_DIR/key.pem"
ENV_FILE=".env"
ENV_EXAMPLE=".env.example"

# Function to print colored output
print_header() {
    echo -e "${PURPLE}================================================${NC}"
    echo -e "${PURPLE}🔒 ServiceNow Advanced Visual Documentation${NC}"
    echo -e "${PURPLE}🚀 SSL-Enhanced Secure Startup${NC}"
    echo -e "${PURPLE}================================================${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

print_security() {
    echo -e "${GREEN}[SECURITY]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        print_warning "Please run as regular user, sudo will be used when needed"
        exit 1
    fi
}

# Function to check system requirements
check_system_requirements() {
    print_step "Checking system requirements..."
    
    # Check Python version
    if command_exists python3; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check pip
    if command_exists pip3; then
        print_success "pip3 found"
    else
        print_error "pip3 is required but not installed"
        exit 1
    fi
    
    # Check OpenSSL
    if command_exists openssl; then
        OPENSSL_VERSION=$(openssl version 2>&1 | cut -d' ' -f2)
        print_success "OpenSSL $OPENSSL_VERSION found"
    else
        print_warning "OpenSSL not found, installing..."
        install_openssl
    fi
    
    # Check available memory
    if command_exists free; then
        MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
        if [ "$MEMORY_GB" -lt 4 ]; then
            print_warning "Less than 4GB RAM available. Performance may be affected."
        else
            print_success "Sufficient memory available ($MEMORY_GB GB)"
        fi
    fi
}

# Function to install OpenSSL
install_openssl() {
    print_step "Installing OpenSSL..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            brew install openssl
        else
            print_error "Homebrew not found. Please install OpenSSL manually."
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            sudo apt-get update && sudo apt-get install -y openssl
        elif command_exists yum; then
            sudo yum install -y openssl
        elif command_exists dnf; then
            sudo dnf install -y openssl
        else
            print_error "Package manager not found. Please install OpenSSL manually."
            exit 1
        fi
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    print_success "OpenSSL installed successfully"
}

# Function to setup virtual environment
setup_virtual_environment() {
    print_step "Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    print_success "Virtual environment setup complete"
}

# Function to install dependencies
install_dependencies() {
    print_step "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        print_status "Installing from requirements.txt..."
        pip install -r requirements.txt
        print_success "Dependencies installed successfully"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
    
    # Install additional security dependencies
    print_status "Installing security dependencies..."
    pip install cryptography==41.0.7
    print_success "Security dependencies installed"
}

# Function to setup environment configuration
setup_environment() {
    print_step "Setting up environment configuration..."
    
    if [ ! -f "$ENV_FILE" ]; then
        if [ -f "$ENV_EXAMPLE" ]; then
            print_status "Creating .env from template..."
            cp "$ENV_EXAMPLE" "$ENV_FILE"
            print_warning "Please edit .env file with your configuration"
            print_status "Opening .env file for editing..."
            
            # Try to open with common editors
            if command_exists nano; then
                nano "$ENV_FILE"
            elif command_exists vim; then
                vim "$ENV_FILE"
            elif command_exists code; then
                code "$ENV_FILE"
            else
                print_warning "Please manually edit .env file with your configuration"
            fi
        else
            print_error ".env.example not found"
            exit 1
        fi
    else
        print_success "Environment configuration already exists"
    fi
}

# Function to generate SSL certificates
generate_ssl_certificates() {
    print_step "Setting up SSL certificates..."
    
    # Create SSL directory
    if [ ! -d "$SSL_DIR" ]; then
        print_status "Creating SSL directory..."
        mkdir -p "$SSL_DIR"
    fi
    
    # Check if certificates already exist
    if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
        print_success "SSL certificates already exist"
        
        # Check certificate validity
        if openssl x509 -in "$CERT_FILE" -text -noout >/dev/null 2>&1; then
            print_success "SSL certificate is valid"
        else
            print_warning "SSL certificate is invalid, regenerating..."
            generate_new_ssl_certificate
        fi
    else
        print_status "Generating new SSL certificates..."
        generate_new_ssl_certificate
    fi
}

# Function to generate new SSL certificate
generate_new_ssl_certificate() {
    print_status "Generating self-signed SSL certificate..."
    
    # Generate certificate with proper subject and SAN
    openssl req -x509 -newkey rsa:4096 -nodes \
        -out "$CERT_FILE" \
        -keyout "$KEY_FILE" \
        -days 365 \
        -subj "/C=US/ST=State/L=City/O=ServiceNow Docs/OU=Development/CN=localhost" \
        -config <(
            echo "[req]"
            echo "distinguished_name = req"
            echo "[req]"
            echo "subjectAltName = @alt_names"
            echo "[alt_names]"
            echo "DNS.1 = localhost"
            echo "DNS.2 = 127.0.0.1"
            echo "IP.1 = 127.0.0.1"
            echo "IP.2 = ::1"
        )
    
    # Set proper permissions
    chmod 600 "$KEY_FILE"
    chmod 644 "$CERT_FILE"
    
    print_success "SSL certificate generated successfully"
    print_security "Certificate valid for 365 days"
    print_security "Subject: localhost"
}

# Function to setup database
setup_database() {
    print_step "Setting up database..."
    
    # Check if database configuration exists
    if grep -q "DB_HOST" "$ENV_FILE"; then
        print_status "Database configuration found"
        
        # Test database connection
        if python3 -c "
import os
from dotenv import load_dotenv
load_dotenv()
from database import DatabaseManager
try:
    db = DatabaseManager()
    db.test_connection()
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
" 2>/dev/null; then
            print_success "Database connection successful"
        else
            print_warning "Database connection failed, but continuing..."
        fi
    else
        print_warning "Database configuration not found in .env"
    fi
}

# Function to setup security configurations
setup_security() {
    print_step "Setting up security configurations..."
    
    # Check for encryption key
    if ! grep -q "ENCRYPTION_KEY" "$ENV_FILE"; then
        print_status "Generating encryption key..."
        ENCRYPTION_KEY=$(openssl rand -hex 32)
        echo "ENCRYPTION_KEY=$ENCRYPTION_KEY" >> "$ENV_FILE"
        print_security "Encryption key generated and added to .env"
    else
        print_success "Encryption key already configured"
    fi
    
    # Set secure file permissions
    print_status "Setting secure file permissions..."
    chmod 600 "$ENV_FILE"
    chmod 600 "$KEY_FILE"
    chmod 644 "$CERT_FILE"
    
    print_success "Security configurations complete"
}

# Function to check port availability
check_port_availability() {
    print_step "Checking port availability..."
    
    if command_exists netstat; then
        if netstat -tuln | grep -q ":$SSL_PORT "; then
            print_warning "Port $SSL_PORT is already in use"
            print_status "Trying alternative port..."
            SSL_PORT=$((SSL_PORT + 1))
            check_port_availability
        else
            print_success "Port $SSL_PORT is available"
        fi
    elif command_exists ss; then
        if ss -tuln | grep -q ":$SSL_PORT "; then
            print_warning "Port $SSL_PORT is already in use"
            print_status "Trying alternative port..."
            SSL_PORT=$((SSL_PORT + 1))
            check_port_availability
        else
            print_success "Port $SSL_PORT is available"
        fi
    else
        print_warning "Cannot check port availability, proceeding..."
    fi
}

# Function to start the application with SSL
start_application_ssl() {
    print_step "Starting application with SSL..."
    
    print_header
    print_success "🚀 Starting ServiceNow Advanced Visual Documentation"
    print_security "🔒 SSL/HTTPS encryption enabled"
    print_status "🌐 Access: https://localhost:$SSL_PORT"
    print_warning "⚠️  Note: Self-signed certificate - accept security warning in browser"
    print_status "📱 Press Ctrl+C to stop"
    echo ""
    
    # Start Streamlit with SSL
    streamlit run enhanced_app.py \
        --server.port "$SSL_PORT" \
        --server.address "0.0.0.0" \
        --server.sslCertFile "$CERT_FILE" \
        --server.sslKeyFile "$KEY_FILE" \
        --browser.gatherUsageStats false \
        --server.headless true
}

# Function to start the application without SSL (fallback)
start_application_no_ssl() {
    print_step "Starting application without SSL (fallback)..."
    
    print_header
    print_success "🚀 Starting ServiceNow Advanced Visual Documentation"
    print_warning "⚠️  Running without SSL - not recommended for production"
    print_status "🌐 Access: http://localhost:$SSL_PORT"
    print_status "📱 Press Ctrl+C to stop"
    echo ""
    
    # Start Streamlit without SSL
    streamlit run enhanced_app.py \
        --server.port "$SSL_PORT" \
        --server.address "0.0.0.0" \
        --browser.gatherUsageStats false \
        --server.headless true
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up..."
    print_success "Application stopped"
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --no-ssl          Start without SSL (not recommended)"
    echo "  --port PORT       Use specific port (default: 8501)"
    echo "  --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                Start with SSL on default port"
    echo "  $0 --port 8502    Start with SSL on port 8502"
    echo "  $0 --no-ssl       Start without SSL"
}

# Main function
main() {
    # Parse command line arguments
    SSL_ENABLED=true
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --no-ssl)
                SSL_ENABLED=false
                shift
                ;;
            --port)
                SSL_PORT="$2"
                shift 2
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Set trap for cleanup
    trap cleanup EXIT
    
    # Start the setup process
    print_header
    
    # Check if running as root
    check_root
    
    # Check system requirements
    check_system_requirements
    
    # Setup virtual environment
    setup_virtual_environment
    
    # Install dependencies
    install_dependencies
    
    # Setup environment
    setup_environment
    
    # Setup SSL certificates if enabled
    if [ "$SSL_ENABLED" = true ]; then
        generate_ssl_certificates
        setup_security
    fi
    
    # Setup database
    setup_database
    
    # Check port availability
    check_port_availability
    
    # Start the application
    if [ "$SSL_ENABLED" = true ]; then
        start_application_ssl
    else
        start_application_no_ssl
    fi
}

# Run main function
main "$@"

# Created By: Ashish Gautam; LinkedIn: https://www.linkedin.com/in/ashishgautamkarn/
