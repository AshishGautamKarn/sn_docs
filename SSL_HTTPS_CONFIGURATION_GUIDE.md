# 🔒 SSL/HTTPS Configuration Guide

**Project**: ServiceNow Advanced Visual Documentation  
**Creator**: Ashish Gautam  
**LinkedIn**: https://www.linkedin.com/in/ashishgautamkarn/  
**Guide Date**: September 27, 2025

---

## 🎯 **Overview**

This guide provides multiple options to enable SSL/HTTPS for your ServiceNow documentation platform. Streamlit doesn't natively support SSL, so we'll use reverse proxy solutions for production-grade HTTPS.

---

## 🚀 **Option 1: Nginx Reverse Proxy (Recommended for Production)**

### **Step 1: Install Nginx**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
# or
sudo dnf install nginx

# macOS (with Homebrew)
brew install nginx
```

### **Step 2: Obtain SSL Certificate**

#### **Option A: Let's Encrypt (Free, Production)**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

#### **Option B: Self-Signed Certificate (Development)**
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

### **Step 3: Configure Nginx**

Create `/etc/nginx/sites-available/servicenow-docs`:
```nginx
# HTTP to HTTPS redirect
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$host$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Streamlit Proxy Configuration
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port $server_port;
        
        # WebSocket support for Streamlit
        proxy_buffering off;
        proxy_cache_bypass $http_upgrade;
        
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
```

### **Step 4: Enable Configuration**
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/servicenow-docs /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## 🐳 **Option 2: Docker with Nginx (Containerized)**

### **Step 1: Create SSL-enabled Docker Compose**

Create `docker-compose.ssl.yml`:
```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
    depends_on:
      - servicenow-app
    restart: unless-stopped

  servicenow-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_NAME=${DB_NAME:-sn_docs}
      - DB_USER=${DB_USER:-servicenow_user}
      - DB_PASSWORD=${DB_PASSWORD}
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:13
    environment:
      - POSTGRES_DB=${DB_NAME:-sn_docs}
      - POSTGRES_USER=${DB_USER:-servicenow_user}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### **Step 2: Create Nginx Configuration**

Create `nginx.conf`:
```nginx
events {
    worker_connections 1024;
}

http {
    upstream streamlit {
        server servicenow-app:8501;
    }

    # HTTP to HTTPS redirect
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        return 301 https://$host$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name yourdomain.com www.yourdomain.com;

        # SSL Configuration
        ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
        
        # SSL Security
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;
        
        # Security Headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options DENY always;
        add_header X-Content-Type-Options nosniff always;

        location / {
            proxy_pass http://streamlit;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_buffering off;
        }
    }
}
```

### **Step 3: Deploy with SSL**
```bash
# Start with SSL-enabled Docker Compose
docker-compose -f docker-compose.ssl.yml up -d
```

---

## 🔧 **Option 3: Streamlit with SSL (Development)**

