"""
ServiceNow Advanced Visual Documentation
Clean application focused on comprehensive ServiceNow data scraping and visualization
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import json
import time
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from models import ServiceNowDocumentation, ServiceNowTable, ModuleType, TableType, RelationshipType
from data_loader import load_servicenow_data
from visualization import ServiceNowVisualizer, create_annotation_popup
from database import DatabaseManager, DatabaseIntrospector, initialize_database
from comprehensive_scraper_ui import ComprehensiveScraperUI
from interactive_visualizer import InteractiveServiceNowVisualizer
from database_introspection_ui import DatabaseIntrospectionUI
from servicenow_instance_introspection_ui import ServiceNowInstanceIntrospectionUI
from configuration_ui import show_configuration_ui

# Page configuration
st.set_page_config(
    page_title="ServiceNow Advanced Visual Documentation",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeaa7;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #f8f9fa;
        border-top: 1px solid #dee2e6;
        padding: 10px 20px;
        text-align: center;
        font-size: 0.9rem;
        color: #6c757d;
        z-index: 1000;
    }
    .footer a {
        color: #007bff;
        text-decoration: none;
    }
    .footer a:hover {
        text-decoration: underline;
    }
    .main-content {
        margin-bottom: 60px;
    }
</style>
""", unsafe_allow_html=True)

def show_footer():
    """Show footer with creator information"""
    st.markdown("""
    <div class="footer">
        Created By: <strong>Ashish Gautam</strong> | 
        <a href="https://www.linkedin.com/in/ashishgautamkarn/" target="_blank">LinkedIn Profile</a>
    </div>
    """, unsafe_allow_html=True)

