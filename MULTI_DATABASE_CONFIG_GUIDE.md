# Multi-Database Configuration System Guide

## Overview

The ServiceNow Documentation App now supports multiple database configurations, allowing users to save, manage, and switch between different database connections without restarting the application. This enables seamless switching between development, testing, and production databases.

## Key Features

### 1. **Multiple Database Configurations**
- Save unlimited database configurations with custom names
- Each configuration includes all connection parameters
- Configurations persist across application restarts

### 2. **Configuration Management**
- Create new configurations in Configuration page
- Load existing configurations for editing
- Delete unused configurations

### 3. **Dynamic Database Switching**
- Select configurations from dropdown in Database page
- Switch between databases with one click
- Automatic table creation in new databases

### 4. **Configuration Synchronization**
- Configuration page shows saved configurations
- Database page reflects selected configuration
- Real-time updates across all pages

## User Interface

### Configuration Page

#### **Database Configuration Section**
```
📋 Saved Database Configurations
┌─────────────────────────────────────┐
│ Select a saved configuration to load: │
│ [Create New Configuration ▼]        │
└─────────────────────────────────────┘

Configuration Name: [production]
Database Type: [PostgreSQL ▼]
Host: [prod-db-host]
Port: [5432]
Database Name: [servicenow_prod]
Username: [prod_user]
Password: [••••••••]
Connection Pool Size: [20]
Max Overflow: [30]
Echo SQL Queries: [☐]
```

#### **Configuration Actions**
- **Load Configuration**: Select from dropdown to load existing configuration
- **Create New**: Choose "Create New Configuration" to start fresh
- **Save Configuration**: Save with custom name (e.g., "production", "development", "test")

### Database Page

#### **Configuration Selector**
```
🔧 Database Configuration Selector
┌─────────────────────────────────────┐
│ Select Database Configuration:       │
│ [production ▼]                      │
│ [🔄 Switch Configuration]           │
└─────────────────────────────────────┘
```

#### **Configuration Actions**
- **Select Configuration**: Choose from dropdown of saved configurations
- **Switch Configuration**: Connect to selected database and create tables
- **Auto Table Creation**: Automatically creates tables in new database

## Configuration Types

### 1. **Production Database**
```yaml
name: production
db_type: postgresql
host: prod-db.company.com
port: 5432
database_name: servicenow_prod
username: prod_user
password: secure_password
connection_pool_size: 20
max_overflow: 30
echo: false
```

### 2. **Development Database**
```yaml
name: development
db_type: postgresql
host: dev-db.company.com
port: 5433
database_name: servicenow_dev
username: dev_user
password: dev_password
connection_pool_size: 10
max_overflow: 20
echo: true
```

### 3. **Test Database**
```yaml
name: test
db_type: sqlite
host: localhost
port: 0
database_name: servicenow_test.db
username: test_user
password: test_password
connection_pool_size: 5
max_overflow: 10
echo: false
```

## Usage Workflow

### 1. **Creating New Configuration**

1. **Navigate to Configuration Page**
   - Go to Configuration → Database tab

2. **Select "Create New Configuration"**
   - Choose from dropdown: "Create New Configuration"

3. **Enter Configuration Details**
   - Configuration Name: e.g., "staging"
   - Database Type: PostgreSQL, MySQL, or SQLite
   - Host, Port, Database Name, Username, Password
   - Connection pool settings

4. **Save Configuration**
   - Click "💾 Save Configuration"
   - Configuration saved with custom name

### 2. **Loading Existing Configuration**

1. **Navigate to Configuration Page**
   - Go to Configuration → Database tab

2. **Select Existing Configuration**
   - Choose from dropdown: e.g., "production"

3. **Configuration Loaded**
   - All fields populated with saved values
   - Make changes if needed

4. **Save Changes**
   - Click "💾 Save Configuration"
   - Updates existing configuration

### 3. **Switching Database Configuration**

1. **Navigate to Database Page**
   - Go to Database page

2. **Select Configuration**
   - Choose from dropdown: e.g., "development"

3. **Switch Configuration**
   - Click "🔄 Switch Configuration"
   - Application connects to new database
   - Tables created automatically

4. **Verification**
   - Check connection status
   - Verify database details
   - Confirm tables are created

## Technical Implementation

### Database Configuration Storage

```python
class DatabaseConfiguration(Base):
    """Database configuration storage"""
    __tablename__ = 'database_configurations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    db_type = Column(String(50), nullable=False, default='postgresql')
    host = Column(String(255), nullable=False, default='localhost')
    port = Column(Integer, nullable=False, default=5432)
    database_name = Column(String(255), nullable=False, default='sn_docs')
    username = Column(String(255), nullable=False, default='servicenow_user')
    password = Column(String(500), nullable=False)
    connection_pool_size = Column(Integer, default=10)
    max_overflow = Column(Integer, default=20)
    echo = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Configuration Management Methods

```python
# Save configuration
def save_database_configuration(self, config_data: Dict[str, Any]) -> DatabaseConfiguration

