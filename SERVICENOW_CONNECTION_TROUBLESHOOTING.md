# 🔍 ServiceNow Connection Troubleshooting Guide

## ❌ **Error**: `Failed to resolve 'your-instance.servicenow.com'`

This error indicates that the hostname `your-instance.servicenow.com` cannot be resolved by DNS.

## 🔍 **Possible Causes**

### **1. Incorrect Instance URL**
- The instance URL might be wrong or incomplete
- Missing `https://` prefix
- Wrong domain format

### **2. Instance Doesn't Exist**
- The ServiceNow instance might not exist
- The instance might have been deactivated
- The instance might be in a different region

### **3. Network Issues**
- DNS resolution problems
- Firewall blocking the connection
- Corporate network restrictions

## ✅ **Solutions**

### **1. Verify Instance URL Format**
```
✅ Correct formats:
- https://yourcompany.service-now.com
- https://yourcompany.servicenow.com
- https://yourcompany.now.com

❌ Incorrect formats:
- your-instance.servicenow.com (missing https://)
- http://your-instance.servicenow.com (should be https://)
- your-instance.service-now.com (wrong domain)
```

### **2. Check Instance Existence**
1. **Try accessing in browser**: Open `https://your-instance.servicenow.com` in your browser
2. **Check with administrator**: Contact your ServiceNow administrator
3. **Verify company name**: Ensure `your-instance` is the correct company identifier

### **3. Test Network Connectivity**
```bash
# Test DNS resolution
nslookup your-instance.servicenow.com

# Test connectivity
ping your-instance.servicenow.com

# Test HTTPS access
curl -I https://your-instance.servicenow.com
```

### **4. Common ServiceNow URL Patterns**
- **Company Name**: Usually your company's name or abbreviation
- **Domain**: `.service-now.com`, `.servicenow.com`, or `.now.com`
- **Protocol**: Always `https://`

## 🔧 **Step-by-Step Fix**

### **Step 1: Verify the URL**
1. Open your browser
2. Try to access: `https://your-instance.servicenow.com`
3. If it doesn't work, try: `https://your-instance.service-now.com`

### **Step 2: Check with Administrator**
1. Contact your ServiceNow administrator
2. Ask for the correct instance URL
3. Verify your account is active

### **Step 3: Try Alternative Formats**
```
Try these variations:
- https://your-instance.service-now.com
- https://your-instance.now.com
- https://yourcompany.service-now.com
- https://yourcompany.servicenow.com
```

### **Step 4: Network Troubleshooting**
1. **Check internet connection**
2. **Try from different network** (mobile hotspot)
3. **Check firewall settings**
4. **Contact IT department** if behind corporate firewall

## 🎯 **Quick Test**

### **Test in Browser**
1. Open browser
2. Go to: `https://your-instance.servicenow.com`
3. If you see ServiceNow login page → URL is correct
4. If you get DNS error → URL is wrong

### **Test with curl**
```bash
curl -I https://your-instance.servicenow.com
```

### **Test DNS Resolution**
```bash
nslookup your-instance.servicenow.com
```

## 📞 **Getting Help**

### **1. Contact ServiceNow Administrator**
- Ask for correct instance URL
- Verify account status
- Check permissions

### **2. Check ServiceNow Documentation**
- Company ServiceNow documentation
- IT department resources
- ServiceNow community forums

### **3. Verify Account Access**
- Try logging into ServiceNow web interface
- Check if account is active
- Verify username and password

## 🎉 **Expected Result**

Once you have the correct URL, the connection test should show:
```
✅ Connection successful
Response time: X.XX seconds
```

---

**🔍 The most likely issue is that `your-instance.servicenow.com` is not the correct ServiceNow instance URL for your organization.**