### **Step 1: Generate Self-Signed Certificate**
```bash
# Create SSL directory
mkdir -p ssl

# Generate certificate
openssl req -x509 -newkey rsa:4096 -nodes -out ssl/cert.pem -keyout ssl/key.pem -days 365 -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

### **Step 2: Modify Streamlit Startup**

Create `start_app_ssl.py`:
```python
#!/usr/bin/env python3
"""
SSL-enabled Streamlit startup script
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🔒 Starting ServiceNow Docs with SSL/HTTPS")
    print("=" * 50)
    
    # Check if SSL certificates exist
    cert_file = Path("ssl/cert.pem")
    key_file = Path("ssl/key.pem")
    
    if not cert_file.exists() or not key_file.exists():
        print("❌ SSL certificates not found!")
        print("📄 Please run: ./generate_ssl_cert.sh")
        sys.exit(1)
    
    # Streamlit command with SSL
    cmd = [
        sys.executable, "-m", "streamlit", "run", "enhanced_app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0",
        "--server.sslCertFile=ssl/cert.pem",
        "--server.sslKeyFile=ssl/key.pem",
        "--browser.gatherUsageStats=false",
        "--server.headless=true"
    ]
    
    print("🚀 Starting Streamlit with SSL...")
    print(f"🔗 Access: https://localhost:8501")
    print("⚠️  Note: Self-signed certificate - accept security warning in browser")
    print()
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Created By: Ashish Gautam; LinkedIn: https://www.linkedin.com/in/ashishgautamkarn/
```

### **Step 3: Create SSL Certificate Generator**

Create `generate_ssl_cert.sh`:
```bash
#!/bin/bash

# SSL Certificate Generator for Development
echo "🔒 Generating SSL Certificate for Development"
echo "=============================================="

# Create SSL directory
mkdir -p ssl

# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes \
    -out ssl/cert.pem \
    -keyout ssl/key.pem \
    -days 365 \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

echo "✅ SSL certificate generated successfully!"
echo "📁 Certificate: ssl/cert.pem"
echo "📁 Private Key: ssl/key.pem"
echo "🔗 Valid for: 365 days"
echo ""
echo "🚀 To start with SSL: python3 start_app_ssl.py"
echo "⚠️  Note: Self-signed certificate - accept security warning in browser"
```

---

## 🌐 **Option 4: Cloudflare SSL (Easiest)**

### **Step 1: Setup Cloudflare**
1. Add your domain to Cloudflare
2. Update DNS nameservers
3. Enable SSL/TLS encryption mode: "Full (strict)"

### **Step 2: Configure Origin Server**
```bash
# Install Cloudflare Origin CA
curl -L https://pkg.cloudflare.com/cloudflare-main.gpg | sudo apt-key add -
echo "deb http://pkg.cloudflare.com/ubuntu focal main" | sudo tee /etc/apt/sources.list.d/cloudflare-main.list
sudo apt update
sudo apt install cloudflare-origin-ca
```

### **Step 3: Generate Origin Certificate**
```bash
# Generate certificate for your domain
cloudflare-origin-ca --hostname yourdomain.com --key-file ssl/origin.key --cert-file ssl/origin.pem
```

---

## 🔧 **Option 5: Apache Reverse Proxy**

### **Step 1: Install Apache**
```bash
sudo apt install apache2
sudo a2enmod ssl proxy proxy_http proxy_wstunnel
```

### **Step 2: Configure Virtual Host**

Create `/etc/apache2/sites-available/servicenow-docs.conf`:
```apache
<VirtualHost *:80>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    Redirect permanent / https://yourdomain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName yourdomain.com
    ServerAlias www.yourdomain.com
    
    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/yourdomain.com/cert.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/yourdomain.com/privkey.pem
    SSLCertificateChainFile /etc/letsencrypt/live/yourdomain.com/chain.pem
    
    # Security Headers
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    Header always set X-Frame-Options DENY
    Header always set X-Content-Type-Options nosniff
    
    # Proxy Configuration
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8501/
    ProxyPassReverse / http://127.0.0.1:8501/
    
    # WebSocket Support
    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} websocket [NC]
    RewriteCond %{HTTP:Connection} upgrade [NC]
    RewriteRule ^/?(.*) "ws://127.0.0.1:8501/$1" [P,L]
</VirtualHost>
```

---

## 🚀 **Quick Start Commands**

### **Development (Self-Signed)**
```bash
# Generate SSL certificate
./generate_ssl_cert.sh

# Start with SSL
python3 start_app_ssl.py
```

### **Production (Nginx + Let's Encrypt)**
```bash
# Install Nginx and Certbot
sudo apt install nginx certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Configure Nginx (use config above)
sudo nano /etc/nginx/sites-available/servicenow-docs

# Enable and start
sudo ln -s /etc/nginx/sites-available/servicenow-docs /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### **Docker (SSL-enabled)**
```bash
# Start with SSL-enabled Docker Compose
docker-compose -f docker-compose.ssl.yml up -d
```

---

## 🔒 **Security Best Practices**

### **SSL Configuration**
- Use TLS 1.2+ only
- Enable HSTS (HTTP Strict Transport Security)
- Use strong cipher suites
- Implement perfect forward secrecy

### **Headers**
- Strict-Transport-Security
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block

### **Certificate Management**
- Use Let's Encrypt for production
- Set up automatic renewal
- Monitor certificate expiration
- Use strong key sizes (4096-bit RSA)

---

## 🧪 **Testing SSL Configuration**

### **SSL Labs Test**
```bash
# Test SSL configuration
curl -I https://yourdomain.com
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
```

### **Browser Testing**
- Check HTTPS lock icon
- Verify certificate validity
- Test WebSocket connections
- Validate security headers

---

## 📊 **Performance Considerations**

### **SSL Termination**
- Use reverse proxy for SSL termination
- Offload SSL processing from application
- Enable HTTP/2 for better performance
- Implement connection pooling

### **Caching**
- Cache static assets
- Use CDN for global distribution
- Implement browser caching
- Optimize SSL handshake

---

## 🎯 **Recommendations**

### **Development**
- Use self-signed certificates
- Streamlit with SSL flags
- Local testing only

### **Production**
- Nginx reverse proxy
- Let's Encrypt certificates
- Security headers
- Monitoring and logging

### **Enterprise**
- Load balancer with SSL
- Multiple certificate authorities
- Advanced security policies
- Compliance requirements

---

**Guide Created**: September 27, 2025  
**Creator**: Ashish Gautam  
**LinkedIn**: https://www.linkedin.com/in/ashishgautamkarn/  
**Status**: ✅ **COMPLETE SSL/HTTPS CONFIGURATION GUIDE**
