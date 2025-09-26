#!/bin/bash

# ServiceNow Advanced Visual Documentation - Automated Startup Script
# This script automatically sets up and starts the ServiceNow documentation app

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${PURPLE}================================================${NC}"
    echo -e "${PURPLE}🚀 ServiceNow Advanced Visual Documentation${NC}"
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

# Function to test network connectivity
test_network_connectivity() {
    local host=$1
    local port=$2
    
    # Try different methods based on available tools
    if command_exists nc; then
        nc -z "$host" "$port" 2>/dev/null
    elif command_exists telnet; then
        timeout 5 telnet "$host" "$port" 2>/dev/null | grep -q "Connected"
    elif command_exists curl; then
        curl -s --connect-timeout 5 "http://$host:$port" >/dev/null 2>&1
    else
        # Fallback: try to connect using bash built-in
        timeout 5 bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null
    fi
}

# Function to check if port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service_name=$3
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z $host $port 2>/dev/null; then
            print_success "$service_name is ready!"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    print_error "$service_name failed to start within expected time"
    return 1
}

# Function to setup Python environment
setup_python_environment() {
    print_step "Setting up Python environment..."
    
    # Check if Python 3 is installed
    if ! command_exists python3; then
        print_error "Python 3 is not installed. Please install Python 3.9+ first."
        echo "Visit: https://www.python.org/downloads/"
        exit 1
    fi
    
    # Check Python version
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_status "Python version: $python_version"
    
    # Check if pip is installed
    if ! command_exists pip3; then
        print_error "pip3 is not installed. Please install pip first."
        exit 1
    fi
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install requirements
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    
    print_success "Python environment setup complete!"
}

# Function to check PostgreSQL installation
check_postgresql() {
    # Check if psql command is available in PATH
    if command_exists psql; then
        return 0
    fi
    
    # Check for Homebrew PostgreSQL installations
    if [ -f "/opt/homebrew/opt/postgresql@15/bin/psql" ] || [ -f "/opt/homebrew/bin/psql" ] || [ -f "/usr/local/bin/psql" ]; then
        return 0
    fi
    
    # Check for system PostgreSQL
    if [ -f "/usr/bin/psql" ]; then
        return 0
    fi
    
    return 1
}

# Function to install PostgreSQL
install_postgresql() {
    print_step "Installing PostgreSQL..."
    
    # Detect OS and install PostgreSQL
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command_exists apt-get; then
            # Ubuntu/Debian
            print_status "Installing PostgreSQL on Ubuntu/Debian..."
            sudo apt-get update
            sudo apt-get install -y postgresql postgresql-contrib
        elif command_exists yum; then
            # CentOS/RHEL/Rocky Linux
            print_status "Installing PostgreSQL on CentOS/RHEL..."
            sudo yum install -y postgresql-server postgresql-contrib
            sudo postgresql-setup initdb
        elif command_exists dnf; then
            # Fedora
            print_status "Installing PostgreSQL on Fedora..."
            sudo dnf install -y postgresql-server postgresql-contrib
            sudo postgresql-setup initdb
        else
            print_error "Unsupported Linux distribution. Please install PostgreSQL manually."
            return 1
        fi
        
        # Start PostgreSQL service
        sudo systemctl enable postgresql
        sudo systemctl start postgresql
        
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            print_status "Installing PostgreSQL on macOS with Homebrew..."
            brew install postgresql
            brew services start postgresql
        else
            print_error "Homebrew not found. Please install PostgreSQL manually or install Homebrew first."
            return 1
        fi
    else
        print_error "Unsupported operating system. Please install PostgreSQL manually."
        return 1
    fi
    
    print_success "PostgreSQL installed successfully!"
    return 0
}

# Function to setup PostgreSQL database
setup_postgresql_database() {
    local db_name="${1:-servicenow_docs}"
    local db_user="${2:-servicenow_user}"
    
    print_step "Setting up PostgreSQL database '$db_name'..."
    
    # Find psql command
    PSQL_CMD=""
    if command_exists psql; then
        PSQL_CMD="psql"
    else
        # Try to find psql in common locations
        if [ -f "/opt/homebrew/opt/postgresql@15/bin/psql" ]; then
            PSQL_CMD="/opt/homebrew/opt/postgresql@15/bin/psql"
        elif [ -f "/opt/homebrew/bin/psql" ]; then
            PSQL_CMD="/opt/homebrew/bin/psql"
        elif [ -f "/usr/local/bin/psql" ]; then
            PSQL_CMD="/usr/local/bin/psql"
        elif [ -f "/usr/bin/psql" ]; then
            PSQL_CMD="/usr/bin/psql"
        else
            print_error "psql command not found. Cannot setup database."
            return 1
        fi
    fi
    
    # Check if database exists
    if "$PSQL_CMD" -lqt | cut -d \| -f 1 | grep -qw "$db_name"; then
        print_status "Database '$db_name' already exists"
    else
        print_status "Creating database '$db_name'..."
        
        # Create database and user
        # For Homebrew PostgreSQL, use current user as superuser
        CURRENT_USER=$(whoami)
        
        # Generate a secure random password
        DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        
        sudo -u "$CURRENT_USER" "$PSQL_CMD" << EOF
CREATE DATABASE $db_name;
CREATE USER $db_user WITH PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE $db_name TO $db_user;
GRANT CREATE ON DATABASE $db_name TO $db_user;
\q
EOF
        
        # Grant additional permissions after connecting to the database
        print_status "Setting up additional permissions..."
        sudo -u "$CURRENT_USER" "$PSQL_CMD" -d "$db_name" << EOF
GRANT ALL PRIVILEGES ON SCHEMA public TO $db_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $db_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $db_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO $db_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO $db_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO $db_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON FUNCTIONS TO $db_user;
\q
EOF
        print_success "Database created successfully!"
        
        # Check permissions for the created user
        print_status "Verifying user permissions..."
        if check_database_permissions "localhost" "5432" "$db_name" "$db_user" "$DB_PASSWORD"; then
            print_success "✅ User permissions verified successfully!"
            
            # Create all application tables
            echo ""
            if create_application_tables "localhost" "5432" "$db_name" "$db_user" "$DB_PASSWORD"; then
                print_success "✅ Database and tables setup completed successfully!"
            else
                print_warning "⚠️ Database created, but table creation failed."
                print_status "You can still proceed, but some features may not work until tables are created."
            fi
        else
            print_warning "⚠️ User permissions check failed, but database was created."
            print_status "You may need to manually grant additional permissions."
        fi
    fi
}

