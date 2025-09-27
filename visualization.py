"""
ServiceNow Visualization Components
This module provides interactive visualization components for ServiceNow table relationships and documentation.
"""

import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import List, Dict, Optional, Tuple
import streamlit as st
from models import ServiceNowDocumentation, ServiceNowTable, TableRelationship, ModuleType, RelationshipType


class ServiceNowVisualizer:
    """Main visualization class for ServiceNow documentation"""
    
    def __init__(self, documentation: ServiceNowDocumentation):
        self.doc = documentation
        self.graph = self._build_network_graph()
    
    def _build_network_graph(self) -> nx.DiGraph:
        """Build NetworkX graph from ServiceNow documentation"""
        G = nx.DiGraph()
        
        # Add nodes (tables)
        for module in self.doc.modules:
            for table in module.tables:
                G.add_node(
                    table.name,
                    label=table.label,
                    module=module.name,
                    module_type=module.module_type.value,
                    table_type=table.table_type.value,
                    description=table.description,
                    field_count=len(table.fields)
                )
        
        # Add edges (relationships)
        for rel in self.doc.global_relationships:
            if G.has_node(rel.source_table) and G.has_node(rel.target_table):
                G.add_edge(
                    rel.source_table,
                    rel.target_table,
                    relationship_type=rel.relationship_type.value,
                    source_field=rel.source_field,
                    target_field=rel.target_field,
                    description=rel.description
                )
        
        return G
    
    def create_network_visualization(self, selected_modules: List[str] = None, 
                                  selected_tables: List[str] = None) -> go.Figure:
        """Create interactive network visualization"""
        
        # Filter graph based on selections
        if selected_modules or selected_tables:
            filtered_nodes = set()
            
            if selected_modules:
                for module_name in selected_modules:
                    module = self.doc.get_module_by_name(module_name)
                    if module:
                        filtered_nodes.update([table.name for table in module.tables])
            
            if selected_tables:
                filtered_nodes.update(selected_tables)
            
            # Create subgraph
            subgraph_nodes = [node for node in self.graph.nodes() if node in filtered_nodes]
            G_filtered = self.graph.subgraph(subgraph_nodes)
        else:
            G_filtered = self.graph
        
        # Calculate layout
        pos = nx.spring_layout(G_filtered, k=3, iterations=50)
        
        # Prepare edge traces
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in G_filtered.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            # Get edge information
            edge_data = G_filtered[edge[0]][edge[1]]
            edge_info.append(f"{edge[0]} → {edge[1]}<br>Type: {edge_data.get('relationship_type', 'Unknown')}<br>Description: {edge_data.get('description', 'No description')}")
        
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='#888'),
            hoverinfo='none',
            mode='lines'
        )
        
        # Prepare node traces
        node_x = []
        node_y = []
        node_text = []
        node_info = []
        node_colors = []
        node_sizes = []
        
        # Color mapping for modules
        module_colors = {
            ModuleType.ITSM.value: '#FF6B6B',
            ModuleType.CSM.value: '#4ECDC4',
            ModuleType.HRSD.value: '#45B7D1',
            ModuleType.FSM.value: '#96CEB4',
            ModuleType.GRC.value: '#FFEAA7',
            ModuleType.SECOPS.value: '#DDA0DD',
            ModuleType.ITOM.value: '#98D8C8',
            ModuleType.APM.value: '#F7DC6F',
            ModuleType.PPM.value: '#BB8FCE',
            ModuleType.IRM.value: '#85C1E9',
            ModuleType.CUSTOM.value: '#F8C471'
        }
        
        for node in G_filtered.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            node_data = G_filtered.nodes[node]
            node_text.append(node_data['label'])
            
            # Create hover information
            info = f"<b>{node_data['label']}</b><br>"
            info += f"Table: {node}<br>"
            info += f"Module: {node_data['module']}<br>"
            info += f"Type: {node_data['table_type']}<br>"
            info += f"Fields: {node_data['field_count']}<br>"
            info += f"Description: {node_data['description'][:100]}..."
            
            node_info.append(info)
            
            # Set color based on module
            module_type = node_data['module_type']
            node_colors.append(module_colors.get(module_type, '#CCCCCC'))
            
            # Set size based on field count
            field_count = node_data['field_count']
            node_sizes.append(max(20, min(50, field_count * 2)))
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            hovertext=node_info,
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=2, color='white')
            )
        )
        
        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title='ServiceNow Table Relationships',
                           titlefont_size=16,
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text="Interactive ServiceNow Table Relationship Network",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002,
                               xanchor='left', yanchor='bottom',
                               font=dict(color='#888', size=12)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           plot_bgcolor='white'
                       ))
        
        return fig
    
    def create_hierarchical_tree(self, root_table: str = None) -> go.Figure:
        """Create hierarchical tree visualization"""
        
        if not root_table:
            # Find a good root table (one with many outgoing relationships)
            root_table = max(self.graph.nodes(), 
                           key=lambda x: self.graph.out_degree(x))
        
        # Build tree structure
        tree = nx.bfs_tree(self.graph, root_table)
        
        # Calculate hierarchical layout
        try:
            pos = nx.nx_agraph.graphviz_layout(tree, prog='dot')
        except ImportError:
            # Fallback to spring layout if pygraphviz is not available
            pos = nx.spring_layout(tree, k=3, iterations=50)
        
        # Prepare traces
        edge_x = []
        edge_y = []
        
        for edge in tree.edges():
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
        
        node_x = []
        node_y = []
        node_text = []
        node_info = []
        node_colors = []
        
        module_colors = {
            ModuleType.ITSM.value: '#FF6B6B',
            ModuleType.CSM.value: '#4ECDC4',
            ModuleType.HRSD.value: '#45B7D1',
            ModuleType.FSM.value: '#96CEB4',
            ModuleType.GRC.value: '#FFEAA7',
            ModuleType.SECOPS.value: '#DDA0DD',
            ModuleType.ITOM.value: '#98D8C8',
            ModuleType.APM.value: '#F7DC6F',
            ModuleType.PPM.value: '#BB8FCE',
            ModuleType.IRM.value: '#85C1E9',
            ModuleType.CUSTOM.value: '#F8C471'
        }
        
        for node in tree.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            node_data = self.graph.nodes[node]
            node_text.append(node_data['label'])
            
            info = f"<b>{node_data['label']}</b><br>"
            info += f"Table: {node}<br>"
            info += f"Module: {node_data['module']}<br>"
            info += f"Type: {node_data['table_type']}<br>"
            info += f"Fields: {node_data['field_count']}<br>"
            info += f"Description: {node_data['description'][:100]}..."
            
            node_info.append(info)
            
            module_type = node_data['module_type']
            node_colors.append(module_colors.get(module_type, '#CCCCCC'))
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            hovertext=node_info,
            marker=dict(
                size=30,
                color=node_colors,
                line=dict(width=2, color='white')
            )
        )
        
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title=f'Hierarchical Tree View - Root: {root_table}',
                           titlefont_size=16,
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           plot_bgcolor='white'
                       ))
        
        return fig
    
    def create_module_overview(self) -> go.Figure:
        """Create module overview visualization"""
        
        module_data = []
        for module in self.doc.modules:
            module_data.append({
                'Module': module.label,
                'Tables': len(module.tables),
                'Total Fields': sum(len(table.fields) for table in module.tables),
                'Module Type': module.module_type.value
            })
        
        df = pd.DataFrame(module_data)
        
        fig = px.bar(df, x='Module', y='Tables', 
                    color='Module Type',
                    title='ServiceNow Modules Overview',
                    labels={'Tables': 'Number of Tables', 'Module': 'Module Name'},
                    color_discrete_map={
                        ModuleType.ITSM.value: '#FF6B6B',
                        ModuleType.CSM.value: '#4ECDC4',
                        ModuleType.HRSD.value: '#45B7D1',
                        ModuleType.FSM.value: '#96CEB4',
                        ModuleType.GRC.value: '#FFEAA7',
                        ModuleType.SECOPS.value: '#DDA0DD',
                        ModuleType.ITOM.value: '#98D8C8',
                        ModuleType.APM.value: '#F7DC6F',
                        ModuleType.PPM.value: '#BB8FCE',
                        ModuleType.IRM.value: '#85C1E9',
                        ModuleType.CUSTOM.value: '#F8C471'
                    })
        
        fig.update_layout(
            xaxis_tickangle=-45,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        
        return fig
    
    def create_table_field_analysis(self, table_name: str) -> go.Figure:
        """Create field analysis for a specific table"""
        
        table = self.doc.get_table_by_name(table_name)
        if not table:
            return go.Figure()
        
        field_types = {}
        for field in table.fields:
            field_type = field.type
            if field_type in field_types:
                field_types[field_type] += 1
            else:
                field_types[field_type] = 1
        
        fig = px.pie(
            values=list(field_types.values()),
            names=list(field_types.keys()),
            title=f'Field Types Distribution - {table.label}'
        )
        
        return fig
    
    def create_relationship_matrix(self) -> go.Figure:
        """Create relationship matrix heatmap"""
        
        tables = list(self.graph.nodes())
        matrix = []
        
        for source in tables:
            row = []
            for target in tables:
                if self.graph.has_edge(source, target):
                    row.append(1)
                else:
                    row.append(0)
            matrix.append(row)
        
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=tables,
            y=tables,
            colorscale='Blues',
            showscale=True
        ))
        
        fig.update_layout(
            title='ServiceNow Table Relationship Matrix',
            xaxis_title='Target Tables',
            yaxis_title='Source Tables'
        )
        
        return fig
    
    def get_table_statistics(self) -> Dict:
        """Get comprehensive statistics about the ServiceNow documentation"""
        
        total_tables = len(self.doc.get_all_tables())
        total_fields = sum(len(table.fields) for table in self.doc.get_all_tables())
        total_relationships = len(self.doc.global_relationships)
        total_parameters = len(self.doc.global_system_parameters)
        
        module_stats = {}
        for module in self.doc.modules:
            module_stats[module.label] = {
                'tables': len(module.tables),
                'fields': sum(len(table.fields) for table in module.tables),
                'parameters': len(module.system_parameters)
            }
        
        return {
            'total_tables': total_tables,
            'total_fields': total_fields,
            'total_relationships': total_relationships,
            'total_parameters': total_parameters,
            'module_stats': module_stats
        }


