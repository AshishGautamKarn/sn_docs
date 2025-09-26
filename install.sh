#!/bin/bash

# ServiceNow Documentation App - Manual Installation Script
# For Linux servers without Docker

set -e

echo "🚀 ServiceNow Documentation App - Manual Installation"
echo "====================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root for system installation"
   exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VER=$VERSION_ID
else
    print_error "Cannot detect OS"
    exit 1
fi

print_status "Detected OS: $OS $VER"

# Install system dependencies
print_status "Installing system dependencies..."

if [[ "$OS" == *"Ubuntu"* ]] || [[ "$OS" == *"Debian"* ]]; then
    apt-get update
    apt-get install -y python3 python3-pip python3-venv postgresql postgresql-contrib curl git build-essential libpq-dev
elif [[ "$OS" == *"CentOS"* ]] || [[ "$OS" == *"Red Hat"* ]] || [[ "$OS" == *"Rocky"* ]]; then
    yum update -y
    yum install -y python3 python3-pip postgresql postgresql-server postgresql-devel curl git gcc gcc-c++ make
    postgresql-setup initdb
    systemctl enable postgresql
    systemctl start postgresql
else
    print_warning "Unsupported OS. Please install Python 3.9+, PostgreSQL, and pip manually"
fi

# Create application user
print_status "Creating application user..."
useradd -m -s /bin/bash servicenow || true
usermod -aG sudo servicenow || true

# Create application directory
print_status "Setting up application directory..."
mkdir -p /opt/servicenow-docs
chown servicenow:servicenow /opt/servicenow-docs

# Copy application files
print_status "Copying application files..."
cp -r . /opt/servicenow-docs/
chown -R servicenow:servicenow /opt/servicenow-docs

# Switch to application user for Python setup
print_status "Setting up Python virtual environment..."
sudo -u servicenow bash << 'EOF'
cd /opt/servicenow-docs
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
EOF

# Setup PostgreSQL
print_status "Setting up PostgreSQL database..."
sudo -u postgres psql << 'EOF'
CREATE DATABASE servicenow_docs;
CREATE USER servicenow_user WITH PASSWORD '${DB_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE servicenow_docs TO servicenow_user;
\q
EOF

# Create environment file
print_status "Creating environment configuration..."
cat > /opt/servicenow-docs/.env << 'EOF'
DB_HOST=localhost
DB_PORT=5432
DB_NAME=servicenow_docs
DB_USER=servicenow_user
DB_PASSWORD=${DB_PASSWORD}
SCRAPER_TIMEOUT=60
SCRAPER_USE_SELENIUM=false
EOF

chown servicenow:servicenow /opt/servicenow-docs/.env

# Create systemd service
print_status "Creating systemd service..."
cp servicenow-app.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable servicenow-app

# Create logs and data directories
print_status "Creating application directories..."
mkdir -p /opt/servicenow-docs/logs /opt/servicenow-docs/data
chown -R servicenow:servicenow /opt/servicenow-docs/logs /opt/servicenow-docs/data

# Start services
print_status "Starting services..."
systemctl start postgresql
systemctl start servicenow-app

# Wait for service to start
sleep 10

# Check service status
if systemctl is-active --quiet servicenow-app; then
    print_success "🎉 Installation Complete!"
    echo ""
    echo "📱 Application URL: http://localhost:8506"
    echo "🗄️  Database: PostgreSQL on localhost:5432"
    echo "📊 Database Name: servicenow_docs"
    echo ""
    echo "📝 Useful Commands:"
    echo "  Check status: systemctl status servicenow-app"
    echo "  View logs: journalctl -u servicenow-app -f"
    echo "  Restart: systemctl restart servicenow-app"
    echo "  Stop: systemctl stop servicenow-app"
    echo ""
    echo "🔧 Configuration:"
    echo "  Edit config: nano /opt/servicenow-docs/.env"
    echo "  App directory: /opt/servicenow-docs"
    echo ""
else
    print_error "Service failed to start. Check logs with: journalctl -u servicenow-app -f"
    exit 1
fi
