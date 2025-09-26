#!/bin/bash

# PostgreSQL Connection Troubleshooting Script
# Helps diagnose PostgreSQL connection issues

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}🔧 PostgreSQL Connection Troubleshooting${NC}"
    echo -e "${BLUE}================================================${NC}"
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to test network connectivity
test_network_connectivity() {
    local host=$1
    local port=$2
    
    if command_exists nc; then
        nc -z "$host" "$port" 2>/dev/null
    elif command_exists telnet; then
        timeout 5 telnet "$host" "$port" 2>/dev/null | grep -q "Connected"
    else
        timeout 5 bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null
    fi
}

# Function to check PostgreSQL service status
check_postgresql_service() {
    print_status "Checking PostgreSQL service status..."
    
    if command_exists systemctl; then
        if systemctl is-active --quiet postgresql; then
            print_success "PostgreSQL service is running"
            systemctl status postgresql --no-pager -l
        else
            print_error "PostgreSQL service is not running"
            print_status "Try: sudo systemctl start postgresql"
        fi
    elif command_exists brew; then
        if brew services list | grep postgresql | grep started >/dev/null; then
            print_success "PostgreSQL service is running (Homebrew)"
        else
            print_error "PostgreSQL service is not running (Homebrew)"
            print_status "Try: brew services start postgresql"
        fi
    else
        print_warning "Cannot check service status (systemctl/brew not available)"
    fi
}

# Function to check PostgreSQL processes
check_postgresql_processes() {
    print_status "Checking PostgreSQL processes..."
    
    if pgrep -f postgres >/dev/null; then
        print_success "PostgreSQL processes are running"
        ps aux | grep postgres | grep -v grep
    else
        print_error "No PostgreSQL processes found"
    fi
}

# Function to check PostgreSQL ports
check_postgresql_ports() {
    print_status "Checking PostgreSQL ports..."
    
    local ports=(5432 5433 5434)
    local found=false
    
    for port in "${ports[@]}"; do
        if netstat -tlnp 2>/dev/null | grep ":$port " >/dev/null; then
            print_success "PostgreSQL listening on port $port"
            netstat -tlnp | grep ":$port "
            found=true
        fi
    done
    
    if [ "$found" = false ]; then
        print_error "PostgreSQL not listening on common ports (5432, 5433, 5434)"
        print_status "Try: sudo netstat -tlnp | grep postgres"
    fi
}

# Function to test PostgreSQL connection
test_postgresql_connection() {
    local host=${1:-localhost}
    local port=${2:-5432}
    local database=${3:-postgres}
    local username=${4:-postgres}
    
    print_status "Testing PostgreSQL connection to $host:$port..."
    
    # Check if psql is available
    if ! command_exists psql; then
        print_error "psql command not found"
        print_status "Install PostgreSQL client tools:"
        echo "  Ubuntu/Debian: sudo apt-get install postgresql-client"
        echo "  CentOS/RHEL: sudo yum install postgresql"
        echo "  macOS: brew install postgresql"
        return 1
    fi
    
    # Test network connectivity
    if ! test_network_connectivity "$host" "$port"; then
        print_error "Cannot connect to $host:$port"
        return 1
    fi
    
    print_success "Network connectivity to $host:$port is working"
    
    # Test PostgreSQL connection
    print_status "Testing PostgreSQL authentication..."
    if psql -h "$host" -p "$port" -U "$username" -d "$database" -c "SELECT version();" >/dev/null 2>&1; then
        print_success "PostgreSQL connection successful!"
        psql -h "$host" -p "$port" -U "$username" -d "$database" -c "SELECT version();"
        return 0
    else
        print_error "PostgreSQL authentication failed"
        print_status "Common issues:"
        echo "  - Wrong username/password"
        echo "  - Database doesn't exist"
        echo "  - User doesn't have access"
        echo "  - Authentication method in pg_hba.conf"
        return 1
    fi
}

