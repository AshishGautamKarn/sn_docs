"""
Configuration Management System
Manages configuration for ServiceNow documentation system.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_type: str = "postgresql"
    host: str = "localhost"
    port: int = 5432
    database_name: str = "sn_docs"
    username: str = "postgres"
    password: str = ""
    connection_pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False


@dataclass
class ScraperConfig:
    """Web scraper configuration"""
    base_url: str = "https://www.servicenow.com/docs"
    max_pages: int = 100
    delay_seconds: int = 1
    timeout_seconds: int = 30
    use_selenium: bool = False
    discover_links: bool = True
    max_concurrent_requests: int = 5
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    chrome_options: list = None
    
    def __post_init__(self):
        if self.chrome_options is None:
            self.chrome_options = [
                "--headless",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1920,1080"
            ]


@dataclass
class VisualizationConfig:
    """Visualization configuration"""
    default_layout: str = "spring"
    node_size_multiplier: float = 2.0
    edge_width: float = 2.0
    color_scheme: str = "default"
    animation_duration: int = 1000
    max_nodes_display: int = 100
    enable_interactions: bool = True


@dataclass
class AutomationConfig:
    """Automation configuration"""
    auto_scrape_enabled: bool = False
    scrape_schedule: str = "daily"
    scrape_time: str = "02:00"
    data_retention_days: int = 30
    auto_cleanup_enabled: bool = True
    validation_enabled: bool = True
    backup_enabled: bool = True
    backup_schedule: str = "weekly"


@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_ssl: bool = True
    allowed_hosts: list = None
    api_key_required: bool = False
    rate_limit_enabled: bool = True
    max_requests_per_minute: int = 60
    
    def __post_init__(self):
        if self.allowed_hosts is None:
            self.allowed_hosts = ["localhost", "127.0.0.1"]


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/sn_docs.log"
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    console_output: bool = True


@dataclass
class ServiceNowConfig:
    """ServiceNow system configuration"""
    instance_url: str = ""
    username: str = ""
    password: str = ""
    api_version: str = "v2"
    timeout: int = 30
    verify_ssl: bool = True
    max_retries: int = 3


class ConfigManager:
    """Configuration manager for ServiceNow documentation system"""
    
    def __init__(self, config_file: str = "config.yaml"):
        self.config_file = Path(config_file)
        self.logger = self._setup_logger()
        
        # Initialize default configurations
        self.database = DatabaseConfig()
        self.scraper = ScraperConfig()
        self.visualization = VisualizationConfig()
        self.automation = AutomationConfig()
        self.security = SecurityConfig()
        self.logging = LoggingConfig()
        self.servicenow = ServiceNowConfig()
        
        # Load configuration from file and environment
        self.load_configuration()
    
    def _setup_logger(self) -> logging.Logger:
        """Setup logging for configuration management"""
        logger = logging.getLogger('config_manager')
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def load_configuration(self):
        """Load configuration from file and environment variables"""
        # Load from YAML file if it exists
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                    self._apply_config_data(config_data)
                self.logger.info(f"Configuration loaded from {self.config_file}")
            except Exception as e:
                self.logger.error(f"Error loading configuration file: {e}")
        
        # Override with environment variables
        self._load_from_environment()
        
        # Create logs directory if it doesn't exist
        log_dir = Path(self.logging.file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
    
    def _apply_config_data(self, config_data: Dict[str, Any]):
        """Apply configuration data to config objects"""
        if 'database' in config_data:
            self._update_config_object(self.database, config_data['database'])
        
        if 'scraper' in config_data:
            self._update_config_object(self.scraper, config_data['scraper'])
        
        if 'visualization' in config_data:
            self._update_config_object(self.visualization, config_data['visualization'])
        
        if 'automation' in config_data:
            self._update_config_object(self.automation, config_data['automation'])
        
        if 'security' in config_data:
            self._update_config_object(self.security, config_data['security'])
        
        if 'logging' in config_data:
            self._update_config_object(self.logging, config_data['logging'])
        
        if 'servicenow' in config_data:
            self._update_config_object(self.servicenow, config_data['servicenow'])
    
    def _update_config_object(self, config_obj, data: Dict[str, Any]):
        """Update configuration object with data"""
        for key, value in data.items():
            if hasattr(config_obj, key):
                setattr(config_obj, key, value)
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        # Database configuration
        self.database.db_type = os.getenv('DB_TYPE', self.database.db_type)
        self.database.host = os.getenv('DB_HOST', self.database.host)
        self.database.port = int(os.getenv('DB_PORT', self.database.port))
        self.database.database_name = os.getenv('DB_NAME', self.database.database_name)
        self.database.username = os.getenv('DB_USER', self.database.username)
        self.database.password = os.getenv('DB_PASSWORD', self.database.password)
        
        # Scraper configuration
        self.scraper.base_url = os.getenv('SCRAPER_BASE_URL', self.scraper.base_url)
        self.scraper.max_pages = int(os.getenv('SCRAPER_MAX_PAGES', self.scraper.max_pages))
        self.scraper.delay_seconds = int(os.getenv('SCRAPER_DELAY', self.scraper.delay_seconds))
        self.scraper.use_selenium = os.getenv('SCRAPER_USE_SELENIUM', 'false').lower() == 'true'
        
        # ServiceNow configuration
        self.servicenow.instance_url = os.getenv('SN_INSTANCE_URL', self.servicenow.instance_url)
        self.servicenow.username = os.getenv('SN_USERNAME', self.servicenow.username)
        self.servicenow.password = os.getenv('SN_PASSWORD', self.servicenow.password)
        
        # Logging configuration
        self.logging.level = os.getenv('LOG_LEVEL', self.logging.level)
        self.logging.file_path = os.getenv('LOG_FILE', self.logging.file_path)
    
    def save_configuration(self):
        """Save current configuration to file"""
        config_data = {
            'database': asdict(self.database),
            'scraper': asdict(self.scraper),
            'visualization': asdict(self.visualization),
            'automation': asdict(self.automation),
            'security': asdict(self.security),
            'logging': asdict(self.logging),
            'servicenow': asdict(self.servicenow)
        }
        
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
            self.logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
    
    def get_database_url(self) -> str:
        """Get database connection URL"""
        if self.database.db_type == 'postgresql':
            return f"postgresql://{self.database.username}:{self.database.password}@{self.database.host}:{self.database.port}/{self.database.database_name}"
        elif self.database.db_type == 'mysql':
            return f"mysql+pymysql://{self.database.username}:{self.database.password}@{self.database.host}:{self.database.port}/{self.database.database_name}"
        else:
            raise ValueError(f"Unsupported database type: {self.database.db_type}")
    
    def get_scraper_urls(self) -> list:
        """Get default scraper URLs"""
        return [
            "https://www.servicenow.com/docs/bundle/zurich-it-operations-management/page/product/event-management/reference/r_InstalledWithEventManagement.html",
            "https://www.servicenow.com/docs/bundle/rome-platform-security/page/administer/security/concept/c_UserRoles.html",
            "https://www.servicenow.com/docs/bundle/rome-platform-administration/page/administer/security/concept/c_SystemProperties.html"
        ]
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Validate configuration and return validation results"""
        validation_results = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validate database configuration
        if not self.database.host:
            validation_results['errors'].append("Database host is required")
            validation_results['valid'] = False
        
        if not self.database.database_name:
            validation_results['errors'].append("Database name is required")
            validation_results['valid'] = False
        
        if not self.database.username:
            validation_results['errors'].append("Database username is required")
            validation_results['valid'] = False
        
        # Validate scraper configuration
        if self.scraper.max_pages <= 0:
            validation_results['errors'].append("Scraper max pages must be positive")
            validation_results['valid'] = False
        
        if self.scraper.delay_seconds < 0:
            validation_results['errors'].append("Scraper delay must be non-negative")
            validation_results['valid'] = False
        
        # Validate ServiceNow configuration
        if self.servicenow.instance_url and not self.servicenow.username:
            validation_results['warnings'].append("ServiceNow instance URL provided but no username")
        
        # Validate logging configuration
        if self.logging.level not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            validation_results['errors'].append("Invalid logging level")
            validation_results['valid'] = False
        
        return validation_results
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            'database': {
                'type': self.database.db_type,
                'host': self.database.host,
                'port': self.database.port,
                'database': self.database.database_name,
                'username': self.database.username
            },
            'scraper': {
                'base_url': self.scraper.base_url,
                'max_pages': self.scraper.max_pages,
                'delay_seconds': self.scraper.delay_seconds,
                'use_selenium': self.scraper.use_selenium
            },
            'automation': {
                'auto_scrape_enabled': self.automation.auto_scrape_enabled,
                'scrape_schedule': self.automation.scrape_schedule,
                'data_retention_days': self.automation.data_retention_days
            },
            'servicenow': {
                'instance_url': self.servicenow.instance_url,
                'api_version': self.servicenow.api_version,
                'timeout': self.servicenow.timeout
            }
        }


