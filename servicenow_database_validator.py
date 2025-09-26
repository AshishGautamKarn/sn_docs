"""
ServiceNow Database Validator
Secure validation and verification for ServiceNow database connections and operations
"""

import os
import logging
import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import requests
from urllib.parse import urlparse


class ServiceNowDatabaseValidator:
    """Secure validator for ServiceNow database connections and operations"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        
        # Security: Validation patterns
        self.valid_url_patterns = [
            r'^https://[a-zA-Z0-9.-]+\.service-now\.com/?$',
            r'^https://[a-zA-Z0-9.-]+\.servicenow\.com/?$',
            r'^https://[a-zA-Z0-9.-]+\.now\.com/?$'
        ]
        
        self.valid_db_patterns = [
            r'^postgresql://[^:]+:[^@]+@[^:]+:\d+/[^?]+$',
            r'^mysql://[^:]+:[^@]+@[^:]+:\d+/[^?]+$',
            r'^mysql\+pymysql://[^:]+:[^@]+@[^:]+:\d+/[^?]+$',
            r'^mssql://[^:]+:[^@]+@[^:]+:\d+/[^?]+$',
            r'^oracle://[^:]+:[^@]+@[^:]+:\d+/[^?]+$'
        ]
        
        # Security: Dangerous patterns to block
        self.dangerous_patterns = [
            r'DROP\s+TABLE',
            r'DELETE\s+FROM',
            r'UPDATE\s+.*SET',
            r'INSERT\s+INTO',
            r'ALTER\s+TABLE',
            r'CREATE\s+TABLE',
            r'TRUNCATE\s+TABLE',
            r'EXEC\s+',
            r'EXECUTE\s+',
            r'UNION\s+SELECT',
            r'--',
            r'/\*.*\*/',
            r';\s*$',
            r'<script',
            r'javascript:',
            r'vbscript:',
            r'data:'
        ]
        
        # Security: ServiceNow-specific validation
        self.servicenow_required_tables = [
            'sys_user',
            'sys_user_role',
            'sys_app',
            'sys_properties',
            'sys_db_object'
        ]
        
        self.servicenow_optional_tables = [
            'sysauto_script',
            'sys_script',
            'sys_security_acl',
            'sys_dictionary',
            'sys_db_object_relationship'
        ]
    
    def _setup_logger(self) -> logging.Logger:
        """Setup secure logging"""
        logger = logging.getLogger('servicenow_database_validator')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def validate_instance_url(self, url: str) -> Dict[str, Any]:
        """Validate ServiceNow instance URL"""
        try:
            validation_result = {
                'is_valid': False,
                'errors': [],
                'warnings': [],
                'sanitized_url': None
            }
            
            if not url:
                validation_result['errors'].append("URL is required")
                return validation_result
            
            # Security: Basic URL validation
            try:
                parsed = urlparse(url)
                if not parsed.scheme or not parsed.netloc:
                    validation_result['errors'].append("Invalid URL format")
                    return validation_result
            except Exception as e:
                validation_result['errors'].append(f"URL parsing error: {str(e)}")
                return validation_result
            
            # Security: Check for dangerous patterns
            if self._contains_dangerous_patterns(url):
                validation_result['errors'].append("URL contains dangerous patterns")
                return validation_result
            
            # Security: Validate ServiceNow URL patterns
            is_valid_servicenow = False
            for pattern in self.valid_url_patterns:
                if re.match(pattern, url, re.IGNORECASE):
                    is_valid_servicenow = True
                    break
            
            if not is_valid_servicenow:
                validation_result['warnings'].append("URL does not match standard ServiceNow patterns")
            
            # Security: Sanitize URL
            sanitized_url = self._sanitize_url(url)
            validation_result['sanitized_url'] = sanitized_url
            
            # Security: Test connectivity
            connectivity_test = self._test_url_connectivity(sanitized_url)
            if not connectivity_test['success']:
                validation_result['errors'].append(f"Connectivity test failed: {connectivity_test['error']}")
            else:
                validation_result['is_valid'] = True
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating instance URL: {e}")
            return {
                'is_valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': [],
                'sanitized_url': None
            }
    
    def validate_database_connection_string(self, connection_string: str) -> Dict[str, Any]:
        """Validate database connection string"""
        try:
            validation_result = {
                'is_valid': False,
                'errors': [],
                'warnings': [],
                'sanitized_connection_string': None,
                'db_type': None,
                'parsed_components': {}
            }
            
            if not connection_string:
                validation_result['errors'].append("Connection string is required")
                return validation_result
            
            # Security: Check for dangerous patterns
            if self._contains_dangerous_patterns(connection_string):
                validation_result['errors'].append("Connection string contains dangerous patterns")
                return validation_result
            
            # Security: Validate connection string format
            is_valid_format = False
            for pattern in self.valid_db_patterns:
                if re.match(pattern, connection_string, re.IGNORECASE):
                    is_valid_format = True
                    break
            
            if not is_valid_format:
                validation_result['errors'].append("Invalid connection string format")
                return validation_result
            
            # Security: Parse and validate components
            try:
                parsed = urlparse(connection_string)
                validation_result['parsed_components'] = {
                    'scheme': parsed.scheme,
                    'hostname': parsed.hostname,
                    'port': parsed.port,
                    'database': parsed.path.lstrip('/'),
                    'username': parsed.username
                }
                
                # Determine database type
                if parsed.scheme.startswith('postgresql'):
                    validation_result['db_type'] = 'postgresql'
                elif parsed.scheme.startswith('mysql'):
                    validation_result['db_type'] = 'mysql'
                elif parsed.scheme.startswith('mssql'):
                    validation_result['db_type'] = 'mssql'
                elif parsed.scheme.startswith('oracle'):
                    validation_result['db_type'] = 'oracle'
                else:
                    validation_result['warnings'].append(f"Unknown database type: {parsed.scheme}")
                
            except Exception as e:
                validation_result['errors'].append(f"Error parsing connection string: {str(e)}")
                return validation_result
            
            # Security: Sanitize connection string
            sanitized_connection_string = self._sanitize_connection_string(connection_string)
            validation_result['sanitized_connection_string'] = sanitized_connection_string
            
            # Security: Test database connection
            connection_test = self._test_database_connection(sanitized_connection_string)
            if not connection_test['success']:
                validation_result['errors'].append(f"Database connection test failed: {connection_test['error']}")
            else:
                validation_result['is_valid'] = True
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating database connection string: {e}")
            return {
                'is_valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': [],
                'sanitized_connection_string': None,
                'db_type': None,
                'parsed_components': {}
            }
    
    def validate_credentials(self, username: str, password: str) -> Dict[str, Any]:
        """Validate ServiceNow credentials"""
        try:
            validation_result = {
                'is_valid': False,
                'errors': [],
                'warnings': [],
                'security_score': 0
            }
            
            # Security: Check for empty credentials
            if not username or not password:
                validation_result['errors'].append("Username and password are required")
                return validation_result
            
            # Security: Check for dangerous patterns
            if self._contains_dangerous_patterns(username) or self._contains_dangerous_patterns(password):
                validation_result['errors'].append("Credentials contain dangerous patterns")
                return validation_result
            
            # Security: Validate username format
            if not self._validate_username_format(username):
                validation_result['errors'].append("Invalid username format")
                return validation_result
            
            # Security: Validate password strength
            password_validation = self._validate_password_strength(password)
            validation_result['security_score'] = password_validation['score']
            
            if password_validation['score'] < 3:
                validation_result['warnings'].append("Password strength is weak")
            
            # Security: Check for common weak passwords
            if self._is_weak_password(password):
                validation_result['warnings'].append("Password appears to be weak")
            
            validation_result['is_valid'] = True
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating credentials: {e}")
            return {
                'is_valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': [],
                'security_score': 0
            }
    
    def validate_servicenow_database(self, connection_string: str) -> Dict[str, Any]:
        """Validate if database is a ServiceNow instance"""
        try:
            validation_result = {
                'is_servicenow': False,
                'confidence_score': 0,
                'version': None,
                'instance_type': None,
                'missing_tables': [],
                'found_tables': [],
                'errors': []
            }
            
            # Security: Validate connection string first
            conn_validation = self.validate_database_connection_string(connection_string)
            if not conn_validation['is_valid']:
                validation_result['errors'].extend(conn_validation['errors'])
                return validation_result
            
            # Security: Test database connection
            try:
                engine = create_engine(connection_string, pool_pre_ping=True)
                with engine.connect() as conn:
                    # Check for ServiceNow required tables
                    for table in self.servicenow_required_tables:
                        try:
                            result = conn.execute(text(f"""
                                SELECT COUNT(*) 
                                FROM information_schema.tables 
                                WHERE table_name = :table_name
                            """), {'table_name': table})
                            
                            if result.scalar() > 0:
                                validation_result['found_tables'].append(table)
                            else:
                                validation_result['missing_tables'].append(table)
                        except Exception as e:
                            validation_result['errors'].append(f"Error checking table {table}: {str(e)}")
                    
                    # Check for optional tables
                    for table in self.servicenow_optional_tables:
                        try:
                            result = conn.execute(text(f"""
                                SELECT COUNT(*) 
                                FROM information_schema.tables 
                                WHERE table_name = :table_name
                            """), {'table_name': table})
                            
                            if result.scalar() > 0:
                                validation_result['found_tables'].append(table)
                        except Exception as e:
                            # Optional tables, don't add to errors
                            pass
                    
                    # Calculate confidence score
                    required_found = len(validation_result['found_tables'])
                    required_total = len(self.servicenow_required_tables)
                    validation_result['confidence_score'] = required_found / required_total
                    validation_result['is_servicenow'] = validation_result['confidence_score'] >= 0.8
                    
                    # Try to detect version
                    if validation_result['is_servicenow']:
                        try:
                            version_result = conn.execute(text("""
                                SELECT value 
                                FROM sys_properties 
                                WHERE name = 'glide.buildname' 
                                LIMIT 1
                            """))
                            version = version_result.scalar()
                            if version:
                                validation_result['version'] = version
                        except Exception as e:
                            validation_result['errors'].append(f"Error detecting version: {str(e)}")
                    
                    # Detect instance type
                    if 'sys_app' in validation_result['found_tables']:
                        validation_result['instance_type'] = 'Production'
                    else:
                        validation_result['instance_type'] = 'Development'
                
            except SQLAlchemyError as e:
                validation_result['errors'].append(f"Database connection error: {str(e)}")
            except Exception as e:
                validation_result['errors'].append(f"Unexpected error: {str(e)}")
            
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating ServiceNow database: {e}")
            return {
                'is_servicenow': False,
                'confidence_score': 0,
                'version': None,
                'instance_type': None,
                'missing_tables': [],
                'found_tables': [],
                'errors': [f"Validation error: {str(e)}"]
            }
    
    def validate_query(self, query: str) -> Dict[str, Any]:
        """Validate SQL query for security"""
        try:
            validation_result = {
                'is_valid': False,
                'errors': [],
                'warnings': [],
                'sanitized_query': None
            }
            
            if not query:
                validation_result['errors'].append("Query is required")
                return validation_result
            
            # Security: Check for dangerous patterns
            if self._contains_dangerous_patterns(query):
                validation_result['errors'].append("Query contains dangerous patterns")
                return validation_result
            
            # Security: Check for read-only operations
            if not self._is_read_only_query(query):
                validation_result['errors'].append("Only read-only queries are allowed")
                return validation_result
            
            # Security: Sanitize query
            sanitized_query = self._sanitize_query(query)
            validation_result['sanitized_query'] = sanitized_query
            
            validation_result['is_valid'] = True
            return validation_result
            
        except Exception as e:
            self.logger.error(f"Error validating query: {e}")
            return {
                'is_valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'warnings': [],
                'sanitized_query': None
            }
    
    def _contains_dangerous_patterns(self, text: str) -> bool:
        """Check if text contains dangerous patterns"""
        if not text:
            return False
        
        text_upper = text.upper()
        for pattern in self.dangerous_patterns:
            if re.search(pattern, text_upper, re.IGNORECASE):
                return True
        
        return False
    
    def _sanitize_url(self, url: str) -> str:
        """Sanitize URL input"""
        if not url:
            return url
        
        # Security: Remove potential injection attempts
        url = url.strip()
        url = re.sub(r'[<>"\']', '', url)
        
        # Security: Ensure HTTPS
        if not url.startswith('https://'):
            url = f"https://{url}"
        
        # Security: Remove trailing slash
        url = url.rstrip('/')
        
        return url
    
    def _sanitize_connection_string(self, conn_str: str) -> str:
        """Sanitize database connection string"""
        if not conn_str:
            return conn_str
        
        # Security: Basic sanitization
        conn_str = conn_str.strip()
        conn_str = re.sub(r'[<>"\']', '', conn_str)
        
        return conn_str
    
    def _sanitize_query(self, query: str) -> str:
        """Sanitize SQL query"""
        if not query:
            return query
        
        # Security: Remove comments
        query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        
        # Security: Remove extra whitespace
        query = re.sub(r'\s+', ' ', query).strip()
        
        return query
    
    def _test_url_connectivity(self, url: str) -> Dict[str, Any]:
        """Test URL connectivity"""
        try:
            # Security: Set timeout and headers
            headers = {
                'User-Agent': 'ServiceNow-Docs-Validator/1.0',
                'Accept': 'application/json'
            }
            
            response = requests.get(
                url, 
                headers=headers, 
                timeout=10, 
                verify=True,
                allow_redirects=False
            )
            
            return {
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'error': None
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'status_code': None,
                'error': str(e)
            }
    
    def _test_database_connection(self, connection_string: str) -> Dict[str, Any]:
        """Test database connection"""
        try:
            engine = create_engine(connection_string, pool_pre_ping=True)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            return {
                'success': True,
                'error': None
            }
            
        except SQLAlchemyError as e:
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_username_format(self, username: str) -> bool:
        """Validate username format"""
        if not username:
            return False
        
        # Security: Check minimum length
        if len(username) < 3:
            return False
        
        # Security: Check for valid characters
        if not re.match(r'^[a-zA-Z0-9._-]+$', username):
            return False
        
        return True
    
    def _validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        score = 0
        feedback = []
        
        if not password:
            return {'score': 0, 'feedback': ['Password is required']}
        
        # Length check
        if len(password) >= 8:
            score += 1
        else:
            feedback.append('Password should be at least 8 characters long')
        
        # Character variety checks
        if re.search(r'[a-z]', password):
            score += 1
        else:
            feedback.append('Password should contain lowercase letters')
        
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            feedback.append('Password should contain uppercase letters')
        
        if re.search(r'[0-9]', password):
            score += 1
        else:
            feedback.append('Password should contain numbers')
        
        if re.search(r'[^a-zA-Z0-9]', password):
            score += 1
        else:
            feedback.append('Password should contain special characters')
        
        return {'score': score, 'feedback': feedback}
    
    def _is_weak_password(self, password: str) -> bool:
        """Check if password is weak"""
        weak_passwords = [
            'password', '123456', 'admin', 'root', 'user',
            'test', 'demo', 'guest', 'servicenow', 'now'
        ]
        
        password_lower = password.lower()
        return password_lower in weak_passwords or len(password) < 6
    
    def _is_read_only_query(self, query: str) -> bool:
        """Check if query is read-only"""
        query_upper = query.upper()
        
        # Security: Check for write operations
        write_operations = [
            'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE',
            'ALTER', 'TRUNCATE', 'EXEC', 'EXECUTE'
        ]
        
        for operation in write_operations:
            if operation in query_upper:
                return False
        
        return True
    
    def get_validation_summary(self, validation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get summary of multiple validation results"""
        try:
            summary = {
                'total_validations': len(validation_results),
                'successful_validations': 0,
                'failed_validations': 0,
                'total_errors': 0,
                'total_warnings': 0,
                'overall_success': False
            }
            
            for result in validation_results:
                if result.get('is_valid', False):
                    summary['successful_validations'] += 1
                else:
                    summary['failed_validations'] += 1
                
                summary['total_errors'] += len(result.get('errors', []))
                summary['total_warnings'] += len(result.get('warnings', []))
            
            summary['overall_success'] = summary['failed_validations'] == 0
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating validation summary: {e}")
            return {
                'total_validations': 0,
                'successful_validations': 0,
                'failed_validations': 0,
                'total_errors': 0,
                'total_warnings': 0,
                'overall_success': False
            }
