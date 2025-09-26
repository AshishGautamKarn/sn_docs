# 🚀 Enhanced ServiceNow App Startup Script - PostgreSQL Integration

## 🎯 **New Features**

The `start_app.sh` script now includes **intelligent PostgreSQL handling** with interactive prompts and automatic installation capabilities.

## 🔧 **PostgreSQL Integration Features**

### ✅ **Smart Detection**
- **Automatically detects** if PostgreSQL is already installed
- **Checks for existing** PostgreSQL installations
- **Offers multiple options** based on your system state

### ✅ **Interactive Setup**
- **User-friendly prompts** for database configuration
- **Connection testing** before proceeding
- **Custom connection strings** support
- **Fallback to SQLite** if PostgreSQL fails

### ✅ **Automatic Installation**
- **Cross-platform support**: Ubuntu, Debian, CentOS, RHEL, Fedora, macOS
- **Package manager detection**: apt-get, yum, dnf, Homebrew
- **Service management**: Automatic start and enable
- **Database creation**: Automatic database and user setup

## 🎮 **Interactive Flow**

### **Scenario 1: PostgreSQL Already Installed**
```
[STEP] Database Setup

[INFO] PostgreSQL is already installed and available

Do you want to use the existing PostgreSQL installation? (y/n) [y]: y

Do you want to use default connection settings? (y/n) [y]: y
```

### **Scenario 2: PostgreSQL Not Installed**
```
[STEP] Database Setup

[WARNING] PostgreSQL is not installed on this system.

You have the following options:
1. Install PostgreSQL locally (recommended)
2. Connect to an existing PostgreSQL server
3. Use SQLite (simpler, but limited functionality)

Choose an option (1/2/3) [1]: 1

Do you want to install PostgreSQL locally? (y/n) [y]: y
```

### **Scenario 3: Custom Connection**
```
[STEP] Database Setup

PostgreSQL Host [localhost]: your-postgres-server.com
PostgreSQL Port [5432]: 5432
Database Name [servicenow_docs]: my_servicenow_db
Username [servicenow_user]: my_user
Password: [hidden input]

[INFO] Testing PostgreSQL connection...
[SUCCESS] PostgreSQL connection successful!
```

## 🛠️ **Supported Operating Systems**

### **Linux Distributions**
- **Ubuntu/Debian**: `apt-get install postgresql postgresql-contrib`
- **CentOS/RHEL**: `yum install postgresql-server postgresql-contrib`
- **Fedora**: `dnf install postgresql-server postgresql-contrib`
- **Rocky Linux**: `yum install postgresql-server postgresql-contrib`

### **macOS**
- **Homebrew**: `brew install postgresql`
- **Automatic service start**: `brew services start postgresql`

## 📋 **Database Configuration Options**

### **Option 1: Use Existing PostgreSQL**
- ✅ **Detects existing installation**
- ✅ **Uses default settings** (localhost:5432)
- ✅ **Creates database and user** automatically
- ✅ **Tests connection** before proceeding

### **Option 2: Install PostgreSQL Locally**
- ✅ **Automatic installation** based on OS
- ✅ **Service management** (start/enable)
- ✅ **Database setup** (servicenow_docs database)
- ✅ **User creation** (servicenow_user with password)

### **Option 3: Connect to Remote PostgreSQL**
- ✅ **Custom connection details** input
- ✅ **Connection testing** before proceeding
- ✅ **Flexible configuration** (host, port, database, user)
- ✅ **Secure password input** (hidden)

### **Option 4: Use SQLite (Fallback)**
- ✅ **No installation required**
- ✅ **Local file database**
- ✅ **Simpler setup**
- ✅ **Limited functionality** (no concurrent access)

## 🔧 **Environment File Configuration**

The script automatically configures your `.env` file based on your database choice:

### **PostgreSQL Configuration**
```bash
DB_TYPE=postgresql
DB_HOST=localhost
DB_PORT=5432
DB_NAME=servicenow_docs
DB_USER=servicenow_user
DB_PASSWORD=YOUR_SECURE_PASSWORD
```

### **SQLite Configuration**
```bash
DB_TYPE=sqlite
DB_HOST=localhost
DB_PORT=5432
DB_NAME=servicenow_docs
DB_USER=servicenow_user
DB_PASSWORD=YOUR_SECURE_PASSWORD
```

