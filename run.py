#!/usr/bin/env python3
"""
ServiceNow Visual Documentation Launcher
Simple launcher script for the ServiceNow documentation application.
"""

import subprocess
import sys
import os
from pathlib import Path


def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'plotly',
        'networkx',
        'pandas',
        'pyvis',
        'dash',
        'dash-cytoscape',
        'dash-bootstrap-components'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Main launcher function"""
    print("🚀 ServiceNow Advanced Visual Documentation")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("app.py"):
        print("❌ Error: app.py not found in current directory")
        print("   Please run this script from the sn_docs directory")
        return 1
    
    # Check requirements
    print("🔍 Checking requirements...")
    if not check_requirements():
        return 1
    
    print("✅ All requirements satisfied!")
    print("\n🌐 Starting ServiceNow Visual Documentation...")
    print("   The application will open in your default browser")
    print("   URL: http://localhost:8501")
    print("\n💡 Press Ctrl+C to stop the application")
    print("=" * 50)
    
    try:
        # Run Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Error running application: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
