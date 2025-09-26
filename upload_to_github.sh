#!/bin/bash

# GitHub Upload Script for ServiceNow Documentation System
# This script helps prepare and upload the project to GitHub

set -e

echo "🚀 ServiceNow Documentation System - GitHub Upload Helper"
echo "========================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if git is installed
if ! command -v git &> /dev/null; then
    print_error "Git is not installed. Please install git first."
    exit 1
fi

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_status "Initializing git repository..."
    git init
    print_success "Git repository initialized"
else
    print_status "Git repository already exists"
fi

# Check for sensitive files
print_status "Checking for sensitive files..."

SENSITIVE_FILES=(
    ".env"
    ".env.backup"
    "config.local.yaml"
    "secrets.yaml"
    "credentials.yaml"
)

for file in "${SENSITIVE_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_warning "Found sensitive file: $file"
        if [ "$file" = ".env" ]; then
            print_status "Creating .env.example from .env..."
            # Create .env.example by removing actual values
            sed 's/=.*/=your_value_here/' .env > .env.example
            print_success ".env.example created"
        fi
    fi
done

# Check .gitignore
if [ ! -f ".gitignore" ]; then
    print_error ".gitignore file not found. Please create one first."
    exit 1
fi

print_success ".gitignore file found"

# Show what files will be added
print_status "Files that will be added to git:"
git add --dry-run . | grep -E "^(add|create)" | head -20

if [ $(git add --dry-run . | grep -E "^(add|create)" | wc -l) -gt 20 ]; then
    echo "... and more files"
fi

# Ask for confirmation
echo
read -p "Do you want to proceed with adding these files? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_status "Upload cancelled by user"
    exit 0
fi

# Add files
print_status "Adding files to git..."
git add .

# Check status
print_status "Git status:"
git status --short

# Ask for commit message
echo
read -p "Enter commit message (or press Enter for default): " commit_message
if [ -z "$commit_message" ]; then
    commit_message="Initial commit: ServiceNow Advanced Visual Documentation System

- Complete Streamlit-based documentation system
- Dynamic credential handling and security
- Multi-database configuration support
- ServiceNow API integration
- Interactive data visualization
- Comprehensive scraping capabilities
- Docker deployment support"
fi

# Commit
print_status "Creating commit..."
git commit -m "$commit_message"
print_success "Commit created successfully"

# Ask about remote repository
echo
print_status "Next steps:"
echo "1. Create a new repository on GitHub"
echo "2. Copy the repository URL"
echo "3. Run the following commands:"
echo
echo "   git remote add origin <YOUR_REPO_URL>"
echo "   git branch -M main"
echo "   git push -u origin main"
echo

read -p "Do you want to add a remote repository now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Enter your GitHub repository URL: " repo_url
    if [ ! -z "$repo_url" ]; then
        print_status "Adding remote repository..."
        git remote add origin "$repo_url"
        print_success "Remote repository added"
        
        print_status "Setting main branch..."
        git branch -M main
        
        print_status "Pushing to GitHub..."
        git push -u origin main
        print_success "Successfully pushed to GitHub!"
        
        echo
        print_success "🎉 Your ServiceNow Documentation System is now on GitHub!"
        print_status "Repository URL: $repo_url"
    else
        print_error "No repository URL provided"
    fi
fi

echo
print_success "GitHub upload preparation complete!"
print_status "Check GITHUB_UPLOAD_GUIDE.md for detailed instructions"
