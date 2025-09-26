"""
Demo script for Enhanced Interactive Visualizations
Shows the key features of the new visualization system
"""

import streamlit as st
from database import DatabaseManager
from interactive_visualizer import InteractiveServiceNowVisualizer

def main():
    st.title("🎯 Enhanced Visualization Demo")
    
    st.markdown("""
    ## 🚀 New Interactive Visualization Features
    
    The enhanced visualization page now includes:
    
    ### 🔍 Module Explorer
    - **Interactive Module Selection**: Choose any module to explore in detail
    - **Component Drill-Down**: Navigate through roles, tables, properties, and scheduled jobs
    - **Search & Filter**: Find specific components within modules
    - **Real-time Metrics**: Live statistics for each module
    
    ### 📊 Module Comparison
    - **Side-by-Side Comparison**: Compare modules across different metrics
    - **Visual Charts**: Bar charts and graphs for easy comparison
    - **Export Options**: Download comparison data as CSV
    
    ### 🌐 Global Analytics
    - **System-wide Overview**: Total counts across all modules
    - **Distribution Analysis**: Pie charts and bar charts for global distribution
    - **Trend Analysis**: Creation timelines and patterns
    
    ### 📈 Custom Analysis
    - **Component Distribution**: Heatmaps and scatter plots
    - **Module Complexity**: Complexity scoring and ranking
    - **Creation Timeline**: Detailed timeline analysis
    - **Custom Queries**: Advanced analysis options
    
    ### 🔗 Relationship Analysis
    - **Table Relationships**: Network graphs showing table connections
    - **Role Dependencies**: Permission and dependency analysis
    - **Property Categories**: Property type and scope analysis
    
    ## 🎮 How to Use
    
    1. **Navigate to Visualizations**: Click on "📈 Visualizations" in the sidebar
    2. **Explore Modules**: Use the "Module Explorer" tab to select and explore modules
    3. **Drill Down**: Choose component types (Roles, Tables, Properties, Jobs) to explore
    4. **Search & Filter**: Use search boxes to find specific items
    5. **Compare**: Use "Module Comparison" to compare different modules
    6. **Analyze**: Use "Global Analytics" for system-wide insights
    7. **Custom Analysis**: Use "Custom Analysis" for advanced visualizations
    
    ## ✨ Key Benefits
    
    - **Interactive Exploration**: Click and navigate through your ServiceNow data
    - **Real-time Updates**: All visualizations update based on current database content
    - **Multiple Views**: Different visualization types for different analysis needs
    - **Export Capabilities**: Download data and charts for further analysis
    - **Responsive Design**: Works on different screen sizes
    - **Search & Filter**: Quickly find what you're looking for
    
    ## 🎯 Use Cases
    
    - **Module Analysis**: Understand the structure and complexity of each module
    - **Component Discovery**: Find specific roles, tables, or properties
    - **System Overview**: Get a high-level view of your ServiceNow instance
    - **Documentation**: Generate visual documentation of your ServiceNow setup
    - **Planning**: Use complexity analysis for implementation planning
    - **Auditing**: Track creation timelines and changes
    """)
    
    # Show current database status
    st.markdown("---")
    st.markdown("### 🗄️ Current Database Status")
    
    try:
        db_manager = DatabaseManager()
        session = db_manager.get_session()
        
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
            
            if module_count > 0:
                st.success("✅ Database has data - Enhanced visualizations are ready!")
                st.info("Navigate to the main application to explore the enhanced visualizations.")
            else:
                st.warning("⚠️ Database is empty - Run the comprehensive scraper first to populate data.")
                
        finally:
            session.close()
            
    except Exception as e:
        st.error(f"Database error: {e}")
    
    # Quick preview of visualization features
    st.markdown("---")
    st.markdown("### 🎨 Visualization Preview")
    
    if module_count > 0:
        st.markdown("""
        **Available Visualizations:**
        
        1. **🔍 Module Explorer**: Interactive module selection and component exploration
        2. **📊 Module Comparison**: Side-by-side module comparison charts
        3. **🌐 Global Analytics**: System-wide statistics and distributions
        4. **📈 Custom Analysis**: Advanced analysis including complexity scoring
        
        **Interactive Features:**
        - Click to explore modules and components
        - Search and filter capabilities
        - Real-time data updates
        - Export options for charts and data
        - Responsive design for all screen sizes
        """)
    else:
        st.info("Run the comprehensive scraper to populate the database and unlock all visualization features.")

if __name__ == "__main__":
    main()
