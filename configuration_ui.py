"""
Configuration Management UI
Handles dynamic configuration of sensitive settings like database credentials and API keys.
"""

import streamlit as st
import os
import yaml
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import secrets
import string
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

class ConfigurationManager:
    """Manages application configuration with secure credential handling"""
    
    def __init__(self):
        self.config_file = "config.yaml"
        self.env_file = ".env"
        self.load_config()
    
    def load_config(self):
        """Load configuration from files"""
        # Load environment variables
        load_dotenv(self.env_file)
        
        # Load YAML config
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'database': {
                'db_type': 'postgresql',
                'host': 'localhost',
                'port': 5432,
                'database_name': 'servicenow_docs',
                'username': 'servicenow_user',
                'password': '',
                'connection_pool_size': 10,
                'max_overflow': 20,
                'echo': False
            },
            'servicenow': {
                'instance_url': '',
                'username': '',
                'password': '',
                'api_version': 'v2',
                'timeout': 30,
                'max_retries': 3,
                'verify_ssl': True
            },
            'scraper': {
                'base_url': 'https://www.servicenow.com/docs',
                'timeout_seconds': 60,
                'max_concurrent_requests': 5,
                'max_pages': 100,
                'delay_seconds': 1.0,
                'use_selenium': False,
                'discover_links': True,
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'chrome_options': [
                    '--headless',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--window-size=1920,1080'
                ]
            },
            'security': {
                'api_key_required': False,
                'rate_limit_enabled': True,
                'max_requests_per_minute': 60,
                'enable_ssl': True,
                'allowed_hosts': ['localhost', '127.0.0.1']
            },
            'visualization': {
                'default_layout': 'spring',
                'color_scheme': 'default',
                'node_size_multiplier': 2.0,
                'edge_width': 2.0,
                'animation_duration': 1000,
                'max_nodes_display': 100,
                'enable_interactions': True
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file_path': 'logs/servicenow_docs.log',
                'max_file_size': 10485760,
                'backup_count': 5,
                'console_output': True
            },
            'automation': {
                'auto_scrape_enabled': False,
                'scrape_schedule': 'daily',
                'scrape_time': '02:00',
                'auto_cleanup_enabled': True,
                'data_retention_days': 30,
                'backup_enabled': True,
                'backup_schedule': 'weekly',
                'validation_enabled': True
            }
        }
    
    def generate_secure_password(self, length: int = 25) -> str:
        """Generate a secure random password"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def save_config(self):
        """Save configuration to files"""
        # Save YAML config
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
        
        # Save environment variables
        self.save_env_file()
    
    def save_env_file(self):
        """Save environment variables to .env file"""
        env_content = []
        
        # Database configuration
        db_config = self.config.get('database', {})
        env_content.append(f"DB_TYPE={db_config.get('db_type', 'postgresql')}")
        env_content.append(f"DB_HOST={db_config.get('host', 'localhost')}")
        env_content.append(f"DB_PORT={db_config.get('port', 5432)}")
        env_content.append(f"DB_NAME={db_config.get('database_name', 'servicenow_docs')}")
        env_content.append(f"DB_USER={db_config.get('username', 'servicenow_user')}")
        env_content.append(f"DB_PASSWORD={db_config.get('password', '')}")
        
        # Scraper configuration
        scraper_config = self.config.get('scraper', {})
        env_content.append(f"SCRAPER_TIMEOUT={scraper_config.get('timeout_seconds', 60)}")
        env_content.append(f"SCRAPER_USE_SELENIUM={str(scraper_config.get('use_selenium', False)).lower()}")
        
        # Application configuration
        env_content.append("STREAMLIT_SERVER_PORT=8506")
        env_content.append("STREAMLIT_SERVER_ADDRESS=0.0.0.0")
        env_content.append("STREAMLIT_BROWSER_GATHER_USAGE_STATS=false")
        env_content.append("STREAMLIT_SERVER_HEADLESS=true")
        
        # Write to .env file
        with open(self.env_file, 'w') as f:
            f.write('\n'.join(env_content))
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration - prioritize current active connection, then fall back to saved configs"""
        try:
            # First, try to get the current active connection from DatabaseManager
            from database import DatabaseManager
            db_manager = DatabaseManager()
            
            # Parse the current database URL to get connection details
            database_url = db_manager.database_url
            
            if database_url.startswith('postgresql://'):
                # Parse PostgreSQL URL: postgresql://user:password@host:port/database
                import re
                pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
                match = re.match(pattern, database_url)
                if match:
                    username, password, host, port, database = match.groups()
                    return {
                        'host': host,
                        'port': int(port),
                        'database_name': database,
                        'username': username,
                        'db_type': 'postgresql',
                        'password': password,
                        '_source': 'current_connection'
                    }
            elif database_url.startswith('sqlite:///'):
                # Parse SQLite URL: sqlite:///path/to/database
                database_path = database_url.replace('sqlite:///', '')
                return {
                    'host': 'localhost',
                    'port': 0,
                    'database_name': database_path,
                    'username': 'sqlite',
                    'db_type': 'sqlite',
                    'password': '',
                    '_source': 'current_connection'
                }
            elif database_url.startswith('mysql'):
                # Parse MySQL URL: mysql+pymysql://user:password@host:port/database
                import re
                pattern = r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
                match = re.match(pattern, database_url)
                if match:
                    username, password, host, port, database = match.groups()
                    return {
                        'host': host,
                        'port': int(port),
                        'database_name': database,
                        'username': username,
                        'db_type': 'mysql',
                        'password': password,
                        '_source': 'current_connection'
                    }
        except Exception as e:
            # If parsing fails, fall back to saved configuration
            pass
        
        # Fall back to saved database configuration
        try:
            from database import DatabaseManager
            db_manager = DatabaseManager()
            db_config = db_manager.get_database_configuration('default')
            if db_config:
                config_dict = db_config.to_dict()
                # Remove sensitive fields for display
                config_dict.pop('password', None)
                config_dict.pop('id', None)
                config_dict.pop('created_at', None)
                config_dict.pop('updated_at', None)
                config_dict.pop('is_active', None)
                config_dict['_source'] = 'saved_config'
                return config_dict
        except Exception as e:
            # Fall back to config file if database loading fails
            pass
        
        # Fall back to config file
        config = self.config.get('database', {})
        config['_source'] = 'config_file'
        return config
    
    def get_database_password(self) -> str:
        """Get database password - prioritize current active connection, then fall back to saved configs"""
        try:
            # First, try to get the current active connection from DatabaseManager
            from database import DatabaseManager
            db_manager = DatabaseManager()
            
            # Parse the current database URL to get password
            database_url = db_manager.database_url
            
            if database_url.startswith('postgresql://'):
                # Parse PostgreSQL URL: postgresql://user:password@host:port/database
                import re
                pattern = r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
                match = re.match(pattern, database_url)
                if match:
                    username, password, host, port, database = match.groups()
                    return password
            elif database_url.startswith('mysql'):
                # Parse MySQL URL: mysql+pymysql://user:password@host:port/database
                import re
                pattern = r'mysql\+pymysql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
                match = re.match(pattern, database_url)
                if match:
                    username, password, host, port, database = match.groups()
                    return password
        except Exception as e:
            # If parsing fails, fall back to saved configuration
            pass
        
        # Fall back to saved database configuration
        try:
            from database import DatabaseManager
            db_manager = DatabaseManager()
            db_config = db_manager.get_database_configuration('default')
            if db_config:
                return db_config.password or ''
        except Exception as e:
            # Fall back to config file if database loading fails
            pass
        
        # Fall back to config file
        return self.config.get('database', {}).get('password', '')
    
    def get_servicenow_config(self) -> Dict[str, Any]:
        """Get ServiceNow configuration"""
        return self.config.get('servicenow', {})
    
    def update_database_config(self, **kwargs):
        """Update database configuration"""
        if 'database' not in self.config:
            self.config['database'] = {}
        self.config['database'].update(kwargs)
    
    def update_servicenow_config(self, **kwargs):
        """Update ServiceNow configuration"""
        if 'servicenow' not in self.config:
            self.config['servicenow'] = {}
        self.config['servicenow'].update(kwargs)

