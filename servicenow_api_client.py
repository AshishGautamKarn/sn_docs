"""
ServiceNow REST API Client for Instance Introspection
Handles authentication and data extraction from ServiceNow instances
"""

import requests
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import time


class ServiceNowAPIClient:
    """ServiceNow REST API client for instance introspection"""
    
    def __init__(self, instance_url: str, username: str, password: str):
        self.instance_url = instance_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for ServiceNow API client"""
        logger = logging.getLogger('servicenow_api_client')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _convert_to_boolean(self, value) -> bool:
        """Convert various string/numeric values to boolean"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', 'active', 'enabled']
        if isinstance(value, (int, float)):
            return bool(value)
        return False
    
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
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to ServiceNow instance"""
        try:
            # Test basic connectivity
            response = self.session.get(f"{self.instance_url}/api/now/table/sys_user", 
                                      params={'sysparm_limit': 1})
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'Connection successful',
                    'instance_url': self.instance_url,
                    'response_time': response.elapsed.total_seconds()
                }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'message': 'Authentication failed - check username and password',
                    'error': 'Unauthorized'
                }
            else:
                return {
                    'success': False,
                    'message': f'Connection failed with status {response.status_code}',
                    'error': response.text
                }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'message': f'Connection error: {str(e)}',
                'error': str(e)
            }
    
    def get_instance_info(self) -> Dict[str, Any]:
        """Get basic instance information"""
        try:
            # Get instance info from sys_properties
            response = self.session.get(f"{self.instance_url}/api/now/table/sys_properties",
                                      params={'sysparm_query': 'name=glide.buildname^ORname=glide.buildtag^ORname=glide.version'})
            
            if response.status_code == 200:
                data = response.json()
                instance_info = {
                    'instance_url': self.instance_url,
                    'version': 'Unknown',
                    'build_name': 'Unknown',
                    'build_tag': 'Unknown',
                    'introspected_at': datetime.now().isoformat()
                }
                
                for prop in data.get('result', []):
                    if prop['name'] == 'glide.version':
                        instance_info['version'] = prop['value']
                    elif prop['name'] == 'glide.buildname':
                        instance_info['build_name'] = prop['value']
                    elif prop['name'] == 'glide.buildtag':
                        instance_info['build_tag'] = prop['value']
                
                return instance_info
            else:
                return {
                    'instance_url': self.instance_url,
                    'version': 'Unknown',
                    'build_name': 'Unknown',
                    'build_tag': 'Unknown',
                    'introspected_at': datetime.now().isoformat(),
                    'error': f'Failed to get instance info: {response.status_code}'
                }
        except Exception as e:
            return {
                'instance_url': self.instance_url,
                'version': 'Unknown',
                'build_name': 'Unknown',
                'build_tag': 'Unknown',
                'introspected_at': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def get_modules(self) -> List[Dict[str, Any]]:
        """Get all modules from sys_app table"""
        try:
            response = self.session.get(f"{self.instance_url}/api/now/table/sys_app",
                                      params={'sysparm_limit': 1000})
            
            if response.status_code == 200:
                data = response.json()
                modules = []
                
                for app in data.get('result', []):
                    module = {
                        'name': app.get('name', ''),
                        'label': app.get('label', ''),
                        'description': app.get('description', '') or f"ServiceNow application: {app.get('name', '')}",
                        'version': app.get('version', ''),
                        'active': self._convert_to_boolean(app.get('active', False)),
                        'scope': app.get('scope', ''),
                        'module_type': 'application',
                        'documentation_url': f"{self.instance_url}/sys_app.do?sys_id={app.get('sys_id', '')}",
                        'source': 'sys_app',
                        'instance_url': self.instance_url,
                        'sys_id': app.get('sys_id', '')
                    }
                    modules.append(module)
                
                self.logger.info(f"Retrieved {len(modules)} modules")
                return modules
            elif response.status_code == 401:
                self.logger.error("Authentication failed - check username and password")
                return []
            else:
                self.logger.error(f"Failed to get modules: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            self.logger.error(f"Error getting modules: {e}")
            return []
    
    def get_roles(self) -> List[Dict[str, Any]]:
        """Get all roles from sys_user_role table"""
        try:
            response = self.session.get(f"{self.instance_url}/api/now/table/sys_user_role",
                                      params={'sysparm_limit': 1000})
            
            if response.status_code == 200:
                data = response.json()
                roles = []
                
                for role in data.get('result', []):
                    # Convert permissions and dependencies from string to list if needed
                    permissions = role.get('permissions', [])
                    if isinstance(permissions, str):
                        try:
                            import json
                            permissions = json.loads(permissions)
                        except (json.JSONDecodeError, ValueError) as e:
                            self.logger.warning(f"Failed to parse permissions JSON: {e}, using empty list")
                            permissions = []
                    elif not isinstance(permissions, list):
                        permissions = []
                    
                    dependencies = role.get('dependencies', [])
                    if isinstance(dependencies, str):
                        try:
                            import json
                            dependencies = json.loads(dependencies)
                        except (json.JSONDecodeError, ValueError) as e:
                            self.logger.warning(f"Failed to parse dependencies JSON: {e}, using empty list")
                            dependencies = []
                    elif not isinstance(dependencies, list):
                        dependencies = []
                    
                    role_data = {
                        'name': role.get('name', ''),
                        'description': role.get('description', '') or f"ServiceNow role: {role.get('name', '')}",
                        'active': self._convert_to_boolean(role.get('active', False)),
                        'grantable': self._convert_to_boolean(role.get('grantable', False)),
                        'permissions': permissions,
                        'dependencies': dependencies,
                        'source': 'sys_user_role',
                        'instance_url': self.instance_url,
                        'sys_id': role.get('sys_id', '')
                    }
                    roles.append(role_data)
                
                self.logger.info(f"Retrieved {len(roles)} roles")
                return roles
            else:
                self.logger.error(f"Failed to get roles: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Error getting roles: {e}")
            return []
    
    def get_tables(self) -> List[Dict[str, Any]]:
        """Get all tables from sys_db_object table"""
        try:
            response = self.session.get(f"{self.instance_url}/api/now/table/sys_db_object",
                                      params={'sysparm_limit': 1000})
            
            if response.status_code == 200:
                data = response.json()
                tables = []
                
                for table in data.get('result', []):
                    # Convert JSON fields from string to list if needed
                    json_fields = ['fields', 'relationships', 'access_controls', 'business_rules', 'scripts']
                    converted_fields = {}
                    
                    for field in json_fields:
                        value = table.get(field, [])
                        if isinstance(value, str):
                            try:
                                import json
                                converted_fields[field] = json.loads(value)
                            except (json.JSONDecodeError, ValueError):
                                converted_fields[field] = []
                        elif not isinstance(value, list):
                            converted_fields[field] = []
                        else:
                            converted_fields[field] = value
                    
                    # Extract super_class value from dictionary if it's a dict
                    super_class = table.get('super_class', '')
                    if isinstance(super_class, dict):
                        super_class = super_class.get('value', 'base')
                    elif not super_class:
                        super_class = 'base'
                    
                    table_data = {
                        'name': table.get('name', ''),
                        'label': table.get('label', '') or table.get('name', ''),
                        'description': table.get('description', '') or f"ServiceNow table: {table.get('name', '')}",
                        'super_class': super_class,
                        'active': self._convert_to_boolean(table.get('active', False)),
                        'table_type': super_class,
                        'fields': converted_fields['fields'],
                        'relationships': converted_fields['relationships'],
                        'access_controls': converted_fields['access_controls'],
                        'business_rules': converted_fields['business_rules'],
                        'scripts': converted_fields['scripts'],
                        'source': 'sys_db_object',
                        'instance_url': self.instance_url,
                        'sys_id': table.get('sys_id', '')
                    }
                    tables.append(table_data)
                
                self.logger.info(f"Retrieved {len(tables)} tables")
                return tables
            else:
                self.logger.error(f"Failed to get tables: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Error getting tables: {e}")
            return []
    
    def get_system_properties(self) -> List[Dict[str, Any]]:
        """Get all system properties from sys_properties table"""
        try:
            response = self.session.get(f"{self.instance_url}/api/now/table/sys_properties",
                                      params={'sysparm_limit': 1000})
            
            if response.status_code == 200:
                data = response.json()
                properties = []
                
                for prop in data.get('result', []):
                    property_data = {
                        'name': prop.get('name', ''),
                        'current_value': prop.get('value', ''),
                        'description': prop.get('description', '') or f"ServiceNow system property: {prop.get('name', '')}",
                        'property_type': prop.get('type', 'string'),
                        'category': prop.get('category', ''),
                        'scope': prop.get('scope', ''),
                        'impact_level': prop.get('impact_level', 'Medium'),
                        'documentation_url': f"{self.instance_url}/sys_properties.do?sys_id={prop.get('sys_id', '')}",
                        'source': 'sys_properties',
                        'instance_url': self.instance_url,
                        'sys_id': prop.get('sys_id', '')
                    }
                    properties.append(property_data)
                
                self.logger.info(f"Retrieved {len(properties)} system properties")
                return properties
            else:
                self.logger.error(f"Failed to get system properties: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Error getting system properties: {e}")
            return []
    
    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get all scheduled jobs from sysauto table"""
        try:
            response = self.session.get(f"{self.instance_url}/api/now/table/sysauto",
                                      params={'sysparm_limit': 1000})
            
            if response.status_code == 200:
                data = response.json()
                jobs = []
                
                for job in data.get('result', []):
                    job_data = {
                        'name': job.get('name', ''),
                        'description': job.get('description', '') or f"ServiceNow scheduled job: {job.get('name', '')}",
                        'active': self._convert_to_boolean(job.get('active', False)),
                        'run_type': job.get('run_type', ''),
                        'frequency': job.get('frequency', ''),
                        'next_run': self._convert_timestamp(job.get('next_run', '')),
                        'last_run': self._convert_timestamp(job.get('last_run', '')),
                        'script': job.get('script', ''),
                        'condition': job.get('condition', ''),
                        'documentation_url': f"{self.instance_url}/sysauto.do?sys_id={job.get('sys_id', '')}",
                        'source': 'sysauto',
                        'instance_url': self.instance_url,
                        'sys_id': job.get('sys_id', '')
                    }
                    jobs.append(job_data)
                
                self.logger.info(f"Retrieved {len(jobs)} scheduled jobs")
                return jobs
            else:
                self.logger.error(f"Failed to get scheduled jobs: {response.status_code}")
                return []
        except Exception as e:
            self.logger.error(f"Error getting scheduled jobs: {e}")
            return []
    
    def get_comprehensive_data(self) -> Dict[str, Any]:
        """Get comprehensive data from ServiceNow instance"""
        self.logger.info("Starting comprehensive data extraction...")
        
        # Get instance info
        instance_info = self.get_instance_info()
        
        # Get all data types
        modules = self.get_modules()
        roles = self.get_roles()
        tables = self.get_tables()
        properties = self.get_system_properties()
        scheduled_jobs = self.get_scheduled_jobs()
        
        comprehensive_data = {
            'instance_info': instance_info,
            'modules': modules,
            'roles': roles,
            'tables': tables,
            'properties': properties,
            'scheduled_jobs': scheduled_jobs,
            'summary': {
                'modules_count': len(modules),
                'roles_count': len(roles),
                'tables_count': len(tables),
                'properties_count': len(properties),
                'scheduled_jobs_count': len(scheduled_jobs),
                'total_items': len(modules) + len(roles) + len(tables) + len(properties) + len(scheduled_jobs)
            }
        }
        
        self.logger.info(f"Comprehensive data extraction completed. Total items: {comprehensive_data['summary']['total_items']}")
        return comprehensive_data
    
    def search_tables_by_module(self, module_name: str) -> List[Dict[str, Any]]:
        """Search for tables related to a specific module"""
        try:
            # Search for tables that might be related to the module
            response = self.session.get(f"{self.instance_url}/api/now/table/sys_db_object",
                                      params={
                                          'sysparm_query': f'nameSTARTSWITH{module_name.lower()}',
                                          'sysparm_limit': 100
                                      })
            
            if response.status_code == 200:
                data = response.json()
                return data.get('result', [])
            else:
                return []
        except Exception as e:
            self.logger.error(f"Error searching tables for module {module_name}: {e}")
            return []
    
    def get_table_fields(self, table_name: str) -> List[Dict[str, Any]]:
        """Get fields for a specific table"""
        try:
            response = self.session.get(f"{self.instance_url}/api/now/table/sys_dictionary",
                                      params={
                                          'sysparm_query': f'name={table_name}',
                                          'sysparm_limit': 1000
                                      })
            
            if response.status_code == 200:
                data = response.json()
                return data.get('result', [])
            else:
                return []
        except Exception as e:
            self.logger.error(f"Error getting fields for table {table_name}: {e}")
            return []
