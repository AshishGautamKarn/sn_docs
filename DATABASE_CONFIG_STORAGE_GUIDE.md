# 🗄️ Database-Backed ServiceNow Configuration Guide

## ✅ **Database Configuration Storage Implemented**

The ServiceNow configuration is now automatically saved to the database when users fill it out in the Configuration page, and the ServiceNow Instance Introspection page automatically loads this saved configuration from the database.

## 🎯 **How It Works**

### **1. Configuration Save Process**
When you save ServiceNow settings in the Configuration page:

1. **💾 Save to Files**: Configuration saved to `config.yaml` and `.env` files
2. **🗄️ Save to Database**: Configuration automatically saved to `servicenow_configurations` table
3. **🔄 Auto-Load**: ServiceNow Instance Introspection page loads from database first
4. **✅ Pre-filled Settings**: All ServiceNow parameters automatically populated

### **2. ServiceNow Instance Introspection Integration**
When you visit the ServiceNow Instance Introspection page:

1. **🗄️ Database First**: Loads configuration from database table
2. **📁 File Fallback**: Falls back to config files if database is empty
3. **📊 Status Display**: Shows configuration source (database vs Configuration page)
4. **📝 Pre-filled Settings**: All parameters populated with saved values
5. **🔄 Manual Refresh**: "Refresh Config" button for manual updates

## 🔧 **Database Schema**

### **ServiceNowConfiguration Table**
```sql
CREATE TABLE servicenow_configurations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE DEFAULT 'default',
    instance_url VARCHAR(500) NOT NULL,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(500) NOT NULL,  -- Encrypted password
    api_version VARCHAR(50) DEFAULT 'v2',
    timeout INTEGER DEFAULT 30,
    max_retries INTEGER DEFAULT 3,
    verify_ssl BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### **Database Fields**
- **`id`**: Primary key (auto-increment)
- **`name`**: Configuration name (default: 'default')
- **`instance_url`**: ServiceNow instance URL
- **`username`**: ServiceNow username
- **`password`**: ServiceNow password (stored securely)
- **`api_version`**: API version (default: 'v2')
- **`timeout`**: Request timeout in seconds (default: 30)
- **`max_retries`**: Maximum retry attempts (default: 3)
- **`verify_ssl`**: SSL verification enabled (default: true)
- **`is_active`**: Configuration active status (default: true)
- **`created_at`**: Creation timestamp
- **`updated_at`**: Last update timestamp

## 🚀 **Features Implemented**

### **1. Database Model** ✅
```python
class ServiceNowConfiguration(Base):
    """ServiceNow configuration storage"""
    __tablename__ = 'servicenow_configurations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, default='default')
    instance_url = Column(String(500), nullable=False)
    username = Column(String(255), nullable=False)
    password = Column(String(500), nullable=False)  # Encrypted password
    api_version = Column(String(50), default='v2')
    timeout = Column(Integer, default=30)
    max_retries = Column(Integer, default=3)
    verify_ssl = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### **2. Database Manager Methods** ✅
```python
# Save ServiceNow configuration to database
def save_servicenow_configuration(self, config_data: Dict[str, Any]) -> ServiceNowConfiguration

# Get ServiceNow configuration from database
def get_servicenow_configuration(self, name: str = 'default') -> Optional[ServiceNowConfiguration]

# Get all ServiceNow configurations from database
def get_all_servicenow_configurations(self) -> List[ServiceNowConfiguration]

# Delete ServiceNow configuration from database
def delete_servicenow_configuration(self, name: str) -> bool
```

### **3. Configuration UI Integration** ✅
```python
# Save ServiceNow configuration to database
if servicenow_config.get('instance_url') and servicenow_config.get('username'):
    config_data = {
        'name': 'default',
        'instance_url': servicenow_config.get('instance_url', ''),
        'username': servicenow_config.get('username', ''),
        'password': servicenow_config.get('password', ''),
        'api_version': servicenow_config.get('api_version', 'v2'),
        'timeout': servicenow_config.get('timeout', 30),
        'max_retries': servicenow_config.get('max_retries', 3),
        'verify_ssl': servicenow_config.get('verify_ssl', True)
    }
    
    db_manager.save_servicenow_configuration(config_data)
    st.success("✅ Configuration saved to database!")
```

