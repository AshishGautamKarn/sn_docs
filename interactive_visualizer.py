"""
Enhanced Interactive Visualizations for ServiceNow Data
Provides interactive exploration of modules and their components
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import networkx as nx
from typing import List, Dict, Any, Optional
import json

class InteractiveServiceNowVisualizer:
    """Enhanced interactive visualizer for ServiceNow data"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.session = None
    
    def get_session(self):
        """Get database session"""
        if not self.session:
            self.session = self.db_manager.get_session()
        return self.session
    
    def close_session(self):
        """Close database session"""
        if self.session:
            self.session.close()
            self.session = None
    
    def get_module_data(self) -> Dict[str, Any]:
        """Get comprehensive module data"""
        session = self.get_session()
        try:
            from database import ServiceNowModule, ServiceNowRole, ServiceNowTable, ServiceNowProperty, ServiceNowScheduledJob
            
            modules = session.query(ServiceNowModule).all()
            roles = session.query(ServiceNowRole).all()
            tables = session.query(ServiceNowTable).all()
            properties = session.query(ServiceNowProperty).all()
            jobs = session.query(ServiceNowScheduledJob).all()
            
            # Organize data by module
            module_data = {}
            for module in modules:
                module_roles = [r for r in roles if r.module_id == module.id]
                module_tables = [t for t in tables if t.module_id == module.id]
                module_properties = [p for p in properties if p.module_id == module.id]
                module_jobs = [j for j in jobs if j.module_id == module.id]
                
                module_data[module.name] = {
                    'module': module,
                    'roles': module_roles,
                    'tables': module_tables,
                    'properties': module_properties,
                    'jobs': module_jobs,
                    'total_items': len(module_roles) + len(module_tables) + len(module_properties) + len(module_jobs)
                }
            
            return module_data
            
        except Exception as e:
            st.error(f"Error retrieving module data: {e}")
            return {}
    
    def show_module_overview(self, module_data: Dict[str, Any]):
        """Show interactive module overview"""
        st.markdown("### 📦 Module Overview")
        
        if not module_data:
            st.info("No module data available. Please run the comprehensive scraper first.")
            return
        
        # Create module selection
        module_names = list(module_data.keys())
        selected_module = st.selectbox(
            "Select Module to Explore:",
            module_names,
            help="Choose a module to explore its components in detail"
        )
        
        if selected_module:
            module_info = module_data[selected_module]
            
            # Display module metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric("Total Items", module_info['total_items'])
            with col2:
                st.metric("Roles", len(module_info['roles']))
            with col3:
                st.metric("Tables", len(module_info['tables']))
            with col4:
                st.metric("Properties", len(module_info['properties']))
            with col5:
                st.metric("Scheduled Jobs", len(module_info['jobs']))
            
            # Module details
            st.markdown(f"#### 📋 {selected_module} Details")
            
            module = module_info['module']
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"**Description:** {module.description or 'No description available'}")
                st.markdown(f"**Type:** {module.module_type or 'Unknown'}")
                st.markdown(f"**Version:** {module.version or 'Unknown'}")
            
            with col2:
                st.markdown(f"**Created:** {module.created_at.strftime('%Y-%m-%d %H:%M') if module.created_at else 'Unknown'}")
                st.markdown(f"**Updated:** {module.updated_at.strftime('%Y-%m-%d %H:%M') if module.updated_at else 'Unknown'}")
                st.markdown(f"**Active:** {'✅ Yes' if module.is_active else '❌ No'}")
            
            return selected_module, module_info
        
        return None, None
    
    def show_component_explorer(self, selected_module: str, module_info: Dict[str, Any]):
        """Show interactive component explorer"""
        if not selected_module or not module_info:
            return
        
        st.markdown("### 🔍 Component Explorer")
        
        # Component type selection
        component_type = st.radio(
            "Select Component Type:",
            ["Roles", "Tables", "Properties", "Scheduled Jobs"],
            horizontal=True
        )
        
        # Get component data
        if component_type == "Roles":
            components = module_info['roles']
            component_key = 'roles'
        elif component_type == "Tables":
            components = module_info['tables']
            component_key = 'tables'
        elif component_type == "Properties":
            components = module_info['properties']
            component_key = 'properties'
        else:  # Scheduled Jobs
            components = module_info['jobs']
            component_key = 'jobs'
        
        if not components:
            st.info(f"No {component_type.lower()} found in {selected_module} module.")
            return
        
        # Search and filter
        search_term = st.text_input(f"Search {component_type}:", placeholder="Enter search term...")
        
        # Filter components
        filtered_components = components
        if search_term:
            filtered_components = [
                comp for comp in components 
                if search_term.lower() in comp.name.lower() or 
                   (hasattr(comp, 'description') and comp.description and search_term.lower() in comp.description.lower())
            ]
        
        st.markdown(f"**Found {len(filtered_components)} {component_type.lower()}**")
        
        # Display components
        if filtered_components:
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["📊 Summary", "📋 Detailed List", "🔗 Relationships"])
            
            with tab1:
                self.show_component_summary(component_type, filtered_components)
            
            with tab2:
                self.show_component_details(component_type, filtered_components)
            
            with tab3:
                self.show_component_relationships(component_type, filtered_components, selected_module)
    
    def show_component_summary(self, component_type: str, components: List[Any]):
        """Show component summary statistics"""
        st.markdown(f"#### 📊 {component_type} Summary")
        
        # Basic statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Count", len(components))
        
        with col2:
            active_count = sum(1 for comp in components if hasattr(comp, 'is_active') and comp.is_active)
            st.metric("Active", active_count)
        
        with col3:
            inactive_count = len(components) - active_count
            st.metric("Inactive", inactive_count)
        
        # Creation timeline
        if components and hasattr(components[0], 'created_at'):
            st.markdown("#### ⏰ Creation Timeline")
            timeline_data = []
            for comp in components:
                if comp.created_at:
                    timeline_data.append({
                        'Date': comp.created_at.date(),
                        'Name': comp.name,
                        'Type': component_type
                    })
            
            if timeline_data:
                timeline_df = pd.DataFrame(timeline_data)
                timeline_df['Date'] = pd.to_datetime(timeline_df['Date'])
                
                fig = px.histogram(timeline_df, x='Date', title=f"{component_type} Creation Timeline")
                st.plotly_chart(fig, use_container_width=True)
    
    def show_component_details(self, component_type: str, components: List[Any]):
        """Show detailed component list"""
        st.markdown(f"#### 📋 {component_type} Details")
        
        # Create dataframe for display
        component_data = []
        for comp in components:
            row = {
                'Name': comp.name,
                'Description': comp.description or 'No description',
                'Created': comp.created_at.strftime('%Y-%m-%d %H:%M') if comp.created_at else 'Unknown',
                'Active': comp.is_active if hasattr(comp, 'is_active') else True
            }
            
            # Add type-specific fields
            if component_type == "Tables" and hasattr(comp, 'table_type'):
                row['Type'] = comp.table_type or 'Unknown'
            elif component_type == "Properties" and hasattr(comp, 'property_type'):
                row['Type'] = comp.property_type or 'Unknown'
                row['Value'] = comp.current_value or 'No value'
            elif component_type == "Scheduled Jobs" and hasattr(comp, 'frequency'):
                row['Frequency'] = comp.frequency or 'Unknown'
                row['Active'] = comp.active if hasattr(comp, 'active') else True
            
            component_data.append(row)
        
        if component_data:
            df = pd.DataFrame(component_data)
            st.dataframe(df, use_container_width=True)
            
            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label=f"📥 Download {component_type} as CSV",
                data=csv,
                file_name=f"{component_type.lower()}_export.csv",
                mime="text/csv"
            )
    
    def show_component_relationships(self, component_type: str, components: List[Any], module_name: str):
        """Show component relationships"""
        st.markdown(f"#### 🔗 {component_type} Relationships")
        
        if component_type == "Tables":
            self.show_table_relationships(components, module_name)
        elif component_type == "Roles":
            self.show_role_relationships(components, module_name)
        elif component_type == "Properties":
            self.show_property_relationships(components, module_name)
        else:
            st.info("Relationship analysis not available for this component type.")
    
    def show_table_relationships(self, tables: List[Any], module_name: str):
        """Show table relationships"""
        if not tables:
            st.info("No tables to analyze relationships.")
            return
        
        # Create network graph
        G = nx.Graph()
        
        # Add nodes
        for table in tables:
            G.add_node(table.name, type='table', module=module_name)
        
        # Add relationships (simplified - in real scenario, you'd parse actual relationships)
        for i, table1 in enumerate(tables):
            for j, table2 in enumerate(tables[i+1:], i+1):
                # Simple heuristic: tables with similar names might be related
                if any(word in table2.name.lower() for word in table1.name.lower().split('_') if len(word) > 3):
                    G.add_edge(table1.name, table2.name)
        
        # Create network visualization
        if G.nodes():
            pos = nx.spring_layout(G, k=3, iterations=50)
            
            # Create edge trace
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=2, color='#888'),
                hoverinfo='none',
                mode='lines'
            )
            
            # Create node trace
            node_x = []
            node_y = []
            node_text = []
            for node in G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(f"{node}<br>Module: {module_name}")
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=node_text,
                textposition="middle center",
                marker=dict(
                    size=20,
                    color='lightblue',
                    line=dict(width=2, color='darkblue')
                )
            )
            
            fig = go.Figure(data=[edge_trace, node_trace],
                           layout=go.Layout(
                               title=f'Table Relationships in {module_name}',
                               titlefont_size=16,
                               showlegend=False,
                               hovermode='closest',
                               margin=dict(b=20,l=5,r=5,t=40),
                               annotations=[ dict(
                                   text="Hover over nodes to see table names",
                                   showarrow=False,
                                   xref="paper", yref="paper",
                                   x=0.005, y=-0.002,
                                   xanchor='left', yanchor='bottom',
                                   font=dict(color='gray', size=12)
                               )],
                               xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                               yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
            
            st.plotly_chart(fig, use_container_width=True)
    
    def show_role_relationships(self, roles: List[Any], module_name: str):
        """Show role relationships"""
        if not roles:
            st.info("No roles to analyze relationships.")
            return
        
        # Analyze role permissions and dependencies
        role_data = []
        for role in roles:
            permissions = getattr(role, 'permissions', []) or []
            dependencies = getattr(role, 'dependencies', []) or []
            
            role_data.append({
                'Role': role.name,
                'Permissions': len(permissions),
                'Dependencies': len(dependencies),
                'Description': role.description or 'No description'
            })
        
        if role_data:
            df = pd.DataFrame(role_data)
            
            # Create bar chart
            fig = px.bar(df, x='Role', y=['Permissions', 'Dependencies'],
                        title=f'Role Permissions and Dependencies in {module_name}',
                        barmode='group')
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed table
            st.dataframe(df, use_container_width=True)
    
    def show_property_relationships(self, properties: List[Any], module_name: str):
        """Show property relationships"""
        if not properties:
            st.info("No properties to analyze relationships.")
            return
        
        # Analyze property types and values
        property_data = []
        for prop in properties:
            property_data.append({
                'Property': prop.name,
                'Type': getattr(prop, 'property_type', 'Unknown'),
                'Value': getattr(prop, 'current_value', 'No value'),
                'Category': getattr(prop, 'category', 'Unknown'),
                'Scope': getattr(prop, 'scope', 'Unknown')
            })
        
        if property_data:
            df = pd.DataFrame(property_data)
            
            # Create pie chart for property types
            type_counts = df['Type'].value_counts()
            fig = px.pie(values=type_counts.values, names=type_counts.index,
                        title=f'Property Types in {module_name}')
            st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed table
            st.dataframe(df, use_container_width=True)
    
    def show_module_comparison(self, module_data: Dict[str, Any]):
        """Show module comparison charts"""
        st.markdown("### 📊 Module Comparison")
        
        if not module_data:
            st.info("No module data available for comparison.")
            return
        
        # Prepare comparison data
        comparison_data = []
        for module_name, info in module_data.items():
            comparison_data.append({
                'Module': module_name,
                'Roles': len(info['roles']),
                'Tables': len(info['tables']),
                'Properties': len(info['properties']),
                'Scheduled Jobs': len(info['jobs']),
                'Total Items': info['total_items']
            })
        
        df = pd.DataFrame(comparison_data)
        
        # Module comparison chart
        fig = px.bar(df, x='Module', y=['Roles', 'Tables', 'Properties', 'Scheduled Jobs'],
                    title='Module Component Comparison',
                    barmode='group')
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Total items comparison
        fig2 = px.bar(df, x='Module', y='Total Items',
                     title='Total Items per Module')
        fig2.update_xaxes(tickangle=45)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Show comparison table
        st.markdown("#### 📋 Module Comparison Table")
        st.dataframe(df, use_container_width=True)
    
    def show_global_analytics(self, module_data: Dict[str, Any]):
        """Show global analytics across all modules"""
        st.markdown("### 🌐 Global Analytics")
        
        if not module_data:
            st.info("No data available for global analytics.")
            return
        
        # Calculate global statistics
        total_roles = sum(len(info['roles']) for info in module_data.values())
        total_tables = sum(len(info['tables']) for info in module_data.values())
        total_properties = sum(len(info['properties']) for info in module_data.values())
        total_jobs = sum(len(info['jobs']) for info in module_data.values())
        total_items = total_roles + total_tables + total_properties + total_jobs
        
        # Global metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Modules", len(module_data))
        with col2:
            st.metric("Total Roles", total_roles)
        with col3:
            st.metric("Total Tables", total_tables)
        with col4:
            st.metric("Total Properties", total_properties)
        with col5:
            st.metric("Total Jobs", total_jobs)
        
        # Global distribution
        st.markdown("#### 📊 Global Distribution")
        
        # Item type distribution
        item_counts = {
            'Roles': total_roles,
            'Tables': total_tables,
            'Properties': total_properties,
            'Scheduled Jobs': total_jobs
        }
        
        fig = px.pie(values=list(item_counts.values()), names=list(item_counts.keys()),
                    title="Global Item Type Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
        # Module size distribution
        module_sizes = [info['total_items'] for info in module_data.values()]
        module_names = list(module_data.keys())
        
        fig2 = px.bar(x=module_names, y=module_sizes,
                     title="Items per Module",
                     labels={'x': 'Module', 'y': 'Number of Items'})
        fig2.update_xaxes(tickangle=45)
        st.plotly_chart(fig2, use_container_width=True)
    
    def show_interactive_visualizations(self):
        """Main method to show all interactive visualizations"""
        try:
            # Get module data
            module_data = self.get_module_data()
            
            if not module_data:
                st.info("No module data available. Please run the comprehensive scraper first.")
                return
            
            # Main tabs
            tab1, tab2, tab3, tab4 = st.tabs(["🔍 Module Explorer", "📊 Module Comparison", "🌐 Global Analytics", "📈 Custom Analysis"])
            
            with tab1:
                # Module overview and component explorer
                selected_module, module_info = self.show_module_overview(module_data)
                if selected_module and module_info:
                    st.markdown("---")
                    self.show_component_explorer(selected_module, module_info)
            
            with tab2:
                self.show_module_comparison(module_data)
            
            with tab3:
                self.show_global_analytics(module_data)
            
            with tab4:
                self.show_custom_analysis(module_data)
            
            # Show footer
            self.show_footer()
                
        except Exception as e:
            st.error(f"Error in interactive visualizations: {e}")
        finally:
            self.close_session()
    
    def show_custom_analysis(self, module_data: Dict[str, Any]):
        """Show custom analysis options"""
        st.markdown("### 📈 Custom Analysis")
        
        # Analysis type selection
        analysis_type = st.selectbox(
            "Select Analysis Type:",
            ["Component Distribution", "Module Complexity", "Creation Timeline", "Custom Query"]
        )
        
        if analysis_type == "Component Distribution":
            self.show_component_distribution_analysis(module_data)
        elif analysis_type == "Module Complexity":
            self.show_module_complexity_analysis(module_data)
        elif analysis_type == "Creation Timeline":
            self.show_creation_timeline_analysis(module_data)
        else:
            st.info("Custom query functionality coming soon!")
    
    def show_component_distribution_analysis(self, module_data: Dict[str, Any]):
        """Show component distribution analysis"""
        st.markdown("#### 📊 Component Distribution Analysis")
        
        # Prepare data for analysis
        analysis_data = []
        for module_name, info in module_data.items():
            analysis_data.append({
                'Module': module_name,
                'Roles': len(info['roles']),
                'Tables': len(info['tables']),
                'Properties': len(info['properties']),
                'Jobs': len(info['jobs']),
                'Total': info['total_items']
            })
        
        df = pd.DataFrame(analysis_data)
        
        # Heatmap
        heatmap_data = df.set_index('Module')[['Roles', 'Tables', 'Properties', 'Jobs']]
        fig = px.imshow(heatmap_data.T, 
                       title="Component Distribution Heatmap",
                       labels=dict(x="Module", y="Component Type", color="Count"))
        st.plotly_chart(fig, use_container_width=True)
        
        # Scatter plot
        fig2 = px.scatter(df, x='Roles', y='Tables', size='Total', hover_name='Module',
                         title="Roles vs Tables Scatter Plot",
                         labels={'Roles': 'Number of Roles', 'Tables': 'Number of Tables'})
        st.plotly_chart(fig2, use_container_width=True)
    
    def show_module_complexity_analysis(self, module_data: Dict[str, Any]):
        """Show module complexity analysis"""
        st.markdown("#### 🧮 Module Complexity Analysis")
        
        complexity_data = []
        for module_name, info in module_data.items():
            # Calculate complexity score (simple heuristic)
            complexity_score = (
                len(info['roles']) * 1 +
                len(info['tables']) * 2 +
                len(info['properties']) * 1 +
                len(info['jobs']) * 3
            )
            
            complexity_data.append({
                'Module': module_name,
                'Complexity Score': complexity_score,
                'Roles': len(info['roles']),
                'Tables': len(info['tables']),
                'Properties': len(info['properties']),
                'Jobs': len(info['jobs'])
            })
        
        df = pd.DataFrame(complexity_data)
        df = df.sort_values('Complexity Score', ascending=False)
        
        # Complexity ranking
        fig = px.bar(df, x='Module', y='Complexity Score',
                    title="Module Complexity Ranking",
                    color='Complexity Score',
                    color_continuous_scale='viridis')
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
        
        # Show complexity table
        st.dataframe(df, use_container_width=True)
    
    def show_creation_timeline_analysis(self, module_data: Dict[str, Any]):
        """Show creation timeline analysis"""
        st.markdown("#### ⏰ Creation Timeline Analysis")
        
        timeline_data = []
        session = self.get_session()
        
        try:
            from database import ServiceNowModule, ServiceNowRole, ServiceNowTable, ServiceNowProperty, ServiceNowScheduledJob
            
            # Get all items with creation dates
            all_items = []
            all_items.extend(session.query(ServiceNowRole).all())
            all_items.extend(session.query(ServiceNowTable).all())
            all_items.extend(session.query(ServiceNowProperty).all())
            all_items.extend(session.query(ServiceNowScheduledJob).all())
            
            for item in all_items:
                if item.created_at:
                    timeline_data.append({
                        'Date': item.created_at.date(),
                        'Type': item.__class__.__name__.replace('ServiceNow', ''),
                        'Name': item.name,
                        'Module': item.module.name if item.module else 'Unknown'
                    })
            
            if timeline_data:
                timeline_df = pd.DataFrame(timeline_data)
                timeline_df['Date'] = pd.to_datetime(timeline_df['Date'])
                
                # Timeline by type
                fig = px.histogram(timeline_df, x='Date', color='Type',
                                 title="Creation Timeline by Item Type",
                                 nbins=30)
                st.plotly_chart(fig, use_container_width=True)
                
                # Timeline by module
                fig2 = px.histogram(timeline_df, x='Date', color='Module',
                                   title="Creation Timeline by Module",
                                   nbins=30)
                st.plotly_chart(fig2, use_container_width=True)
                
                # Show timeline table
                st.dataframe(timeline_df, use_container_width=True)
            else:
                st.info("No creation timeline data available.")
                
        finally:
            session.close()
    
    def show_footer(self):
        """Show footer with creator information"""
        st.markdown("""
        <div style="position: fixed; bottom: 0; left: 0; right: 0; background-color: #f8f9fa; border-top: 1px solid #dee2e6; padding: 10px 20px; text-align: center; font-size: 0.9rem; color: #6c757d; z-index: 1000;">
            Created By: <strong>Ashish Gautam</strong> | 
            <a href="https://www.linkedin.com/in/ashishgautamkarn/" target="_blank" style="color: #007bff; text-decoration: none;">LinkedIn Profile</a>
        </div>
        """, unsafe_allow_html=True)
