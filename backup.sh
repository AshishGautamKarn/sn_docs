#!/bin/bash

# ServiceNow Documentation App - Backup Script
# Creates backups of database and application data

set -e

BACKUP_DIR="/opt/backups/servicenow-docs"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="servicenow-docs-backup-$DATE"

echo "🔄 Creating backup: $BACKUP_FILE"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
echo "📊 Backing up database..."
pg_dump -h localhost -U servicenow_user servicenow_docs > $BACKUP_DIR/$BACKUP_FILE.sql

# Application files backup
echo "📁 Backing up application files..."
tar -czf $BACKUP_DIR/$BACKUP_FILE-app.tar.gz /opt/servicenow-docs/ --exclude=venv --exclude=logs --exclude=data

# Create restore script
cat > $BACKUP_DIR/restore-$BACKUP_FILE.sh << EOF
#!/bin/bash
echo "🔄 Restoring from backup: $BACKUP_FILE"

# Restore database
echo "📊 Restoring database..."
psql -h localhost -U servicenow_user -d servicenow_docs < $BACKUP_FILE.sql

# Restore application files
echo "📁 Restoring application files..."
tar -xzf $BACKUP_FILE-app.tar.gz -C /

echo "✅ Restore complete!"
EOF

chmod +x $BACKUP_DIR/restore-$BACKUP_FILE.sh

echo "✅ Backup complete!"
echo "📁 Backup location: $BACKUP_DIR/$BACKUP_FILE"
echo "🔄 Restore script: $BACKUP_DIR/restore-$BACKUP_FILE.sh"
