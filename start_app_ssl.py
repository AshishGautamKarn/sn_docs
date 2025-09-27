#!/usr/bin/env python3
"""
SSL-enabled Streamlit startup script
ServiceNow Advanced Visual Documentation
"""

import subprocess
import sys
import os
from pathlib import Path
import argparse

def print_header():
    """Print startup header"""
    print("🔒 ServiceNow Advanced Visual Documentation - SSL Mode")
    print("=" * 60)
    print("🚀 Starting with SSL/HTTPS encryption")
    print("")

def check_ssl_certificates():
    """Check if SSL certificates exist"""
    cert_file = Path("ssl/cert.pem")
    key_file = Path("ssl/key.pem")
    
    if not cert_file.exists() or not key_file.exists():
        print("❌ SSL certificates not found!")
        print("📄 Please run: ./generate_ssl_cert.sh")
        print("")
        print("🔧 This will generate self-signed certificates for development")
        return False
    
    print("✅ SSL certificates found")
    print(f"📁 Certificate: {cert_file}")
    print(f"📁 Private Key: {key_file}")
    return True

def get_streamlit_command(port=8501, ssl_mode=True):
    """Get Streamlit command with SSL configuration"""
    cmd = [
        sys.executable, "-m", "streamlit", "run", "enhanced_app.py",
        "--server.port", str(port),
        "--server.address", "0.0.0.0",
        "--browser.gatherUsageStats", "false",
        "--server.headless", "true"
    ]
    
    if ssl_mode:
        cmd.extend([
            "--server.sslCertFile", "ssl/cert.pem",
            "--server.sslKeyFile", "ssl/key.pem"
        ])
    
    return cmd

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Start ServiceNow Docs with SSL")
    parser.add_argument("--port", type=int, default=8501, help="Port to run on (default: 8501)")
    parser.add_argument("--no-ssl", action="store_true", help="Run without SSL")
    parser.add_argument("--generate-cert", action="store_true", help="Generate SSL certificate first")
    
    args = parser.parse_args()
    
    print_header()
    
    # Generate certificate if requested
    if args.generate_cert:
        print("🔧 Generating SSL certificate...")
        try:
            subprocess.run(["./generate_ssl_cert.sh"], check=True)
            print("✅ SSL certificate generated")
        except subprocess.CalledProcessError:
            print("❌ Failed to generate SSL certificate")
            sys.exit(1)
        except FileNotFoundError:
            print("❌ generate_ssl_cert.sh not found")
            sys.exit(1)
    
    # Check SSL certificates
    ssl_mode = not args.no_ssl
    if ssl_mode and not check_ssl_certificates():
        sys.exit(1)
    
    # Get Streamlit command
    cmd = get_streamlit_command(args.port, ssl_mode)
    
    # Print startup information
    protocol = "https" if ssl_mode else "http"
    print(f"🌐 Protocol: {protocol.upper()}")
    print(f"🔗 Access: {protocol}://localhost:{args.port}")
    
    if ssl_mode:
        print("⚠️  Note: Self-signed certificate - accept security warning in browser")
        print("🔒 SSL/TLS encryption enabled")
    else:
        print("⚠️  Note: Running without SSL - not recommended for production")
    
    print("")
    print("🚀 Starting Streamlit...")
    print("📱 Press Ctrl+C to stop")
    print("")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        print("👋 Goodbye!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Streamlit: {e}")
        print("")
        print("🔧 Troubleshooting:")
        print("   1. Check if port {args.port} is available")
        print("   2. Verify SSL certificates exist (ssl/cert.pem, ssl/key.pem)")
        print("   3. Try running without SSL: python3 start_app_ssl.py --no-ssl")
        sys.exit(1)

if __name__ == "__main__":
    main()

# Created By: Ashish Gautam; LinkedIn: https://www.linkedin.com/in/ashishgautamkarn/
