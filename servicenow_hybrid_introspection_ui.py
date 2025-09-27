"""
ServiceNow Hybrid Introspection UI
Combines REST API + Database access for comprehensive ServiceNow instance analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from servicenow_database_connector import ServiceNowDatabaseConnector
from servicenow_database_queries import ServiceNowDatabaseQueries
from servicenow_database_validator import ServiceNowDatabaseValidator
from database import DatabaseManager
from typing import Dict, List, Any
import time
from datetime import datetime
import os


class ServiceNowHybridIntrospectionUI:
    """UI for hybrid ServiceNow introspection (REST API + Database)"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.connector = None
        self.queries = ServiceNowDatabaseQueries()
        self.validator = ServiceNowDatabaseValidator()
        
        # Initialize session state
        if 'hybrid_introspection_results' not in st.session_state:
            st.session_state.hybrid_introspection_results = {}
    
    def show_hybrid_introspection_interface(self):
        """Show the main hybrid introspection interface"""
        st.markdown('<h2 class="section-header">🔗 ServiceNow Hybrid Introspection</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        This advanced tool combines REST API and direct database access to provide comprehensive ServiceNow analysis:
        - **REST API Access**: Real-time data from ServiceNow instance
        - **Database Access**: Direct access to underlying database for deeper insights
        - **Data Correlation**: Cross-reference and validate data between sources
        - **Enhanced Security**: Secure credential management and validation
        """)
        
        # Connection configuration
        self._show_connection_config()
        
        # Introspection results
        if st.session_state.hybrid_introspection_results:
            self._show_introspection_results()
        
        # Show footer
        self.show_footer()
    
    def _show_connection_config(self):
        """Show connection configuration section"""
        st.markdown("### 🔗 Hybrid Connection Configuration")
        
        # Tabs for different connection types
        tab1, tab2, tab3 = st.tabs(["🌐 REST API", "🗄️ Database", "🔗 Hybrid Mode"])
        
        with tab1:
            self._show_rest_api_config()
        
        with tab2:
            self._show_database_config()
        
        with tab3:
            self._show_hybrid_config()
    
    def _show_rest_api_config(self):
        """Show REST API configuration"""
        st.markdown("#### ServiceNow REST API Configuration")
        
        # Get loaded configuration values if available
        loaded_config = st.session_state.get('loaded_rest_api_config', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            instance_url = st.text_input(
                "Instance URL",
                value=loaded_config.get('instance_url', os.getenv('SN_INSTANCE_URL', '')),
                help="ServiceNow instance URL (e.g., https://your-instance.service-now.com)",
                placeholder="https://your-instance.service-now.com"
            )
            
            username = st.text_input(
                "Username",
                value=loaded_config.get('username', os.getenv('SN_USERNAME', '')),
                help="ServiceNow username",
                placeholder="Enter username"
            )
        
        with col2:
            password = st.text_input(
                "Password",
                type="password",
                value=loaded_config.get('password', os.getenv('SN_PASSWORD', '')),
                help="ServiceNow password",
                placeholder="Enter password"
            )
            
            timeout = st.number_input(
                "Timeout (seconds)",
                value=loaded_config.get('timeout', 30),
                min_value=5,
                max_value=300,
                help="Request timeout"
            )
        
        # Load saved configuration section
        st.markdown("---")
        st.markdown("#### 📥 Load Saved Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 Load REST API Config", use_container_width=True, key="load_rest_api_config"):
                self._load_rest_api_configuration()
        
        with col2:
            if st.button("🗑️ Clear Loaded Config", use_container_width=True, key="clear_loaded_rest_api_config"):
                self._clear_loaded_rest_api_config()
        
        # Show loaded configuration if available
        if hasattr(st.session_state, 'loaded_rest_api_config') and st.session_state.loaded_rest_api_config:
            st.success("✅ Configuration loaded from database")
            loaded_config = st.session_state.loaded_rest_api_config
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.info(f"**Instance**: {loaded_config.get('instance_url', 'N/A')}")
            with col2:
                st.info(f"**Username**: {loaded_config.get('username', 'N/A')}")
            with col3:
                st.info(f"**Timeout**: {loaded_config.get('timeout', 'N/A')}s")
        
        # Action buttons
        st.markdown("---")
        st.markdown("#### 🔧 Configuration Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧪 Test REST API Connection", use_container_width=True, key="test_rest_api_connection"):
                self._test_rest_api_connection(instance_url, username, password, timeout)
        
        with col2:
            if st.button("💾 Save REST API Config", use_container_width=True, type="primary", key="save_rest_api_config"):
                self._save_rest_api_config(instance_url, username, password, timeout)
        
        with col3:
            if st.button("📊 Populate & Save Data", use_container_width=True, key="populate_save_data_1"):
                self._populate_and_save_rest_api_data(instance_url, username, password, timeout)
    
    def _load_rest_api_configuration(self):
        """Load REST API configuration from database"""
        try:
            from centralized_db_config import get_centralized_db_config
            centralized_config = get_centralized_db_config()
            
            # Get all REST API configurations
            configs = centralized_config.get_all_servicenow_configurations()
            
            if not configs:
                st.warning("⚠️ No REST API configurations found in database")
                return
            
            # Filter for REST API configurations
            rest_api_configs = [config for config in configs if config.get('name', '').startswith('hybrid_rest_api')]
            
            if not rest_api_configs:
                st.warning("⚠️ No REST API configurations found. Please save a configuration first.")
                return
            
            # Show configuration selection
            if len(rest_api_configs) == 1:
                selected_config = rest_api_configs[0]
                st.info(f"📥 Loading configuration: {selected_config.get('name', 'Unknown')}")
            else:
                config_names = [f"{config.get('name', 'Unknown')} ({config.get('instance_url', 'No URL')})" for config in rest_api_configs]
                selected_index = st.selectbox(
                    "Select configuration to load:",
                    range(len(config_names)),
                    format_func=lambda x: config_names[x],
                    key="unique_widget_key"
                )
                selected_config = rest_api_configs[selected_index]
            
            # Store in session state for form population
            st.session_state.loaded_rest_api_config = selected_config
            st.success(f"✅ Configuration '{selected_config.get('name', 'Unknown')}' loaded successfully!")
            
        except Exception as e:
            st.error(f"❌ Error loading REST API configuration: {e}")
    
    def _clear_loaded_rest_api_config(self):
        """Clear loaded REST API configuration from session state"""
        if hasattr(st.session_state, 'loaded_rest_api_config'):
            del st.session_state.loaded_rest_api_config
            st.success("🗑️ Loaded configuration cleared!")
        else:
            st.info("ℹ️ No configuration loaded to clear")
    
    def _show_database_config(self):
        """Show database configuration"""
        st.markdown("#### ServiceNow Database Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            db_type = st.selectbox(
                "Database Type",
                ["PostgreSQL", "MySQL", "SQL Server", "Oracle"],
                help="ServiceNow database type"
            )
            
            host = st.text_input(
                "Database Host",
                value=os.getenv('SN_DB_HOST', ''),
                help="Database server hostname or IP",
                placeholder="localhost or IP address"
            )
            
            port = st.number_input(
                "Port",
                value=5432 if db_type == "PostgreSQL" else 3306,
                min_value=1,
                max_value=65535,
                help="Database port"
            )
        
        with col2:
            database = st.text_input(
                "Database Name",
                value=os.getenv('SN_DB_NAME', ''),
                help="ServiceNow database name",
                placeholder="servicenow"
            )
            
            db_username = st.text_input(
                "Database Username",
                value=os.getenv('SN_DB_USER', ''),
                help="Database username",
                placeholder="Enter database username"
            )
            
            db_password = st.text_input(
                "Database Password",
                type="password",
                value=os.getenv('SN_DB_PASSWORD', ''),
                help="Database password",
                placeholder="Enter database password"
            )
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧪 Test Database Connection", use_container_width=True, key="test_database_connection_2"):
                self._test_database_connection(db_type, host, port, database, db_username, db_password)
        
        with col2:
            if st.button("💾 Save Database Config", use_container_width=True, type="primary", key="save_database_config_3"):
                self._save_database_config(db_type, host, port, database, db_username, db_password)
        
        with col3:
            if st.button("📊 Populate & Save Data", use_container_width=True, key="populate_save_data_4"):
                self._populate_and_save_database_data(db_type, host, port, database, db_username, db_password)
    
    def _show_hybrid_config(self):
        """Show hybrid configuration"""
        st.markdown("#### Hybrid Mode Configuration")
        
        st.info("💡 Hybrid mode combines both REST API and database access for comprehensive analysis.")
        
        # Check configuration status
        from centralized_db_config import get_centralized_db_config
        centralized_config = get_centralized_db_config()
        
        rest_api_config = centralized_config.get_servicenow_configuration('hybrid_rest_api')
        db_config = centralized_config.get_database_configuration('hybrid_database')
        
        # Show configuration status
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**REST API Status**")
            if rest_api_config:
                st.success("✅ REST API configured")
                st.caption(f"Instance: {rest_api_config.get('instance_url', 'N/A')}")
            else:
                st.warning("⚠️ REST API not configured")
                st.caption("Configure in REST API tab first")
        
        with col2:
            st.markdown("**Database Status**")
            if db_config:
                st.success("✅ Database configured")
                st.caption(f"Type: {db_config.get('db_type', 'N/A')} | Host: {db_config.get('host', 'N/A')}")
            else:
                st.warning("⚠️ Database not configured")
                st.caption("Configure in Database tab first")
        
        st.markdown("---")
        
        # Check for loaded configuration
        loaded_config = st.session_state.get('loaded_hybrid_config', {})
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**REST API Settings**")
            api_enabled = st.checkbox("Enable REST API", 
                                    value=loaded_config.get('api_enabled', bool(rest_api_config)))
            api_timeout = st.number_input("API Timeout", 
                                        value=loaded_config.get('api_timeout', 30), 
                                        min_value=5, max_value=300)
        
        with col2:
            st.markdown("**Database Settings**")
            db_enabled = st.checkbox("Enable Database Access", 
                                   value=loaded_config.get('db_enabled', bool(db_config)))
            db_timeout = st.number_input("DB Timeout", 
                                       value=loaded_config.get('db_timeout', 30), 
                                       min_value=5, max_value=300)
        
        # Advanced options
        st.markdown("**Advanced Options**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            correlation_enabled = st.checkbox("Enable Data Correlation", 
                                            value=loaded_config.get('correlation_enabled', True))
        
        with col2:
            validation_enabled = st.checkbox("Enable Security Validation", 
                                           value=loaded_config.get('validation_enabled', True))
        
        with col3:
            rate_limiting = st.checkbox("Enable Rate Limiting", 
                                      value=loaded_config.get('rate_limiting', True))
        
        # Force update option
        st.markdown("**Update Options**")
        force_update = st.checkbox("🔄 Force Update Existing Data", value=False, 
                                 help="Check this to update existing records instead of skipping them")
        
        # Clear loaded configuration option
        if loaded_config:
            st.markdown("**Configuration Management**")
            if st.button("🗑️ Clear Loaded Configuration", key="clear_loaded_configuration_5"):
                if 'loaded_hybrid_config' in st.session_state:
                    del st.session_state.loaded_hybrid_config
                st.success("✅ Loaded configuration cleared!")
                st.rerun()
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🚀 Start Hybrid Introspection", use_container_width=True, type="primary", key="start_hybrid_introspection_6"):
                self._start_hybrid_introspection(
                    api_enabled, db_enabled, correlation_enabled, 
                    validation_enabled, rate_limiting, api_timeout, db_timeout, force_update
                )
        
        with col2:
            if st.button("💾 Save Hybrid Config", use_container_width=True, key="save_hybrid_config_7"):
                self._save_hybrid_config(
                api_enabled, db_enabled, correlation_enabled, 
                validation_enabled, rate_limiting, api_timeout, db_timeout
            )
        
        with col3:
            if st.button("📊 Populate & Save Data", use_container_width=True, key="populate_save_data_8"):
                self._populate_and_save_hybrid_data(
                    api_enabled, db_enabled, correlation_enabled, 
                    validation_enabled, rate_limiting, api_timeout, db_timeout, force_update
                )
        
        with col4:
            if st.button("📥 Load Configuration", use_container_width=True, key="load_configuration_9"):
                self._load_hybrid_configuration()
    
    def _test_rest_api_connection(self, instance_url: str, username: str, password: str, timeout: int):
        """Test REST API connection"""
        try:
            if not instance_url or not username or not password:
                st.error("❌ Please fill in all required fields")
                return
            
            # Validate inputs
            validation_result = self.validator.validate_instance_url(instance_url)
            if not validation_result['is_valid']:
                st.error(f"❌ Invalid instance URL: {', '.join(validation_result['errors'])}")
                return
            
            # Test connection
            with st.spinner("Testing REST API connection..."):
                from servicenow_api_client import ServiceNowAPIClient
                api_client = ServiceNowAPIClient(instance_url, username, password)
                test_result = api_client.test_connection()
                
                if test_result['success']:
                    st.success("✅ REST API connection successful!")
                    st.info(f"Connected to: {instance_url}")
                else:
                    st.error(f"❌ REST API connection failed: {test_result['message']}")
        
        except Exception as e:
            st.error(f"❌ Connection test failed: {str(e)}")
    
    def _test_database_connection(self, db_type: str, host: str, port: int, database: str, username: str, password: str):
        """Test database connection"""
        try:
            if not host or not database or not username:
                st.error("❌ Please fill in all required fields")
                return
            
            # Build connection string
            import urllib.parse
            encoded_password = urllib.parse.quote_plus(password) if password else ""
            encoded_username = urllib.parse.quote_plus(username)
            encoded_host = urllib.parse.quote_plus(host)
            encoded_database = urllib.parse.quote_plus(database)
            
            if db_type == "PostgreSQL":
                connection_string = f"postgresql://user:password@host:port/database"
            elif db_type == "MySQL":
                connection_string = f"mysql+pymysql://user:password@host:port/database"
            elif db_type == "SQL Server":
                connection_string = f"mssql+pyodbc://{encoded_username}:{encoded_password}@{encoded_host}:{port}/{encoded_database}?driver=ODBC+Driver+17+for+SQL+Server"
            elif db_type == "Oracle":
                connection_string = f"oracle://{encoded_username}:{encoded_password}@{encoded_host}:{port}/{encoded_database}"
            else:
                st.error(f"❌ Unsupported database type: {db_type}")
                return
            
            # Validate connection string
            validation_result = self.validator.validate_database_connection_string(connection_string)
            if not validation_result['is_valid']:
                st.error(f"❌ Invalid connection string: {', '.join(validation_result['errors'])}")
                return
            
            # Test connection
            with st.spinner("Testing database connection..."):
                from sqlalchemy import create_engine, text
                engine = create_engine(connection_string)
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                
                st.success("✅ Database connection successful!")
                st.info(f"Connected to: {db_type} database '{database}' on {host}:{port}")
                
                # Check if it's a ServiceNow database
                servicenow_validation = self.validator.validate_servicenow_database(connection_string)
                if servicenow_validation['is_servicenow']:
                    st.success(f"🎉 ServiceNow database detected! (Confidence: {servicenow_validation['confidence_score']:.1%})")
                    if servicenow_validation['version']:
                        st.info(f"Version: {servicenow_validation['version']}")
                else:
                    st.warning("⚠️ This may not be a ServiceNow database")
        
        except Exception as e:
            st.error(f"❌ Database connection failed: {str(e)}")
    
    def _start_hybrid_introspection(self, api_enabled: bool, db_enabled: bool, 
                                  correlation_enabled: bool, validation_enabled: bool, 
                                  rate_limiting: bool, api_timeout: int, db_timeout: int, force_update: bool = False):
        """Start hybrid introspection"""
        try:
            if not api_enabled and not db_enabled:
                st.error("❌ Please enable at least one connection type (REST API or Database)")
                return
            
            # Get configurations from centralized storage
            from centralized_db_config import get_centralized_db_config
            centralized_config = get_centralized_db_config()
            
            instance_url = None
            db_connection_string = None
            
            # Get REST API configuration if enabled
            if api_enabled:
                rest_api_config = centralized_config.get_servicenow_configuration('hybrid_rest_api')
                if rest_api_config:
                    instance_url = rest_api_config.get('instance_url')
                else:
                    st.warning("⚠️ REST API configuration not found. Please configure REST API settings first.")
            
            # Get Database configuration if enabled
            if db_enabled:
                db_config = centralized_config.get_database_configuration('hybrid_database')
                if db_config:
                    # Build connection string from saved configuration
                    db_type = db_config.get('db_type', 'postgresql')
                    host = db_config.get('host')
                    port = db_config.get('port')
                    database = db_config.get('database_name')
                    username = db_config.get('username')
                    password = db_config.get('password')
                    
                    if db_type == 'postgresql':
                        db_connection_string = f"postgresql://user:password@host:port/database"
                        # Warn about PostgreSQL limitations
                        if not api_enabled:
                            st.warning("⚠️ **PostgreSQL Database Detected**: PostgreSQL databases don't contain ServiceNow system tables. Please enable REST API connection for data collection.")
                    elif db_type == 'mysql':
                        db_connection_string = f"mysql+pymysql://user:password@host:port/database"
                else:
                    st.warning("⚠️ Database configuration not found. Please configure Database settings first.")
            
            # Check if we have at least one valid configuration
            if not instance_url and not db_connection_string:
                st.error("❌ Please configure REST API and/or Database settings in the respective tabs first.")
                return
            
            # Initialize connector with available configurations
            self.connector = ServiceNowDatabaseConnector(instance_url, db_connection_string)
            
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Establish connections
            status_text.text("🔗 Establishing connections...")
            progress_bar.progress(20)
            
            connection_results = self.connector.establish_connections()
            
            if not connection_results['database_connected'] and not connection_results['api_connected']:
                st.error("❌ Failed to establish any connections")
                
                # Show detailed error information
                st.markdown("#### 🔍 Connection Error Details")
                for error in connection_results['errors']:
                    st.error(f"• {error}")
                
                # Provide specific guidance based on error types
                st.markdown("#### 💡 Troubleshooting Steps")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**🌐 REST API Connection:**")
                    st.markdown("""
                    1. Verify ServiceNow instance URL is correct
                    2. Check if instance is accessible from your network
                    3. Ensure username and password are valid
                    4. Test connection in browser first
                    5. Check firewall/proxy settings
                    """)
                
                with col2:
                    st.markdown("**🗄️ Database Connection:**")
                    st.markdown("""
                    1. Verify database connection string
                    2. Check if database server is running
                    3. Ensure user has proper permissions
                    4. For PostgreSQL: Use only REST API
                    5. For ServiceNow DB: Check table access
                    """)
                
                return
            
            # Get hybrid data
            status_text.text("📊 Extracting comprehensive data...")
            progress_bar.progress(50)
            
            hybrid_data = self.connector.get_hybrid_data()
            
            # Store results
            st.session_state.hybrid_introspection_results = hybrid_data
            
            # Save comprehensive data to database
            status_text.text("💾 Saving comprehensive data to database...")
            progress_bar.progress(75)
            
            self._save_comprehensive_data_to_database(hybrid_data, force_update)
            
            progress_bar.progress(100)
            status_text.text("✅ Hybrid introspection completed!")
            
            # Show summary
            summary = hybrid_data.get('summary', {})
            api_summary = hybrid_data.get('api_data', {}).get('summary', {})
            db_summary = hybrid_data.get('database_data', {}).get('summary', {})
            
            api_total = api_summary.get('total_items', 0) if api_summary else 0
            if api_total is None:
                api_total = 0
            total_items = api_total + len(db_summary.get('modules', [])) + len(db_summary.get('tables', []))
            
            st.success(f"🎉 Successfully extracted {total_items} items from ServiceNow!")
            
            # Show detailed breakdown
            if api_total > 0:
                st.info(f"📊 API Data: {api_summary.get('modules_count', 0)} modules, {api_summary.get('roles_count', 0)} roles, {api_summary.get('tables_count', 0)} tables, {api_summary.get('properties_count', 0)} properties, {api_summary.get('scheduled_jobs_count', 0)} scheduled jobs")
            
            if db_summary:
                st.info(f"🗄️ Database Data: {len(db_summary.get('modules', []))} modules, {len(db_summary.get('tables', []))} tables")
            
            if summary.get('correlation_score', 0) > 0:
                st.info(f"📊 Data correlation score: {summary['correlation_score']:.1%}")
        
        except Exception as e:
            st.error(f"❌ Hybrid introspection failed: {str(e)}")
    
    def _save_comprehensive_data_to_database(self, hybrid_data: dict, force_update: bool = False):
        """Save comprehensive hybrid introspection data to database"""
        try:
            # Import database models
            from database import ServiceNowModule, ServiceNowRole, ServiceNowTable, ServiceNowProperty, ServiceNowScheduledJob
            
            session = self.db_manager.get_session()
            try:
                # Get API data
                api_data = hybrid_data.get('api_data', {})
                db_data = hybrid_data.get('database_data', {})
                
                saved_count = 0
                skipped_count = 0
                
                # Save modules from API
                if api_data.get('modules'):
                    for module_data in api_data['modules']:
                        existing_module = session.query(ServiceNowModule).filter_by(
                            name=module_data['name']
                        ).first()
                        
                        if not existing_module:
                            module = ServiceNowModule(
                                name=module_data['name'],
                                label=module_data.get('label', ''),
                                description=module_data.get('description', ''),
                                is_active=module_data.get('active', True)
                            )
                            session.add(module)
                            saved_count += 1
                        elif force_update:
                            # Update existing module
                            existing_module.label = module_data.get('label', existing_module.label)
                            existing_module.description = module_data.get('description', existing_module.description)
                            existing_module.is_active = module_data.get('active', existing_module.is_active)
                            saved_count += 1
                        else:
                            skipped_count += 1
                
                # Save roles from API
                if api_data.get('roles'):
                    for role_data in api_data['roles']:
                        existing_role = session.query(ServiceNowRole).filter_by(
                            name=role_data['name']
                        ).first()
                        
                        if not existing_role:
                            role = ServiceNowRole(
                                name=role_data['name'],
                                label=role_data.get('label', ''),
                                description=role_data.get('description', ''),
                                is_active=role_data.get('active', True)
                            )
                            session.add(role)
                            saved_count += 1
                        else:
                            skipped_count += 1
                
                # Save tables from API
                if api_data.get('tables'):
                    for table_data in api_data['tables']:
                        existing_table = session.query(ServiceNowTable).filter_by(
                            name=table_data['name']
                        ).first()
                        
                        if not existing_table:
                            table = ServiceNowTable(
                                name=table_data['name'],
                                label=table_data.get('label', ''),
                                description=table_data.get('description', ''),
                                is_active=table_data.get('active', True)
                            )
                            session.add(table)
                            saved_count += 1
                        else:
                            skipped_count += 1
                
                # Save properties from API
                if api_data.get('properties'):
                    for prop_data in api_data['properties']:
                        existing_prop = session.query(ServiceNowProperty).filter_by(
                            name=prop_data['name']
                        ).first()
                        
                        if not existing_prop:
                            # Get or create a default module for properties
                            default_module = session.query(ServiceNowModule).filter_by(
                                name='System'
                            ).first()
                            
                            if not default_module:
                                default_module = ServiceNowModule(
                                    name='System',
                                    label='System',
                                    description='System module for properties and scheduled jobs',
                                    is_active=True
                                )
                                session.add(default_module)
                                session.flush()  # Get the ID
                            
                            prop = ServiceNowProperty(
                                name=prop_data['name'],
                                current_value=prop_data.get('value', ''),
                                description=prop_data.get('description', ''),
                                property_type=prop_data.get('type', 'string'),
                                module_id=default_module.id
                            )
                            session.add(prop)
                            saved_count += 1
                        else:
                            skipped_count += 1
                
                # Save scheduled jobs from API
                if api_data.get('scheduled_jobs'):
                    for job_data in api_data['scheduled_jobs']:
                        existing_job = session.query(ServiceNowScheduledJob).filter_by(
                            name=job_data['name']
                        ).first()
                        
                        if not existing_job:
                            # Get or create a default module for scheduled jobs
                            default_module = session.query(ServiceNowModule).filter_by(
                                name='System'
                            ).first()
                            
                            if not default_module:
                                default_module = ServiceNowModule(
                                    name='System',
                                    label='System',
                                    description='System module for properties and scheduled jobs',
                                    is_active=True
                                )
                                session.add(default_module)
                                session.flush()  # Get the ID
                            
                            job = ServiceNowScheduledJob(
                                name=job_data['name'],
                                description=job_data.get('description', ''),
                                script=job_data.get('script', ''),
                                active=job_data.get('active', True),
                                module_id=default_module.id
                            )
                            session.add(job)
                            saved_count += 1
                        else:
                            skipped_count += 1
                
                # Save database modules
                if db_data.get('modules'):
                    for module_data in db_data['modules']:
                        existing_module = session.query(ServiceNowModule).filter_by(
                            name=module_data['name']
                        ).first()
                        
                        if not existing_module:
                            module = ServiceNowModule(
                                name=module_data['name'],
                                label=module_data.get('label', ''),
                                description=module_data.get('description', ''),
                                is_active=True
                            )
                            session.add(module)
                            saved_count += 1
                        else:
                            skipped_count += 1
                
                # Save database tables
                if db_data.get('tables'):
                    for table_data in db_data['tables']:
                        existing_table = session.query(ServiceNowTable).filter_by(
                            name=table_data['name']
                        ).first()
                        
                        if not existing_table:
                            table = ServiceNowTable(
                                name=table_data['name'],
                                label=table_data.get('label', ''),
                                description=table_data.get('description', ''),
                                is_active=True
                            )
                            session.add(table)
                            saved_count += 1
                        else:
                            skipped_count += 1
                
                # Save database properties
                if db_data.get('properties'):
                    for prop_data in db_data['properties']:
                        existing_prop = session.query(ServiceNowProperty).filter_by(
                            name=prop_data['name']
                        ).first()
                        
                        if not existing_prop:
                            # Get or create a default module for properties
                            default_module = session.query(ServiceNowModule).filter_by(
                                name='System'
                            ).first()
                            
                            if not default_module:
                                default_module = ServiceNowModule(
                                    name='System',
                                    label='System',
                                    description='System module for properties and scheduled jobs',
                                    is_active=True
                                )
                                session.add(default_module)
                                session.flush()  # Get the ID
                            
                            prop = ServiceNowProperty(
                                name=prop_data['name'],
                                current_value=prop_data.get('value', ''),
                                description=prop_data.get('description', ''),
                                property_type=prop_data.get('type', 'string'),
                                module_id=default_module.id
                            )
                            session.add(prop)
                            saved_count += 1
                        else:
                            skipped_count += 1
                
                # Commit all changes
                session.commit()
                
                # Also save to centralized configuration for cross-tab access
                from centralized_db_config import get_centralized_db_config
                centralized_config = get_centralized_db_config()
                
                # Save comprehensive data summary
                comprehensive_summary = {
                    'name': 'comprehensive_introspection_data',
                    'data_type': 'comprehensive_introspection',
                    'api_data': api_data,
                    'database_data': db_data,
                    'correlation_results': hybrid_data.get('correlation_results', {}),
                    'summary': hybrid_data.get('summary', {}),
                    'metadata': {
                        'created_at': datetime.now().isoformat(),
                        'data_source': 'hybrid_introspection',
                        'total_items_saved': saved_count,
                        'api_items': api_data.get('summary', {}).get('total_items', 0),
                        'database_items': len(db_data.get('modules', [])) + len(db_data.get('tables', [])) + len(db_data.get('properties', []))
                    },
                    'is_active': True
                }
                
                # Add name to the config_data
                comprehensive_summary['name'] = 'comprehensive_introspection_data'
                centralized_config.save_servicenow_configuration(comprehensive_summary)
                
                if saved_count > 0:
                    st.success(f"💾 Saved {saved_count} new items to database")
                if skipped_count > 0:
                    st.info(f"⏭️ Skipped {skipped_count} items (already exist in database)")
                if saved_count == 0 and skipped_count == 0:
                    # Check if we actually have data to process
                    api_data = hybrid_data.get('api_data', {})
                    db_data = hybrid_data.get('database_data', {})
                    
                    api_summary = api_data.get('summary', {})
                    api_items = api_summary.get('total_items', 0) if api_summary else 0
                    if api_items is None:
                        api_items = 0
                    
                    db_items = len(db_data.get('modules', [])) + len(db_data.get('tables', [])) + len(db_data.get('properties', []))
                    
                    if api_items == 0 and db_items == 0:
                        st.warning("⚠️ No data was collected from ServiceNow")
                        
                        # Provide specific troubleshooting guidance
                        st.markdown("#### 🔍 Troubleshooting Guide")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**🌐 REST API Issues:**")
                            st.markdown("""
                            - Check if ServiceNow instance URL is correct
                            - Verify the instance is accessible from your network
                            - Ensure username and password are valid
                            - Check if your account has API permissions
                            - Try accessing the instance in your browser first
                            """)
                        
                        with col2:
                            st.markdown("**🗄️ Database Issues:**")
                            st.markdown("""
                            - If using PostgreSQL: This is normal - PostgreSQL doesn't contain ServiceNow tables
                            - For ServiceNow database: Check connection string and permissions
                            - Ensure database contains ServiceNow system tables
                            - Verify database user has read permissions
                            """)
                        
                        st.info("💡 **Tip**: For PostgreSQL databases, use only REST API connection. For ServiceNow databases, you can use both API and database connections.")
                    else:
                        st.warning(f"⚠️ No data was saved to database despite collecting {api_items + db_items} items - all items already exist in database")
                        st.info("💡 Enable 'Force Update Existing Data' to update existing records")
                
                # Return the saved count for the calling method
                return saved_count
                
            finally:
                session.close()
                
        except Exception as e:
            st.error(f"❌ Error saving comprehensive data to database: {e}")
    
    def _show_introspection_results(self):
        """Show hybrid introspection results with enhanced visual analytics"""
        if not st.session_state.hybrid_introspection_results:
            return
        
        results = st.session_state.hybrid_introspection_results
        
        st.markdown("### 📊 Hybrid Introspection Results")
        
        # Summary metrics with enhanced styling
        summary = results.get('summary', {})
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "📊 Total Items", 
                summary.get('total_items', 0),
                help="Total items collected from all sources"
            )
        with col2:
            st.metric(
                "🗄️ Database Items", 
                summary.get('database_items', 0),
                help="Items collected from direct database access"
            )
        with col3:
            st.metric(
                "🌐 API Items", 
                summary.get('api_items', 0),
                help="Items collected from REST API"
            )
        with col4:
            st.metric(
                "🔗 Correlation Score", 
                f"{summary.get('correlation_score', 0):.1%}",
                help="Data correlation between sources"
            )
        with col5:
            last_updated = summary.get('last_updated', 'Unknown')
            if last_updated != 'Unknown':
                from datetime import datetime
                try:
                    dt = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                    formatted_time = dt.strftime('%H:%M:%S')
                except:
                    formatted_time = last_updated
            else:
                formatted_time = 'Unknown'
            st.metric("⏰ Last Updated", formatted_time, help="Time of last data collection")
        
        # Data source comparison chart
        self._show_data_source_chart(results)
        
        # Detailed results tabs with enhanced content
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🗄️ Database Data", 
            "🌐 API Data", 
            "🔗 Correlation", 
            "📈 Analytics", 
            "📋 Raw Data"
        ])
        
        with tab1:
            self._show_database_data(results.get('database_data', {}))
        
        with tab2:
            self._show_api_data(results.get('api_data', {}))
        
        with tab3:
            self._show_correlation_results(results.get('correlation_results', {}))
        
        with tab4:
            self._show_analysis_results(results)
            
        with tab5:
            self._show_raw_data(results)
    
    def _show_data_source_chart(self, results: Dict):
        """Show data source comparison chart"""
        try:
            import plotly.express as px
            import plotly.graph_objects as go
            
            summary = results.get('summary', {})
            api_items = summary.get('api_items', 0)
            db_items = summary.get('database_items', 0)
            
            if api_items > 0 or db_items > 0:
                # Create pie chart for data sources
                labels = ['REST API', 'Database']
                values = [api_items, db_items]
                colors = ['#1f77b4', '#ff7f0e']
                
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.3,
                    marker_colors=colors,
                    textinfo='label+percent+value',
                    textfont_size=12
                )])
                
                fig.update_layout(
                    title="📊 Data Source Distribution",
                    title_x=0.5,
                    showlegend=True,
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add insights
                if api_items > db_items:
                    st.info("💡 **Insight**: REST API is the primary data source, providing more comprehensive coverage.")
                elif db_items > api_items:
                    st.info("💡 **Insight**: Database access is the primary data source, providing direct access to underlying data.")
                else:
                    st.info("💡 **Insight**: Both data sources are providing equal coverage.")
                    
        except ImportError:
            st.warning("📊 Chart visualization requires plotly. Install with: pip install plotly")
        except Exception as e:
            st.warning(f"📊 Chart visualization error: {e}")
    
    def _show_raw_data(self, results: Dict):
        """Show raw data in expandable sections"""
        st.markdown("#### 📋 Raw Data Export")
        
        # JSON export
        if st.button("📥 Export as JSON", key="export_as_json_10"):
            import json
            json_data = json.dumps(results, indent=2, default=str)
            st.download_button(
                label="💾 Download JSON",
                data=json_data,
                file_name=f"hybrid_introspection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        # Expandable sections for different data types
        with st.expander("🔍 Instance Information", expanded=False):
            instance_info = results.get('instance_info', {})
            if instance_info:
                st.json(instance_info)
            else:
                st.info("No instance information available")
        
        with st.expander("🗄️ Database Data Details", expanded=False):
            db_data = results.get('database_data', {})
            if db_data:
                st.json(db_data)
            else:
                st.info("No database data available")
        
        with st.expander("🌐 API Data Details", expanded=False):
            api_data = results.get('api_data', {})
            if api_data:
                st.json(api_data)
            else:
                st.info("No API data available")
        
        with st.expander("🔗 Correlation Results", expanded=False):
            correlation = results.get('correlation_results', {})
            if correlation:
                st.json(correlation)
            else:
                st.info("No correlation data available")
    
    def _show_database_data(self, database_data: Dict):
        """Show database data results with enhanced visualization"""
        if not database_data:
            st.info("ℹ️ No database data available - this is normal if using PostgreSQL instead of ServiceNow database")
            return
        
        # Summary cards
        modules_count = len(database_data.get('modules', []))
        roles_count = len(database_data.get('roles', []))
        properties_count = len(database_data.get('properties', []))
        tables_count = len(database_data.get('tables', []))
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 Modules", modules_count)
        with col2:
            st.metric("👥 Roles", roles_count)
        with col3:
            st.metric("⚙️ Properties", properties_count)
        with col4:
            st.metric("📊 Tables", tables_count)
        
        # Modules
        if database_data.get('modules'):
            st.markdown("#### 📦 Modules (Database)")
            modules_df = pd.DataFrame(database_data['modules'])
            st.dataframe(modules_df, use_container_width=True)
            
            # Module status chart
            if 'active' in modules_df.columns:
                try:
                    import plotly.express as px
                    status_counts = modules_df['active'].value_counts()
                    fig = px.pie(
                        values=status_counts.values, 
                        names=status_counts.index.map({True: 'Active', False: 'Inactive'}),
                        title="Module Status Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    pass
        
        # Roles
        if database_data.get('roles'):
            st.markdown("#### 👥 Roles (Database)")
            roles_df = pd.DataFrame(database_data['roles'])
            st.dataframe(roles_df, use_container_width=True)
        
        # Properties
        if database_data.get('properties'):
            st.markdown("#### ⚙️ Properties (Database)")
            properties_df = pd.DataFrame(database_data['properties'])
            st.dataframe(properties_df, use_container_width=True)
            
            # Property type distribution
            if 'type' in properties_df.columns:
                try:
                    import plotly.express as px
                    type_counts = properties_df['type'].value_counts()
                    fig = px.bar(
                        x=type_counts.index, 
                        y=type_counts.values,
                        title="Property Types Distribution"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    pass
        
        # Tables
        if database_data.get('tables'):
            st.markdown("#### 📊 Tables (Database)")
            tables_df = pd.DataFrame(database_data['tables'])
            st.dataframe(tables_df, use_container_width=True)
    
    def _show_api_data(self, api_data: Dict):
        """Show API data results with enhanced visualization"""
        if not api_data:
            st.info("ℹ️ No API data available")
            return
        
        # Summary from API data
        summary = api_data.get('summary', {})
        modules_count = summary.get('modules_count', len(api_data.get('modules', [])))
        roles_count = summary.get('roles_count', len(api_data.get('roles', [])))
        tables_count = summary.get('tables_count', len(api_data.get('tables', [])))
        properties_count = summary.get('properties_count', len(api_data.get('properties', [])))
        scheduled_jobs_count = summary.get('scheduled_jobs_count', len(api_data.get('scheduled_jobs', [])))
        
        # Summary cards
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("📦 Modules", modules_count)
        with col2:
            st.metric("👥 Roles", roles_count)
        with col3:
            st.metric("📊 Tables", tables_count)
        with col4:
            st.metric("⚙️ Properties", properties_count)
        with col5:
            st.metric("⏰ Scheduled Jobs", scheduled_jobs_count)
        
        # Data type distribution chart
        try:
            import plotly.express as px
            import plotly.graph_objects as go
            
            data_types = ['Modules', 'Roles', 'Tables', 'Properties', 'Scheduled Jobs']
            counts = [modules_count, roles_count, tables_count, properties_count, scheduled_jobs_count]
            
            # Filter out zero counts for cleaner chart
            filtered_data = [(dt, count) for dt, count in zip(data_types, counts) if count > 0]
            if filtered_data:
                labels, values = zip(*filtered_data)
                
                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.4,
                    textinfo='label+percent+value',
                    textfont_size=10
                )])
                
                fig.update_layout(
                    title="📊 API Data Distribution",
                    title_x=0.5,
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
        except:
            pass
        
        # Modules
        if api_data.get('modules'):
            st.markdown("#### 📦 Modules (API)")
            modules_df = pd.DataFrame(api_data['modules'])
            st.dataframe(modules_df, use_container_width=True)
        
        # Roles
        if api_data.get('roles'):
            st.markdown("#### 👥 Roles (API)")
            roles_df = pd.DataFrame(api_data['roles'])
            st.dataframe(roles_df, use_container_width=True)
            
            # Role insights
            if len(roles_df) > 0:
                st.markdown("##### 🔍 Role Insights")
                col1, col2 = st.columns(2)
                with col1:
                    if 'active' in roles_df.columns:
                        active_roles = roles_df[roles_df['active'] == True].shape[0]
                        st.info(f"✅ **Active Roles**: {active_roles}")
                with col2:
                    if 'description' in roles_df.columns:
                        roles_with_desc = roles_df[roles_df['description'].notna()].shape[0]
                        st.info(f"📝 **Roles with Description**: {roles_with_desc}")
        
        # Tables
        if api_data.get('tables'):
            st.markdown("#### 📊 Tables (API)")
            tables_df = pd.DataFrame(api_data['tables'])
            st.dataframe(tables_df, use_container_width=True)
        
        # Properties
        if api_data.get('properties'):
            st.markdown("#### ⚙️ Properties (API)")
            properties_df = pd.DataFrame(api_data['properties'])
            st.dataframe(properties_df, use_container_width=True)
        
        # Scheduled Jobs
        if api_data.get('scheduled_jobs'):
            st.markdown("#### ⏰ Scheduled Jobs (API)")
            jobs_df = pd.DataFrame(api_data['scheduled_jobs'])
            st.dataframe(jobs_df, use_container_width=True)
            
            # Job insights
            if len(jobs_df) > 0:
                st.markdown("##### 🔍 Scheduled Job Insights")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if 'active' in jobs_df.columns:
                        active_jobs = jobs_df[jobs_df['active'] == True].shape[0]
                        st.info(f"✅ **Active Jobs**: {active_jobs}")
                with col2:
                    if 'state' in jobs_df.columns:
                        running_jobs = jobs_df[jobs_df['state'] == 'running'].shape[0]
                        st.info(f"🏃 **Running Jobs**: {running_jobs}")
                with col3:
                    if 'next_run' in jobs_df.columns:
                        upcoming_jobs = jobs_df[jobs_df['next_run'].notna()].shape[0]
                        st.info(f"⏭️ **Upcoming Jobs**: {upcoming_jobs}")
    
    def _show_correlation_results(self, correlation_results: Dict):
        """Show data correlation results"""
        if not correlation_results:
            st.info("No correlation data available")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Matched Items", correlation_results.get('matched_items', 0))
            st.metric("Database Only", correlation_results.get('database_only', 0))
        
        with col2:
            st.metric("API Only", correlation_results.get('api_only', 0))
            st.metric("Correlation Score", f"{correlation_results.get('correlation_score', 0):.1%}")
        
        # Correlation chart
        if correlation_results.get('matched_items', 0) > 0:
            fig = px.pie(
                values=[
                    correlation_results.get('matched_items', 0),
                    correlation_results.get('database_only', 0),
                    correlation_results.get('api_only', 0)
                ],
                names=['Matched', 'Database Only', 'API Only'],
                title="Data Source Correlation"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_analysis_results(self, results: Dict):
        """Show comprehensive analysis results with actionable insights"""
        st.markdown("#### 📈 Comprehensive Analysis")
        
        # Get data for analysis
        api_data = results.get('api_data', {})
        db_data = results.get('database_data', {})
        correlation_results = results.get('correlation_results', {})
        summary = results.get('summary', {})
        
        # Calculate real metrics
        api_summary = api_data.get('summary', {})
        api_items = api_summary.get('total_items', 0) if api_summary else 0
        db_items = len(db_data.get('modules', [])) + len(db_data.get('tables', [])) + len(db_data.get('properties', []))
        
        # Data source analysis
        st.markdown("##### 🔍 Data Source Analysis")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🌐 API Items", api_items, help="Items collected from REST API")
        with col2:
            st.metric("🗄️ Database Items", db_items, help="Items collected from database")
        with col3:
            correlation_score = correlation_results.get('correlation_score', 0)
            st.metric("🔗 Correlation Score", f"{correlation_score:.1%}", help="Data correlation between sources")
        with col4:
            total_items = summary.get('total_items', 0)
            st.metric("📊 Total Items", total_items, help="Total unique items across all sources")
        
        # Data quality assessment
        st.markdown("##### 📊 Data Quality Assessment")
        self._show_data_quality_metrics(results)
        
        # Correlation analysis
        st.markdown("##### 🔗 Correlation Analysis")
        self._show_correlation_analysis(correlation_results, api_data, db_data)
        
        # Discrepancy investigation
        if correlation_score < 0.8:
            st.markdown("##### 🔍 Data Discrepancy Investigation")
            self._show_discrepancy_investigation(api_data, db_data, correlation_results)
        
        # Recommendations
        st.markdown("##### 💡 Actionable Recommendations")
        self._show_actionable_recommendations(results)
        
        # Data validation tools
        st.markdown("##### 🛠️ Data Validation Tools")
        self._show_data_validation_tools(results)
        
        # Save results
        st.markdown("---")
        if st.button("💾 Save Analysis Results to Database", use_container_width=True, key="save_analysis_results_to_database_11"):
            self._save_hybrid_results(results)
    
    def _show_data_quality_metrics(self, results: Dict):
        """Show data quality metrics"""
        api_data = results.get('api_data', {})
        db_data = results.get('database_data', {})
        
        # Calculate completeness
        api_summary = api_data.get('summary', {})
        api_items = api_summary.get('total_items', 0) if api_summary else 0
        db_items = len(db_data.get('modules', [])) + len(db_data.get('tables', [])) + len(db_data.get('properties', []))
        
        # Calculate metrics
        total_possible = max(api_items, db_items) if max(api_items, db_items) > 0 else 1
        completeness = min(api_items, db_items) / total_possible if total_possible > 0 else 0
        
        # Data consistency (based on correlation)
        correlation_score = results.get('correlation_results', {}).get('correlation_score', 0)
        consistency = correlation_score
        
        # Data accuracy (estimated based on completeness and consistency)
        accuracy = (completeness + consistency) / 2
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📊 Data Completeness", f"{completeness:.1%}", 
                     delta=f"{min(api_items, db_items)}/{total_possible} items")
        
        with col2:
            st.metric("🎯 Data Accuracy", f"{accuracy:.1%}", 
                     delta="Estimated from correlation")
        
        with col3:
            st.metric("🔄 Data Consistency", f"{consistency:.1%}", 
                     delta="Source correlation")
    
    def _show_correlation_analysis(self, correlation_results: Dict, api_data: Dict, db_data: Dict):
        """Show detailed correlation analysis"""
        matched_items = correlation_results.get('matched_items', 0)
        database_only = correlation_results.get('database_only', 0)
        api_only = correlation_results.get('api_only', 0)
        correlation_score = correlation_results.get('correlation_score', 0)
        
        # Correlation status
        if correlation_score > 0.8:
            st.success("✅ **Excellent Correlation**: Data sources are highly consistent")
        elif correlation_score > 0.5:
            st.warning("⚠️ **Moderate Correlation**: Some discrepancies detected")
        else:
            st.error("❌ **Low Correlation**: Significant discrepancies require investigation")
        
        # Detailed breakdown
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("🤝 Matched Items", matched_items, help="Items found in both sources")
        
        with col2:
            st.metric("🗄️ Database Only", database_only, help="Items only in database")
        
        with col3:
            st.metric("🌐 API Only", api_only, help="Items only in API")
        
        # Show discrepancies if any
        if database_only > 0 or api_only > 0:
            st.markdown("##### 📋 Discrepancy Details")
            
            if database_only > 0:
                st.warning(f"⚠️ **{database_only} items** are only in the database")
                st.info("💡 This could indicate: API permissions, data filtering, or database-specific data")
            
            if api_only > 0:
                st.warning(f"⚠️ **{api_only} items** are only in the API")
                st.info("💡 This could indicate: Database connection issues, table access, or API-specific data")
    
    def _show_discrepancy_investigation(self, api_data: Dict, db_data: Dict, correlation_results: Dict):
        """Show tools to investigate data discrepancies"""
        st.markdown("**🔍 Investigation Tools**")
        
        # Show specific discrepancies
        discrepancies = correlation_results.get('discrepancies', [])
        
        if discrepancies:
            st.markdown("##### 🚨 Identified Discrepancies")
            
            # Group discrepancies by type
            discrepancy_types = {}
            for disc in discrepancies:
                disc_type = disc.get('type', 'Unknown')
                if disc_type not in discrepancy_types:
                    discrepancy_types[disc_type] = []
                discrepancy_types[disc_type].append(disc)
            
            for disc_type, disc_list in discrepancy_types.items():
                with st.expander(f"🔍 {disc_type} ({len(disc_list)} items)", expanded=False):
                    for i, disc in enumerate(disc_list[:10]):  # Show first 10
                        st.write(f"**{i+1}.** {disc.get('description', 'No description')}")
                        if disc.get('api_value'):
                            st.write(f"   🌐 API: {disc['api_value']}")
                        if disc.get('db_value'):
                            st.write(f"   🗄️ DB: {disc['db_value']}")
                    if len(disc_list) > 10:
                        st.info(f"... and {len(disc_list) - 10} more discrepancies")
        else:
            st.info("ℹ️ No specific discrepancies identified")
        
        # Investigation actions
        st.markdown("##### 🛠️ Investigation Actions")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Re-run Data Collection", key="rerun_data_collection_12"):
                st.info("💡 Use the 'Populate & Save Data' buttons to re-collect data")
        
        with col2:
            if st.button("🔍 Compare Data Sources", key="compare_data_sources_13"):
                self._show_data_source_comparison(api_data, db_data)
        
        with col3:
            if st.button("📊 Generate Discrepancy Report", key="generate_discrepancy_report_14"):
                self._generate_discrepancy_report(api_data, db_data, correlation_results)
    
    def _show_actionable_recommendations(self, results: Dict):
        """Show actionable recommendations based on analysis"""
        correlation_score = results.get('correlation_results', {}).get('correlation_score', 0)
        api_data = results.get('api_data', {})
        db_data = results.get('database_data', {})
        
        recommendations = []
        
        # Correlation-based recommendations
        if correlation_score < 0.3:
            recommendations.append({
                'priority': '🔴 High',
                'title': 'Critical Data Discrepancy',
                'description': 'Very low correlation indicates major data source issues',
                'actions': [
                    'Check API permissions and authentication',
                    'Verify database connection and table access',
                    'Review data filtering and query conditions',
                    'Consider re-running data collection'
                ]
            })
        elif correlation_score < 0.6:
            recommendations.append({
                'priority': '🟡 Medium',
                'title': 'Moderate Data Discrepancy',
                'description': 'Some discrepancies detected that should be investigated',
                'actions': [
                    'Review specific discrepancies listed above',
                    'Check for data filtering differences',
                    'Verify API and database access permissions',
                    'Consider data validation processes'
                ]
            })
        else:
            recommendations.append({
                'priority': '🟢 Low',
                'title': 'Good Data Correlation',
                'description': 'Data sources are reasonably consistent',
                'actions': [
                    'Continue monitoring data quality',
                    'Set up regular data validation',
                    'Document any minor discrepancies found'
                ]
            })
        
        # Data source specific recommendations
        api_summary = api_data.get('summary', {})
        api_items = api_summary.get('total_items', 0) if api_summary else 0
        db_items = len(db_data.get('modules', [])) + len(db_data.get('tables', [])) + len(db_data.get('properties', []))
        
        if api_items == 0:
            recommendations.append({
                'priority': '🔴 High',
                'title': 'No API Data Collected',
                'description': 'REST API returned no data',
                'actions': [
                    'Check API connection and authentication',
                    'Verify API permissions and roles',
                    'Review API endpoint accessibility',
                    'Test API connection manually'
                ]
            })
        
        if db_items == 0:
            recommendations.append({
                'priority': '🟡 Medium',
                'title': 'No Database Data Collected',
                'description': 'Database returned no data (normal for PostgreSQL)',
                'actions': [
                    'This is expected if using PostgreSQL instead of ServiceNow database',
                    'Consider using REST API as primary data source',
                    'Verify database connection is working'
                ]
            })
        
        # Display recommendations
        for i, rec in enumerate(recommendations):
            with st.expander(f"{rec['priority']} {rec['title']}", expanded=True):
                st.write(rec['description'])
                st.markdown("**Recommended Actions:**")
                for action in rec['actions']:
                    st.write(f"• {action}")
    
    def _show_data_validation_tools(self, results: Dict):
        """Show data validation and testing tools"""
        st.markdown("**🛠️ Available Tools**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🧪 Test API Connection", key="test_api_connection_15"):
                st.info("💡 Use the 'Test REST API Connection' button in the REST API tab")
            
            if st.button("🗄️ Test Database Connection", key="test_database_connection_16"):
                st.info("💡 Use the 'Test Database Connection' button in the Database tab")
        
        with col2:
            if st.button("📊 Validate Data Integrity", key="validate_data_integrity_17"):
                self._validate_data_integrity(results)
            
            if st.button("🔄 Force Data Refresh", key="force_data_refresh_18"):
                st.info("💡 Use the 'Populate & Save Data' buttons to refresh data")
        
        # Data export options
        st.markdown("##### 📥 Data Export")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Export Discrepancy Report", key="export_discrepancy_report_19"):
                self._export_discrepancy_report(results)
        
        with col2:
            if st.button("📊 Export Analysis Summary", key="export_analysis_summary_20"):
                self._export_analysis_summary(results)
    
    def _show_data_source_comparison(self, api_data: Dict, db_data: Dict):
        """Show detailed comparison between data sources"""
        st.markdown("##### 🔍 Data Source Comparison")
        
        # API data breakdown
        api_summary = api_data.get('summary', {})
        if api_summary:
            st.markdown("**🌐 REST API Data:**")
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Modules", api_summary.get('modules_count', 0))
            with col2:
                st.metric("Roles", api_summary.get('roles_count', 0))
            with col3:
                st.metric("Tables", api_summary.get('tables_count', 0))
            with col4:
                st.metric("Properties", api_summary.get('properties_count', 0))
            with col5:
                st.metric("Jobs", api_summary.get('scheduled_jobs_count', 0))
        
        # Database data breakdown
        st.markdown("**🗄️ Database Data:**")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Modules", len(db_data.get('modules', [])))
        with col2:
            st.metric("Tables", len(db_data.get('tables', [])))
        with col3:
            st.metric("Properties", len(db_data.get('properties', [])))
        with col4:
            st.metric("Roles", len(db_data.get('roles', [])))
    
    def _generate_discrepancy_report(self, api_data: Dict, db_data: Dict, correlation_results: Dict):
        """Generate a detailed discrepancy report"""
        st.markdown("##### 📊 Discrepancy Report")
        
        # Summary statistics
        matched_items = correlation_results.get('matched_items', 0)
        database_only = correlation_results.get('database_only', 0)
        api_only = correlation_results.get('api_only', 0)
        correlation_score = correlation_results.get('correlation_score', 0)
        
        st.write(f"**Correlation Score**: {correlation_score:.1%}")
        st.write(f"**Matched Items**: {matched_items}")
        st.write(f"**Database Only**: {database_only}")
        st.write(f"**API Only**: {api_only}")
        
        # Detailed discrepancies
        discrepancies = correlation_results.get('discrepancies', [])
        if discrepancies:
            st.markdown("**Detailed Discrepancies:**")
            for i, disc in enumerate(discrepancies[:20]):  # Show first 20
                st.write(f"{i+1}. {disc.get('description', 'No description')}")
        else:
            st.info("No specific discrepancies identified")
    
    def _validate_data_integrity(self, results: Dict):
        """Validate data integrity across sources"""
        st.markdown("##### 🔍 Data Integrity Validation")
        
        api_data = results.get('api_data', {})
        db_data = results.get('database_data', {})
        
        # Check for required fields
        validation_results = []
        
        # API data validation
        api_summary = api_data.get('summary', {})
        if api_summary:
            if api_summary.get('total_items', 0) > 0:
                validation_results.append("✅ API data collection successful")
            else:
                validation_results.append("❌ API data collection failed")
        else:
            validation_results.append("❌ No API summary available")
        
        # Database data validation
        db_items = len(db_data.get('modules', [])) + len(db_data.get('tables', [])) + len(db_data.get('properties', []))
        if db_items > 0:
            validation_results.append("✅ Database data collection successful")
        else:
            validation_results.append("ℹ️ No database data (normal for PostgreSQL)")
        
        # Display results
        for result in validation_results:
            st.write(result)
    
    def _export_discrepancy_report(self, results: Dict):
        """Export discrepancy report as downloadable file"""
        import json
        from datetime import datetime
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'correlation_score': results.get('correlation_results', {}).get('correlation_score', 0),
            'discrepancies': results.get('correlation_results', {}).get('discrepancies', []),
            'summary': results.get('summary', {}),
            'api_data_summary': results.get('api_data', {}).get('summary', {}),
            'database_data_summary': {
                'modules_count': len(results.get('database_data', {}).get('modules', [])),
                'tables_count': len(results.get('database_data', {}).get('tables', [])),
                'properties_count': len(results.get('database_data', {}).get('properties', []))
            }
        }
        
        json_data = json.dumps(report, indent=2, default=str)
        st.download_button(
            label="💾 Download Discrepancy Report",
            data=json_data,
            file_name=f"discrepancy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    def _export_analysis_summary(self, results: Dict):
        """Export analysis summary as downloadable file"""
        import json
        from datetime import datetime
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'analysis_type': 'hybrid_introspection',
            'correlation_score': results.get('correlation_results', {}).get('correlation_score', 0),
            'total_items': results.get('summary', {}).get('total_items', 0),
            'api_items': results.get('api_data', {}).get('summary', {}).get('total_items', 0),
            'database_items': len(results.get('database_data', {}).get('modules', [])) + 
                            len(results.get('database_data', {}).get('tables', [])) + 
                            len(results.get('database_data', {}).get('properties', [])),
            'recommendations': self._generate_recommendations_summary(results)
        }
        
        json_data = json.dumps(summary, indent=2, default=str)
        st.download_button(
            label="💾 Download Analysis Summary",
            data=json_data,
            file_name=f"analysis_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )
    
    def _generate_recommendations_summary(self, results: Dict):
        """Generate recommendations summary for export"""
        correlation_score = results.get('correlation_results', {}).get('correlation_score', 0)
        
        if correlation_score < 0.3:
            return ["Critical data discrepancy detected", "Check API and database connections", "Review data collection processes"]
        elif correlation_score < 0.6:
            return ["Moderate data discrepancy detected", "Investigate specific discrepancies", "Consider data validation"]
        else:
            return ["Good data correlation", "Continue monitoring", "Set up regular validation"]
    
    def _save_hybrid_results(self, results: Dict):
        """Save hybrid results to database"""
        try:
            with st.spinner("Saving results to database..."):
                # Save modules
                for module in results.get('database_data', {}).get('modules', []):
                    self.db_manager.save_module(module)
                
                # Save roles
                for role in results.get('database_data', {}).get('roles', []):
                    # Find or create module for role
                    module = self.db_manager.save_module({'name': 'Hybrid Module', 'label': 'Hybrid Module'})
                    self.db_manager.save_role(role, module.id)
                
                st.success("✅ Results saved to database successfully!")
        
        except Exception as e:
            st.error(f"❌ Error saving results: {str(e)}")
    
    def _save_rest_api_config(self, instance_url: str, username: str, password: str, timeout: int):
        """Save REST API configuration to database"""
        try:
            if not instance_url or not username or not password:
                st.error("❌ Please fill in all required fields (Instance URL, Username, Password)")
                return
            
            # Save to centralized configuration
            from centralized_db_config import get_centralized_db_config
            centralized_config = get_centralized_db_config()
            
            config_data = {
                'name': 'hybrid_rest_api',
                'instance_url': instance_url,
                'username': username,
                'password': password,
                'api_version': 'v2',
                'timeout': timeout,
                'max_retries': 3,
                'verify_ssl': True,
                'is_active': True
            }
            
            if centralized_config.save_servicenow_configuration(config_data):
                st.success("✅ REST API configuration saved successfully!")
            else:
                st.error("❌ Failed to save REST API configuration")
                
        except Exception as e:
            st.error(f"❌ Error saving REST API configuration: {e}")
    
    def _populate_and_save_rest_api_data(self, instance_url: str, username: str, password: str, timeout: int):
        """Populate and save REST API data to database"""
        try:
            if not instance_url or not username or not password:
                st.error("❌ Please fill in all required fields (Instance URL, Username, Password)")
                return
            
            with st.spinner("🔄 Populating and saving REST API data..."):
                # Test connection first
                if not self._test_rest_api_connection(instance_url, username, password, timeout):
                    return
                
                # Save configuration
                self._save_rest_api_config(instance_url, username, password, timeout)
                
                # Populate data
                from servicenow_api_client import ServiceNowAPIClient
                api_client = ServiceNowAPIClient(instance_url, username, password)
                
                # Get basic data
                modules = api_client.get_modules()
                roles = api_client.get_roles()
                tables = api_client.get_tables()
                
                # Save to database
                session = self.db_manager.get_session()
                try:
                    # Save modules
                    for module_data in modules:
                        # Check if module exists
                        existing_module = session.query(ServiceNowModule).filter_by(
                            name=module_data['name']
                        ).first()
                        
                        if not existing_module:
                            module = ServiceNowModule(
                                name=module_data['name'],
                                label=module_data.get('label', ''),
                                description=module_data.get('description', ''),
                                is_active=True
                            )
                            session.add(module)
                    
                    # Save roles
                    for role_data in roles:
                        existing_role = session.query(self.db_manager.ServiceNowRole).filter_by(
                            name=role_data['name']
                        ).first()
                        
                        if not existing_role:
                            role = self.db_manager.ServiceNowRole(
                                name=role_data['name'],
                                label=role_data.get('label', ''),
                                description=role_data.get('description', ''),
                                is_active=True
                            )
                            session.add(role)
                    
                    session.commit()
                    st.success("✅ REST API data populated and saved successfully!")
                    
                finally:
                    session.close()
                    
        except Exception as e:
            st.error(f"❌ Error populating REST API data: {e}")
    
    def _save_database_config(self, db_type: str, host: str, port: int, database: str, db_username: str, db_password: str):
        """Save database configuration to database"""
        try:
            if not host or not database or not db_username or not db_password:
                st.error("❌ Please fill in all required fields (Host, Database, Username, Password)")
                return
            
            # Save to centralized configuration
            from centralized_db_config import get_centralized_db_config
            centralized_config = get_centralized_db_config()
            
            # Convert database type to lowercase for consistency
            db_type_lower = db_type.lower().replace(' ', '_')
            
            config_data = {
                'name': 'hybrid_database',
                'db_type': db_type_lower,
                'host': host,
                'port': port,
                'database_name': database,
                'username': db_username,
                'password': db_password,
                'connection_pool_size': 10,
                'max_overflow': 20,
                'echo': False,
                'is_active': True
            }
            
            if centralized_config.save_database_configuration(config_data):
                st.success("✅ Database configuration saved successfully!")
            else:
                st.error("❌ Failed to save database configuration")
                
        except Exception as e:
            st.error(f"❌ Error saving database configuration: {e}")
    
    def _populate_and_save_database_data(self, db_type: str, host: str, port: int, database: str, db_username: str, db_password: str):
        """Populate and save database data"""
        try:
            if not host or not database or not db_username or not db_password:
                st.error("❌ Please fill in all required fields (Host, Database, Username, Password)")
                return
            
            with st.spinner("🔄 Populating and saving database data..."):
                # Test connection first
                if not self._test_database_connection(db_type, host, port, database, db_username, db_password):
                    return
                
                # Save configuration
                self._save_database_config(db_type, host, port, database, db_username, db_password)
                
                # Build connection string
                db_type_lower = db_type.lower().replace(' ', '_')
                if db_type_lower == 'postgresql':
                    connection_string = f"postgresql://user:password@host:port/database"
                elif db_type_lower == 'mysql':
                    connection_string = f"mysql+pymysql://user:password@host:port/database"
                else:
                    st.error(f"❌ Unsupported database type: {db_type}")
                    return
                
                # Use database connector to get data
                connector = ServiceNowDatabaseConnector(db_connection_string=connection_string)
                
                # Get basic data
                tables = connector.get_tables()
                modules = connector.get_modules()
                
                # Save to our database
                session = self.db_manager.get_session()
                try:
                    # Save tables
                    for table_data in tables:
                        existing_table = session.query(ServiceNowTable).filter_by(
                            name=table_data['name']
                        ).first()
                        
                        if not existing_table:
                            table = ServiceNowTable(
                                name=table_data['name'],
                                label=table_data.get('label', ''),
                                description=table_data.get('description', ''),
                                is_active=True
                            )
                            session.add(table)
                    
                    session.commit()
                    st.success("✅ Database data populated and saved successfully!")
                    
                finally:
                    session.close()
                    
        except Exception as e:
            st.error(f"❌ Error populating database data: {e}")
    
    def _save_hybrid_config(self, api_enabled: bool, db_enabled: bool, correlation_enabled: bool, 
                           validation_enabled: bool, rate_limiting: bool, api_timeout: int, db_timeout: int):
        """Save hybrid configuration to database"""
        try:
            from centralized_db_config import get_centralized_db_config
            centralized_config = get_centralized_db_config()
            
            # Save hybrid configuration as a JSON configuration
            config_data = {
                'name': 'hybrid_mode',
                'api_enabled': api_enabled,
                'db_enabled': db_enabled,
                'correlation_enabled': correlation_enabled,
                'validation_enabled': validation_enabled,
                'rate_limiting': rate_limiting,
                'api_timeout': api_timeout,
                'db_timeout': db_timeout,
                'is_active': True,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            # Save to centralized database
            config_data['name'] = 'hybrid_mode'
            centralized_config.save_servicenow_configuration(config_data)
            
            # Also save to session state for immediate access
            st.session_state.hybrid_config = config_data
            st.success("✅ Hybrid configuration saved successfully!")
            
        except Exception as e:
            st.error(f"❌ Error saving hybrid configuration: {e}")
    
    def _load_hybrid_configuration(self):
        """Load saved hybrid configuration from database"""
        try:
            from centralized_db_config import get_centralized_db_config
            centralized_config = get_centralized_db_config()
            
            # Get saved hybrid configuration
            hybrid_config = centralized_config.get_servicenow_configuration('hybrid_mode')
            
            if hybrid_config:
                st.success("✅ Hybrid configuration loaded successfully!")
                
                # Display loaded configuration
                st.markdown("#### 📋 Loaded Configuration")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**REST API Settings**")
                    st.write(f"**API Enabled:** {hybrid_config.get('api_enabled', False)}")
                    st.write(f"**API Timeout:** {hybrid_config.get('api_timeout', 30)} seconds")
                
                with col2:
                    st.markdown("**Database Settings**")
                    st.write(f"**Database Enabled:** {hybrid_config.get('db_enabled', False)}")
                    st.write(f"**Database Timeout:** {hybrid_config.get('db_timeout', 30)} seconds")
                
                st.markdown("**Advanced Options**")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Data Correlation:** {hybrid_config.get('correlation_enabled', False)}")
                
                with col2:
                    st.write(f"**Security Validation:** {hybrid_config.get('validation_enabled', False)}")
                
                with col3:
                    st.write(f"**Rate Limiting:** {hybrid_config.get('rate_limiting', False)}")
                
                # Show metadata
                metadata = hybrid_config.get('metadata', {})
                if metadata:
                    st.markdown("**Configuration Details**")
                    st.write(f"**Created:** {metadata.get('created_at', 'N/A')}")
                    st.write(f"**Last Updated:** {metadata.get('updated_at', 'N/A')}")
                
                # Option to apply configuration
                if st.button("🔄 Apply This Configuration", key="apply_this_configuration_21"):
                    self._apply_loaded_configuration(hybrid_config)
                    
            else:
                st.warning("⚠️ No hybrid configuration found in database. Please save a configuration first.")
                
        except Exception as e:
            st.error(f"❌ Error loading hybrid configuration: {e}")
    
    def _apply_loaded_configuration(self, config_data: dict):
        """Apply loaded configuration to session state"""
        try:
            # Store configuration in session state for form population
            st.session_state.loaded_hybrid_config = {
                'api_enabled': config_data.get('api_enabled', True),
                'db_enabled': config_data.get('db_enabled', True),
                'correlation_enabled': config_data.get('correlation_enabled', True),
                'validation_enabled': config_data.get('validation_enabled', True),
                'rate_limiting': config_data.get('rate_limiting', True),
                'api_timeout': config_data.get('api_timeout', 30),
                'db_timeout': config_data.get('db_timeout', 30)
            }
            
            st.success("✅ Configuration applied! The form will be populated with these settings on the next page refresh.")
            st.info("💡 Refresh the page to see the loaded configuration in the form fields.")
            
        except Exception as e:
            st.error(f"❌ Error applying configuration: {e}")
    
    def _populate_and_save_hybrid_data(self, api_enabled: bool, db_enabled: bool, correlation_enabled: bool, 
                                      validation_enabled: bool, rate_limiting: bool, api_timeout: int, db_timeout: int, force_update: bool = False):
        """Populate and save hybrid data to database"""
        try:
            with st.spinner("🔄 Populating and saving hybrid data to database..."):
                # Save configuration first
                self._save_hybrid_config(api_enabled, db_enabled, correlation_enabled, 
                                       validation_enabled, rate_limiting, api_timeout, db_timeout)
                
                # Start hybrid introspection to collect data
                self._start_hybrid_introspection(
                    api_enabled, db_enabled, correlation_enabled, 
                    validation_enabled, rate_limiting, api_timeout, db_timeout, force_update
                )
                
                # Save collected data to database
                if hasattr(st.session_state, 'hybrid_introspection_results') and st.session_state.hybrid_introspection_results:
                    self._save_hybrid_data_to_database(st.session_state.hybrid_introspection_results, force_update)
                    
                    # Show success message (the method handles its own error reporting)
                    st.success("✅ Hybrid data populated and saved to database successfully!")
                else:
                    st.warning("⚠️ No data collected to save. Please ensure connections are working.")
                
        except Exception as e:
            st.error(f"❌ Error populating hybrid data: {e}")
    
    def _save_hybrid_data_to_database(self, hybrid_data: dict, force_update: bool = False):
        """Save hybrid introspection data to database"""
        try:
            from centralized_db_config import get_centralized_db_config
            centralized_config = get_centralized_db_config()
            
            # Prepare data for database storage
            data_to_save = {
                'name': 'hybrid_introspection_data',
                'data_type': 'hybrid_introspection',
                'summary': hybrid_data.get('summary', {}),
                'tables': hybrid_data.get('tables', []),
                'apis': hybrid_data.get('apis', []),
                'correlations': hybrid_data.get('correlations', []),
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'data_source': 'hybrid_introspection',
                    'total_items': hybrid_data.get('summary', {}).get('total_items', 0),
                    'correlation_score': hybrid_data.get('summary', {}).get('correlation_score', 0)
                },
                'is_active': True
            }
            
            # Save to centralized database
            data_to_save['name'] = 'hybrid_introspection_data'
            centralized_config.save_servicenow_configuration(data_to_save)
            
            # Also save individual components for easier access
            if hybrid_data.get('tables'):
                tables_data = {
                    'name': 'hybrid_tables_data',
                    'data_type': 'tables',
                    'tables': hybrid_data['tables'],
                    'created_at': datetime.now().isoformat(),
                    'is_active': True
                }
                centralized_config.save_servicenow_configuration(tables_data)
            
            if hybrid_data.get('apis'):
                apis_data = {
                    'name': 'hybrid_apis_data',
                    'data_type': 'apis',
                    'apis': hybrid_data['apis'],
                    'created_at': datetime.now().isoformat(),
                    'is_active': True
                }
                centralized_config.save_servicenow_configuration(apis_data)
            
            if hybrid_data.get('correlations'):
                correlations_data = {
                    'name': 'hybrid_correlations_data',
                    'data_type': 'correlations',
                    'correlations': hybrid_data['correlations'],
                    'created_at': datetime.now().isoformat(),
                    'is_active': True
                }
                centralized_config.save_servicenow_configuration(correlations_data)
            
            st.info(f"💾 Saved {data_to_save['metadata']['total_items']} items to database")
            
        except Exception as e:
            st.error(f"❌ Error saving hybrid data to database: {e}")
    
    def show_footer(self):
        """Show footer with creator information"""
        st.markdown("""
        <div style="position: fixed; bottom: 0; left: 0; right: 0; background-color: #f8f9fa; border-top: 1px solid #dee2e6; padding: 10px 20px; text-align: center; font-size: 0.9rem; color: #6c757d; z-index: 1000;">
            Created By: <strong>Ashish Gautam</strong> | 
            <a href="https://www.linkedin.com/in/ashishgautamkarn/" target="_blank" style="color: #007bff; text-decoration: none;">LinkedIn Profile</a>
        </div>
        """, unsafe_allow_html=True)

# Created By: Ashish Gautam; LinkedIn: https://www.linkedin.com/in/ashishgautamkarn/
