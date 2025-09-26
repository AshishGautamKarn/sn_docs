"""
Database Introspection UI for ServiceNow Instances
Allows connecting to ServiceNow instances and extracting comprehensive data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import DatabaseIntrospector, DatabaseManager
from typing import Dict, List, Any
import time
from datetime import datetime


class DatabaseIntrospectionUI:
    """UI for database introspection of ServiceNow instances"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.introspector = None
        self.introspection_results = {}
    
    def show_introspection_interface(self):
        """Show the main database introspection interface"""
        st.markdown('<h2 class="section-header">🔍 ServiceNow Database Introspection</h2>', unsafe_allow_html=True)
        
        st.markdown("""
        This tool allows you to connect to ServiceNow instances and extract comprehensive data including:
        - **Modules**: All ServiceNow modules and their configurations
        - **Roles**: User roles and permissions
        - **Tables**: Database tables and their relationships
        - **System Properties**: Configuration properties and values
        - **Scheduled Jobs**: Automated jobs and their schedules
        """)
        
        # Connection configuration
        self._show_connection_config()
        
        # Introspection results
        if self.introspector:
            self._show_introspection_results()
        
        # Show footer
        self.show_footer()
    
    def _show_connection_config(self):
        """Show connection configuration section"""
        st.markdown("### 🔗 ServiceNow Instance Connection")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Database Connection")
            db_type = st.selectbox(
                "Database Type",
                ["PostgreSQL", "MySQL", "SQL Server", "Oracle"],
                help="Select the database type of your ServiceNow instance"
            )
            
            host = st.text_input(
                "Host",
                value="localhost",
                help="Database server hostname or IP address (e.g., localhost, 192.168.1.100, db.example.com)",
                placeholder="Enter hostname or IP address"
            )
            
            port = st.number_input(
                "Port",
                value=5432 if db_type == "PostgreSQL" else 3306 if db_type == "MySQL" else 1433,
                min_value=1,
                max_value=65535,
                help="Database server port"
            )
            
            database = st.text_input(
                "Database Name",
                value="servicenow",
                help="ServiceNow database name",
                placeholder="Enter database name"
            )
        
        with col2:
            st.markdown("#### Authentication")
            username = st.text_input(
                "Username",
                value="servicenow",
                help="Database username",
                placeholder="Enter username"
            )
            
            password = st.text_input(
                "Password",
                type="password",
                help="Database password",
                placeholder="Enter password"
            )
            
            # Connection options
            st.markdown("#### Connection Options")
            timeout = st.number_input(
                "Connection Timeout (seconds)",
                value=30,
                min_value=5,
                max_value=300,
                help="Database connection timeout"
            )
            
            max_connections = st.number_input(
                "Max Connections",
                value=5,
                min_value=1,
                max_value=20,
                help="Maximum number of concurrent connections"
            )
        
        # Connection string preview
        st.markdown("#### 🔗 Connection String Preview")
        if host and database and username:
            import urllib.parse
            encoded_password = urllib.parse.quote_plus(password) if password else ""
            encoded_username = urllib.parse.quote_plus(username)
            encoded_host = urllib.parse.quote_plus(host)
            encoded_database = urllib.parse.quote_plus(database)
            
            if db_type == "PostgreSQL":
                preview_string = f"postgresql://{encoded_username}:***@{encoded_host}:{port}/{encoded_database}"
            elif db_type == "MySQL":
                preview_string = f"mysql+pymysql://{encoded_username}:***@{encoded_host}:{port}/{encoded_database}"
            elif db_type == "SQL Server":
                preview_string = f"mssql+pyodbc://{encoded_username}:***@{encoded_host}:{port}/{encoded_database}?driver=ODBC+Driver+17+for+SQL+Server"
            elif db_type == "Oracle":
                preview_string = f"oracle://{encoded_username}:***@{encoded_host}:{port}/{encoded_database}"
            else:
                preview_string = "Select a database type"
            
            st.code(preview_string, language="text")
        else:
            st.info("Fill in Host, Database Name, and Username to see connection string preview")
        
        # Test and connect buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧪 Test Connection", use_container_width=True):
                self._test_connection(db_type, host, port, database, username, password, timeout)
        
        with col2:
            if st.button("🔍 Start Introspection", use_container_width=True):
                self._start_introspection(db_type, host, port, database, username, password, timeout, max_connections)
        
        with col3:
            if st.button("💾 Save to Database", use_container_width=True):
                self._save_introspection_results()
    
    def _test_connection(self, db_type: str, host: str, port: int, database: str, username: str, password: str, timeout: int):
        """Test database connection"""
        try:
            # Validate inputs
            if not host or not database or not username:
                st.error("❌ Please fill in all required fields (Host, Database Name, Username)")
                return
            
            # Build connection string with proper URL encoding
            import urllib.parse
            
            # URL encode special characters in password
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
            
            # Show connection string for debugging (without password)
            debug_string = connection_string.replace(encoded_password, "***") if encoded_password else connection_string
            st.info(f"🔗 Connection string: {debug_string}")
            
            # Test connection
            from sqlalchemy import text
            test_introspector = DatabaseIntrospector(connection_string, db_type.lower())
            session = test_introspector.SessionLocal()
            session.execute(text("SELECT 1"))
            session.close()
            
            st.success("✅ Connection successful!")
            st.info(f"Connected to {db_type} database: {database} on {host}:{port}")
            
        except Exception as e:
            st.error(f"❌ Connection failed: {e}")
            st.error("💡 Troubleshooting tips:")
            st.error("• Check if the hostname/IP address is correct")
            st.error("• Verify the port number")
            st.error("• Ensure the database name exists")
            st.error("• Check username and password")
            st.error("• Make sure the MySQL server is running and accessible")
    
    def _start_introspection(self, db_type: str, host: str, port: int, database: str, username: str, password: str, timeout: int, max_connections: int):
        """Start database introspection"""
        try:
            # Validate inputs
            if not host or not database or not username:
                st.error("❌ Please fill in all required fields (Host, Database Name, Username)")
                return
            
            # Build connection string with proper URL encoding
            import urllib.parse
            
            # URL encode special characters
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
            
            # Initialize introspector
            self.introspector = DatabaseIntrospector(connection_string, db_type.lower())
            
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Introspect tables
            status_text.text("🔍 Discovering database tables...")
            progress_bar.progress(10)
            tables = self.introspector.introspect_tables()
            
            # Introspect each table
            status_text.text("📊 Analyzing table structures...")
            progress_bar.progress(30)
            
            introspection_data = {
                'instance_info': {
                    'db_type': db_type,
                    'host': host,
                    'port': port,
                    'database': database,
                    'username': username,
                    'introspected_at': datetime.now().isoformat()
                },
                'tables': [],
                'modules': [],
                'roles': [],
                'properties': [],
                'scheduled_jobs': []
            }
            
            # Analyze each table
            for i, table in enumerate(tables):
                table_name = table['name']
                status_text.text(f"🔍 Analyzing table: {table_name}")
                progress_bar.progress(30 + (i * 40 / len(tables)))
                
                # Get table columns
                columns = self.introspector.introspect_table_columns(table_name)
                
                # Get foreign keys
                foreign_keys = self.introspector.introspect_foreign_keys(table_name)
                
                # Categorize table
                table_info = {
                    'name': table_name,
                    'type': table['type'],
                    'schema': table['schema'],
                    'columns': columns,
                    'foreign_keys': foreign_keys,
                    'category': self._categorize_table(table_name, columns)
                }
                
                introspection_data['tables'].append(table_info)
                
                # Extract specific data based on table type
                if self._is_module_table(table_name):
                    self._extract_module_data(table_name, introspection_data)
                elif self._is_role_table(table_name):
                    self._extract_role_data(table_name, introspection_data)
                elif self._is_property_table(table_name):
                    self._extract_property_data(table_name, introspection_data)
                elif self._is_scheduled_job_table(table_name):
                    self._extract_scheduled_job_data(table_name, introspection_data)
            
            # Store results
            self.introspection_results = introspection_data
            
            progress_bar.progress(100)
            status_text.text("✅ Introspection completed!")
            
            st.success(f"🎉 Successfully introspected {len(tables)} tables!")
            
        except Exception as e:
            st.error(f"❌ Introspection failed: {e}")
            st.exception(e)
    
    def _categorize_table(self, table_name: str, columns: List[Dict]) -> str:
        """Categorize table based on name and columns"""
        table_lower = table_name.lower()
        
        if 'sys_user' in table_lower or 'user' in table_lower:
            return 'User Management'
        elif 'incident' in table_lower or 'problem' in table_lower or 'change' in table_lower:
            return 'IT Service Management'
        elif 'cmdb' in table_lower or 'asset' in table_lower or 'ci' in table_lower:
            return 'Configuration Management'
        elif 'sc_' in table_lower or 'catalog' in table_lower:
            return 'Service Catalog'
        elif 'kb_' in table_lower or 'knowledge' in table_lower:
            return 'Knowledge Management'
        elif 'sys_' in table_lower:
            return 'System Tables'
        else:
            return 'Other'
    
    def _is_module_table(self, table_name: str) -> bool:
        """Check if table is related to modules"""
        return 'sys_app' in table_name.lower() or 'sys_plugin' in table_name.lower()
    
    def _is_role_table(self, table_name: str) -> bool:
        """Check if table is related to roles"""
        return 'sys_user_role' in table_name.lower() or 'role' in table_name.lower()
    
    def _is_property_table(self, table_name: str) -> bool:
        """Check if table is related to properties"""
        return 'sys_properties' in table_name.lower() or 'property' in table_name.lower()
    
    def _is_scheduled_job_table(self, table_name: str) -> bool:
        """Check if table is related to scheduled jobs"""
        return 'sysauto' in table_name.lower() or 'scheduled' in table_name.lower() or 'job' in table_name.lower()
    
    def _extract_module_data(self, table_name: str, introspection_data: Dict):
        """Extract module data from table"""
        try:
            from sqlalchemy import text
            session = self.introspector.SessionLocal()
            result = session.execute(text(f"SELECT * FROM {table_name} LIMIT 100"))
            rows = result.fetchall()
            session.close()
            
            for row in rows:
                module_data = {
                    'name': str(row[0]) if len(row) > 0 else 'Unknown',
                    'label': str(row[1]) if len(row) > 1 else 'Unknown',
                    'description': str(row[2]) if len(row) > 2 else '',
                    'version': str(row[3]) if len(row) > 3 else '',
                    'active': bool(row[4]) if len(row) > 4 else True,
                    'source_table': table_name
                }
                introspection_data['modules'].append(module_data)
        except Exception as e:
            st.warning(f"Could not extract module data from {table_name}: {e}")
    
    def _extract_role_data(self, table_name: str, introspection_data: Dict):
        """Extract role data from table"""
        try:
            from sqlalchemy import text
            session = self.introspector.SessionLocal()
            result = session.execute(text(f"SELECT * FROM {table_name} LIMIT 100"))
            rows = result.fetchall()
            session.close()
            
            for row in rows:
                role_data = {
                    'name': str(row[0]) if len(row) > 0 else 'Unknown',
                    'description': str(row[1]) if len(row) > 1 else '',
                    'active': bool(row[2]) if len(row) > 2 else True,
                    'source_table': table_name
                }
                introspection_data['roles'].append(role_data)
        except Exception as e:
            st.warning(f"Could not extract role data from {table_name}: {e}")
    
    def _extract_property_data(self, table_name: str, introspection_data: Dict):
        """Extract property data from table"""
        try:
            from sqlalchemy import text
            session = self.introspector.SessionLocal()
            result = session.execute(text(f"SELECT * FROM {table_name} LIMIT 100"))
            rows = result.fetchall()
            session.close()
            
            for row in rows:
                property_data = {
                    'name': str(row[0]) if len(row) > 0 else 'Unknown',
                    'value': str(row[1]) if len(row) > 1 else '',
                    'description': str(row[2]) if len(row) > 2 else '',
                    'type': str(row[3]) if len(row) > 3 else 'string',
                    'source_table': table_name
                }
                introspection_data['properties'].append(property_data)
        except Exception as e:
            st.warning(f"Could not extract property data from {table_name}: {e}")
    
    def _extract_scheduled_job_data(self, table_name: str, introspection_data: Dict):
        """Extract scheduled job data from table"""
        try:
            from sqlalchemy import text
            session = self.introspector.SessionLocal()
            result = session.execute(text(f"SELECT * FROM {table_name} LIMIT 100"))
            rows = result.fetchall()
            session.close()
            
            for row in rows:
                job_data = {
                    'name': str(row[0]) if len(row) > 0 else 'Unknown',
                    'description': str(row[1]) if len(row) > 1 else '',
                    'frequency': str(row[2]) if len(row) > 2 else '',
                    'active': bool(row[3]) if len(row) > 3 else True,
                    'source_table': table_name
                }
                introspection_data['scheduled_jobs'].append(job_data)
        except Exception as e:
            st.warning(f"Could not extract scheduled job data from {table_name}: {e}")
    
    def _show_introspection_results(self):
        """Show introspection results"""
        if not self.introspection_results:
            return
        
        st.markdown("### 📊 Introspection Results")
        
        # Instance info
        instance_info = self.introspection_results['instance_info']
        st.markdown(f"**Instance**: {instance_info['db_type']} - {instance_info['database']} @ {instance_info['host']}")
        st.markdown(f"**Introspected**: {instance_info['introspected_at']}")
        
        # Summary metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Tables", len(self.introspection_results['tables']))
        with col2:
            st.metric("Modules", len(self.introspection_results['modules']))
        with col3:
            st.metric("Roles", len(self.introspection_results['roles']))
        with col4:
            st.metric("Properties", len(self.introspection_results['properties']))
        with col5:
            st.metric("Scheduled Jobs", len(self.introspection_results['scheduled_jobs']))
        
        # Detailed results tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Tables", "Modules", "Roles", "Properties", "Scheduled Jobs"])
        
        with tab1:
            self._show_tables_results()
        
        with tab2:
            self._show_modules_results()
        
        with tab3:
            self._show_roles_results()
        
        with tab4:
            self._show_properties_results()
        
        with tab5:
            self._show_scheduled_jobs_results()
    
    def _show_tables_results(self):
        """Show tables introspection results"""
        tables = self.introspection_results['tables']
        
        if not tables:
            st.info("No tables found.")
            return
        
        # Table summary
        table_summary = []
        for table in tables:
            table_summary.append({
                'Name': table['name'],
                'Category': table['category'],
                'Type': table['type'],
                'Schema': table['schema'],
                'Columns': len(table['columns']),
                'Foreign Keys': len(table['foreign_keys'])
            })
        
        df = pd.DataFrame(table_summary)
        st.dataframe(df, use_container_width=True)
        
        # Category distribution
        if len(table_summary) > 0:
            category_counts = df['Category'].value_counts()
            fig = px.pie(values=category_counts.values, names=category_counts.index, title="Table Categories Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_modules_results(self):
        """Show modules introspection results"""
        modules = self.introspection_results['modules']
        
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
                'Source Table': module['source_table']
            })
        
        df = pd.DataFrame(module_data)
        st.dataframe(df, use_container_width=True)
    
    def _show_roles_results(self):
        """Show roles introspection results"""
        roles = self.introspection_results['roles']
        
        if not roles:
            st.info("No roles found.")
            return
        
        role_data = []
        for role in roles:
            role_data.append({
                'Name': role['name'],
                'Description': role['description'],
                'Active': role['active'],
                'Source Table': role['source_table']
            })
        
        df = pd.DataFrame(role_data)
        st.dataframe(df, use_container_width=True)
    
    def _show_properties_results(self):
        """Show properties introspection results"""
        properties = self.introspection_results['properties']
        
        if not properties:
            st.info("No properties found.")
            return
        
        property_data = []
        for prop in properties:
            property_data.append({
                'Name': prop['name'],
                'Value': prop['value'],
                'Description': prop['description'],
                'Type': prop['type'],
                'Source Table': prop['source_table']
            })
        
        df = pd.DataFrame(property_data)
        st.dataframe(df, use_container_width=True)
    
    def _show_scheduled_jobs_results(self):
        """Show scheduled jobs introspection results"""
        jobs = self.introspection_results['scheduled_jobs']
        
        if not jobs:
            st.info("No scheduled jobs found.")
            return
        
        job_data = []
        for job in jobs:
            job_data.append({
                'Name': job['name'],
                'Description': job['description'],
                'Frequency': job['frequency'],
                'Active': job['active'],
                'Source Table': job['source_table']
            })
        
        df = pd.DataFrame(job_data)
        st.dataframe(df, use_container_width=True)
    
    def _save_introspection_results(self):
        """Save introspection results to database"""
        if not self.introspection_results:
            st.error("No introspection results to save.")
            return
        
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Save modules
            status_text.text("💾 Saving modules...")
            progress_bar.progress(20)
            
            for module_data in self.introspection_results['modules']:
                self.db_manager.save_module(module_data)
            
            # Save roles
            status_text.text("💾 Saving roles...")
            progress_bar.progress(40)
            
            for role_data in self.introspection_results['roles']:
                # Find or create module for role
                module = self.db_manager.save_module({'name': 'Introspected Module', 'label': 'Introspected Module'})
                self.db_manager.save_role(role_data, module.id)
            
            # Save properties
            status_text.text("💾 Saving properties...")
            progress_bar.progress(60)
            
            for property_data in self.introspection_results['properties']:
                # Find or create module for property
                module = self.db_manager.save_module({'name': 'Introspected Module', 'label': 'Introspected Module'})
                self.db_manager.save_property(property_data, module.id)
            
            # Save scheduled jobs
            status_text.text("💾 Saving scheduled jobs...")
            progress_bar.progress(80)
            
            for job_data in self.introspection_results['scheduled_jobs']:
                # Find or create module for job
                module = self.db_manager.save_module({'name': 'Introspected Module', 'label': 'Introspected Module'})
                self.db_manager.save_scheduled_job(job_data, module.id)
            
            progress_bar.progress(100)
            status_text.text("✅ All data saved successfully!")
            
            st.success("🎉 Introspection results saved to database!")
            
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
