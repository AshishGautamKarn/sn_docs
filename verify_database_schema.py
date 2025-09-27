#!/usr/bin/env python3
"""
Database Schema Verification Script
Verifies that all required tables exist and have the correct structure.
Compares against the reference database structure.
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
    """Setup logging for schema verification"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def get_reference_schema():
    """Get the reference schema from the working database"""
    reference_schema = {
        'servicenow_modules': {
            'columns': ['id', 'name', 'label', 'description', 'version', 'module_type', 'documentation_url', 'created_at', 'updated_at', 'is_active'],
            'indexes': ['servicenow_modules_pkey', 'idx_servicenow_modules_name', 'ix_servicenow_modules_name']
        },
        'servicenow_roles': {
            'columns': ['id', 'name', 'description', 'module_id', 'permissions', 'dependencies', 'created_at', 'updated_at', 'is_active'],
            'indexes': ['servicenow_roles_pkey']
        },
        'servicenow_tables': {
            'columns': ['id', 'name', 'label', 'description', 'module_id', 'table_type', 'fields', 'relationships', 'access_controls', 'business_rules', 'scripts', 'created_at', 'updated_at', 'is_active'],
            'indexes': ['servicenow_tables_pkey']
        },
        'servicenow_properties': {
            'columns': ['id', 'name', 'description', 'default_value', 'current_value', 'module_id', 'category', 'property_type', 'scope', 'impact_level', 'documentation_url', 'created_at', 'updated_at', 'is_active'],
            'indexes': ['servicenow_properties_pkey']
        },
        'servicenow_scheduled_jobs': {
            'columns': ['id', 'name', 'description', 'module_id', 'frequency', 'script', 'active', 'last_run', 'next_run', 'created_at', 'updated_at'],
            'indexes': ['servicenow_scheduled_jobs_pkey']
        },
        'database_connections': {
            'columns': ['id', 'name', 'connection_type', 'host', 'port', 'database_name', 'username', 'password', 'connection_string', 'is_active', 'created_at', 'updated_at'],
            'indexes': ['database_connections_pkey']
        },
        'database_configurations': {
            'columns': ['id', 'name', 'db_type', 'host', 'port', 'database_name', 'username', 'password', 'connection_pool_size', 'max_overflow', 'echo', 'is_active', 'created_at', 'updated_at'],
            'indexes': ['database_configurations_pkey']
        },
        'servicenow_configurations': {
            'columns': ['id', 'name', 'instance_url', 'username', 'password', 'api_version', 'timeout', 'max_retries', 'verify_ssl', 'is_active', 'created_at', 'updated_at'],
            'indexes': ['servicenow_configurations_pkey']
        },
        'database_introspections': {
            'columns': ['id', 'connection_id', 'introspection_type', 'introspection_data', 'status', 'error_message', 'created_at', 'completed_at'],
            'indexes': ['database_introspections_pkey']
        }
    }
    return reference_schema

def verify_database_schema():
    """Verify that the database schema matches the expected structure"""
    logger = setup_logging()
    
    try:
        # Get centralized database configuration
        centralized_config = get_centralized_db_config()
        engine = centralized_config.get_engine()
        
        logger.info("🔍 Starting database schema verification...")
        
        # Get reference schema
        reference_schema = get_reference_schema()
        inspector = inspect(engine)
        
        # Get current tables
        current_tables = inspector.get_table_names()
        logger.info(f"📋 Found {len(current_tables)} tables in database")
        
        # Check each required table
        all_good = True
        missing_tables = []
        incorrect_tables = []
        
        for table_name, expected_structure in reference_schema.items():
            if table_name not in current_tables:
                logger.error(f"❌ Missing table: {table_name}")
                missing_tables.append(table_name)
                all_good = False
                continue
            
            # Check columns
            current_columns = [col['name'] for col in inspector.get_columns(table_name)]
            expected_columns = expected_structure['columns']
            
            missing_columns = set(expected_columns) - set(current_columns)
            extra_columns = set(current_columns) - set(expected_columns)
            
            if missing_columns or extra_columns:
                logger.warning(f"⚠️ Table '{table_name}' has column discrepancies:")
                if missing_columns:
                    logger.warning(f"   Missing columns: {missing_columns}")
                if extra_columns:
                    logger.warning(f"   Extra columns: {extra_columns}")
                incorrect_tables.append(table_name)
                all_good = False
            else:
                logger.info(f"✅ Table '{table_name}' structure is correct")
        
        # Summary
        logger.info("=" * 60)
        if all_good:
            logger.info("🎉 Database schema verification PASSED!")
            logger.info("✅ All tables exist with correct structure")
            return True
        else:
            logger.warning("⚠️ Database schema verification found issues:")
            if missing_tables:
                logger.warning(f"   Missing tables: {missing_tables}")
            if incorrect_tables:
                logger.warning(f"   Tables with issues: {incorrect_tables}")
            
            logger.info("💡 Run 'python3 initialize_tables.py' to fix missing tables")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during schema verification: {e}")
        return False

def fix_schema_issues():
    """Attempt to fix schema issues"""
    logger = setup_logging()
    
    logger.info("🔧 Attempting to fix schema issues...")
    
    try:
        # Run the table initialization script
        import subprocess
        result = subprocess.run(['python3', 'initialize_tables.py'], 
                             capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.info("✅ Schema fix successful!")
            return True
        else:
            logger.error(f"❌ Schema fix failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during schema fix: {e}")
        return False

def main():
    """Main function to verify and optionally fix database schema"""
    logger = setup_logging()
    
    logger.info("🚀 ServiceNow Database Schema Verification")
    logger.info("=" * 60)
    
    try:
        # Verify schema
        schema_ok = verify_database_schema()
        
        if schema_ok:
            logger.info("🎉 Database schema is correct!")
            return 0
        else:
            logger.info("🔧 Attempting to fix schema issues...")
            if fix_schema_issues():
                logger.info("🔄 Re-verifying schema after fix...")
                if verify_database_schema():
                    logger.info("🎉 Schema issues fixed successfully!")
                    return 0
                else:
                    logger.error("❌ Schema issues persist after fix attempt")
                    return 1
            else:
                logger.error("❌ Could not fix schema issues")
                return 1
                
    except Exception as e:
        logger.error(f"❌ Unexpected error during verification: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

# Created By: Ashish Gautam; LinkedIn: https://www.linkedin.com/in/ashishgautamkarn/
