"""
ServiceNow Instance Introspection UI
Allows connecting to ServiceNow instances via REST API and extracting comprehensive data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from servicenow_api_client import ServiceNowAPIClient
from database import DatabaseManager
from configuration_ui import ConfigurationManager
from typing import Dict, List, Any
import time
from datetime import datetime


class ServiceNowInstanceIntrospectionUI:
    """UI for ServiceNow instance introspection via REST API"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.api_client = None
        self.config_manager = ConfigurationManager()
        
        # Initialize session state for introspection results
        if 'servicenow_introspection_results' not in st.session_state:
            st.session_state.servicenow_introspection_results = {}
    
    def show_introspection_interface(self):
        """Show the main ServiceNow instance introspection interface"""
        st.markdown('<h2 class="section-header">🔍 ServiceNow Instance Introspection</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        This tool allows you to connect to ServiceNow instances via REST API and extract comprehensive data including:
        - **Modules**: All ServiceNow applications and modules
        - **Roles**: User roles and permissions
        - **Tables**: Database tables and their structures
        - **System Properties**: Configuration properties and values
        - **Scheduled Jobs**: Automated jobs and their schedules
        
        **Authentication**: Uses ServiceNow username/password for REST API access
        """)
        
        # Connection configuration
        self._show_connection_config()
        
        # Introspection results
        if st.session_state.servicenow_introspection_results:
            self._show_introspection_results()
        
        # Show footer
        self.show_footer()
    
    def _load_servicenow_configuration(self) -> Dict[str, Any]:
        """Load ServiceNow configuration from database first, then fall back to config files"""
        try:
            # Try to load from database first
            db_config = self.db_manager.get_servicenow_configuration('default')
            if db_config:
                # db_config is already a dictionary from centralized config
                config_dict = db_config.copy()
                config_dict['_source'] = 'database'
                return config_dict
        except Exception as e:
            st.warning(f"⚠️ Could not load from database: {str(e)}")
        
        # Fall back to config files
        try:
            file_config = self.config_manager.get_servicenow_config()
            if file_config.get('instance_url') and file_config.get('username'):
                file_config['_source'] = 'Configuration page'
                return file_config
        except Exception as e:
            st.warning(f"⚠️ Could not load from config files: {str(e)}")
        
        # Return empty config if nothing found
        return {
            'instance_url': '',
            'username': '',
            'password': '',
            'timeout': 30,
            'max_retries': 3,
            'api_version': 'v2',
            'verify_ssl': True,
            '_source': 'none'
        }
    
    def _show_connection_config(self):
        """Show ServiceNow instance connection configuration"""
        st.markdown("### 🔗 ServiceNow Instance Connection")
        
        # Load ServiceNow configuration from database first, then fall back to config files
        servicenow_config = self._load_servicenow_configuration()
        
        # Show configuration status
        col_status, col_refresh = st.columns([3, 1])
        
        with col_status:
            if servicenow_config.get('instance_url') and servicenow_config.get('username'):
                config_source = servicenow_config.get('_source', 'Configuration page')
                st.success(f"✅ Using saved ServiceNow configuration from {config_source}")
                st.info(f"**Instance**: {servicenow_config.get('instance_url', 'Not configured')}")
                st.info(f"**Username**: {servicenow_config.get('username', 'Not configured')}")
            else:
                st.warning("⚠️ No ServiceNow configuration found. Please configure in Configuration page first.")
        
        with col_refresh:
            if st.button("🔄 Refresh Config", help="Reload configuration from database and Configuration page"):
                self.config_manager.load_config()
                st.success("✅ Configuration refreshed!")
                st.rerun()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Instance Details")
            instance_url = st.text_input(
                "ServiceNow Instance URL",
                value=servicenow_config.get('instance_url', 'https://your-instance.service-now.com'),
                help="Full URL of your ServiceNow instance (e.g., https://dev12345.service-now.com)",
                placeholder="https://your-instance.service-now.com"
            )
            
            # Validate URL format
            if instance_url and not instance_url.startswith('https://'):
                st.warning("⚠️ URL should start with https://")
            
            # Connection options
            st.markdown("#### Connection Options")
            timeout = st.number_input(
                "Request Timeout (seconds)",
                value=servicenow_config.get('timeout', 30),
                min_value=5,
                max_value=300,
                help="Timeout for API requests"
            )
            
            max_requests = st.number_input(
                "Max Concurrent Requests",
                value=5,
                min_value=1,
                max_value=20,
                help="Maximum number of concurrent API requests"
            )
        
        with col2:
            st.markdown("#### Authentication")
            username = st.text_input(
                "Username",
                value=servicenow_config.get('username', ''),
                help="ServiceNow username (e.g., admin, your-username)",
                placeholder="Enter ServiceNow username"
            )
            
            password = st.text_input(
                "Password",
                value=servicenow_config.get('password', ''),
                type="password",
                help="ServiceNow password",
                placeholder="Enter ServiceNow password"
            )
            
            # Additional options
            st.markdown("#### Data Options")
            include_inactive = st.checkbox(
                "Include Inactive Items",
                value=False,
                help="Include inactive modules, roles, tables, etc."
            )
            
            detailed_fields = st.checkbox(
                "Get Detailed Field Information",
                value=False,
                help="Retrieve detailed field information for tables (slower)"
            )
        
        # Connection string preview
        st.markdown("#### 🔗 Connection Preview")
        if instance_url and username:
            preview_info = f"**Instance**: {instance_url}\n"
            preview_info += f"**Username**: {username}\n"
            preview_info += f"**Authentication**: Basic Auth (REST API)\n"
            preview_info += f"**Include Inactive**: {'Yes' if include_inactive else 'No'}\n"
            preview_info += f"**Detailed Fields**: {'Yes' if detailed_fields else 'No'}"
            st.info(preview_info)
        else:
            st.info("Fill in Instance URL and Username to see connection preview")
        
        # Test and connect buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧪 Test Connection", use_container_width=True):
                self._test_connection(instance_url, username, password, timeout)
        
        with col2:
            if st.button("🔍 Start Introspection", use_container_width=True):
                self._start_introspection(instance_url, username, password, timeout, max_requests, include_inactive, detailed_fields)
        
        with col3:
            if st.button("💾 Save to Database", use_container_width=True):
                self._save_introspection_results()
        
        # Clear results button (only show if there are results)
        if st.session_state.servicenow_introspection_results:
            st.markdown("---")
            if st.button("🗑️ Clear Results", use_container_width=True, type="secondary"):
                st.session_state.servicenow_introspection_results = {}
                st.rerun()
    
    def _test_connection(self, instance_url: str, username: str, password: str, timeout: int):
        """Test ServiceNow instance connection"""
        try:
            # Validate inputs
            if not instance_url or not username or not password:
                st.error("❌ Please fill in all required fields (Instance URL, Username, Password)")
                return
            
            # Clean up URL
            instance_url = instance_url.rstrip('/')
            if not instance_url.startswith('https://'):
                instance_url = f"https://{instance_url}"
            
            # Test connection
            with st.spinner("Testing connection..."):
                api_client = ServiceNowAPIClient(instance_url, username, password)
                result = api_client.test_connection()
            
            if result['success']:
                st.success("✅ Connection successful!")
                st.info(f"**Instance**: {result['instance_url']}")
                st.info(f"**Response Time**: {result['response_time']:.2f} seconds")
                
                # Store successful client for later use
                self.api_client = api_client
            else:
                st.error(f"❌ Connection failed: {result['message']}")
                if 'error' in result:
                    st.error(f"**Error Details**: {result['error']}")
                
                # Provide specific guidance for common errors
                if '401' in str(result.get('error', '')) or 'Unauthorized' in str(result.get('error', '')):
                    st.warning("""
                    **Authentication Issue Detected:**
                    - Check your ServiceNow username and password
                    - Ensure the user has REST API access permissions
                    - Verify the user account is active
                    - Try using 'admin' username if testing with a developer instance
                    """)
                elif '404' in str(result.get('error', '')):
                    st.warning("""
                    **Instance Not Found:**
                    - Verify the ServiceNow instance URL is correct
                    - Ensure the instance is accessible from your network
                    - Check if the instance URL includes the correct domain
                    """)
                
                # Show troubleshooting tips
                st.error("💡 Troubleshooting tips:")
                st.error("• Check if the instance URL is correct")
                st.error("• Verify username and password")
                st.error("• Ensure the instance is accessible from your network")
                st.error("• Check if REST API access is enabled")
                st.error("• Verify user has necessary permissions")
            
        except Exception as e:
            st.error(f"❌ Connection test failed: {e}")
    
    def _start_introspection(self, instance_url: str, username: str, password: str, timeout: int, max_requests: int, include_inactive: bool, detailed_fields: bool):
        """Start ServiceNow instance introspection"""
        try:
            # Validate inputs
            if not instance_url or not username or not password:
                st.error("❌ Please fill in all required fields (Instance URL, Username, Password)")
                return
            
            # Clean up URL
            instance_url = instance_url.rstrip('/')
            if not instance_url.startswith('https://'):
                instance_url = f"https://{instance_url}"
            
            # Initialize API client
            self.api_client = ServiceNowAPIClient(instance_url, username, password)
            
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Test connection first
            status_text.text("🔍 Testing connection...")
            progress_bar.progress(10)
            
            connection_test = self.api_client.test_connection()
            if not connection_test['success']:
                st.error(f"❌ Connection failed: {connection_test['message']}")
                return
            
            # Get comprehensive data
            status_text.text("📊 Extracting comprehensive data...")
            progress_bar.progress(30)
            
            comprehensive_data = self.api_client.get_comprehensive_data()
            
            # Store results in session state
            st.session_state.servicenow_introspection_results = comprehensive_data
            
            progress_bar.progress(100)
            status_text.text("✅ Introspection completed!")
            
            summary = comprehensive_data['summary']
            st.success(f"🎉 Successfully introspected ServiceNow instance!")
            st.info(f"**Total Items**: {summary['total_items']}")
            st.info(f"**Modules**: {summary['modules_count']}")
            st.info(f"**Roles**: {summary['roles_count']}")
            st.info(f"**Tables**: {summary['tables_count']}")
            st.info(f"**Properties**: {summary['properties_count']}")
            st.info(f"**Scheduled Jobs**: {summary['scheduled_jobs_count']}")
            
            # Show warning if modules are 0 but other data exists
            if summary['modules_count'] == 0 and summary['total_items'] > 0:
                st.warning("""
                ⚠️ **No modules found** - This could indicate:
                - Authentication issues with the sys_app table
                - User lacks permissions to access application data
                - Instance has no applications installed
                - Try using admin credentials or check user permissions
                """)
            
        except Exception as e:
            st.error(f"❌ Introspection failed: {e}")
            st.exception(e)
    
    def _show_introspection_results(self):
        """Show ServiceNow instance introspection results"""
        if not st.session_state.servicenow_introspection_results:
            return
        
        st.markdown("### 📊 Introspection Results")
        
        # Instance info
        instance_info = st.session_state.servicenow_introspection_results['instance_info']
        st.markdown(f"**Instance**: {instance_info['instance_url']}")
        st.markdown(f"**Version**: {instance_info['version']}")
        st.markdown(f"**Build**: {instance_info['build_name']} ({instance_info['build_tag']})")
        st.markdown(f"**Introspected**: {instance_info['introspected_at']}")
        
        # Summary metrics
        summary = st.session_state.servicenow_introspection_results['summary']
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Modules", summary['modules_count'])
        with col2:
            st.metric("Roles", summary['roles_count'])
        with col3:
            st.metric("Tables", summary['tables_count'])
        with col4:
            st.metric("Properties", summary['properties_count'])
        with col5:
            st.metric("Scheduled Jobs", summary['scheduled_jobs_count'])
        
        # Detailed results tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Modules", "Roles", "Tables", "Properties", "Scheduled Jobs"])
        
        with tab1:
            self._show_modules_results()
        
        with tab2:
            self._show_roles_results()
        
        with tab3:
            self._show_tables_results()
        
        with tab4:
            self._show_properties_results()
        
        with tab5:
            self._show_scheduled_jobs_results()
    
    def _show_modules_results(self):
        """Show modules introspection results"""
        modules = st.session_state.servicenow_introspection_results['modules']
        
        if not modules:
            st.info("No modules found.")
            return
        
        module_data = []
        for module in modules:
            module_data.append({
                'Name': module['name'],
                'Label': module['label'],
                'Description': module['description'],
                'Version': module['version'],
                'Active': module['active'],
                'Scope': module['scope']
            })
        
        df = pd.DataFrame(module_data)
        st.dataframe(df, use_container_width=True)
        
        # Module distribution chart
        if len(module_data) > 0:
            active_count = df['Active'].sum()
            inactive_count = len(df) - active_count
            
            fig = px.pie(values=[active_count, inactive_count], 
                        names=['Active', 'Inactive'],
                        title="Module Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_roles_results(self):
        """Show roles introspection results"""
        roles = st.session_state.servicenow_introspection_results['roles']
        
        if not roles:
            st.info("No roles found.")
            return
        
        role_data = []
        for role in roles:
            role_data.append({
                'Name': role['name'],
                'Description': role['description'],
                'Active': role['active'],
                'Grantable': role['grantable']
            })
        
        df = pd.DataFrame(role_data)
        st.dataframe(df, use_container_width=True)
        
        # Role distribution chart
        if len(role_data) > 0:
            active_count = df['Active'].sum()
            inactive_count = len(df) - active_count
            
            fig = px.pie(values=[active_count, inactive_count], 
                        names=['Active', 'Inactive'],
                        title="Role Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_tables_results(self):
        """Show tables introspection results"""
        tables = st.session_state.servicenow_introspection_results['tables']
        
        if not tables:
            st.info("No tables found.")
            return
        
        table_data = []
        for table in tables:
            table_data.append({
                'Name': table['name'],
                'Label': table['label'],
                'Description': table['description'],
                'Super Class': table['super_class'],
                'Active': table['active']
            })
        
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)
        
        # Table distribution chart
        if len(table_data) > 0:
            active_count = df['Active'].sum()
            inactive_count = len(df) - active_count
            
            fig = px.pie(values=[active_count, inactive_count], 
                        names=['Active', 'Inactive'],
                        title="Table Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_properties_results(self):
        """Show properties introspection results"""
        properties = st.session_state.servicenow_introspection_results['properties']
        
        if not properties:
            st.info("No system properties found.")
            return
        
        property_data = []
        for prop in properties:
            property_data.append({
                'Name': prop['name'],
                'Value': prop['current_value'],
                'Description': prop['description'],
                'Type': prop['property_type'],
                'Category': prop['category']
            })
        
        df = pd.DataFrame(property_data)
        st.dataframe(df, use_container_width=True)
        
        # Property type distribution chart
        if len(property_data) > 0:
            type_counts = df['Type'].value_counts()
            fig = px.pie(values=type_counts.values, 
                        names=type_counts.index,
                        title="Property Type Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_scheduled_jobs_results(self):
        """Show scheduled jobs introspection results"""
        jobs = st.session_state.servicenow_introspection_results['scheduled_jobs']
        
        if not jobs:
            st.info("No scheduled jobs found.")
            return
        
        job_data = []
        for job in jobs:
            job_data.append({
                'Name': job['name'],
                'Description': job['description'],
                'Active': job['active'],
                'Run Type': job['run_type'],
                'Frequency': job['frequency'],
                'Next Run': job['next_run']
            })
        
        df = pd.DataFrame(job_data)
        st.dataframe(df, use_container_width=True)
        
        # Job status distribution chart
        if len(job_data) > 0:
            active_count = df['Active'].sum()
            inactive_count = len(df) - active_count
            
            fig = px.pie(values=[active_count, inactive_count], 
                        names=['Active', 'Inactive'],
                        title="Scheduled Job Status Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    def _save_introspection_results(self):
        """Save ServiceNow instance introspection results to database"""
        if not st.session_state.servicenow_introspection_results:
            st.error("No introspection results to save.")
            return
        
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Save modules
            status_text.text("💾 Saving modules...")
            progress_bar.progress(20)
            
            for module_data in st.session_state.servicenow_introspection_results['modules']:
                self.db_manager.save_module(module_data)
            
            # Save roles
            status_text.text("💾 Saving roles...")
            progress_bar.progress(40)
            
            for role_data in st.session_state.servicenow_introspection_results['roles']:
                # Find or create module for role
                module_data = {
                    'name': 'ServiceNow Instance',
                    'label': 'ServiceNow Instance',
                    'description': f'ServiceNow Instance: {st.session_state.servicenow_introspection_results["instance_info"]["instance_url"]}',
                    'version': st.session_state.servicenow_introspection_results['instance_info']['version'],
                    'module_type': 'instance',
                    'documentation_url': st.session_state.servicenow_introspection_results['instance_info']['instance_url']
                }
                # Add module info to role_data for the simplified save_role method
                role_data['module'] = 'ServiceNow Instance'
                self.db_manager.save_role(role_data)
            
            # Save properties
            status_text.text("💾 Saving properties...")
            progress_bar.progress(60)
            
            for property_data in st.session_state.servicenow_introspection_results['properties']:
                # Find or create module for property
                module_data = {
                    'name': 'ServiceNow Instance',
                    'label': 'ServiceNow Instance',
                    'description': f'ServiceNow Instance: {st.session_state.servicenow_introspection_results["instance_info"]["instance_url"]}',
                    'version': st.session_state.servicenow_introspection_results['instance_info']['version'],
                    'module_type': 'instance',
                    'documentation_url': st.session_state.servicenow_introspection_results['instance_info']['instance_url']
                }
                # Add module info to property_data for the simplified save_property method
                property_data['module'] = 'ServiceNow Instance'
                self.db_manager.save_property(property_data)
            
            # Save tables
            status_text.text("💾 Saving tables...")
            progress_bar.progress(70)
            
            for table_data in st.session_state.servicenow_introspection_results['tables']:
                # Find or create module for table
                module_data = {
                    'name': 'ServiceNow Instance',
                    'label': 'ServiceNow Instance',
                    'description': f'ServiceNow Instance: {st.session_state.servicenow_introspection_results["instance_info"]["instance_url"]}',
                    'version': st.session_state.servicenow_introspection_results['instance_info']['version'],
                    'module_type': 'instance',
                    'documentation_url': st.session_state.servicenow_introspection_results['instance_info']['instance_url']
                }
                # Add module info to table_data for the simplified save_table method
                table_data['module'] = 'ServiceNow Instance'
                self.db_manager.save_table(table_data)
            
            # Save scheduled jobs
            status_text.text("💾 Saving scheduled jobs...")
            progress_bar.progress(80)
            
            for job_data in st.session_state.servicenow_introspection_results['scheduled_jobs']:
                # Find or create module for job
                module_data = {
                    'name': 'ServiceNow Instance',
                    'label': 'ServiceNow Instance',
                    'description': f'ServiceNow Instance: {st.session_state.servicenow_introspection_results["instance_info"]["instance_url"]}',
                    'version': st.session_state.servicenow_introspection_results['instance_info']['version'],
                    'module_type': 'instance',
                    'documentation_url': st.session_state.servicenow_introspection_results['instance_info']['instance_url']
                }
                # Add module info to job_data for the simplified save_scheduled_job method
                job_data['module'] = 'ServiceNow Instance'
                self.db_manager.save_scheduled_job(job_data)
            
            progress_bar.progress(100)
            status_text.text("✅ All data saved successfully!")
            
            st.success("🎉 ServiceNow instance introspection results saved to database!")
            
        except Exception as e:
            st.error(f"❌ Error saving results: {e}")
            st.exception(e)
    
    def show_footer(self):
        """Show footer with creator information"""
        st.markdown("""
        <div style="position: fixed; bottom: 0; left: 0; right: 0; background-color: #f8f9fa; border-top: 1px solid #dee2e6; padding: 10px 20px; text-align: center; font-size: 0.9rem; color: #6c757d; z-index: 1000;">
            Created By: <strong>Ashish Gautam</strong> | 
            <a href="https://www.linkedin.com/in/ashishgautamkarn/" target="_blank" style="color: #007bff; text-decoration: none;">LinkedIn Profile</a>
        </div>
        """, unsafe_allow_html=True)

# Created By: Ashish Gautam; LinkedIn: https://www.linkedin.com/in/ashishgautamkarn/
