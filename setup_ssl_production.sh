#!/bin/bash

# Production SSL Setup Script
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

echo -e "${PURPLE}🔒 Production SSL Setup${NC}"
echo -e "${PURPLE}======================${NC}"
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    echo -e "${RED}❌ This script should not be run as root${NC}"
    echo -e "${YELLOW}💡 Run as regular user, sudo will be used when needed${NC}"
    exit 1
fi

# Check if domain is provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}📝 Usage: $0 <domain-name>${NC}"
    echo -e "${CYAN}Example: $0 servicenow-docs.example.com${NC}"
    exit 1
fi

DOMAIN=$1
echo -e "${BLUE}🌐 Domain: ${DOMAIN}${NC}"
echo ""

# Check if Nginx is installed
if ! command -v nginx &> /dev/null; then
    echo -e "${BLUE}📦 Installing Nginx...${NC}"
    sudo apt update
    sudo apt install -y nginx
    sudo systemctl enable nginx
    sudo systemctl start nginx
    echo -e "${GREEN}✅ Nginx installed${NC}"
else
    echo -e "${GREEN}✅ Nginx is already installed${NC}"
fi

# Check if Certbot is installed
if ! command -v certbot &> /dev/null; then
    echo -e "${BLUE}📦 Installing Certbot...${NC}"
    sudo apt install -y certbot python3-certbot-nginx
    echo -e "${GREEN}✅ Certbot installed${NC}"
else
    echo -e "${GREEN}✅ Certbot is already installed${NC}"
fi

# Create Nginx configuration
echo -e "${BLUE}📝 Creating Nginx configuration...${NC}"
sudo tee /etc/nginx/sites-available/servicenow-docs > /dev/null <<EOF
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};
    return 301 https://\$host\$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name ${DOMAIN} www.${DOMAIN};

    # SSL Configuration (will be updated by Certbot)
    ssl_certificate /etc/letsencrypt/live/${DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${DOMAIN}/privkey.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Streamlit Proxy Configuration
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;
        
        # WebSocket support for Streamlit
        proxy_buffering off;
        proxy_cache_bypass \$http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        proxy_pass http://127.0.0.1:8501;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable the site
echo -e "${BLUE}🔗 Enabling site...${NC}"
sudo ln -sf /etc/nginx/sites-available/servicenow-docs /etc/nginx/sites-enabled/

# Remove default site
sudo rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
echo -e "${BLUE}🧪 Testing Nginx configuration...${NC}"
sudo nginx -t

# Reload Nginx
echo -e "${BLUE}🔄 Reloading Nginx...${NC}"
sudo systemctl reload nginx

# Obtain SSL certificate
echo -e "${BLUE}🔒 Obtaining SSL certificate from Let's Encrypt...${NC}"
echo -e "${YELLOW}⚠️  Make sure your domain ${DOMAIN} points to this server!${NC}"
echo ""

read -p "Press Enter to continue with SSL certificate generation..."

sudo certbot --nginx -d ${DOMAIN} -d www.${DOMAIN} --non-interactive --agree-tos --email admin@${DOMAIN}

# Set up automatic renewal
echo -e "${BLUE}🔄 Setting up automatic certificate renewal...${NC}"
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet && systemctl reload nginx") | crontab -

# Final Nginx reload
sudo systemctl reload nginx

echo ""
echo -e "${GREEN}🎉 SSL setup completed successfully!${NC}"
echo ""
echo -e "${CYAN}📊 Summary:${NC}"
echo -e "${CYAN}  • Domain: ${DOMAIN}${NC}"
echo -e "${CYAN}  • SSL Certificate: Let's Encrypt${NC}"
echo -e "${CYAN}  • HTTPS: https://${DOMAIN}${NC}"
echo -e "${CYAN}  • Auto-renewal: Enabled${NC}"
echo ""
echo -e "${YELLOW}🚀 Next steps:${NC}"
echo -e "${YELLOW}  1. Start your Streamlit app: python3 enhanced_app.py${NC}"
echo -e "${YELLOW}  2. Access: https://${DOMAIN}${NC}"
echo -e "${YELLOW}  3. Test SSL: https://www.ssllabs.com/ssltest/${NC}"
echo ""
echo -e "${BLUE}📚 For more information, see: SSL_HTTPS_CONFIGURATION_GUIDE.md${NC}"

# Created By: Ashish Gautam; LinkedIn: https://www.linkedin.com/in/ashishgautamkarn/
