#!/bin/bash

# ServiceNow Documentation App - Deployment Script
# This script automates the deployment process

set -e

echo "🚀 ServiceNow Documentation App - Deployment Script"
echo "=================================================="

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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

print_status "Docker and Docker Compose are available"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs data

# Set proper permissions
chmod 755 logs data

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from template..."
    cp env.template .env
    print_warning "Please edit .env file with your configuration before continuing"
    print_warning "Run: nano .env"
    read -p "Press Enter after you've configured the .env file..."
fi

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    print_success "Environment variables loaded"
else
    print_error ".env file not found"
    exit 1
fi

# Build and start services
print_status "Building and starting services with Docker Compose..."
docker-compose up --build -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    print_success "Services are running!"
    
    # Show service status
    echo ""
    print_status "Service Status:"
    docker-compose ps
    
    # Show access information
    echo ""
    print_success "🎉 Deployment Complete!"
    echo ""
    echo "📱 Application URL: http://localhost:8506"
    echo "🗄️  Database: PostgreSQL on localhost:5432"
    echo "📊 Database Name: ${DB_NAME:-servicenow_docs}"
    echo ""
    echo "📝 Useful Commands:"
    echo "  View logs: docker-compose logs -f"
    echo "  Stop services: docker-compose down"
    echo "  Restart services: docker-compose restart"
    echo "  Update application: docker-compose up --build -d"
    echo ""
    
else
    print_error "Services failed to start. Check logs with: docker-compose logs"
    exit 1
fi
