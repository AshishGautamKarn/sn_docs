# 🔧 PostgreSQL Connection Troubleshooting Guide

## ❌ **Issue**: PostgreSQL Connection Failed

When you see this error:
```
[ERROR] PostgreSQL connection failed. Please check your credentials.
```

## 🔍 **Quick Diagnosis**

### **Step 1: Run the Troubleshooting Script**
```bash
./troubleshoot_postgresql.sh
```

This script will automatically check:
- ✅ PostgreSQL service status
- ✅ PostgreSQL processes
- ✅ Network connectivity
- ✅ Port availability
- ✅ Configuration files

### **Step 2: Manual Checks**

#### **Check PostgreSQL Service Status**
```bash
# Linux (systemd)
sudo systemctl status postgresql

# macOS (Homebrew)
brew services list | grep postgresql

# Check if PostgreSQL is running
ps aux | grep postgres
```

#### **Check Network Connectivity**
```bash
# Test if PostgreSQL port is open
netstat -tlnp | grep 5432

# Test connection
telnet localhost 5432
# or
nc -z localhost 5432
```

#### **Test PostgreSQL Connection**
```bash
# Test as postgres superuser
sudo -u postgres psql

# Test with specific credentials
psql -h localhost -U servicenow_user -d sn_docs
```

## 🛠️ **Common Solutions**

### **Solution 1: Start PostgreSQL Service**

#### **Linux (Ubuntu/Debian)**
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### **Linux (CentOS/RHEL)**
```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### **macOS (Homebrew)**
```bash
brew services start postgresql
```

### **Solution 2: Create Database and User**

```bash
# Connect as postgres superuser
sudo -u postgres psql

# Create database
CREATE DATABASE sn_docs;

# Create user
CREATE USER servicenow_user WITH PASSWORD 'YOUR_SECURE_PASSWORD';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE sn_docs TO servicenow_user;

# Exit
\q
```

### **Solution 3: Fix Authentication Issues**

#### **Check pg_hba.conf**
```bash
# Find pg_hba.conf file
sudo find /etc -name "pg_hba.conf" 2>/dev/null
# or
sudo find /var/lib/postgresql -name "pg_hba.conf" 2>/dev/null

# Edit the file
sudo nano /path/to/pg_hba.conf
```

#### **Add Local Connection Rule**
Add this line to pg_hba.conf:
```
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
```

#### **Restart PostgreSQL**
```bash
sudo systemctl restart postgresql
```

### **Solution 4: Install PostgreSQL Client Tools**

#### **Ubuntu/Debian**
```bash
sudo apt-get update
sudo apt-get install postgresql-client
```

#### **CentOS/RHEL**
```bash
sudo yum install postgresql
```

#### **macOS**
```bash
brew install postgresql
```

## 🎯 **Enhanced Startup Script Features**

The updated `start_app.sh` now includes:

### ✅ **Better Error Messages**
- **Network connectivity testing** before authentication
- **Detailed troubleshooting suggestions**
- **Step-by-step error diagnosis**

### ✅ **Automatic Database Creation**
- **Offers to create database and user** if connection fails
- **Uses postgres superuser** to set up permissions
- **Tests connection again** after setup

### ✅ **Multiple Connectivity Tests**
- **netcat (nc)** for port testing
- **telnet** as fallback
- **bash built-in** /dev/tcp as last resort

## 🚀 **Quick Fix Commands**

### **If PostgreSQL is not running:**
```bash
sudo systemctl start postgresql
```

### **If database doesn't exist:**
```bash
sudo -u postgres psql -c "CREATE DATABASE sn_docs;"
```

### **If user doesn't exist:**
```bash
sudo -u postgres psql -c "CREATE USER servicenow_user WITH PASSWORD 'YOUR_SECURE_PASSWORD';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sn_docs TO servicenow_user;"
```

### **If you want to use SQLite instead:**
```bash
./start_app.sh --skip-db
```

## 🔍 **Diagnostic Commands**

### **Check PostgreSQL Status**
```bash
# Service status
sudo systemctl status postgresql

# Process list
ps aux | grep postgres

# Port listening
netstat -tlnp | grep 5432

# Connection test
psql -h localhost -U postgres -c "SELECT version();"
```

### **Check Logs**
```bash
# System logs
sudo journalctl -u postgresql -f

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

## 🎮 **Interactive Troubleshooting**

When you run the enhanced startup script and encounter connection issues:

1. **The script will show detailed error messages**
2. **It will offer to create the database and user**
3. **It will test connectivity step by step**
4. **It will provide specific troubleshooting suggestions**

### **Example Enhanced Flow:**
```
[ERROR] PostgreSQL connection failed. Please check your credentials.

Troubleshooting suggestions:
  - Verify username and password are correct
  - Check if the database 'sn_docs' exists
  - Ensure user 'servicenow_user' has access to database 'sn_docs'
  - Check PostgreSQL authentication settings (pg_hba.conf)

Do you want to create the database and user? (y/n) [n]: y
PostgreSQL superuser (postgres) password: [hidden input]
[SUCCESS] Database 'sn_docs' created successfully!
[SUCCESS] User 'servicenow_user' created successfully!
[SUCCESS] Privileges granted successfully!
[SUCCESS] PostgreSQL connection successful after setup!
```

## 📞 **Still Having Issues?**

If you're still experiencing problems:

1. **Run the troubleshooting script**: `./troubleshoot_postgresql.sh`
2. **Check PostgreSQL logs** for specific error messages
3. **Verify your PostgreSQL installation** is complete
4. **Consider using SQLite** as a fallback: `./start_app.sh --skip-db`
5. **Check firewall settings** if connecting to remote PostgreSQL

---

**🎉 The enhanced startup script now provides much better error handling and automatic database setup!**

Created by: **Ashish Gautam**  
LinkedIn: [https://www.linkedin.com/in/ashishgautamkarn/](https://www.linkedin.com/in/ashishgautamkarn/)
