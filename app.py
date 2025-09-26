"""
ServiceNow Advanced Visual Documentation
Main Streamlit application for interactive ServiceNow table documentation.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from typing import List, Dict, Optional

from models import ServiceNowDocumentation, ServiceNowTable, ModuleType, TableType, RelationshipType
from data_loader import load_servicenow_data
from visualization import ServiceNowVisualizer, create_annotation_popup


# Page configuration
st.set_page_config(
    page_title="ServiceNow Visual Documentation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    
    .section-header {
        font-size: 1.5rem;
        color: #A23B72;
        margin-top: 2rem;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2E86AB;
        margin-bottom: 1rem;
    }
    
    .table-info {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
    
    .parameter-info {
        background-color: #fff3cd;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 3px solid #ffc107;
        margin-bottom: 0.5rem;
    }
    
    .relationship-info {
        background-color: #d1ecf1;
        padding: 0.5rem;
        border-radius: 0.3rem;
        border-left: 3px solid #17a2b8;
        margin-bottom: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #2E86AB;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load ServiceNow data with caching"""
    return load_servicenow_data()


def main():
    """Main application function"""
    
    # Load data
    doc = load_data()
    visualizer = ServiceNowVisualizer(doc)
    
    # Header
    st.markdown('<h1 class="main-header">📊 ServiceNow Advanced Visual Documentation</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎛️ Navigation")
        
        # Module selection
        st.markdown("### 📁 Select Modules")
        available_modules = [module.name for module in doc.modules]
        selected_modules = st.multiselect(
            "Choose modules to display:",
            available_modules,
            default=available_modules[:2]  # Default to first 2 modules
        )
        
        # Table selection
        st.markdown("### 🗂️ Select Tables")
        all_tables = doc.get_all_tables()
        table_names = [table.name for table in all_tables]
        selected_tables = st.multiselect(
            "Choose specific tables:",
            table_names,
            default=[]
        )
        
        # Visualization type
        st.markdown("### 📈 Visualization Type")
        viz_type = st.selectbox(
            "Choose visualization:",
            ["Network Graph", "Hierarchical Tree", "Module Overview", "Relationship Matrix"]
        )
        
        # Statistics
        st.markdown("### 📊 Statistics")
        stats = visualizer.get_table_statistics()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Tables", stats['total_tables'])
            st.metric("Total Fields", stats['total_fields'])
        with col2:
            st.metric("Relationships", stats['total_relationships'])
            st.metric("Parameters", stats['total_parameters'])
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Dashboard", 
        "🔗 Relationships", 
        "📋 Table Details", 
        "⚙️ System Parameters", 
        "📤 Export"
    ])
    
    with tab1:
        st.markdown('<h2 class="section-header">📊 Dashboard Overview</h2>', 
                    unsafe_allow_html=True)
        
        # Module statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Module Statistics")
            module_fig = visualizer.create_module_overview()
            st.plotly_chart(module_fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Module Details")
            for module in doc.modules:
                with st.expander(f"📁 {module.label}"):
                    st.write(f"**Description:** {module.description}")
                    st.write(f"**Tables:** {len(module.tables)}")
                    st.write(f"**Type:** {module.module_type.value}")
                    
                    # Show tables in this module
                    st.write("**Tables in this module:**")
                    for table in module.tables:
                        st.write(f"• {table.label} ({table.name})")
        
        # Recent activity (simulated)
        st.markdown("### 🔄 Recent Activity")
        activity_data = {
            "Time": ["2024-01-15 10:30", "2024-01-15 09:45", "2024-01-15 09:15", "2024-01-15 08:30"],
            "Action": ["Table Updated", "Relationship Added", "Parameter Modified", "New Table Created"],
            "Table": ["incident", "problem", "change_request", "case"],
            "User": ["admin", "developer", "admin", "developer"]
        }
        activity_df = pd.DataFrame(activity_data)
        st.dataframe(activity_df, use_container_width=True)
    
    with tab2:
        st.markdown('<h2 class="section-header">🔗 Table Relationships</h2>', 
                    unsafe_allow_html=True)
        
        # Visualization controls
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if viz_type == "Network Graph":
                fig = visualizer.create_network_visualization(selected_modules, selected_tables)
                st.plotly_chart(fig, use_container_width=True)
            elif viz_type == "Hierarchical Tree":
                root_table = st.selectbox("Select root table:", table_names, index=0)
                fig = visualizer.create_hierarchical_tree(root_table)
                st.plotly_chart(fig, use_container_width=True)
            elif viz_type == "Module Overview":
                fig = visualizer.create_module_overview()
                st.plotly_chart(fig, use_container_width=True)
            elif viz_type == "Relationship Matrix":
                fig = visualizer.create_relationship_matrix()
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 🔍 Relationship Details")
            
            # Show relationships for selected tables
            if selected_tables:
                for table_name in selected_tables[:3]:  # Show first 3 selected tables
                    table = doc.get_table_by_name(table_name)
                    if table:
                        relationships = doc.get_relationships_for_table(table_name)
                        
                        st.markdown(f"**{table.label}**")
                        for rel in relationships[:5]:  # Show first 5 relationships
                            st.markdown(f"""
                            <div class="relationship-info">
                                <strong>{rel.source_table}</strong> → <strong>{rel.target_table}</strong><br>
                                <small>Type: {rel.relationship_type.value}</small><br>
                                <small>{rel.description}</small>
                            </div>
                            """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown('<h2 class="section-header">📋 Table Details</h2>', 
                    unsafe_allow_html=True)
        
        # Table selection
        selected_table_name = st.selectbox("Select table to view details:", table_names)
        
        if selected_table_name:
            table = doc.get_table_by_name(selected_table_name)
            
            if table:
                # Table information
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"""
                    <div class="table-info">
                        <h3>{table.label}</h3>
                        <p><strong>Table Name:</strong> {table.name}</p>
                        <p><strong>Module:</strong> {table.module.value}</p>
                        <p><strong>Type:</strong> {table.table_type.value}</p>
                        <p><strong>Description:</strong> {table.description}</p>
                        <p><strong>Fields:</strong> {len(table.fields)}</p>
                        <p><strong>System Parameters:</strong> {len(table.system_parameters)}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Field type distribution
                    field_fig = visualizer.create_table_field_analysis(selected_table_name)
                    st.plotly_chart(field_fig, use_container_width=True)
                
                # Fields details
                st.markdown("### 📝 Fields")
                fields_data = []
                for field in table.fields:
                    fields_data.append({
                        "Name": field.name,
                        "Type": field.type,
                        "Label": field.label,
                        "Description": field.description,
                        "Mandatory": "Yes" if field.mandatory else "No",
                        "Unique": "Yes" if field.unique else "No",
                        "Reference Table": field.reference_table or "",
                        "Default Value": field.default_value or ""
                    })
                
                fields_df = pd.DataFrame(fields_data)
                st.dataframe(fields_df, use_container_width=True)
                
                # Relationships
                st.markdown("### 🔗 Relationships")
                relationships = doc.get_relationships_for_table(selected_table_name)
                
                if relationships:
                    rel_data = []
                    for rel in relationships:
                        rel_data.append({
                            "Source Table": rel.source_table,
                            "Target Table": rel.target_table,
                            "Type": rel.relationship_type.value,
                            "Source Field": rel.source_field,
                            "Target Field": rel.target_field,
                            "Description": rel.description
                        })
                    
                    rel_df = pd.DataFrame(rel_data)
                    st.dataframe(rel_df, use_container_width=True)
                else:
                    st.info("No relationships found for this table.")
                
                # Business rules and scripts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📋 Business Rules")
                    if table.business_rules:
                        for rule in table.business_rules:
                            st.write(f"• {rule}")
                    else:
                        st.info("No business rules defined.")
                
                with col2:
                    st.markdown("### 🔧 Scripts")
                    if table.scripts:
                        for script in table.scripts:
                            st.write(f"• {script}")
                    else:
                        st.info("No scripts defined.")
    
    with tab4:
        st.markdown('<h2 class="section-header">⚙️ System Parameters</h2>', 
                    unsafe_allow_html=True)
        
        # Parameter search
        search_param = st.text_input("🔍 Search parameters:", placeholder="Enter parameter name...")
        
        # Filter parameters
        filtered_params = doc.global_system_parameters
        if search_param:
            filtered_params = [p for p in filtered_params if search_param.lower() in p.name.lower()]
        
        # Parameter details
        for param in filtered_params:
            st.markdown(f"""
            <div class="parameter-info">
                <h4>{param.name}</h4>
                <p><strong>Description:</strong> {param.description}</p>
                <p><strong>Default Value:</strong> {param.default_value}</p>
                <p><strong>Current Value:</strong> {param.current_value or "Not set"}</p>
                <p><strong>Impact Level:</strong> {param.impact_level}</p>
                <p><strong>Affects Tables:</strong> {', '.join(param.affects_tables)}</p>
                {f'<p><strong>Documentation:</strong> <a href="{param.documentation_url}" target="_blank">View Documentation</a></p>' if param.documentation_url else ''}
            </div>
            """, unsafe_allow_html=True)
        
        # Parameter by table
        st.markdown("### 📊 Parameters by Table")
        table_param_data = []
        for table in all_tables:
            for param_name in table.system_parameters:
                param = next((p for p in doc.global_system_parameters if p.name == param_name), None)
                if param:
                    table_param_data.append({
                        "Table": table.label,
                        "Parameter": param.name,
                        "Description": param.description,
                        "Impact": param.impact_level
                    })
        
        if table_param_data:
            table_param_df = pd.DataFrame(table_param_data)
            st.dataframe(table_param_df, use_container_width=True)
        else:
            st.info("No parameters found.")
    
    with tab5:
        st.markdown('<h2 class="section-header">📤 Export Documentation</h2>', 
                    unsafe_allow_html=True)
        
        # Export options
        export_format = st.selectbox("Select export format:", ["JSON", "CSV", "Markdown"])
        
        if st.button("📥 Generate Export"):
            if export_format == "JSON":
                # Export as JSON
                export_data = {
                    "modules": [],
                    "global_parameters": [],
                    "global_relationships": []
                }
                
                for module in doc.modules:
                    module_data = {
                        "name": module.name,
                        "label": module.label,
                        "description": module.description,
                        "module_type": module.module_type.value,
                        "tables": []
                    }
                    
                    for table in module.tables:
                        table_data = {
                            "name": table.name,
                            "label": table.label,
                            "description": table.description,
                            "table_type": table.table_type.value,
                            "fields": [
                                {
                                    "name": field.name,
                                    "type": field.type,
                                    "label": field.label,
                                    "description": field.description,
                                    "mandatory": field.mandatory,
                                    "unique": field.unique,
                                    "reference_table": field.reference_table
                                }
                                for field in table.fields
                            ],
                            "system_parameters": table.system_parameters,
                            "business_rules": table.business_rules,
                            "scripts": table.scripts
                        }
                        module_data["tables"].append(table_data)
                    
                    export_data["modules"].append(module_data)
                
                export_data["global_parameters"] = [
                    {
                        "name": param.name,
                        "description": param.description,
                        "default_value": param.default_value,
                        "impact_level": param.impact_level,
                        "affects_tables": param.affects_tables
                    }
                    for param in doc.global_system_parameters
                ]
                
                export_data["global_relationships"] = [
                    {
                        "source_table": rel.source_table,
                        "target_table": rel.target_table,
                        "relationship_type": rel.relationship_type.value,
                        "source_field": rel.source_field,
                        "target_field": rel.target_field,
                        "description": rel.description
                    }
                    for rel in doc.global_relationships
                ]
                
                json_str = json.dumps(export_data, indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_str,
                    file_name="servicenow_documentation.json",
                    mime="application/json"
                )
            
            elif export_format == "CSV":
                # Export tables as CSV
                tables_data = []
                for table in all_tables:
                    tables_data.append({
                        "Table Name": table.name,
                        "Label": table.label,
                        "Module": table.module.value,
                        "Type": table.table_type.value,
                        "Description": table.description,
                        "Field Count": len(table.fields),
                        "System Parameters": len(table.system_parameters)
                    })
                
                tables_df = pd.DataFrame(tables_data)
                csv = tables_df.to_csv(index=False)
                
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="servicenow_tables.csv",
                    mime="text/csv"
                )
            
            elif export_format == "Markdown":
                # Export as Markdown
                markdown_content = "# ServiceNow Documentation\n\n"
                
                for module in doc.modules:
                    markdown_content += f"## {module.label}\n\n"
                    markdown_content += f"**Description:** {module.description}\n\n"
                    markdown_content += f"**Module Type:** {module.module_type.value}\n\n"
                    
                    for table in module.tables:
                        markdown_content += f"### {table.label}\n\n"
                        markdown_content += f"**Table Name:** {table.name}\n\n"
                        markdown_content += f"**Description:** {table.description}\n\n"
                        markdown_content += f"**Type:** {table.table_type.value}\n\n"
                        
                        markdown_content += "#### Fields\n\n"
                        for field in table.fields:
                            markdown_content += f"- **{field.name}** ({field.type}): {field.description}\n"
                        
                        markdown_content += "\n#### System Parameters\n\n"
                        for param in table.system_parameters:
                            markdown_content += f"- {param}\n"
                        
                        markdown_content += "\n---\n\n"
                
                st.download_button(
                    label="📥 Download Markdown",
                    data=markdown_content,
                    file_name="servicenow_documentation.md",
                    mime="text/markdown"
                )
        
        # Documentation statistics
        st.markdown("### 📊 Export Statistics")
        stats = visualizer.get_table_statistics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Modules", len(doc.modules))
        with col2:
            st.metric("Tables", stats['total_tables'])
        with col3:
            st.metric("Fields", stats['total_fields'])
        with col4:
            st.metric("Parameters", stats['total_parameters'])


if __name__ == "__main__":
    main()