def show_dashboard():
    """Show the main dashboard"""
    st.markdown('<h1 class="main-header">🚀 ServiceNow Advanced Visual Documentation</h1>', unsafe_allow_html=True)
    
    # Show current page status
    st.success(f"📍 Currently viewing: Dashboard")
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    # Get database statistics
    try:
        session = db_manager.get_session()
        try:
            # Test basic connection first
            from sqlalchemy import text
            session.execute(text("SELECT 1"))
            
            # If basic connection works, try to get statistics
            try:
                from database import ServiceNowModule, ServiceNowRole, ServiceNowTable, ServiceNowProperty, ServiceNowScheduledJob
                
                module_count = session.query(ServiceNowModule).count()
                role_count = session.query(ServiceNowRole).count()
                table_count = session.query(ServiceNowTable).count()
                property_count = session.query(ServiceNowProperty).count()
                job_count = session.query(ServiceNowScheduledJob).count()
                
                # Display metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("📦 Modules", module_count)
                with col2:
                    st.metric("👥 Roles", role_count)
                with col3:
                    st.metric("📊 Tables", table_count)
                with col4:
                    st.metric("⚙️ Properties", property_count)
                with col5:
                    st.metric("⏰ Scheduled Jobs", job_count)
                    
            except Exception as table_error:
                # Tables don't exist yet
                st.info("ℹ️ Database connected but tables not created yet. Go to Database page to create tables.")
                
                # Show empty metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("📦 Modules", 0)
                with col2:
                    st.metric("👥 Roles", 0)
                with col3:
                    st.metric("📊 Tables", 0)
                with col4:
                    st.metric("⚙️ Properties", 0)
                with col5:
                    st.metric("⏰ Scheduled Jobs", 0)
            
        finally:
            session.close()
            
    except Exception as e:
        st.warning(f"Could not retrieve database statistics: {e}")
        st.info("💡 Go to Database page to configure database connection and create tables.")
    
    # Quick actions
    st.markdown('<h2 class="section-header">🎯 Quick Actions</h2>', unsafe_allow_html=True)
    st.info("💡 Click any button below to navigate to that section of the application.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🕷️ Run Comprehensive Scraper", use_container_width=True, type="primary"):
            st.session_state.current_page = "comprehensive_scraper"
            st.rerun()
    
    with col2:
        if st.button("📊 View Database", use_container_width=True):
            st.session_state.current_page = "database"
            st.rerun()
    
    with col3:
        if st.button("📈 Visualizations", use_container_width=True):
            st.session_state.current_page = "visualizations"
            st.rerun()
    
    # Additional quick actions
    st.markdown('<h3 class="section-header">🔧 Advanced Tools</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Database Introspection", use_container_width=True):
            st.session_state.current_page = "introspection"
            st.rerun()
    
    with col2:
        if st.button("🌐 ServiceNow Instance", use_container_width=True):
            st.session_state.current_page = "servicenow_instance"
            st.rerun()
    
    with col3:
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            st.session_state.current_page = "dashboard"
            st.rerun()
    
    # Recent activity
    st.markdown('<h2 class="section-header">📋 Recent Activity</h2>', unsafe_allow_html=True)
    
    try:
        # Get recent items
        recent_roles = db_manager.get_recent_roles(5)
        recent_tables = db_manager.get_recent_tables(5)
        recent_properties = db_manager.get_recent_properties(5)
        
        if recent_roles or recent_tables or recent_properties:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if recent_roles:
                    st.markdown("**Recent Roles:**")
                    for role in recent_roles:
                        st.text(f"• {role['name']} ({role['module']})")
            
            with col2:
                if recent_tables:
                    st.markdown("**Recent Tables:**")
                    for table in recent_tables:
                        st.text(f"• {table['name']} ({table['module']})")
            
            with col3:
                if recent_properties:
                    st.markdown("**Recent Properties:**")
                    for prop in recent_properties:
                        st.text(f"• {prop['name']} ({prop['module']})")
        else:
            st.info("No recent activity found. Run the comprehensive scraper to populate the database.")
            
    except Exception as e:
        st.warning(f"Could not retrieve recent activity: {e}")
    
    # Show footer
    show_footer()

def show_comprehensive_scraper():
    """Show the comprehensive scraper interface"""
    scraper_ui = ComprehensiveScraperUI()
    scraper_ui.show_main_interface()
    # Show footer
    show_footer()

def _load_database_configuration(db_manager: DatabaseManager) -> Dict[str, Any]:
    """Load database configuration - prioritize current active connection, then fall back to saved configs"""
    try:
        # First, try to get the current active connection from DatabaseManager
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
        db_config = current_db_manager.get_database_configuration('default')
        if db_config:
            config_dict = db_config.to_dict()
            config_dict['_source'] = 'saved_config'
            return config_dict
    except Exception as e:
        # Fall back to environment variables if database loading fails
        pass
    
    # Fall back to environment variables
    try:
        # Get configuration from environment variables
        import os
        env_config = {
            'db_type': os.getenv('DB_TYPE', 'postgresql'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', '5432')),
            'database_name': os.getenv('DB_NAME', 'servicenow_docs'),
            'username': os.getenv('DB_USER', 'servicenow_user'),
            'password': os.getenv('DB_PASSWORD', ''),
            'connection_pool_size': int(os.getenv('DB_CONNECTION_POOL_SIZE', '10')),
            'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '20')),
            'echo': os.getenv('DB_ECHO', 'false').lower() == 'true',
            '_source': 'environment'
        }
        return env_config
    except Exception as e:
        st.warning(f"⚠️ Could not load from environment variables: {str(e)}")
    
    # Return default config if nothing found
    return {
        'db_type': 'postgresql',
        'host': 'localhost',
        'port': 5432,
        'database_name': 'servicenow_docs',
        'username': 'servicenow_user',
        'password': '',
        'connection_pool_size': 10,
        'max_overflow': 20,
        'echo': False,
        '_source': 'default'
    }

def show_database_view():
    """Show database view and management"""
    st.markdown('<h2 class="section-header">🗄️ Database Management</h2>', unsafe_allow_html=True)
    
    # Create database manager and force reload configuration to ensure latest settings
    db_manager = DatabaseManager()
    
    # If we have a switched database URL in session state, validate and update the DatabaseManager
    if 'current_database_url' in st.session_state and st.session_state.current_database_url:
        try:
            from sqlalchemy import create_engine, text
            from sqlalchemy.orm import sessionmaker
            
            # Test the connection first to make sure it's still valid
            temp_engine = create_engine(st.session_state.current_database_url, echo=False)
            with temp_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            # If connection test passes, update DatabaseManager with the switched connection
            db_manager.database_url = st.session_state.current_database_url
            db_manager.engine = create_engine(st.session_state.current_database_url, echo=False)
            db_manager.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_manager.engine)
        except Exception as e:
            st.warning(f"⚠️ Could not restore switched database connection: {e}")
            st.info("💡 The previously switched database may no longer be available. Using default connection.")
            # Clear the session state if there's an error
            st.session_state.current_database_url = None
    
    # Get current database connection details from DatabaseManager
    def get_current_db_connection_details():
        """Get current database connection details from DatabaseManager"""
        try:
            # Get fresh DatabaseManager instance to ensure we have the latest connection
            current_db_manager = DatabaseManager()
            database_url = current_db_manager.database_url
            
            if database_url and database_url.startswith('postgresql://'):
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
            elif database_url and database_url.startswith('mysql'):
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
            elif database_url and database_url.startswith('sqlite'):
                # Parse SQLite URL: sqlite:///path/to/database
                return {
                    'host': 'localhost',
                    'port': 0,
                    'database_name': database_url.replace('sqlite:///', ''),
                    'username': '',
                    'db_type': 'sqlite',
                    'password': '',
                    '_source': 'current_connection'
                }
            
            # Fallback to environment variables if parsing fails
            return {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', '5432')),
                'database_name': os.getenv('DB_NAME', 'servicenow_docs'),
                'username': os.getenv('DB_USER', 'servicenow_user'),
                'db_type': os.getenv('DB_TYPE', 'postgresql'),
                'password': os.getenv('DB_PASSWORD', ''),
                '_source': 'environment'
            }
        except Exception as e:
            st.warning(f"⚠️ Could not parse current database connection: {e}")
            return {
                'host': 'Unknown',
                'port': 0,
                'database_name': 'Unknown',
                'username': 'Unknown',
                'db_type': 'Unknown',
                'password': '',
                '_source': 'unknown'
            }
    
    # Show database configurations selector (including current active connection)
    try:
        saved_configs = db_manager.get_all_database_configurations()
        
        # Get current active connection details
        current_db_config = get_current_db_connection_details()
        
        # Create options list with current active connection first
        config_options = []
        config_options.append("🔄 Current Active Connection")
        
        if saved_configs:
            config_names = [config.name for config in saved_configs]
            config_options.extend(config_names)
        
        st.markdown("### 🔧 Database Configuration Selector")
        
        col_selector, col_switch = st.columns([3, 1])
        
        with col_selector:
            # Determine default selection
            default_index = 0  # Default to "Current Active Connection"
            if 'active_db_config' in st.session_state and st.session_state.active_db_config:
                # If there's an active config, try to find it in the list
                try:
                    active_config_index = config_options.index(st.session_state.active_db_config)
                    default_index = active_config_index
                except ValueError:
                    default_index = 0  # Fall back to current active connection
            
            selected_config_name = st.selectbox(
                "Select Database Configuration:",
                config_options,
                index=default_index,
                help="Choose which database configuration to use",
                key="db_config_selector"
            )
            
            # Show selected configuration details
            if selected_config_name:
                if selected_config_name == "🔄 Current Active Connection":
                    # Show current active connection details
                    st.info(f"**Selected**: Current Active Connection")
                    st.info(f"**Host**: {current_db_config.get('host', 'Unknown')}:{current_db_config.get('port', 'Unknown')}")
                    st.info(f"**Database**: {current_db_config.get('database_name', 'Unknown')}")
                    st.info(f"**Username**: {current_db_config.get('username', 'Unknown')}")
                    st.info(f"**Type**: {current_db_config.get('db_type', 'Unknown')}")
                else:
                    # Show selected saved configuration details
                    selected_config = next((config for config in saved_configs if config.name == selected_config_name), None)
                    if selected_config:
                        st.info(f"**Selected**: {selected_config.name}")
                        st.info(f"**Host**: {selected_config.host}:{selected_config.port}")
                        st.info(f"**Database**: {selected_config.database_name}")
                        st.info(f"**Username**: {selected_config.username}")
                        st.info(f"**Type**: {selected_config.db_type}")
            
            with col_switch:
                if st.button("🔄 Switch Configuration", type="primary", help="Switch to selected database configuration"):
                    try:
                        if selected_config_name == "🔄 Current Active Connection":
                            # Already using current active connection, no need to switch
                            st.info("ℹ️ Already using current active connection. No switch needed.")
                        else:
                            # Load selected configuration
                            selected_config = next((config for config in saved_configs if config.name == selected_config_name), None)
                            if selected_config:
                                # Test connection first
                                st.info(f"🔄 Testing connection to '{selected_config_name}'...")
                                
                                # Update DatabaseManager to use selected configuration
                                if selected_config.db_type == 'postgresql':
                                    new_database_url = f"postgresql://{selected_config.username}:{selected_config.password}@{selected_config.host}:{selected_config.port}/{selected_config.database_name}"
                                elif selected_config.db_type == 'mysql':
                                    new_database_url = f"mysql+pymysql://{selected_config.username}:{selected_config.password}@{selected_config.host}:{selected_config.port}/{selected_config.database_name}"
                                elif selected_config.db_type == 'sqlite':
                                    new_database_url = f"sqlite:///{selected_config.database_name}"
                                else:
                                    new_database_url = f"{selected_config.db_type}://{selected_config.username}:{selected_config.password}@{selected_config.host}:{selected_config.port}/{selected_config.database_name}"
                                
                                # Test connection with temporary engine
                                from sqlalchemy import create_engine, text
                                temp_engine = create_engine(new_database_url, echo=False)
                                
                                try:
                                    with temp_engine.connect() as conn:
                                        conn.execute(text("SELECT 1"))
                                    st.success("✅ Connection test successful!")
                                    
                                    # Update DatabaseManager to use selected configuration
                                    from sqlalchemy.orm import sessionmaker
                                    db_manager.database_url = new_database_url
                                    db_manager.engine = create_engine(new_database_url, echo=selected_config.echo)
                                    db_manager.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_manager.engine)
                                    
                                    # Store the new connection details in session state for persistence
                                    st.session_state.current_database_url = new_database_url
                                    
                                    # Create tables in new database
                                    st.info("🔄 Creating tables in new database...")
                                    try:
                                        db_manager.create_tables()
                                        st.success(f"✅ Successfully switched to '{selected_config_name}' configuration!")
                                        st.success("✅ All necessary tables created in new database!")
                                        st.info(f"💡 **New Connection**: {selected_config.host}:{selected_config.port}/{selected_config.database_name}")
                                        
                                        # Update session state to reflect the new active configuration
                                        st.session_state.active_db_config = selected_config_name
                                        st.session_state.db_switch_success = True
                                        
                                        # Force refresh the page to show updated connection details
                                        st.rerun()
                                        
                                    except Exception as table_error:
                                        st.warning(f"⚠️ Switched to '{selected_config_name}' but could not create tables: {str(table_error)}")
                                        st.info("💡 You may need to create tables manually or check database permissions.")
                                        
                                        # Still update session state even if table creation failed
                                        st.session_state.active_db_config = selected_config_name
                                        st.session_state.db_switch_success = True
                                        
                                        # Force refresh the page to show updated connection details
                                        st.rerun()
                                
                                except Exception as conn_error:
                                    st.error(f"❌ Connection test failed: {str(conn_error)}")
                                    st.info("💡 Please check your database credentials and network connectivity.")
                            else:
                                st.error("❌ Selected configuration not found!")
                    except Exception as e:
                        st.error(f"❌ Failed to switch configuration: {str(e)}")
            
            st.markdown("---")
    except Exception as e:
        st.warning(f"⚠️ Could not load saved configurations: {e}")
    
    # Force reload configuration from database to get latest settings
    db_manager.reload_configuration()
    
    # Get current database connection details AFTER reloading configuration
    # This ensures we get the actual current active connection after any switches
    current_db_config = get_current_db_connection_details()
    
    # Database Configuration Section
    st.markdown("### ⚙️ Current Database Configuration")
    
    # Show configuration status
    col_status, col_refresh = st.columns([3, 1])
    # Show configuration status
    col_status, col_refresh = st.columns([3, 1])
    
    with col_status:
        # Always show current active connection details (real-time from DatabaseManager)
        config_source = current_db_config.get('_source', 'current_connection')
        if config_source == 'current_connection':
            st.success("✅ **Current Active Connection**")
        elif config_source == 'environment':
            st.info("ℹ️ Using database configuration from environment variables")
        else:
            st.warning("⚠️ Using default database configuration")
        
        st.info(f"**Host**: {current_db_config.get('host', 'Not configured')}")
        st.info(f"**Database**: {current_db_config.get('database_name', 'Not configured')}")
        st.info(f"**Username**: {current_db_config.get('username', 'Not configured')}")
        st.info(f"**Type**: {current_db_config.get('db_type', 'Not configured')}")
        
        # Show active configuration name if available
        if 'active_db_config' in st.session_state and st.session_state.active_db_config:
            st.caption(f"📋 Active Configuration: {st.session_state.active_db_config}")
        else:
            # Check if a configuration is selected from dropdown (preview mode)
            if 'db_config_selector' in st.session_state and st.session_state.db_config_selector:
                try:
                    saved_configs = db_manager.get_all_database_configurations()
                    selected_config = next((config for config in saved_configs if config.name == st.session_state.db_config_selector), None)
                    if selected_config:
                        st.caption(f"📋 Preview: {selected_config.name} configuration (not yet active)")
                        st.caption(f"Host: {selected_config.host}:{selected_config.port}")
                        st.caption(f"Database: {selected_config.database_name}")
                        st.caption(f"Username: {selected_config.username}")
                        st.caption(f"Type: {selected_config.db_type}")
                        st.warning("⚠️ **Note**: This is a preview. Click 'Switch Configuration' to make it active.")
                    else:
                        st.caption("📋 No preview available")
                except Exception as e:
                    st.caption(f"📋 Preview error: {str(e)}")
            else:
                st.caption("📋 No configuration selected for preview")
            
            # Show switch success message if applicable
            if st.session_state.get('db_switch_success'):
                st.success("✅ Database configuration switched successfully!")
                # Clear the success flag
                st.session_state.db_switch_success = False
    
    with col_refresh:
        if st.button("🔄 Refresh Configuration", type="secondary", help="Reload configuration from Configuration page"):
            # Force reload configuration from database to get latest settings
            db_manager.reload_configuration()
            st.success("✅ Database configuration refreshed!")
            st.rerun()
    
    # Get database configuration
    try:
        config_info = db_manager.get_database_info()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Connection Details:**")
            st.text(f"Database Type: {current_db_config.get('db_type', 'Unknown')}")
            st.text(f"Host: {current_db_config.get('host', 'Unknown')}")
            st.text(f"Port: {current_db_config.get('port', 'Unknown')}")
            st.text(f"Database Name: {current_db_config.get('database_name', 'Unknown')}")
            st.text(f"Username: {current_db_config.get('username', 'Unknown')}")
            st.text(f"Password: {'*' * len(current_db_config.get('password', '')) if current_db_config.get('password') else 'Not set'}")
            
            # Show full URL in expander
            with st.expander("🔗 Full Connection URL"):
                # Build connection URL from loaded configuration
                db_type = current_db_config.get('db_type', 'postgresql')
                host = current_db_config.get('host', 'localhost')
                port = current_db_config.get('port', 5432)
                database_name = current_db_config.get('database_name', 'servicenow_docs')
                username = current_db_config.get('username', 'servicenow_user')
                password = current_db_config.get('password', '')
                
                if db_type == 'postgresql':
                    full_url = f"postgresql://{username}:{password}@{host}:{port}/{database_name}"
                elif db_type == 'mysql':
                    full_url = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database_name}"
                elif db_type == 'sqlite':
                    full_url = f"sqlite:///{database_name}"
                else:
                    full_url = f"{db_type}://{username}:{password}@{host}:{port}/{database_name}"
                
                st.code(full_url, language='text')
        
        with col2:
            st.markdown("**Connection Status:**")
            # Test actual database connection using the loaded configuration
            try:
                # Test connection with current database manager
                from sqlalchemy import text
                session = db_manager.get_session()
                session.execute(text("SELECT 1"))
                session.close()
                st.success("✅ Connected")
                connected = True
            except Exception as e:
                st.error("❌ Not Connected")
                st.caption(f"Error: {str(e)}")
                connected = False
            
            st.markdown("**Database Info:**")
            # Get database statistics
            try:
                stats = db_manager.get_database_statistics()
                st.text(f"Tables Created: {'Yes' if stats.get('modules', 0) > 0 else 'No'}")
                st.text(f"Last Updated: {stats.get('last_updated', 'Unknown')}")
            except Exception as e:
                st.text(f"Tables Created: Unknown")
                st.text(f"Last Updated: Unknown")
                st.caption(f"Stats error: {str(e)}")
            
            # Show connection pool info from loaded configuration
            st.markdown("**Connection Pool:**")
            st.text(f"Pool Size: {current_db_config.get('connection_pool_size', 'Unknown')}")
            st.text(f"Max Overflow: {current_db_config.get('max_overflow', 'Unknown')}")
            st.text(f"Echo SQL: {'Yes' if current_db_config.get('echo', False) else 'No'}")
            
            # Show detailed statistics if available
            try:
                stats = db_manager.get_database_statistics()
                if stats:
                    st.markdown("### 📊 Detailed Database Statistics")
                    col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Total Modules", stats.get('modules', 0))
                    st.metric("Active Modules", stats.get('active_modules', 0))
                
                with col2:
                    st.metric("Total Roles", stats.get('roles', 0))
                    st.metric("Active Roles", stats.get('active_roles', 0))
                
                with col3:
                    st.metric("Total Tables", stats.get('tables', 0))
                    st.metric("Active Tables", stats.get('active_tables', 0))
                
                with col4:
                    st.metric("Total Properties", stats.get('properties', 0))
                    st.metric("Active Properties", stats.get('active_properties', 0))
                
                with col5:
                    st.metric("Total Jobs", stats.get('scheduled_jobs', 0))
                    st.metric("Active Jobs", stats.get('active_scheduled_jobs', 0))
            except Exception as e:
                st.caption(f"Statistics error: {str(e)}")
            
            # Test connection button
            if st.button("🔄 Test Connection", use_container_width=True):
                try:
                    from sqlalchemy import text
                    session = db_manager.get_session()
                    session.execute(text("SELECT 1"))
                    session.close()
                    st.success("✅ Connection test successful!")
                except Exception as e:
                    st.error(f"❌ Connection test failed: {e}")
    
    except Exception as e:
        st.error(f"Error retrieving database configuration: {e}")
    
    # Database Management Actions
    st.markdown("### 🔧 Database Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🗃️ Create Tables", use_container_width=True):
            try:
                db_manager.create_tables()
                st.success("✅ Database tables created successfully!")
            except Exception as e:
                st.error(f"❌ Error creating tables: {e}")
    
    with col2:
        if st.button("📊 Get Statistics", use_container_width=True):
            try:
                stats = db_manager.get_database_statistics()
                st.success(f"✅ Statistics retrieved: {stats}")
            except Exception as e:
                st.error(f"❌ Error getting statistics: {e}")
    
    with col3:
        if st.button("🧹 Clear All Data", use_container_width=True, type="secondary"):
            if st.session_state.get('confirm_clear', False):
                try:
                    # Clear all data
                    from database import ServiceNowModule, ServiceNowRole, ServiceNowTable, ServiceNowProperty, ServiceNowScheduledJob
                    session = db_manager.get_session()
                    session.query(ServiceNowScheduledJob).delete()
                    session.query(ServiceNowProperty).delete()
                    session.query(ServiceNowTable).delete()
                    session.query(ServiceNowRole).delete()
                    session.query(ServiceNowModule).delete()
                    session.commit()
                    session.close()
                    st.success("✅ All data cleared successfully!")
                    st.session_state.confirm_clear = False
                except Exception as e:
                    st.error(f"❌ Error clearing data: {e}")
            else:
                st.session_state.confirm_clear = True
                st.warning("⚠️ Click again to confirm clearing all data!")
    
    st.markdown("---")
    
    # Database statistics
    try:
        session = db_manager.get_session()
        try:
            # Test basic connection first
            from sqlalchemy import text
            session.execute(text("SELECT 1"))
            
            # If basic connection works, try to get statistics
            try:
                from database import ServiceNowModule, ServiceNowRole, ServiceNowTable, ServiceNowProperty, ServiceNowScheduledJob
                
                # Get counts
                module_count = session.query(ServiceNowModule).count()
                role_count = session.query(ServiceNowRole).count()
                table_count = session.query(ServiceNowTable).count()
                property_count = session.query(ServiceNowProperty).count()
                job_count = session.query(ServiceNowScheduledJob).count()
                
                # Display statistics
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Modules", module_count)
                with col2:
                    st.metric("Roles", role_count)
                with col3:
                    st.metric("Tables", table_count)
                with col4:
                    st.metric("Properties", property_count)
                with col5:
                    st.metric("Scheduled Jobs", job_count)
                    
            except Exception as table_error:
                # Tables don't exist yet
                st.info("ℹ️ Database connected but tables not created yet.")
                
                # Show empty statistics
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Modules", 0)
                with col2:
                    st.metric("Roles", 0)
                with col3:
                    st.metric("Tables", 0)
                with col4:
                    st.metric("Properties", 0)
                with col5:
                    st.metric("Scheduled Jobs", 0)
            
            # Data tables (only show if tables exist)
            st.markdown("### 📊 Data Tables")
            
            try:
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["Modules", "Roles", "Tables", "Properties", "Scheduled Jobs"])
            
                with tab1:
                    modules = session.query(ServiceNowModule).all()
                    if modules:
                        module_data = []
                        for module in modules:
                            module_data.append({
                                'Name': module.name,
                                'Label': module.label,
                                'Description': module.description or '',
                                'Type': module.module_type or '',
                                'Created': module.created_at.strftime('%Y-%m-%d %H:%M') if module.created_at else '',
                                'Active': module.is_active
                            })
                        df = pd.DataFrame(module_data)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No modules found.")
            
                with tab2:
                    roles = session.query(ServiceNowRole).all()
                    if roles:
                        role_data = []
                        for role in roles:
                            role_data.append({
                                'Name': role.name,
                                'Description': role.description or '',
                                'Created': role.created_at.strftime('%Y-%m-%d %H:%M') if role.created_at else '',
                                'Active': role.is_active
                            })
                        df = pd.DataFrame(role_data)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No roles found.")
                
                with tab3:
                    tables = session.query(ServiceNowTable).all()
                    if tables:
                        table_data = []
                        for table in tables:
                            table_data.append({
                                'Name': table.name,
                                'Label': table.label,
                                'Description': table.description or '',
                                'Type': table.table_type or '',
                                'Created': table.created_at.strftime('%Y-%m-%d %H:%M') if table.created_at else '',
                                'Active': table.is_active
                            })
                        df = pd.DataFrame(table_data)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No tables found.")
                
                with tab4:
                    properties = session.query(ServiceNowProperty).all()
                    if properties:
                        property_data = []
                        for prop in properties:
                            property_data.append({
                                'Name': prop.name,
                                'Description': prop.description or '',
                                'Type': prop.property_type or '',
                                'Current Value': prop.current_value or '',
                                'Created': prop.created_at.strftime('%Y-%m-%d %H:%M') if prop.created_at else '',
                                'Active': prop.is_active
                            })
                        df = pd.DataFrame(property_data)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No properties found.")
                
                with tab5:
                    jobs = session.query(ServiceNowScheduledJob).all()
                    if jobs:
                        job_data = []
                        for job in jobs:
                            job_data.append({
                                'Name': job.name,
                                'Description': job.description or '',
                                'Module': job.module.name if job.module else '',
                                'Frequency': job.frequency or '',
                                'Created': job.created_at.strftime('%Y-%m-%d %H:%M') if job.created_at else '',
                                'Active': job.is_active
                            })
                        df = pd.DataFrame(job_data)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.info("No scheduled jobs found.")
                    
            except Exception as table_error:
                # Tables don't exist yet
                st.info("ℹ️ Database connected but tables not created yet.")
                
                # Show empty statistics
                col1, col2, col3, col4, col5 = st.columns(5)
                
                with col1:
                    st.metric("Modules", 0)
                with col2:
                    st.metric("Roles", 0)
                with col3:
                    st.metric("Tables", 0)
                with col4:
                    st.metric("Properties", 0)
                with col5:
                    st.metric("Scheduled Jobs", 0)
            
        finally:
            session.close()
            
    except Exception as e:
        st.error(f"Error accessing database: {e}")
    
    # Show footer
    show_footer()

