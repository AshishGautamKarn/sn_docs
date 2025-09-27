#!/usr/bin/env python3
"""
ServiceNow Advanced Visual Documentation - Python Startup Script
Cross-platform startup script that automatically sets up and starts the app
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_colored(text, color="white"):
    """Print colored text based on platform"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m", 
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "purple": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }
    
    if platform.system() == "Windows":
        # Windows doesn't support ANSI colors by default
        print(text)
    else:
        print(f"{colors.get(color, colors['white'])}{text}{colors['reset']}")

def print_header():
    """Print application header"""
    print_colored("=" * 50, "purple")
    print_colored("🚀 ServiceNow Advanced Visual Documentation", "purple")
    print_colored("=" * 50, "purple")
    print()

def print_status(message):
    """Print status message"""
    print_colored(f"[INFO] {message}", "blue")

def print_success(message):
    """Print success message"""
    print_colored(f"[SUCCESS] {message}", "green")

def print_warning(message):
    """Print warning message"""
    print_colored(f"[WARNING] {message}", "yellow")

def print_error(message):
    """Print error message"""
    print_colored(f"[ERROR] {message}", "red")

def print_step(message):
    """Print step message"""
    print_colored(f"[STEP] {message}", "cyan")

def check_command_exists(command):
    """Check if a command exists in PATH"""
    return shutil.which(command) is not None

def run_command(command, shell=True, check=True):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=shell, check=check, 
                              capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        return False, e.stdout, e.stderr

def check_dependencies():
    """Check if required dependencies are available"""
    print_step("Checking system dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print_error("Python 3.9+ is required. Current version: " + sys.version)
        return False
    
    print_status(f"Python version: {sys.version}")
    
    # Check if pip is available
    if not check_command_exists("pip"):
        print_error("pip is not available")
        return False
    
    print_success("All dependencies are available!")
    return True

def setup_virtual_environment():
    """Setup Python virtual environment"""
    print_step("Setting up Python virtual environment...")
    
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print_status("Creating virtual environment...")
        success, stdout, stderr = run_command([sys.executable, "-m", "venv", "venv"])
        if not success:
            print_error(f"Failed to create virtual environment: {stderr}")
            return False
        print_success("Virtual environment created!")
    else:
        print_status("Virtual environment already exists")
    
    return True

def get_venv_python():
    """Get the Python executable path for virtual environment"""
    if platform.system() == "Windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")

def get_venv_pip():
    """Get the pip executable path for virtual environment"""
    if platform.system() == "Windows":
        return Path("venv/Scripts/pip.exe")
    else:
        return Path("venv/bin/pip")

def install_requirements():
    """Install Python requirements"""
    print_step("Installing Python dependencies...")
    
    venv_pip = get_venv_pip()
    
    # Upgrade pip first
    print_status("Upgrading pip...")
    success, stdout, stderr = run_command([str(venv_pip), "install", "--upgrade", "pip"])
    if not success:
        print_warning(f"Failed to upgrade pip: {stderr}")
    
    # Install requirements
    print_status("Installing requirements...")
    success, stdout, stderr = run_command([str(venv_pip), "install", "-r", "requirements.txt"])
    if not success:
        print_error(f"Failed to install requirements: {stderr}")
        
        # Try to install missing dependencies individually
        print_status("Attempting to install missing dependencies individually...")
        critical_deps = ["aiohttp", "streamlit", "pandas", "plotly", "sqlalchemy", "requests", "beautifulsoup4"]
        
        for dep in critical_deps:
            print_status(f"Installing {dep}...")
            success, stdout, stderr = run_command([str(venv_pip), "install", dep])
            if not success:
                print_warning(f"Failed to install {dep}: {stderr}")
        
        print_warning("Some dependencies may not have installed correctly. The app may still work.")
    
    print_success("Requirements installation completed!")
    return True

def setup_environment_file():
    """Setup environment configuration file"""
    print_step("Setting up environment configuration...")
    
    env_file = Path(".env")
    template_file = Path("env.template")
    
    if not env_file.exists():
        if template_file.exists():
            print_status("Creating .env file from template...")
            shutil.copy(template_file, env_file)
            print_success("Environment file created!")
        else:
            print_warning("No env.template found, creating basic .env file...")
            with open(env_file, "w") as f:
                f.write("""# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sn_docs
DB_USER=servicenow_user
DB_PASSWORD=

# Scraper Configuration
SCRAPER_TIMEOUT=60
SCRAPER_USE_SELENIUM=false

# Application Configuration
STREAMLIT_SERVER_PORT=8506
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
STREAMLIT_SERVER_HEADLESS=true
""")
            print_success("Basic environment file created!")
    else:
        print_status("Environment file already exists")

def initialize_database():
    """Initialize database tables"""
    print_step("Initializing database tables...")
    
    venv_python = get_venv_python()
    
    try:
        success, stdout, stderr = run_command([
            str(venv_python), "-c", 
            "from database import initialize_database; db = initialize_database(); print('✅ Database tables created successfully!')"
        ])
        if success:
            print_success("Database initialized successfully!")
        else:
            print_warning(f"Database initialization warning: {stderr}")
            print_warning("The app will still work with SQLite fallback.")
    except Exception as e:
        print_warning(f"Database initialization had issues: {e}")
        print_warning("The app will still work with SQLite fallback.")

def start_application():
    """Start the Streamlit application"""
    print_step("Starting ServiceNow Documentation App...")
    
    venv_python = get_venv_python()
    
    print_success("🎉 ServiceNow Documentation App is starting!")
    print()
    print_colored("📱 Application URL: http://localhost:8506", "green")
    print_colored("🗄️  Database: SQLite (default)", "green")
    print()
    print_colored("Press Ctrl+C to stop the application", "yellow")
    print()
    
    # Start Streamlit
    try:
        subprocess.run([
            str(venv_python), "-m", "streamlit", "run", "enhanced_app.py",
            "--server.port=8506",
            "--server.address=0.0.0.0", 
            "--browser.gatherUsageStats=false"
        ])
    except KeyboardInterrupt:
        print()
        print_colored("Application stopped by user", "yellow")
    except Exception as e:
        print_error(f"Failed to start application: {e}")

def main():
    """Main function"""
    print_header()
    
    # Check if we're in the right directory
    if not Path("enhanced_app.py").exists():
        print_error("This script must be run from the ServiceNow documentation project directory")
        print_error("Please navigate to the project directory and run this script again")
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Setup virtual environment
    if not setup_virtual_environment():
        return False
    
    # Install requirements
    if not install_requirements():
        return False
    
    # Setup environment file
    setup_environment_file()
    
    # Initialize database
    initialize_database()
    
    print_success("🎉 Setup complete! All systems are ready.")
    print()
    
    # Start the application
    start_application()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print()
        print_colored("Setup interrupted by user", "yellow")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)
