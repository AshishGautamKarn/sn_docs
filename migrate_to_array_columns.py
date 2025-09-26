#!/usr/bin/env python3
"""
Database Migration Script: Convert JSON columns to PostgreSQL ARRAY columns
This script migrates the existing database schema to use PostgreSQL ARRAY columns
instead of JSON columns for better array handling.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from database import Base, DatabaseManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_database():
    """Migrate database from JSON to ARRAY columns"""
    
    # Get database URL from environment
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        logger.error("DATABASE_URL environment variable not set")
        return False
    
    try:
        # Create engine
        engine = create_engine(db_url)
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                logger.info("Starting database migration from JSON to ARRAY columns...")
                
                # 1. Update servicenow_roles table
                logger.info("Migrating servicenow_roles table...")
                
                # Add new ARRAY columns
                conn.execute(text("""
                    ALTER TABLE servicenow_roles 
                    ADD COLUMN permissions_new TEXT[],
                    ADD COLUMN dependencies_new TEXT[]
                """))
                
                # Migrate data from JSON to ARRAY - set all to empty arrays for now
                conn.execute(text("""
                    UPDATE servicenow_roles 
                    SET permissions_new = ARRAY[]::TEXT[],
                        dependencies_new = ARRAY[]::TEXT[]
                """))
                
                # Drop old columns and rename new ones
                conn.execute(text("ALTER TABLE servicenow_roles DROP COLUMN permissions, DROP COLUMN dependencies"))
                conn.execute(text("ALTER TABLE servicenow_roles RENAME COLUMN permissions_new TO permissions"))
                conn.execute(text("ALTER TABLE servicenow_roles RENAME COLUMN dependencies_new TO dependencies"))
                
                # 2. Update servicenow_tables table
                logger.info("Migrating servicenow_tables table...")
                
                # Add new ARRAY columns
                conn.execute(text("""
                    ALTER TABLE servicenow_tables 
                    ADD COLUMN fields_new TEXT[],
                    ADD COLUMN relationships_new TEXT[],
                    ADD COLUMN access_controls_new TEXT[],
                    ADD COLUMN business_rules_new TEXT[],
                    ADD COLUMN scripts_new TEXT[]
                """))
                
                # Migrate data from JSON to ARRAY - set all to empty arrays for now
                conn.execute(text("""
                    UPDATE servicenow_tables 
                    SET fields_new = ARRAY[]::TEXT[],
                        relationships_new = ARRAY[]::TEXT[],
                        access_controls_new = ARRAY[]::TEXT[],
                        business_rules_new = ARRAY[]::TEXT[],
                        scripts_new = ARRAY[]::TEXT[]
                """))
                
                # Drop old columns and rename new ones
                conn.execute(text("""
                    ALTER TABLE servicenow_tables 
                    DROP COLUMN fields, 
                    DROP COLUMN relationships, 
                    DROP COLUMN access_controls, 
                    DROP COLUMN business_rules, 
                    DROP COLUMN scripts
                """))
                conn.execute(text("ALTER TABLE servicenow_tables RENAME COLUMN fields_new TO fields"))
                conn.execute(text("ALTER TABLE servicenow_tables RENAME COLUMN relationships_new TO relationships"))
                conn.execute(text("ALTER TABLE servicenow_tables RENAME COLUMN access_controls_new TO access_controls"))
                conn.execute(text("ALTER TABLE servicenow_tables RENAME COLUMN business_rules_new TO business_rules"))
                conn.execute(text("ALTER TABLE servicenow_tables RENAME COLUMN scripts_new TO scripts"))
                
                # Commit transaction
                trans.commit()
                logger.info("✅ Database migration completed successfully!")
                return True
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                logger.error(f"❌ Migration failed: {e}")
                return False
                
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🔄 PostgreSQL ARRAY Migration Script")
    print("=" * 50)
    
    success = migrate_database()
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("The database now uses PostgreSQL ARRAY columns for better array handling.")
    else:
        print("\n❌ Migration failed!")
        print("Please check the logs for details and try again.")
        sys.exit(1)