def show_configuration_ui():
    """Show configuration management UI"""
    st.header("🔧 Configuration Management")
    st.markdown("Manage application settings and credentials securely.")
    
    config_manager = ConfigurationManager()
    
    # Create tabs for different configuration sections
    tab1, tab2, tab3, tab4 = st.tabs(["🗄️ Database", "🔗 ServiceNow", "🛡️ Security", "⚙️ General"])
    
    with tab1:
        show_database_config(config_manager)
    
    with tab2:
        show_servicenow_config(config_manager)
    
    with tab3:
        show_security_config(config_manager)
    
    with tab4:
        show_general_config(config_manager)
    
    # Show footer
    st.markdown("""
    <div class="footer">
        Created By: <strong>Ashish Gautam</strong> | 
        <a href="https://www.linkedin.com/in/ashishgautamkarn/" target="_blank">LinkedIn Profile</a>
    </div>
    """, unsafe_allow_html=True)

def show_database_config(config_manager: ConfigurationManager):
    """Show database configuration UI"""
    st.subheader("Database Configuration")
    
    # Check if configuration is loaded from current connection or saved config
    try:
        from database import DatabaseManager
        db_manager = DatabaseManager()
        db_config_from_db = db_manager.get_database_configuration('default')
        
        # Get current config to check source
        current_config = config_manager.get_database_config()
        config_source = current_config.get('_source', 'unknown')
        
        if config_source == 'current_connection':
            st.success("✅ Using current active database connection")
        elif config_source == 'saved_config':
            st.success("✅ Using saved database configuration from database")
        else:
            st.info("ℹ️ Using database configuration from config files")
    except Exception as e:
        st.info("ℹ️ Using database configuration from config files")
    
    # Show current startup configuration
    st.markdown("### 🚀 Current Startup Configuration")
    startup_config = config_manager.get_database_config()
    st.info(f"**Current startup configuration:** {startup_config.get('host', 'localhost')}:{startup_config.get('port', 5432)}/{startup_config.get('database_name', 'servicenow_docs')} ({startup_config.get('username', 'servicenow_user')})")
    
    # Show saved configurations
    try:
        from database import DatabaseManager
        db_manager = DatabaseManager()
        saved_configs = db_manager.get_all_database_configurations()
        
        if saved_configs:
            st.markdown("### 📋 Saved Database Configurations")
            st.success(f"✅ Found {len(saved_configs)} saved configurations")
            
            config_names = [config.name for config in saved_configs]
            
            # Default to current configuration if available, otherwise "Create New Configuration"
            default_option = "🔄 Current Configuration"
            if default_option not in config_names:
                config_names.insert(0, default_option)
            
            # Set default index to current configuration
            default_index = 0
            
            selected_config = st.selectbox(
                "Select a saved configuration to load:",
                config_names,
                index=default_index,
                help="Load an existing configuration or work with current configuration"
            )
            
            if selected_config == "🔄 Current Configuration":
                # Load current configuration
                st.info("Loading current configuration")
                db_config = config_manager.get_database_config()
            else:
                # Load selected saved configuration
                selected_config_obj = next((config for config in saved_configs if config.name == selected_config), None)
                if selected_config_obj:
                    st.info(f"Loading configuration: **{selected_config_obj.name}**")
                    db_config = selected_config_obj.to_dict()
                    # Remove sensitive fields for display
                    db_config.pop('password', None)
                    db_config.pop('id', None)
                    db_config.pop('created_at', None)
                    db_config.pop('updated_at', None)
                    db_config.pop('is_active', None)
                else:
                    st.warning("Selected configuration not found. Using current configuration.")
                    db_config = config_manager.get_database_config()
        else:
            st.warning("No saved configurations found. Working with current configuration.")
            db_config = config_manager.get_database_config()
    except Exception as e:
        st.error(f"❌ Could not load saved configurations: {e}")
        st.info("Using configuration from config files")
        db_config = config_manager.get_database_config()
    
    # Configuration name input - Enhanced for new configurations
    st.markdown("### 📝 Configuration Name")
    
    # Check if this is a new configuration or existing one
    is_new_config = db_config.get('name', 'default') == 'default' or not db_config.get('name')
    
    if is_new_config:
        st.info("💡 **Creating New Configuration**: Please provide a descriptive name for this database configuration.")
        st.markdown("**Examples**: `production`, `development`, `test`, `staging`, `backup`")
    
    config_name = st.text_input(
        "Configuration Name",
        value=db_config.get('name', 'default'),
        help="Name for this database configuration (e.g., 'production', 'development', 'test')",
        placeholder="Enter a descriptive name for this configuration"
    )
    
    # Validation for configuration name
    if config_name and config_name.strip():
        if config_name.strip() == 'default':
            st.warning("⚠️ **Warning**: Using 'default' as configuration name. Consider using a more descriptive name like 'production' or 'development'.")
        elif len(config_name.strip()) < 3:
            st.error("❌ **Error**: Configuration name must be at least 3 characters long.")
        else:
            st.success(f"✅ **Configuration Name**: `{config_name.strip()}`")
    else:
        st.error("❌ **Error**: Configuration name is required!")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### 🔄 Quick Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📋 Create Configuration from Startup", help="Create a new configuration using the current startup settings"):
            # Pre-fill the form with startup configuration
            startup_config = config_manager.get_database_config()
            st.session_state['prefill_startup'] = True
            st.session_state['prefill_config'] = startup_config
            st.rerun()
    
    with col2:
        if st.button("🔄 Refresh Configurations", help="Reload saved configurations from database"):
            st.rerun()
    
    # Check if we should pre-fill with startup configuration
    if st.session_state.get('prefill_startup', False):
        startup_config = st.session_state.get('prefill_config', {})
        if startup_config:
            st.success("✅ Pre-filled form with startup configuration. Please provide a name and save.")
            # Clear the prefill flag
            st.session_state['prefill_startup'] = False
            st.session_state['prefill_config'] = None
    
    st.markdown("---")
    
    # Database Settings
    st.markdown("### ⚙️ Database Settings")
    col1, col2 = st.columns(2)
    
    with col1:
        db_type = st.selectbox(
            "Database Type",
            ["postgresql", "sqlite", "mysql"],
            index=["postgresql", "sqlite", "mysql"].index(db_config.get('db_type', 'postgresql'))
        )
        
        host = st.text_input(
            "Host",
            value=db_config.get('host', 'localhost'),
            help="Database server hostname or IP address"
        )
        
        port = st.number_input(
            "Port",
            value=db_config.get('port', 5432),
            min_value=1,
            max_value=65535,
            help="Database server port"
        )
    
    with col2:
        database_name = st.text_input(
            "Database Name",
            value=db_config.get('database_name', 'servicenow_docs'),
            help="Name of the database to connect to"
        )
        
        username = st.text_input(
            "Username",
            value=db_config.get('username', 'servicenow_user'),
            help="Database username"
        )
        
        col_pass, col_gen = st.columns([2, 1])
        with col_pass:
            password = st.text_input(
                "Password",
                value=config_manager.get_database_password(),
                type="password",
                help="Database password"
            )
        with col_gen:
            if st.button("🎲 Generate", help="Generate secure password"):
                new_password = config_manager.generate_secure_password()
                st.session_state['generated_password'] = new_password
                st.rerun()
        
        if 'generated_password' in st.session_state:
            password = st.session_state['generated_password']
            st.info(f"Generated password: `{password}`")
    
    # Advanced settings
    with st.expander("🔧 Advanced Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            connection_pool_size = st.number_input(
                "Connection Pool Size",
                value=db_config.get('connection_pool_size', 10),
                min_value=1,
                max_value=100
            )
            
            max_overflow = st.number_input(
                "Max Overflow",
                value=db_config.get('max_overflow', 20),
                min_value=0,
                max_value=100
            )
        
        with col2:
            echo = st.checkbox(
                "Echo SQL Queries",
                value=db_config.get('echo', False),
                help="Log SQL queries (for debugging)"
            )
    
    # Update configuration
    config_manager.update_database_config(
        db_type=db_type,
        host=host,
        port=port,
        database_name=database_name,
        username=username,
        password=password,
        connection_pool_size=connection_pool_size,
        max_overflow=max_overflow,
        echo=echo,
        name=config_name  # Add config name to the update
    )
    
    # Test database connection button
    st.markdown("---")
    if st.button("🔍 Test Database Connection", type="secondary"):
        try:
            # Create a temporary database manager with test configuration
            # instead of updating global environment variables
            from database import DatabaseManager
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            
            # Build database URL for testing
            if db_type == 'postgresql':
                test_database_url = f"postgresql://{username}:{password}@{host}:{port}/{database_name}"
            elif db_type == 'mysql':
                test_database_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}"
            elif db_type == 'sqlite':
                test_database_url = f"sqlite:///{database_name}"
            else:
                test_database_url = f"{db_type}://{username}:{password}@{host}:{port}/{database_name}"
            
            # Create temporary engine and session for testing
            test_engine = create_engine(test_database_url, echo=False)
            TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
            session = TestSessionLocal()
            
            # Test basic connection with simple query
            from sqlalchemy import text
            result = session.execute(text("SELECT 1")).fetchone()
            
            if result:
                st.success("✅ Database connection successful!")
                
                # Check if tables exist
                tables_exist = False
                try:
                    from database import ServiceNowModule
                    module_count = session.query(ServiceNowModule).count()
                    st.info(f"📊 Found {module_count} modules in existing tables")
                    tables_exist = True
                except Exception as table_error:
                    st.info("ℹ️ Database connected but tables don't exist yet.")
                
                
                # Store connection details in session state for table creation
                if not tables_exist:
                    st.session_state.test_connection_details = {
                        'host': host,
                        'port': port,
                        'database_name': database_name,
                        'username': username,
                        'password': password,
                        'db_type': db_type,
                        'test_database_url': test_database_url
                    }
                    st.session_state.tables_need_creation = True
                else:
                    st.session_state.tables_need_creation = False
            
            session.close()
            test_engine.dispose()
            
        except Exception as e:
            st.error(f"❌ Database connection failed: {str(e)}")
            st.markdown("**🔧 Troubleshooting:**")
            st.markdown("""
            - Check if the database server is running
            - Verify the connection parameters (host, port, database name, username, password)
            - Ensure the database exists
            - Check network connectivity
            - Verify user permissions
            """)
    
    # SEPARATE SECTION FOR TABLE CREATION (outside form context)
    if st.session_state.get('tables_need_creation', False):
        st.markdown("---")
        st.markdown("### 🔨 **Table Creation**")
        st.markdown("**💡 You can create all necessary tables now:**")
        
        # Get connection details from session state
        conn_details = st.session_state.get('test_connection_details', {})
        
        if conn_details:
            st.info(f"📋 **Target Database**: {conn_details.get('database_name', 'Unknown')} on {conn_details.get('host', 'Unknown')}:{conn_details.get('port', 'Unknown')}")
            
            # Quick Create Tables button
            if st.button("⚡ Quick Create Tables", type="primary", help="Create all necessary tables", key="quick_create_outside"):
                
                # Create tables using stored connection details
                try:
                    st.write("🔄 **Step 1**: Connecting to database...")
                    
                    # Import SQLAlchemy components locally to ensure they're available
                    from sqlalchemy import create_engine, text
                    from sqlalchemy.orm import sessionmaker
                    
                    # Recreate the test engine
                    test_database_url = conn_details['test_database_url']
                    test_engine = create_engine(test_database_url, echo=False)
                    
                    with test_engine.connect() as conn:
                        st.write("✅ **Step 2**: Connection established!")
                        
                        # Create tables one by one with direct SQL
                        tables = [
                            ("servicenow_modules", """
                                CREATE TABLE IF NOT EXISTS servicenow_modules (
                                    id SERIAL PRIMARY KEY,
                                    name VARCHAR(255) NOT NULL,
                                    description TEXT,
                                    version VARCHAR(50),
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )
                            """),
                            ("servicenow_roles", """
                                CREATE TABLE IF NOT EXISTS servicenow_roles (
                                    id SERIAL PRIMARY KEY,
                                    name VARCHAR(255) NOT NULL,
                                    description TEXT,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )
                            """),
                            ("servicenow_tables", """
                                CREATE TABLE IF NOT EXISTS servicenow_tables (
                                    id SERIAL PRIMARY KEY,
                                    name VARCHAR(255) NOT NULL,
                                    label VARCHAR(255),
                                    description TEXT,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )
                            """),
                            ("servicenow_properties", """
                                CREATE TABLE IF NOT EXISTS servicenow_properties (
                                    id SERIAL PRIMARY KEY,
                                    name VARCHAR(255) NOT NULL,
                                    value TEXT,
                                    description TEXT,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )
                            """),
                            ("servicenow_scheduled_jobs", """
                                CREATE TABLE IF NOT EXISTS servicenow_scheduled_jobs (
                                    id SERIAL PRIMARY KEY,
                                    name VARCHAR(255) NOT NULL,
                                    script TEXT,
                                    schedule VARCHAR(255),
                                    active BOOLEAN DEFAULT TRUE,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )
                            """),
                            ("database_connections", """
                                CREATE TABLE IF NOT EXISTS database_connections (
                                    id SERIAL PRIMARY KEY,
                                    name VARCHAR(255) NOT NULL,
                                    host VARCHAR(255),
                                    port INTEGER,
                                    database_name VARCHAR(255),
                                    username VARCHAR(255),
                                    password VARCHAR(255),
                                    db_type VARCHAR(50),
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )
                            """),
                            ("database_configurations", """
                                CREATE TABLE IF NOT EXISTS database_configurations (
                                    id SERIAL PRIMARY KEY,
                                    name VARCHAR(255) NOT NULL UNIQUE,
                                    host VARCHAR(255) NOT NULL,
                                    port INTEGER NOT NULL,
                                    database_name VARCHAR(255) NOT NULL,
                                    username VARCHAR(255) NOT NULL,
                                    password VARCHAR(255) NOT NULL,
                                    db_type VARCHAR(50) NOT NULL DEFAULT 'postgresql',
                                    connection_pool_size INTEGER DEFAULT 10,
                                    max_overflow INTEGER DEFAULT 20,
                                    echo BOOLEAN DEFAULT FALSE,
                                    is_active BOOLEAN DEFAULT FALSE,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )
                            """),
                            ("servicenow_configurations", """
                                CREATE TABLE IF NOT EXISTS servicenow_configurations (
                                    id SERIAL PRIMARY KEY,
                                    name VARCHAR(255) NOT NULL UNIQUE,
                                    instance_url VARCHAR(500) NOT NULL,
                                    username VARCHAR(255) NOT NULL,
                                    password VARCHAR(255) NOT NULL,
                                    timeout INTEGER DEFAULT 30,
                                    max_requests INTEGER DEFAULT 100,
                                    is_active BOOLEAN DEFAULT FALSE,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )
                            """),
                            ("database_introspection", """
                                CREATE TABLE IF NOT EXISTS database_introspection (
                                    id SERIAL PRIMARY KEY,
                                    table_name VARCHAR(255) NOT NULL,
                                    column_name VARCHAR(255) NOT NULL,
                                    data_type VARCHAR(100),
                                    is_nullable BOOLEAN,
                                    column_default TEXT,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                )
                            """)
                        ]
                        
                        created_count = 0
                        failed_count = 0
                        
                        for i, (table_name, sql) in enumerate(tables, 1):
                            try:
                                st.write(f"**Step {i+2}**: Creating table `{table_name}`...")
                                conn.execute(text(sql))
                                conn.commit()
                                st.write(f"✅ Table `{table_name}` created successfully!")
                                created_count += 1
                            except Exception as e:
                                st.write(f"❌ Failed to create table `{table_name}`: {str(e)}")
                                failed_count += 1
                                
                                # If it's a permission error, rollback and stop
                                if "permission denied" in str(e).lower() or "insufficientprivilege" in str(e).lower():
                                    st.error("🚫 **Permission Denied!**")
                                    st.markdown("**The database user doesn't have CREATE privileges on the public schema.**")
                                    st.markdown("**To fix this, run these commands as a database superuser:**")
                                    
                                    db_name = conn_details.get('database_name', 'your_database')
                                    db_user = conn_details.get('username', 'your_user')
                                    
                                    st.code(f"""
-- Connect as superuser (postgres) and run:
psql -U postgres -d {db_name}

-- Grant privileges to your user:
GRANT CREATE ON SCHEMA public TO {db_user};
GRANT USAGE ON SCHEMA public TO {db_user};
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {db_user};
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {db_user};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO {db_user};
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO {db_user};
                                    """, language="sql")
                                    
                                    st.info("💡 **After granting permissions, try the table creation again.**")
                                    break  # Stop trying to create more tables
                        
                        # Final summary
                        st.markdown("---")
                        st.markdown("### 🎯 **Creation Summary**")
                        st.write(f"✅ **Created**: {created_count} tables")
                        st.write(f"❌ **Failed**: {failed_count} tables")
                        
                        if created_count == len(tables):
                            st.success("🎉 **All tables created successfully!**")
                            st.info("✅ **Safe to save this configuration** - All required tables are now available.")
                            # Clear the session state to hide the table creation section
                            st.session_state.tables_need_creation = False
                        elif created_count > 0:
                            st.warning("⚠️ **Some tables were created successfully.**")
                            st.info("💡 You can save this configuration, but some features may not work until all tables are created.")
                        else:
                            st.error("❌ **No tables were created.**")
                            st.info("💡 Please check database permissions and try again.")
                            
                    test_engine.dispose()
                                    
                except Exception as e:
                    st.error(f"❌ Quick create failed: {str(e)}")
                    st.info("💡 Please check database permissions and try again.")
        
        # Clear button to reset the table creation section
        if st.button("🔄 Clear Table Creation", type="secondary", help="Clear table creation section"):
            st.session_state.tables_need_creation = False
            st.rerun()
    
    # Enhanced save button with validation
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("💾 Save Database Configuration", type="primary", use_container_width=True):
            # Validate configuration name before saving
            if not config_name or not config_name.strip():
                st.error("❌ **Error**: Configuration name is required! Please enter a name for this configuration.")
                st.stop()
            
            if len(config_name.strip()) < 3:
                st.error("❌ **Error**: Configuration name must be at least 3 characters long.")
                st.stop()
            
            # Check if configuration name already exists
            try:
                from database import DatabaseManager
                db_manager = DatabaseManager()
                existing_configs = db_manager.get_all_database_configurations()
                existing_names = [config.name for config in existing_configs]
                
                if config_name.strip() in existing_names and config_name.strip() != 'default':
                    st.warning(f"⚠️ **Warning**: Configuration name '{config_name.strip()}' already exists. This will update the existing configuration.")
                
            except Exception as e:
                st.warning(f"⚠️ Could not check existing configurations: {e}")
            
            try:
                config_manager.save_config()
                
                # Save database configuration to database
                try:
                    from database import DatabaseManager
                    db_manager = DatabaseManager()
                    
                    # Save database configuration to database using form data
                    if host and username:
                        db_config_data = {
                            'name': config_name.strip(),  # Use the validated config name
                            'db_type': db_type,
                            'host': host,
                            'port': port,
                            'database_name': database_name,
                            'username': username,
                            'password': password,
                            'connection_pool_size': connection_pool_size,
                            'max_overflow': max_overflow,
                            'echo': echo
                        }
                        
                        db_manager.save_database_configuration(db_config_data)
                        
                        # Check if this was an update to existing config or new config
                        existing_configs = db_manager.get_all_database_configurations()
                        existing_names = [config.name for config in existing_configs]
                        
                        if config_name.strip() in existing_names:
                            st.success(f"✅ **Configuration '{config_name.strip()}' updated successfully!**")
                            st.info(f"💡 **Next Steps**: Go to the Database page and select '{config_name.strip()}' from the dropdown to switch to this configuration.")
                        else:
                            st.success(f"✅ **New configuration '{config_name.strip()}' saved successfully!**")
                            st.info(f"💡 **Next Steps**: Go to the Database page and select '{config_name.strip()}' from the dropdown to switch to this configuration.")
                    
                    # Reload database configuration if database settings changed
                    if db_manager.reload_configuration():
                        st.success("✅ Database reconnected!")
                    
                except Exception as db_error:
                    st.success("✅ Configuration saved to files!")
                    st.warning(f"⚠️ Database save failed: {str(db_error)}")
                
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to save configuration: {str(e)}")

