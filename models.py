"""
ServiceNow Table Documentation Models
This module defines the data structures for ServiceNow tables, relationships, and system parameters.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum


class ModuleType(Enum):
    """ServiceNow module types"""
    ITSM = "IT Service Management"
    CSM = "Customer Service Management"
    HRSD = "HR Service Delivery"
    FSM = "Field Service Management"
    GRC = "Governance, Risk & Compliance"
    SECOPS = "Security Operations"
    ITOM = "IT Operations Management"
    APM = "Application Portfolio Management"
    PPM = "Project Portfolio Management"
    IRM = "Integrated Risk Management"
    CUSTOM = "Custom Application"


class TableType(Enum):
    """ServiceNow table types"""
    BASE = "Base Table"
    EXTENSION = "Extension Table"
    CUSTOM = "Custom Table"
    SYSTEM = "System Table"
    VIEW = "Database View"
    TEMP = "Temporary Table"


class RelationshipType(Enum):
    """Relationship types between tables"""
    ONE_TO_ONE = "1:1"
    ONE_TO_MANY = "1:M"
    MANY_TO_ONE = "M:1"
    MANY_TO_MANY = "M:M"
    PARENT_CHILD = "Parent-Child"
    REFERENCE = "Reference"
    EXTENSION = "Extension"


@dataclass
class SystemParameter:
    """System parameter that affects table functionality"""
    name: str
    description: str
    default_value: str
    current_value: Optional[str] = None
    impact_level: str = "Medium"  # Low, Medium, High, Critical
    affects_tables: List[str] = field(default_factory=list)
    documentation_url: Optional[str] = None


@dataclass
class TableField:
    """Individual field/column in a ServiceNow table"""
    name: str
    type: str
    label: str
    description: str
    mandatory: bool = False
    unique: bool = False
    reference_table: Optional[str] = None
    choices: List[str] = field(default_factory=list)
    default_value: Optional[str] = None
    max_length: Optional[int] = None


@dataclass
class TableRelationship:
    """Relationship between two tables"""
    source_table: str
    target_table: str
    relationship_type: RelationshipType
    source_field: str
    target_field: str
    description: str
    cascade_delete: bool = False
    cascade_update: bool = False


@dataclass
class ServiceNowRole:
    """ServiceNow role definition"""
    name: str
    description: str
    module: ModuleType
    permissions: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    created_by: Optional[str] = None
    last_updated: Optional[str] = None


@dataclass
class ServiceNowProperty:
    """ServiceNow system property definition"""
    name: str
    description: str
    module: ModuleType
    value: str
    type: str  # string, boolean, integer, etc.
    default_value: Optional[str] = None
    is_encrypted: bool = False
    created_by: Optional[str] = None
    last_updated: Optional[str] = None


@dataclass
class ServiceNowScheduledJob:
    """ServiceNow scheduled job definition"""
    name: str
    description: str
    module: ModuleType
    frequency: str
    script: str
    active: bool = True
    next_run: Optional[str] = None
    last_run: Optional[str] = None
    created_by: Optional[str] = None
    last_updated: Optional[str] = None


@dataclass
class ServiceNowTable:
    """ServiceNow table definition with all metadata"""
    name: str
    label: str
    description: str
    module: ModuleType
    table_type: TableType
    fields: List[TableField] = field(default_factory=list)
    relationships: List[TableRelationship] = field(default_factory=list)
    system_parameters: List[str] = field(default_factory=list)
    business_rules: List[str] = field(default_factory=list)
    scripts: List[str] = field(default_factory=list)
    access_controls: List[str] = field(default_factory=list)
    documentation_url: Optional[str] = None
    last_updated: Optional[str] = None
    created_by: Optional[str] = None
    
    def get_field_by_name(self, field_name: str) -> Optional[TableField]:
        """Get field by name"""
        for field in self.fields:
            if field.name == field_name:
                return field
        return None
    
    def get_reference_tables(self) -> Set[str]:
        """Get all tables referenced by this table"""
        referenced = set()
        for field in self.fields:
            if field.reference_table:
                referenced.add(field.reference_table)
        return referenced
    
    def get_referencing_tables(self, all_tables: List['ServiceNowTable']) -> Set[str]:
        """Get all tables that reference this table"""
        referencing = set()
        for table in all_tables:
            if self.name in table.get_reference_tables():
                referencing.add(table.name)
        return referencing


@dataclass
class ServiceNowModule:
    """ServiceNow module containing multiple tables"""
    name: str
    label: str
    description: str
    module_type: ModuleType
    tables: List[ServiceNowTable] = field(default_factory=list)
    system_parameters: List[SystemParameter] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    
    def add_table(self, table: ServiceNowTable):
        """Add a table to this module"""
        self.tables.append(table)
    
    def get_table_by_name(self, table_name: str) -> Optional[ServiceNowTable]:
        """Get table by name"""
        for table in self.tables:
            if table.name == table_name:
                return table
        return None


@dataclass
class ServiceNowDocumentation:
    """Complete ServiceNow documentation structure"""
    modules: List[ServiceNowModule] = field(default_factory=list)
    global_system_parameters: List[SystemParameter] = field(default_factory=list)
    global_relationships: List[TableRelationship] = field(default_factory=list)
    
    def get_all_tables(self) -> List[ServiceNowTable]:
        """Get all tables across all modules"""
        all_tables = []
        for module in self.modules:
            all_tables.extend(module.tables)
        return all_tables
    
    def get_table_by_name(self, table_name: str) -> Optional[ServiceNowTable]:
        """Get table by name across all modules"""
        for module in self.modules:
            table = module.get_table_by_name(table_name)
            if table:
                return table
        return None
    
    def get_module_by_name(self, module_name: str) -> Optional[ServiceNowModule]:
        """Get module by name"""
        for module in self.modules:
            if module.name == module_name:
                return module
        return None
    
    def get_relationships_for_table(self, table_name: str) -> List[TableRelationship]:
        """Get all relationships for a specific table"""
        relationships = []
        for rel in self.global_relationships:
            if rel.source_table == table_name or rel.target_table == table_name:
                relationships.append(rel)
        return relationships

# Created By: Ashish Gautam; LinkedIn: https://www.linkedin.com/in/ashishgautamkarn/
