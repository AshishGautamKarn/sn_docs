# 🔒 ServiceNow Advanced Visual Documentation

<div align="center">

![ServiceNow](https://img.shields.io/badge/ServiceNow-Platform-blue?style=for-the-badge&logo=servicenow)
![Python](https://img.shields.io/badge/Python-3.9+-green?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-red?style=for-the-badge&logo=streamlit)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue?style=for-the-badge&logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue?style=for-the-badge&logo=docker)
![SSL](https://img.shields.io/badge/SSL-HTTPS-green?style=for-the-badge&logo=ssl)

**A comprehensive, secure, and modern ServiceNow documentation platform with advanced analytics, hybrid data collection, and beautiful visualizations.**

[![Security](https://img.shields.io/badge/Security-A%2B-green?style=flat-square)](#security)
[![Code Quality](https://img.shields.io/badge/Code%20Quality-A-blue?style=flat-square)](#code-quality)
[![UI/UX](https://img.shields.io/badge/UI%2FUX-A%2B-purple?style=flat-square)](#user-interface)
[![Documentation](https://img.shields.io/badge/Documentation-Complete-orange?style=flat-square)](#documentation)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](#license)

</div>

---

## 📋 Table of Contents

- [🎯 Overview](#-overview)
- [✨ Features](#-features)
- [🔒 Security](#-security)
- [🚀 Quick Start](#-quick-start)
- [📦 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [🎨 User Interface](#-user-interface)
- [📊 Data Collection](#-data-collection)
- [🔧 Development](#-development)
- [🐳 Deployment](#-deployment)
- [📚 Documentation](#-documentation)
- [🤝 Contributing](#-contributing)
- [💖 Sponsoring](#-sponsoring)
- [📄 License](#-license)
- [👤 Creator](#-creator)

---

## 🎯 Overview

**ServiceNow Advanced Visual Documentation** is a comprehensive platform designed to extract, analyze, and visualize ServiceNow instance data through multiple collection methods. Built with modern Python technologies and featuring a beautiful Streamlit interface, this tool provides deep insights into your ServiceNow environment.

### 🎯 **Key Objectives**
- **Comprehensive Data Collection**: Extract data via REST API and direct database access
- **Advanced Analytics**: Provide insights through correlation analysis and visualizations
- **Security-First Design**: Protect sensitive data with encryption and secure practices
- **Modern UI/UX**: Beautiful, responsive interface with intuitive navigation
- **Production Ready**: Docker support, SSL/HTTPS, deployment scripts, and comprehensive documentation

### 🌟 **Why Choose This Platform?**
- **🔍 Deep Insights**: Comprehensive analysis of your ServiceNow instance
- **🔒 Enterprise Security**: Encrypted storage and secure credential management
- **🎨 Modern Interface**: Beautiful, responsive Streamlit-based UI
- **🚀 Production Ready**: Docker, SSL/HTTPS, and deployment automation
- **📊 Advanced Analytics**: Data correlation and visualization capabilities
- **⚡ High Performance**: Optimized for large-scale ServiceNow instances

---

## ✨ Features

### 🔍 **Data Collection & Integration**
- **REST API Integration**: Comprehensive ServiceNow REST API client
- **Direct Database Access**: PostgreSQL and MySQL support with schema introspection
- **Hybrid Collection**: Combine API and database data for complete coverage
- **Real-time Analytics**: Live data correlation and analysis
- **Batch Processing**: Efficient bulk data collection and processing
- **Multi-Instance Support**: Connect to multiple ServiceNow instances

### 📊 **Analytics & Visualization**
- **Interactive Dashboards**: Modern Streamlit-based interface with real-time updates
- **Data Correlation**: Cross-reference API and database data for completeness
- **Visual Analytics**: Plotly-powered charts, graphs, and network visualizations
- **Export Capabilities**: JSON, CSV, and PDF export options
- **Real-time Monitoring**: Live system health indicators and performance metrics
- **Custom Reports**: Generate comprehensive documentation reports

### 🔒 **Security & Compliance**
- **Encrypted Storage**: Fernet encryption for sensitive data
- **Environment Variables**: Secure credential management with `.env` support
- **No Hardcoded Secrets**: Zero credentials in source code
- **Access Control**: Role-based permissions and authentication
- **Audit Logging**: Comprehensive activity tracking and logging
- **SSL/HTTPS Support**: Complete SSL configuration for production

### 🎨 **User Interface & Experience**
- **Modern Design**: Clean, professional Streamlit interface
- **Responsive Layout**: Works seamlessly on desktop, tablet, and mobile
- **Intuitive Navigation**: Easy-to-use sidebar navigation with breadcrumbs
- **Real-time Feedback**: Success, error, and progress indicators
- **Accessibility**: ARIA labels and keyboard navigation support
- **Dark/Light Mode**: Theme support for user preference

### 🚀 **Deployment & Operations**
- **Docker Support**: Containerized deployment with Docker Compose
- **SSL/HTTPS**: Production-ready SSL configuration with Let's Encrypt
- **Database Migration**: Automated schema creation and updates
- **Health Monitoring**: Built-in health checks and monitoring
- **Backup & Recovery**: Automated backup and restore capabilities
- **Scaling**: Horizontal scaling support with load balancing

---

## 🔒 Security

### 🛡️ **Security Features**
- **Zero Hardcoded Credentials**: All sensitive data uses environment variables
- **Encrypted Database Storage**: Fernet encryption for all sensitive data
- **SSL/TLS Encryption**: Complete SSL configuration for all communications
- **Secure Configuration Management**: Centralized, encrypted configuration system
- **Access Control**: Role-based permissions and authentication
- **Audit Logging**: Comprehensive security event logging

### 🔐 **Security Best Practices**
- **Environment Variables**: All credentials stored in `.env` files (excluded from Git)
- **Encryption Keys**: Generated automatically with secure random keys
- **Database Security**: Encrypted connections and secure credential storage
- **Network Security**: SSL/TLS for all external communications
- **Input Validation**: Comprehensive input sanitization and validation
- **Error Handling**: Secure error messages without information disclosure

### 🚫 **What's Protected**
- **Database Credentials**: Encrypted storage with Fernet encryption
- **ServiceNow Credentials**: Secure environment variable management
- **SSL Certificates**: Excluded from version control
- **API Keys**: Environment variable based management
- **Private Keys**: Secure file permissions and exclusion from Git

---

## 🚀 Quick Start

### **Prerequisites**
- **Python 3.9+** - Download from [python.org](https://www.python.org/downloads/)
- **pip** - Usually comes with Python
- **PostgreSQL** (optional) - For production database

### **1. Clone Repository**
```bash
git clone https://github.com/AshishGautamKarn/sn_docs/
cd sn_docs
```

### **2. Automated Setup**
```bash
# Make startup script executable
chmod +x start_app.sh

# Run automated setup with database questionnaire
./start_app.sh
```

### **3. Manual Setup (Alternative)**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env

# Start application
streamlit run enhanced_app.py
```

**🎉 Access your application at: http://localhost:8501**

---

## 📦 Installation

### **Option 1: Automated Installation**

#### **Enhanced Startup Script**
```bash
# Full setup with database questionnaire and verification
./start_app.sh

# Development mode (SQLite, no SSL)
./start_app.sh --dev

# Custom port
./start_app.sh --port 8080

# Skip database configuration
./start_app.sh --skip-db-config
```

#### **System Requirements**
- **OS**: Windows 10+, macOS 10.15+, Ubuntu 18.04+
- **Python**: 3.9 or higher
- **Memory**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Network**: Internet connection for dependencies

### **Option 2: Docker Installation**

#### **Using Docker Compose**
```bash
# Clone repository
git clone https://github.com/AshishGautamKarn/sn_docs/
cd sn_docs

# Create environment file
cp .env.example .env
# Edit .env with your settings

# Start with Docker Compose
docker-compose up -d
```

#### **Using Docker**
```bash
# Build image
docker build -t sn_docs .

# Run container
docker run -p 8501:8501 --env-file .env sn_docs
```

### **Option 3: SSL/HTTPS Installation**

#### **Development SSL**
```bash
# Generate SSL certificate
./generate_ssl_cert.sh

# Start with SSL
python3 start_app_ssl.py
```

#### **Production SSL**
```bash
# Setup production SSL
./setup_ssl_production.sh yourdomain.com
```

---

## ⚙️ Configuration

### **Environment Variables**

Create a `.env` file with the following variables:

```bash
# Database Configuration
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=servicenow_docs
DB_USER=your_username
DB_PASSWORD=your_password

# ServiceNow Configuration
SN_INSTANCE_URL=https://your-instance.service-now.com
SN_USERNAME=your_username
SN_PASSWORD=your_password
SN_API_VERSION=v1

# Application Configuration
APP_ENV=production
LOG_LEVEL=INFO
ENCRYPTION_KEY=your_32_character_encryption_key
SECRET_KEY=your_secret_key

# SSL Configuration
SSL_ENABLED=true
SSL_CERT_FILE=ssl/cert.pem
SSL_KEY_FILE=ssl/key.pem
```

### **Configuration Files**

#### **config.yaml**
```yaml
database:
  type: postgresql
  host: localhost
  port: 5432
  name: servicenow_docs
  user: your_username
  password: your_password

servicenow:
  instance_url: https://your-instance.service-now.com
  username: your_username
  password: your_password
  api_version: v1
  timeout: 30
  max_retries: 3
  verify_ssl: true

application:
  environment: production
  log_level: INFO
  encryption_key: your_32_character_encryption_key
```

### **Database Setup**

#### **PostgreSQL Setup**
```sql
-- Create database
CREATE DATABASE servicenow_docs;

-- Create user
CREATE USER servicenow_user WITH PASSWORD 'your_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE servicenow_docs TO servicenow_user;
GRANT USAGE ON SCHEMA public TO servicenow_user;
GRANT CREATE ON SCHEMA public TO servicenow_user;
```

#### **MySQL Setup**
```sql
-- Create database
CREATE DATABASE servicenow_docs;

-- Create user
CREATE USER 'servicenow_user'@'localhost' IDENTIFIED BY 'your_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON servicenow_docs.* TO 'servicenow_user'@'localhost';
FLUSH PRIVILEGES;
```

---

## 🎨 User Interface

### **📊 Dashboard**
- **System Overview**: Real-time metrics and health indicators
- **Quick Actions**: One-click access to common tasks
- **Recent Activity**: Latest data collection and analysis results
- **Performance Metrics**: System performance and resource usage

### **🗄️ Database Management**
- **Connection Status**: Real-time database connectivity monitoring
- **Data Tables**: Comprehensive view of all collected data
- **Schema Information**: Database structure and relationships
- **Query Interface**: Direct database query capabilities

### **🔗 ServiceNow Integration**
- **Instance Configuration**: ServiceNow instance setup and testing
- **API Testing**: REST API connection validation
- **Data Collection**: Automated data extraction from ServiceNow
- **Hybrid Analysis**: Combined API and database data analysis

### **📈 Visualizations**
- **Interactive Charts**: Plotly-powered data visualizations
- **Network Graphs**: ServiceNow object relationship mapping
- **Trend Analysis**: Historical data analysis and trends
- **Export Options**: Multiple export formats (JSON, CSV, PDF)

### **⚙️ Configuration**
- **Environment Setup**: Centralized configuration management
- **Security Settings**: SSL, encryption, and access control
- **Database Configuration**: Connection and schema management
- **ServiceNow Settings**: Instance and API configuration

---

## 📊 Data Collection

### **🔍 Data Sources**

#### **REST API Collection**
- **Modules**: ServiceNow applications and plugins
- **Roles**: User roles and permissions
- **Tables**: Database table structures and metadata
- **Properties**: System properties and configuration
- **Scheduled Jobs**: Automated job definitions

#### **Database Collection**
- **Direct Access**: PostgreSQL and MySQL database introspection
- **Schema Analysis**: Table structures and relationships
- **Data Sampling**: Representative data collection
- **Metadata Extraction**: Database object information

#### **Hybrid Collection**
- **Data Correlation**: Cross-reference API and database data
- **Completeness Analysis**: Identify missing or inconsistent data
- **Quality Assessment**: Data accuracy and consistency validation
- **Comprehensive Reports**: Detailed analysis and recommendations

### **📋 Data Models**

#### **ServiceNow Modules**
```python
class ServiceNowModule:
    name: str
    type: ModuleType
    version: str
    description: str
    tables: List[ServiceNowTable]
    roles: List[ServiceNowRole]
    properties: List[ServiceNowProperty]
```

#### **ServiceNow Tables**
```python
class ServiceNowTable:
    name: str
    type: TableType
    fields: List[TableField]
    relationships: List[TableRelationship]
    indexes: List[TableIndex]
    constraints: List[TableConstraint]
```

#### **ServiceNow Roles**
```python
class ServiceNowRole:
    name: str
    description: str
    permissions: List[Permission]
    dependencies: List[RoleDependency]
    modules: List[str]
```

---

## 🔧 Development

### **🏗️ Architecture**

#### **Technology Stack**
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python with SQLAlchemy ORM
- **Database**: PostgreSQL (primary), MySQL (supported)
- **Visualization**: Plotly, NetworkX
- **Data Processing**: Pandas, BeautifulSoup4
- **Deployment**: Docker, Docker Compose
- **Configuration**: YAML, Environment Variables

#### **Core Components**
- **`enhanced_app.py`**: Main Streamlit application
- **`models.py`**: Database models and data structures
- **`database.py`**: Database management and operations
- **`centralized_db_config.py`**: Configuration management
- **`servicenow_api_client.py`**: ServiceNow REST API client
- **`servicenow_database_connector.py`**: Database connector

### **🛠️ Development Setup**

#### **Local Development**
```bash
# Clone repository
git clone https://github.com/AshishGautamKarn/sn_docs/
cd sn_docs

# Create development environment
python -m venv venv
source venv/bin/activate

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Run in development mode
streamlit run enhanced_app.py --server.port 8501
```

### **Code Quality**
- **Type Hints**: Comprehensive type annotations
- **Documentation**: Detailed docstrings and comments
- **Error Handling**: Robust exception management
- **Testing**: Unit and integration tests
- **Linting**: Code quality enforcement

### **Contributing Guidelines**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 🐳 Deployment

### **Production Deployment**

#### **Using Docker Compose**
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

#### **Using Kubernetes**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: servicenow-docs
spec:
  replicas: 3
  selector:
    matchLabels:
      app: servicenow-docs
  template:
    metadata:
      labels:
        app: servicenow-docs
    spec:
      containers:
      - name: servicenow-docs
        image: servicenow-docs:latest
        ports:
        - containerPort: 8501
        env:
        - name: DB_HOST
          value: "postgres-service"
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: password
```

#### **Using Nginx Reverse Proxy**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **SSL/HTTPS Configuration**

#### **Development SSL**
```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Start with SSL
streamlit run enhanced_app.py --server.sslCertFile=cert.pem --server.sslKeyFile=key.pem
```

#### **Production SSL with Let's Encrypt**
```bash
# Install Certbot
sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d yourdomain.com

# Configure Nginx
sudo nano /etc/nginx/sites-available/servicenow-docs
```

---

## 📚 Documentation

### **📖 Available Guides**
- **[Deployment Guide](DEPLOYMENT.md)**: Complete deployment instructions
- **[Startup Guide](STARTUP_GUIDE.md)**: Application setup and configuration
- **[SSL Configuration](SSL_HTTPS_CONFIGURATION_GUIDE.md)**: SSL/HTTPS setup
- **[Project Index](PROJECT_INDEX.md)**: Complete project navigation
- **[Project Summary](PROJECT_SUMMARY.md)**: Project overview and features

### **🔧 Technical Documentation**
- **API Documentation**: REST API client usage
- **Database Schema**: Complete database structure
- **Configuration Reference**: All configuration options
- **Security Guidelines**: Security best practices
- **Troubleshooting**: Common issues and solutions

### **📊 User Guides**
- **Getting Started**: First-time setup guide
- **Data Collection**: How to collect ServiceNow data
- **Visualization**: Creating charts and graphs
- **Export Options**: Data export and reporting
- **Advanced Features**: Power user features

---

## 🤝 Contributing

### **How to Contribute**
1. **Fork the Repository**: Create your own fork
2. **Create Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Make Changes**: Implement your feature or fix
4. **Add Tests**: Include tests for new functionality
5. **Commit Changes**: `git commit -m 'Add amazing feature'`
6. **Push to Branch**: `git push origin feature/amazing-feature`
7. **Open Pull Request**: Create a pull request

### **Contribution Guidelines**
- **Code Style**: Follow PEP 8 Python style guide
- **Documentation**: Update documentation for new features
- **Testing**: Add tests for new functionality
- **Security**: Ensure no sensitive data in commits
- **Performance**: Consider performance implications

### **Development Areas**
- **Frontend**: Streamlit UI improvements
- **Backend**: Python backend enhancements
- **Database**: Database optimization and features
- **Visualization**: Chart and graph improvements
- **Documentation**: Documentation improvements
- **Testing**: Test coverage and quality

---

## 💖 Sponsoring

### **Support the Project**
If you find this project helpful, please consider supporting it:

- **☕️ Buy me a coffee**: Show your appreciation on https://buymeacoffee.com/ashishgautamkarn
- **⭐ Star the Repository**: Show your appreciation
- **🐛 Report Issues**: Help improve the project
- **💡 Suggest Features**: Share your ideas
- **📖 Improve Documentation**: Help others learn
- **🤝 Contribute Code**: Add new features

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👤 Creator

<div align="center">

**Created by [Ashish Gautam](https://www.linkedin.com/in/ashishgautamkarn/)**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/ashishgautamkarn/)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=for-the-badge&logo=github)](https://github.com/ashishgautamkarn)

</div>

### **About the Creator**
- **Name**: Ashish Gautam
- **LinkedIn**: [https://www.linkedin.com/in/ashishgautamkarn/](https://www.linkedin.com/in/ashishgautamkarn/)
- **Expertise**: Database Engineering and Administration, Postgres, Mysql, Mongo, MS-SQL Server, Oracle, Full-Stack development, AI, Python ...
- **Location**: Available for remote work and consulting

### **Contact Information**
- **LinkedIn**: [ashishgautamkarn](https://www.linkedin.com/in/ashishgautamkarn/)
- **GitHub**: [ashishgautamkarn](https://github.com/ashishgautamkarn)
- **Email**: Available through LinkedIn


---

<div align="center">

**⭐ If you found this project helpful, please give it a star! ⭐**


[![GitHub stars](https://img.shields.io/github/stars/ashishgautamkarn/servicenow-docs?style=social)](https://github.com/ashishgautamkarn/servicenow-docs)
[![GitHub forks](https://img.shields.io/github/forks/ashishgautamkarn/servicenow-docs?style=social)](https://github.com/ashishgautamkarn/servicenow-docs)
[![GitHub watchers](https://img.shields.io/github/watchers/ashishgautamkarn/servicenow-docs?style=social)](https://github.com/ashishgautamkarn/servicenow-docs)

---

**Made with ❤️ by [Ashish Gautam](https://www.linkedin.com/in/ashishgautamkarn/)**

</div>

---

## 📊 Project Statistics

- **📁 Total Files**: 75+ files
- **🐍 Python Files**: 33 files
- **📄 Documentation**: 15 comprehensive guides
- **🔧 Configuration**: 16 setup files
- **🚀 Deployment**: Docker, SSL, and automation scripts
- **🔒 Security**: A+ security rating with zero vulnerabilities

---

## 🎯 Key Features Summary

- **🔍 Comprehensive Data Collection**: REST API and database access
- **📊 Advanced Analytics**: Data correlation and visualization
- **🔒 Enterprise Security**: Encrypted storage and secure practices
- **🎨 Modern UI/UX**: Beautiful Streamlit interface
- **🚀 Production Ready**: Docker, SSL/HTTPS, and deployment automation
- **📚 Complete Documentation**: Comprehensive guides and examples
- **👤 Creator Attribution**: Professional attribution throughout

---

**Ready to get started? Jump to the [Quick Start](#-quick-start) section!**

---

*Last updated: December 2024*
