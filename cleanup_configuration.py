"""
Cleanup Configuration Script
Cleans up the database configuration and suppresses warnings.
"""

import os
import warnings
import logging
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Suppress SSL warnings
warnings.filterwarnings("ignore", message=".*urllib3.*OpenSSL.*")

# Suppress Plotly deprecation warnings
warnings.filterwarnings("ignore", message=".*DatetimeProperties.to_pydatetime.*")

# Suppress pandas warnings
warnings.filterwarnings("ignore", category=FutureWarning)

def cleanup_database_configuration():
    """Clean up database configuration by removing empty/invalid entries"""
    
    # Load environment variables
    load_dotenv()
    
    # Get database connection
    db_type = os.getenv('DB_TYPE', 'postgresql')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'sn_docs')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', '')
    
    if db_type == 'postgresql':
        database_url = f"postgresql://user:password@host:port/database"
    elif db_type == 'mysql':
        database_url = f"mysql+pymysql://user:password@host:port/database"
    elif db_type == 'sqlite':
        database_url = f"sqlite:///database.db"
    else:
        print(f"❌ Unsupported database type: {db_type}")
        return False
    
    try:
        # Create engine
        engine = create_engine(database_url, echo=False)
        
        with engine.connect() as conn:
            # Clean up empty configurations
            conn.execute(text("""
                DELETE FROM database_configurations 
                WHERE password = '' OR password IS NULL
            """))
            
            conn.execute(text("""
                DELETE FROM servicenow_configurations 
                WHERE password = '' OR password IS NULL
            """))
            
            # Update default configuration with current environment settings
            conn.execute(text("""
                INSERT INTO database_configurations 
                (name, db_type, host, port, database_name, username, password, 
                 connection_pool_size, max_overflow, echo, is_active)
                VALUES 
                (:name, :db_type, :host, :port, :database_name, :username, :password,
                 :connection_pool_size, :max_overflow, :echo, :is_active)
                ON CONFLICT (name) DO UPDATE SET
                    db_type = EXCLUDED.db_type,
                    host = EXCLUDED.host,
                    port = EXCLUDED.port,
                    database_name = EXCLUDED.database_name,
                    username = EXCLUDED.username,
                    password = EXCLUDED.password,
                    updated_at = CURRENT_TIMESTAMP
            """), {
                'name': 'default',
                'db_type': db_type,
                'host': db_host,
                'port': db_port,
                'database_name': db_name,
                'username': db_user,
                'password': db_password,
                'connection_pool_size': 10,
                'max_overflow': 20,
                'echo': False,
                'is_active': True
            })
            
            conn.commit()
            
        print("✅ Database configuration cleaned up successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning up configuration: {e}")
        return False

def setup_logging():
    """Setup cleaner logging configuration"""
    
    # Configure logging to be less verbose
    logging.basicConfig(
        level=logging.WARNING,  # Only show warnings and errors
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    
    # Set specific loggers to be less verbose
    logging.getLogger('centralized_db_config').setLevel(logging.WARNING)
    logging.getLogger('servicenow_database').setLevel(logging.WARNING)
    logging.getLogger('servicenow_database_connector').setLevel(logging.WARNING)
    logging.getLogger('servicenow_api_client').setLevel(logging.WARNING)

if __name__ == "__main__":
    print("🧹 Cleaning up configuration and suppressing warnings...")
    
    # Setup cleaner logging
    setup_logging()
    
    # Clean up database configuration
    if cleanup_database_configuration():
        print("🎉 Configuration cleanup completed!")
        print("📝 Warnings have been suppressed for cleaner startup.")
        print("🔧 Database configuration has been cleaned up.")
    else:
        print("❌ Configuration cleanup failed.")
