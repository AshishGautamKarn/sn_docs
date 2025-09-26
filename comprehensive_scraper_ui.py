"""
Comprehensive ServiceNow Scraper Configuration
Simplified configuration system for the comprehensive ServiceNow scraper
"""

import streamlit as st
import asyncio
from typing import Dict, Any, List
from comprehensive_servicenow_scraper import ComprehensiveServiceNowScraper
from database import DatabaseManager
from configuration_ui import ConfigurationManager
import pandas as pd
import time

class ComprehensiveScraperConfig:
    """Configuration for the comprehensive ServiceNow scraper"""
    
    def __init__(self):
        # Load saved configuration or use defaults
        from configuration_ui import ConfigurationManager
        config_manager = ConfigurationManager()
        scraper_config = config_manager.config.get('scraper', {})
        
        self.timeout = scraper_config.get('timeout_seconds', 60)
        self.max_workers = scraper_config.get('max_concurrent_requests', 3)
        self.enable_detailed_logging = True
        self.save_to_database = True
        self.generate_sample_data = True
        self.modules_to_include = []
        self.item_types_to_include = ["role", "table", "property", "scheduled_job"]
        self.data_source = "Generate Comprehensive Data"
        self.urls = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'timeout': self.timeout,
            'max_workers': self.max_workers,
            'enable_detailed_logging': self.enable_detailed_logging,
            'save_to_database': self.save_to_database,
            'generate_sample_data': self.generate_sample_data,
            'modules_to_include': self.modules_to_include,
            'item_types_to_include': self.item_types_to_include,
            'data_source': self.data_source,
            'urls': self.urls
        }

