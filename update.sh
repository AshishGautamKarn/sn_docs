#!/bin/bash

# ServiceNow Documentation App - Update Script
# Updates the application to the latest version

set -e

echo "🔄 Updating ServiceNow Documentation App"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "❌ This script should not be run as root"
   exit 1
fi

# Backup current version
echo "💾 Creating backup before update..."
./backup.sh

# Stop the service
echo "⏹️  Stopping application..."
sudo systemctl stop servicenow-app

# Update application files
echo "📥 Updating application files..."
# Assuming you have the new files in a directory called 'update'
if [ -d "update" ]; then
    sudo cp -r update/* /opt/servicenow-docs/
    sudo chown -R servicenow:servicenow /opt/servicenow-docs
else
    echo "⚠️  No update directory found. Please place new files in 'update' directory"
    exit 1
fi

# Update Python dependencies
echo "🐍 Updating Python dependencies..."
cd /opt/servicenow-docs
sudo -u servicenow venv/bin/pip install --upgrade pip
sudo -u servicenow venv/bin/pip install -r requirements.txt

# Start the service
echo "▶️  Starting application..."
sudo systemctl start servicenow-app

# Wait for service to start
sleep 10

# Check if service is running
if systemctl is-active --quiet servicenow-app; then
    echo "✅ Update complete!"
    echo "🌐 Application is running at: http://localhost:8506"
else
    echo "❌ Service failed to start. Check logs with: journalctl -u servicenow-app -f"
    exit 1
fi
