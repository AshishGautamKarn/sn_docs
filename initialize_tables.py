#!/usr/bin/env python3
"""
Database Table Initialization Script
Creates all necessary tables for the ServiceNow documentation application.
This script ensures all tables are created with proper structure and indexes.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from centralized_db_config import get_centralized_db_config

# Load environment variables
load_dotenv()

def setup_logging():
    """Setup logging for table initialization"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def check_table_exists(engine, table_name):
    """Check if a table exists in the database"""
    try:
        inspector = inspect(engine)
        return table_name in inspector.get_table_names()
    except Exception as e:
        logging.error(f"Error checking if table {table_name} exists: {e}")
        return False

def create_all_tables():
    """Create all necessary tables for the ServiceNow documentation application"""
    logger = setup_logging()
    
    try:
        # Get centralized database configuration
        centralized_config = get_centralized_db_config()
        engine = centralized_config.get_engine()
        session = centralized_config.get_session()
        
        logger.info("Starting database table initialization...")
        
        # List of all tables that should exist
        required_tables = [
            'servicenow_modules',
            'servicenow_roles', 
            'servicenow_tables',
            'servicenow_properties',
            'servicenow_scheduled_jobs',
            'database_connections',
            'database_configurations',
            'servicenow_configurations',
            'database_introspections'
        ]
        
        # Check which tables already exist
        existing_tables = []
        missing_tables = []
        
        for table in required_tables:
            if check_table_exists(engine, table):
                existing_tables.append(table)
                logger.info(f"✅ Table '{table}' already exists")
            else:
                missing_tables.append(table)
                logger.info(f"❌ Table '{table}' is missing")
        
        if not missing_tables:
            logger.info("🎉 All required tables already exist!")
            return True
        
        logger.info(f"Creating {len(missing_tables)} missing tables...")
        
        # Create missing tables using SQLAlchemy models
        try:
            from database import Base
            Base.metadata.create_all(bind=engine)
            logger.info("✅ All tables created successfully using SQLAlchemy models!")
        except Exception as e:
            logger.error(f"Failed to create tables using SQLAlchemy: {e}")
            logger.info("Attempting manual table creation...")
            
            # Manual table creation as fallback
            create_tables_manually(session, missing_tables)
        
        # Verify all tables were created
        logger.info("Verifying table creation...")
        all_created = True
        for table in required_tables:
            if check_table_exists(engine, table):
                logger.info(f"✅ Verified: Table '{table}' exists")
            else:
                logger.error(f"❌ Failed: Table '{table}' still missing")
                all_created = False
        
        if all_created:
            logger.info("🎉 All tables initialized successfully!")
            return True
        else:
            logger.error("❌ Some tables failed to initialize")
            return False
            
    except Exception as e:
        logger.error(f"Error during table initialization: {e}")
        return False
    finally:
        try:
            session.close()
        except:
            pass

