#!/bin/bash

# Quick Fix for Homebrew PostgreSQL PATH Issue
# Adds PostgreSQL to PATH and creates symlinks

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}🔧 Homebrew PostgreSQL PATH Fix${NC}"
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

# Function to add PostgreSQL to PATH
add_postgresql_to_path() {
    print_status "Adding PostgreSQL to PATH..."
    
    # Find PostgreSQL installation
    POSTGRES_PATH=""
    if [ -d "/opt/homebrew/opt/postgresql@15" ]; then
        POSTGRES_PATH="/opt/homebrew/opt/postgresql@15/bin"
        print_status "Found PostgreSQL@15 at: $POSTGRES_PATH"
    elif [ -d "/opt/homebrew/opt/postgresql" ]; then
        POSTGRES_PATH="/opt/homebrew/opt/postgresql/bin"
        print_status "Found PostgreSQL at: $POSTGRES_PATH"
    elif [ -d "/usr/local/opt/postgresql" ]; then
        POSTGRES_PATH="/usr/local/opt/postgresql/bin"
        print_status "Found PostgreSQL at: $POSTGRES_PATH"
    else
        print_error "PostgreSQL installation not found"
        return 1
    fi
    
    # Add to PATH in current session
    export PATH="$POSTGRES_PATH:$PATH"
    print_success "Added PostgreSQL to PATH for current session"
    
    # Add to shell profile
    SHELL_PROFILE=""
    if [ -f "$HOME/.zshrc" ]; then
        SHELL_PROFILE="$HOME/.zshrc"
    elif [ -f "$HOME/.bash_profile" ]; then
        SHELL_PROFILE="$HOME/.bash_profile"
    elif [ -f "$HOME/.bashrc" ]; then
        SHELL_PROFILE="$HOME/.bashrc"
    fi
    
    if [ -n "$SHELL_PROFILE" ]; then
        print_status "Adding PostgreSQL to $SHELL_PROFILE..."
        
        # Check if already added
        if ! grep -q "postgresql.*bin" "$SHELL_PROFILE"; then
            echo "" >> "$SHELL_PROFILE"
            echo "# PostgreSQL PATH" >> "$SHELL_PROFILE"
            echo "export PATH=\"$POSTGRES_PATH:\$PATH\"" >> "$SHELL_PROFILE"
            print_success "Added PostgreSQL to $SHELL_PROFILE"
        else
            print_status "PostgreSQL already in $SHELL_PROFILE"
        fi
    fi
    
    return 0
}

# Function to create symlinks
create_symlinks() {
    print_status "Creating symlinks for PostgreSQL commands..."
    
    # Find PostgreSQL installation
    POSTGRES_PATH=""
    if [ -d "/opt/homebrew/opt/postgresql@15" ]; then
        POSTGRES_PATH="/opt/homebrew/opt/postgresql@15/bin"
    elif [ -d "/opt/homebrew/opt/postgresql" ]; then
        POSTGRES_PATH="/opt/homebrew/opt/postgresql/bin"
    elif [ -d "/usr/local/opt/postgresql" ]; then
        POSTGRES_PATH="/usr/local/opt/postgresql/bin"
    else
        print_error "PostgreSQL installation not found"
        return 1
    fi
    
    # Create symlinks in /usr/local/bin
    if [ -d "/usr/local/bin" ]; then
        if [ -f "$POSTGRES_PATH/psql" ] && [ ! -f "/usr/local/bin/psql" ]; then
            sudo ln -s "$POSTGRES_PATH/psql" "/usr/local/bin/psql"
            print_success "Created symlink: /usr/local/bin/psql"
        fi
        
        if [ -f "$POSTGRES_PATH/pg_dump" ] && [ ! -f "/usr/local/bin/pg_dump" ]; then
            sudo ln -s "$POSTGRES_PATH/pg_dump" "/usr/local/bin/pg_dump"
            print_success "Created symlink: /usr/local/bin/pg_dump"
        fi
        
        if [ -f "$POSTGRES_PATH/pg_restore" ] && [ ! -f "/usr/local/bin/pg_restore" ]; then
            sudo ln -s "$POSTGRES_PATH/pg_restore" "/usr/local/bin/pg_restore"
            print_success "Created symlink: /usr/local/bin/pg_restore"
        fi
    fi
    
    return 0
}

# Function to test PostgreSQL connection
test_postgresql() {
    print_status "Testing PostgreSQL connection..."
    
    # Find psql command
    PSQL_CMD=""
    if command_exists psql; then
        PSQL_CMD="psql"
        print_success "Found psql in PATH: $(which psql)"
    else
        # Try to find psql in common locations
        if [ -f "/opt/homebrew/opt/postgresql@15/bin/psql" ]; then
            PSQL_CMD="/opt/homebrew/opt/postgresql@15/bin/psql"
        elif [ -f "/opt/homebrew/bin/psql" ]; then
            PSQL_CMD="/opt/homebrew/bin/psql"
        elif [ -f "/usr/local/bin/psql" ]; then
            PSQL_CMD="/usr/local/bin/psql"
        else
            print_error "psql command not found"
            return 1
        fi
        print_status "Using psql from: $PSQL_CMD"
    fi
    
    # Test connection
    if "$PSQL_CMD" --version >/dev/null 2>&1; then
        print_success "PostgreSQL client is working!"
        "$PSQL_CMD" --version
        return 0
    else
        print_error "PostgreSQL client test failed"
        return 1
    fi
}

# Function to provide manual instructions
provide_manual_instructions() {
    print_status "Manual instructions for adding PostgreSQL to PATH:"
    echo ""
    echo "1. Add to your shell profile (~/.zshrc or ~/.bash_profile):"
    echo "   export PATH=\"/opt/homebrew/opt/postgresql@15/bin:\$PATH\""
    echo ""
    echo "2. Reload your shell:"
    echo "   source ~/.zshrc"
    echo "   # or"
    echo "   source ~/.bash_profile"
    echo ""
    echo "3. Test PostgreSQL:"
    echo "   psql --version"
    echo ""
    echo "4. Or use the full path:"
    echo "   /opt/homebrew/opt/postgresql@15/bin/psql"
}

# Main function
main() {
    print_header
    
    # Check if we're on macOS
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This script is for macOS with Homebrew PostgreSQL"
        exit 1
    fi
    
    # Check if Homebrew is installed
    if ! command_exists brew; then
        print_error "Homebrew not found. Please install Homebrew first."
        exit 1
    fi
    
    print_status "Detected macOS with Homebrew"
    
    # Add PostgreSQL to PATH
    if add_postgresql_to_path; then
        print_success "PostgreSQL added to PATH"
    else
        print_warning "Failed to add PostgreSQL to PATH"
    fi
    
    # Create symlinks
    if create_symlinks; then
        print_success "Symlinks created"
    else
        print_warning "Failed to create symlinks"
    fi
    
    # Test PostgreSQL
    if test_postgresql; then
        print_success "PostgreSQL is working correctly!"
        echo ""
        print_status "You can now run the startup script:"
        echo "  ./start_app.sh"
    else
        print_warning "PostgreSQL test failed"
        provide_manual_instructions
    fi
}

# Run main function
main "$@"
