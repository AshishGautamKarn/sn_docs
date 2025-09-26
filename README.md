# 🚀 ServiceNow Advanced Visual Documentation System

A comprehensive web application built with Streamlit that provides advanced data scraping, visualization, and management capabilities for ServiceNow instances. This system enables users to extract, analyze, and visualize ServiceNow data including modules, roles, tables, properties, and scheduled jobs.

**Creator**: [Ashish Gautam](https://www.linkedin.com/in/ashishgautamkarn/)  
**GitHub**: [https://github.com/AshishGautamKarn/servicenow_docs](https://github.com/AshishGautamKarn/servicenow_docs)

---

## 📋 **Table of Contents**

- [🎯 Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [📦 Installation](#-installation)
- [🚀 Quick Start](#-quick-start)
- [🔧 Configuration](#-configuration)
- [📊 Usage Guide](#-usage-guide)
- [🐳 Docker Deployment](#-docker-deployment)
- [🔒 Security](#-security)
- [📈 Data Models](#-data-models)
- [🎨 Visualizations](#-visualizations)
- [🛠️ Development](#️-development)
- [📚 Documentation](#-documentation)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🎯 **Features**

### **Core Functionality**
- **🕷️ Comprehensive Data Scraping**: Generate detailed ServiceNow data with 21+ modules and 639+ items
- **🗄️ Multi-Database Support**: PostgreSQL (primary) and MySQL support with connection pooling
- **📊 Interactive Visualizations**: Advanced charts, graphs, and network diagrams
- **🔍 Database Introspection**: Connect to external ServiceNow databases for analysis
- **🌐 Live Instance Integration**: REST API integration for real-time ServiceNow data extraction
- **⚙️ Advanced Configuration**: Comprehensive settings management through web interface
- **🔒 Security-First Design**: No hardcoded credentials, environment-based configuration

### **Data Management**
- **📦 Modules**: Event Management, Security, Administration, ITSM, CSM, HRSD, FSM, GRC, SECOPS
- **👥 Roles**: User roles with permissions, dependencies, and access controls
- **📊 Tables**: Database tables with fields, relationships, and business rules
- **⚙️ Properties**: System properties with values, types, and configuration
- **⏰ Scheduled Jobs**: Automated jobs with frequencies, scripts, and schedules

### **User Interface**
- **🏠 Dashboard**: Real-time statistics and quick access to all features
- **📈 Interactive Charts**: Module explorer, comparison charts, and analytics
- **🔧 Configuration Management**: Centralized settings for all components
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **🎨 Professional UI**: Clean, modern interface with consistent styling

---

## 🏗️ **Architecture**

### **Technology Stack**
- **Frontend**: Streamlit (Python web framework)
- **Backend**: Python with SQLAlchemy ORM
- **Database**: PostgreSQL (primary), MySQL (supported)
- **Visualization**: Plotly, NetworkX, Pandas
- **Data Processing**: BeautifulSoup4, Requests, aiohttp
- **Deployment**: Docker, Docker Compose
- **Configuration**: YAML, Environment Variables

### **Core Components**

#### **1. Main Application** (`enhanced_app.py`)
- Central Streamlit application with multi-page navigation
- Dashboard with metrics and quick actions
- Database management interface
- Professional footer on all pages

#### **2. Data Models** (`models.py`)
- `ServiceNowModule`: Module definitions with metadata
- `ServiceNowTable`: Table structures with fields and relationships
- `ServiceNowRole`: Role definitions with permissions
- `ServiceNowProperty`: System properties configuration
- `ServiceNowScheduledJob`: Scheduled job definitions

#### **3. Database Layer** (`database.py`)
- `DatabaseManager`: Main database operations
- `DatabaseIntrospector`: External database analysis
- SQLAlchemy models with relationships
- Connection pooling and error handling

#### **4. Configuration Management** (`config.py`)
- `DatabaseConfig`: Database connection settings
- `ScraperConfig`: Web scraping parameters
- `VisualizationConfig`: Chart and graph settings
- `SecurityConfig`: Security and access control
- `ServiceNowConfig`: ServiceNow instance settings

---

## 📦 **Installation**

### **Prerequisites**
- Python 3.9 or higher
- PostgreSQL 12+ (recommended) or MySQL 8+
- Git

### **Option 1: Quick Start (Recommended)**

```bash
# Clone the repository
git clone https://github.com/AshishGautamKarn/servicenow_docs.git
cd servicenow_docs

# Run the automated setup
python start_app.py
```

### **Option 2: Manual Installation**

```bash
# Clone the repository
git clone https://github.com/AshishGautamKarn/servicenow_docs.git
cd servicenow_docs

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.template .env
# Edit .env with your database credentials

# Run the application
streamlit run enhanced_app.py
```

---

## 🚀 **Quick Start**

### **1. Start the Application**
```bash
# Using the startup script (recommended)
python start_app.py

# Or manually
streamlit run enhanced_app.py
```

### **2. Access the Web Interface**
- Open your browser to `http://localhost:8501`
- The application will automatically open in your default browser

### **3. Configure Database**
1. Go to **🔧 Configuration** page
2. Set up your database connection
3. Test the connection
4. Create necessary tables

### **4. Generate Data**
1. Go to **🕷️ Comprehensive Scraper** page
2. Configure scraper settings
3. Run data generation
4. View results in **📊 Database** page

---

## 🔧 **Configuration**

### **Environment Variables**
Create a `.env` file with the following variables:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=servicenow_docs
DB_USER=servicenow_user
DB_PASSWORD=your_password

# ServiceNow Configuration
SN_INSTANCE_URL=https://your-instance.service-now.com
SN_USERNAME=your_username
SN_PASSWORD=your_password

# Scraper Configuration
SCRAPER_TIMEOUT=60
SCRAPER_USE_SELENIUM=false
```

### **Configuration Files**
- `config.yaml`: Main configuration file
- `env.template`: Environment variables template
- `.env`: Your local environment variables (not committed to git)

---

## 📊 **Usage Guide**

### **🏠 Dashboard**
- View database statistics and recent activity
- Quick access to all features
- Real-time metrics and status

### **🕷️ Comprehensive Scraper**
- Configure scraper settings (timeout, workers, modules, data types)
- Run comprehensive data generation
- View real-time progress and results
- Save data to database

### **🗄️ Database Management**
- View all stored data in tabular format
- Database statistics and metrics
- Switch between database configurations
- Clear database functionality

### **📈 Visualizations**
- **🔍 Module Explorer**: Interactive module exploration with drill-down capabilities
- **📊 Module Comparison**: Side-by-side module analysis
- **🌐 Global Analytics**: System-wide statistics and trends
- **📈 Custom Analysis**: Advanced filtering and analysis options

### **🔍 Database Introspection**
- Connect to external ServiceNow databases
- Analyze database structure and relationships
- Import data from external sources

### **🌐 ServiceNow Instance Integration**
- Connect to live ServiceNow instances via REST API
- Extract comprehensive data including modules, roles, tables, properties, and scheduled jobs
- Real-time data synchronization

### **🔧 Configuration Management**
- **Database Configuration**: Multiple database connection management
- **ServiceNow Configuration**: Instance settings and API configuration
- **Security Configuration**: Access control and security settings
- **General Configuration**: Scraper and logging settings

---

## 🐳 **Docker Deployment**

### **Using Docker Compose (Recommended)**

```bash
# Clone the repository
git clone https://github.com/AshishGautamKarn/servicenow_docs.git
cd servicenow_docs

# Set up environment variables
cp env.template .env
# Edit .env with your configuration

# Deploy with Docker Compose
docker-compose up -d

# Access the application
# http://localhost:8506
```

### **Using Docker**

```bash
# Build the image
docker build -t servicenow-docs .

# Run the container
docker run -p 8506:8506 --env-file .env servicenow-docs
```

---

## 🔒 **Security**

### **Security Features**
- ✅ **No Hardcoded Credentials**: All sensitive data loaded from environment variables
- ✅ **Environment-Based Configuration**: Secure credential management
- ✅ **Database Connection Pooling**: Secure and efficient database connections
- ✅ **Input Validation**: Comprehensive input sanitization
- ✅ **Error Handling**: Secure error messages without sensitive information

### **Security Audit**
- **Status**: ✅ **SECURE - NO HARDCODED CREDENTIALS FOUND**
- **Audit Date**: December 2024
- **Scope**: Complete project codebase analysis
- **Result**: All sensitive data properly externalized

---

## 📈 **Data Models**

### **Core Entities**

#### **ServiceNowModule**
```python
- id: Integer (Primary Key)
- name: String (Unique)
- label: String
- description: Text
- version: String
- module_type: String
- documentation_url: String
- is_active: Boolean
- created_at: DateTime
- updated_at: DateTime
```

#### **ServiceNowTable**
```python
- id: Integer (Primary Key)
- name: String
- label: String
- description: Text
- module_id: Integer (Foreign Key)
- table_type: String
- fields: Array[Text]
- relationships: Array[Text]
- access_controls: Array[Text]
- business_rules: Array[Text]
- scripts: Array[Text]
- is_active: Boolean
```

#### **ServiceNowRole**
```python
- id: Integer (Primary Key)
- name: String
- description: Text
- module_id: Integer (Foreign Key)
- permissions: Array[Text]
- dependencies: Array[Text]
- is_active: Boolean
```

#### **ServiceNowProperty**
```python
- id: Integer (Primary Key)
- name: String
- description: Text
- module_id: Integer (Foreign Key)
- default_value: Text
- current_value: Text
- category: String
- property_type: String
- scope: String
- impact_level: String
- documentation_url: String
- is_active: Boolean
```

#### **ServiceNowScheduledJob**
```python
- id: Integer (Primary Key)
- name: String
- description: Text
- module_id: Integer (Foreign Key)
- script: Text
- schedule: String
- frequency: String
- last_run: DateTime
- next_run: DateTime
- active: Boolean
```

---

## 🎨 **Visualizations**

### **Interactive Features**
- **🔍 Module Explorer**: Drill-down exploration of modules and components
- **📊 Module Comparison**: Side-by-side analysis of different modules
- **🌐 Global Analytics**: System-wide statistics and trends
- **📈 Custom Analysis**: Advanced filtering and analysis options
- **🕸️ Network Graphs**: Visual representation of table relationships
- **📊 Charts and Graphs**: Plotly-based interactive visualizations

### **Visualization Types**
- **Bar Charts**: Module and component counts
- **Pie Charts**: Field type distributions
- **Network Graphs**: Table relationship networks
- **Heatmaps**: Relationship matrices
- **Timeline Charts**: Creation and update timelines
- **Scatter Plots**: Custom analysis visualizations

---

## 🛠️ **Development**

### **Project Structure**
```
servicenow_docs/
├── enhanced_app.py              # Main Streamlit application
├── models.py                    # Data models and enums
├── database.py                  # Database models and connectivity
├── config.py                    # Configuration management
├── comprehensive_servicenow_scraper.py  # Data generation scraper
├── comprehensive_scraper_ui.py  # Scraper user interface
├── interactive_visualizer.py    # Interactive visualizations
├── database_introspection_ui.py # Database introspection UI
├── servicenow_api_client.py     # ServiceNow REST API client
├── servicenow_instance_introspection_ui.py # Instance introspection UI
├── configuration_ui.py          # Configuration management UI
├── visualization.py             # Core visualization components
├── data_loader.py               # Data loading utilities
├── requirements.txt             # Python dependencies
├── docker-compose.yml           # Docker Compose configuration
├── Dockerfile                   # Docker container configuration
├── start_app.py                 # Cross-platform startup script
├── deploy.sh                    # Automated deployment script
├── install.sh                   # Manual installation script
└── README.md                    # This file
```

### **Key Dependencies**
```
streamlit==1.28.1
pandas==2.1.3
plotly==5.17.0
networkx==3.2.1
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pymysql==1.1.0
beautifulsoup4==4.12.2
requests==2.31.0
aiohttp==3.9.1
python-dotenv==1.0.0
pyyaml==6.0.1
```

---

## 📚 **Documentation**

### **Available Documentation**
- **DEPLOYMENT.md**: Comprehensive deployment guide
- **PROJECT_INDEX.md**: Detailed project structure and components
- **PACKAGE_INFO.md**: Package contents and deployment options
- **COMPREHENSIVE_SECURITY_AUDIT_REPORT.md**: Security audit results
- **GITHUB_UPLOAD_GUIDE.md**: GitHub upload instructions

### **Configuration Guides**
- **DATABASE_CONFIG_STORAGE_GUIDE.md**: Database configuration management
- **SERVICENOW_CONFIG_SYNC_GUIDE.md**: ServiceNow configuration synchronization
- **MULTI_DATABASE_CONFIG_GUIDE.md**: Multiple database configuration

---

## 🤝 **Contributing**

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add some amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### **Development Guidelines**
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update documentation as needed
- Ensure all tests pass before submitting

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 **Support**

### **Getting Help**
- **Issues**: [GitHub Issues](https://github.com/AshishGautamKarn/servicenow_docs/issues)
- **Discussions**: [GitHub Discussions](https://github.com/AshishGautamKarn/servicenow_docs/discussions)
- **LinkedIn**: [Ashish Gautam](https://www.linkedin.com/in/ashishgautamkarn/)

### **Common Issues**
- **Database Connection**: Check your `.env` file configuration
- **Permission Errors**: Ensure proper database user permissions
- **Port Conflicts**: Change the port in `streamlit run enhanced_app.py --server.port 8502`

---

## 🎉 **Acknowledgments**

- **ServiceNow**: For providing the platform and APIs
- **Streamlit**: For the excellent web framework
- **Plotly**: For interactive visualizations
- **SQLAlchemy**: For robust database ORM
- **Open Source Community**: For the amazing tools and libraries

---

**⭐ If you find this project helpful, please give it a star on GitHub!**

---

*Last updated: December 2024*