# Function to check PostgreSQL configuration
check_postgresql_config() {
    print_status "Checking PostgreSQL configuration..."
    
    # Find PostgreSQL data directory
    local pg_data_dir=""
    if [ -d "/var/lib/postgresql" ]; then
        pg_data_dir="/var/lib/postgresql"
    elif [ -d "/usr/local/var/postgres" ]; then
        pg_data_dir="/usr/local/var/postgres"
    elif [ -d "/opt/homebrew/var/postgres" ]; then
        pg_data_dir="/opt/homebrew/var/postgres"
    fi
    
    if [ -n "$pg_data_dir" ]; then
        print_success "PostgreSQL data directory: $pg_data_dir"
        
        # Check postgresql.conf
        if [ -f "$pg_data_dir/postgresql.conf" ]; then
            print_status "PostgreSQL configuration file found"
            echo "  listen_addresses: $(grep '^listen_addresses' "$pg_data_dir/postgresql.conf" 2>/dev/null || echo 'not set')"
            echo "  port: $(grep '^port' "$pg_data_dir/postgresql.conf" 2>/dev/null || echo 'not set')"
        fi
        
        # Check pg_hba.conf
        if [ -f "$pg_data_dir/pg_hba.conf" ]; then
            print_status "PostgreSQL authentication configuration:"
            grep -v '^#' "$pg_data_dir/pg_hba.conf" | grep -v '^$' | head -5
        fi
    else
        print_warning "PostgreSQL data directory not found"
    fi
}

# Function to provide troubleshooting suggestions
provide_troubleshooting_suggestions() {
    print_status "Troubleshooting suggestions:"
    echo ""
    echo "1. Start PostgreSQL service:"
    echo "   sudo systemctl start postgresql"
    echo "   # or on macOS: brew services start postgresql"
    echo ""
    echo "2. Check PostgreSQL status:"
    echo "   sudo systemctl status postgresql"
    echo ""
    echo "3. Check PostgreSQL logs:"
    echo "   sudo journalctl -u postgresql -f"
    echo "   # or check log files in PostgreSQL data directory"
    echo ""
    echo "4. Test connection as postgres user:"
    echo "   sudo -u postgres psql"
    echo ""
    echo "5. Create database and user:"
    echo "   sudo -u postgres psql -c \"CREATE DATABASE servicenow_docs;\""
    echo "   sudo -u postgres psql -c \"CREATE USER servicenow_user WITH PASSWORD 'YOUR_SECURE_PASSWORD';\""
    echo "   sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE servicenow_docs TO servicenow_user;\""
    echo ""
    echo "6. Check firewall settings:"
    echo "   sudo ufw status"
    echo "   sudo firewall-cmd --list-all"
    echo ""
    echo "7. Check PostgreSQL configuration:"
    echo "   sudo find /etc -name 'postgresql.conf' 2>/dev/null"
    echo "   sudo find /etc -name 'pg_hba.conf' 2>/dev/null"
}

# Main function
main() {
    print_header
    
    # Get connection details
    read -p "PostgreSQL Host [localhost]: " HOST
    HOST=${HOST:-localhost}
    
    read -p "PostgreSQL Port [5432]: " PORT
    PORT=${PORT:-5432}
    
    read -p "Database Name [postgres]: " DATABASE
    DATABASE=${DATABASE:-postgres}
    
    read -p "Username [postgres]: " USERNAME
    USERNAME=${USERNAME:-postgres}
    
    echo ""
    
    # Run diagnostics
    check_postgresql_service
    echo ""
    
    check_postgresql_processes
    echo ""
    
    check_postgresql_ports
    echo ""
    
    check_postgresql_config
    echo ""
    
    test_postgresql_connection "$HOST" "$PORT" "$DATABASE" "$USERNAME"
    echo ""
    
    provide_troubleshooting_suggestions
}

# Run main function
main "$@"