## 🚀 **Usage Examples**

### **Full Setup with PostgreSQL Prompts**
```bash
./start_app.sh
```

### **Skip Database Setup (Use SQLite)**
```bash
./start_app.sh --skip-db
```

### **Setup Only (Don't Start App)**
```bash
./start_app.sh --setup-only
```

### **Show Help**
```bash
./start_app.sh --help
```

## 🔍 **What Happens During Setup**

### **Step 1: PostgreSQL Detection**
```
[STEP] Database Setup
[INFO] PostgreSQL is already installed and available
```

### **Step 2: User Choice**
```
Do you want to use the existing PostgreSQL installation? (y/n) [y]: y
Do you want to use default connection settings? (y/n) [y]: y
```

### **Step 3: Database Creation**
```
[STEP] Setting up PostgreSQL database...
[INFO] Creating database 'servicenow_docs'...
[SUCCESS] Database created successfully!
```

### **Step 4: Environment Configuration**
```
[STEP] Setting up environment configuration...
[INFO] Configuring PostgreSQL settings...
[SUCCESS] Environment file created with postgresql configuration!
```

### **Step 5: Application Start**
```
[STEP] Starting ServiceNow Documentation App...
[SUCCESS] 🎉 ServiceNow Documentation App is starting!

📱 Application URL: http://localhost:8506
🗄️  Database: PostgreSQL (localhost:5432/servicenow_docs)
```

## 🛡️ **Error Handling**

### **PostgreSQL Installation Fails**
```
[ERROR] PostgreSQL installation failed. Using SQLite as fallback.
[WARNING] PostgreSQL installation failed. Using SQLite as fallback.
```

### **Connection Test Fails**
```
[ERROR] PostgreSQL connection failed. Please check your credentials.
[WARNING] Using SQLite as fallback due to connection issues.
```

### **Permission Issues**
```
[ERROR] Permission denied. Please run with appropriate permissions.
```

## 🔧 **Manual PostgreSQL Setup (if needed)**

If the automatic installation fails, you can set up PostgreSQL manually:

### **Ubuntu/Debian**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo -u postgres psql -c "CREATE DATABASE servicenow_docs;"
sudo -u postgres psql -c "CREATE USER servicenow_user WITH PASSWORD 'YOUR_SECURE_PASSWORD';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE servicenow_docs TO servicenow_user;"
```

### **CentOS/RHEL**
```bash
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl enable postgresql
sudo systemctl start postgresql
sudo -u postgres psql -c "CREATE DATABASE servicenow_docs;"
sudo -u postgres psql -c "CREATE USER servicenow_user WITH PASSWORD 'YOUR_SECURE_PASSWORD';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE servicenow_docs TO servicenow_user;"
```

### **macOS**
```bash
brew install postgresql
brew services start postgresql
createdb servicenow_docs
psql -c "CREATE USER servicenow_user WITH PASSWORD 'YOUR_SECURE_PASSWORD';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE servicenow_docs TO servicenow_user;"
```

## 🎯 **Benefits**

### **For Users**
- ✅ **No manual PostgreSQL setup** required
- ✅ **Interactive prompts** guide you through options
- ✅ **Automatic fallback** to SQLite if PostgreSQL fails
- ✅ **Cross-platform support** for all major OS

### **For Developers**
- ✅ **Consistent database setup** across environments
- ✅ **Flexible configuration** options
- ✅ **Error handling** with graceful fallbacks
- ✅ **Environment file management** automatic

## 📞 **Troubleshooting**

### **Common Issues**

1. **Permission Denied**: Ensure you have sudo access for PostgreSQL installation
2. **Connection Failed**: Check PostgreSQL service status and credentials
3. **Installation Failed**: Verify package manager availability and internet connection
4. **Port Already in Use**: The script handles port conflicts automatically

### **Manual Verification**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -h localhost -U servicenow_user -d servicenow_docs

# Check environment file
cat .env | grep DB_
```

---

**🎉 The enhanced startup script now provides a seamless PostgreSQL experience with intelligent detection, automatic installation, and flexible configuration options!**

Created by: **Ashish Gautam**  
LinkedIn: [https://www.linkedin.com/in/ashishgautamkarn/](https://www.linkedin.com/in/ashishgautamkarn/)
