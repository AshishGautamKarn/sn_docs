#!/bin/bash

# PostgreSQL Permissions Fix Script
# Fixes permission issues for existing databases

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}🔧 PostgreSQL Permissions Fix${NC}"
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

# Function to find psql command
find_psql() {
    if command_exists psql; then
        echo "psql"
    elif [ -f "/opt/homebrew/opt/postgresql@15/bin/psql" ]; then
        echo "/opt/homebrew/opt/postgresql@15/bin/psql"
    elif [ -f "/opt/homebrew/bin/psql" ]; then
        echo "/opt/homebrew/bin/psql"
    elif [ -f "/usr/local/bin/psql" ]; then
        echo "/usr/local/bin/psql"
    elif [ -f "/usr/bin/psql" ]; then
        echo "/usr/bin/psql"
    else
        echo ""
    fi
}

# Function to fix permissions
fix_permissions() {
    local host=$1
    local port=$2
    local database=$3
    local username=$4
    local password=$5
    
    print_status "Fixing permissions for user '$username' on database '$database'..."
    
    # Find psql command
    PSQL_CMD=$(find_psql)
    if [ -z "$PSQL_CMD" ]; then
        print_error "psql command not found"
        return 1
    fi
    
    print_status "Using psql from: $PSQL_CMD"
    
    # Grant comprehensive permissions
    print_status "Granting database privileges..."
    PGPASSWORD="$password" "$PSQL_CMD" -h "$host" -p "$port" -U postgres -d "$database" << EOF
-- Grant schema privileges
GRANT ALL PRIVILEGES ON SCHEMA public TO $username;

-- Grant privileges on existing tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $username;

-- Grant privileges on existing sequences
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $username;

-- Grant privileges on existing functions
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO $username;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO $username;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO $username;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON FUNCTIONS TO $username;

-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO $username;

-- Make user owner of public schema (if needed)
-- ALTER SCHEMA public OWNER TO $username;
EOF
    
    if [ $? -eq 0 ]; then
        print_success "Permissions granted successfully!"
        return 0
    else
        print_error "Failed to grant permissions"
        return 1
    fi
}

# Function to test permissions
test_permissions() {
    local host=$1
    local port=$2
    local database=$3
    local username=$4
    local password=$5
    
    print_status "Testing permissions..."
    
    PSQL_CMD=$(find_psql)
    
    # Test basic connection
    if PGPASSWORD="$password" "$PSQL_CMD" -h "$host" -p "$port" -U "$username" -d "$database" -c "SELECT 1;" >/dev/null 2>&1; then
        print_success "Basic connection successful!"
    else
        print_error "Basic connection failed"
        return 1
    fi
    
    # Test table access
    if PGPASSWORD="$password" "$PSQL_CMD" -h "$host" -p "$port" -U "$username" -d "$database" -c "SELECT count(*) FROM servicenow_modules;" >/dev/null 2>&1; then
        print_success "Table access successful!"
    else
        print_warning "Table access failed - may need additional permissions"
    fi
    
    # Test table creation
    if PGPASSWORD="$password" "$PSQL_CMD" -h "$host" -p "$port" -U "$username" -d "$database" -c "CREATE TABLE test_permissions (id SERIAL PRIMARY KEY); DROP TABLE test_permissions;" >/dev/null 2>&1; then
        print_success "Table creation/deletion successful!"
    else
        print_warning "Table creation failed - may need CREATE privileges"
    fi
    
    return 0
}

# Function to provide manual fix instructions
provide_manual_instructions() {
    print_status "Manual fix instructions:"
    echo ""
    echo "1. Connect as postgres superuser:"
    echo "   psql -h localhost -U postgres -d servicenow_docs"
    echo ""
    echo "2. Grant permissions:"
    echo "   GRANT ALL PRIVILEGES ON SCHEMA public TO servicenow_user;"
    echo "   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO servicenow_user;"
    echo "   GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO servicenow_user;"
    echo "   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO servicenow_user;"
    echo ""
    echo "3. Test connection:"
    echo "   psql -h localhost -U servicenow_user -d servicenow_docs -c \"SELECT count(*) FROM servicenow_modules;\""
    echo ""
}

# Main function
main() {
    print_header
    
    # Get connection details
    read -p "PostgreSQL Host [localhost]: " HOST
    HOST=${HOST:-localhost}
    
    read -p "PostgreSQL Port [5432]: " PORT
    PORT=${PORT:-5432}
    
    read -p "Database Name [servicenow_docs]: " DATABASE
    DATABASE=${DATABASE:-servicenow_docs}
    
    read -p "Username [servicenow_user]: " USERNAME
    USERNAME=${USERNAME:-servicenow_user}
    
    read -s -p "Password: " PASSWORD
    echo ""
    
    echo ""
    
    # Test current permissions
    print_status "Testing current permissions..."
    if test_permissions "$HOST" "$PORT" "$DATABASE" "$USERNAME" "$PASSWORD"; then
        print_success "Permissions are working correctly!"
        exit 0
    fi
    
    echo ""
    
    # Ask for postgres superuser password
    read -s -p "PostgreSQL superuser (postgres) password: " POSTGRES_PASSWORD
    echo ""
    
    # Fix permissions
    if fix_permissions "$HOST" "$PORT" "$DATABASE" "$USERNAME" "$POSTGRES_PASSWORD"; then
        print_success "Permissions fixed successfully!"
        
        # Test again
        echo ""
        if test_permissions "$HOST" "$PORT" "$DATABASE" "$USERNAME" "$PASSWORD"; then
            print_success "All permissions are now working correctly!"
            echo ""
            print_status "You can now run the startup script:"
            echo "  ./start_app.sh"
        else
            print_warning "Some permissions may still need manual adjustment"
            provide_manual_instructions
        fi
    else
        print_error "Failed to fix permissions"
        provide_manual_instructions
    fi
}

# Run main function
main "$@"
