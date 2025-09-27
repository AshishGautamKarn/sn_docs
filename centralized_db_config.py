"""
Centralized Database Configuration Manager
Ensures all database connections use the same source of truth and stores sensitive data in database.
"""

import os
import logging
import threading
from typing import Dict, Any, Optional, List
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
import hashlib
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Load environment variables
load_dotenv()

class CentralizedDatabaseConfig:
    """
    Centralized database configuration manager that ensures all modules use the same database connection.
    All sensitive data is stored in the database, not in files.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern to ensure single instance"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CentralizedDatabaseConfig, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.logger = self._setup_logger()
        self._database_url = None
        self._engine = None
        self._SessionLocal = None
        self._encryption_key = None
        
        # Initialize with environment variables first
        self._initialize_from_environment()
        
        # Try to load from database if available
        self._load_from_database()
        
        self._initialized = True
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for centralized database configuration"""
        logger = logging.getLogger('centralized_db_config')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _initialize_from_environment(self):
        """Initialize database connection from environment variables"""
        try:
            db_type = os.getenv('DB_TYPE', 'postgresql')
            db_host = os.getenv('DB_HOST', 'localhost')
            db_port = os.getenv('DB_PORT', '5432')
            db_name = os.getenv('DB_NAME', 'sn_docs')
            db_user = os.getenv('DB_USER', 'postgres')
            db_password = os.getenv('DB_PASSWORD', '')
            
            # Use SQLite as fallback if no proper database configuration is found
            # Check if we're using default values (no real configuration)
            self.logger.info(f"Checking database config: host={db_host}, password={'***' if db_password else 'empty'}, name={db_name}, user={db_user}, port={db_port}")
            
            if (db_host == 'localhost' and db_password == '' and 
                db_name == 'sn_docs' and db_user == 'postgres' and db_port == '5432'):
                self.logger.info("No database configuration found, using SQLite fallback")
                self._database_url = "sqlite:///servicenow_docs.db"
                db_type = 'sqlite'
            else:
                if db_type == 'postgresql':
                    self._database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
                elif db_type == 'mysql':
                    self._database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
                elif db_type == 'sqlite':
                    self._database_url = f"sqlite:///{db_name}"
                else:
                    raise ValueError(f"Unsupported database type: {db_type}")
            
            # Create engine and session
            self._engine = create_engine(self._database_url, echo=False)
            self._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
            
            # Generate encryption key for sensitive data
            self._generate_encryption_key()
            
            self.logger.info(f"Database configuration initialized: {db_type} database")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize from environment: {e}")
            # Fallback to SQLite
            self.logger.info("Falling back to SQLite database")
            self._database_url = "sqlite:///servicenow_docs.db"
            self._engine = create_engine(self._database_url, echo=False)
            self._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
            self._generate_encryption_key()
    
    def _generate_encryption_key(self):
        """Generate encryption key for sensitive data storage"""
        try:
            # Use a combination of environment variables and system info for key generation
            key_source = f"{os.getenv('DB_HOST', 'localhost')}{os.getenv('DB_NAME', 'sn_docs')}{os.getenv('DB_USER', 'postgres')}"
            
            # Generate a deterministic but secure key
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'sn_docs_salt',  # Fixed salt for deterministic key
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(key_source.encode()))
            self._encryption_key = Fernet(key)
            
        except Exception as e:
            self.logger.error(f"Failed to generate encryption key: {e}")
            # Fallback to a simple key (not recommended for production)
            self._encryption_key = Fernet(Fernet.generate_key())
    
    def _encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data before storing in database"""
        if not data:
            return ""
        try:
            return self._encryption_key.encrypt(data.encode()).decode()
        except Exception as e:
            self.logger.error(f"Failed to encrypt data: {e}")
            return data
    
    def _decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data from database"""
        if not encrypted_data:
            return ""
        try:
            return self._encryption_key.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            # Only log error if it's not an empty string or invalid data
            if encrypted_data.strip() and not encrypted_data.startswith('gAAAAAB'):
                self.logger.debug(f"Failed to decrypt data (likely unencrypted): {e}")
            return encrypted_data
    
    def _load_from_database(self):
        """Load configuration from database if available"""
        try:
            session = self._SessionLocal()
            try:
                # Check if configuration table exists and has data
                result = session.execute(text("""
                    SELECT name, db_type, host, port, database_name, username, password, 
                           connection_pool_size, max_overflow, echo, is_active
                    FROM database_configurations 
                    WHERE name = 'default' AND is_active = true
                    LIMIT 1
                """))
                
                row = result.fetchone()
                if row:
                    # Decrypt password
                    decrypted_password = self._decrypt_sensitive_data(row[6])
                    
                    # Build new database URL
                    if row[1] == 'postgresql':
                        new_url = f"postgresql://{row[5]}:{decrypted_password}@{row[2]}:{row[3]}/{row[4]}"
                    elif row[1] == 'mysql':
                        new_url = f"mysql+pymysql://{row[5]}:{decrypted_password}@{row[2]}:{row[3]}/{row[4]}"
                    elif row[1] == 'sqlite':
                        new_url = f"sqlite:///{row[4]}"
                    else:
                        new_url = f"{row[1]}://{row[5]}:{decrypted_password}@{row[2]}:{row[3]}/{row[4]}"
                    
                    # Update connection if different
                    if new_url != self._database_url:
                        self._database_url = new_url
                        self._engine = create_engine(new_url, echo=row[9])
                        self._SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)
                        self.logger.info("Database configuration loaded from database")
                        
            finally:
                session.close()
                
        except Exception as e:
            self.logger.warning(f"Could not load configuration from database: {e}")
    
    def get_database_url(self) -> str:
        """Get the current database URL"""
        return self._database_url
    
    def get_engine(self):
        """Get the SQLAlchemy engine"""
        return self._engine
    
    def get_session(self):
        """Get a database session"""
        return self._SessionLocal()
    
    def save_database_configuration(self, config_data: Dict[str, Any]) -> bool:
        """Save database configuration to database"""
        try:
            session = self.get_session()
            try:
                # Encrypt password
                encrypted_password = self._encrypt_sensitive_data(config_data.get('password', ''))
                
                # Check if configuration exists
                result = session.execute(text("""
                    SELECT id FROM database_configurations 
                    WHERE name = :name
                """), {'name': config_data.get('name', 'default')})
                
                existing = result.fetchone()
                
                if existing:
                    # Update existing configuration
                    session.execute(text("""
                        UPDATE database_configurations SET
                            db_type = :db_type,
                            host = :host,
                            port = :port,
                            database_name = :database_name,
                            username = :username,
                            password = :password,
                            connection_pool_size = :connection_pool_size,
                            max_overflow = :max_overflow,
                            echo = :echo,
                            is_active = :is_active,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE name = :name
                    """), {
                        'name': config_data.get('name', 'default'),
                        'db_type': config_data.get('db_type', 'postgresql'),
                        'host': config_data.get('host', 'localhost'),
                        'port': config_data.get('port', 5432),
                        'database_name': config_data.get('database_name', 'sn_docs'),
                        'username': config_data.get('username', 'postgres'),
                        'password': encrypted_password,
                        'connection_pool_size': config_data.get('connection_pool_size', 10),
                        'max_overflow': config_data.get('max_overflow', 20),
                        'echo': config_data.get('echo', False),
                        'is_active': config_data.get('is_active', True)
                    })
                else:
                    # Insert new configuration
                    session.execute(text("""
                        INSERT INTO database_configurations 
                        (name, db_type, host, port, database_name, username, password, 
                         connection_pool_size, max_overflow, echo, is_active, created_at, updated_at)
                        VALUES 
                        (:name, :db_type, :host, :port, :database_name, :username, :password,
                         :connection_pool_size, :max_overflow, :echo, :is_active, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """), {
                        'name': config_data.get('name', 'default'),
                        'db_type': config_data.get('db_type', 'postgresql'),
                        'host': config_data.get('host', 'localhost'),
                        'port': config_data.get('port', 5432),
                        'database_name': config_data.get('database_name', 'sn_docs'),
                        'username': config_data.get('username', 'postgres'),
                        'password': encrypted_password,
                        'connection_pool_size': config_data.get('connection_pool_size', 10),
                        'max_overflow': config_data.get('max_overflow', 20),
                        'echo': config_data.get('echo', False),
                        'is_active': config_data.get('is_active', True)
                    })
                
                session.commit()
                self.logger.info(f"Database configuration saved: {config_data.get('name', 'default')}")
                
                # Reload configuration if this is the default
                if config_data.get('name', 'default') == 'default':
                    self._load_from_database()
                
                return True
                
            finally:
                session.close()
                
        except Exception as e:
            self.logger.error(f"Failed to save database configuration: {e}")
            return False
    
    def save_servicenow_configuration(self, config_data: Dict[str, Any]) -> bool:
        """Save ServiceNow configuration to database"""
        try:
            session = self.get_session()
            try:
                # Encrypt passwords
                encrypted_password = self._encrypt_sensitive_data(config_data.get('password', ''))
                
                # Check if configuration exists
                result = session.execute(text("""
                    SELECT id FROM servicenow_configurations 
                    WHERE name = :name
                """), {'name': config_data.get('name', 'default')})
                
                existing = result.fetchone()
                
                if existing:
                    # Update existing configuration
                    session.execute(text("""
                        UPDATE servicenow_configurations SET
                            instance_url = :instance_url,
                            username = :username,
                            password = :password,
                            api_version = :api_version,
                            timeout = :timeout,
                            max_retries = :max_retries,
                            verify_ssl = :verify_ssl,
                            is_active = :is_active,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE name = :name
                    """), {
                        'name': config_data.get('name', 'default'),
                        'instance_url': config_data.get('instance_url', ''),
                        'username': config_data.get('username', ''),
                        'password': encrypted_password,
                        'api_version': config_data.get('api_version', 'v2'),
                        'timeout': config_data.get('timeout', 30),
                        'max_retries': config_data.get('max_retries', 3),
                        'verify_ssl': config_data.get('verify_ssl', True),
                        'is_active': config_data.get('is_active', True)
                    })
                else:
                    # Insert new configuration
                    session.execute(text("""
                        INSERT INTO servicenow_configurations 
                        (name, instance_url, username, password, api_version, timeout, max_retries, 
                         verify_ssl, is_active, created_at, updated_at)
                        VALUES 
                        (:name, :instance_url, :username, :password, :api_version, :timeout, :max_retries,
                         :verify_ssl, :is_active, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """), {
                        'name': config_data.get('name', 'default'),
                        'instance_url': config_data.get('instance_url', ''),
                        'username': config_data.get('username', ''),
                        'password': encrypted_password,
                        'api_version': config_data.get('api_version', 'v2'),
                        'timeout': config_data.get('timeout', 30),
                        'max_retries': config_data.get('max_retries', 3),
                        'verify_ssl': config_data.get('verify_ssl', True),
                        'is_active': config_data.get('is_active', True)
                    })
                
                session.commit()
                self.logger.info(f"ServiceNow configuration saved: {config_data.get('name', 'default')}")
                return True
                
            finally:
                session.close()
                
        except Exception as e:
            self.logger.error(f"Failed to save ServiceNow configuration: {e}")
            return False
    
    def get_database_configuration(self, name: str = 'default') -> Optional[Dict[str, Any]]:
        """Get database configuration from database"""
        try:
            session = self.get_session()
            try:
                result = session.execute(text("""
                    SELECT name, db_type, host, port, database_name, username, password, 
                           connection_pool_size, max_overflow, echo, is_active, created_at, updated_at
                    FROM database_configurations 
                    WHERE name = :name AND is_active = true
                """), {'name': name})
                
                row = result.fetchone()
                if row:
                    # Decrypt password
                    decrypted_password = self._decrypt_sensitive_data(row[6])
                    
                    return {
                        'name': row[0],
                        'db_type': row[1],
                        'host': row[2],
                        'port': row[3],
                        'database_name': row[4],
                        'username': row[5],
                        'password': decrypted_password,
                        'connection_pool_size': row[7],
                        'max_overflow': row[8],
                        'echo': row[9],
                        'is_active': row[10],
                        'created_at': row[11],
                        'updated_at': row[12]
                    }
                return None
                
            finally:
                session.close()
                
        except Exception as e:
            self.logger.error(f"Failed to get database configuration: {e}")
            return None
    
    def get_servicenow_configuration(self, name: str = 'default') -> Optional[Dict[str, Any]]:
        """Get ServiceNow configuration from database"""
        try:
            session = self.get_session()
            try:
                result = session.execute(text("""
                    SELECT name, instance_url, username, password, api_version, timeout, max_retries, 
                           verify_ssl, is_active, created_at, updated_at
                    FROM servicenow_configurations 
                    WHERE name = :name AND is_active = true
                """), {'name': name})
                
                row = result.fetchone()
                if row:
                    # Decrypt password
                    decrypted_password = self._decrypt_sensitive_data(row[3])
                    
                    return {
                        'name': row[0],
                        'instance_url': row[1],
                        'username': row[2],
                        'password': decrypted_password,
                        'api_version': row[4],
                        'timeout': row[5],
                        'max_retries': row[6],
                        'verify_ssl': row[7],
                        'is_active': row[8],
                        'created_at': row[9],
                        'updated_at': row[10]
                    }
                return None
                
            finally:
                session.close()
                
        except Exception as e:
            self.logger.error(f"Failed to get ServiceNow configuration: {e}")
            return None
    
    def get_all_servicenow_configurations(self) -> List[Dict[str, Any]]:
        """Get all ServiceNow configurations from database"""
        try:
            session = self.get_session()
            try:
                result = session.execute(text("""
                    SELECT name, instance_url, username, password, api_version, timeout, max_retries, 
                           verify_ssl, is_active, created_at, updated_at
                    FROM servicenow_configurations 
                    WHERE is_active = true
                    ORDER BY name, created_at DESC
                """))
                
                configurations = []
                for row in result.fetchall():
                    # Decrypt password
                    decrypted_password = self._decrypt_sensitive_data(row[3])
                    
                    configurations.append({
                        'name': row[0],
                        'instance_url': row[1],
                        'username': row[2],
                        'password': decrypted_password,
                        'api_version': row[4],
                        'timeout': row[5],
                        'max_retries': row[6],
                        'verify_ssl': row[7],
                        'is_active': row[8],
                        'created_at': row[9].isoformat() if row[9] else None,
                        'updated_at': row[10].isoformat() if row[10] else None
                    })
                
                return configurations
                
            finally:
                session.close()
                
        except Exception as e:
            self.logger.error(f"Failed to get all ServiceNow configurations: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            session = self.get_session()
            try:
                session.execute(text("SELECT 1"))
                return True
            finally:
                session.close()
        except Exception as e:
            self.logger.error(f"Database connection test failed: {e}")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get current connection information"""
        try:
            # Parse database URL to extract connection details
            db_url = self._database_url
            
            if db_url.startswith('postgresql://'):
                import re
                pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
                match = re.match(pattern, db_url)
                if match:
                    username, password, host, port, database = match.groups()
                    return {
                        'db_type': 'PostgreSQL',
                        'host': host,
                        'port': port,
                        'database': database,
                        'username': username,
                        'password': '***' + password[-3:] if len(password) > 3 else '***',
                        'connected': self.test_connection()
                    }
            elif db_url.startswith('mysql'):
                import re
                pattern = r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
                match = re.match(pattern, db_url)
                if match:
                    username, password, host, port, database = match.groups()
                    return {
                        'db_type': 'MySQL',
                        'host': host,
                        'port': port,
                        'database': database,
                        'username': username,
                        'password': '***' + password[-3:] if len(password) > 3 else '***',
                        'connected': self.test_connection()
                    }
            elif db_url.startswith('sqlite'):
                return {
                    'db_type': 'SQLite',
                    'host': 'localhost',
                    'port': 0,
                    'database': db_url.replace('sqlite:///database.db', ''),
                    'username': '',
                    'password': '',
                    'connected': self.test_connection()
                }
            
            return {
                'db_type': 'Unknown',
                'host': 'Unknown',
                'port': 'Unknown',
                'database': 'Unknown',
                'username': 'Unknown',
                'password': 'Unknown',
                'connected': False
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get connection info: {e}")
            return {
                'db_type': 'Error',
                'host': 'Error',
                'port': 'Error',
                'database': 'Error',
                'username': 'Error',
                'password': 'Error',
                'connected': False,
                'error': str(e)
            }


# Global instance
centralized_db_config = CentralizedDatabaseConfig()


def get_centralized_db_config() -> CentralizedDatabaseConfig:
    """Get the global centralized database configuration instance"""
    return centralized_db_config


def get_database_session():
    """Get a database session from the centralized configuration"""
    return centralized_db_config.get_session()


def get_database_engine():
    """Get the database engine from the centralized configuration"""
    return centralized_db_config.get_engine()


def get_database_url():
    """Get the database URL from the centralized configuration"""
    return centralized_db_config.get_database_url()

# Created By: Ashish Gautam; LinkedIn: https://www.linkedin.com/in/ashishgautamkarn/