# Function to get PostgreSQL connection details
get_postgresql_connection() {
    print_step "PostgreSQL Connection Setup"
    echo ""
    print_status "Please provide your PostgreSQL connection details:"
    echo ""
    
    read -p "PostgreSQL Host [localhost]: " DB_HOST
    DB_HOST=${DB_HOST:-localhost}
    
    read -p "PostgreSQL Port [5432]: " DB_PORT
    DB_PORT=${DB_PORT:-5432}
    
    read -p "Database Name [servicenow_docs]: " DB_NAME
    DB_NAME=${DB_NAME:-servicenow_docs}
    
    read -p "Username [servicenow_user]: " DB_USER
    DB_USER=${DB_USER:-servicenow_user}
    
    read -s -p "Password: " DB_PASSWORD
    echo ""
    
    # Test connection with detailed error reporting
    print_status "Testing PostgreSQL connection..."
    
    # Check if psql is available and find it if not in PATH
    PSQL_CMD=""
    if command_exists psql; then
        PSQL_CMD="psql"
    else
        # Try to find psql in common locations
        if [ -f "/opt/homebrew/opt/postgresql@15/bin/psql" ]; then
            PSQL_CMD="/opt/homebrew/opt/postgresql@15/bin/psql"
            print_status "Found PostgreSQL client at: $PSQL_CMD"
        elif [ -f "/opt/homebrew/bin/psql" ]; then
            PSQL_CMD="/opt/homebrew/bin/psql"
            print_status "Found PostgreSQL client at: $PSQL_CMD"
        elif [ -f "/usr/local/bin/psql" ]; then
            PSQL_CMD="/usr/local/bin/psql"
            print_status "Found PostgreSQL client at: $PSQL_CMD"
        elif [ -f "/usr/bin/psql" ]; then
            PSQL_CMD="/usr/bin/psql"
            print_status "Found PostgreSQL client at: $PSQL_CMD"
        else
            print_error "psql command not found. Please install PostgreSQL client tools."
            print_status "For macOS with Homebrew: brew install postgresql"
            print_status "For Ubuntu/Debian: sudo apt-get install postgresql-client"
            print_status "For CentOS/RHEL: sudo yum install postgresql"
            return 1
        fi
    fi
    
    # Test basic connectivity
    if ! test_network_connectivity "$DB_HOST" "$DB_PORT"; then
        print_error "Cannot connect to $DB_HOST:$DB_PORT"
        print_status "Troubleshooting suggestions:"
        echo "  - Check if PostgreSQL server is running"
        echo "  - Verify the host and port are correct"
        echo "  - Check firewall settings"
        echo "  - Ensure PostgreSQL is listening on the specified port"
        echo "  - Try: sudo systemctl status postgresql"
        echo "  - Try: sudo netstat -tlnp | grep $DB_PORT"
        return 1
    fi
    
    # Test database connection
    if PGPASSWORD="$DB_PASSWORD" "$PSQL_CMD" -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" >/dev/null 2>&1; then
        print_success "PostgreSQL connection successful!"
        
        # Check database user permissions
        if check_database_permissions "$DB_HOST" "$DB_PORT" "$DB_NAME" "$DB_USER" "$DB_PASSWORD"; then
            print_success "✅ Database user has all necessary permissions!"
            
            # Create all application tables
            echo ""
            if create_application_tables "$DB_HOST" "$DB_PORT" "$DB_NAME" "$DB_USER" "$DB_PASSWORD"; then
                print_success "✅ Database setup completed successfully!"
                return 0
            else
                print_warning "⚠️ Database permissions verified, but table creation failed."
                print_status "You can still proceed, but some features may not work until tables are created."
                return 0
            fi
        else
            print_error "❌ Database user lacks necessary permissions for table creation."
            echo ""
            print_status "Please grant the required permissions and run this script again."
            return 1
        fi
    else
        print_error "PostgreSQL connection failed. Please check your credentials."
        echo ""
        print_status "Troubleshooting suggestions:"
        echo "  - Verify username and password are correct"
        echo "  - Check if the database '$DB_NAME' exists"
        echo "  - Ensure user '$DB_USER' has access to database '$DB_NAME'"
        echo "  - Check PostgreSQL authentication settings (pg_hba.conf)"
        echo ""
        
        # Offer to create database and user
        read -p "Do you want to create the database and user? (y/n) [n]: " CREATE_DB_USER
        CREATE_DB_USER=${CREATE_DB_USER:-n}
        
        if [[ "$CREATE_DB_USER" =~ ^[Yy]$ ]]; then
            print_status "Attempting to create database and user..."
            
            # Try to connect as superuser to create database and user
            # For Homebrew PostgreSQL, use current user as superuser
            CURRENT_USER=$(whoami)
            print_status "Using '$CURRENT_USER' as PostgreSQL superuser"
            read -p "PostgreSQL superuser ($CURRENT_USER) password: " POSTGRES_PASSWORD
            
            if PGPASSWORD="$POSTGRES_PASSWORD" "$PSQL_CMD" -h "$DB_HOST" -p "$DB_PORT" -U "$CURRENT_USER" -c "CREATE DATABASE $DB_NAME;" >/dev/null 2>&1; then
                print_success "Database '$DB_NAME' created successfully!"
            else
                print_warning "Database '$DB_NAME' may already exist or creation failed"
            fi
            
            # Generate a secure random password for the new user
            NEW_USER_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
            
            if PGPASSWORD="$POSTGRES_PASSWORD" "$PSQL_CMD" -h "$DB_HOST" -p "$DB_PORT" -U "$CURRENT_USER" -c "CREATE USER $DB_USER WITH PASSWORD '$NEW_USER_PASSWORD';" >/dev/null 2>&1; then
                print_success "User '$DB_USER' created successfully!"
            else
                print_warning "User '$DB_USER' may already exist or creation failed"
            fi
            
            if PGPASSWORD="$POSTGRES_PASSWORD" "$PSQL_CMD" -h "$DB_HOST" -p "$DB_PORT" -U "$CURRENT_USER" -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" >/dev/null 2>&1; then
                print_success "Database privileges granted successfully!"
            else
                print_warning "Failed to grant database privileges"
            fi
            
            # Grant additional permissions
            print_status "Setting up additional permissions..."
            if PGPASSWORD="$POSTGRES_PASSWORD" "$PSQL_CMD" -h "$DB_HOST" -p "$DB_PORT" -U "$CURRENT_USER" -d "$DB_NAME" -c "GRANT ALL PRIVILEGES ON SCHEMA public TO $DB_USER;" >/dev/null 2>&1; then
                print_success "Schema privileges granted!"
            fi
            
            if PGPASSWORD="$POSTGRES_PASSWORD" "$PSQL_CMD" -h "$DB_HOST" -p "$DB_PORT" -U "$CURRENT_USER" -d "$DB_NAME" -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;" >/dev/null 2>&1; then
                print_success "Table privileges granted!"
            fi
            
            if PGPASSWORD="$POSTGRES_PASSWORD" "$PSQL_CMD" -h "$DB_HOST" -p "$DB_PORT" -U "$CURRENT_USER" -d "$DB_NAME" -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;" >/dev/null 2>&1; then
                print_success "Sequence privileges granted!"
            fi
            
            if PGPASSWORD="$POSTGRES_PASSWORD" "$PSQL_CMD" -h "$DB_HOST" -p "$DB_PORT" -U "$CURRENT_USER" -d "$DB_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO $DB_USER;" >/dev/null 2>&1; then
                print_success "Default table privileges granted!"
            fi
            
            # Test connection again
            print_status "Testing connection again..."
            if PGPASSWORD="$NEW_USER_PASSWORD" "$PSQL_CMD" -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" >/dev/null 2>&1; then
                print_success "PostgreSQL connection successful after setup!"
                return 0
            else
                print_error "Connection still failed after database/user creation"
                return 1
            fi
        else
            return 1
        fi
    fi
}

