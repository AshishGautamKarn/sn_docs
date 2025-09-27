# ServiceNow Documentation App - Package Contents

This package contains everything needed to deploy the ServiceNow Documentation App on another server.

## 📦 Package Contents

### Core Application Files
- `enhanced_app.py` - Main Streamlit application
- `database.py` - Database models and management
- `models.py` - Data models
- `config.py` - Configuration management
- `requirements.txt` - Python dependencies
- `comprehensive_servicenow_scraper.py` - Data generation scraper
- `comprehensive_scraper_ui.py` - Scraper UI
- `interactive_visualizer.py` - Interactive visualizations
- `database_introspection_ui.py` - Database introspection UI
- `servicenow_api_client.py` - ServiceNow REST API client
- `servicenow_instance_introspection_ui.py` - ServiceNow instance introspection UI

### Deployment Files
- `Dockerfile` - Docker container configuration
- `docker-compose.yml` - Docker Compose configuration
- `deploy.sh` - Automated Docker deployment script
- `install.sh` - Manual Linux installation script
- `servicenow-app.service` - Systemd service configuration
- `env.template` - Environment configuration template

### Utility Scripts
- `backup.sh` - Database and application backup script
- `update.sh` - Application update script

### Documentation
- `DEPLOYMENT.md` - Comprehensive deployment guide
- `README.md` - Application documentation

## 🚀 Quick Deployment Options

### Option 1: Docker (Recommended)
```bash
# Copy files to server
scp -r sn_docs/ user@your-server:/home/user/

# SSH to server
ssh user@your-server
cd sn_docs/

# Deploy with Docker
./deploy.sh
```

### Option 2: Manual Installation
```bash
# Copy files to server
scp -r sn_docs/ root@your-server:/tmp/

# SSH to server as root
ssh root@your-server
cd /tmp/sn_docs/

# Install manually
./install.sh
```

## 🔧 Configuration

1. **Edit environment file:**
   ```bash
   cp env.template .env
   nano .env
   ```

2. **Key configuration options:**
   - Database connection settings
   - Scraper timeout settings
   - Application port and address

## 📊 Features

- **Comprehensive Scraper**: Generate ServiceNow data
- **Interactive Visualizations**: Explore modules, tables, roles
- **Database Introspection**: Connect to external ServiceNow databases
- **ServiceNow Instance Introspection**: Connect to live ServiceNow instances via REST API
- **Database Management**: View statistics, manage data

## 🌐 Access

Once deployed, access the application at:
- **URL**: `http://your-server:8506`
- **Database**: PostgreSQL on port 5432

## 📞 Support

For deployment issues:
1. Check the `DEPLOYMENT.md` guide
2. Review logs: `docker-compose logs` or `journalctl -u servicenow-app -f`
3. Verify configuration in `.env` file
4. Test database connectivity

## 🔒 Security Notes

- Change default passwords in production
- Use environment variables for secrets
- Configure firewall rules
- Consider using HTTPS with reverse proxy
- Regular security updates recommended
