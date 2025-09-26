# 🔗 ServiceNow Hybrid Introspection Guide

## Overview

The ServiceNow Hybrid Introspection feature combines REST API and direct database access to provide comprehensive analysis of ServiceNow instances. This advanced tool offers deeper insights by correlating data from both sources.

## 🚀 Features

### **Hybrid Data Access**
- **REST API Integration**: Real-time data from ServiceNow instance
- **Database Direct Access**: Direct connection to underlying database
- **Data Correlation**: Cross-reference and validate data between sources
- **Enhanced Security**: Secure credential management and validation

### **Security Features**
- ✅ **No Hardcoded Credentials**: All sensitive data loaded from environment variables
- ✅ **Environment-Based Configuration**: Secure credential management
- ✅ **Database Connection Pooling**: Secure and efficient database connections
- ✅ **Input Validation**: Comprehensive input sanitization
- ✅ **Error Handling**: Secure error messages without sensitive information
- ✅ **Rate Limiting**: Prevents abuse and ensures system stability
- ✅ **Query Validation**: Prevents SQL injection and dangerous operations

## 🔧 Configuration

### **Environment Variables**

Add the following variables to your `.env` file:

```env
# ServiceNow REST API Configuration
SN_INSTANCE_URL=https://your-instance.service-now.com
SN_USERNAME=your_username
SN_PASSWORD=your_password

# ServiceNow Database Configuration
SN_DB_CONNECTION_STRING=postgresql://username:password@host:port/database
SN_DB_HOST=localhost
SN_DB_PORT=5432
SN_DB_NAME=servicenow
SN_DB_USER=servicenow_user
SN_DB_PASSWORD=your_db_password

# Hybrid Introspection Settings
SN_DB_CONNECTION_TIMEOUT=30
SN_DB_MAX_RETRIES=3
SN_DB_RETRY_DELAY=5
SN_DB_POOL_SIZE=5
SN_DB_MAX_OVERFLOW=10
SN_DB_POOL_TIMEOUT=30
SN_DB_POOL_RECYCLE=3600
SN_DB_ECHO=false

# Rate Limiting
SN_DB_RATE_LIMIT_REQUESTS=100
SN_DB_RATE_LIMIT_WINDOW=60

# Security Settings
SN_DB_ENABLE_SSL=true
SN_DB_VERIFY_SSL=true
SN_DB_ALLOWED_HOSTS=localhost,127.0.0.1
```

### **Database Connection Strings**

#### **PostgreSQL**
```
postgresql://username:password@host:port/database
```

#### **MySQL**
```
mysql+pymysql://username:password@host:port/database
```

#### **SQL Server**
```
mssql+pyodbc://username:password@host:port/database?driver=ODBC+Driver+17+for+SQL+Server
```

#### **Oracle**
```
oracle://username:password@host:port/database
```

## 🎯 Usage

### **1. Access Hybrid Introspection**
1. Navigate to **🔗 Hybrid Introspection** in the main menu
2. Configure your connections in the respective tabs
3. Test connections before starting introspection

### **2. Connection Types**

#### **REST API Only**
- Configure ServiceNow instance URL and credentials
- Test connection to ensure proper authentication
- Extract data via REST API endpoints

#### **Database Only**
- Configure database connection string
- Validate ServiceNow database detection
- Extract data directly from database tables

#### **Hybrid Mode (Recommended)**
- Configure both REST API and database connections
- Enable data correlation for comprehensive analysis
- Get enhanced insights from both sources

### **3. Data Analysis**

#### **Database Data**
- **Modules**: Applications and plugins from `sys_app` table
- **Roles**: User roles from `sys_user_role` table
- **Properties**: System properties from `sys_properties` table
- **Tables**: Database objects from `sys_db_object` table

#### **API Data**
- **Modules**: Real-time application data
- **Roles**: Current role configurations
- **Tables**: Live table information
- **Properties**: Current system properties

