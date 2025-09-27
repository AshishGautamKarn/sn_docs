#!/usr/bin/env python3
"""
ServiceNow Advanced Visual Documentation Setup Script
Automated setup and installation script for the ServiceNow documentation system.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path
import argparse
import logging


class ServiceNowSetup:
    """Setup class for ServiceNow documentation system"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.logger = self._setup_logger()
        self.system_info = self._get_system_info()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for setup process"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger('servicenow_setup')
    
    def _get_system_info(self) -> dict:
        """Get system information"""
        return {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'python_version': sys.version,
            'architecture': platform.architecture()[0],
            'processor': platform.processor()
        }
    
    def check_python_version(self) -> bool:
        """Check if Python version is compatible"""
        if sys.version_info < (3, 8):
            self.logger.error("Python 3.8 or higher is required")
            return False
        
        self.logger.info(f"✅ Python version: {sys.version}")
        return True
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies"""
        try:
            self.logger.info("📦 Installing Python dependencies...")
            
            # Install requirements
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], check=True, cwd=self.project_root)
            
            self.logger.info("✅ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Failed to install dependencies: {e}")
            return False
    
    def setup_database(self, db_type: str = "postgresql") -> bool:
        """Setup database"""
        try:
            if db_type == "postgresql":
                return self._setup_postgresql()
            elif db_type == "mysql":
                return self._setup_mysql()
            else:
                self.logger.error(f"Unsupported database type: {db_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Database setup failed: {e}")
            return False
    
    def _setup_postgresql(self) -> bool:
        """Setup PostgreSQL database"""
        self.logger.info("🐘 Setting up PostgreSQL...")
        
        # Check if PostgreSQL is installed
        try:
            subprocess.run(["psql", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.warning("PostgreSQL not found. Please install PostgreSQL first.")
            self.logger.info("Installation instructions:")
            self.logger.info("- Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib")
            self.logger.info("- macOS: brew install postgresql")
            self.logger.info("- Windows: Download from https://www.postgresql.org/download/")
            return False
        
        # Create database
        try:
            subprocess.run([
                "createdb", "sn_docs"
            ], check=True)
            self.logger.info("✅ PostgreSQL database created")
            return True
        except subprocess.CalledProcessError:
            self.logger.warning("Database might already exist or creation failed")
            return True
    
    def _setup_mysql(self) -> bool:
        """Setup MySQL database"""
        self.logger.info("🐬 Setting up MySQL...")
        
        # Check if MySQL is installed
        try:
            subprocess.run(["mysql", "--version"], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.logger.warning("MySQL not found. Please install MySQL first.")
            self.logger.info("Installation instructions:")
            self.logger.info("- Ubuntu/Debian: sudo apt-get install mysql-server")
            self.logger.info("- macOS: brew install mysql")
            self.logger.info("- Windows: Download from https://dev.mysql.com/downloads/")
            return False
        
        # Create database
        try:
            subprocess.run([
                "mysql", "-e", "CREATE DATABASE IF NOT EXISTS sn_docs;"
            ], check=True)
            self.logger.info("✅ MySQL database created")
            return True
        except subprocess.CalledProcessError:
            self.logger.warning("Database creation failed or MySQL not accessible")
            return False
    
    def create_config_files(self) -> bool:
        """Create configuration files"""
        try:
            self.logger.info("⚙️ Creating configuration files...")
            
            # Create .env file from example
            env_example = self.project_root / "env_example.txt"
            env_file = self.project_root / ".env"
            
            if env_example.exists() and not env_file.exists():
                with open(env_example, 'r') as src, open(env_file, 'w') as dst:
                    dst.write(src.read())
                self.logger.info("✅ Environment file created")
            
            # Create config.yaml
            config_file = self.project_root / "config.yaml"
            if not config_file.exists():
                from config import create_sample_config_file
                create_sample_config_file()
                self.logger.info("✅ Configuration file created")
            
            # Create logs directory
            logs_dir = self.project_root / "logs"
            logs_dir.mkdir(exist_ok=True)
            self.logger.info("✅ Logs directory created")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Configuration setup failed: {e}")
            return False
    
    def initialize_database_schema(self) -> bool:
        """Initialize database schema"""
        try:
            self.logger.info("🗄️ Initializing database schema...")
            
            # Import and initialize database
            from database import initialize_database
            
            db_manager = initialize_database()
            self.logger.info("✅ Database schema initialized")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Database schema initialization failed: {e}")
            return False
    
    def run_tests(self) -> bool:
        """Run basic tests"""
        try:
            self.logger.info("🧪 Running basic tests...")
            
            # Test imports
            from models import ServiceNowDocumentation
            from data_loader import load_servicenow_data
            from visualization import ServiceNowVisualizer
            from database import DatabaseManager
            from scraper import ServiceNowDocumentationScraper
            
            # Test data loading
            doc = load_servicenow_data()
            visualizer = ServiceNowVisualizer(doc)
            
            # Test database connection
            db_manager = DatabaseManager()
            stats = db_manager.get_database_statistics()
            
            self.logger.info("✅ All tests passed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Tests failed: {e}")
            return False
    
    def create_startup_scripts(self) -> bool:
        """Create startup scripts"""
        try:
            self.logger.info("🚀 Creating startup scripts...")
            
            # Create run script for different platforms
            if self.system_info['platform'] == 'Windows':
                self._create_windows_scripts()
            else:
                self._create_unix_scripts()
            
            self.logger.info("✅ Startup scripts created")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Startup script creation failed: {e}")
            return False
    
    def _create_windows_scripts(self):
        """Create Windows startup scripts"""
        # Batch file
        batch_content = """@echo off
