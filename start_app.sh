#!/bin/bash

# ServiceNow Advanced Visual Documentation - Enhanced Automated Startup Script
# This script automatically detects existing services, configures database, verifies permissions, and starts the app securely

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
    echo -e "${PURPLE}🚀 Enhanced Secure Startup with Service Detection${NC}"
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect running PostgreSQL services
detect_postgresql_services() {
    print_status "Detecting PostgreSQL services..."
    
    local detected_services=""
    
    # Check for PostgreSQL services on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # Check Homebrew services
        if command_exists brew; then
            local brew_services=$(brew services list | grep postgresql | grep started | awk '{print $1}' 2>/dev/null || true)
            if [ -n "$brew_services" ]; then
                while IFS= read -r service; do
                    if [ -n "$service" ]; then
                        # Get version from service name
                        local version=$(echo "$service" | grep -o '[0-9]\+' | head -1 || echo "Unknown")
                        detected_services="${detected_services}${service}|5432|${version}\n"
                    fi
                done <<< "$brew_services"
            fi
        fi
        
        # Check for PostgreSQL.app
        if [ -d "/Applications/PostgreSQL.app" ]; then
            detected_services="${detected_services}PostgreSQL.app|5432|App\n"
        fi
        
        # Check for system PostgreSQL
        if pgrep -f "postgres.*-D" >/dev/null 2>&1; then
            detected_services="${detected_services}System PostgreSQL|5432|System\n"
        fi
    fi
    
    # Check for PostgreSQL services on Linux
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Check systemd services
        if command_exists systemctl; then
            local systemd_services=$(systemctl list-units --type=service --state=running | grep postgresql | awk '{print $1}' 2>/dev/null || true)
            if [ -n "$systemd_services" ]; then
                while IFS= read -r service; do
                    if [ -n "$service" ]; then
                        # Get port from service configuration
                        local port=$(systemctl show "$service" --property=ExecStart 2>/dev/null | grep -o 'port=[0-9]\+' | cut -d= -f2 || echo "5432")
                        # Get version
                        local version=$(systemctl show "$service" --property=ExecStart 2>/dev/null | grep -o 'postgresql[0-9]\+' | grep -o '[0-9]\+' || echo "Unknown")
                        detected_services="${detected_services}${service}|${port}|${version}\n"
                    fi
                done <<< "$systemd_services"
            fi
        fi
        
        # Check for running PostgreSQL processes
        if pgrep -f "postgres.*-D" >/dev/null 2>&1; then
            detected_services="${detected_services}Running PostgreSQL Process|5432|Process\n"
        fi
    fi
    
    # Return results
    echo -e "$detected_services"
}

# Function to detect running MySQL services
detect_mysql_services() {
    print_status "Detecting MySQL services..."
    
    local detected_services=""
    
    # Check for MySQL services on macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # Check Homebrew services
        if command_exists brew; then
            local brew_services=$(brew services list | grep mysql | grep started | awk '{print $1}' 2>/dev/null || true)
            if [ -n "$brew_services" ]; then
                while IFS= read -r service; do
                    if [ -n "$service" ]; then
                        detected_services="${detected_services}${service}|3306|Homebrew\n"
                    fi
                done <<< "$brew_services"
            fi
        fi
        
        # Check for MySQL.app
        if [ -d "/Applications/MySQL.app" ]; then
            detected_services="${detected_services}MySQL.app|3306|App\n"
        fi
    fi
    
    # Check for MySQL services on Linux
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Check systemd services
        if command_exists systemctl; then
            local systemd_services=$(systemctl list-units --type=service --state=running | grep mysql | awk '{print $1}' 2>/dev/null || true)
            if [ -n "$systemd_services" ]; then
                while IFS= read -r service; do
                    if [ -n "$service" ]; then
                        detected_services="${detected_services}${service}|3306|System\n"
                    fi
                done <<< "$systemd_services"
            fi
        fi
    fi
    
    # Return results
    echo -e "$detected_services"
}

