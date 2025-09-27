#!/usr/bin/env python3
"""
Clean Startup Script for ServiceNow Documentation App
Suppresses warnings and provides cleaner startup experience.
"""

import os
import sys
import warnings
import logging

# Suppress SSL warnings
warnings.filterwarnings("ignore", message=".*urllib3.*OpenSSL.*")

# Suppress Plotly deprecation warnings
warnings.filterwarnings("ignore", message=".*DatetimeProperties.to_pydatetime.*")

# Suppress pandas warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Suppress Streamlit warnings
warnings.filterwarnings("ignore", message=".*Streamlit.*")

def setup_clean_logging():
    """Setup cleaner logging configuration"""
    
    # Configure logging to be less verbose
    logging.basicConfig(
        level=logging.ERROR,  # Only show errors
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # Set specific loggers to be less verbose
    logging.getLogger('centralized_db_config').setLevel(logging.ERROR)
    logging.getLogger('servicenow_database').setLevel(logging.ERROR)
    logging.getLogger('servicenow_database_connector').setLevel(logging.ERROR)
    logging.getLogger('servicenow_api_client').setLevel(logging.ERROR)
    logging.getLogger('urllib3').setLevel(logging.ERROR)
    logging.getLogger('requests').setLevel(logging.ERROR)

def main():
    """Main startup function"""
    
    print("🚀 Starting ServiceNow Documentation App...")
    print("🔧 Suppressing warnings for cleaner experience...")
    
    # Setup clean logging
    setup_clean_logging()
    
    # Import and run the main app
    try:
        from enhanced_app import main as app_main
        print("✅ App loaded successfully!")
        print("🌐 Starting Streamlit server...")
        app_main()
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