# Function to check database user permissions
check_database_permissions() {
    local db_host="$1"
    local db_port="$2"
    local db_name="$3"
    local db_user="$4"
    local db_password="$5"
    
    print_step "Checking Database User Permissions"
    echo ""
    
    # Find psql command
    PSQL_CMD=""
    if command_exists psql; then
        PSQL_CMD="psql"
    elif [ -f "/opt/homebrew/opt/postgresql@15/bin/psql" ]; then
        PSQL_CMD="/opt/homebrew/opt/postgresql@15/bin/psql"
    elif [ -f "/opt/homebrew/opt/postgresql@14/bin/psql" ]; then
        PSQL_CMD="/opt/homebrew/opt/postgresql@14/bin/psql"
    elif [ -f "/opt/homebrew/opt/postgresql@13/bin/psql" ]; then
        PSQL_CMD="/opt/homebrew/opt/postgresql@13/bin/psql"
    elif [ -f "/opt/homebrew/opt/postgresql/bin/psql" ]; then
        PSQL_CMD="/opt/homebrew/opt/postgresql/bin/psql"
    else
        print_error "psql command not found. Please install PostgreSQL client tools."
        return 1
    fi
    
    print_status "Using psql command: $PSQL_CMD"
    
    # Test connection and check permissions
    print_status "Testing database connection and checking permissions..."
    
    # Create a temporary SQL file for permission checks
    TEMP_SQL=$(mktemp)
    cat > "$TEMP_SQL" << 'EOF'
-- Check if user can connect
SELECT 'Connection successful' as status;

-- Check schema privileges
SELECT 
    CASE 
        WHEN has_schema_privilege(current_user, 'public', 'CREATE') THEN 'CREATE: Yes'
        ELSE 'CREATE: No'
    END as create_privilege,
    CASE 
        WHEN has_schema_privilege(current_user, 'USAGE') THEN 'USAGE: Yes'
        ELSE 'USAGE: No'
    END as usage_privilege;

-- Check if user can create tables
SELECT 
    CASE 
        WHEN has_database_privilege(current_database(), 'CREATE') THEN 'Database CREATE: Yes'
        ELSE 'Database CREATE: No'
    END as db_create_privilege;

-- Check current user and database
SELECT 
    current_user as current_user,
    current_database() as current_database;
EOF

    # Run permission checks
    if [ -n "$db_password" ]; then
        PGPASSWORD="$db_password" "$PSQL_CMD" -h "$db_host" -p "$db_port" -U "$db_user" -d "$db_name" -f "$TEMP_SQL" 2>/dev/null
    else
        "$PSQL_CMD" -h "$db_host" -p "$db_port" -U "$db_user" -d "$db_name" -f "$TEMP_SQL" 2>/dev/null
    fi
    
    local exit_code=$?
    rm -f "$TEMP_SQL"
    
    if [ $exit_code -ne 0 ]; then
        print_error "Failed to connect to database or check permissions."
        return 1
    fi
    
    # Check specific permissions
    print_status "Checking specific permissions..."
    
    # Check comprehensive database permissions
    print_status "Checking comprehensive database permissions..."
    
    # Create a temporary SQL file for comprehensive permission checks
    TEMP_SQL=$(mktemp)
    cat > "$TEMP_SQL" << EOF
-- Check if user can connect to the database
SELECT 'Database connection: OK' as connection_status;

-- Check database-level permissions
SELECT 
    CASE 
        WHEN has_database_privilege(current_user, current_database(), 'CREATE') THEN 'Database CREATE: Yes'
        ELSE 'Database CREATE: No'
    END as db_create_privilege,
    CASE 
        WHEN has_database_privilege(current_user, current_database(), 'CONNECT') THEN 'Database CONNECT: Yes'
        ELSE 'Database CONNECT: No'
    END as db_connect_privilege;

-- Check schema-level permissions
SELECT 
    CASE 
        WHEN has_schema_privilege(current_user, 'public', 'CREATE') THEN 'Schema CREATE: Yes'
        ELSE 'Schema CREATE: No'
    END as schema_create_privilege,
    CASE 
        WHEN has_schema_privilege(current_user, 'public', 'USAGE') THEN 'Schema USAGE: Yes'
        ELSE 'Schema USAGE: No'
    END as schema_usage_privilege;

-- Check if user can actually create a table
SELECT 
    CASE 
        WHEN has_database_privilege(current_user, current_database(), 'CREATE') 
         AND has_schema_privilege(current_user, 'public', 'CREATE') 
         AND has_schema_privilege(current_user, 'public', 'USAGE') THEN 'Can create tables: Yes'
        ELSE 'Can create tables: No'
    END as can_create_tables;
EOF

    # Run comprehensive permission checks
    local permission_result
    if [ -n "$db_password" ]; then
        permission_result=$(PGPASSWORD="$db_password" "$PSQL_CMD" -h "$db_host" -p "$db_port" -U "$db_user" -d "$db_name" -f "$TEMP_SQL" 2>/dev/null)
    else
        permission_result=$("$PSQL_CMD" -h "$db_host" -p "$db_port" -U "$db_user" -d "$db_name" -f "$TEMP_SQL" 2>/dev/null)
    fi
    
    local exit_code=$?
    rm -f "$TEMP_SQL"
    
    if [ $exit_code -ne 0 ]; then
        print_error "Failed to check database permissions."
        return 1
    fi
    
    # Check if user can create tables (comprehensive check)
    local can_create_check
    if [ -n "$db_password" ]; then
        can_create_check=$(PGPASSWORD="$db_password" "$PSQL_CMD" -h "$db_host" -p "$db_port" -U "$db_user" -d "$db_name" -t -c "
            SELECT 
                CASE 
                    WHEN has_database_privilege(current_user, current_database(), 'CREATE') 
                     AND has_schema_privilege(current_user, 'public', 'CREATE') 
                     AND has_schema_privilege(current_user, 'public', 'USAGE') THEN 't'
                    ELSE 'f'
                END;" 2>/dev/null | tr -d ' \n')
    else
        can_create_check=$("$PSQL_CMD" -h "$db_host" -p "$db_port" -U "$db_user" -d "$db_name" -t -c "
            SELECT 
                CASE 
                    WHEN has_database_privilege(current_user, current_database(), 'CREATE') 
                     AND has_schema_privilege(current_user, 'public', 'CREATE') 
                     AND has_schema_privilege(current_user, 'public', 'USAGE') THEN 't'
                    ELSE 'f'
                END;" 2>/dev/null | tr -d ' \n')
    fi
    
    if [ "$can_create_check" = "t" ]; then
        print_success "✅ User has all necessary permissions to create tables in database '$db_name'"
        return 0
    else
        print_error "❌ User lacks necessary permissions to create tables in database '$db_name'"
        echo ""
        print_warning "The user '$db_user' needs additional permissions for database '$db_name'."
        echo ""
        print_status "To fix this, run the following commands as a PostgreSQL superuser:"
        echo ""
        echo -e "${YELLOW}# Connect as superuser (replace 'superuser' with your PostgreSQL superuser)${NC}"
        echo -e "${CYAN}$PSQL_CMD -h $db_host -p $db_port -U superuser -d $db_name${NC}"
        echo ""
        echo -e "${YELLOW}# Grant necessary privileges to $db_user for database $db_name${NC}"
        echo -e "${CYAN}ALTER USER $db_user CREATEDB;${NC}"
        echo -e "${CYAN}GRANT ALL PRIVILEGES ON DATABASE $db_name TO $db_user;${NC}"
        echo -e "${CYAN}GRANT ALL ON SCHEMA public TO $db_user;${NC}"
        echo -e "${CYAN}GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $db_user;${NC}"
        echo -e "${CYAN}GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $db_user;${NC}"
        echo -e "${CYAN}ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO $db_user;${NC}"
        echo -e "${CYAN}ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO $db_user;${NC}"
        echo ""
        echo -e "${YELLOW}# Verify privileges${NC}"
        echo -e "${CYAN}SELECT has_database_privilege('$db_user', '$db_name', 'CREATE');${NC}"
        echo -e "${CYAN}SELECT has_schema_privilege('$db_user', 'public', 'CREATE');${NC}"
        echo ""
        print_status "After granting permissions, run this script again."
        return 1
    fi
}

# Function to create all necessary database tables
create_application_tables() {
    local db_host="$1"
    local db_port="$2"
    local db_name="$3"
    local db_user="$4"
    local db_password="$5"
    
    print_step "Creating Application Database Tables"
    echo ""
    print_status "Creating all necessary tables in database '$db_name'..."
    
    # Find psql command
    PSQL_CMD=""
    if command_exists psql; then
        PSQL_CMD="psql"
    elif [ -f "/opt/homebrew/opt/postgresql@15/bin/psql" ]; then
        PSQL_CMD="/opt/homebrew/opt/postgresql@15/bin/psql"
    elif [ -f "/opt/homebrew/opt/postgresql@14/bin/psql" ]; then
        PSQL_CMD="/opt/homebrew/opt/postgresql@14/bin/psql"
    elif [ -f "/opt/homebrew/opt/postgresql@13/bin/psql" ]; then
        PSQL_CMD="/opt/homebrew/opt/postgresql@13/bin/psql"
    elif [ -f "/opt/homebrew/opt/postgresql/bin/psql" ]; then
        PSQL_CMD="/opt/homebrew/opt/postgresql/bin/psql"
    else
        print_error "psql command not found. Cannot create tables."
        return 1
    fi
    
    print_status "Using psql command: $PSQL_CMD"
    
    # Create a temporary SQL file with all table creation statements
    TEMP_SQL=$(mktemp)
    cat > "$TEMP_SQL" << 'EOF'
-- ServiceNow Modules Table
CREATE TABLE IF NOT EXISTS servicenow_modules (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    label VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(50),
    module_type VARCHAR(100),
    documentation_url VARCHAR(500),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- ServiceNow Roles Table
CREATE TABLE IF NOT EXISTS servicenow_roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    label VARCHAR(255),
    description TEXT,
    module_id INTEGER REFERENCES servicenow_modules(id) ON DELETE CASCADE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(name, module_id)
);

-- ServiceNow Tables Table
CREATE TABLE IF NOT EXISTS servicenow_tables (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    label VARCHAR(255),
    description TEXT,
    module_id INTEGER REFERENCES servicenow_modules(id) ON DELETE CASCADE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(name, module_id)
);

-- ServiceNow Properties Table
CREATE TABLE IF NOT EXISTS servicenow_properties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    label VARCHAR(255),
    description TEXT,
    data_type VARCHAR(100),
    module_id INTEGER REFERENCES servicenow_modules(id) ON DELETE CASCADE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(name, module_id)
);

-- ServiceNow Scheduled Jobs Table
CREATE TABLE IF NOT EXISTS servicenow_scheduled_jobs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    label VARCHAR(255),
    description TEXT,
    schedule VARCHAR(255),
    module_id INTEGER REFERENCES servicenow_modules(id) ON DELETE CASCADE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    UNIQUE(name, module_id)
);

-- Database Connections Table
CREATE TABLE IF NOT EXISTS database_connections (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    db_type VARCHAR(50) NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    database_name VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(500) NOT NULL,
    connection_pool_size INTEGER DEFAULT 10,
    max_overflow INTEGER DEFAULT 20,
    echo BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Database Configurations Table
CREATE TABLE IF NOT EXISTS database_configurations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    db_type VARCHAR(50) NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    database_name VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(500) NOT NULL,
    connection_pool_size INTEGER DEFAULT 10,
    max_overflow INTEGER DEFAULT 20,
    echo BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ServiceNow Configurations Table
CREATE TABLE IF NOT EXISTS servicenow_configurations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    instance_url VARCHAR(500) NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(500) NOT NULL,
    api_version VARCHAR(50) DEFAULT 'v2',
    timeout INTEGER DEFAULT 30,
    max_retries INTEGER DEFAULT 3,
    verify_ssl BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Database Introspection Table
CREATE TABLE IF NOT EXISTS database_introspection (
    id SERIAL PRIMARY KEY,
    database_name VARCHAR(255) NOT NULL,
    table_name VARCHAR(255) NOT NULL,
    column_name VARCHAR(255) NOT NULL,
    data_type VARCHAR(100),
    is_nullable BOOLEAN,
    column_default TEXT,
    introspection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(database_name, table_name, column_name)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_servicenow_modules_name ON servicenow_modules(name);
CREATE INDEX IF NOT EXISTS idx_servicenow_roles_module_id ON servicenow_roles(module_id);
CREATE INDEX IF NOT EXISTS idx_servicenow_tables_module_id ON servicenow_tables(module_id);
CREATE INDEX IF NOT EXISTS idx_servicenow_properties_module_id ON servicenow_properties(module_id);
CREATE INDEX IF NOT EXISTS idx_servicenow_scheduled_jobs_module_id ON servicenow_scheduled_jobs(module_id);
CREATE INDEX IF NOT EXISTS idx_database_configurations_name ON database_configurations(name);
CREATE INDEX IF NOT EXISTS idx_servicenow_configurations_name ON servicenow_configurations(name);
CREATE INDEX IF NOT EXISTS idx_database_introspection_database_name ON database_introspection(database_name);

-- Insert default configuration if it doesn't exist
INSERT INTO database_configurations (name, db_type, host, port, database_name, username, password, is_active)
SELECT 'default', 'postgresql', 'localhost', 5432, 'servicenow_docs', 'servicenow_user', 'servicenow123', true
WHERE NOT EXISTS (SELECT 1 FROM database_configurations WHERE name = 'default');
EOF

    # Execute the table creation script
    print_status "Executing table creation script..."
    if [ -n "$db_password" ]; then
        if PGPASSWORD="$db_password" "$PSQL_CMD" -h "$db_host" -p "$db_port" -U "$db_user" -d "$db_name" -f "$TEMP_SQL" >/dev/null 2>&1; then
            print_success "✅ All application tables created successfully!"
        else
            print_error "❌ Failed to create application tables"
            rm -f "$TEMP_SQL"
            return 1
        fi
    else
        if "$PSQL_CMD" -h "$db_host" -p "$db_port" -U "$db_user" -d "$db_name" -f "$TEMP_SQL" >/dev/null 2>&1; then
            print_success "✅ All application tables created successfully!"
        else
            print_error "❌ Failed to create application tables"
            rm -f "$TEMP_SQL"
            return 1
        fi
    fi
    
    rm -f "$TEMP_SQL"
    
    # Verify tables were created
    print_status "Verifying table creation..."
    local table_count
    if [ -n "$db_password" ]; then
        table_count=$(PGPASSWORD="$db_password" "$PSQL_CMD" -h "$db_host" -p "$db_port" -U "$db_user" -d "$db_name" -t -c "
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('servicenow_modules', 'servicenow_roles', 'servicenow_tables', 'servicenow_properties', 
                              'servicenow_scheduled_jobs', 'database_connections', 'database_configurations', 
                              'servicenow_configurations', 'database_introspection');" 2>/dev/null | tr -d ' \n')
    else
        table_count=$("$PSQL_CMD" -h "$db_host" -p "$db_port" -U "$db_user" -d "$db_name" -t -c "
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('servicenow_modules', 'servicenow_roles', 'servicenow_tables', 'servicenow_properties', 
                              'servicenow_scheduled_jobs', 'database_connections', 'database_configurations', 
                              'servicenow_configurations', 'database_introspection');" 2>/dev/null | tr -d ' \n')
    fi
    
    if [ "$table_count" = "9" ]; then
        print_success "✅ All 9 application tables verified successfully!"
        print_status "Tables created:"
        echo "  • servicenow_modules"
        echo "  • servicenow_roles" 
        echo "  • servicenow_tables"
        echo "  • servicenow_properties"
        echo "  • servicenow_scheduled_jobs"
        echo "  • database_connections"
        echo "  • database_configurations"
        echo "  • servicenow_configurations"
        echo "  • database_introspection"
        return 0
    else
        print_warning "⚠️ Expected 9 tables, but found $table_count tables"
        return 1
    fi
}

# Function to setup database with user interaction
setup_database() {
    print_step "Database Setup"
    echo ""
    
    # Check if PostgreSQL is available
    if check_postgresql; then
        print_status "PostgreSQL is already installed and available"
        echo ""
        read -p "Do you want to use the existing PostgreSQL installation? (y/n) [y]: " USE_EXISTING_POSTGRES
        USE_EXISTING_POSTGRES=${USE_EXISTING_POSTGRES:-y}
        
        if [[ "$USE_EXISTING_POSTGRES" =~ ^[Yy]$ ]]; then
            # Use existing PostgreSQL
            echo ""
            read -p "Do you want to use default connection settings? (y/n) [y]: " USE_DEFAULT_CONNECTION
            USE_DEFAULT_CONNECTION=${USE_DEFAULT_CONNECTION:-y}
            
            if [[ "$USE_DEFAULT_CONNECTION" =~ ^[Yy]$ ]]; then
                # Use default settings
                DB_HOST="localhost"
                DB_PORT="5432"
                DB_NAME="servicenow_docs"
                DB_USER="servicenow_user"
                DB_PASSWORD=""
                
                # Setup database with default settings
                setup_postgresql_database "$DB_NAME" "$DB_USER"
            else
                # Get custom connection details
                get_postgresql_connection
                if [ $? -ne 0 ]; then
                    print_warning "Using SQLite as fallback due to connection issues."
                    USE_POSTGRESQL=false
                else
                    USE_POSTGRESQL=true
                fi
            fi
        else
            # Don't use existing PostgreSQL
            USE_POSTGRESQL=false
        fi
    else
        # PostgreSQL not installed
        print_warning "PostgreSQL is not installed on this system."
        echo ""
        print_status "You have the following options:"
        echo "1. Install PostgreSQL locally (recommended)"
        echo "2. Connect to an existing PostgreSQL server"
        echo "3. Check database user permissions"
        echo "4. Create application tables"
        echo "5. Use SQLite (simpler, but limited functionality)"
        echo ""
        
        read -p "Choose an option (1/2/3/4/5) [1]: " DB_OPTION
        DB_OPTION=${DB_OPTION:-1}
        
        case $DB_OPTION in
            1)
                # Install PostgreSQL
                echo ""
                read -p "Do you want to install PostgreSQL locally? (y/n) [y]: " INSTALL_POSTGRES
                INSTALL_POSTGRES=${INSTALL_POSTGRES:-y}
                
                if [[ "$INSTALL_POSTGRES" =~ ^[Yy]$ ]]; then
                    install_postgresql
                    if [ $? -eq 0 ]; then
                        # Set default database settings before setup
                        DB_HOST="localhost"
                        DB_PORT="5432"
                        DB_NAME="servicenow_docs"
                        DB_USER="servicenow_user"
                        DB_PASSWORD=""
                        
                        setup_postgresql_database "$DB_NAME" "$DB_USER"
                        USE_POSTGRESQL=true
                    else
                        print_warning "PostgreSQL installation failed. Using SQLite as fallback."
                        USE_POSTGRESQL=false
                    fi
                else
                    print_warning "Skipping PostgreSQL installation. Using SQLite as fallback."
                    USE_POSTGRESQL=false
                fi
                ;;
            2)
                # Connect to existing PostgreSQL
                get_postgresql_connection
                if [ $? -eq 0 ]; then
                    USE_POSTGRESQL=true
                else
                    print_warning "Using SQLite as fallback due to connection issues."
                    USE_POSTGRESQL=false
                fi
                ;;
            3)
                # Check database user permissions
                print_step "Database User Permission Check"
                echo ""
                print_status "This will check if a database user has the necessary permissions to create tables."
                echo ""
                
                read -p "PostgreSQL Host [localhost]: " DB_HOST
                DB_HOST=${DB_HOST:-localhost}
                
                read -p "PostgreSQL Port [5432]: " DB_PORT
                DB_PORT=${DB_PORT:-5432}
                
                read -p "Database Name [servicenow_docs]: " DB_NAME
                DB_NAME=${DB_NAME:-servicenow_docs}
                
                read -p "Username: " DB_USER
                
                read -s -p "Password: " DB_PASSWORD
                echo ""
                
                if check_database_permissions "$DB_HOST" "$DB_PORT" "$DB_NAME" "$DB_USER" "$DB_PASSWORD"; then
                    print_success "✅ User has all necessary permissions!"
                    echo ""
                    print_status "You can now proceed with the database setup."
                else
                    print_error "❌ User lacks necessary permissions."
                    echo ""
                    print_status "Please grant the required permissions and try again."
                fi
                
                # Ask if they want to continue with setup
                echo ""
                read -p "Do you want to continue with database setup? (y/n) [n]: " CONTINUE_SETUP
                CONTINUE_SETUP=${CONTINUE_SETUP:-n}
                
                if [[ "$CONTINUE_SETUP" =~ ^[Yy]$ ]]; then
                    # Set the connection details and continue
                    USE_POSTGRESQL=true
                else
                    print_status "Permission check completed. Exiting."
                    exit 0
                fi
                ;;
            4)
                # Create application tables
                print_step "Create Application Tables"
                echo ""
                print_status "This will create all necessary tables in your existing database."
                echo ""
                
                read -p "Database Host [localhost]: " DB_HOST
                DB_HOST=${DB_HOST:-localhost}
                
                read -p "Database Port [5432]: " DB_PORT
                DB_PORT=${DB_PORT:-5432}
                
                read -p "Database Name: " DB_NAME
                
                read -p "Username: " DB_USER
                
                read -s -p "Password: " DB_PASSWORD
                echo ""
                
                if create_application_tables "$DB_HOST" "$DB_PORT" "$DB_NAME" "$DB_USER" "$DB_PASSWORD"; then
                    print_success "✅ Application tables created successfully!"
                    echo ""
                    print_status "You can now start the application."
                else
                    print_error "❌ Failed to create application tables."
                    echo ""
                    print_status "Please check your database connection and permissions."
                fi
                
                exit 0
                ;;
            5)
                # Use SQLite
                print_status "Using SQLite database (simpler setup)"
                USE_POSTGRESQL=false
                ;;
            *)
                print_warning "Invalid option. Using SQLite as fallback."
                USE_POSTGRESQL=false
                ;;
        esac
    fi
    
    # Set database type for environment file
    if [ "$USE_POSTGRESQL" = true ]; then
        DB_TYPE="postgresql"
        print_success "PostgreSQL database configured successfully!"
    else
        DB_TYPE="sqlite"
        print_status "Using SQLite database (no additional setup required)"
    fi
}

