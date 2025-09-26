# ServiceNow Documentation App - Deployment Guide

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)

**Prerequisites:**
- Docker and Docker Compose installed
- Git (to clone the repository)

**Steps:**
1. Clone or copy the application files to your server
2. Run the automated deployment script:
   ```bash
   ./deploy.sh
   ```
3. Access the application at `http://your-server:8506`

### Option 2: Manual Installation

**Prerequisites:**
- Linux server (Ubuntu/CentOS/RHEL)
- Root access
- Internet connection

**Steps:**
1. Copy the application files to your server
2. Run the installation script as root:
   ```bash
   sudo ./install.sh
   ```
3. Access the application at `http://your-server:8506`

## 📋 Detailed Deployment Options

### 🐳 Docker Deployment

#### Using Docker Compose (Recommended)

1. **Prepare the server:**
   ```bash
   # Install Docker and Docker Compose
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   sudo usermod -aG docker $USER
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

2. **Deploy the application:**
   ```bash
   # Copy application files to server
   scp -r servicenow_docs/ user@your-server:/home/user/
   
   # SSH to server
   ssh user@your-server
   
   # Navigate to application directory
   cd servicenow_docs/
   
   # Configure environment
   cp env.template .env
   nano .env  # Edit configuration
   
   # Deploy
   ./deploy.sh
   ```

3. **Access the application:**
   - URL: `http://your-server-ip:8506`
   - Database: PostgreSQL on port 5432

#### Using Docker only

```bash
# Build the image
docker build -t servicenow-docs .

# Run with external PostgreSQL
docker run -d \
  --name servicenow-app \
  -p 8506:8506 \
  -e DB_HOST=your-postgres-host \
  -e DB_USER=your-db-user \
  -e DB_PASSWORD=your-db-password \
  -e DB_NAME=servicenow_docs \
  servicenow-docs
```

### 🐧 Manual Linux Installation

#### Ubuntu/Debian

1. **Install dependencies:**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib curl git build-essential libpq-dev
   ```

2. **Setup PostgreSQL:**
   ```bash
   sudo -u postgres psql
   CREATE DATABASE servicenow_docs;
   CREATE USER servicenow_user WITH PASSWORD 'YOUR_SECURE_PASSWORD';
   GRANT ALL PRIVILEGES ON DATABASE servicenow_docs TO servicenow_user;
   \q
   ```

3. **Deploy application:**
   ```bash
   # Copy files to /opt/servicenow-docs
   sudo cp -r . /opt/servicenow-docs/
   
   # Create user
   sudo useradd -m servicenow
   sudo chown -R servicenow:servicenow /opt/servicenow-docs
   
   # Setup Python environment
   cd /opt/servicenow-docs
   sudo -u servicenow python3 -m venv venv
   sudo -u servicenow venv/bin/pip install -r requirements.txt
   
   # Configure environment
   sudo -u servicenow cp env.template .env
   sudo -u servicenow nano .env
   
   # Create systemd service
   sudo cp servicenow-app.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable servicenow-app
   sudo systemctl start servicenow-app
   ```

#### CentOS/RHEL/Rocky Linux

1. **Install dependencies:**
   ```bash
   sudo yum update -y
   sudo yum install -y python3 python3-pip postgresql postgresql-server postgresql-devel curl git gcc gcc-c++ make
   sudo postgresql-setup initdb
   sudo systemctl enable postgresql
   sudo systemctl start postgresql
   ```

2. **Follow similar steps as Ubuntu/Debian**

### ☁️ Cloud Deployment

#### AWS EC2

1. **Launch EC2 instance:**
   - AMI: Ubuntu 20.04 LTS or Amazon Linux 2
   - Instance type: t3.medium or larger
   - Security group: Allow ports 22 (SSH), 8506 (App), 5432 (PostgreSQL)

2. **Connect and deploy:**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   # Follow Docker or manual installation steps
   ```

#### Google Cloud Platform

1. **Create VM instance:**
   ```bash
   gcloud compute instances create servicenow-app \
     --image-family=ubuntu-2004-lts \
     --image-project=ubuntu-os-cloud \
     --machine-type=e2-medium \
     --tags=http-server,https-server
   ```

