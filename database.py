"""
ServiceNow Database Models and Connectivity
PostgreSQL database schema and ORM models for ServiceNow documentation data.
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Float, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.mysql import LONGTEXT
# import uuid  # Not needed for integer primary keys
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging
import os
from dotenv import load_dotenv
from centralized_db_config import get_centralized_db_config

# Load environment variables
load_dotenv()

Base = declarative_base()


class ServiceNowModule(Base):
    """ServiceNow module database model"""
    __tablename__ = 'servicenow_modules'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    label = Column(String(255), nullable=False)
    description = Column(Text)
    version = Column(String(50))
    module_type = Column(String(100))
    documentation_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    roles = relationship("ServiceNowRole", back_populates="module", cascade="all, delete-orphan")
    tables = relationship("ServiceNowTable", back_populates="module", cascade="all, delete-orphan")
    properties = relationship("ServiceNowProperty", back_populates="module", cascade="all, delete-orphan")
    scheduled_jobs = relationship("ServiceNowScheduledJob", back_populates="module", cascade="all, delete-orphan")


class ServiceNowRole(Base):
    """ServiceNow role database model"""
    __tablename__ = 'servicenow_roles'
    __table_args__ = (
        # Composite unique constraint: same role name can exist in different modules
        {'extend_existing': True}
    )
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    module_id = Column(Integer, ForeignKey('servicenow_modules.id'), nullable=False)
    permissions = Column(ARRAY(Text))  # List of permissions
    dependencies = Column(ARRAY(Text))  # List of dependent roles
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    module = relationship("ServiceNowModule", back_populates="roles")


class ServiceNowTable(Base):
    """ServiceNow table database model"""
    __tablename__ = 'servicenow_tables'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    label = Column(String(255), nullable=False)
    description = Column(Text)
    module_id = Column(Integer, ForeignKey('servicenow_modules.id'), nullable=False)
    table_type = Column(String(100))  # Base, Extension, Custom, System, View, Temp
    fields = Column(ARRAY(Text))  # List of field definitions
    relationships = Column(ARRAY(Text))  # List of relationships
    access_controls = Column(ARRAY(Text))  # List of access controls
    business_rules = Column(ARRAY(Text))  # List of business rules
    scripts = Column(ARRAY(Text))  # List of scripts
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    module = relationship("ServiceNowModule", back_populates="tables")


class ServiceNowProperty(Base):
    """ServiceNow system property database model"""
    __tablename__ = 'servicenow_properties'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    default_value = Column(Text)
    current_value = Column(Text)
    module_id = Column(Integer, ForeignKey('servicenow_modules.id'), nullable=False)
    category = Column(String(100))
    property_type = Column(String(50))  # String, Integer, Boolean, etc.
    scope = Column(String(50))  # Global, System, User, etc.
    impact_level = Column(String(20))  # Low, Medium, High, Critical
    documentation_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    module = relationship("ServiceNowModule", back_populates="properties")


class ServiceNowScheduledJob(Base):
    """ServiceNow scheduled job database model"""
    __tablename__ = 'servicenow_scheduled_jobs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    module_id = Column(Integer, ForeignKey('servicenow_modules.id'), nullable=False)
    frequency = Column(String(100))  # Daily, Hourly, Weekly, Cron expression
    script = Column(Text)
    active = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    module = relationship("ServiceNowModule", back_populates="scheduled_jobs")


class DatabaseConnection(Base):
    """Database connection configuration"""
    __tablename__ = 'database_connections'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    connection_type = Column(String(50), nullable=False)  # postgresql, mysql
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    database_name = Column(String(255), nullable=False)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    connection_string = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DatabaseConfiguration(Base):
    """Database configuration storage"""
    __tablename__ = 'database_configurations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, default='default')
    db_type = Column(String(50), nullable=False, default='postgresql')
    host = Column(String(255), nullable=False, default='localhost')
    port = Column(Integer, nullable=False, default=5432)
    database_name = Column(String(255), nullable=False, default='sn_docs')
    username = Column(String(255), nullable=False, default='servicenow_user')
    password = Column(String(500), nullable=False)  # Encrypted password
    connection_pool_size = Column(Integer, default=10)
    max_overflow = Column(Integer, default=20)
    echo = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'db_type': self.db_type,
            'host': self.host,
            'port': self.port,
            'database_name': self.database_name,
            'username': self.username,
            'password': self.password,  # Note: This is encrypted
            'connection_pool_size': self.connection_pool_size,
            'max_overflow': self.max_overflow,
            'echo': self.echo,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ServiceNowConfiguration(Base):
    """ServiceNow configuration storage"""
    __tablename__ = 'servicenow_configurations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, default='default')
    instance_url = Column(String(500), nullable=False)
    username = Column(String(255), nullable=False)
    password = Column(String(500), nullable=False)  # Encrypted password
    api_version = Column(String(50), default='v2')
    timeout = Column(Integer, default=30)
    max_retries = Column(Integer, default=3)
    verify_ssl = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'instance_url': self.instance_url,
            'username': self.username,
            'password': self.password,  # Note: This is encrypted
            'api_version': self.api_version,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'verify_ssl': self.verify_ssl,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class DatabaseIntrospection(Base):
    """Database introspection results"""
    __tablename__ = 'database_introspections'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    connection_id = Column(Integer, ForeignKey('database_connections.id'), nullable=False)
    introspection_type = Column(String(50), nullable=False)  # tables, roles, properties, jobs
    introspection_data = Column(JSON)  # Raw introspection results
    status = Column(String(20), default='pending')  # pending, completed, failed
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


class DatabaseManager:
    """Database manager for ServiceNow documentation"""
    
    def __init__(self, database_url: str = None):
        # Use centralized database configuration
        self.centralized_config = get_centralized_db_config()
        self.database_url = database_url or self.centralized_config.get_database_url()
        self.engine = self.centralized_config.get_engine()
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.logger = self._setup_logger()
    
    def reload_configuration(self):
        """Reload database configuration using centralized configuration"""
        try:
            # Reload centralized configuration
            self.centralized_config._load_from_database()
            
            # Update local references
            new_database_url = self.centralized_config.get_database_url()
            if new_database_url != self.database_url:
                self.database_url = new_database_url
                self.engine = self.centralized_config.get_engine()
                self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
                self.logger.debug("Database configuration reloaded from centralized configuration")
                return True
            else:
                self.logger.debug("Database configuration unchanged")
                return False
        except Exception as e:
            self.logger.error(f"Failed to reload database configuration: {e}")
            return False
    
    def _get_database_url(self) -> str:
        """Get database URL from environment variables"""
        db_type = os.getenv('DB_TYPE', 'postgresql')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'sn_docs')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        
        if db_type == 'postgresql':
            return f"postgresql://user:password@host:port/database"
        elif db_type == 'mysql':
            return f"mysql+pymysql://user:password@host:port/database"
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for database operations"""
        logger = logging.getLogger('servicenow_database')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _convert_timestamp(self, value):
        """Convert timestamp values to None if empty or invalid"""
        if value is None:
            return None
        if isinstance(value, str):
            # Convert empty string, 'null', 'None', etc. to None
            if value.strip() in ['', 'null', 'None', 'NULL', 'NONE']:
                return None
            # If it's a valid timestamp string, return as is
            return value
        return value
    
    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            self.logger.info("Database tables created successfully")
        except Exception as e:
            self.logger.error(f"Error creating database tables: {e}")
            raise
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def save_module(self, module_data: Dict[str, Any]) -> ServiceNowModule:
        """Save ServiceNow module to database"""
        session = self.get_session()
        try:
            # Check if module exists
            existing_module = session.query(ServiceNowModule).filter(
                ServiceNowModule.name == module_data['name']
            ).first()
            
            if existing_module:
                # Update existing module
                for key, value in module_data.items():
                    if hasattr(existing_module, key):
                        setattr(existing_module, key, value)
                existing_module.updated_at = datetime.utcnow()
                module = existing_module
            else:
                # Create new module
                module = ServiceNowModule(**module_data)
                session.add(module)
            
            session.commit()
            session.refresh(module)
            return module
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error saving module: {e}")
            raise
        finally:
            session.close()
    
    def save_role(self, role_data: Dict[str, Any], module_id: str) -> ServiceNowRole:
        """Save ServiceNow role to database"""
        session = self.get_session()
        try:
            role_data['module_id'] = module_id
            
            # Check if role exists
            existing_role = session.query(ServiceNowRole).filter(
                ServiceNowRole.name == role_data['name'],
                ServiceNowRole.module_id == module_id
            ).first()
            
            if existing_role:
                # Update existing role
                for key, value in role_data.items():
                    if hasattr(existing_role, key):
                        setattr(existing_role, key, value)
                existing_role.updated_at = datetime.utcnow()
                role = existing_role
            else:
                # Create new role
                role = ServiceNowRole(**role_data)
                session.add(role)
            
            session.commit()
            session.refresh(role)
            return role
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error saving role: {e}")
            raise
        finally:
            session.close()
    
    def save_table(self, table_data: Dict[str, Any], module_id: str) -> ServiceNowTable:
        """Save ServiceNow table to database"""
        session = self.get_session()
        try:
            table_data['module_id'] = module_id
            
            # Check if table exists
            existing_table = session.query(ServiceNowTable).filter(
                ServiceNowTable.name == table_data['name'],
                ServiceNowTable.module_id == module_id
            ).first()
            
            if existing_table:
                # Update existing table
                for key, value in table_data.items():
                    if hasattr(existing_table, key):
                        setattr(existing_table, key, value)
                existing_table.updated_at = datetime.utcnow()
                table = existing_table
            else:
                # Create new table
                table = ServiceNowTable(**table_data)
                session.add(table)
            
            session.commit()
            session.refresh(table)
            return table
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error saving table: {e}")
            raise
        finally:
            session.close()
    
    def save_property(self, property_data: Dict[str, Any], module_id: str) -> ServiceNowProperty:
        """Save ServiceNow property to database"""
        session = self.get_session()
        try:
            property_data['module_id'] = module_id
            
            # Check if property exists
            existing_property = session.query(ServiceNowProperty).filter(
                ServiceNowProperty.name == property_data['name'],
                ServiceNowProperty.module_id == module_id
            ).first()
            
            if existing_property:
                # Update existing property
                for key, value in property_data.items():
                    if hasattr(existing_property, key):
                        setattr(existing_property, key, value)
                existing_property.updated_at = datetime.utcnow()
                property_obj = existing_property
            else:
                # Create new property
                property_obj = ServiceNowProperty(**property_data)
                session.add(property_obj)
            
            session.commit()
            session.refresh(property_obj)
            return property_obj
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error saving property: {e}")
            raise
        finally:
            session.close()
    
    def save_scheduled_job(self, job_data: Dict[str, Any], module_id: str) -> ServiceNowScheduledJob:
        """Save ServiceNow scheduled job to database"""
        session = self.get_session()
        try:
            job_data['module_id'] = module_id
            
            # Check if job exists
            existing_job = session.query(ServiceNowScheduledJob).filter(
                ServiceNowScheduledJob.name == job_data['name'],
                ServiceNowScheduledJob.module_id == module_id
            ).first()
            
            if existing_job:
                # Update existing job
                for key, value in job_data.items():
                    if hasattr(existing_job, key):
                        setattr(existing_job, key, value)
                existing_job.updated_at = datetime.utcnow()
                job = existing_job
            else:
                # Create new job
                job = ServiceNowScheduledJob(**job_data)
                session.add(job)
            
            session.commit()
            session.refresh(job)
            return job
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error saving scheduled job: {e}")
            raise
        finally:
            session.close()
    
    def get_all_modules(self) -> List[ServiceNowModule]:
        """Get all ServiceNow modules"""
        session = self.get_session()
        try:
            return session.query(ServiceNowModule).filter(ServiceNowModule.is_active == True).all()
        finally:
            session.close()
    
    def get_module_by_name(self, name: str) -> Optional[ServiceNowModule]:
        """Get module by name"""
        session = self.get_session()
        try:
            return session.query(ServiceNowModule).filter(
                ServiceNowModule.name == name,
                ServiceNowModule.is_active == True
            ).first()
        finally:
            session.close()
    
    def get_tables_by_module(self, module_id: str) -> List[ServiceNowTable]:
        """Get all tables for a module"""
        session = self.get_session()
        try:
            return session.query(ServiceNowTable).filter(
                ServiceNowTable.module_id == module_id,
                ServiceNowTable.is_active == True
            ).all()
        finally:
            session.close()
    
    def get_properties_by_module(self, module_id: str) -> List[ServiceNowProperty]:
        """Get all properties for a module"""
        session = self.get_session()
        try:
            return session.query(ServiceNowProperty).filter(
                ServiceNowProperty.module_id == module_id,
                ServiceNowProperty.is_active == True
            ).all()
        finally:
            session.close()
    
    def search_tables(self, query: str) -> List[ServiceNowTable]:
        """Search tables by name or description"""
        session = self.get_session()
        try:
            return session.query(ServiceNowTable).filter(
                ServiceNowTable.is_active == True,
                (ServiceNowTable.name.ilike(f"%{query}%") | 
                 ServiceNowTable.label.ilike(f"%{query}%") |
                 ServiceNowTable.description.ilike(f"%{query}%"))
            ).all()
        finally:
            session.close()
    
    def get_database_statistics(self) -> Dict[str, int]:
        """Get database statistics"""
        session = self.get_session()
        try:
            stats = {
                'modules': session.query(ServiceNowModule).filter(ServiceNowModule.is_active == True).count(),
                'roles': session.query(ServiceNowRole).filter(ServiceNowRole.is_active == True).count(),
                'tables': session.query(ServiceNowTable).filter(ServiceNowTable.is_active == True).count(),
                'properties': session.query(ServiceNowProperty).filter(ServiceNowProperty.is_active == True).count(),
                'scheduled_jobs': session.query(ServiceNowScheduledJob).count()
            }
            return stats
        finally:
            session.close()
    
    def save_role(self, role_data: Dict[str, Any]) -> ServiceNowRole:
        """Save ServiceNow role to database (simplified version)"""
        session = self.get_session()
        try:
            # Find or create module
            module_name = role_data.get('module', 'Unknown')
            module = session.query(ServiceNowModule).filter(
                ServiceNowModule.name == module_name
            ).first()
            
            if not module:
                module = ServiceNowModule(
                    name=module_name,
                    label=module_name,
                    description=f"Module for {module_name}",
                    module_type="scraped"
                )
                session.add(module)
                session.flush()
            
            # Check if role exists
            existing_role = session.query(ServiceNowRole).filter(
                ServiceNowRole.name == role_data['name'],
                ServiceNowRole.module_id == module.id
            ).first()
            
            if existing_role:
                # Update existing role
                for key, value in role_data.items():
                    if hasattr(existing_role, key) and key not in ['module', 'active', 'grantable', 'source', 'instance_url', 'sys_id']:
                        # Ensure permissions and dependencies are lists (PostgreSQL ARRAY handles the rest)
                        if key in ['permissions', 'dependencies'] and not isinstance(value, list):
                            setattr(existing_role, key, [])
                        else:
                            setattr(existing_role, key, value)
                existing_role.updated_at = datetime.utcnow()
                role = existing_role
            else:
                # Create new role - remove module from role_data and set module_id
                role_data_copy = role_data.copy()
                role_data_copy.pop('module', None)  # Remove module string
                role_data_copy.pop('active', None)  # Remove active field (not in model)
                role_data_copy.pop('grantable', None)  # Remove grantable field (not in model)
                role_data_copy.pop('source', None)  # Remove source field (not in model)
                role_data_copy.pop('instance_url', None)  # Remove instance_url field (not in model)
                role_data_copy.pop('sys_id', None)  # Remove sys_id field (not in model)
                
                # Ensure permissions and dependencies are lists (PostgreSQL ARRAY handles the rest)
                if 'permissions' in role_data_copy and not isinstance(role_data_copy['permissions'], list):
                    role_data_copy['permissions'] = []
                if 'dependencies' in role_data_copy and not isinstance(role_data_copy['dependencies'], list):
                    role_data_copy['dependencies'] = []
                
                role_data_copy['module_id'] = module.id
                role = ServiceNowRole(**role_data_copy)
                session.add(role)
            
            session.commit()
            session.refresh(role)
            return role
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error saving role: {e}")
            raise
        finally:
            session.close()
    
    def save_table(self, table_data: Dict[str, Any]) -> ServiceNowTable:
        """Save ServiceNow table to database (simplified version)"""
        session = self.get_session()
        try:
            # Find or create module
            module_name = table_data.get('module', 'Unknown')
            module = session.query(ServiceNowModule).filter(
                ServiceNowModule.name == module_name
            ).first()
            
            if not module:
                module = ServiceNowModule(
                    name=module_name,
                    label=module_name,
                    description=f"Module for {module_name}",
                    module_type="scraped"
                )
                session.add(module)
                session.flush()
            
            # Check if table exists
            existing_table = session.query(ServiceNowTable).filter(
                ServiceNowTable.name == table_data['name'],
                ServiceNowTable.module_id == module.id
            ).first()
            
            if existing_table:
                # Update existing table
                for key, value in table_data.items():
                    if hasattr(existing_table, key) and key not in ['module', 'active', 'super_class', 'source', 'instance_url', 'sys_id']:
                        # Ensure array fields are lists (PostgreSQL ARRAY handles the rest)
                        array_fields = ['fields', 'relationships', 'access_controls', 'business_rules', 'scripts']
                        if key in array_fields and not isinstance(value, list):
                            setattr(existing_table, key, [])
                        else:
                            setattr(existing_table, key, value)
                existing_table.updated_at = datetime.utcnow()
                table = existing_table
            else:
                # Create new table - remove invalid fields from table_data and set module_id
                table_data_copy = table_data.copy()
                table_data_copy.pop('module', None)  # Remove module string
                table_data_copy.pop('url', None)  # Remove url field (not in ServiceNowTable model)
                table_data_copy.pop('scraped_at', None)  # Remove scraped_at field (not in ServiceNowTable model)
                table_data_copy.pop('scraper_type', None)  # Remove scraper_type field (not in ServiceNowTable model)
                table_data_copy.pop('active', None)  # Remove active field (not in model)
                table_data_copy.pop('super_class', None)  # Remove super_class field (not in model)
                table_data_copy.pop('source', None)  # Remove source field (not in model)
                table_data_copy.pop('instance_url', None)  # Remove instance_url field (not in model)
                table_data_copy.pop('sys_id', None)  # Remove sys_id field (not in model)
                
                # Ensure array fields are lists (PostgreSQL ARRAY handles the rest)
                array_fields = ['fields', 'relationships', 'access_controls', 'business_rules', 'scripts']
                for field in array_fields:
                    if field in table_data_copy and not isinstance(table_data_copy[field], list):
                        table_data_copy[field] = []
                
                table_data_copy['module_id'] = module.id
                # Ensure label is provided
                if 'label' not in table_data_copy or not table_data_copy['label']:
                    table_data_copy['label'] = table_data_copy['name'].replace('_', ' ').title()
                # Ensure table_type is provided
                if 'table_type' not in table_data_copy or not table_data_copy['table_type']:
                    table_data_copy['table_type'] = 'base'
                table = ServiceNowTable(**table_data_copy)
                session.add(table)
            
            session.commit()
            session.refresh(table)
            return table
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error saving table: {e}")
            raise
        finally:
            session.close()
    
    def save_property(self, property_data: Dict[str, Any]) -> ServiceNowProperty:
        """Save ServiceNow property to database (simplified version)"""
        session = self.get_session()
        try:
            # Find or create module
            module_name = property_data.get('module', 'Unknown')
            module = session.query(ServiceNowModule).filter(
                ServiceNowModule.name == module_name
            ).first()
            
            if not module:
                module = ServiceNowModule(
                    name=module_name,
                    label=module_name,
                    description=f"Module for {module_name}",
                    module_type="scraped"
                )
                session.add(module)
                session.flush()
            
            # Check if property exists
            existing_property = session.query(ServiceNowProperty).filter(
                ServiceNowProperty.name == property_data['name'],
                ServiceNowProperty.module_id == module.id
            ).first()
            
            if existing_property:
                # Update existing property
                for key, value in property_data.items():
                    if hasattr(existing_property, key) and key not in ['module', 'source', 'instance_url', 'sys_id']:
                        setattr(existing_property, key, value)
                existing_property.updated_at = datetime.utcnow()
                property_obj = existing_property
            else:
                # Create new property - remove invalid fields from property_data and set module_id
                property_data_copy = property_data.copy()
                property_data_copy.pop('module', None)  # Remove module string
                property_data_copy.pop('source', None)  # Remove source field (not in model)
                property_data_copy.pop('instance_url', None)  # Remove instance_url field (not in model)
                property_data_copy.pop('sys_id', None)  # Remove sys_id field (not in model)
                property_data_copy['module_id'] = module.id
                # Convert 'value' to 'current_value' if present
                if 'value' in property_data_copy:
                    property_data_copy['current_value'] = property_data_copy.pop('value')
                # Convert 'type' to 'property_type' if present
                if 'type' in property_data_copy:
                    property_data_copy['property_type'] = property_data_copy.pop('type')
                property_obj = ServiceNowProperty(**property_data_copy)
                session.add(property_obj)
            
            session.commit()
            session.refresh(property_obj)
            return property_obj
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error saving property: {e}")
            raise
        finally:
            session.close()
    
    def save_scheduled_job(self, job_data: Dict[str, Any]) -> ServiceNowScheduledJob:
        """Save ServiceNow scheduled job to database (simplified version)"""
        session = self.get_session()
        try:
            # Find or create module
            module_name = job_data.get('module', 'Unknown')
            module = session.query(ServiceNowModule).filter(
                ServiceNowModule.name == module_name
            ).first()
            
            if not module:
                module = ServiceNowModule(
                    name=module_name,
                    label=module_name,
                    description=f"Module for {module_name}",
                    module_type="scraped"
                )
                session.add(module)
                session.flush()
            
            # Check if job exists
            existing_job = session.query(ServiceNowScheduledJob).filter(
                ServiceNowScheduledJob.name == job_data['name'],
                ServiceNowScheduledJob.module_id == module.id
            ).first()
            
            if existing_job:
                # Update existing job
                for key, value in job_data.items():
                    if hasattr(existing_job, key) and key not in ['module', 'run_type', 'condition', 'documentation_url', 'source', 'instance_url', 'sys_id']:
                        # Convert empty strings to None for timestamp fields
                        if key in ['last_run', 'next_run']:
                            value = self._convert_timestamp(value)
                        setattr(existing_job, key, value)
                existing_job.updated_at = datetime.utcnow()
                job = existing_job
            else:
                # Create new job - remove invalid fields from job_data and set module_id
                job_data_copy = job_data.copy()
                job_data_copy.pop('module', None)  # Remove module string
                job_data_copy.pop('url', None)  # Remove url field (not in ServiceNowScheduledJob model)
                job_data_copy.pop('scraped_at', None)  # Remove scraped_at field (not in ServiceNowScheduledJob model)
                job_data_copy.pop('scraper_type', None)  # Remove scraper_type field (not in ServiceNowScheduledJob model)
                job_data_copy.pop('run_type', None)  # Remove run_type field (not in model)
                job_data_copy.pop('condition', None)  # Remove condition field (not in model)
                job_data_copy.pop('documentation_url', None)  # Remove documentation_url field (not in model)
                job_data_copy.pop('source', None)  # Remove source field (not in model)
                job_data_copy.pop('instance_url', None)  # Remove instance_url field (not in model)
                job_data_copy.pop('sys_id', None)  # Remove sys_id field (not in model)
                
                # Convert empty strings to None for timestamp fields
                if 'last_run' in job_data_copy:
                    job_data_copy['last_run'] = self._convert_timestamp(job_data_copy['last_run'])
                if 'next_run' in job_data_copy:
                    job_data_copy['next_run'] = self._convert_timestamp(job_data_copy['next_run'])
                
                job_data_copy['module_id'] = module.id
                job = ServiceNowScheduledJob(**job_data_copy)
                session.add(job)
            
            session.commit()
            session.refresh(job)
            return job
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error saving scheduled job: {e}")
            raise
        finally:
            session.close()
    
    def get_recent_tables(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent tables from database"""
        session = self.get_session()
        try:
            tables = session.query(ServiceNowTable).filter(
                ServiceNowTable.is_active == True
            ).order_by(ServiceNowTable.created_at.desc()).limit(limit).all()
            
            return [{
                'name': table.name,
                'module': table.module.name if table.module else 'Unknown',
                'description': table.description or '',
                'created_at': table.created_at.strftime('%Y-%m-%d %H:%M:%S') if table.created_at else ''
            } for table in tables]
        finally:
            session.close()
    
    def get_recent_roles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent roles from database"""
        session = self.get_session()
        try:
            roles = session.query(ServiceNowRole).filter(
                ServiceNowRole.is_active == True
            ).order_by(ServiceNowRole.created_at.desc()).limit(limit).all()
            
            return [{
                'name': role.name,
                'module': role.module.name if role.module else 'Unknown',
                'description': role.description or '',
                'created_at': role.created_at.strftime('%Y-%m-%d %H:%M:%S') if role.created_at else ''
            } for role in roles]
        finally:
            session.close()
    
    def get_recent_properties(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent properties from database"""
        session = self.get_session()
        try:
            properties = session.query(ServiceNowProperty).filter(
                ServiceNowProperty.is_active == True
            ).order_by(ServiceNowProperty.created_at.desc()).limit(limit).all()
            
            return [{
                'name': prop.name,
                'module': prop.module.name if prop.module else 'Unknown',
                'value': prop.current_value or '',
                'type': prop.property_type or 'string',
                'created_at': prop.created_at.strftime('%Y-%m-%d %H:%M:%S') if prop.created_at else ''
            } for prop in properties]
        finally:
            session.close()
    
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
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        session = self.get_session()
        try:
            from database import ServiceNowModule, ServiceNowRole, ServiceNowTable, ServiceNowProperty, ServiceNowScheduledJob
            
            stats = {
                'modules': session.query(ServiceNowModule).count(),
                'roles': session.query(ServiceNowRole).count(),
                'tables': session.query(ServiceNowTable).count(),
                'properties': session.query(ServiceNowProperty).count(),
                'scheduled_jobs': session.query(ServiceNowScheduledJob).count(),
                'active_modules': session.query(ServiceNowModule).filter(ServiceNowModule.is_active == True).count(),
                'active_roles': session.query(ServiceNowRole).filter(ServiceNowRole.is_active == True).count(),
                'active_tables': session.query(ServiceNowTable).filter(ServiceNowTable.is_active == True).count(),
                'active_properties': session.query(ServiceNowProperty).filter(ServiceNowProperty.is_active == True).count(),
                'active_scheduled_jobs': session.query(ServiceNowScheduledJob).filter(ServiceNowScheduledJob.active == True).count()
            }
            
            return stats
        except Exception as e:
            self.logger.error(f"Error getting database statistics: {e}")
            return {}
        finally:
            session.close()
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database configuration and connection information"""
        try:
            # Parse database URL to extract connection details
            db_url = self.database_url
            
            # Extract connection details from URL
            if db_url.startswith('postgresql://user:password@host:port/database'):
                # PostgreSQL URL format: postgresql://user:password@host:port/database'postgresql://user:password@host:port/database'
                match = re.match(pattern, db_url)
                if match:
                    username, password, host, port, database = match.groups()
                    
                    # Test connection
                    connected = False
                    try:
                        session = self.get_session()
                        session.execute("SELECT 1")
                        session.close()
                        connected = True
                    except:
                        connected = False
                    
                    # Get database statistics
                    stats = self.get_database_statistics()
                    
                    return {
                        'db_type': 'PostgreSQL',
                        'host': host,
                        'port': port,
                        'database': database,
                        'username': username,
                        'password': '***' + password[-3:] if len(password) > 3 else '***',
                        'connected': connected,
                        'tables_created': stats.get('modules', 0) > 0,
                        'last_updated': 'Just now',
                        'full_url': db_url,
                        'connection_pool_size': getattr(self.engine.pool, 'size', 'Unknown'),
                        'max_overflow': getattr(self.engine.pool, 'max_overflow', 'Unknown'),
                        'pool_timeout': getattr(self.engine.pool, 'timeout', 'Unknown'),
                        'statistics': stats
                    }
            elif db_url.startswith('mysql://user:password@host:port/database'):
                # MySQL URL format: mysql://user:password@host:port/database'mysql://user:password@host:port/database'
                match = re.match(pattern, db_url)
                if match:
                    username, password, host, port, database = match.groups()
                    
                    # Test connection
                    connected = False
                    try:
                        session = self.get_session()
                        session.execute("SELECT 1")
                        session.close()
                        connected = True
                    except:
                        connected = False
                    
                    # Get database statistics
                    stats = self.get_database_statistics()
                    
                    return {
                        'db_type': 'MySQL',
                        'host': host,
                        'port': port,
                        'database': database,
                        'username': username,
                        'password': '***' + password[-3:] if len(password) > 3 else '***',
                        'connected': connected,
                        'tables_created': stats.get('modules', 0) > 0,
                        'last_updated': 'Just now',
                        'full_url': db_url,
                        'connection_pool_size': getattr(self.engine.pool, 'size', 'Unknown'),
                        'max_overflow': getattr(self.engine.pool, 'max_overflow', 'Unknown'),
                        'pool_timeout': getattr(self.engine.pool, 'timeout', 'Unknown'),
                        'statistics': stats
                    }
            
            # Fallback for other URL formats
            return {
                'db_type': 'Unknown',
                'host': 'Unknown',
                'port': 'Unknown',
                'database': 'Unknown',
                'username': 'Unknown',
                'password': 'Unknown',
                'connected': False,
                'tables_created': False,
                'last_updated': 'Unknown',
                'full_url': db_url,
                'connection_pool_size': 'Unknown',
                'max_overflow': 'Unknown',
                'pool_timeout': 'Unknown',
                'statistics': {}
            }
            
        except Exception as e:
            self.logger.error(f"Error getting database info: {e}")
            return {
                'db_type': 'Error',
                'host': 'Error',
                'port': 'Error',
                'database': 'Error',
                'username': 'Error',
                'password': 'Error',
                'connected': False,
                'tables_created': False,
                'last_updated': 'Error',
                'full_url': 'Error',
                'connection_pool_size': 'Error',
                'max_overflow': 'Error',
                'pool_timeout': 'Error',
                'statistics': {},
                'error': str(e)
            }

    # ServiceNow Configuration Methods
    def save_servicenow_configuration(self, config_data: Dict[str, Any]) -> bool:
        """Save ServiceNow configuration using centralized configuration"""
        try:
            return self.centralized_config.save_servicenow_configuration(config_data)
        except Exception as e:
            self.logger.error(f"Failed to save ServiceNow configuration: {e}")
            return False
    
    def get_servicenow_configuration(self, name: str = 'default') -> Optional[Dict[str, Any]]:
        """Get ServiceNow configuration using centralized configuration"""
        try:
            return self.centralized_config.get_servicenow_configuration(name)
        except Exception as e:
            self.logger.error(f"Failed to get ServiceNow configuration: {e}")
            return None
    
    def get_all_servicenow_configurations(self) -> List[ServiceNowConfiguration]:
        """Get all ServiceNow configurations from database"""
        session = self.get_session()
        try:
            configs = session.query(ServiceNowConfiguration).filter_by(is_active=True).all()
            return configs
        except Exception as e:
            self.logger.error(f"Failed to get ServiceNow configurations: {e}")
            return []
        finally:
            session.close()
    
    def delete_servicenow_configuration(self, name: str) -> bool:
        """Delete ServiceNow configuration from database"""
        session = self.get_session()
        try:
            config = session.query(ServiceNowConfiguration).filter_by(name=name).first()
            if config:
                session.delete(config)
                session.commit()
                self.logger.info(f"Deleted ServiceNow configuration: {name}")
                return True
            return False
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to delete ServiceNow configuration: {e}")
            return False
        finally:
            session.close()

    # Database Configuration Methods
    def save_database_configuration(self, config_data: Dict[str, Any]) -> bool:
        """Save database configuration using centralized configuration"""
        try:
            return self.centralized_config.save_database_configuration(config_data)
        except Exception as e:
            self.logger.error(f"Failed to save database configuration: {e}")
            return False
    
    def get_database_configuration(self, name: str = 'default') -> Optional[Dict[str, Any]]:
        """Get database configuration using centralized configuration"""
        try:
            return self.centralized_config.get_database_configuration(name)
        except Exception as e:
            self.logger.error(f"Failed to get database configuration: {e}")
            return None
    
    def get_all_database_configurations(self) -> List[DatabaseConfiguration]:
        """Get all database configurations from database"""
        session = self.get_session()
        try:
            # Use raw SQL to avoid permission issues
            from sqlalchemy import text
            result = session.execute(text("""
                SELECT id, name, db_type, host, port, database_name, username, password,
                       connection_pool_size, max_overflow, echo, is_active, created_at, updated_at
                FROM database_configurations 
                WHERE is_active = true
                ORDER BY name
            """))
            
            configs = []
            for row in result:
                config = DatabaseConfiguration()
                config.id = row[0]
                config.name = row[1]
                config.db_type = row[2]
                config.host = row[3]
                config.port = row[4]
                config.database_name = row[5]
                config.username = row[6]
                config.password = row[7]
                config.connection_pool_size = row[8]
                config.max_overflow = row[9]
                config.echo = row[10]
                config.is_active = row[11]
                config.created_at = row[12]
                config.updated_at = row[13]
                configs.append(config)
            
            return configs
        except Exception as e:
            self.logger.error(f"Failed to get database configurations: {e}")
            return []
        finally:
            session.close()
    
    def delete_database_configuration(self, name: str) -> bool:
        """Delete database configuration from database"""
        session = self.get_session()
        try:
            config = session.query(DatabaseConfiguration).filter_by(name=name).first()
            if config:
                session.delete(config)
                session.commit()
                self.logger.info(f"Deleted database configuration: {name}")
                return True
            return False
        except Exception as e:
            session.rollback()
            self.logger.error(f"Failed to delete database configuration: {e}")
            return False
        finally:
            session.close()


class DatabaseIntrospector:
    """Database introspector for MySQL/PostgreSQL ServiceNow instances"""
    
    def __init__(self, connection_string: str, db_type: str = 'postgresql'):
        self.connection_string = connection_string
        self.db_type = db_type
        self.engine = create_engine(connection_string)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for database introspection"""
        logger = logging.getLogger('database_introspector')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def introspect_tables(self) -> List[Dict[str, Any]]:
        """Introspect database tables"""
        session = self.SessionLocal()
        try:
            from sqlalchemy import text
            
            if self.db_type == 'postgresql':
                # First, get all available schemas
                schema_query = """
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY schema_name
                """
                schema_result = session.execute(text(schema_query))
                available_schemas = [row[0] for row in schema_result.fetchall()]
                
                # Then get tables from all schemas
                query = """
                SELECT 
                    table_name,
                    table_type,
                    table_schema
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY table_schema, table_name
                """
            else:  # MySQL
                query = """
                SELECT 
                    table_name,
                    table_type,
                    table_schema
                FROM information_schema.tables 
                WHERE table_schema NOT IN ('information_schema', 'performance_schema', 'mysql', 'sys')
                ORDER BY table_schema, table_name
                """
                available_schemas = ['public']  # Default for MySQL
            result = session.execute(text(query))
            tables = []
            
            for row in result:
                tables.append({
                    'name': row[0],
                    'type': row[1],
                    'schema': row[2]
                })
            
            # Log schema information for debugging
            if self.db_type == 'postgresql':
                self.logger.info(f"Available schemas: {available_schemas}")
                schema_counts = {}
                for table in tables:
                    schema = table['schema']
                    schema_counts[schema] = schema_counts.get(schema, 0) + 1
                self.logger.info(f"Tables per schema: {schema_counts}")
            
            return tables
            
        except Exception as e:
            self.logger.error(f"Error introspecting tables: {e}")
            return []
        finally:
            session.close()
    
    def introspect_table_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """Introspect table columns"""
        session = self.SessionLocal()
        try:
            if self.db_type == 'postgresql':
                query = """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = :table_name
                ORDER BY ordinal_position
                """
            else:  # MySQL
                query = """
                SELECT 
                    column_name,
                    data_type,
                    is_nullable,
                    column_default,
                    character_maximum_length
                FROM information_schema.columns 
                WHERE table_name = :table_name
                ORDER BY ordinal_position
                """
            
            from sqlalchemy import text
            result = session.execute(text(query), {'table_name': table_name})
            columns = []
            
            for row in result:
                columns.append({
                    'name': row[0],
                    'type': row[1],
                    'nullable': row[2] == 'YES',
                    'default': row[3],
                    'max_length': row[4]
                })
            
            return columns
            
        except Exception as e:
            self.logger.error(f"Error introspecting table columns for {table_name}: {e}")
            return []
        finally:
            session.close()
    
    def introspect_foreign_keys(self, table_name: str) -> List[Dict[str, Any]]:
        """Introspect foreign key relationships"""
        session = self.SessionLocal()
        try:
            if self.db_type == 'postgresql':
                query = """
                SELECT 
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                    AND tc.table_name = :table_name
                """
            else:  # MySQL
                query = """
                SELECT 
                    constraint_name,
                    table_name,
                    column_name,
                    referenced_table_name,
                    referenced_column_name
                FROM information_schema.key_column_usage
                WHERE referenced_table_name IS NOT NULL
                    AND table_name = :table_name
                """
            
            from sqlalchemy import text
            result = session.execute(text(query), {'table_name': table_name})
            foreign_keys = []
            
            for row in result:
                foreign_keys.append({
                    'constraint_name': row[0],
                    'table_name': row[1],
                    'column_name': row[2],
                    'foreign_table_name': row[3],
                    'foreign_column_name': row[4]
                })
            
            return foreign_keys
            
        except Exception as e:
            self.logger.error(f"Error introspecting foreign keys for {table_name}: {e}")
            return []
        finally:
            session.close()
    
    def get_recent_roles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent roles"""
        session = self.get_session()
        try:
            roles = session.query(ServiceNowRole).join(ServiceNowModule).order_by(
                ServiceNowRole.created_at.desc()
            ).limit(limit).all()
            
            return [{
                'name': role.name,
                'module': role.module.name if role.module else 'Unknown',
                'created_at': role.created_at
            } for role in roles]
        except Exception as e:
            self.logger.error(f"Error getting recent roles: {e}")
            return []
        finally:
            session.close()
    
    def get_recent_tables(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent tables"""
        session = self.get_session()
        try:
            tables = session.query(ServiceNowTable).join(ServiceNowModule).order_by(
                ServiceNowTable.created_at.desc()
            ).limit(limit).all()
            
            return [{
                'name': table.name,
                'module': table.module.name if table.module else 'Unknown',
                'created_at': table.created_at
            } for table in tables]
        except Exception as e:
            self.logger.error(f"Error getting recent tables: {e}")
            return []
        finally:
            session.close()
    
    def get_recent_properties(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent properties"""
        session = self.get_session()
        try:
            properties = session.query(ServiceNowProperty).join(ServiceNowModule).order_by(
                ServiceNowProperty.created_at.desc()
            ).limit(limit).all()
            
            return [{
                'name': prop.name,
                'module': prop.module.name if prop.module else 'Unknown',
                'created_at': prop.created_at
            } for prop in properties]
        except Exception as e:
            self.logger.error(f"Error getting recent properties: {e}")
            return []
        finally:
            session.close()
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get database configuration and connection information"""
        try:
            # Parse database URL to extract connection details
            db_url = self.database_url
            
            # Extract connection details from URL
            if db_url.startswith('postgresql://user:password@host:port/database'):
                # PostgreSQL URL format: postgresql://user:password@host:port/database'postgresql://user:password@host:port/database'
                match = re.match(pattern, db_url)
                if match:
                    username, password, host, port, database = match.groups()
                    
                    # Test connection
                    connected = False
                    try:
                        session = self.get_session()
                        session.execute("SELECT 1")
                        session.close()
                        connected = True
                    except:
                        connected = False
                    
                    # Get database statistics
                    stats = self.get_database_statistics()
                    
                    return {
                        'db_type': 'PostgreSQL',
                        'host': host,
                        'port': port,
                        'database': database,
                        'username': username,
                        'password': '***' + password[-3:] if len(password) > 3 else '***',
                        'connected': connected,
                        'tables_created': stats.get('modules', 0) > 0,
                        'last_updated': 'Just now',
                        'full_url': db_url,
                        'connection_pool_size': getattr(self.engine.pool, 'size', 'Unknown'),
                        'max_overflow': getattr(self.engine.pool, 'max_overflow', 'Unknown'),
                        'pool_timeout': getattr(self.engine.pool, 'timeout', 'Unknown'),
                        'statistics': stats
                    }
            elif db_url.startswith('mysql://user:password@host:port/database'):
                # MySQL URL format: mysql://user:password@host:port/database'mysql://user:password@host:port/database'
                match = re.match(pattern, db_url)
                if match:
                    username, password, host, port, database = match.groups()
                    
                    # Test connection
                    connected = False
                    try:
                        session = self.get_session()
                        session.execute("SELECT 1")
                        session.close()
                        connected = True
                    except:
                        connected = False
                    
                    # Get database statistics
                    stats = self.get_database_statistics()
                    
                    return {
                        'db_type': 'MySQL',
                        'host': host,
                        'port': port,
                        'database': database,
                        'username': username,
                        'password': '***' + password[-3:] if len(password) > 3 else '***',
                        'connected': connected,
                        'tables_created': stats.get('modules', 0) > 0,
                        'last_updated': 'Just now',
                        'full_url': db_url,
                        'connection_pool_size': getattr(self.engine.pool, 'size', 'Unknown'),
                        'max_overflow': getattr(self.engine.pool, 'max_overflow', 'Unknown'),
                        'pool_timeout': getattr(self.engine.pool, 'timeout', 'Unknown'),
                        'statistics': stats
                    }
            
            # Fallback for other URL formats
            return {
                'db_type': 'Unknown',
                'host': 'Unknown',
                'port': 'Unknown',
                'database': 'Unknown',
                'username': 'Unknown',
                'password': 'Unknown',
                'connected': False,
                'tables_created': False,
                'last_updated': 'Unknown',
                'full_url': db_url,
                'connection_pool_size': 'Unknown',
                'max_overflow': 'Unknown',
                'pool_timeout': 'Unknown',
                'statistics': {}
            }
            
        except Exception as e:
            self.logger.error(f"Error getting database info: {e}")
            return {
                'db_type': 'Error',
                'host': 'Error',
                'port': 'Error',
                'database': 'Error',
                'username': 'Error',
                'password': 'Error',
                'connected': False,
                'tables_created': False,
                'last_updated': 'Error',
                'full_url': 'Error',
                'connection_pool_size': 'Error',
                'max_overflow': 'Error',
                'pool_timeout': 'Error',
                'statistics': {},
                'error': str(e)
            }


def initialize_database():
    """Initialize the database with tables"""
    db_manager = DatabaseManager()
    db_manager.create_tables()
    return db_manager


if __name__ == "__main__":
    # Initialize database
    db = initialize_database()
    print("✅ Database initialized successfully")
    
    # Test database connection
    stats = db.get_database_statistics()
    print(f"📊 Database statistics: {stats}")

# Created By: Ashish Gautam; LinkedIn: https://www.linkedin.com/in/ashishgautamkarn/