# Function to setup environment file
setup_environment() {
    print_step "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        cp env.template .env
        
        # Update .env with database settings
        if [ "$USE_POSTGRESQL" = true ]; then
            print_status "Configuring PostgreSQL settings..."
            sed -i.bak "s/DB_HOST=localhost/DB_HOST=$DB_HOST/" .env
            sed -i.bak "s/DB_PORT=5432/DB_PORT=$DB_PORT/" .env
            sed -i.bak "s/DB_NAME=servicenow_docs/DB_NAME=$DB_NAME/" .env
            sed -i.bak "s/DB_USER=servicenow_user/DB_USER=$DB_USER/" .env
            sed -i.bak "s/DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" .env
            
            # Add database type
            echo "DB_TYPE=postgresql" >> .env
        else
            print_status "Configuring SQLite settings..."
            sed -i.bak "s/DB_HOST=localhost/DB_HOST=localhost/" .env
            sed -i.bak "s/DB_USER=servicenow_user/DB_USER=servicenow_user/" .env
            sed -i.bak "s/DB_PASSWORD=.*/DB_PASSWORD=/" .env
            sed -i.bak "s/DB_NAME=servicenow_docs/DB_NAME=servicenow_docs/" .env
            
            # Add database type
            echo "DB_TYPE=sqlite" >> .env
        fi
        
        # Clean up backup file
        rm -f .env.bak
        
        print_success "Environment file created with $DB_TYPE configuration!"
    else
        print_status "Environment file already exists"
        
        # Update existing .env file if needed
        if [ "$USE_POSTGRESQL" = true ]; then
            print_status "Updating existing .env file with PostgreSQL settings..."
            sed -i.bak "s/DB_HOST=.*/DB_HOST=$DB_HOST/" .env
            sed -i.bak "s/DB_PORT=.*/DB_PORT=$DB_PORT/" .env
            sed -i.bak "s/DB_NAME=.*/DB_NAME=$DB_NAME/" .env
            sed -i.bak "s/DB_USER=.*/DB_USER=$DB_USER/" .env
            sed -i.bak "s/DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" .env
            sed -i.bak "s/DB_TYPE=.*/DB_TYPE=postgresql/" .env
            
            # Add DB_TYPE if it doesn't exist
            if ! grep -q "DB_TYPE=" .env; then
                echo "DB_TYPE=postgresql" >> .env
            fi
            
            rm -f .env.bak
            print_success "Environment file updated with PostgreSQL settings!"
        fi
    fi
}