def show_servicenow_config(config_manager: ConfigurationManager):
    """Show ServiceNow configuration UI"""
    st.subheader("ServiceNow Configuration")
    st.markdown("Configure connection to ServiceNow instances for live data extraction.")
    
    # Helpful information about ServiceNow URLs
    with st.expander("ℹ️ How to find your ServiceNow instance URL"):
        st.markdown("""
        **Common ServiceNow instance URL formats:**
        
        1. **Standard format**: `https://yourcompany.service-now.com`
        2. **Alternative format**: `https://yourcompany.servicenow.com`
        3. **Newer format**: `https://yourcompany.now.com`
        
        **How to find your instance URL:**
        - Check your ServiceNow login page URL
        - Look in your ServiceNow bookmarks
        - Ask your ServiceNow administrator
        - Check your company's ServiceNow documentation
        
        **Example URLs:**
        - `https://acme.service-now.com`
        - `https://mycompany.servicenow.com`
        - `https://enterprise.now.com`
        """)
    
    servicenow_config = config_manager.get_servicenow_config()
    
    col1, col2 = st.columns(2)
    
    with col1:
        instance_url = st.text_input(
            "Instance URL",
            value=servicenow_config.get('instance_url', ''),
            placeholder="https://yourcompany.service-now.com",
            help="ServiceNow instance URL (e.g., https://yourcompany.service-now.com)"
        )
        
        username = st.text_input(
            "Username",
            value=servicenow_config.get('username', ''),
            help="ServiceNow username"
        )
        
        password = st.text_input(
            "Password",
            value=servicenow_config.get('password', ''),
            type="password",
            help="ServiceNow password"
        )
    
    with col2:
        api_version = st.selectbox(
            "API Version",
            ["v1", "v2"],
            index=["v1", "v2"].index(servicenow_config.get('api_version', 'v2'))
        )
        
        timeout = st.number_input(
            "Timeout (seconds)",
            value=servicenow_config.get('timeout', 30),
            min_value=5,
            max_value=300
        )
        
        max_retries = st.number_input(
            "Max Retries",
            value=servicenow_config.get('max_retries', 3),
            min_value=0,
            max_value=10
        )
        
        verify_ssl = st.checkbox(
            "Verify SSL",
            value=servicenow_config.get('verify_ssl', True)
        )
    
    # Test connection button
    if st.button("🔍 Test Connection", type="secondary"):
        if instance_url and username and password:
            # Validate instance URL format
            if not instance_url.startswith(('http://', 'https://')):
                st.error("❌ Instance URL must start with http:// or https://")
            elif not any(domain in instance_url for domain in ['.service-now.com', '.servicenow.com', '.now.com']):
                st.warning("⚠️ Instance URL should contain a valid ServiceNow domain (.service-now.com, .servicenow.com, or .now.com)")
            
            try:
                from servicenow_api_client import ServiceNowAPIClient
                client = ServiceNowAPIClient(instance_url, username, password)
                # Test connection using the proper method
                result = client.test_connection()
                if result.get('success', False):
                    st.success(f"✅ {result.get('message', 'Connection successful')}")
                    if 'response_time' in result:
                        st.info(f"Response time: {result['response_time']:.2f} seconds")
                else:
                    error_msg = result.get('message', 'Connection failed')
                    st.error(f"❌ {error_msg}")
                    
                    # Provide specific troubleshooting based on error type
                    if 'NameResolutionError' in error_msg or 'Failed to resolve' in error_msg:
                        st.markdown("**🔍 Troubleshooting DNS Resolution:**")
                        st.markdown("""
                        - Check if the instance URL is correct
                        - Verify the instance exists and is accessible
                        - Try accessing the instance in your browser first
                        - Common ServiceNow URL formats:
                          - `https://yourcompany.service-now.com`
                          - `https://yourcompany.servicenow.com`
                          - `https://yourcompany.now.com`
                        """)
                    elif 'Authentication failed' in error_msg or 'Unauthorized' in error_msg:
                        st.markdown("**🔐 Troubleshooting Authentication:**")
                        st.markdown("""
                        - Verify your username and password are correct
                        - Check if your account is active
                        - Ensure you have the necessary permissions
                        - Try logging into the ServiceNow instance in your browser
                        """)
                    elif 'Connection error' in error_msg:
                        st.markdown("**🌐 Troubleshooting Network:**")
                        st.markdown("""
                        - Check your internet connection
                        - Verify firewall settings
                        - Try accessing the instance from your browser
                        - Contact your IT department if behind a corporate firewall
                        """)
            except Exception as e:
                st.error(f"❌ Connection failed: {str(e)}")
                st.markdown("**🔧 General Troubleshooting:**")
                st.markdown("""
                - Verify all fields are filled correctly
                - Check your internet connection
                - Try accessing the ServiceNow instance in your browser
                - Contact your ServiceNow administrator if issues persist
                """)
        else:
            st.warning("⚠️ Please fill in all required fields")
    
    # Save ServiceNow Configuration button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("💾 Save ServiceNow Configuration", type="primary", use_container_width=True):
            if not instance_url or not username or not password:
                st.error("❌ Please fill in all required fields (Instance URL, Username, Password)")
            else:
                try:
                    # Update configuration
                    config_manager.update_servicenow_config(
                        instance_url=instance_url,
                        username=username,
                        password=password,
                        api_version=api_version,
                        timeout=timeout,
                        max_retries=max_retries,
                        verify_ssl=verify_ssl
                    )
                    
                    # Save to database
                    from database import DatabaseManager
                    db_manager = DatabaseManager()
                    db_manager.save_servicenow_configuration({
                        'name': 'default',
                        'instance_url': instance_url,
                        'username': username,
                        'password': password,
                        'api_version': api_version,
                        'timeout': timeout,
                        'max_retries': max_retries,
                        'verify_ssl': verify_ssl
                    })
                    
                    st.success("✅ ServiceNow configuration saved successfully!")
                    st.info("💡 This configuration will be automatically loaded in the ServiceNow Instance Introspection page.")
                    
                except Exception as e:
                    st.error(f"❌ Failed to save ServiceNow configuration: {str(e)}")