# Get all configurations
def get_all_database_configurations(self) -> List[DatabaseConfiguration]

# Get specific configuration
def get_database_configuration(self, name: str) -> DatabaseConfiguration

# Delete configuration
def delete_database_configuration(self, name: str) -> bool
```

### Database Switching Logic

```python
def switch_database_configuration(self, config_name: str):
    """Switch to a different database configuration"""
    # Load configuration
    config = self.get_database_configuration(config_name)
    
    # Build new database URL
    if config.db_type == 'postgresql':
        new_database_url = f"postgresql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database_name}"
    elif config.db_type == 'mysql':
        new_database_url = f"mysql+pymysql://{config.username}:{config.password}@{config.host}:{config.port}/{config.database_name}"
    elif config.db_type == 'sqlite':
        new_database_url = f"sqlite:///{config.database_name}"
    
    # Update engine
    self.database_url = new_database_url
    self.engine = create_engine(new_database_url, echo=config.echo)
    self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    # Create tables in new database
    self.create_tables()
```

## Configuration Examples

### Example 1: Production Environment
```yaml
Configuration Name: production
Database Type: PostgreSQL
Host: prod-db.company.com
Port: 5432
Database Name: servicenow_prod
Username: prod_user
Password: [secure_password]
Connection Pool Size: 20
Max Overflow: 30
Echo SQL Queries: false
```

### Example 2: Development Environment
```yaml
Configuration Name: development
Database Type: PostgreSQL
Host: dev-db.company.com
Port: 5433
Database Name: servicenow_dev
Username: dev_user
Password: [dev_password]
Connection Pool Size: 10
Max Overflow: 20
Echo SQL Queries: true
```

### Example 3: Local Testing
```yaml
Configuration Name: local_test
Database Type: SQLite
Host: localhost
Port: 0
Database Name: servicenow_test.db
Username: test_user
Password: [test_password]
Connection Pool Size: 5
Max Overflow: 10
Echo SQL Queries: false
```

## Error Handling

### Connection Failures
- **Invalid Host**: Shows error message with troubleshooting suggestions
- **Authentication Failed**: Displays authentication error details
- **Network Issues**: Provides network connectivity guidance

### Configuration Errors
- **Duplicate Names**: Prevents saving configurations with existing names
- **Invalid Parameters**: Validates configuration parameters before saving
- **Missing Fields**: Ensures required fields are provided

### Database Switching Issues
- **Connection Failed**: Falls back to previous configuration
- **Table Creation Failed**: Shows warning but continues with connection
- **Permission Issues**: Displays permission error details

## Best Practices

### 1. **Configuration Naming**
- Use descriptive names: "production", "development", "staging"
- Include environment: "prod-east", "dev-west", "test-local"
- Avoid generic names: "db1", "test", "new"

### 2. **Security**
- Use strong passwords for production configurations
- Store passwords securely (encrypted in database)
- Limit access to production configurations

### 3. **Connection Pool Settings**
- **Production**: Higher pool sizes (20-50 connections)
- **Development**: Moderate pool sizes (10-20 connections)
- **Testing**: Lower pool sizes (5-10 connections)

### 4. **Database Types**
- **PostgreSQL**: Recommended for production and development
- **MySQL**: Alternative for existing MySQL environments
- **SQLite**: Suitable for local testing and development

## Troubleshooting

### Common Issues

1. **Configuration Not Saving**
   - Check if configuration name already exists
   - Verify all required fields are filled
   - Ensure database connection is working

2. **Database Switching Failed**
   - Verify target database is accessible
   - Check credentials and permissions
   - Ensure database exists

3. **Tables Not Created**
   - Check database permissions
   - Verify connection is successful
   - Review error messages for details

### Debug Information

- **Configuration Source**: Shows whether using saved or default configuration
- **Connection Status**: Real-time connection testing
- **Error Details**: Specific error messages for troubleshooting
- **Logging**: Detailed application logs for debugging

## Benefits

### 1. **Flexibility**
- Switch between environments without restarting
- Test with different database configurations
- Support multiple deployment scenarios

### 2. **Efficiency**
- No application restart required
- Quick configuration switching
- Automatic table management

### 3. **Organization**
- Clear separation of environments
- Easy configuration management
- Persistent configuration storage

### 4. **Scalability**
- Support for multiple database types
- Configurable connection pools
- Environment-specific settings

## Conclusion

The multi-database configuration system provides a powerful and flexible way to manage database connections in the ServiceNow Documentation App. Users can easily create, manage, and switch between different database configurations, enabling seamless development, testing, and production workflows.

---

**Created By**: Ashish Gautam  
**LinkedIn**: [https://www.linkedin.com/in/ashishgautamkarn/](https://www.linkedin.com/in/ashishgautamkarn/)
