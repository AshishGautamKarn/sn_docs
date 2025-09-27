#!/usr/bin/env python3
"""
Warning Suppression Script for ServiceNow Documentation App
This script suppresses common warnings that don't affect functionality
"""

import warnings
import os

def suppress_warnings():
    """Suppress common warnings that don't affect functionality"""
    
    # Suppress urllib3 LibreSSL warning (common on macOS)
    warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")
    
    # Suppress cryptography warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="cryptography")
    
    # Suppress pandas warnings
    warnings.filterwarnings("ignore", category=FutureWarning, module="pandas")
    
    # Suppress matplotlib warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")
    
    # Suppress plotly warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="plotly")
    
    # Suppress streamlit warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="streamlit")
    
    # Set environment variable to suppress urllib3 warnings
    os.environ['PYTHONWARNINGS'] = 'ignore::urllib3.exceptions.NotOpenSSLWarning'

if __name__ == "__main__":
    suppress_warnings()
    print("✅ Warnings suppressed successfully")