# Function to initialize database tables
initialize_database() {
    print_step "Initializing database tables..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run database initialization
    python3 -c "
from database import initialize_database
try:
    db = initialize_database()
    print('✅ Database tables created successfully!')
except Exception as e:
    print(f'⚠️  Database initialization warning: {e}')
    print('The app will still work with SQLite fallback.')
"
}

# Function to check dependencies
check_dependencies() {
    print_step "Checking system dependencies..."
    
    # Check for required commands
    local missing_deps=()
    
    if ! command_exists python3; then
        missing_deps+=("python3")
    fi
    
    if ! command_exists pip3; then
        missing_deps+=("pip3")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        echo "Please install the missing dependencies and run this script again."
        exit 1
    fi
    
    print_success "All dependencies are available!"
}

# Function to start the application
start_application() {
    print_step "Starting ServiceNow Documentation App..."
    
    # Check if port 8506 is already in use
    if port_in_use 8506; then
        print_warning "Port 8506 is already in use. Attempting to free it..."
        
        # Find and kill process using port 8506
        local pid=$(lsof -ti:8506)
        if [ ! -z "$pid" ]; then
            kill -9 $pid
            sleep 2
            print_status "Freed port 8506"
        fi
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start the application
    print_status "Launching Streamlit application..."
    print_success "🎉 ServiceNow Documentation App is starting!"
    echo ""
    echo -e "${GREEN}📱 Application URL: http://localhost:8506${NC}"
    if [ "$USE_POSTGRESQL" = true ]; then
        echo -e "${GREEN}🗄️  Database: PostgreSQL ($DB_HOST:$DB_PORT/$DB_NAME)${NC}"
    else
        echo -e "${GREEN}🗄️  Database: SQLite (local file)${NC}"
    fi
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop the application${NC}"
    echo ""
    
    # Start Streamlit
    streamlit run enhanced_app.py --server.port=8506 --server.address=0.0.0.0 --browser.gatherUsageStats=false
}