2. **Configure firewall:**
   ```bash
   gcloud compute firewall-rules create allow-servicenow-app \
     --allow tcp:8506 \
     --source-ranges 0.0.0.0/0 \
     --target-tags http-server
   ```

#### Azure

1. **Create VM:**
   ```bash
   az vm create \
     --resource-group myResourceGroup \
     --name servicenow-app \
     --image UbuntuLTS \
     --size Standard_B2s \
     --admin-username azureuser \
     --generate-ssh-keys
   ```

2. **Open port:**
   ```bash
   az vm open-port --port 8506 --resource-group myResourceGroup --name servicenow-app
   ```

## 🔧 Configuration

### Environment Variables

Edit `.env` file with your configuration:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=servicenow_docs
DB_USER=servicenow_user
DB_PASSWORD=your-secure-password

# Scraper Configuration
SCRAPER_TIMEOUT=60
SCRAPER_USE_SELENIUM=false

# Application Configuration
STREAMLIT_SERVER_PORT=8506
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Database Configuration

#### External PostgreSQL Database

1. **Install PostgreSQL on separate server**
2. **Create database and user:**
   ```sql
   CREATE DATABASE servicenow_docs;
   CREATE USER servicenow_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE servicenow_docs TO servicenow_user;
   ```

3. **Update .env file:**
   ```bash
   DB_HOST=your-postgres-server-ip
   DB_PORT=5432
   DB_NAME=servicenow_docs
   DB_USER=servicenow_user
   DB_PASSWORD=secure_password
   ```

#### Using Cloud Database Services

**AWS RDS:**
```bash
DB_HOST=your-rds-endpoint.region.rds.amazonaws.com
DB_PORT=5432
DB_NAME=servicenow_docs
DB_USER=your-rds-username
DB_PASSWORD=your-rds-password
```

**Google Cloud SQL:**
```bash
DB_HOST=your-cloud-sql-ip
DB_PORT=5432
DB_NAME=servicenow_docs
DB_USER=your-cloud-sql-user
DB_PASSWORD=your-cloud-sql-password
```

## 🔒 Security Considerations

### Production Security

1. **Change default passwords**
2. **Use environment variables for secrets**
3. **Enable firewall rules**
4. **Use HTTPS with reverse proxy (Nginx/Apache)**
5. **Regular security updates**

### Reverse Proxy Setup (Nginx)

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8506;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### SSL/HTTPS Setup

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 Monitoring and Maintenance

### Health Checks

```bash
# Check application status
curl http://localhost:8506/_stcore/health

# Check Docker containers
docker-compose ps

# Check systemd service
systemctl status servicenow-app
```

### Logs

```bash
# Docker logs
docker-compose logs -f

# Systemd logs
journalctl -u servicenow-app -f

# Application logs
tail -f logs/app.log
```

### Backup

```bash
# Database backup
pg_dump -h localhost -U servicenow_user servicenow_docs > backup.sql

# Application backup
tar -czf servicenow-app-backup.tar.gz /opt/servicenow-docs/
```

### Updates

```bash
# Docker update
docker-compose pull
docker-compose up --build -d

# Manual update
sudo systemctl stop servicenow-app
# Update code
sudo systemctl start servicenow-app
```

## 🆘 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   sudo lsof -i :8506
   sudo kill -9 <PID>
   ```

2. **Database connection failed:**
   - Check PostgreSQL service: `systemctl status postgresql`
   - Verify credentials in `.env`
   - Check firewall rules

3. **Permission denied:**
   ```bash
   sudo chown -R servicenow:servicenow /opt/servicenow-docs/
   ```

4. **Docker issues:**
   ```bash
   docker-compose down
   docker system prune -a
   docker-compose up --build -d
   ```

### Support

- Check logs for detailed error messages
- Verify all prerequisites are installed
- Ensure ports are open in firewall
- Test database connectivity separately

## 📞 Getting Help

If you encounter issues:

1. Check the logs first
2. Verify your configuration
3. Test database connectivity
4. Check firewall and network settings
5. Review this deployment guide

The application should be accessible at `http://your-server:8506` once deployed successfully.