echo Starting ServiceNow Advanced Visual Documentation...
python enhanced_app.py
pause
"""
        
        with open(self.project_root / "start.bat", 'w') as f:
            f.write(batch_content)
        
        # PowerShell script
        ps_content = """Write-Host "Starting ServiceNow Advanced Visual Documentation..." -ForegroundColor Green
python enhanced_app.py
Read-Host "Press Enter to continue"
"""
        
        with open(self.project_root / "start.ps1", 'w') as f:
            f.write(ps_content)
    
    def _create_unix_scripts(self):
        """Create Unix startup scripts"""
        # Bash script
        bash_content = """#!/bin/bash
echo "Starting ServiceNow Advanced Visual Documentation..."
python3 enhanced_app.py
"""
        
        start_script = self.project_root / "start.sh"
        with open(start_script, 'w') as f:
            f.write(bash_content)
        
        # Make executable
        os.chmod(start_script, 0o755)
    
    def show_system_info(self):
        """Show system information"""
        self.logger.info("🖥️ System Information:")
        for key, value in self.system_info.items():
            self.logger.info(f"  {key}: {value}")
    
    def show_next_steps(self):
        """Show next steps for the user"""
        self.logger.info("\n🎉 Setup completed successfully!")
        self.logger.info("\n📋 Next Steps:")
        self.logger.info("1. Update configuration files:")
        self.logger.info("   - Edit .env file with your database credentials")
        self.logger.info("   - Edit config.yaml for advanced configuration")
        
        self.logger.info("\n2. Start the application:")
        if self.system_info['platform'] == 'Windows':
            self.logger.info("   - Double-click start.bat")
            self.logger.info("   - Or run: python enhanced_app.py")
        else:
            self.logger.info("   - Run: ./start.sh")
            self.logger.info("   - Or run: python3 enhanced_app.py")
        
        self.logger.info("\n3. Access the application:")
        self.logger.info("   - Open your browser to: http://localhost:8501")
        
        self.logger.info("\n4. Optional: Run web scraper:")
        self.logger.info("   - Use the Web Scraper interface in the application")
        self.logger.info("   - Or run: python scraper.py")
        
        self.logger.info("\n📚 Documentation:")
        self.logger.info("   - README.md: Complete documentation")
        self.logger.info("   - config.yaml: Configuration options")
        self.logger.info("   - logs/: Application logs")
    
    def run_full_setup(self, db_type: str = "postgresql") -> bool:
        """Run complete setup process"""
        self.logger.info("🚀 Starting ServiceNow Advanced Visual Documentation Setup")
        self.logger.info("=" * 60)
        
        # Show system info
        self.show_system_info()
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Setup database
        if not self.setup_database(db_type):
            self.logger.warning("Database setup had issues, but continuing...")
        
        # Create config files
        if not self.create_config_files():
            return False
        
        # Initialize database schema
        if not self.initialize_database_schema():
            self.logger.warning("Database schema initialization had issues, but continuing...")
        
        # Run tests
        if not self.run_tests():
            self.logger.warning("Some tests failed, but continuing...")
        
        # Create startup scripts
        if not self.create_startup_scripts():
            self.logger.warning("Startup script creation had issues, but continuing...")
        
        # Show next steps
        self.show_next_steps()
        
        return True


def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="ServiceNow Advanced Visual Documentation Setup")
    parser.add_argument(
        "--db-type", 
        choices=["postgresql", "mysql"], 
        default="postgresql",
        help="Database type to setup (default: postgresql)"
    )
    parser.add_argument(
        "--skip-db", 
        action="store_true",
        help="Skip database setup"
    )
    parser.add_argument(
        "--test-only", 
        action="store_true",
        help="Run tests only"
    )
    
    args = parser.parse_args()
    
    setup = ServiceNowSetup()
    
    if args.test_only:
        success = setup.run_tests()
    elif args.skip_db:
        # Run setup without database
        setup.check_python_version()
        setup.install_dependencies()
        setup.create_config_files()
        setup.create_startup_scripts()
        setup.show_next_steps()
        success = True
    else:
        success = setup.run_full_setup(args.db_type)
    
    if success:
        print("\n✅ Setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Setup failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
