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
SN_DB_CONNECTION_STRING=postgresql://user:password@host:port/database"instance_info": {
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

- **ServiceNow REST API Documentation**: [https://your-instance.service-now.com