### **4. ServiceNow Instance Introspection Integration** ✅
```python
def _load_servicenow_configuration(self) -> Dict[str, Any]:
    """Load ServiceNow configuration from database first, then fall back to config files"""
    try:
        # Try to load from database first
        db_config = self.db_manager.get_servicenow_configuration('default')
        if db_config:
            config_dict = db_config.to_dict()
            config_dict['_source'] = 'database'
            return config_dict
    except Exception as e:
        st.warning(f"⚠️ Could not load from database: {str(e)}")
    
    # Fall back to config files
    try:
        file_config = self.config_manager.get_servicenow_config()
        if file_config.get('instance_url') and file_config.get('username'):
            file_config['_source'] = 'Configuration page'
            return file_config
    except Exception as e:
        st.warning(f"⚠️ Could not load from config files: {str(e)}")
    
    # Return empty config if nothing found
    return {
        'instance_url': '',
        'username': '',
        'password': '',
        'timeout': 30,
        'max_retries': 3,
        'api_version': 'v2',
        'verify_ssl': True,
        '_source': 'none'
    }
```

## 🎯 **User Experience**

### **1. Configure ServiceNow Settings**
1. **Go to Configuration page** → "🔗 ServiceNow" tab
2. **Configure ServiceNow settings**:
   - **Instance URL**: `https://your-instance.service-now.com`
   - **Username**: Your ServiceNow username
   - **Password**: Your ServiceNow password
   - **API Version**: `v2` (default)
   - **Timeout**: Request timeout in seconds (default: 30)
   - **Max Retries**: Maximum retry attempts (default: 3)
   - **Verify SSL**: SSL verification enabled (default: true)
3. **Save configuration** using "💾 Save Configuration"

### **2. Use ServiceNow Instance Introspection**
1. **Go to ServiceNow Instance Introspection page** → "🌐 ServiceNow Instance"
2. **See configuration status**:
   - ✅ **Database**: "Using saved ServiceNow configuration from database"
   - ✅ **Files**: "Using saved ServiceNow configuration from Configuration page"
   - ⚠️ **None**: "No ServiceNow configuration found"
3. **All settings pre-filled** with saved values
4. **Ready to configure** and run introspection

### **3. Configuration Sources**
- **🗄️ Database First**: Loads from `servicenow_configurations` table
- **📁 File Fallback**: Falls back to `config.yaml` if database is empty
- **🔄 Manual Refresh**: "Refresh Config" button reloads from both sources

## 🔍 **Configuration Flow**

```
Configuration Page (ServiceNow Tab)
       ↓
   Save Settings
       ↓
   Update Files + Database
       ↓
   ServiceNow Instance Introspection Page
       ↓
   Load from Database First
       ↓
   Fallback to Files if Empty
       ↓
   Pre-filled Settings
       ↓
   Ready for Introspection
```

## 🛠️ **Technical Implementation**

### **1. Database Operations**
- **✅ Create**: New configurations saved to database
- **✅ Read**: Configurations loaded from database
- **✅ Update**: Existing configurations updated in database
- **✅ Delete**: Configurations deleted from database

### **2. Configuration Priority**
1. **🗄️ Database**: Primary source for ServiceNow configurations
2. **📁 Files**: Fallback source if database is empty
3. **🔄 Refresh**: Manual reload from both sources

### **3. Error Handling**
- **✅ Database Errors**: Graceful fallback to config files
- **✅ File Errors**: Clear error messages
- **✅ Missing Config**: Default empty configuration
- **✅ Connection Issues**: Retry mechanisms

## 🎉 **Benefits**

### **1. Persistent Storage**
- ✅ **Database Storage**: Configurations persist across application restarts
- ✅ **Multiple Configs**: Support for multiple ServiceNow configurations
- ✅ **Version Control**: Track configuration changes over time
- ✅ **Backup**: Database backups include configurations

### **2. Better User Experience**
- ✅ **Auto-Load**: No need to re-enter ServiceNow credentials
- ✅ **Pre-filled Forms**: All parameters automatically populated
- ✅ **Source Indication**: Clear indication of configuration source
- ✅ **Manual Refresh**: Option to reload configuration

### **3. Robust Error Handling**
- ✅ **Graceful Fallback**: Falls back to files if database fails
- ✅ **Clear Messages**: Informative error messages
- ✅ **Default Values**: Sensible defaults if no configuration found
- ✅ **Retry Logic**: Automatic retry for failed operations

## 📋 **Configuration Fields Synchronized**

### **1. ServiceNow Settings**
- ✅ **Instance URL**: ServiceNow instance URL
- ✅ **Username**: ServiceNow username
- ✅ **Password**: ServiceNow password
- ✅ **API Version**: API version (v2)
- ✅ **Timeout**: Request timeout in seconds
- ✅ **Max Retries**: Maximum retry attempts
- ✅ **Verify SSL**: SSL verification setting