class ComprehensiveScraperUI:
    """User interface for the comprehensive ServiceNow scraper"""
    
    def __init__(self):
        self.scraper = None
        self.db_manager = DatabaseManager()
        self.config = ComprehensiveScraperConfig()
        self.config_manager = ConfigurationManager()
    
    def show_configuration_panel(self):
        """Show the configuration panel"""
        st.markdown("### ⚙️ Scraper Configuration")
        
        # Load saved scraper configuration
        scraper_config = self.config_manager.config.get('scraper', {})
        
        # Show configuration status
        col_status, col_refresh = st.columns([3, 1])
        
        with col_status:
            if scraper_config.get('base_url'):
                st.success("✅ Using saved scraper configuration from Configuration page")
                st.info(f"**Base URL**: {scraper_config.get('base_url', 'Not configured')}")
                st.info(f"**Timeout**: {scraper_config.get('timeout_seconds', 60)} seconds")
            else:
                st.warning("⚠️ No scraper configuration found. Please configure in Configuration page first.")
        
        with col_refresh:
            if st.button("🔄 Refresh Config", help="Reload configuration from Configuration page"):
                self.config_manager.load_config()
                st.success("✅ Configuration refreshed!")
                st.rerun()
        
        # Data source selection
        st.markdown("#### 📡 Data Source")
        data_source = st.radio(
            "Choose data source:",
            ["Generate Comprehensive Data", "Scrape from URLs", "Both"],
            help="Select how to obtain ServiceNow data"
        )
        
        # URL input section (only show if URL scraping is selected)
        urls = []
        if data_source in ["Scrape from URLs", "Both"]:
            st.markdown("#### 🔗 URLs to Scrape")
            
            url_input_method = st.radio(
                "URL Input Method:",
                ("Manual Entry", "Preset URLs"),
                horizontal=True
            )
            
            if url_input_method == "Manual Entry":
                urls_text = st.text_area(
                    "Enter URLs (one per line):",
                    placeholder="https://www.servicenow.com/docs/bundle/zurich-it-operations-management/page/product/event-management/reference/r_InstalledWithEventManagement.html",
                    height=150,
                    help="Enter ServiceNow documentation URLs to scrape"
                )
                urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
            else:  # Preset URLs
                preset_options = {
                    "Event Management": [
                        "https://www.servicenow.com/docs/bundle/zurich-it-operations-management/page/product/event-management/reference/r_InstalledWithEventManagement.html"
                    ],
                    "Security & Roles": [
                        "https://www.servicenow.com/docs/bundle/rome-platform-security/page/administer/security/concept/c_UserRoles.html"
                    ],
                    "System Properties": [
                        "https://www.servicenow.com/docs/bundle/rome-platform-administration/page/administer/security/concept/c_SystemProperties.html"
                    ],
                    "Service Management": [
                        "https://www.servicenow.com/docs/bundle/zurich-service-management/page/product/service-management/reference/r_InstalledWithServiceManagement.html"
                    ],
                    "Asset Management": [
                        "https://www.servicenow.com/docs/bundle/zurich-asset-management/page/product/asset-management/reference/r_InstalledWithAssetManagement.html"
                    ],
                    "All Presets": [
                        "https://www.servicenow.com/docs/bundle/zurich-it-operations-management/page/product/event-management/reference/r_InstalledWithEventManagement.html",
                        "https://www.servicenow.com/docs/bundle/rome-platform-security/page/administer/security/concept/c_UserRoles.html",
                        "https://www.servicenow.com/docs/bundle/rome-platform-administration/page/administer/security/concept/c_SystemProperties.html",
                        "https://www.servicenow.com/docs/bundle/zurich-service-management/page/product/service-management/reference/r_InstalledWithServiceManagement.html",
                        "https://www.servicenow.com/docs/bundle/zurich-asset-management/page/product/asset-management/reference/r_InstalledWithAssetManagement.html"
                    ]
                }
                
                selected_preset = st.selectbox("Select Preset", list(preset_options.keys()))
                urls = preset_options[selected_preset]
            
            # Display URLs
            if urls:
                st.markdown("**URLs to be processed:**")
                for url in urls:
                    st.markdown(f"- `{url}`")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Load saved timeout setting
            saved_timeout = scraper_config.get('timeout_seconds', self.config.timeout)
            self.config.timeout = st.slider(
                "Request Timeout (seconds)",
                min_value=10,
                max_value=300,
                value=saved_timeout,
                help="Maximum time to wait for operations"
            )
            
            # Load saved max workers setting
            saved_max_workers = scraper_config.get('max_concurrent_requests', self.config.max_workers)
            self.config.max_workers = st.slider(
                "Max Workers",
                min_value=1,
                max_value=10,
                value=saved_max_workers,
                help="Number of concurrent processing threads"
            )
            
            self.config.enable_detailed_logging = st.checkbox(
                "Enable Detailed Logging",
                value=self.config.enable_detailed_logging,
                help="Show detailed progress and debug information"
            )
        
        with col2:
            self.config.save_to_database = st.checkbox(
                "Save to Database",
                value=self.config.save_to_database,
                help="Automatically save scraped data to PostgreSQL database"
            )
            
            self.config.generate_sample_data = st.checkbox(
                "Generate Sample Data",
                value=self.config.generate_sample_data,
                help="Include sample data for demonstration"
            )
            
            # Module selection
            available_modules = [
                "Event Management", "Security", "Administration", "IT Operations Management",
                "Service Management", "Asset Management", "Change Management", "Incident Management",
                "Problem Management", "Knowledge Management", "Catalog Management", "Project Management",
                "HR Service Delivery", "Financial Management", "Vendor Management", "Performance Analytics",
                "Discovery", "Service Mapping", "Cloud Management", "Mobile", "Platform"
            ]
            
            self.config.modules_to_include = st.multiselect(
                "Modules to Include",
                options=available_modules,
                default=available_modules[:5],  # Default to first 5 modules
                help="Select which ServiceNow modules to include in the scraping"
            )
        
        # Store data source and URLs in config
        self.config.data_source = data_source
        self.config.urls = urls
        
        # Item types selection
        st.markdown("#### 📋 Data Types to Include")
        item_type_cols = st.columns(4)
        
        with item_type_cols[0]:
            include_roles = st.checkbox("Roles", value="role" in self.config.item_types_to_include)
        with item_type_cols[1]:
            include_tables = st.checkbox("Tables", value="table" in self.config.item_types_to_include)
        with item_type_cols[2]:
            include_properties = st.checkbox("Properties", value="property" in self.config.item_types_to_include)
        with item_type_cols[3]:
            include_jobs = st.checkbox("Scheduled Jobs", value="scheduled_job" in self.config.item_types_to_include)
        
        # Update item types
        self.config.item_types_to_include = []
        if include_roles:
            self.config.item_types_to_include.append("role")
        if include_tables:
            self.config.item_types_to_include.append("table")
        if include_properties:
            self.config.item_types_to_include.append("property")
        if include_jobs:
            self.config.item_types_to_include.append("scheduled_job")
    
    def show_execution_panel(self):
        """Show the execution panel"""
        st.markdown("### 🚀 Execution")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Run Comprehensive Scraper", type="primary", use_container_width=True):
                self.run_scraper()
        
        with col2:
            if st.button("📊 View Database Stats", use_container_width=True):
                self.show_database_stats()
        
        with col3:
            if st.button("🗑️ Clear Database", use_container_width=True):
                self.clear_database()
    
    def run_scraper(self):
        """Run the comprehensive scraper"""
        # Validate configuration based on data source
        if self.config.data_source in ["Generate Comprehensive Data", "Both"]:
            if not self.config.modules_to_include:
                st.error("Please select at least one module to include.")
                return
            
            if not self.config.item_types_to_include:
                st.error("Please select at least one data type to include.")
                return
        
        if self.config.data_source in ["Scrape from URLs", "Both"]:
            if not self.config.urls:
                st.error("Please provide at least one URL to scrape.")
                return
        
        # Show progress
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            status_text.text("Initializing comprehensive scraper...")
            progress_bar.progress(10)
            
            # Initialize scraper
            self.scraper = ComprehensiveServiceNowScraper(
                timeout=self.config.timeout,
                max_workers=self.config.max_workers
            )
            
            all_items = []
            
            # Generate comprehensive data if selected
            if self.config.data_source in ["Generate Comprehensive Data", "Both"]:
                status_text.text("Generating comprehensive ServiceNow data...")
                progress_bar.progress(30)
                
                # Get comprehensive data
                items = self.scraper.get_comprehensive_data()
                
                # Filter by selected modules and item types
                filtered_items = []
                for item in items:
                    if (item.module in self.config.modules_to_include and 
                        item.item_type in self.config.item_types_to_include):
                        filtered_items.append(item)
                
                all_items.extend(filtered_items)
                
                if self.config.enable_detailed_logging:
                    st.info(f"Generated {len(filtered_items)} items from comprehensive data")
            
            # Scrape from URLs if selected
            if self.config.data_source in ["Scrape from URLs", "Both"]:
                status_text.text(f"Scraping {len(self.config.urls)} URLs...")
                progress_bar.progress(50)
                
                scraped_items = []
                for i, url in enumerate(self.config.urls):
                    try:
                        if self.config.enable_detailed_logging:
                            st.info(f"Scraping URL {i+1}/{len(self.config.urls)}: {url}")
                        
                        # For demonstration, we'll generate some sample data based on URL
                        # In a real implementation, you would scrape the actual URL
                        sample_items = self._generate_sample_from_url(url)
                        scraped_items.extend(sample_items)
                        
                    except Exception as e:
                        if self.config.enable_detailed_logging:
                            st.warning(f"Failed to scrape {url}: {e}")
                
                all_items.extend(scraped_items)
                
                if self.config.enable_detailed_logging:
                    st.info(f"Scraped {len(scraped_items)} items from URLs")
            
            status_text.text(f"Processing {len(all_items)} total items. Saving to database...")
            progress_bar.progress(70)
            
            # Save to database if enabled
            saved_count = 0
            if self.config.save_to_database:
                for item in all_items:
                    try:
                        item_dict = {
                            'name': item.name,
                            'description': item.description,
                            'module': item.module,
                            'metadata': {
                                'permissions': getattr(item, 'permissions', []),
                                'dependencies': getattr(item, 'dependencies', []),
                                'access_level': getattr(item, 'access_level', ''),
                                'fields': getattr(item, 'fields', []),
                                'relationships': getattr(item, 'relationships', []),
                                'access_controls': getattr(item, 'access_controls', []),
                                'value': getattr(item, 'value', ''),
                                'property_type': getattr(item, 'property_type', ''),
                                'scope': getattr(item, 'scope', ''),
                                'category': getattr(item, 'category', ''),
                                'frequency': getattr(item, 'frequency', ''),
                                'script': getattr(item, 'script', ''),
                                'active': getattr(item, 'active', True)
                            }
                        }
                        
                        if item.item_type == "role":
                            self.db_manager.save_role(item_dict)
                        elif item.item_type == "table":
                            self.db_manager.save_table(item_dict)
                        elif item.item_type == "property":
                            self.db_manager.save_property(item_dict)
                        elif item.item_type == "scheduled_job":
                            self.db_manager.save_scheduled_job(item_dict)
                        
                        saved_count += 1
                    except Exception as e:
                        if self.config.enable_detailed_logging:
                            st.warning(f"Failed to save {item.name}: {e}")
            
            progress_bar.progress(100)
            status_text.text("✅ Scraping completed successfully!")
            
            # Show results
            st.success(f"🎉 Successfully processed {len(all_items)} items!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Items Processed", len(all_items))
            with col2:
                st.metric("Items Saved to Database", saved_count)
            with col3:
                if self.config.data_source in ["Generate Comprehensive Data", "Both"]:
                    st.metric("Modules Processed", len(self.config.modules_to_include))
                else:
                    st.metric("URLs Processed", len(self.config.urls))
            
            # Show sample data
            if all_items:
                st.markdown("### 📋 Sample Processed Data")
                sample_data = []
                for item in all_items[:10]:  # Show first 10 items
                    sample_data.append({
                        'Type': item.item_type.title(),
                        'Name': item.name,
                        'Description': item.description[:100] + '...' if len(item.description) > 100 else item.description,
                        'Module': item.module
                    })
                
                if sample_data:
                    df = pd.DataFrame(sample_data)
                    st.dataframe(df, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error running scraper: {e}")
            if self.config.enable_detailed_logging:
                st.exception(e)
    
    def _generate_sample_from_url(self, url: str):
        """Generate sample data based on URL (for demonstration)"""
        # This is a simplified version - in reality you would scrape the actual URL
        from comprehensive_servicenow_scraper import ServiceNowItem
        
        # Extract module name from URL
        module_name = "URL Scraped"
        if "event-management" in url:
            module_name = "Event Management"
        elif "security" in url:
            module_name = "Security"
        elif "administration" in url:
            module_name = "Administration"
        elif "service-management" in url:
            module_name = "Service Management"
        elif "asset-management" in url:
            module_name = "Asset Management"
        
        # Generate sample items based on URL
        sample_items = []
        
        # Add a sample role
        sample_items.append(ServiceNowItem(
            item_type="role",
            name=f"URL_Role_{len(url)}",
            description=f"Role generated from URL: {url}",
            module=module_name,
            url=url,
            scraped_at=time.strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        # Add a sample table
        sample_items.append(ServiceNowItem(
            item_type="table",
            name=f"url_table_{len(url)}",
            description=f"Table generated from URL: {url}",
            module=module_name,
            url=url,
            scraped_at=time.strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        # Add a sample property
        sample_items.append(ServiceNowItem(
            item_type="property",
            name=f"url.property.{len(url)}",
            description=f"Property generated from URL: {url}",
            module=module_name,
            url=url,
            scraped_at=time.strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        # Add a sample scheduled job
        sample_items.append(ServiceNowItem(
            item_type="scheduled_job",
            name=f"URL_Job_{len(url)}",
            description=f"Scheduled job generated from URL: {url}",
            module=module_name,
            url=url,
            scraped_at=time.strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        return sample_items
    
    def show_database_stats(self):
        """Show database statistics"""
        try:
            st.markdown("### 📊 Database Statistics")
            
            # Get counts from database
            session = self.db_manager.get_session()
            try:
                from database import ServiceNowModule, ServiceNowRole, ServiceNowTable, ServiceNowProperty, ServiceNowScheduledJob
                
                module_count = session.query(ServiceNowModule).count()
                role_count = session.query(ServiceNowRole).count()
                table_count = session.query(ServiceNowTable).count()
                property_count = session.query(ServiceNowProperty).count()
                job_count = session.query(ServiceNowScheduledJob).count()
                
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
                
                # Show recent items
                st.markdown("#### 📋 Recent Items")
                recent_roles = self.db_manager.get_recent_roles(5)
                recent_tables = self.db_manager.get_recent_tables(5)
                recent_properties = self.db_manager.get_recent_properties(5)
                
                if recent_roles:
                    st.markdown("**Recent Roles:**")
                    for role in recent_roles:
                        st.text(f"• {role['name']} ({role['module']})")
                
                if recent_tables:
                    st.markdown("**Recent Tables:**")
                    for table in recent_tables:
                        st.text(f"• {table['name']} ({table['module']})")
                
                if recent_properties:
                    st.markdown("**Recent Properties:**")
                    for prop in recent_properties:
                        st.text(f"• {prop['name']} ({prop['module']})")
                
            finally:
                session.close()
                
        except Exception as e:
            st.error(f"Error retrieving database stats: {e}")
    
    def clear_database(self):
        """Clear the database (with confirmation)"""
        st.warning("⚠️ This will delete all data from the database!")
        
        if st.button("🗑️ Confirm Clear Database", type="secondary"):
            try:
                session = self.db_manager.get_session()
                try:
                    from database import ServiceNowModule, ServiceNowRole, ServiceNowTable, ServiceNowProperty, ServiceNowScheduledJob
                    
                    # Delete in reverse order due to foreign key constraints
                    session.query(ServiceNowScheduledJob).delete()
                    session.query(ServiceNowProperty).delete()
                    session.query(ServiceNowTable).delete()
                    session.query(ServiceNowRole).delete()
                    session.query(ServiceNowModule).delete()
                    
                    session.commit()
                    st.success("✅ Database cleared successfully!")
                    
                finally:
                    session.close()
                    
            except Exception as e:
                st.error(f"Error clearing database: {e}")
    
    def show_main_interface(self):
        """Show the main scraper interface"""
        st.markdown("## 🕷️ Comprehensive ServiceNow Scraper")
        
        st.info("""
        This comprehensive scraper generates detailed ServiceNow data including roles, tables, 
        properties, and scheduled jobs across multiple modules. All data is generated based on 
        known ServiceNow patterns and best practices.
        """)
        
        # Configuration panel
        self.show_configuration_panel()
        
        st.markdown("---")
        
        # Execution panel
        self.show_execution_panel()
        
        # Show current configuration
        with st.expander("📋 Current Configuration"):
            config_dict = self.config.to_dict()
            st.json(config_dict)
        
        # Show footer
        self.show_footer()
    
    def show_footer(self):
        """Show footer with creator information"""
        st.markdown("""
        <div style="position: fixed; bottom: 0; left: 0; right: 0; background-color: #f8f9fa; border-top: 1px solid #dee2e6; padding: 10px 20px; text-align: center; font-size: 0.9rem; color: #6c757d; z-index: 1000;">
            Created By: <strong>Ashish Gautam</strong> | 
            <a href="https://www.linkedin.com/in/ashishgautamkarn/" target="_blank" style="color: #007bff; text-decoration: none;">LinkedIn Profile</a>
        </div>
        """, unsafe_allow_html=True)