# Global configuration instance
config = ConfigManager()


def get_config() -> ConfigManager:
    """Get global configuration instance"""
    return config


def create_sample_config_file():
    """Create a sample configuration file"""
    sample_config = {
        'database': {
            'db_type': 'postgresql',
            'host': 'localhost',
            'port': 5432,
            'database_name': 'sn_docs',
            'username': 'postgres',
            'password': 'password',
            'connection_pool_size': 10,
            'max_overflow': 20,
            'echo': False
        },
        'scraper': {
            'base_url': 'https://www.servicenow.com/docs',
            'max_pages': 100,
            'delay_seconds': 1,
            'timeout_seconds': 30,
            'use_selenium': False,
            'discover_links': True,
            'max_concurrent_requests': 5,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'chrome_options': [
                '--headless',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--window-size=1920,1080'
            ]
        },
        'visualization': {
            'default_layout': 'spring',
            'node_size_multiplier': 2.0,
            'edge_width': 2.0,
            'color_scheme': 'default',
            'animation_duration': 1000,
            'max_nodes_display': 100,
            'enable_interactions': True
        },
        'automation': {
            'auto_scrape_enabled': False,
            'scrape_schedule': 'daily',
            'scrape_time': '02:00',
            'data_retention_days': 30,
            'auto_cleanup_enabled': True,
            'validation_enabled': True,
            'backup_enabled': True,
            'backup_schedule': 'weekly'
        },
        'security': {
            'enable_ssl': True,
            'allowed_hosts': ['localhost', '127.0.0.1'],
            'api_key_required': False,
            'rate_limit_enabled': True,
            'max_requests_per_minute': 60
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file_path': 'logs/sn_docs.log',
            'max_file_size': 10485760,
            'backup_count': 5,
            'console_output': True
        },
        'servicenow': {
            'instance_url': '',
            'username': '',
            'password': '',
            'api_version': 'v2',
            'timeout': 30,
            'verify_ssl': True,
            'max_retries': 3
        }
    }
    
    with open('config.yaml', 'w') as f:
        yaml.dump(sample_config, f, default_flow_style=False, indent=2)
    
    print("✅ Sample configuration file created: config.yaml")


if __name__ == "__main__":
    # Test configuration
    config_manager = ConfigManager()
    
    print("📋 Configuration Summary:")
    summary = config_manager.get_config_summary()
    print(json.dumps(summary, indent=2))
    
    print("\n✅ Configuration Validation:")
    validation = config_manager.validate_configuration()
    print(json.dumps(validation, indent=2))
    
    # Create sample config file
    create_sample_config_file()

# Created By: Ashish Gautam; LinkedIn: https://www.linkedin.com/in/ashishgautamkarn/