def create_annotation_popup(table: ServiceNowTable) -> str:
    """Create HTML popup content for table annotations"""
    
    html = f"""
    <div style="max-width: 400px; font-family: Arial, sans-serif;">
        <h3 style="color: #2E86AB; margin-bottom: 10px;">{table.label}</h3>
        <p><strong>Table Name:</strong> {table.name}</p>
        <p><strong>Module:</strong> {table.module.value}</p>
        <p><strong>Type:</strong> {table.table_type.value}</p>
        <p><strong>Description:</strong> {table.description}</p>
        
        <h4 style="color: #A23B72; margin-top: 15px; margin-bottom: 10px;">Fields ({len(table.fields)})</h4>
        <div style="max-height: 200px; overflow-y: auto;">
    """
    
    for field in table.fields[:10]:  # Show first 10 fields
        html += f"""
            <div style="margin-bottom: 5px; padding: 5px; background-color: #f8f9fa; border-radius: 3px;">
                <strong>{field.name}</strong> ({field.type})<br>
                <small>{field.label}</small>
            </div>
        """
    
    if len(table.fields) > 10:
        html += f"<p><em>... and {len(table.fields) - 10} more fields</em></p>"
    
    html += """
        </div>
        
        <h4 style="color: #A23B72; margin-top: 15px; margin-bottom: 10px;">System Parameters</h4>
        <div style="max-height: 150px; overflow-y: auto;">
    """
    
    for param in table.system_parameters[:5]:  # Show first 5 parameters
        html += f"""
            <div style="margin-bottom: 3px; padding: 3px; background-color: #e9ecef; border-radius: 3px;">
                <small>{param}</small>
            </div>
        """
    
    if len(table.system_parameters) > 5:
        html += f"<p><em>... and {len(table.system_parameters) - 5} more parameters</em></p>"
    
    html += """
        </div>
    </div>
    """
    
    return html

# Created By: Ashish Gautam; LinkedIn: https://www.linkedin.com/in/ashishgautamkarn/