def show_visualizations():
    """Show enhanced interactive visualizations"""
    st.markdown('<h2 class="section-header">📈 Interactive ServiceNow Visualizations</h2>', unsafe_allow_html=True)
    
    db_manager = DatabaseManager()
    
    # Initialize interactive visualizer
    visualizer = InteractiveServiceNowVisualizer(db_manager)
    
    # Show interactive visualizations
    visualizer.show_interactive_visualizations()
    
    # Show footer
    show_footer()

def show_introspection():
    """Show database introspection interface"""
    introspection_ui = DatabaseIntrospectionUI()
    introspection_ui.show_introspection_interface()
    # Show footer
    show_footer()

def show_servicenow_instance():
    """Show ServiceNow instance introspection interface"""
    instance_introspection_ui = ServiceNowInstanceIntrospectionUI()
    instance_introspection_ui.show_introspection_interface()
    # Show footer
    show_footer()

def main():
    """Main application function"""
    
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("## 🎛️ Navigation")
        
        # Main navigation
        navigation_options = ["🏠 Dashboard", "🕷️ Comprehensive Scraper", "🗄️ Database", "📈 Visualizations", "🔍 Database Introspection", "🌐 ServiceNow Instance", "🔧 Configuration"]
        
        # Map current page to navigation option
        page_mapping = {
            "dashboard": "🏠 Dashboard",
            "comprehensive_scraper": "🕷️ Comprehensive Scraper",
            "database": "🗄️ Database",
            "visualizations": "📈 Visualizations",
            "introspection": "🔍 Database Introspection",
            "servicenow_instance": "🌐 ServiceNow Instance",
            "configuration": "🔧 Configuration"
        }
        
        # Get current page index for selectbox
        current_page_option = page_mapping.get(st.session_state.current_page, "🏠 Dashboard")
        current_index = navigation_options.index(current_page_option)
        
        page = st.selectbox(
            "Select Page:",
            navigation_options,
            index=current_index
        )
        
        # Update session state based on selection
        if page == "🏠 Dashboard":
            st.session_state.current_page = "dashboard"
        elif page == "🕷️ Comprehensive Scraper":
            st.session_state.current_page = "comprehensive_scraper"
        elif page == "🗄️ Database":
            st.session_state.current_page = "database"
        elif page == "📈 Visualizations":
            st.session_state.current_page = "visualizations"
        elif page == "🔍 Database Introspection":
            st.session_state.current_page = "introspection"
        elif page == "🌐 ServiceNow Instance":
            st.session_state.current_page = "servicenow_instance"
        elif page == "🔧 Configuration":
            st.session_state.current_page = "configuration"
        
        # Database status
        st.markdown("---")
        st.markdown("### 🗄️ Database Status")
        
        try:
            db_manager = DatabaseManager()
            session = db_manager.get_session()
            try:
                # Test basic connection first
                from sqlalchemy import text
                session.execute(text("SELECT 1"))
                
                # If basic connection works, try to get module count
                try:
                    from database import ServiceNowModule
                    module_count = session.query(ServiceNowModule).count()
                    if module_count > 0:
                        st.success(f"✅ Connected ({module_count} modules)")
                    else:
                        st.warning("⚠️ Connected (empty database)")
                except Exception as table_error:
                    # Tables don't exist yet
                    st.info("ℹ️ Connected (tables not created)")
            finally:
                session.close()
        except Exception as e:
            st.error(f"❌ Database error: {e}")
    
    # Main content area
    if st.session_state.current_page == "dashboard":
        show_dashboard()
    elif st.session_state.current_page == "comprehensive_scraper":
        show_comprehensive_scraper()
    elif st.session_state.current_page == "database":
        show_database_view()
    elif st.session_state.current_page == "visualizations":
        show_visualizations()
    elif st.session_state.current_page == "introspection":
        show_introspection()
    elif st.session_state.current_page == "servicenow_instance":
        show_servicenow_instance()
    elif st.session_state.current_page == "configuration":
        show_configuration_ui()

if __name__ == "__main__":
    main()
