"""
ServiceNow Database Connector
Secure connector for ServiceNow database operations with hybrid REST API + Database access
"""

import os
import logging
import hashlib
import secrets
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, MetaData, Table, Column, String, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import requests
from urllib.parse import urlparse
import json
import re


class ServiceNowDatabaseConnector:
    """Secure ServiceNow database connector with hybrid REST API + Database access"""
    
    def __init__(self, instance_url: str = None, db_connection_string: str = None):
        """
        Initialize ServiceNow database connector
        
        Args:
            instance_url: ServiceNow instance URL (from environment or parameter)
            db_connection_string: Database connection string (from environment or parameter)
        """
        self.logger = self._setup_logger()
        self.instance_url = instance_url or os.getenv('SN_INSTANCE_URL', '')
        self.db_connection_string = db_connection_string or os.getenv('SN_DB_CONNECTION_STRING', '')
        
        # Security: Validate inputs
        self._validate_inputs()
        
        # Initialize connections
        self.db_engine = None
        self.db_session = None
        self.api_client = None
        self.connection_established = False
        self.last_connection_test = None
        
        # Security: Connection timeout and retry settings
        self.connection_timeout = int(os.getenv('SN_DB_CONNECTION_TIMEOUT', '30'))
        self.max_retries = int(os.getenv('SN_DB_MAX_RETRIES', '3'))
        self.retry_delay = int(os.getenv('SN_DB_RETRY_DELAY', '5'))
        
        # Security: Rate limiting
        self.rate_limit_requests = int(os.getenv('SN_DB_RATE_LIMIT_REQUESTS', '100'))
        self.rate_limit_window = int(os.getenv('SN_DB_RATE_LIMIT_WINDOW', '60'))
        self.request_timestamps = []
    
    def _setup_logger(self) -> logging.Logger:
        """Setup secure logging for ServiceNow database connector"""
        logger = logging.getLogger('servicenow_database_connector')
        logger.setLevel(logging.INFO)
        
        # Security: Don't log sensitive information
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _validate_inputs(self):
        """Validate and sanitize input parameters"""
        # Security: Input validation
        if not self.instance_url:
            raise ValueError("ServiceNow instance URL is required")
        
        if not self.db_connection_string:
            raise ValueError("Database connection string is required")
        
        # Security: URL validation
        if not self._is_valid_url(self.instance_url):
            raise ValueError("Invalid ServiceNow instance URL format")
        
        # Security: Connection string validation
        if not self._is_valid_connection_string(self.db_connection_string):
            raise ValueError("Invalid database connection string format")
        
        # Security: Sanitize inputs
        self.instance_url = self._sanitize_url(self.instance_url)
        self.db_connection_string = self._sanitize_connection_string(self.db_connection_string)
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _is_valid_connection_string(self, conn_str: str) -> bool:
        """Validate database connection string format"""
        try:
            # Check for common database connection string patterns
            valid_patterns = [
                r'postgresql://',
                r'mysql://',
                r'mysql\+pymysql://',
                r'mssql://',
                r'oracle://'
            ]
            return any(re.match(pattern, conn_str) for pattern in valid_patterns)
        except Exception:
            return False
    
    def _sanitize_url(self, url: str) -> str:
        """Sanitize URL input"""
        # Security: Remove potential injection attempts
        url = url.strip()
        # Remove any potential SQL injection or script injection attempts
        url = re.sub(r'[<>"\']', '', url)
        return url
    
    def _sanitize_connection_string(self, conn_str: str) -> str:
        """Sanitize database connection string"""
        # Security: Basic sanitization
        conn_str = conn_str.strip()
        # Remove any potential injection attempts
        conn_str = re.sub(r'[<>"\']', '', conn_str)
        return conn_str
    
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        current_time = datetime.now()
        
        # Remove old timestamps outside the window
        self.request_timestamps = [
            ts for ts in self.request_timestamps 
            if current_time - ts < timedelta(seconds=self.rate_limit_window)
        ]
        
        # Check if we're within limits
        if len(self.request_timestamps) >= self.rate_limit_requests:
            return False
        
        # Add current timestamp
        self.request_timestamps.append(current_time)
        return True
    
    def _secure_connection_string(self, connection_string: str) -> str:
        """Create a secure connection string with proper encoding"""
        try:
            from urllib.parse import urlparse, urlunparse, quote_plus
            
            parsed = urlparse(connection_string)
            
            # Security: Properly encode username and password
            if parsed.username:
                username = quote_plus(parsed.username)
            else:
                username = parsed.username
                
            if parsed.password:
                password = quote_plus(parsed.password)
            else:
                password = parsed.password
            
            # Rebuild connection string with encoded credentials
            secure_parsed = parsed._replace(
                netloc=f"{username}:{password}@{parsed.hostname}:{parsed.port}" if username else f"{parsed.hostname}:{parsed.port}"
            )
            
            return urlunparse(secure_parsed)
            
        except Exception as e:
            self.logger.error(f"Error securing connection string: {e}")
            return connection_string
    
    def establish_connections(self) -> Dict[str, Any]:
        """Establish secure connections to both database and REST API"""
        try:
            # Security: Check rate limits
            if not self._check_rate_limit():
                raise Exception("Rate limit exceeded. Please wait before retrying.")
            
            results = {
                'database_connected': False,
                'api_connected': False,
                'errors': []
            }
            
            # Establish database connection
            try:
                self._establish_database_connection()
                results['database_connected'] = True
                self.logger.info("Database connection established successfully")
            except Exception as e:
                error_msg = f"Database connection failed: {str(e)}"
                results['errors'].append(error_msg)
                self.logger.error(error_msg)
            
            # Establish REST API connection
            try:
                self._establish_api_connection()
                results['api_connected'] = True
                self.logger.info("REST API connection established successfully")
            except Exception as e:
                error_msg = f"REST API connection failed: {str(e)}"
                results['errors'].append(error_msg)
                self.logger.error(error_msg)
            
            # Update connection status
            self.connection_established = results['database_connected'] or results['api_connected']
            self.last_connection_test = datetime.now()
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error establishing connections: {e}")
            return {
                'database_connected': False,
                'api_connected': False,
                'errors': [f"Connection establishment failed: {str(e)}"]
            }
    
    def _establish_database_connection(self):
        """Establish secure database connection"""
        try:
            # Security: Use secure connection string
            secure_conn_str = self._secure_connection_string(self.db_connection_string)
            
            # Security: Connection pooling with secure settings
            self.db_engine = create_engine(
                secure_conn_str,
                pool_size=int(os.getenv('SN_DB_POOL_SIZE', '5')),
                max_overflow=int(os.getenv('SN_DB_MAX_OVERFLOW', '10')),
                pool_timeout=int(os.getenv('SN_DB_POOL_TIMEOUT', '30')),
                pool_recycle=int(os.getenv('SN_DB_POOL_RECYCLE', '3600')),
                echo=os.getenv('SN_DB_ECHO', 'false').lower() == 'true',
                connect_args={
                    'connect_timeout': self.connection_timeout,
                    'application_name': 'servicenow_docs_connector'
                }
            )
            
            # Test connection
            with self.db_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # Create session
            Session = sessionmaker(bind=self.db_engine)
            self.db_session = Session()
            
        except SQLAlchemyError as e:
            raise Exception(f"Database connection error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected database error: {str(e)}")
    
    def _establish_api_connection(self):
        """Establish secure REST API connection"""
        try:
            # Security: Get credentials from environment
            username = os.getenv('SN_USERNAME', '')
            password = os.getenv('SN_PASSWORD', '')
            
            if not username or not password:
                raise Exception("ServiceNow credentials not found in environment variables")
            
            # Security: Validate credentials format
            if not self._validate_credentials(username, password):
                raise Exception("Invalid credentials format")
            
            # Create API client
            self.api_client = ServiceNowAPIClient(self.instance_url, username, password)
            
            # Test connection
            test_result = self.api_client.test_connection()
            if not test_result['success']:
                raise Exception(f"API connection test failed: {test_result['message']}")
                
        except Exception as e:
            raise Exception(f"REST API connection error: {str(e)}")
    
    def _validate_credentials(self, username: str, password: str) -> bool:
        """Validate credential format"""
        # Security: Basic credential validation
        if not username or not password:
            return False
        
        # Security: Check for minimum length
        if len(username) < 3 or len(password) < 3:
            return False
        
        # Security: Check for common injection patterns
        dangerous_patterns = ['<', '>', '"', "'", ';', '--', '/*', '*/']
        for pattern in dangerous_patterns:
            if pattern in username or pattern in password:
                return False
        
        return True
    
    def detect_servicenow_database(self) -> Dict[str, Any]:
        """Detect if the connected database is a ServiceNow instance"""
        try:
            if not self.db_engine:
                raise Exception("Database connection not established")
            
            detection_result = {
                'is_servicenow': False,
                'confidence_score': 0,
                'version': None,
                'instance_type': None,
                'tables_found': [],
                'errors': []
            }
            
            # Security: Use parameterized queries
            with self.db_engine.connect() as conn:
                # Check for ServiceNow-specific tables
                servicenow_tables = [
                    'sys_user', 'sys_user_role', 'sys_app', 'sys_properties',
                    'sys_db_object', 'sysauto_script', 'sys_script'
                ]
                
                found_tables = []
                for table in servicenow_tables:
                    try:
                        result = conn.execute(text(
                            "SELECT COUNT(*) FROM information_schema.tables WHERE table_name = :table_name"
                        ), {'table_name': table})
                        
                        if result.scalar() > 0:
                            found_tables.append(table)
                    except Exception as e:
                        detection_result['errors'].append(f"Error checking table {table}: {str(e)}")
                
                detection_result['tables_found'] = found_tables
                
                # Calculate confidence score
                confidence = len(found_tables) / len(servicenow_tables)
                detection_result['confidence_score'] = confidence
                detection_result['is_servicenow'] = confidence >= 0.5
                
                # Try to detect version
                if detection_result['is_servicenow']:
                    try:
                        version_result = conn.execute(text(
                            "SELECT value FROM sys_properties WHERE name = 'glide.buildname' LIMIT 1"
                        ))
                        version = version_result.scalar()
                        if version:
                            detection_result['version'] = version
                    except Exception as e:
                        detection_result['errors'].append(f"Error detecting version: {str(e)}")
                
                # Detect instance type
                if 'sys_app' in found_tables:
                    detection_result['instance_type'] = 'Production'
                else:
                    detection_result['instance_type'] = 'Development'
            
            return detection_result
            
        except Exception as e:
            self.logger.error(f"Error detecting ServiceNow database: {e}")
            return {
                'is_servicenow': False,
                'confidence_score': 0,
                'version': None,
                'instance_type': None,
                'tables_found': [],
                'errors': [f"Detection failed: {str(e)}"]
            }
    
    def get_hybrid_data(self) -> Dict[str, Any]:
        """Get comprehensive data using both database and REST API"""
        try:
            if not self.connection_established:
                raise Exception("No connections established")
            
            hybrid_data = {
                'instance_info': {},
                'database_data': {},
                'api_data': {},
                'correlation_results': {},
                'summary': {},
                'errors': []
            }
            
            # Get database data
            if self.db_engine:
                try:
                    hybrid_data['database_data'] = self._get_database_data()
                except Exception as e:
                    error_msg = f"Database data extraction failed: {str(e)}"
                    hybrid_data['errors'].append(error_msg)
                    self.logger.error(error_msg)
            
            # Get API data
            if self.api_client:
                try:
                    hybrid_data['api_data'] = self._get_api_data()
                except Exception as e:
                    error_msg = f"API data extraction failed: {str(e)}"
                    hybrid_data['errors'].append(error_msg)
                    self.logger.error(error_msg)
            
            # Correlate data
            try:
                hybrid_data['correlation_results'] = self._correlate_data(
                    hybrid_data['database_data'], 
                    hybrid_data['api_data']
                )
            except Exception as e:
                error_msg = f"Data correlation failed: {str(e)}"
                hybrid_data['errors'].append(error_msg)
                self.logger.error(error_msg)
            
            # Generate summary
            hybrid_data['summary'] = self._generate_summary(hybrid_data)
            
            return hybrid_data
            
        except Exception as e:
            self.logger.error(f"Error getting hybrid data: {e}")
            return {
                'instance_info': {},
                'database_data': {},
                'api_data': {},
                'correlation_results': {},
                'summary': {},
                'errors': [f"Hybrid data extraction failed: {str(e)}"]
            }
    
    def _get_database_data(self) -> Dict[str, Any]:
        """Get data from ServiceNow database"""
        try:
            if not self.db_engine:
                return {}
            
            database_data = {
                'modules': [],
                'roles': [],
                'tables': [],
                'properties': [],
                'scheduled_jobs': []
            }
            
            with self.db_engine.connect() as conn:
                # Get modules from sys_app
                try:
                    result = conn.execute(text("""
                        SELECT sys_id, name, version, active, description 
                        FROM sys_app 
                        WHERE active = true 
                        ORDER BY name
                    """))
                    
                    for row in result:
                        database_data['modules'].append({
                            'sys_id': str(row[0]),
                            'name': str(row[1]),
                            'version': str(row[2]) if row[2] else '',
                            'active': bool(row[3]),
                            'description': str(row[4]) if row[4] else '',
                            'source': 'database'
                        })
                except Exception as e:
                    self.logger.warning(f"Error getting modules from database: {e}")
                
                # Get roles from sys_user_role
                try:
                    result = conn.execute(text("""
                        SELECT sys_id, name, description, active 
                        FROM sys_user_role 
                        WHERE active = true 
                        ORDER BY name
                    """))
                    
                    for row in result:
                        database_data['roles'].append({
                            'sys_id': str(row[0]),
                            'name': str(row[1]),
                            'description': str(row[2]) if row[2] else '',
                            'active': bool(row[3]),
                            'source': 'database'
                        })
                except Exception as e:
                    self.logger.warning(f"Error getting roles from database: {e}")
                
                # Get system properties
                try:
                    result = conn.execute(text("""
                        SELECT name, value, description, type 
                        FROM sys_properties 
                        WHERE name LIKE 'glide.%' 
                        ORDER BY name
                    """))
                    
                    for row in result:
                        database_data['properties'].append({
                            'name': str(row[0]),
                            'value': str(row[1]) if row[1] else '',
                            'description': str(row[2]) if row[2] else '',
                            'type': str(row[3]) if row[3] else 'string',
                            'source': 'database'
                        })
                except Exception as e:
                    self.logger.warning(f"Error getting properties from database: {e}")
            
            return database_data
            
        except Exception as e:
            self.logger.error(f"Error getting database data: {e}")
            return {}
    
    def _get_api_data(self) -> Dict[str, Any]:
        """Get data from ServiceNow REST API"""
        try:
            if not self.api_client:
                return {}
            
            return self.api_client.get_comprehensive_data()
            
        except Exception as e:
            self.logger.error(f"Error getting API data: {e}")
            return {}
    
    def _correlate_data(self, database_data: Dict, api_data: Dict) -> Dict[str, Any]:
        """Correlate data between database and API sources"""
        try:
            correlation_results = {
                'matched_items': 0,
                'database_only': 0,
                'api_only': 0,
                'discrepancies': [],
                'correlation_score': 0
            }
            
            # Correlate modules
            db_modules = {m['name']: m for m in database_data.get('modules', [])}
            api_modules = {m['name']: m for m in api_data.get('modules', [])}
            
            matched_modules = 0
            for name in db_modules:
                if name in api_modules:
                    matched_modules += 1
                else:
                    correlation_results['database_only'] += 1
            
            for name in api_modules:
                if name not in db_modules:
                    correlation_results['api_only'] += 1
            
            correlation_results['matched_items'] = matched_modules
            
            # Calculate correlation score
            total_items = len(db_modules) + len(api_modules)
            if total_items > 0:
                correlation_results['correlation_score'] = matched_modules / total_items
            
            return correlation_results
            
        except Exception as e:
            self.logger.error(f"Error correlating data: {e}")
            return {
                'matched_items': 0,
                'database_only': 0,
                'api_only': 0,
                'discrepancies': [],
                'correlation_score': 0
            }
    
    def _generate_summary(self, hybrid_data: Dict) -> Dict[str, Any]:
        """Generate summary of hybrid data"""
        try:
            summary = {
                'total_items': 0,
                'database_items': 0,
                'api_items': 0,
                'correlation_score': 0,
                'errors_count': len(hybrid_data.get('errors', [])),
                'last_updated': datetime.now().isoformat()
            }
            
            # Count database items
            db_data = hybrid_data.get('database_data', {})
            for key, items in db_data.items():
                if isinstance(items, list):
                    summary['database_items'] += len(items)
            
            # Count API items
            api_data = hybrid_data.get('api_data', {})
            for key, items in api_data.items():
                if isinstance(items, list):
                    summary['api_items'] += len(items)
            
            summary['total_items'] = summary['database_items'] + summary['api_items']
            
            # Get correlation score
            correlation = hybrid_data.get('correlation_results', {})
            summary['correlation_score'] = correlation.get('correlation_score', 0)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {e}")
            return {
                'total_items': 0,
                'database_items': 0,
                'api_items': 0,
                'correlation_score': 0,
                'errors_count': 0,
                'last_updated': datetime.now().isoformat()
            }
    
    def close_connections(self):
        """Close all connections securely"""
        try:
            if self.db_session:
                self.db_session.close()
                self.db_session = None
            
            if self.db_engine:
                self.db_engine.dispose()
                self.db_engine = None
            
            self.connection_established = False
            self.logger.info("All connections closed securely")
            
        except Exception as e:
            self.logger.error(f"Error closing connections: {e}")
    
    def __del__(self):
        """Destructor to ensure connections are closed"""
        self.close_connections()


# Import ServiceNowAPIClient for hybrid functionality
try:
    from servicenow_api_client import ServiceNowAPIClient
except ImportError:
    # Fallback if ServiceNowAPIClient is not available
    class ServiceNowAPIClient:
        def __init__(self, instance_url, username, password):
            self.instance_url = instance_url
            self.username = username
            self.password = password
        
        def test_connection(self):
            return {'success': False, 'message': 'ServiceNowAPIClient not available'}
        
        def get_comprehensive_data(self):
            return {}