def show_security_config(config_manager: ConfigurationManager):
    """Show security configuration UI"""
    st.subheader("Security Configuration")
    
    security_config = config_manager.config.get('security', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        api_key_required = st.checkbox(
            "Require API Key",
            value=security_config.get('api_key_required', False),
            help="Require API key for external access"
        )
        
        rate_limit_enabled = st.checkbox(
            "Enable Rate Limiting",
            value=security_config.get('rate_limit_enabled', True),
            help="Enable rate limiting for API requests"
        )
        
        enable_ssl = st.checkbox(
            "Enable SSL",
            value=security_config.get('enable_ssl', True),
            help="Enable SSL/TLS encryption"
        )
    
    with col2:
        max_requests_per_minute = st.number_input(
            "Max Requests per Minute",
            value=security_config.get('max_requests_per_minute', 60),
            min_value=1,
            max_value=1000
        )
        
        allowed_hosts = st.text_area(
            "Allowed Hosts",
            value='\n'.join(security_config.get('allowed_hosts', ['localhost', '127.0.0.1'])),
            help="One host per line"
        )
    
    # Save Security Configuration button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("💾 Save Security Configuration", type="primary", use_container_width=True):
            try:
                # Update configuration
                config_manager.config['security'] = {
                    'api_key_required': api_key_required,
                    'rate_limit_enabled': rate_limit_enabled,
                    'enable_ssl': enable_ssl,
                    'max_requests_per_minute': max_requests_per_minute,
                    'allowed_hosts': [host.strip() for host in allowed_hosts.split('\n') if host.strip()]
                }
                
                # Save to config file
                config_manager.save_config()
                
                st.success("✅ Security configuration saved successfully!")
                st.info("💡 Security settings have been updated and will take effect on next restart.")
                
            except Exception as e:
                st.error(f"❌ Failed to save security configuration: {str(e)}")

def show_general_config(config_manager: ConfigurationManager):
    """Show general configuration UI"""
    st.subheader("General Configuration")
    
    # Scraper configuration
    st.markdown("#### 🕷️ Scraper Settings")
    scraper_config = config_manager.config.get('scraper', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        base_url = st.text_input(
            "Base URL",
            value=scraper_config.get('base_url', 'https://www.servicenow.com/docs'),
            help="Base URL for scraping"
        )
        
        timeout_seconds = st.number_input(
            "Timeout (seconds)",
            value=scraper_config.get('timeout_seconds', 60),
            min_value=1,
            max_value=300
        )
        
        max_concurrent_requests = st.number_input(
            "Max Concurrent Requests",
            value=scraper_config.get('max_concurrent_requests', 5),
            min_value=1,
            max_value=20
        )
    
    with col2:
        max_pages = st.number_input(
            "Max Pages",
            value=scraper_config.get('max_pages', 100),
            min_value=1,
            max_value=10000
        )
        
        delay_seconds = st.number_input(
            "Delay (seconds)",
            value=float(scraper_config.get('delay_seconds', 1.0)),
            min_value=0.1,
            max_value=10.0,
            step=0.1
        )
        
        use_selenium = st.checkbox(
            "Use Selenium",
            value=scraper_config.get('use_selenium', False),
            help="Use Selenium for JavaScript-heavy pages"
        )
    
    # Update scraper configuration
    config_manager.config['scraper'] = {
        'base_url': base_url,
        'timeout_seconds': timeout_seconds,
        'max_concurrent_requests': max_concurrent_requests,
        'max_pages': max_pages,
        'delay_seconds': delay_seconds,
        'use_selenium': use_selenium,
        'discover_links': scraper_config.get('discover_links', True),
        'user_agent': scraper_config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
        'chrome_options': scraper_config.get('chrome_options', [
            '--headless',
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--window-size=1920,1080'
        ])
    }
    
    # Logging configuration
    st.markdown("#### 📝 Logging Settings")
    logging_config = config_manager.config.get('logging', {})
    
    col1, col2 = st.columns(2)
    
    with col1:
        log_level = st.selectbox(
            "Log Level",
            ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            index=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"].index(logging_config.get('level', 'INFO'))
        )
        
        console_output = st.checkbox(
            "Console Output",
            value=logging_config.get('console_output', True)
        )
    
    with col2:
        max_file_size = st.number_input(
            "Max File Size (bytes)",
            value=logging_config.get('max_file_size', 10485760),
            min_value=1024,
            max_value=104857600
        )
        
        backup_count = st.number_input(
            "Backup Count",
            value=logging_config.get('backup_count', 5),
            min_value=1,
            max_value=20
        )
    
    # Save General Configuration button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("💾 Save General Configuration", type="primary", use_container_width=True):
            try:
                # Update scraper configuration
                config_manager.config['scraper'] = {
                    'base_url': base_url,
                    'timeout_seconds': timeout_seconds,
                    'max_concurrent_requests': max_concurrent_requests,
                    'max_pages': max_pages,
                    'delay_seconds': delay_seconds,
                    'use_selenium': use_selenium,
                    'discover_links': scraper_config.get('discover_links', True),
                    'user_agent': scraper_config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
                    'chrome_options': scraper_config.get('chrome_options', [
                        '--headless',
                        '--no-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--window-size=1920,1080'
                    ])
                }
                
                # Update logging configuration
                config_manager.config['logging'] = {
                    'level': log_level,
                    'format': logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
                    'file_path': logging_config.get('file_path', 'logs/servicenow_docs.log'),
                    'max_file_size': max_file_size,
                    'backup_count': backup_count,
                    'console_output': console_output
                }
                
                # Save to config file
                config_manager.save_config()
                
                st.success("✅ General configuration saved successfully!")
                st.info("💡 Scraper and logging settings have been updated and will take effect on next restart.")
                
            except Exception as e:
                st.error(f"❌ Failed to save general configuration: {str(e)}")

if __name__ == "__main__":
    show_configuration_ui()