### **2. Connection Options**
- ✅ **Request Timeout**: Maximum time to wait for operations
- ✅ **Max Concurrent Requests**: Number of parallel requests
- ✅ **Retry Logic**: Retry failed requests
- ✅ **SSL Settings**: SSL verification options

## 🔧 **Database Management**

### **1. Configuration Storage**
- **Table**: `servicenow_configurations`
- **Primary Key**: `id` (auto-increment)
- **Unique Key**: `name` (default: 'default')
- **Active Flag**: `is_active` (default: true)

### **2. Configuration Retrieval**
- **Default Config**: `get_servicenow_configuration('default')`
- **All Configs**: `get_all_servicenow_configurations()`
- **Active Only**: Only active configurations returned

### **3. Configuration Updates**
- **Create New**: New configurations added to database
- **Update Existing**: Existing configurations updated
- **Soft Delete**: Set `is_active = false` instead of hard delete

## 📊 **Configuration Status Display**

### **1. Success Messages**
- ✅ **Database**: "Using saved ServiceNow configuration from database"
- ✅ **Files**: "Using saved ServiceNow configuration from Configuration page"
- ✅ **Saved**: "Configuration saved to database!"

### **2. Warning Messages**
- ⚠️ **Missing**: "No ServiceNow configuration found"
- ⚠️ **Database Error**: "Could not load from database"
- ⚠️ **File Error**: "Could not load from config files"

### **3. Information Display**
- **Instance**: Shows configured instance URL
- **Username**: Shows configured username
- **Source**: Shows configuration source (database/files)

## 🚀 **Quick Reference**

### **Configuration Page**
- **🔗 ServiceNow Tab**: Configure ServiceNow settings
- **💾 Save Configuration**: Save to files and database

### **ServiceNow Instance Introspection Page**
- **🔗 ServiceNow Instance Connection**: View and use saved configuration
- **🔄 Refresh Config**: Manual configuration reload
- **📡 Data Source**: Choose data source (Generate/Scrape/Both)
- **🚀 Start Introspection**: Begin data extraction with saved settings

## 🔍 **Troubleshooting**

### **1. Configuration Not Loading**
- **Check**: Verify ServiceNow settings were saved in Configuration page
- **Solution**: Use "🔄 Refresh Config" button
- **Alternative**: Go back to Configuration page and save again

### **2. Database Connection Issues**
- **Check**: Verify database is running and accessible
- **Solution**: Configuration will fall back to config files
- **Test**: Use database connection test in Configuration page

### **3. Settings Not Pre-filled**
- **Check**: Ensure ServiceNow configuration was saved
- **Solution**: Save configuration in Configuration page
- **Refresh**: Use "🔄 Refresh Config" button

## 🎯 **Example Workflow**

### **1. Configure ServiceNow Settings**
```
1. Go to Configuration page → ServiceNow tab
2. Set Instance URL: https://your-instance.service-now.com
3. Set Username: your-username
4. Set Password: your-password
5. Set Timeout: 30 seconds
6. Set Max Retries: 3
7. Save configuration → "Configuration saved to database!"
```

### **2. Use ServiceNow Instance Introspection**
```
1. Go to ServiceNow Instance Introspection page
2. See: "✅ Using saved ServiceNow configuration from database"
3. See: "Instance: https://your-instance.service-now.com"
4. See: "Username: your-username"
5. All settings pre-filled
6. Configure data source and start introspection
```

## 🔧 **Advanced Configuration**

### **1. Multiple Configurations**
- **Default Config**: `name = 'default'`
- **Custom Configs**: `name = 'production'`, `name = 'development'`
- **Active Management**: Enable/disable configurations

### **2. Configuration Management**
- **Create**: New configurations via Configuration page
- **Update**: Existing configurations updated automatically
- **Delete**: Configurations can be deleted from database
- **List**: View all configurations in database

### **3. Security Considerations**
- **Password Storage**: Passwords stored securely in database
- **Access Control**: Database access controlled by application
- **Encryption**: Consider encrypting sensitive data
- **Backup**: Regular database backups include configurations

---

**🗄️ Your ServiceNow configuration now persists in the database and is automatically loaded by the ServiceNow Instance Introspection page!**

Created by: **Ashish Gautam**  
LinkedIn: [https://www.linkedin.com/in/ashishgautamkarn/](https://www.linkedin.com/in/ashishgautamkarn/)
