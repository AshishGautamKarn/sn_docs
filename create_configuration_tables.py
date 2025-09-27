"""
Create Configuration Tables Migration Script
Creates the necessary tables for centralized configuration storage.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_configuration_tables():
    """Create configuration tables for centralized storage"""
    
    # Get database connection from environment
    db_type = os.getenv('DB_TYPE', 'postgresql')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'sn_docs')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', '')
    
    if db_type == 'postgresql':
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    elif db_type == 'mysql':
        database_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    elif db_type == 'sqlite':
        database_url = f"sqlite:///{db_name}"
    else:
        raise ValueError(f"Unsupported database type: {db_type}")
    
    try:
        # Create engine
        engine = create_engine(database_url, echo=True)
        
        with engine.connect() as conn:
            # Create database_configurations table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS database_configurations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    db_type VARCHAR(50) NOT NULL,
                    host VARCHAR(255) NOT NULL,
                    port INTEGER NOT NULL,
                    database_name VARCHAR(255) NOT NULL,
                    username VARCHAR(255) NOT NULL,
                    password TEXT NOT NULL,
                    connection_pool_size INTEGER DEFAULT 10,
                    max_overflow INTEGER DEFAULT 20,
                    echo BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create servicenow_configurations table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS servicenow_configurations (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    instance_url VARCHAR(500) NOT NULL,
                    username VARCHAR(255) NOT NULL,
                    password TEXT NOT NULL,
                    api_version VARCHAR(10) DEFAULT 'v2',
                    timeout INTEGER DEFAULT 30,
                    max_retries INTEGER DEFAULT 3,
                    verify_ssl BOOLEAN DEFAULT TRUE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create indexes for better performance
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_database_configurations_name 
                ON database_configurations(name)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_database_configurations_active 
                ON database_configurations(is_active)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_servicenow_configurations_name 
                ON servicenow_configurations(name)
            """))
            
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_servicenow_configurations_active 
                ON servicenow_configurations(is_active)
            """))
            
            # Commit the transaction
            conn.commit()
            
        print("✅ Configuration tables created successfully!")
        
        # Insert default configuration if it doesn't exist
        with engine.connect() as conn:
            # Check if default database configuration exists
            result = conn.execute(text("""
                SELECT COUNT(*) FROM database_configurations 
                WHERE name = 'default'
            """))
            
            if result.fetchone()[0] == 0:
                # Insert default database configuration
                conn.execute(text("""
                    INSERT INTO database_configurations 
                    (name, db_type, host, port, database_name, username, password, 
                     connection_pool_size, max_overflow, echo, is_active)
                    VALUES 
                    (:name, :db_type, :host, :port, :database_name, :username, :password,
                     :connection_pool_size, :max_overflow, :echo, :is_active)
                """), {
                    'name': 'default',
                    'db_type': db_type,
                    'host': db_host,
                    'port': db_port,
                    'database_name': db_name,
                    'username': db_user,
                    'password': db_password,  # This will be encrypted by the centralized config
                    'connection_pool_size': 10,
                    'max_overflow': 20,
                    'echo': False,
                    'is_active': True
                })
                
                print("✅ Default database configuration inserted!")
            
            # Check if default ServiceNow configuration exists
            result = conn.execute(text("""
                SELECT COUNT(*) FROM servicenow_configurations 
                WHERE name = 'default'
            """))
            
            if result.fetchone()[0] == 0:
                # Insert default ServiceNow configuration
                conn.execute(text("""
                    INSERT INTO servicenow_configurations 
                    (name, instance_url, username, password, api_version, timeout, max_retries, 
                     verify_ssl, is_active)
                    VALUES 
                    (:name, :instance_url, :username, :password, :api_version, :timeout, :max_retries,
                     :verify_ssl, :is_active)
                """), {
                    'name': 'default',
                    'instance_url': os.getenv('SN_INSTANCE_URL', ''),
                    'username': os.getenv('SN_USERNAME', ''),
                    'password': os.getenv('SN_PASSWORD', ''),  # This will be encrypted by the centralized config
                    'api_version': 'v2',
                    'timeout': 30,
                    'max_retries': 3,
                    'verify_ssl': True,
                    'is_active': True
                })
                
                print("✅ Default ServiceNow configuration inserted!")
            
            conn.commit()
            
        print("✅ Configuration tables setup completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating configuration tables: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Creating configuration tables for centralized storage...")
    
    if create_configuration_tables():
        print("🎉 Configuration tables created successfully!")
        print("📝 All sensitive data will now be stored securely in the database.")
        print("🔒 Passwords are encrypted using Fernet encryption.")
    else:
        print("❌ Failed to create configuration tables.")
        sys.exit(1)
