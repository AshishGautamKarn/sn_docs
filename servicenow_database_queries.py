"""
ServiceNow Database Queries
Pre-configured, secure queries for ServiceNow database operations
"""

import logging
from typing import Dict, List, Any, Optional
from sqlalchemy import text
import re


class ServiceNowDatabaseQueries:
    """Secure, pre-configured queries for ServiceNow database operations"""
    
    def __init__(self):
        self.logger = self._setup_logger()
        
        # Security: Query validation patterns
        self.allowed_table_patterns = [
            r'^sys_[a-zA-Z_]+$',
            r'^sc_[a-zA-Z_]+$',
            r'^kb_[a-zA-Z_]+$',
            r'^cmdb_[a-zA-Z_]+$',
            r'^u_[a-zA-Z_]+$'
        ]
        
        # Security: Dangerous SQL patterns to block
        self.dangerous_patterns = [
            r'DROP\s+TABLE',
            r'DELETE\s+FROM',
            r'UPDATE\s+.*SET',
            r'INSERT\s+INTO',
            r'ALTER\s+TABLE',
            r'CREATE\s+TABLE',
            r'TRUNCATE\s+TABLE',
            r'EXEC\s+',
            r'EXECUTE\s+',
            r'UNION\s+SELECT',
            r'--',
            r'/\*.*\*/',
            r';\s*$'
        ]
    
    def _setup_logger(self) -> logging.Logger:
        """Setup secure logging"""
        logger = logging.getLogger('servicenow_database_queries')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _validate_table_name(self, table_name: str) -> bool:
        """Validate table name against allowed patterns"""
        if not table_name:
            return False
        
        # Security: Check against allowed patterns
        for pattern in self.allowed_table_patterns:
            if re.match(pattern, table_name, re.IGNORECASE):
                return True
        
        return False
    
    def _validate_query(self, query: str) -> bool:
        """Validate query for dangerous patterns"""
        if not query:
            return False
        
        query_upper = query.upper()
        
        # Security: Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, query_upper, re.IGNORECASE):
                self.logger.warning(f"Dangerous pattern detected in query: {pattern}")
                return False
        
        return True
    
    def _sanitize_parameter(self, param: Any) -> str:
        """Sanitize query parameters"""
        if param is None:
            return 'NULL'
        
        # Security: Convert to string and escape
        param_str = str(param)
        
        # Security: Remove potential injection characters
        param_str = re.sub(r'[;\'"\\]', '', param_str)
        
        return param_str
    
    def get_instance_info_queries(self) -> Dict[str, str]:
        """Get queries for ServiceNow instance information"""
        return {
            'version': """
                SELECT value 
                FROM sys_properties 
                WHERE name = 'glide.buildname' 
                LIMIT 1
            """,
            'build_date': """
                SELECT value 
                FROM sys_properties 
                WHERE name = 'glide.builddate' 
                LIMIT 1
            """,
            'instance_name': """
                SELECT value 
                FROM sys_properties 
                WHERE name = 'glide.instance_name' 
                LIMIT 1
            """,
            'timezone': """
                SELECT value 
                FROM sys_properties 
                WHERE name = 'glide.sys.timezone' 
                LIMIT 1
            """,
            'max_upload_size': """
                SELECT value 
                FROM sys_properties 
                WHERE name = 'glide.ui.attachment.max_size' 
                LIMIT 1
            """
        }
    
    def get_modules_queries(self) -> Dict[str, str]:
        """Get queries for ServiceNow modules/applications"""
        return {
            'all_applications': """
                SELECT 
                    sys_id,
                    name,
                    version,
                    active,
                    description,
                    created_on,
                    updated_on
                FROM sys_app 
                ORDER BY name
            """,
            'active_applications': """
                SELECT 
                    sys_id,
                    name,
                    version,
                    active,
                    description,
                    created_on,
                    updated_on
                FROM sys_app 
                WHERE active = true 
                ORDER BY name
            """,
            'application_by_name': """
                SELECT 
                    sys_id,
                    name,
                    version,
                    active,
                    description,
                    created_on,
                    updated_on
                FROM sys_app 
                WHERE name = :app_name
                LIMIT 1
            """,
            'application_plugins': """
                SELECT 
                    p.sys_id,
                    p.name,
                    p.version,
                    p.active,
                    p.description,
                    a.name as application_name
                FROM sys_plugin p
                LEFT JOIN sys_app a ON p.source = a.sys_id
                WHERE p.active = true
                ORDER BY a.name, p.name
            """
        }
    
    def get_roles_queries(self) -> Dict[str, str]:
        """Get queries for ServiceNow roles"""
        return {
            'all_roles': """
                SELECT 
                    sys_id,
                    name,
                    description,
                    active,
                    created_on,
                    updated_on
                FROM sys_user_role 
                ORDER BY name
            """,
            'active_roles': """
                SELECT 
                    sys_id,
                    name,
                    description,
                    active,
                    created_on,
                    updated_on
                FROM sys_user_role 
                WHERE active = true 
                ORDER BY name
            """,
            'role_by_name': """
                SELECT 
                    sys_id,
                    name,
                    description,
                    active,
                    created_on,
                    updated_on
                FROM sys_user_role 
                WHERE name = :role_name
                LIMIT 1
            """,
            'role_assignments': """
                SELECT 
                    r.name as role_name,
                    u.name as user_name,
                    u.email as user_email,
                    u.active as user_active
                FROM sys_user_role r
                JOIN sys_user_has_role ur ON r.sys_id = ur.role
                JOIN sys_user u ON ur.user = u.sys_id
                WHERE r.active = true AND u.active = true
                ORDER BY r.name, u.name
            """
        }
    
    def get_tables_queries(self) -> Dict[str, str]:
        """Get queries for ServiceNow tables"""
        return {
            'all_tables': """
                SELECT 
                    name,
                    label,
                    super_class,
                    class_name,
                    sys_class_name,
                    created_on,
                    updated_on
                FROM sys_db_object 
                WHERE super_class IS NOT NULL
                ORDER BY name
            """,
            'tables_by_module': """
                SELECT 
                    d.name,
                    d.label,
                    d.super_class,
                    d.class_name,
                    d.sys_class_name,
                    a.name as application_name
                FROM sys_db_object d
                LEFT JOIN sys_app a ON d.sys_package = a.sys_id
                WHERE d.super_class IS NOT NULL
                AND a.name = :module_name
                ORDER BY d.name
            """,
            'table_columns': """
                SELECT 
                    column_name,
                    internal_type,
                    max_length,
                    reference,
                    reference_key,
                    is_nullable,
                    default_value
                FROM sys_dictionary 
                WHERE name = :table_name
                ORDER BY column_order
            """,
            'table_relationships': """
                SELECT 
                    source_table,
                    target_table,
                    source_field,
                    target_field,
                    relationship_type
                FROM sys_db_object_relationship 
                WHERE source_table = :table_name 
                OR target_table = :table_name
                ORDER BY source_table, target_table
            """
        }
    
    def get_properties_queries(self) -> Dict[str, str]:
        """Get queries for ServiceNow system properties"""
        return {
            'all_properties': """
                SELECT 
                    name,
                    value,
                    description,
                    type,
                    is_private,
                    created_on,
                    updated_on
                FROM sys_properties 
                ORDER BY name
            """,
            'properties_by_category': """
                SELECT 
                    name,
                    value,
                    description,
                    type,
                    is_private,
                    created_on,
                    updated_on
                FROM sys_properties 
                WHERE name LIKE :category_pattern
                ORDER BY name
            """,
            'glide_properties': """
                SELECT 
                    name,
                    value,
                    description,
                    type,
                    is_private,
                    created_on,
                    updated_on
                FROM sys_properties 
                WHERE name LIKE 'glide.%'
                ORDER BY name
            """,
            'security_properties': """
                SELECT 
                    name,
                    value,
                    description,
                    type,
                    is_private,
                    created_on,
                    updated_on
                FROM sys_properties 
                WHERE name LIKE 'glide.security.%'
                OR name LIKE 'glide.authenticate.%'
                ORDER BY name
            """
        }
    
    def get_scheduled_jobs_queries(self) -> Dict[str, str]:
        """Get queries for ServiceNow scheduled jobs"""
        return {
            'all_jobs': """
                SELECT 
                    sys_id,
                    name,
                    description,
                    script,
                    run_script,
                    run_script_override,
                    active,
                    next_run,
                    last_run,
                    created_on,
                    updated_on
                FROM sysauto_script 
                ORDER BY name
            """,
            'active_jobs': """
                SELECT 
                    sys_id,
                    name,
                    description,
                    script,
                    run_script,
                    run_script_override,
                    active,
                    next_run,
                    last_run,
                    created_on,
                    updated_on
                FROM sysauto_script 
                WHERE active = true 
                ORDER BY name
            """,
            'job_by_name': """
                SELECT 
                    sys_id,
                    name,
                    description,
                    script,
                    run_script,
                    run_script_override,
                    active,
                    next_run,
                    last_run,
                    created_on,
                    updated_on
                FROM sysauto_script 
                WHERE name = :job_name
                LIMIT 1
            """,
            'job_execution_history': """
                SELECT 
                    sys_id,
                    job,
                    started_on,
                    completed_on,
                    status,
                    output
                FROM sysauto_script_execution 
                WHERE job = :job_id
                ORDER BY started_on DESC
                LIMIT 100
            """
        }
    
    def get_users_queries(self) -> Dict[str, str]:
        """Get queries for ServiceNow users"""
        return {
            'all_users': """
                SELECT 
                    sys_id,
                    user_name,
                    first_name,
                    last_name,
                    email,
                    active,
                    last_login_time,
                    created_on,
                    updated_on
                FROM sys_user 
                ORDER BY user_name
            """,
            'active_users': """
                SELECT 
                    sys_id,
                    user_name,
                    first_name,
                    last_name,
                    email,
                    active,
                    last_login_time,
                    created_on,
                    updated_on
                FROM sys_user 
                WHERE active = true 
                ORDER BY user_name
            """,
            'user_by_name': """
                SELECT 
                    sys_id,
                    user_name,
                    first_name,
                    last_name,
                    email,
                    active,
                    last_login_time,
                    created_on,
                    updated_on
                FROM sys_user 
                WHERE user_name = :user_name
                LIMIT 1
            """,
            'user_roles': """
                SELECT 
                    u.user_name,
                    r.name as role_name,
                    r.description as role_description
                FROM sys_user u
                JOIN sys_user_has_role ur ON u.sys_id = ur.user
                JOIN sys_user_role r ON ur.role = r.sys_id
                WHERE u.active = true AND r.active = true
                ORDER BY u.user_name, r.name
            """
        }
    
    def get_security_queries(self) -> Dict[str, str]:
        """Get queries for ServiceNow security information"""
        return {
            'access_controls': """
                SELECT 
                    sys_id,
                    name,
                    operation,
                    script,
                    active,
                    created_on,
                    updated_on
                FROM sys_security_acl 
                WHERE active = true 
                ORDER BY name
            """,
            'security_roles': """
                SELECT 
                    sys_id,
                    name,
                    description,
                    active,
                    created_on,
                    updated_on
                FROM sys_user_role 
                WHERE name LIKE '%admin%' 
                OR name LIKE '%security%'
                OR name LIKE '%audit%'
                ORDER BY name
            """,
            'login_methods': """
                SELECT 
                    name,
                    value,
                    description
                FROM sys_properties 
                WHERE name LIKE 'glide.authenticate.%'
                ORDER BY name
            """,
            'password_policies': """
                SELECT 
                    name,
                    value,
                    description
                FROM sys_properties 
                WHERE name LIKE 'glide.password.%'
                ORDER BY name
            """
        }
    
    def get_performance_queries(self) -> Dict[str, str]:
        """Get queries for ServiceNow performance information"""
        return {
            'table_sizes': """
                SELECT 
                    schemaname,
                    tablename,
                    attname,
                    n_distinct,
                    correlation
                FROM pg_stats 
                WHERE schemaname = 'public'
                ORDER BY tablename, attname
            """,
            'index_usage': """
                SELECT 
                    schemaname,
                    tablename,
                    indexname,
                    idx_scan,
                    idx_tup_read,
                    idx_tup_fetch
                FROM pg_stat_user_indexes 
                ORDER BY idx_scan DESC
            """,
            'slow_queries': """
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    rows
                FROM pg_stat_statements 
                ORDER BY total_time DESC
                LIMIT 50
            """
        }
    
    def execute_secure_query(self, query_name: str, query_type: str, parameters: Dict[str, Any] = None) -> str:
        """Execute a secure query by name and type"""
        try:
            # Security: Validate query name and type
            if not query_name or not query_type:
                raise ValueError("Query name and type are required")
            
            # Security: Get query based on type
            queries = self._get_queries_by_type(query_type)
            if query_name not in queries:
                raise ValueError(f"Query '{query_name}' not found in type '{query_type}'")
            
            query = queries[query_name]
            
            # Security: Validate query
            if not self._validate_query(query):
                raise ValueError("Query contains dangerous patterns")
            
            # Security: Sanitize parameters
            if parameters:
                sanitized_params = {}
                for key, value in parameters.items():
                    sanitized_params[key] = self._sanitize_parameter(value)
                parameters = sanitized_params
            
            return query
            
        except Exception as e:
            self.logger.error(f"Error executing secure query: {e}")
            raise
    
    def _get_queries_by_type(self, query_type: str) -> Dict[str, str]:
        """Get queries by type"""
        query_methods = {
            'instance_info': self.get_instance_info_queries,
            'modules': self.get_modules_queries,
            'roles': self.get_roles_queries,
            'tables': self.get_tables_queries,
            'properties': self.get_properties_queries,
            'scheduled_jobs': self.get_scheduled_jobs_queries,
            'users': self.get_users_queries,
            'security': self.get_security_queries,
            'performance': self.get_performance_queries
        }
        
        if query_type not in query_methods:
            raise ValueError(f"Unknown query type: {query_type}")
        
        return query_methods[query_type]()
    
    def get_table_analysis_query(self, table_name: str) -> str:
        """Get comprehensive table analysis query"""
        if not self._validate_table_name(table_name):
            raise ValueError(f"Invalid table name: {table_name}")
        
        return f"""
            SELECT 
                t.name as table_name,
                t.label as table_label,
                t.super_class,
                t.class_name,
                COUNT(d.column_name) as column_count,
                COUNT(CASE WHEN d.internal_type = 'reference' THEN 1 END) as reference_columns,
                COUNT(CASE WHEN d.is_nullable = false THEN 1 END) as required_columns,
                t.created_on,
                t.updated_on
            FROM sys_db_object t
            LEFT JOIN sys_dictionary d ON t.name = d.name
            WHERE t.name = :table_name
            GROUP BY t.name, t.label, t.super_class, t.class_name, t.created_on, t.updated_on
        """
    
    def get_relationship_analysis_query(self, table_name: str) -> str:
        """Get table relationship analysis query"""
        if not self._validate_table_name(table_name):
            raise ValueError(f"Invalid table name: {table_name}")
        
        return f"""
            SELECT 
                r.source_table,
                r.target_table,
                r.source_field,
                r.target_field,
                r.relationship_type,
                s.label as source_label,
                t.label as target_label
            FROM sys_db_object_relationship r
            LEFT JOIN sys_db_object s ON r.source_table = s.name
            LEFT JOIN sys_db_object t ON r.target_table = t.name
            WHERE r.source_table = :table_name 
            OR r.target_table = :table_name
            ORDER BY r.source_table, r.target_table
        """
    
    def get_custom_application_queries(self, app_name: str) -> Dict[str, str]:
        """Get queries for custom application analysis"""
        if not app_name:
            raise ValueError("Application name is required")
        
        # Security: Sanitize app name
        app_name = self._sanitize_parameter(app_name)
        
        return {
            'app_tables': f"""
                SELECT 
                    d.name,
                    d.label,
                    d.super_class,
                    d.class_name,
                    d.created_on,
                    d.updated_on
                FROM sys_db_object d
                JOIN sys_app a ON d.sys_package = a.sys_id
                WHERE a.name = :app_name
                ORDER BY d.name
            """,
            'app_scripts': f"""
                SELECT 
                    s.name,
                    s.script,
                    s.active,
                    s.created_on,
                    s.updated_on
                FROM sys_script s
                JOIN sys_app a ON s.sys_package = a.sys_id
                WHERE a.name = :app_name
                ORDER BY s.name
            """,
            'app_business_rules': f"""
                SELECT 
                    br.name,
                    br.script,
                    br.active,
                    br.table,
                    br.created_on,
                    br.updated_on
                FROM sys_script br
                JOIN sys_app a ON br.sys_package = a.sys_id
                WHERE a.name = :app_name
                AND br.name LIKE '%business%'
                ORDER BY br.name
            """
        }

# Created By: Ashish Gautam; LinkedIn: https://www.linkedin.com/in/ashishgautamkarn/
