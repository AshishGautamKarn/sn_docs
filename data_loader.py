"""
ServiceNow Data Loader
This module loads comprehensive ServiceNow table data with relationships and system parameters.
"""

from models import (
    ServiceNowDocumentation, ServiceNowModule, ServiceNowTable, TableField,
    TableRelationship, SystemParameter, ModuleType, TableType, RelationshipType
)


def create_sample_data() -> ServiceNowDocumentation:
    """Create comprehensive sample ServiceNow data"""
    
    # Initialize documentation structure
    doc = ServiceNowDocumentation()
    
    # Create ITSM Module
    itsm_module = ServiceNowModule(
        name="it_service_management",
        label="IT Service Management",
        description="Core ITSM functionality including incidents, problems, changes, and requests",
        module_type=ModuleType.ITSM
    )
    
    # Incident Management Tables
    incident_table = ServiceNowTable(
        name="incident",
        label="Incident",
        description="Records incidents reported by users or detected by monitoring systems",
        module=ModuleType.ITSM,
        table_type=TableType.BASE,
        fields=[
            TableField("number", "String", "Number", "Unique incident identifier", True, True),
            TableField("short_description", "String", "Short Description", "Brief description of the incident", True),
            TableField("description", "String", "Description", "Detailed description of the incident"),
            TableField("state", "Choice", "State", "Current state of the incident", True, choices=["New", "In Progress", "On Hold", "Resolved", "Closed", "Canceled"]),
            TableField("priority", "Choice", "Priority", "Business priority", True, choices=["1 - Critical", "2 - High", "3 - Moderate", "4 - Low", "5 - Planning"]),
            TableField("urgency", "Choice", "Urgency", "Technical urgency", True, choices=["1 - Critical", "2 - High", "3 - Moderate", "4 - Low"]),
            TableField("impact", "Choice", "Impact", "Business impact", True, choices=["1 - High", "2 - Medium", "3 - Low"]),
            TableField("category", "String", "Category", "Incident category"),
            TableField("subcategory", "String", "Subcategory", "Incident subcategory"),
            TableField("assigned_to", "Reference", "Assigned to", "User assigned to resolve the incident", reference_table="sys_user"),
            TableField("assignment_group", "Reference", "Assignment Group", "Group responsible for the incident", reference_table="sys_user_group"),
            TableField("caller_id", "Reference", "Caller", "Person who reported the incident", reference_table="sys_user"),
            TableField("opened_by", "Reference", "Opened by", "User who opened the incident", reference_table="sys_user"),
            TableField("resolved_by", "Reference", "Resolved by", "User who resolved the incident", reference_table="sys_user"),
            TableField("closed_by", "Reference", "Closed by", "User who closed the incident", reference_table="sys_user"),
            TableField("opened_at", "Date/Time", "Opened", "When the incident was opened", True),
            TableField("resolved_at", "Date/Time", "Resolved", "When the incident was resolved"),
            TableField("closed_at", "Date/Time", "Closed", "When the incident was closed"),
            TableField("work_notes", "Journal", "Work Notes", "Internal notes for incident resolution"),
            TableField("close_notes", "Journal", "Close Notes", "Notes explaining how the incident was resolved"),
            TableField("business_service", "Reference", "Business Service", "Affected business service", reference_table="cmdb_ci_service"),
            TableField("configuration_item", "Reference", "Configuration Item", "Affected configuration item", reference_table="cmdb_ci")
        ],
        system_parameters=[
            "glide.incident.default_priority",
            "glide.incident.default_urgency",
            "glide.incident.default_impact",
            "glide.incident.auto_close",
            "glide.incident.auto_resolve"
        ],
        business_rules=[
            "Incident State Change",
            "Incident Assignment",
            "Incident SLA Calculation",
            "Incident Auto-Close"
        ],
        scripts=[
            "Incident Before Insert",
            "Incident After Insert",
            "Incident Before Update",
            "Incident After Update"
        ],
        access_controls=[
            "incident.read",
            "incident.write",
            "incident.delete",
            "incident.admin"
        ]
    )
    
    # Problem Management Table
    problem_table = ServiceNowTable(
        name="problem",
        label="Problem",
        description="Records problems that cause multiple incidents or require investigation",
        module=ModuleType.ITSM,
        table_type=TableType.BASE,
        fields=[
            TableField("number", "String", "Number", "Unique problem identifier", True, True),
            TableField("short_description", "String", "Short Description", "Brief description of the problem", True),
            TableField("description", "String", "Description", "Detailed description of the problem"),
            TableField("state", "Choice", "State", "Current state of the problem", True, choices=["New", "In Progress", "On Hold", "Resolved", "Closed", "Canceled"]),
            TableField("priority", "Choice", "Priority", "Business priority", True, choices=["1 - Critical", "2 - High", "3 - Moderate", "4 - Low", "5 - Planning"]),
            TableField("urgency", "Choice", "Urgency", "Technical urgency", True, choices=["1 - Critical", "2 - High", "3 - Moderate", "4 - Low"]),
            TableField("impact", "Choice", "Impact", "Business impact", True, choices=["1 - High", "2 - Medium", "3 - Low"]),
            TableField("category", "String", "Category", "Problem category"),
            TableField("subcategory", "String", "Subcategory", "Problem subcategory"),
            TableField("assigned_to", "Reference", "Assigned to", "User assigned to resolve the problem", reference_table="sys_user"),
            TableField("assignment_group", "Reference", "Assignment Group", "Group responsible for the problem", reference_table="sys_user_group"),
            TableField("opened_by", "Reference", "Opened by", "User who opened the problem", reference_table="sys_user"),
            TableField("resolved_by", "Reference", "Resolved by", "User who resolved the problem", reference_table="sys_user"),
            TableField("closed_by", "Reference", "Closed by", "User who closed the problem", reference_table="sys_user"),
            TableField("opened_at", "Date/Time", "Opened", "When the problem was opened", True),
            TableField("resolved_at", "Date/Time", "Resolved", "When the problem was resolved"),
            TableField("closed_at", "Date/Time", "Closed", "When the problem was closed"),
            TableField("work_notes", "Journal", "Work Notes", "Internal notes for problem resolution"),
            TableField("close_notes", "Journal", "Close Notes", "Notes explaining how the problem was resolved"),
            TableField("root_cause", "Journal", "Root Cause", "Analysis of the root cause"),
            TableField("workaround", "Journal", "Workaround", "Temporary workaround for the problem")
        ],
        system_parameters=[
            "glide.problem.default_priority",
            "glide.problem.default_urgency",
            "glide.problem.default_impact",
            "glide.problem.auto_close"
        ]
    )
    
    # Change Management Table
    change_request_table = ServiceNowTable(
        name="change_request",
        label="Change Request",
        description="Records requests for changes to IT infrastructure and services",
        module=ModuleType.ITSM,
        table_type=TableType.BASE,
        fields=[
            TableField("number", "String", "Number", "Unique change request identifier", True, True),
            TableField("short_description", "String", "Short Description", "Brief description of the change", True),
            TableField("description", "String", "Description", "Detailed description of the change"),
            TableField("state", "Choice", "State", "Current state of the change", True, choices=["New", "Assess", "Authorize", "Scheduled", "Implement", "Review", "Closed", "Canceled"]),
            TableField("priority", "Choice", "Priority", "Business priority", True, choices=["1 - Critical", "2 - High", "3 - Moderate", "4 - Low", "5 - Planning"]),
            TableField("risk", "Choice", "Risk", "Risk level of the change", True, choices=["Low", "Medium", "High"]),
            TableField("type", "Choice", "Type", "Type of change", True, choices=["Normal", "Standard", "Emergency", "Minor"]),
            TableField("category", "String", "Category", "Change category"),
            TableField("subcategory", "String", "Subcategory", "Change subcategory"),
            TableField("assigned_to", "Reference", "Assigned to", "User assigned to implement the change", reference_table="sys_user"),
            TableField("assignment_group", "Reference", "Assignment Group", "Group responsible for the change", reference_table="sys_user_group"),
            TableField("requested_by", "Reference", "Requested by", "User who requested the change", reference_table="sys_user"),
            TableField("opened_by", "Reference", "Opened by", "User who opened the change request", reference_table="sys_user"),
            TableField("closed_by", "Reference", "Closed by", "User who closed the change request", reference_table="sys_user"),
            TableField("opened_at", "Date/Time", "Opened", "When the change request was opened", True),
            TableField("closed_at", "Date/Time", "Closed", "When the change request was closed"),
            TableField("work_notes", "Journal", "Work Notes", "Internal notes for change implementation"),
            TableField("close_notes", "Journal", "Close Notes", "Notes explaining the change outcome"),
            TableField("implementation_plan", "Journal", "Implementation Plan", "Detailed plan for implementing the change"),
            TableField("rollback_plan", "Journal", "Rollback Plan", "Plan for rolling back the change if needed"),
            TableField("test_plan", "Journal", "Test Plan", "Plan for testing the change")
        ],
        system_parameters=[
            "glide.change.default_priority",
            "glide.change.default_risk",
            "glide.change.default_type",
            "glide.change.auto_close"
        ]
    )
    
    # Request Management Table
    sc_request_table = ServiceNowTable(
        name="sc_request",
        label="Service Catalog Request",
        description="Records service requests from the service catalog",
        module=ModuleType.ITSM,
        table_type=TableType.BASE,
        fields=[
            TableField("number", "String", "Number", "Unique request identifier", True, True),
            TableField("short_description", "String", "Short Description", "Brief description of the request", True),
            TableField("description", "String", "Description", "Detailed description of the request"),
            TableField("state", "Choice", "State", "Current state of the request", True, choices=["New", "In Progress", "Approval", "Fulfillment", "Closed", "Canceled"]),
            TableField("priority", "Choice", "Priority", "Business priority", True, choices=["1 - Critical", "2 - High", "3 - Moderate", "4 - Low", "5 - Planning"]),
            TableField("requested_for", "Reference", "Requested for", "User the request is for", reference_table="sys_user"),
            TableField("requested_by", "Reference", "Requested by", "User who made the request", reference_table="sys_user"),
            TableField("assigned_to", "Reference", "Assigned to", "User assigned to fulfill the request", reference_table="sys_user"),
            TableField("assignment_group", "Reference", "Assignment Group", "Group responsible for the request", reference_table="sys_user_group"),
            TableField("opened_at", "Date/Time", "Opened", "When the request was opened", True),
            TableField("closed_at", "Date/Time", "Closed", "When the request was closed"),
            TableField("work_notes", "Journal", "Work Notes", "Internal notes for request fulfillment"),
            TableField("close_notes", "Journal", "Close Notes", "Notes explaining how the request was fulfilled")
        ],
        system_parameters=[
            "glide.sc_request.default_priority",
            "glide.sc_request.auto_close"
        ]
    )
    
    # System User Table
    sys_user_table = ServiceNowTable(
        name="sys_user",
        label="User",
        description="System users and their information",
        module=ModuleType.ITSM,
        table_type=TableType.SYSTEM,
        fields=[
            TableField("user_name", "String", "User Name", "Unique username", True, True),
            TableField("first_name", "String", "First Name", "User's first name"),
            TableField("last_name", "String", "Last Name", "User's last name"),
            TableField("email", "Email", "Email", "User's email address"),
            TableField("phone", "Phone Number", "Phone", "User's phone number"),
            TableField("department", "Reference", "Department", "User's department", reference_table="cmn_department"),
            TableField("location", "Reference", "Location", "User's location", reference_table="cmn_location"),
            TableField("manager", "Reference", "Manager", "User's manager", reference_table="sys_user"),
            TableField("active", "True/False", "Active", "Whether the user is active", True),
            TableField("locked_out", "True/False", "Locked Out", "Whether the user is locked out"),
            TableField("last_login", "Date/Time", "Last Login", "When the user last logged in")
        ],
        system_parameters=[
            "glide.user.default_password",
            "glide.user.password_policy",
            "glide.user.session_timeout"
        ]
    )
    
    # System User Group Table
    sys_user_group_table = ServiceNowTable(
        name="sys_user_group",
        label="Group",
        description="User groups for assignment and access control",
        module=ModuleType.ITSM,
        table_type=TableType.SYSTEM,
        fields=[
            TableField("name", "String", "Name", "Group name", True, True),
            TableField("description", "String", "Description", "Group description"),
            TableField("manager", "Reference", "Manager", "Group manager", reference_table="sys_user"),
            TableField("email", "Email", "Email", "Group email address"),
            TableField("active", "True/False", "Active", "Whether the group is active", True),
            TableField("cost_center", "Reference", "Cost Center", "Associated cost center", reference_table="cmn_cost_center")
        ]
    )
    
    # Add tables to ITSM module
    itsm_module.add_table(incident_table)
    itsm_module.add_table(problem_table)
    itsm_module.add_table(change_request_table)
    itsm_module.add_table(sc_request_table)
    itsm_module.add_table(sys_user_table)
    itsm_module.add_table(sys_user_group_table)
    
    # Create CSM Module
    csm_module = ServiceNowModule(
        name="customer_service_management",
        label="Customer Service Management",
        description="Customer service functionality including cases, knowledge, and customer portal",
        module_type=ModuleType.CSM
    )
    
    # Case Management Table
    case_table = ServiceNowTable(
        name="case",
        label="Case",
        description="Customer service cases for issue resolution and support",
        module=ModuleType.CSM,
        table_type=TableType.BASE,
        fields=[
            TableField("number", "String", "Number", "Unique case identifier", True, True),
            TableField("short_description", "String", "Short Description", "Brief description of the case", True),
            TableField("description", "String", "Description", "Detailed description of the case"),
            TableField("state", "Choice", "State", "Current state of the case", True, choices=["New", "In Progress", "On Hold", "Resolved", "Closed", "Canceled"]),
            TableField("priority", "Choice", "Priority", "Business priority", True, choices=["1 - Critical", "2 - High", "3 - Moderate", "4 - Low", "5 - Planning"]),
            TableField("category", "String", "Category", "Case category"),
            TableField("subcategory", "String", "Subcategory", "Case subcategory"),
            TableField("contact", "Reference", "Contact", "Customer contact", reference_table="customer_contact"),
            TableField("account", "Reference", "Account", "Customer account", reference_table="customer_account"),
            TableField("assigned_to", "Reference", "Assigned to", "Agent assigned to the case", reference_table="sys_user"),
            TableField("assignment_group", "Reference", "Assignment Group", "Group responsible for the case", reference_table="sys_user_group"),
            TableField("opened_at", "Date/Time", "Opened", "When the case was opened", True),
            TableField("resolved_at", "Date/Time", "Resolved", "When the case was resolved"),
            TableField("closed_at", "Date/Time", "Closed", "When the case was closed"),
            TableField("work_notes", "Journal", "Work Notes", "Internal notes for case resolution"),
            TableField("close_notes", "Journal", "Close Notes", "Notes explaining how the case was resolved")
        ],
        system_parameters=[
            "glide.case.default_priority",
            "glide.case.auto_close",
            "glide.case.sla_enabled"
        ]
    )
    
    # Customer Account Table
    customer_account_table = ServiceNowTable(
        name="customer_account",
        label="Customer Account",
        description="Customer accounts and their information",
        module=ModuleType.CSM,
        table_type=TableType.BASE,
        fields=[
            TableField("name", "String", "Name", "Account name", True, True),
            TableField("description", "String", "Description", "Account description"),
            TableField("account_type", "Choice", "Account Type", "Type of account", choices=["Customer", "Partner", "Prospect"]),
            TableField("industry", "String", "Industry", "Account industry"),
            TableField("website", "URL", "Website", "Account website"),
            TableField("phone", "Phone Number", "Phone", "Account phone number"),
            TableField("email", "Email", "Email", "Account email address"),
            TableField("address", "String", "Address", "Account address"),
            TableField("city", "String", "City", "Account city"),
            TableField("state", "String", "State", "Account state"),
            TableField("country", "String", "Country", "Account country"),
            TableField("zip", "String", "ZIP Code", "Account ZIP code"),
            TableField("account_manager", "Reference", "Account Manager", "Assigned account manager", reference_table="sys_user"),
            TableField("active", "True/False", "Active", "Whether the account is active", True)
        ]
    )
    
    # Customer Contact Table
    customer_contact_table = ServiceNowTable(
        name="customer_contact",
        label="Customer Contact",
        description="Customer contacts and their information",
        module=ModuleType.CSM,
        table_type=TableType.BASE,
        fields=[
            TableField("first_name", "String", "First Name", "Contact's first name"),
            TableField("last_name", "String", "Last Name", "Contact's last name", True),
            TableField("email", "Email", "Email", "Contact's email address", True),
            TableField("phone", "Phone Number", "Phone", "Contact's phone number"),
            TableField("mobile_phone", "Phone Number", "Mobile Phone", "Contact's mobile phone"),
            TableField("title", "String", "Title", "Contact's job title"),
            TableField("department", "String", "Department", "Contact's department"),
            TableField("account", "Reference", "Account", "Associated customer account", reference_table="customer_account"),
            TableField("primary", "True/False", "Primary", "Whether this is the primary contact"),
            TableField("active", "True/False", "Active", "Whether the contact is active", True)
        ]
    )
    
    # Add tables to CSM module
    csm_module.add_table(case_table)
    csm_module.add_table(customer_account_table)
    csm_module.add_table(customer_contact_table)
    
    # Create HRSD Module
    hrsd_module = ServiceNowModule(
        name="hr_service_delivery",
        label="HR Service Delivery",
        description="Human resources service delivery including employee requests and HR processes",
        module_type=ModuleType.HRSD
    )
    
    # HR Case Table
    hr_case_table = ServiceNowTable(
        name="hr_case",
        label="HR Case",
        description="Human resources cases for employee requests and issues",
        module=ModuleType.HRSD,
        table_type=TableType.BASE,
        fields=[
            TableField("number", "String", "Number", "Unique HR case identifier", True, True),
            TableField("short_description", "String", "Short Description", "Brief description of the HR case", True),
            TableField("description", "String", "Description", "Detailed description of the HR case"),
            TableField("state", "Choice", "State", "Current state of the HR case", True, choices=["New", "In Progress", "On Hold", "Resolved", "Closed", "Canceled"]),
            TableField("priority", "Choice", "Priority", "Business priority", True, choices=["1 - Critical", "2 - High", "3 - Moderate", "4 - Low", "5 - Planning"]),
            TableField("category", "String", "Category", "HR case category"),
            TableField("subcategory", "String", "Subcategory", "HR case subcategory"),
            TableField("requested_for", "Reference", "Requested for", "Employee the case is for", reference_table="sys_user"),
            TableField("requested_by", "Reference", "Requested by", "Employee who requested the case", reference_table="sys_user"),
            TableField("assigned_to", "Reference", "Assigned to", "HR agent assigned to the case", reference_table="sys_user"),
            TableField("assignment_group", "Reference", "Assignment Group", "HR group responsible for the case", reference_table="sys_user_group"),
            TableField("opened_at", "Date/Time", "Opened", "When the HR case was opened", True),
            TableField("resolved_at", "Date/Time", "Resolved", "When the HR case was resolved"),
            TableField("closed_at", "Date/Time", "Closed", "When the HR case was closed"),
            TableField("work_notes", "Journal", "Work Notes", "Internal notes for HR case resolution"),
            TableField("close_notes", "Journal", "Close Notes", "Notes explaining how the HR case was resolved")
        ],
        system_parameters=[
            "glide.hr_case.default_priority",
            "glide.hr_case.auto_close"
        ]
    )
    
    # Add tables to HRSD module
    hrsd_module.add_table(hr_case_table)
    
    # Add modules to documentation
    doc.modules.append(itsm_module)
    doc.modules.append(csm_module)
    doc.modules.append(hrsd_module)
    
    # Create global system parameters
    doc.global_system_parameters = [
        SystemParameter(
            name="glide.incident.default_priority",
            description="Default priority for new incidents",
            default_value="3 - Moderate",
            impact_level="Medium",
            affects_tables=["incident"],
            documentation_url="https://docs.servicenow.com/bundle/itsm-incident-management/page/administer/incident-management/concept/c_IncidentPriority.html"
        ),
        SystemParameter(
            name="glide.incident.default_urgency",
            description="Default urgency for new incidents",
            default_value="3 - Moderate",
            impact_level="Medium",
            affects_tables=["incident"],
            documentation_url="https://docs.servicenow.com/bundle/itsm-incident-management/page/administer/incident-management/concept/c_IncidentUrgency.html"
        ),
        SystemParameter(
            name="glide.incident.default_impact",
            description="Default impact for new incidents",
            default_value="3 - Low",
            impact_level="Medium",
            affects_tables=["incident"],
            documentation_url="https://docs.servicenow.com/bundle/itsm-incident-management/page/administer/incident-management/concept/c_IncidentImpact.html"
        ),
        SystemParameter(
            name="glide.incident.auto_close",
            description="Enable automatic closure of resolved incidents",
            default_value="false",
            impact_level="High",
            affects_tables=["incident"],
            documentation_url="https://docs.servicenow.com/bundle/itsm-incident-management/page/administer/incident-management/concept/c_AutoCloseIncidents.html"
        ),
        SystemParameter(
            name="glide.incident.auto_resolve",
            description="Enable automatic resolution of incidents",
            default_value="false",
            impact_level="High",
            affects_tables=["incident"],
            documentation_url="https://docs.servicenow.com/bundle/itsm-incident-management/page/administer/incident-management/concept/c_AutoResolveIncidents.html"
        ),
        SystemParameter(
            name="glide.problem.default_priority",
            description="Default priority for new problems",
            default_value="3 - Moderate",
            impact_level="Medium",
            affects_tables=["problem"],
            documentation_url="https://docs.servicenow.com/bundle/itsm-problem-management/page/administer/problem-management/concept/c_ProblemPriority.html"
        ),
        SystemParameter(
            name="glide.change.default_priority",
            description="Default priority for new change requests",
            default_value="3 - Moderate",
            impact_level="Medium",
            affects_tables=["change_request"],
            documentation_url="https://docs.servicenow.com/bundle/itsm-change-management/page/administer/change-management/concept/c_ChangePriority.html"
        ),
        SystemParameter(
            name="glide.change.default_risk",
            description="Default risk level for new change requests",
            default_value="Medium",
            impact_level="Medium",
            affects_tables=["change_request"],
            documentation_url="https://docs.servicenow.com/bundle/itsm-change-management/page/administer/change-management/concept/c_ChangeRisk.html"
        ),
        SystemParameter(
            name="glide.sc_request.default_priority",
            description="Default priority for new service catalog requests",
            default_value="3 - Moderate",
            impact_level="Medium",
            affects_tables=["sc_request"],
            documentation_url="https://docs.servicenow.com/bundle/service-catalog/page/administer/service-catalog/concept/c_RequestPriority.html"
        ),
        SystemParameter(
            name="glide.case.default_priority",
            description="Default priority for new customer service cases",
            default_value="3 - Moderate",
            impact_level="Medium",
            affects_tables=["case"],
            documentation_url="https://docs.servicenow.com/bundle/csm/page/administer/customer-service-management/concept/c_CasePriority.html"
        ),
        SystemParameter(
            name="glide.hr_case.default_priority",
            description="Default priority for new HR cases",
            default_value="3 - Moderate",
            impact_level="Medium",
            affects_tables=["hr_case"],
            documentation_url="https://docs.servicenow.com/bundle/hr-service-delivery/page/administer/hr-service-delivery/concept/c_HRCasePriority.html"
        ),
        SystemParameter(
            name="glide.user.default_password",
            description="Default password for new users",
            default_value="changeme",
            impact_level="High",
            affects_tables=["sys_user"],
            documentation_url="https://docs.servicenow.com/bundle/rome-platform-security/page/administer/security/concept/c_UserPasswordPolicy.html"
        ),
        SystemParameter(
            name="glide.user.password_policy",
            description="Password policy configuration",
            default_value="default",
            impact_level="High",
            affects_tables=["sys_user"],
            documentation_url="https://docs.servicenow.com/bundle/rome-platform-security/page/administer/security/concept/c_UserPasswordPolicy.html"
        ),
        SystemParameter(
            name="glide.user.session_timeout",
            description="User session timeout in minutes",
            default_value="30",
            impact_level="Medium",
            affects_tables=["sys_user"],
            documentation_url="https://docs.servicenow.com/bundle/rome-platform-security/page/administer/security/concept/c_UserSessionTimeout.html"
        )
    ]
    
    # Create global relationships
    doc.global_relationships = [
        TableRelationship(
            source_table="incident",
            target_table="sys_user",
            relationship_type=RelationshipType.REFERENCE,
            source_field="assigned_to",
            target_field="sys_id",
            description="Incident assigned to user"
        ),
        TableRelationship(
            source_table="incident",
            target_table="sys_user_group",
            relationship_type=RelationshipType.REFERENCE,
            source_field="assignment_group",
            target_field="sys_id",
            description="Incident assigned to group"
        ),
        TableRelationship(
            source_table="incident",
            target_table="sys_user",
            relationship_type=RelationshipType.REFERENCE,
            source_field="caller_id",
            target_field="sys_id",
            description="Incident reported by user"
        ),
        TableRelationship(
            source_table="problem",
            target_table="incident",
            relationship_type=RelationshipType.ONE_TO_MANY,
            source_field="sys_id",
            target_field="problem_id",
            description="Problem can have multiple related incidents"
        ),
        TableRelationship(
            source_table="change_request",
            target_table="sys_user",
            relationship_type=RelationshipType.REFERENCE,
            source_field="assigned_to",
            target_field="sys_id",
            description="Change request assigned to user"
        ),
        TableRelationship(
            source_table="sc_request",
            target_table="sys_user",
            relationship_type=RelationshipType.REFERENCE,
            source_field="requested_for",
            target_field="sys_id",
            description="Service request for user"
        ),
        TableRelationship(
            source_table="case",
            target_table="customer_contact",
            relationship_type=RelationshipType.REFERENCE,
            source_field="contact",
            target_field="sys_id",
            description="Case associated with customer contact"
        ),
        TableRelationship(
            source_table="case",
            target_table="customer_account",
            relationship_type=RelationshipType.REFERENCE,
            source_field="account",
            target_field="sys_id",
            description="Case associated with customer account"
        ),
        TableRelationship(
            source_table="customer_contact",
            target_table="customer_account",
            relationship_type=RelationshipType.MANY_TO_ONE,
            source_field="account",
            target_field="sys_id",
            description="Contact belongs to account"
        ),
        TableRelationship(
            source_table="hr_case",
            target_table="sys_user",
            relationship_type=RelationshipType.REFERENCE,
            source_field="requested_for",
            target_field="sys_id",
            description="HR case requested for employee"
        ),
        TableRelationship(
            source_table="sys_user",
            target_table="sys_user_group",
            relationship_type=RelationshipType.MANY_TO_MANY,
            source_field="sys_id",
            target_field="sys_id",
            description="Users can belong to multiple groups"
        ),
        TableRelationship(
            source_table="sys_user",
            target_table="sys_user",
            relationship_type=RelationshipType.REFERENCE,
            source_field="manager",
            target_field="sys_id",
            description="User's manager"
        )
    ]
    
    return doc


def load_servicenow_data() -> ServiceNowDocumentation:
    """Load ServiceNow documentation data"""
    return create_sample_data()
