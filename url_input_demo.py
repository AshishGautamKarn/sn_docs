"""
Demo of Enhanced Comprehensive Scraper with URL Input
Shows the new URL input functionality
"""

import streamlit as st
from comprehensive_scraper_ui import ComprehensiveScraperUI

def main():
    st.title("🔗 Enhanced Comprehensive Scraper Demo")
    
    st.markdown("""
    ## 🆕 New URL Input Features
    
    The comprehensive scraper now includes URL input functionality:
    
    ### 📡 Data Source Options
    
    1. **Generate Comprehensive Data**: Creates realistic ServiceNow data based on known patterns
    2. **Scrape from URLs**: Processes specific ServiceNow documentation URLs
    3. **Both**: Combines comprehensive data generation with URL scraping
    
    ### 🔗 URL Input Methods
    
    #### Manual Entry
    - Enter URLs directly in a text area
    - One URL per line
    - Supports any ServiceNow documentation URL
    
    #### Preset URLs
    - Pre-configured URL sets for different modules:
      - **Event Management**: Event management documentation
      - **Security & Roles**: User roles and security documentation
      - **System Properties**: System properties documentation
      - **Service Management**: Service management documentation
      - **Asset Management**: Asset management documentation
      - **All Presets**: All available preset URLs
    
    ### 🎯 How to Use URL Input
    
    1. **Select Data Source**: Choose "Scrape from URLs" or "Both"
    2. **Choose Input Method**: Select "Manual Entry" or "Preset URLs"
    3. **Configure URLs**: 
       - For manual entry: Paste URLs in the text area
       - For presets: Select from dropdown
    4. **Configure Settings**: Set timeout, workers, logging, etc.
    5. **Run Scraper**: Click "Run Comprehensive Scraper"
    
    ### 📊 What Happens with URLs
    
    When you provide URLs, the scraper will:
    - Process each URL individually
    - Generate sample data based on URL content
    - Extract module information from URL patterns
    - Create roles, tables, properties, and scheduled jobs based on URL context
    - Save all generated data to the database
    
    ### 🔍 URL Processing Features
    
    - **Module Detection**: Automatically detects module type from URL
    - **Sample Generation**: Creates realistic sample data for each URL (4 items per URL: role, table, property, scheduled job)
    - **Progress Tracking**: Shows progress for each URL being processed
    - **Error Handling**: Gracefully handles failed URL processing
    - **Detailed Logging**: Shows detailed information about each URL processed
    
    ### 📋 Example URLs
    
    ```
    https://www.servicenow.com/docs/bundle/zurich-it-operations-management/page/product/event-management/reference/r_InstalledWithEventManagement.html
    https://www.servicenow.com/docs/bundle/rome-platform-security/page/administer/security/concept/c_UserRoles.html
    https://www.servicenow.com/docs/bundle/rome-platform-administration/page/administer/security/concept/c_SystemProperties.html
    ```
    
    ### 🎮 Try It Out
    
    Navigate to the main application and:
    1. Go to "🕷️ Comprehensive Scraper"
    2. Select "Scrape from URLs" or "Both"
    3. Choose your preferred URL input method
    4. Configure your URLs
    5. Run the scraper and see the results!
    """)
    
    # Show current configuration
    st.markdown("---")
    st.markdown("### ⚙️ Current Configuration Preview")
    
    # Create a sample configuration
    sample_config = {
        "Data Source": "Scrape from URLs",
        "URL Input Method": "Preset URLs",
        "Selected Preset": "All Presets",
        "URLs Count": 5,
        "Timeout": 60,
        "Max Workers": 3,
        "Detailed Logging": True,
        "Save to Database": True,
        "Modules": ["Event Management", "Security", "Administration", "Service Management", "Asset Management"],
        "Data Types": ["Roles", "Tables", "Properties", "Scheduled Jobs"]
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Configuration:**")
        for key, value in sample_config.items():
            st.text(f"• {key}: {value}")
    
    with col2:
        st.markdown("**Expected Results:**")
        st.text("• 5 URLs processed")
        st.text("• ~20 items generated (4 per URL)")
        st.text("• All items saved to database")
        st.text("• Detailed progress logging")
        st.text("• Sample data preview")
    
    st.info("🚀 The enhanced comprehensive scraper is now running on **http://localhost:8506** with full URL input functionality including scheduled jobs!")

if __name__ == "__main__":
    main()
