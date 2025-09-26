# Database Configuration Synchronization Guide

## Overview

The ServiceNow Documentation App now supports real-time database configuration synchronization between the Configuration page and the Database page. This allows users to change database settings dynamically without restarting the application.

## User Flow Timeline

### 1. **Application Startup**
- User provides database connection parameters via `start_app.sh` or environment variables
- Application initializes with these parameters

### 2. **Configuration Page Auto-Population**
- Configuration page automatically loads database settings from startup parameters
- Shows status: "✅ Using saved database configuration from database" or "ℹ️ Using database configuration from config files"

### 3. **Database Page Display**
- Database page shows current configuration from Configuration page
- Displays connection details, status, and statistics
- Shows configuration source (database vs environment variables)

### 4. **Dynamic Configuration Changes**
- User can modify database settings in Configuration page
- Changes are saved to database for persistence
- Database page reflects changes when refreshed

### 5. **Real-Time Synchronization**
- Click "🔄 Refresh Configuration" button on Database page
- Configuration is reloaded from database
- Database connection is updated if settings changed
- Page refreshes to show new configuration

## Technical Implementation

### Database Configuration Storage

```python
class DatabaseConfiguration(Base):
    """Database configuration storage"""
    __tablename__ = 'database_configurations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, default='default')
    db_type = Column(String(50), nullable=False, default='postgresql')
    host = Column(String(255), nullable=False, default='localhost')
    port = Column(Integer, nullable=False, default=5432)
    database_name = Column(String(255), nullable=False, default='servicenow_docs')
    username = Column(String(255), nullable=False, default='servicenow_user')
    password = Column(String(500), nullable=False)  # Encrypted password
    connection_pool_size = Column(Integer, default=10)
    max_overflow = Column(Integer, default=20)
    echo = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Configuration Loading Priority

1. **Database First**: Load from `database_configurations` table
2. **Environment Fallback**: Load from environment variables
3. **Default Values**: Use sensible defaults if nothing found

### Real-Time Connection Updates

When configuration changes are detected:

```python
def reload_configuration(self):
    """Reload database configuration from environment variables and saved database configuration"""
    try:
        # First try to load from saved database configuration
        db_config = self.get_database_configuration('default')
        if db_config:
            # Build database URL from saved configuration
            new_database_url = f"postgresql://{db_config.username}:{db_config.password}@{db_config.host}:{db_config.port}/{db_config.database_name}"
            
            # Update engine if URL changed
            if new_database_url != self.database_url:
                self.database_url = new_database_url
                self.engine = create_engine(new_database_url, echo=db_config.echo)
                self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
                return True
    except Exception as e:
        # Fall back to environment variables
        pass
```

## User Interface Features

### Configuration Page

- **Status Indicator**: Shows whether configuration is loaded from database or config files
- **Auto-Population**: Database settings automatically populated from startup parameters
- **Save to Database**: Changes are saved to database for persistence
- **Password Handling**: Secure password storage and retrieval

### Database Page

- **Connection Details**: Shows actual connection parameters
- **Connection Status**: Real-time connection testing with error details
- **Configuration Source**: Indicates whether settings come from database or environment
- **Refresh Button**: "🔄 Refresh Configuration" button to reload settings
- **Connection Pool Info**: Shows pool size, max overflow, and echo settings

## Configuration Sources

### 1. Database Configuration (Priority 1)
- Stored in `database_configurations` table
- Persisted across application restarts
- Can be modified via Configuration page
- Automatically loaded by Database page

### 2. Environment Variables (Priority 2)
- Loaded from `.env` file or system environment
- Used as fallback when database configuration is not available
- Set during application startup

### 3. Default Values (Priority 3)
- Hardcoded sensible defaults
- Used when neither database nor environment configuration is available

## Usage Examples

### Example 1: Changing Database Host

1. **Start Application**: `./start_app.sh` with initial database settings
2. **Configuration Page**: Shows current settings (e.g., localhost:5432)
3. **Modify Settings**: Change host to "production-db.company.com"
4. **Save Configuration**: Click "💾 Save Configuration"
5. **Database Page**: Click "🔄 Refresh Configuration"
6. **Result**: Database page now shows new host and attempts to connect

### Example 2: Switching Database Types

1. **Current**: PostgreSQL database
2. **Configuration Page**: Change database type to MySQL
3. **Update Settings**: Modify host, port, and credentials
4. **Save**: Configuration saved to database
5. **Refresh**: Database page reloads with MySQL settings
6. **Connection**: Application now connects to MySQL database

### Example 3: Connection Pool Tuning

1. **Default**: Connection pool size 10, max overflow 20
2. **Configuration Page**: Increase pool size to 25, max overflow to 50
3. **Save**: Settings saved to database
4. **Refresh**: Database page shows new pool settings
5. **Application**: Uses new connection pool settings

## Error Handling

### Connection Failures
- **Database Page**: Shows "❌ Not Connected" with error details
- **Error Details**: Displays specific connection error messages
- **Troubleshooting**: Provides guidance for common connection issues

### Configuration Loading Failures
- **Fallback**: Automatically falls back to environment variables
- **Warning**: Shows warning messages for configuration loading issues
- **Recovery**: Application continues with available configuration

### Database Access Issues
- **Graceful Degradation**: Falls back to environment variables
- **Logging**: Detailed error logging for troubleshooting
- **User Feedback**: Clear error messages in UI

## Security Considerations

### Password Handling
- **Encryption**: Passwords stored encrypted in database
- **Display**: Passwords masked in UI (shown as asterisks)
- **Transmission**: Secure password handling in configuration updates

### Configuration Validation
- **Input Validation**: Database connection parameters validated
- **Error Prevention**: Prevents invalid configuration from being saved
- **Sanitization**: Input sanitization for security

## Troubleshooting

### Common Issues

1. **Configuration Not Updating**
   - **Solution**: Click "🔄 Refresh Configuration" button
   - **Check**: Verify configuration was saved to database

2. **Connection Failures**
   - **Check**: Database host, port, and credentials
   - **Verify**: Network connectivity to database server
   - **Test**: Use "🔄 Test Connection" button

3. **Configuration Not Persisting**
   - **Check**: Database write permissions
   - **Verify**: Configuration table exists
   - **Logs**: Check application logs for errors

### Debug Information

- **Configuration Source**: Shows whether settings come from database or environment
- **Connection Status**: Real-time connection testing
- **Error Details**: Specific error messages for troubleshooting
- **Logging**: Detailed application logs for debugging

## Benefits

### 1. **Dynamic Configuration**
- Change database settings without restarting application
- Real-time configuration updates
- Persistent configuration storage

### 2. **User Experience**
- Intuitive configuration management
- Clear status indicators
- Easy troubleshooting

### 3. **Flexibility**
- Support for multiple database types
- Easy switching between databases
- Configuration validation and error handling

### 4. **Reliability**
- Graceful fallback mechanisms
- Error recovery
- Persistent configuration storage

## Conclusion

The database configuration synchronization feature provides a seamless experience for managing database connections in the ServiceNow Documentation App. Users can dynamically change database settings, and the application automatically updates its connection while maintaining configuration persistence across restarts.

---

**Created By**: Ashish Gautam  
**LinkedIn**: [https://www.linkedin.com/in/ashishgautamkarn/](https://www.linkedin.com/in/ashishgautamkarn/)