def create_tables_manually(session, missing_tables):
    """Manually create tables using raw SQL"""
    logger = setup_logging()
    
    table_definitions = {
        'servicenow_modules': """
            CREATE TABLE IF NOT EXISTS servicenow_modules (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                label VARCHAR(255) NOT NULL,
                description TEXT,
                version VARCHAR(50),
                module_type VARCHAR(100),
                documentation_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """,
        'servicenow_roles': """
            CREATE TABLE IF NOT EXISTS servicenow_roles (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                module_id INTEGER REFERENCES servicenow_modules(id) ON DELETE CASCADE,
                permissions TEXT[],
                dependencies TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """,
        'servicenow_tables': """
            CREATE TABLE IF NOT EXISTS servicenow_tables (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                label VARCHAR(255) NOT NULL,
                description TEXT,
                module_id INTEGER REFERENCES servicenow_modules(id) ON DELETE CASCADE,
                table_type VARCHAR(100),
                fields TEXT[],
                relationships TEXT[],
                access_controls TEXT[],
                business_rules TEXT[],
                scripts TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """,
        'servicenow_properties': """
            CREATE TABLE IF NOT EXISTS servicenow_properties (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                default_value TEXT,
                current_value TEXT,
                module_id INTEGER REFERENCES servicenow_modules(id) ON DELETE CASCADE,
                category VARCHAR(100),
                property_type VARCHAR(50),
                scope VARCHAR(50),
                impact_level VARCHAR(20),
                documentation_url VARCHAR(500),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """,
        'servicenow_scheduled_jobs': """
            CREATE TABLE IF NOT EXISTS servicenow_scheduled_jobs (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                module_id INTEGER REFERENCES servicenow_modules(id) ON DELETE CASCADE,
                frequency VARCHAR(100),
                script TEXT,
                active BOOLEAN DEFAULT TRUE,
                last_run TIMESTAMP,
                next_run TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        'database_connections': """
            CREATE TABLE IF NOT EXISTS database_connections (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                connection_type VARCHAR(50) NOT NULL,
                host VARCHAR(255) NOT NULL,
                port INTEGER NOT NULL,
                database_name VARCHAR(255) NOT NULL,
                username VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                connection_string TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        'database_configurations': """
            CREATE TABLE IF NOT EXISTS database_configurations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE DEFAULT 'default',
                db_type VARCHAR(50) NOT NULL DEFAULT 'postgresql',
                host VARCHAR(255) NOT NULL DEFAULT 'localhost',
                port INTEGER NOT NULL DEFAULT 5432,
                database_name VARCHAR(255) NOT NULL DEFAULT 'sn_docs',
                username VARCHAR(255) NOT NULL DEFAULT 'servicenow_user',
                password VARCHAR(500) NOT NULL,
                connection_pool_size INTEGER DEFAULT 10,
                max_overflow INTEGER DEFAULT 20,
                echo BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        'servicenow_configurations': """
            CREATE TABLE IF NOT EXISTS servicenow_configurations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE DEFAULT 'default',
                instance_url VARCHAR(500) NOT NULL,
                username VARCHAR(255) NOT NULL,
                password VARCHAR(500) NOT NULL,
                api_version VARCHAR(50) DEFAULT 'v2',
                timeout INTEGER DEFAULT 30,
                max_retries INTEGER DEFAULT 3,
                verify_ssl BOOLEAN DEFAULT TRUE,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        'database_introspections': """
            CREATE TABLE IF NOT EXISTS database_introspections (
                id SERIAL PRIMARY KEY,
                connection_id INTEGER REFERENCES database_connections(id),
                introspection_type VARCHAR(50) NOT NULL,
                introspection_data JSON,
                status VARCHAR(20) DEFAULT 'pending',
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """
    }
    
    # Create tables
    for table_name in missing_tables:
        if table_name in table_definitions:
            try:
                session.execute(text(table_definitions[table_name]))
                logger.info(f"✅ Created table '{table_name}'")
            except Exception as e:
                logger.error(f"❌ Failed to create table '{table_name}': {e}")
    
    # Create indexes
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_servicenow_modules_name ON servicenow_modules(name)",
        "CREATE INDEX IF NOT EXISTS idx_servicenow_roles_module_id ON servicenow_roles(module_id)",
        "CREATE INDEX IF NOT EXISTS idx_servicenow_tables_module_id ON servicenow_tables(module_id)",
        "CREATE INDEX IF NOT EXISTS idx_servicenow_properties_module_id ON servicenow_properties(module_id)",
        "CREATE INDEX IF NOT EXISTS idx_servicenow_scheduled_jobs_module_id ON servicenow_scheduled_jobs(module_id)",
        "CREATE INDEX IF NOT EXISTS idx_database_configurations_name ON database_configurations(name)",
        "CREATE INDEX IF NOT EXISTS idx_servicenow_configurations_name ON servicenow_configurations(name)",
        "CREATE INDEX IF NOT EXISTS idx_database_introspections_connection_id ON database_introspections(connection_id)"
    ]
    
    for index_sql in indexes:
        try:
            session.execute(text(index_sql))
        except Exception as e:
            logger.warning(f"Failed to create index: {e}")
    
    try:
        session.commit()
        logger.info("✅ All tables and indexes created successfully!")
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Failed to commit table creation: {e}")
        raise

def main():
    """Main function to initialize database tables"""
    logger = setup_logging()
    
    logger.info("🚀 Starting ServiceNow Database Table Initialization")
    logger.info("=" * 60)
    
    try:
        success = create_all_tables()
        
        if success:
            logger.info("=" * 60)
            logger.info("🎉 Database table initialization completed successfully!")
            logger.info("✅ All required tables are now available")
            return 0
        else:
            logger.error("=" * 60)
            logger.error("❌ Database table initialization failed!")
            logger.error("Please check the error messages above and try again")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Unexpected error during initialization: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

# Created By: Ashish Gautam; LinkedIn: https://www.linkedin.com/in/ashishgautamkarn/