# Function to check system requirements
check_system_requirements() {
    print_step "Checking system requirements..."
    
    # Check Python
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    # Check pip
    if ! command_exists pip3; then
        print_error "pip3 is not installed. Please install pip3."
        exit 1
    fi
    
    # Check PostgreSQL client (don't install automatically)
    if ! command_exists psql; then
        print_warning "PostgreSQL client (psql) not found."
        print_status "You can install it with:"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            print_status "  brew install postgresql"
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            print_status "  sudo apt-get install postgresql-client"
        fi
        print_status "Or continue with SQLite for development."
    fi
    
    print_success "System requirements check completed"
}

# Function to configure database connection with service detection
configure_database() {
    print_step "Configuring database connection..."
    
    echo -e "${CYAN}📊 Database Configuration with Service Detection${NC}"
    echo -e "${CYAN}===============================================${NC}"
    echo ""
    
    # Detect existing services
    local postgres_services=()
    local postgres_ports=()
    local postgres_versions=()
    
    # Parse PostgreSQL services
    local postgres_output=$(detect_postgresql_services)
    if [ -n "$postgres_output" ]; then
        while IFS= read -r line; do
            if [ -n "$line" ]; then
                IFS='|' read -r service port version <<< "$line"
                postgres_services+=("$service")
                postgres_ports+=("$port")
                postgres_versions+=("$version")
            fi
        done <<< "$postgres_output"
    fi
    
    local mysql_services=()
    local mysql_ports=()
    local mysql_versions=()
    
    # Parse MySQL services
    local mysql_output=$(detect_mysql_services)
    if [ -n "$mysql_output" ]; then
        while IFS= read -r line; do
            if [ -n "$line" ]; then
                IFS='|' read -r service port version <<< "$line"
                mysql_services+=("$service")
                mysql_ports+=("$port")
                mysql_versions+=("$version")
            fi
        done <<< "$mysql_output"
    fi
    
    # Display detected services
    if [ ${#postgres_services[@]} -gt 0 ]; then
        echo "🔍 Detected PostgreSQL Services:"
        for i in "${!postgres_services[@]}"; do
            echo "   ${postgres_services[$i]} (Port: ${postgres_ports[$i]}, Version: ${postgres_versions[$i]})"
        done
        echo ""
    fi
    
    if [ ${#mysql_services[@]} -gt 0 ]; then
        echo "🔍 Detected MySQL Services:"
        for i in "${!mysql_services[@]}"; do
            echo "   ${mysql_services[$i]} (Port: ${mysql_ports[$i]}, Version: ${mysql_versions[$i]})"
        done
        echo ""
    fi
    
    # Database type selection
    echo "1. Select database type:"
    echo "   a) PostgreSQL (Recommended)"
    echo "   b) MySQL"
    echo "   c) SQLite (Development only)"
    echo ""
    read -p "Enter your choice (a/b/c): " DB_TYPE
    
    case $DB_TYPE in
        a|A)
            DB_TYPE="postgresql"
            ;;
        b|B)
            DB_TYPE="mysql"
            ;;
        c|C)
            DB_TYPE="sqlite"
            ;;
        *)
            print_error "Invalid choice. Defaulting to PostgreSQL."
            DB_TYPE="postgresql"
            ;;
    esac
    
    if [ "$DB_TYPE" = "sqlite" ]; then
        # SQLite configuration
        DB_HOST=""
        DB_PORT=""
        DB_NAME="servicenow_docs.db"
        DB_USER=""
        DB_PASSWORD=""
        DB_URL="sqlite:///servicenow_docs.db"
    else
        # PostgreSQL/MySQL configuration
        echo ""
        echo "2. Database connection details:"
        
        # Suggest detected services
        if [ "$DB_TYPE" = "postgresql" ] && [ ${#postgres_services[@]} -gt 0 ]; then
            echo "   Detected PostgreSQL services available:"
            for i in "${!postgres_services[@]}"; do
                echo "   $((i+1)). ${postgres_services[$i]} (Port: ${postgres_ports[$i]})"
            done
            echo ""
            read -p "   Use detected service (1-${#postgres_services[@]}) or enter custom host (default: localhost): " SERVICE_CHOICE
            
            if [[ "$SERVICE_CHOICE" =~ ^[0-9]+$ ]] && [ "$SERVICE_CHOICE" -ge 1 ] && [ "$SERVICE_CHOICE" -le ${#postgres_services[@]} ]; then
                DB_HOST="localhost"
                DB_PORT="${postgres_ports[$((SERVICE_CHOICE-1))]}"
                print_success "Using detected service: ${postgres_services[$((SERVICE_CHOICE-1))]} on port $DB_PORT"
            else
                read -p "   Database host (default: localhost): " DB_HOST
                DB_HOST=${DB_HOST:-localhost}
                read -p "   Database port (default: 5432): " DB_PORT
                DB_PORT=${DB_PORT:-5432}
            fi
        elif [ "$DB_TYPE" = "mysql" ] && [ ${#mysql_services[@]} -gt 0 ]; then
            echo "   Detected MySQL services available:"
            for i in "${!mysql_services[@]}"; do
                echo "   $((i+1)). ${mysql_services[$i]} (Port: ${mysql_ports[$i]})"
            done
            echo ""
            read -p "   Use detected service (1-${#mysql_services[@]}) or enter custom host (default: localhost): " SERVICE_CHOICE
            
            if [[ "$SERVICE_CHOICE" =~ ^[0-9]+$ ]] && [ "$SERVICE_CHOICE" -ge 1 ] && [ "$SERVICE_CHOICE" -le ${#mysql_services[@]} ]; then
                DB_HOST="localhost"
                DB_PORT="${mysql_ports[$((SERVICE_CHOICE-1))]}"
                print_success "Using detected service: ${mysql_services[$((SERVICE_CHOICE-1))]} on port $DB_PORT"
            else
                read -p "   Database host (default: localhost): " DB_HOST
                DB_HOST=${DB_HOST:-localhost}
                read -p "   Database port (default: 3306): " DB_PORT
                DB_PORT=${DB_PORT:-3306}
            fi
        else
            read -p "   Database host (default: localhost): " DB_HOST
            DB_HOST=${DB_HOST:-localhost}
            
            if [ "$DB_TYPE" = "postgresql" ]; then
                read -p "   Database port (default: 5432): " DB_PORT
                DB_PORT=${DB_PORT:-5432}
            else
                read -p "   Database port (default: 3306): " DB_PORT
                DB_PORT=${DB_PORT:-3306}
            fi
        fi
        
        read -p "   Database name: " DB_NAME
        read -p "   Database username: " DB_USER
        read -s -p "   Database password: " DB_PASSWORD
        echo ""
        
        # Construct database URL
        if [ "$DB_TYPE" = "postgresql" ]; then
            DB_URL="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
        else
            DB_URL="mysql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
        fi
    fi
    
    print_success "Database configuration completed"
}

# Function to verify database connection and permissions
verify_database_connection() {
    print_step "Verifying database connection and permissions..."
    
    if [ "$DB_TYPE" = "sqlite" ]; then
        print_success "SQLite database will be created automatically"
        return 0
    fi
    
    # Test connection
    print_status "Testing database connection..."
    
    if [ "$DB_TYPE" = "postgresql" ]; then
        if ! PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" >/dev/null 2>&1; then
            print_error "Failed to connect to PostgreSQL database"
            print_status "Please check:"
            echo "   - Database server is running"
            echo "   - Host, port, username, and password are correct"
            echo "   - Database exists"
            echo "   - User has CONNECT privilege on the database"
            exit 1
        fi
    else
        if ! mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "SELECT 1;" >/dev/null 2>&1; then
            print_error "Failed to connect to MySQL database"
            print_status "Please check:"
            echo "   - Database server is running"
            echo "   - Host, port, username, and password are correct"
            echo "   - Database exists"
            echo "   - User has CONNECT privilege on the database"
            exit 1
        fi
    fi
    
    print_success "Database connection verified"
    
    # Check permissions
    print_status "Checking database permissions..."
    
    if [ "$DB_TYPE" = "postgresql" ]; then
        # Check if user can create tables
        if ! PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "CREATE TEMP TABLE test_permissions (id SERIAL PRIMARY KEY);" >/dev/null 2>&1; then
            print_error "User lacks CREATE TABLE permission"
            print_status "Please grant the following permissions:"
            echo "   GRANT CREATE ON DATABASE $DB_NAME TO $DB_USER;"
            echo "   GRANT USAGE ON SCHEMA public TO $DB_USER;"
            echo "   GRANT CREATE ON SCHEMA public TO $DB_USER;"
            exit 1
        fi
        
        # Check if user can create indexes
        if ! PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "CREATE INDEX CONCURRENTLY test_index ON test_permissions(id);" >/dev/null 2>&1; then
            print_warning "User lacks CREATE INDEX permission (non-critical)"
        fi
        
        # Clean up test table
        PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "DROP TABLE IF EXISTS test_permissions;" >/dev/null 2>&1
        
    else
        # MySQL permission checks
        if ! mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "CREATE TEMPORARY TABLE test_permissions (id INT AUTO_INCREMENT PRIMARY KEY);" >/dev/null 2>&1; then
            print_error "User lacks CREATE TABLE permission"
            print_status "Please grant the following permissions:"
            echo "   GRANT CREATE ON $DB_NAME.* TO '$DB_USER'@'$DB_HOST';"
            echo "   GRANT INDEX ON $DB_NAME.* TO '$DB_USER'@'$DB_HOST';"
            exit 1
        fi
        
        # Clean up test table
        mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "DROP TEMPORARY TABLE IF EXISTS test_permissions;" >/dev/null 2>&1
    fi
    
    print_success "Database permissions verified"
}

# Function to create .env file
create_env_file() {
    print_step "Creating environment configuration file..."
    
    if [ -f "$ENV_FILE" ]; then
        print_warning "Environment file already exists. Creating backup..."
        cp "$ENV_FILE" "${ENV_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    cat > "$ENV_FILE" << EOF
# ServiceNow Advanced Visual Documentation - Environment Configuration
# Generated on $(date)

# Database Configuration
DB_TYPE=$DB_TYPE
DB_HOST=$DB_HOST
DB_PORT=$DB_PORT
DB_NAME=$DB_NAME
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DATABASE_URL=$DB_URL

# ServiceNow Configuration (Configure via UI)
SN_INSTANCE_URL=
SN_USERNAME=
SN_PASSWORD=
SN_CLIENT_ID=
SN_CLIENT_SECRET=

# Application Configuration
APP_PORT=$SSL_PORT
SSL_ENABLED=true
SSL_CERT_FILE=$CERT_FILE
SSL_KEY_FILE=$KEY_FILE

# Security Configuration
SECRET_KEY=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)

# Development Configuration
DEBUG=false
LOG_LEVEL=INFO
EOF
    
    print_success "Environment file created: $ENV_FILE"
}

# Function to generate SSL certificates
generate_ssl_certificates() {
    print_step "Generating SSL certificates..."
    
    if [ -d "$SSL_DIR" ]; then
        print_warning "SSL directory already exists. Creating backup..."
        mv "$SSL_DIR" "${SSL_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    mkdir -p "$SSL_DIR"
    
    # Generate private key
    openssl genrsa -out "$KEY_FILE" 2048
    
    # Generate certificate
    openssl req -new -x509 -key "$KEY_FILE" -out "$CERT_FILE" -days 365 -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    
    # Set proper permissions
    chmod 600 "$KEY_FILE"
    chmod 644 "$CERT_FILE"
    
    print_success "SSL certificates generated successfully"
}

# Function to install Python dependencies
install_dependencies() {
    print_step "Installing Python dependencies..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found. Installing basic dependencies..."
        pip3 install streamlit sqlalchemy psycopg2-binary cryptography python-dotenv
    fi
}

# Function to initialize database tables
initialize_database_tables() {
    print_step "🗄️ Initializing Database Schema"
    echo ""
    
    if [ "$DB_TYPE" = "sqlite" ]; then
        print_status "SQLite database - tables will be created automatically"
        return 0
    fi
    
    print_status "📋 Database Schema Initialization Workflow:"
    print_status "   1. 🔍 Verifying current database schema..."
    print_status "   2. 🛠️ Creating missing tables if needed..."
    print_status "   3. ✅ Verifying final schema integrity..."
    echo ""
    
    # Set environment variables for the Python scripts
    export DB_TYPE="$DB_TYPE"
    export DB_HOST="$DB_HOST"
    export DB_PORT="$DB_PORT"
    export DB_NAME="$DB_NAME"
    export DB_USER="$DB_USER"
    export DB_PASSWORD="$DB_PASSWORD"
    
    # Step 1: Verify current schema
    print_status "🔍 Step 1: Verifying current database schema..."
    if python3 verify_database_schema.py >/dev/null 2>&1; then
        print_success "✅ Database schema is already complete!"
        print_status "   All required tables exist with correct structure"
        return 0
    else
        print_warning "⚠️ Database schema needs initialization"
        print_status "   Some tables are missing or have incorrect structure"
    fi
    
    # Step 2: Initialize tables
    print_status "🛠️ Step 2: Creating missing database tables..."
    if python3 initialize_tables.py >/dev/null 2>&1; then
        print_success "✅ Database tables created successfully!"
    else
        print_error "❌ Failed to create tables using initialization script"
        print_status "🔄 Attempting fallback table creation..."
        
        # Fallback: try to create tables using the database module
        if python3 -c "
import os
os.environ['DB_TYPE'] = '$DB_TYPE'
os.environ['DB_HOST'] = '$DB_HOST'
os.environ['DB_PORT'] = '$DB_PORT'
os.environ['DB_NAME'] = '$DB_NAME'
os.environ['DB_USER'] = '$DB_USER'
os.environ['DB_PASSWORD'] = '$DB_PASSWORD'
from database import initialize_database
db = initialize_database()
print('✅ Fallback table creation successful!')
" 2>/dev/null; then
            print_success "✅ Fallback table creation successful!"
        else
            print_error "❌ All table creation methods failed!"
            print_status "Please check database permissions and try again"
            print_status "Required permissions: CREATE TABLE, CREATE INDEX, INSERT, SELECT"
            return 1
        fi
    fi
    
    # Step 3: Verify final schema
    print_status "✅ Step 3: Verifying final schema integrity..."
    if python3 verify_database_schema.py >/dev/null 2>&1; then
        print_success "🎉 Database schema initialization completed successfully!"
        print_status "   All required tables are now available"
        echo ""
        print_status "📊 Database Schema Summary:"
        print_status "   • servicenow_modules - ServiceNow application modules"
        print_status "   • servicenow_roles - User roles and permissions"
        print_status "   • servicenow_tables - Database table definitions"
        print_status "   • servicenow_properties - System properties"
        print_status "   • servicenow_scheduled_jobs - Automated jobs"
        print_status "   • database_configurations - Database settings"
        print_status "   • servicenow_configurations - ServiceNow settings"
        print_status "   • database_connections - Connection configs"
        print_status "   • database_introspections - Introspection results"
        return 0
    else
        print_error "❌ Schema verification failed after initialization!"
        print_status "Some tables may not have been created correctly"
        return 1
    fi
}

# Function to setup security
setup_security() {
    print_step "Setting up security configurations..."
    
    # Create .gitignore if it doesn't exist
    if [ ! -f ".gitignore" ]; then
        cat > .gitignore << EOF
# Environment files
.env
.env.local
.env.*.local

# SSL Certificates and Keys
ssl/
*.pem
*.key
*.crt
*.cert
*.p12
*.pfx
certificates/
certs/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Backup files
*.backup.*
EOF
        print_success ".gitignore created"
    fi
    
    # Set proper file permissions
    chmod 600 "$ENV_FILE" 2>/dev/null || true
    chmod 600 "$KEY_FILE" 2>/dev/null || true
    
    print_success "Security setup completed"
}

# Function to start application with SSL
start_application_ssl() {
    print_step "Starting ServiceNow Advanced Visual Documentation with SSL..."
    
    # Check if main app file exists
    if [ -f "enhanced_app.py" ]; then
        APP_FILE="enhanced_app.py"
    elif [ -f "app.py" ]; then
        APP_FILE="app.py"
    else
        print_error "No application file found (enhanced_app.py or app.py)"
        exit 1
    fi
    
    print_status "Starting application: $APP_FILE"
    print_status "SSL enabled on port: $SSL_PORT"
    print_status "Access your application at: https://localhost:$SSL_PORT"
    print_status "Press Ctrl+C to stop the application"
    echo ""
    
    # Start Streamlit with SSL
    PYTHONWARNINGS="ignore::urllib3.exceptions.NotOpenSSLWarning" streamlit run "$APP_FILE" \
        --server.port="$SSL_PORT" \
        --server.sslCertFile="$CERT_FILE" \
        --server.sslKeyFile="$KEY_FILE" \
        --server.headless=true \
        --server.enableXsrfProtection=true
}

# Function to show help
show_help() {
    echo "ServiceNow Advanced Visual Documentation - Enhanced Startup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h          Show this help message"
    echo "  --port PORT         Set application port (default: 8501)"
    echo "  --no-ssl           Disable SSL (not recommended)"
    echo "  --skip-db-config    Skip database configuration"
    echo "  --skip-db-verify    Skip database verification"
    echo "  --dev               Development mode (SQLite, no SSL)"
    echo ""
    echo "Examples:"
    echo "  $0                  # Full setup with service detection"
    echo "  $0 --port 8080     # Custom port"
    echo "  $0 --dev           # Development mode"
    echo "  $0 --skip-db-config # Skip database setup"
}

# Main function
main() {
    # Parse command line arguments
    SKIP_DB_CONFIG=false
    SKIP_DB_VERIFY=false
    DEV_MODE=false
    NO_SSL=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --port)
                SSL_PORT="$2"
                shift 2
                ;;
            --no-ssl)
                NO_SSL=true
                shift
                ;;
            --skip-db-config)
                SKIP_DB_CONFIG=true
                shift
                ;;
            --skip-db-verify)
                SKIP_DB_VERIFY=true
                shift
                ;;
            --dev)
                DEV_MODE=true
                SKIP_DB_CONFIG=true
                NO_SSL=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    print_header
    
    # Development mode setup
    if [ "$DEV_MODE" = true ]; then
        print_status "Development mode enabled"
        DB_TYPE="sqlite"
        DB_URL="sqlite:///servicenow_docs.db"
        SSL_PORT=8501
    fi
    
    # Check system requirements
    check_system_requirements
    
    # Configure database (unless skipped)
    if [ "$SKIP_DB_CONFIG" = false ]; then
        configure_database
    else
        print_status "Skipping database configuration"
        # Load from existing .env if available
        if [ -f "$ENV_FILE" ]; then
            source "$ENV_FILE"
        else
            print_error "No database configuration found. Please run without --skip-db-config"
            exit 1
        fi
    fi
    
    # Verify database connection (unless skipped)
    if [ "$SKIP_DB_VERIFY" = false ]; then
        verify_database_connection
    else
        print_status "Skipping database verification"
    fi
    
    # Initialize database tables IMMEDIATELY after connection verification
    initialize_database_tables
    
    # Create environment file
    create_env_file
    
    # Generate SSL certificates (unless disabled)
    if [ "$NO_SSL" = false ]; then
        generate_ssl_certificates
    else
        print_status "SSL disabled"
    fi
    
    # Install dependencies
    install_dependencies
    
    # Setup security
    setup_security
    
    # Start application
    if [ "$NO_SSL" = true ]; then
        print_step "Starting ServiceNow Advanced Visual Documentation..."
        PYTHONWARNINGS="ignore::urllib3.exceptions.NotOpenSSLWarning" streamlit run "$APP_FILE" --server.port="$SSL_PORT" --server.headless=true
    else
        start_application_ssl
    fi
}

# Run main function
main "$@"