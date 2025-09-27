#!/usr/bin/env python3
"""
Database Schema Fix Script
Fixes the unique constraint issue for ServiceNowRole table
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_database_schema():
    """Fix the database schema to remove unique constraint on role names"""
    
    # Database connection parameters
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'sn_docs')
    db_user = os.getenv('DB_USER', 'servicenow_user')
    db_password = os.getenv('DB_PASSWORD', '')
    
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("🔧 Fixing database schema...")
        
        # Check if the unique constraint exists
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'servicenow_roles' 
            AND constraint_type = 'UNIQUE'
            AND constraint_name LIKE '%name%'
        """)
        
        constraints = cursor.fetchall()
        print(f"Found {len(constraints)} unique constraints on servicenow_roles table")
        
        # Drop the unique constraint on name column for roles
        for constraint in constraints:
            constraint_name = constraint[0]
            print(f"Dropping constraint: {constraint_name}")
            cursor.execute(f"ALTER TABLE servicenow_roles DROP CONSTRAINT IF EXISTS {constraint_name}")
        
        # Add a composite unique constraint on (name, module_id) for roles
        print("Adding composite unique constraint on (name, module_id) for roles...")
        cursor.execute("""
            ALTER TABLE servicenow_roles 
            ADD CONSTRAINT servicenow_roles_name_module_unique 
            UNIQUE (name, module_id)
        """)
        
        # Fix tables unique constraint
        print("Fixing tables unique constraint...")
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'servicenow_tables' 
            AND constraint_type = 'UNIQUE'
            AND constraint_name LIKE '%name%'
        """)
        
        table_constraints = cursor.fetchall()
        for constraint in table_constraints:
            constraint_name = constraint[0]
            print(f"Dropping table constraint: {constraint_name}")
            cursor.execute(f"ALTER TABLE servicenow_tables DROP CONSTRAINT IF EXISTS {constraint_name}")
        
        cursor.execute("""
            ALTER TABLE servicenow_tables 
            ADD CONSTRAINT servicenow_tables_name_module_unique 
            UNIQUE (name, module_id)
        """)
        
        # Fix scheduled jobs unique constraint
        print("Fixing scheduled jobs unique constraint...")
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'servicenow_scheduled_jobs' 
            AND constraint_type = 'UNIQUE'
            AND constraint_name LIKE '%name%'
        """)
        
        job_constraints = cursor.fetchall()
        for constraint in job_constraints:
            constraint_name = constraint[0]
            print(f"Dropping job constraint: {constraint_name}")
            cursor.execute(f"ALTER TABLE servicenow_scheduled_jobs DROP CONSTRAINT IF EXISTS {constraint_name}")
        
        cursor.execute("""
            ALTER TABLE servicenow_scheduled_jobs 
            ADD CONSTRAINT servicenow_scheduled_jobs_name_module_unique 
            UNIQUE (name, module_id)
        """)
        
        print("✅ Database schema fixed successfully!")
        
        # Verify the changes
        cursor.execute("""
            SELECT constraint_name, constraint_type 
            FROM information_schema.table_constraints 
            WHERE table_name = 'servicenow_roles' 
            AND constraint_type = 'UNIQUE'
        """)
        
        new_constraints = cursor.fetchall()
        print(f"New unique constraints: {new_constraints}")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    
    return True

if __name__ == "__main__":
    success = fix_database_schema()
    if success:
        print("🎉 Database schema fix completed successfully!")
        sys.exit(0)
    else:
        print("💥 Database schema fix failed!")
        sys.exit(1)