#### **Correlation Results**
- **Matched Items**: Data found in both sources
- **Database Only**: Items only in database
- **API Only**: Items only in API
- **Correlation Score**: Overall data consistency

## 🔒 Security Considerations

### **Database Access Requirements**
- **Read-only access** to ServiceNow database
- **Proper permissions** for system tables
- **Network connectivity** to database server
- **Database credentials** with appropriate privileges

### **ServiceNow Instance Requirements**
- **REST API access** with proper permissions
- **Valid credentials** with necessary roles
- **Network connectivity** to ServiceNow instance
- **HTTPS connection** for secure communication

### **Security Best Practices**
1. **Use environment variables** for all credentials
2. **Enable SSL/TLS** for all connections
3. **Implement rate limiting** to prevent abuse
4. **Validate all inputs** before processing
5. **Log security events** for monitoring
6. **Regular credential rotation** for enhanced security

## 📊 Data Models

### **Hybrid Data Structure**
```json
{
  "instance_info": {
    "db_type": "postgresql",
    "version": "Tokyo",
    "instance_type": "Production"
  },
  "database_data": {
    "modules": [...],
    "roles": [...],
    "properties": [...],
    "tables": [...]
  },
  "api_data": {
    "modules": [...],
    "roles": [...],
    "properties": [...],
    "tables": [...]
  },
  "correlation_results": {
    "matched_items": 150,
    "database_only": 25,
    "api_only": 10,
    "correlation_score": 0.85
  },
  "summary": {
    "total_items": 185,
    "database_items": 175,
    "api_items": 160,
    "correlation_score": 0.85,
    "errors_count": 0
  }
}
```

## 🛠️ Troubleshooting

### **Common Issues**

#### **Connection Failures**
- **Database**: Check connection string format and credentials
- **REST API**: Verify instance URL and authentication
- **Network**: Ensure proper network connectivity

#### **Permission Errors**
- **Database**: Grant read-only access to required tables
- **REST API**: Check user roles and permissions
- **ServiceNow**: Verify user has necessary access rights

#### **Data Correlation Issues**
- **Low correlation score**: Check data consistency between sources
- **Missing data**: Verify table access and query permissions
- **Version mismatch**: Ensure compatible ServiceNow versions

### **Debug Mode**
Enable debug logging by setting:
```env
SN_DB_LOG_LEVEL=DEBUG
SN_DB_ECHO=true
```

## 📈 Performance Optimization

### **Database Optimization**
- **Connection pooling**: Configure appropriate pool sizes
- **Query optimization**: Use indexed columns in WHERE clauses
- **Batch processing**: Process data in chunks for large datasets

### **API Optimization**
- **Rate limiting**: Respect ServiceNow API limits
- **Caching**: Cache frequently accessed data
- **Parallel processing**: Use async operations where possible

## 🔄 Maintenance

### **Regular Tasks**
1. **Monitor connection health** and performance
2. **Update credentials** as needed
3. **Review security logs** for anomalies
4. **Test connections** after system updates
5. **Backup configuration** settings

### **Updates**
- **Keep dependencies** up to date
- **Monitor ServiceNow changes** that might affect compatibility
- **Test new features** in development environment
- **Document changes** for team reference

## 📚 Additional Resources

- **ServiceNow REST API Documentation**: [https://developer.servicenow.com/dev.do](https://developer.servicenow.com/dev.do)
- **Database Connection Guides**: See project documentation
- **Security Best Practices**: Review security audit reports
- **Troubleshooting Guides**: Check project troubleshooting documentation

## 🆘 Support

For issues or questions:
1. **Check logs** for error details
2. **Review configuration** settings
3. **Test connections** individually
4. **Contact support** with detailed error information

---

**Created by**: Ashish Gautam  
**LinkedIn**: [https://www.linkedin.com/in/ashishgautamkarn/](https://www.linkedin.com/in/ashishgautamkarn/)  
**Last Updated**: December 2024
