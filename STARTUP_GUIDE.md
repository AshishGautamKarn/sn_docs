# 🚀 ServiceNow App Startup Scripts

This directory contains automated startup scripts that will set up and launch your ServiceNow Advanced Visual Documentation app with minimal effort.

## 📋 Available Startup Scripts

### 1. **Linux/macOS** - `start_app.sh`
```bash
./start_app.sh
```

### 2. **Windows** - `start_app.bat`
```cmd
start_app.bat
```

### 3. **Cross-Platform** - `start_app.py`
```bash
python start_app.py
```

## 🎯 What These Scripts Do

### ✅ **Automatic Setup**
- ✅ Check Python 3.9+ installation
- ✅ Create virtual environment (`venv/`)
- ✅ Install all required dependencies
- ✅ Create environment configuration (`.env`)
- ✅ Initialize database tables
- ✅ Start the Streamlit application

### ✅ **Smart Features**
- ✅ **Dependency Checking**: Verifies Python and pip are installed
- ✅ **Virtual Environment**: Creates isolated Python environment
- ✅ **Port Management**: Automatically handles port 8506 conflicts
- ✅ **Database Setup**: Initializes PostgreSQL or falls back to SQLite
- ✅ **Error Handling**: Graceful error handling with helpful messages
- ✅ **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### **Option 1: Linux/macOS (Recommended)**
```bash
# Make executable and run
chmod +x start_app.sh
./start_app.sh
```

### **Option 2: Windows**
```cmd
# Double-click or run from command prompt
start_app.bat
```

### **Option 3: Cross-Platform Python**
```bash
# Works on any platform with Python
python start_app.py
```

## 📱 Access Your App

Once the script completes, your app will be available at:
- **URL**: http://localhost:8506
- **Database**: PostgreSQL (if available) or SQLite

## 🔧 Advanced Options

### **Linux/macOS Script Options**
```bash
./start_app.sh --help          # Show help
./start_app.sh --setup-only    # Only setup, don't start
./start_app.sh --skip-db       # Skip database setup
./start_app.sh --skip-env       # Skip environment setup
./start_app.sh --force          # Force setup even if configured
```

### **Examples**
```bash
# Full setup and start
./start_app.sh

# Only setup environment, don't start app
./start_app.sh --setup-only

# Skip database setup (use SQLite only)
./start_app.sh --skip-db
```

## 🛠️ Prerequisites

### **Required**
- **Python 3.9+** - Download from [python.org](https://www.python.org/downloads/)
- **pip** - Usually comes with Python

### **Optional (for PostgreSQL)**
- **PostgreSQL** - For production database
- **psql** - PostgreSQL command line tools

## 📊 What Happens During Setup

### **Step 1: Dependency Check**
```
[STEP] Checking system dependencies...
[INFO] Python version: 3.9.7
[SUCCESS] All dependencies are available!
```

### **Step 2: Virtual Environment**
```
[STEP] Setting up Python environment...
[INFO] Creating virtual environment...
[SUCCESS] Python environment setup complete!
```

### **Step 3: Dependencies Installation**
```
[STEP] Installing Python dependencies...
[INFO] Installing requirements...
[SUCCESS] Requirements installed successfully!
```

### **Step 4: Configuration**
```
[STEP] Setting up environment configuration...
[SUCCESS] Environment file created!
```

### **Step 5: Database Setup**
```
[STEP] Setting up database...
[INFO] PostgreSQL is available
[SUCCESS] Database created successfully!
```

### **Step 6: Application Start**
```
[STEP] Starting ServiceNow Documentation App...
[SUCCESS] 🎉 ServiceNow Documentation App is starting!

📱 Application URL: http://localhost:8506
🗄️  Database: PostgreSQL
```

## 🎨 Features

### **Smart Port Management**
- Automatically detects if port 8506 is in use
- Kills conflicting processes if needed
- Provides clear error messages

### **Database Intelligence**
- Detects PostgreSQL installation
- Creates database and user automatically
- Falls back to SQLite if PostgreSQL unavailable
- Initializes all required tables

### **Environment Management**
- Creates `.env` file from template
- Configures database settings automatically
- Handles environment variables properly

### **Error Handling**
- Clear, colored error messages
- Helpful troubleshooting information
- Graceful fallbacks for missing components

## 🔍 Troubleshooting

### **Common Issues**

#### **Python Not Found**
```
[ERROR] Python 3.9+ is not installed
```
**Solution**: Install Python 3.9+ from [python.org](https://www.python.org/downloads/)

#### **Port Already in Use**
```
[WARNING] Port 8506 is already in use
```
**Solution**: The script will automatically free the port, or manually kill the process

#### **Database Connection Failed**
```
[WARNING] Database initialization had issues
```
**Solution**: The app will use SQLite fallback, which works fine for development

#### **Permission Denied (Linux/macOS)**
```
Permission denied: ./start_app.sh
```
**Solution**: 
```bash
chmod +x start_app.sh
./start_app.sh
```

### **Manual Steps (if scripts fail)**

1. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate    # Windows
   ```

2. **Install requirements**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment file**:
   ```bash
   cp env.template .env
   ```

4. **Start application**:
   ```bash
   streamlit run enhanced_app.py --server.port=8506 --server.address=0.0.0.0
   ```

## 🎯 Success Indicators

### **Setup Complete**
```
[SUCCESS] 🎉 Setup complete! All systems are ready.
```

### **Application Running**
```
📱 Application URL: http://localhost:8506
🗄️  Database: PostgreSQL/SQLite
```

### **Browser Access**
Open your browser and navigate to: **http://localhost:8506**

## 🚀 Next Steps

After the app starts:

1. **Open Browser**: Navigate to http://localhost:8506
2. **Explore Dashboard**: View the main dashboard with metrics
3. **Run Scraper**: Click "Run Comprehensive Scraper" to generate data
4. **View Database**: Browse generated data in tabular format
5. **Explore Visualizations**: Analyze data with interactive charts
6. **Connect Live Instance**: Import data from real ServiceNow instances

## 📞 Support

If you encounter issues:

1. **Check Prerequisites**: Ensure Python 3.9+ and pip are installed
2. **Check Logs**: Look for error messages in the script output
3. **Manual Setup**: Follow the manual steps above
4. **Port Issues**: Ensure port 8506 is available
5. **Permissions**: Ensure you have write permissions in the project directory

---

**🎉 Enjoy your ServiceNow Advanced Visual Documentation App!**

Created by: **Ashish Gautam**  
LinkedIn: [https://www.linkedin.com/in/ashishgautamkarn/](https://www.linkedin.com/in/ashishgautamkarn/)
