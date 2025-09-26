    # Get current database connection details
    current_db_config = get_current_db_connection_details()
    
    # Database Configuration Section
    st.markdown("### ⚙️ Current Database Configuration")
    
    # Show configuration status
    col_status, col_refresh = st.columns([3, 1])