# Function to show help
show_help() {
    echo "ServiceNow Advanced Visual Documentation - Startup Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h          Show this help message"
    echo "  --setup-only        Only setup environment, don't start app"
    echo "  --skip-db           Skip database setup (use SQLite)"
    echo "  --skip-env          Skip environment file setup"
    echo "  --force             Force setup even if already configured"
    echo ""
    echo "Database Options:"
    echo "  The script will automatically detect PostgreSQL and offer options:"
    echo "  1. Use existing PostgreSQL installation"
    echo "  2. Install PostgreSQL locally (Ubuntu/Debian/CentOS/macOS)"
    echo "  3. Check database user permissions"
    echo "  4. Create application tables"
    echo "  5. Connect to remote PostgreSQL server"
    echo "  6. Use SQLite (fallback option)"
    echo ""
    echo "Permission Check:"
    echo "  Option 3 allows you to verify if a database user has the necessary"
    echo "  permissions to create tables in a PostgreSQL database."
    echo ""
    echo "Table Creation:"
    echo "  Option 4 allows you to create all necessary application tables"
    echo "  in an existing PostgreSQL database."
    echo ""
    echo "Examples:"
    echo "  $0                  # Full setup with PostgreSQL prompts"
    echo "  $0 --setup-only     # Only setup, don't start"
    echo "  $0 --skip-db        # Skip database setup, use SQLite"
    echo ""
    echo "PostgreSQL Installation:"
    echo "  - Ubuntu/Debian: Uses apt-get"
    echo "  - CentOS/RHEL: Uses yum"
    echo "  - Fedora: Uses dnf"
    echo "  - macOS: Uses Homebrew"
    echo ""
}

