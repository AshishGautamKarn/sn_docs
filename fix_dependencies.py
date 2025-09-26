#!/usr/bin/env python3
"""
Quick Fix Script for ServiceNow App Dependencies
Fixes common missing dependency issues
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def fix_dependencies():
    """Fix missing dependencies"""
    print("🔧 ServiceNow App - Dependency Fix Script")
    print("=" * 50)
    
    # Check if virtual environment exists
    venv_path = Path("venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found. Please run start_app.py first.")
        return False
    
    # Determine pip path
    if os.name == 'nt':  # Windows
        pip_path = "venv/Scripts/pip.exe"
    else:  # Unix/Linux/macOS
        pip_path = "venv/bin/pip"
    
    print(f"📦 Installing missing dependencies using {pip_path}...")
    
    # Critical dependencies that are commonly missing
    critical_deps = [
        "aiohttp==3.9.1",
        "streamlit==1.28.1", 
        "pandas==2.1.3",
        "plotly==5.17.0",
        "sqlalchemy==2.0.23",
        "requests==2.31.0",
        "beautifulsoup4==4.12.2",
        "python-dotenv==1.0.0",
        "pyyaml==6.0.1",
        "networkx==3.2.1"
    ]
    
    success_count = 0
    total_count = len(critical_deps)
    
    for dep in critical_deps:
        print(f"Installing {dep}...")
        success, output = run_command(f"{pip_path} install {dep}")
        if success:
            print(f"✅ {dep} installed successfully")
            success_count += 1
        else:
            print(f"❌ Failed to install {dep}: {output}")
    
    print(f"\n📊 Installation Summary: {success_count}/{total_count} dependencies installed")
    
    if success_count == total_count:
        print("🎉 All dependencies installed successfully!")
        print("🚀 You can now run: streamlit run enhanced_app.py --server.port=8506 --server.address=0.0.0.0")
        return True
    else:
        print("⚠️  Some dependencies failed to install. The app may still work.")
        print("💡 Try running the app anyway, or check the error messages above.")
        return False

if __name__ == "__main__":
    try:
        success = fix_dependencies()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Installation interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
