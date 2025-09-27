#!/bin/bash

# SSL Certificate Generator for Development
# ServiceNow Advanced Visual Documentation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🔒 SSL Certificate Generator${NC}"
echo -e "${PURPLE}============================${NC}"
echo ""

# Check if OpenSSL is installed
if ! command -v openssl &> /dev/null; then
    echo -e "${RED}❌ OpenSSL is not installed!${NC}"
    echo -e "${YELLOW}📦 Installing OpenSSL...${NC}"
    
    # Install OpenSSL based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command -v brew &> /dev/null; then
            brew install openssl
        else
            echo -e "${RED}❌ Please install Homebrew first: https://brew.sh/${NC}"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y openssl
        elif command -v yum &> /dev/null; then
            sudo yum install -y openssl
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y openssl
        else
            echo -e "${RED}❌ Please install OpenSSL manually${NC}"
            exit 1
        fi
    else
        echo -e "${RED}❌ Unsupported operating system${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ OpenSSL is available${NC}"

# Create SSL directory
echo -e "${BLUE}📁 Creating SSL directory...${NC}"
mkdir -p ssl

# Check if certificates already exist
if [ -f "ssl/cert.pem" ] && [ -f "ssl/key.pem" ]; then
    echo -e "${YELLOW}⚠️  SSL certificates already exist!${NC}"
    echo -e "${CYAN}📄 Certificate: ssl/cert.pem${NC}"
    echo -e "${CYAN}📄 Private Key: ssl/key.pem${NC}"
    echo ""
    read -p "Do you want to regenerate them? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}✅ Using existing certificates${NC}"
        exit 0
    fi
fi

echo -e "${BLUE}🔧 Generating SSL certificate...${NC}"

# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes \
    -out ssl/cert.pem \
    -keyout ssl/key.pem \
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
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem

echo ""
echo -e "${GREEN}✅ SSL certificate generated successfully!${NC}"
echo ""
echo -e "${CYAN}📁 Certificate: ssl/cert.pem${NC}"
echo -e "${CYAN}📁 Private Key: ssl/key.pem${NC}"
echo -e "${CYAN}🔗 Valid for: 365 days${NC}"
echo -e "${CYAN}🌐 Subject: localhost${NC}"
echo ""
echo -e "${YELLOW}🚀 Next steps:${NC}"
echo -e "${YELLOW}   1. Start with SSL: python3 start_app_ssl.py${NC}"
echo -e "${YELLOW}   2. Access: https://localhost:8501${NC}"
echo -e "${YELLOW}   3. Accept security warning in browser${NC}"
echo ""
echo -e "${BLUE}⚠️  Note: This is a self-signed certificate for development only${NC}"
echo -e "${BLUE}   For production, use Let's Encrypt or a trusted CA${NC}"

# Created By: Ashish Gautam; LinkedIn: https://www.linkedin.com/in/ashishgautamkarn/