# Main function
main() {
    local setup_only=false
    local skip_db=false
    local skip_env=false
    local force=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --setup-only)
                setup_only=true
                shift
                ;;
            --skip-db)
                skip_db=true
                shift
                ;;
            --skip-env)
                skip_env=true
                shift
                ;;
            --force)
                force=true
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # Show header
    print_header
    
    # Check if we're in the right directory
    if [ ! -f "enhanced_app.py" ]; then
        print_error "This script must be run from the ServiceNow documentation project directory"
        print_error "Please navigate to the project directory and run this script again"
        exit 1
    fi
    
    # Check dependencies
    check_dependencies
    
    # Setup Python environment
    setup_python_environment
    
    # Setup database (this sets up database variables)
    if [ "$skip_db" = false ]; then
        setup_database
    else
        # Set default values if skipping database setup
        USE_POSTGRESQL=false
        DB_TYPE="sqlite"
        DB_HOST="localhost"
        DB_PORT="5432"
        DB_NAME="servicenow_docs"
        DB_USER="servicenow_user"
        DB_PASSWORD=""
    fi
    
    # Setup environment file (uses database variables from above)
    if [ "$skip_env" = false ]; then
        setup_environment
    fi
    
    # Initialize database tables
    initialize_database
    
    print_success "🎉 Setup complete! All systems are ready."
    
    if [ "$setup_only" = true ]; then
        print_status "Setup completed. Run '$0' to start the application."
        exit 0
    fi
    
    # Start the application
    start_application
}

# Run main function with all arguments
main "$@"
