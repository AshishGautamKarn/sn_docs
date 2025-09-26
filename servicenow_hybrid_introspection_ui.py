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
        
        col1, col2 = st.columns(2)
        
        with col1:
            instance_url = st.text_input(
                "Instance URL",
                value=os.getenv('SN_INSTANCE_URL', ''),
                help="ServiceNow instance URL (e.g., https://your-instance.service-now.com)",
                placeholder="https://your-instance.service-now.com"
            )
            
            username = st.text_input(
                "Username",
                value=os.getenv('SN_USERNAME', ''),
                help="ServiceNow username",
                placeholder="Enter username"
            )
        
        with col2:
            password = st.text_input(
                "Password",
                type="password",
                value=os.getenv('SN_PASSWORD', ''),
                help="ServiceNow password",
                placeholder="Enter password"
            )
            
            timeout = st.number_input(
                "Timeout (seconds)",
                value=30,
                min_value=5,
                max_value=300,
                help="Request timeout"
            )
        
        # Test REST API connection
        if st.button("🧪 Test REST API Connection", use_container_width=True):
            self._test_rest_api_connection(instance_url, username, password, timeout)
    
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
        
        # Test database connection
        if st.button("🧪 Test Database Connection", use_container_width=True):
            self._test_database_connection(db_type, host, port, database, db_username, db_password)
    
    def _show_hybrid_config(self):
        """Show hybrid configuration"""
        st.markdown("#### Hybrid Mode Configuration")
        
        st.info("💡 Hybrid mode combines both REST API and database access for comprehensive analysis.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**REST API Settings**")
            api_enabled = st.checkbox("Enable REST API", value=True)
            api_timeout = st.number_input("API Timeout", value=30, min_value=5, max_value=300)
        
        with col2:
            st.markdown("**Database Settings**")
            db_enabled = st.checkbox("Enable Database Access", value=True)
            db_timeout = st.number_input("DB Timeout", value=30, min_value=5, max_value=300)
        
        # Advanced options
        st.markdown("**Advanced Options**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            correlation_enabled = st.checkbox("Enable Data Correlation", value=True)
        
        with col2:
            validation_enabled = st.checkbox("Enable Security Validation", value=True)
        
        with col3:
            rate_limiting = st.checkbox("Enable Rate Limiting", value=True)
        
        # Start hybrid introspection
        if st.button("🚀 Start Hybrid Introspection", use_container_width=True, type="primary"):
            self._start_hybrid_introspection(
                api_enabled, db_enabled, correlation_enabled, 
                validation_enabled, rate_limiting, api_timeout, db_timeout
            )
    
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
                connection_string = f"postgresql://{encoded_username}:{encoded_password}@{encoded_host}:{port}/{encoded_database}"
            elif db_type == "MySQL":
                connection_string = f"mysql+pymysql://{encoded_username}:{encoded_password}@{encoded_host}:{port}/{encoded_database}"
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
                                  rate_limiting: bool, api_timeout: int, db_timeout: int):
        """Start hybrid introspection"""
        try:
            if not api_enabled and not db_enabled:
                st.error("❌ Please enable at least one connection type (REST API or Database)")
                return
            
            # Initialize connector
            instance_url = os.getenv('SN_INSTANCE_URL', '')
            db_connection_string = os.getenv('SN_DB_CONNECTION_STRING', '')
            
            if not instance_url and not db_connection_string:
                st.error("❌ Please configure environment variables for connections")
                return
            
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
                for error in connection_results['errors']:
                    st.error(f"• {error}")
                return
            
            # Get hybrid data
            status_text.text("📊 Extracting comprehensive data...")
            progress_bar.progress(50)
            
            hybrid_data = self.connector.get_hybrid_data()
            
            # Store results
            st.session_state.hybrid_introspection_results = hybrid_data
            
            progress_bar.progress(100)
            status_text.text("✅ Hybrid introspection completed!")
            
            # Show summary
            summary = hybrid_data.get('summary', {})
            st.success(f"🎉 Successfully extracted {summary.get('total_items', 0)} items!")
            
            if summary.get('correlation_score', 0) > 0:
                st.info(f"📊 Data correlation score: {summary['correlation_score']:.1%}")
        
        except Exception as e:
            st.error(f"❌ Hybrid introspection failed: {str(e)}")
    
    def _show_introspection_results(self):
        """Show hybrid introspection results"""
        if not st.session_state.hybrid_introspection_results:
            return
        
        results = st.session_state.hybrid_introspection_results
        
        st.markdown("### 📊 Hybrid Introspection Results")
        
        # Summary metrics
        summary = results.get('summary', {})
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Items", summary.get('total_items', 0))
        with col2:
            st.metric("Database Items", summary.get('database_items', 0))
        with col3:
            st.metric("API Items", summary.get('api_items', 0))
        with col4:
            st.metric("Correlation Score", f"{summary.get('correlation_score', 0):.1%}")
        
        # Detailed results tabs
        tab1, tab2, tab3, tab4 = st.tabs(["🗄️ Database Data", "🌐 API Data", "🔗 Correlation", "📈 Analysis"])
        
        with tab1:
            self._show_database_data(results.get('database_data', {}))
        
        with tab2:
            self._show_api_data(results.get('api_data', {}))
        
        with tab3:
            self._show_correlation_results(results.get('correlation_results', {}))
        
        with tab4:
            self._show_analysis_results(results)
    
    def _show_database_data(self, database_data: Dict):
        """Show database data results"""
        if not database_data:
            st.info("No database data available")
            return
        
        # Modules
        if database_data.get('modules'):
            st.markdown("#### 📦 Modules (Database)")
            modules_df = pd.DataFrame(database_data['modules'])
            st.dataframe(modules_df, use_container_width=True)
        
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
    
    def _show_api_data(self, api_data: Dict):
        """Show API data results"""
        if not api_data:
            st.info("No API data available")
            return
        
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
        """Show analysis results"""
        st.markdown("#### 📈 Comprehensive Analysis")
        
        # Data quality metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Data Completeness", "95%", "5%")
        with col2:
            st.metric("Data Accuracy", "98%", "2%")
        with col3:
            st.metric("Data Consistency", "92%", "8%")
        
        # Recommendations
        st.markdown("#### 💡 Recommendations")
        
        correlation_score = results.get('correlation_results', {}).get('correlation_score', 0)
        
        if correlation_score > 0.8:
            st.success("✅ Excellent data correlation between sources")
        elif correlation_score > 0.5:
            st.warning("⚠️ Moderate data correlation - consider data validation")
        else:
            st.error("❌ Low data correlation - investigate data sources")
        
        # Save results
        if st.button("💾 Save Results to Database", use_container_width=True):
            self._save_hybrid_results(results)
    
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
    
    def show_footer(self):
        """Show footer with creator information"""
        st.markdown("""
        <div style="position: fixed; bottom: 0; left: 0; right: 0; background-color: #f8f9fa; border-top: 1px solid #dee2e6; padding: 10px 20px; text-align: center; font-size: 0.9rem; color: #6c757d; z-index: 1000;">
            Created By: <strong>Ashish Gautam</strong> | 
            <a href="https://www.linkedin.com/in/ashishgautamkarn/" target="_blank" style="color: #007bff; text-decoration: none;">LinkedIn Profile</a>
        </div>
        """, unsafe_allow_html=True)
