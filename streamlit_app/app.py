import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import toml
import os
from pathlib import Path
import snowflake.connector
from snowflake.connector.errors import ProgrammingError
import json
import time
import requests
from typing import List, Dict, Any, Optional
import re

# Page configuration
st.set_page_config(
    page_title="Snowflake Semantic Analytics - Business Intelligence Chat",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern chat interface
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
        border: 1px solid #e9ecef;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0;
        max-width: 80%;
        margin-left: auto;
    }
    
    .assistant-message {
        background: white;
        color: #333;
        padding: 15px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        max-width: 80%;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    .chart-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e9ecef;
        padding: 12px 20px;
    }
    
    .stButton > button {
        border-radius: 25px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        font-weight: bold;
    }
    
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    .insight-card {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #ff7f0e;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #e17055;
    }
    
    .success-card {
        background: linear-gradient(135deg, #a8e6cf 0%, #dcedc1 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #2ecc71;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_config():
    """Load Snowflake configuration from config.toml"""
    try:
        config_path = Path("/Users/akhilgurrapu/Documents/Projects/semanticSnowflake/config.toml")
        config = toml.load(str(config_path))
        return config['connections']['semantics']
    except Exception as e:
        st.error(f"Error loading config: {e}")
        return None

@st.cache_resource
def get_snowflake_connection():
    """Create and cache Snowflake connection"""
    config = load_config()
    if not config:
        return None
    
    try:
        # Read token from file
        token_path = Path("/Users/akhilgurrapu/Documents/Projects/semanticSnowflake/snowflake-pat.token")
        with open(token_path, 'r') as f:
            token = f.read().strip()
        
        conn = snowflake.connector.connect(
            account=config['account'],
            user=config['user'],
            authenticator='PROGRAMMATIC_ACCESS_TOKEN',
            token=token,
            role=config['role'],
            warehouse=config['warehouse'],
            database=config['database'],
            schema=config['schema']
        )
        return conn
    except Exception as e:
        st.error(f"Error connecting to Snowflake: {e}")
        return None

def execute_semantic_query(dimensions: List[str], metrics: List[str], filters: Optional[str] = None, limit: int = 1000, semantic_view: str = "snowflake_monitoring_semantic") -> Optional[pd.DataFrame]:
    """Execute a semantic view query"""
    conn = get_snowflake_connection()
    if not conn:
        return None
    
    try:
        # Build the semantic query
        dim_str = ", ".join(dimensions) if isinstance(dimensions, list) else dimensions
        metric_str = ", ".join(metrics) if isinstance(metrics, list) else metrics
        
        query = f"""
        SELECT * FROM SEMANTIC_VIEW(
            {semantic_view.upper()}
            DIMENSIONS {dim_str}
            METRICS {metric_str}
        )
        """
        
        if filters:
            query += f" WHERE {filters}"
        
        query += f" LIMIT {limit}"
        
        # Execute query
        cursor = conn.cursor()
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        df = pd.DataFrame(results, columns=columns)
        cursor.close()
        return df
        
    except Exception as e:
        st.error(f"Error executing semantic query: {e}")
        return None

def get_available_dimensions() -> List[str]:
    """Get available dimensions from semantic views"""
    return [
        "WAREHOUSE_NAME",
        "USER_NAME", 
        "QUERY_TYPE",
        "WAREHOUSE_SIZE",
        "USAGE_DATE",
        "USAGE_HOUR"
    ]

def get_available_metrics() -> List[str]:
    """Get available metrics from semantic views"""
    return [
        "TOTAL_CREDITS", 
        "TOTAL_QUERIES",
        "AVG_EXECUTION_TIME",
        "SLOW_QUERIES",
        "TOTAL_DATA_SCANNED",
        "AVG_QUEUE_TIME",
        "TOTAL_COST",
        "AVG_DAILY_COST",
        "COMPUTE_VS_CLOUD_RATIO",
        "HIGH_COST_DAYS",
        "TOTAL_USER_QUERIES",
        "AVG_USER_EXECUTION_TIME",
        "USER_DATA_ACCESS",
        "SUSPICIOUS_ACTIVITY",
        "LONG_RUNNING_QUERIES"
    ]

def format_currency(value: float) -> str:
    """Format value as currency"""
    if pd.isna(value) or value == 0:
        return "$0.00"
    return f"${value:,.2f}"

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable format"""
    if pd.isna(seconds) or seconds == 0:
        return "0s"
    
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def parse_natural_language_query(query: str) -> Dict[str, Any]:
    """Parse natural language query and convert to semantic query parameters"""
    query_lower = query.lower()
    
    # Initialize default parameters
    params = {
        'dimensions': [],
        'metrics': [],
        'filters': None,
        'time_period': '7d',
        'semantic_view': 'snowflake_monitoring_semantic'
    }
    
    # Determine semantic view based on query type
    # Check for specific phrases first
    if 'performance analysis' in query_lower:
        params['semantic_view'] = 'query_performance_semantic'
    elif 'cost analysis' in query_lower:
        params['semantic_view'] = 'cost_analysis_semantic'
    elif 'query performance' in query_lower:
        params['semantic_view'] = 'query_performance_semantic'
    elif 'user activity' in query_lower:
        params['semantic_view'] = 'user_activity_semantic'
    elif 'avg timing' in query_lower or 'average timing' in query_lower:
        params['semantic_view'] = 'query_performance_semantic'
    elif 'query metrics' in query_lower:
        params['semantic_view'] = 'query_performance_semantic'
    # Then check for individual keywords
    elif any(word in query_lower for word in ['performance', 'slow', 'execution', 'time', 'timing']):
        params['semantic_view'] = 'query_performance_semantic'
    elif any(word in query_lower for word in ['cost', 'spend', 'expense', 'money', 'billing']):
        params['semantic_view'] = 'cost_analysis_semantic'
    elif any(word in query_lower for word in ['user', 'activity', 'who', 'person']):
        params['semantic_view'] = 'user_activity_semantic'
    elif any(word in query_lower for word in ['resource', 'utilization', 'efficiency', 'usage']):
        params['semantic_view'] = 'resource_utilization_semantic'
    elif any(word in query_lower for word in ['security', 'access', 'suspicious', 'audit']):
        params['semantic_view'] = 'security_monitoring_semantic'
    
    # Extract dimensions based on keywords and semantic view
    if 'warehouse' in query_lower:
        params['dimensions'].append('WAREHOUSE_NAME')
    if 'user' in query_lower:
        params['dimensions'].append('USER_NAME')
    if 'type' in query_lower or 'query type' in query_lower:
        params['dimensions'].append('QUERY_TYPE')
    if 'date' in query_lower or 'time' in query_lower:
        params['dimensions'].append('USAGE_DATE')
    
    # Extract metrics based on keywords
    if 'cost' in query_lower or 'spend' in query_lower or 'expense' in query_lower or 'credits' in query_lower:
        if params['semantic_view'] == 'cost_analysis_semantic':
            params['metrics'].append('TOTAL_COST')
        else:
            params['metrics'].append('TOTAL_CREDITS')
    if 'query' in query_lower and ('count' in query_lower or 'number' in query_lower):
        params['metrics'].append('TOTAL_QUERIES')
    if any(word in query_lower for word in ['avg', 'average', 'mean']) and any(word in query_lower for word in ['time', 'timing', 'execution']):
        if params['semantic_view'] == 'query_performance_semantic':
            params['metrics'].append('AVG_EXECUTION_TIME')
        elif params['semantic_view'] == 'user_activity_semantic':
            params['metrics'].append('AVG_USER_EXECUTION_TIME')
        else:
            params['metrics'].append('AVG_EXECUTION_TIME')
    elif 'performance' in query_lower or 'execution' in query_lower or 'time' in query_lower:
        params['metrics'].append('AVG_EXECUTION_TIME')
    if 'slow' in query_lower:
        params['metrics'].append('SLOW_QUERIES')
    if 'data' in query_lower and 'scan' in query_lower:
        params['metrics'].append('TOTAL_DATA_SCANNED')
    if 'activity' in query_lower:
        params['metrics'].append('TOTAL_USER_QUERIES')
    if 'security' in query_lower or 'suspicious' in query_lower:
        params['metrics'].append('SUSPICIOUS_ACTIVITY')
    
    # Set default dimensions and metrics if none specified
    if not params['dimensions']:
        if params['semantic_view'] == 'user_activity_semantic':
            params['dimensions'] = ['USER_NAME']
        elif params['semantic_view'] == 'query_performance_semantic':
            params['dimensions'] = ['QUERY_TYPE']
        elif params['semantic_view'] == 'cost_analysis_semantic':
            params['dimensions'] = ['WAREHOUSE_NAME']
        elif params['semantic_view'] == 'resource_utilization_semantic':
            params['dimensions'] = ['WAREHOUSE_NAME']
        elif params['semantic_view'] == 'security_monitoring_semantic':
            params['dimensions'] = ['USER_NAME']
        else:
            params['dimensions'] = ['WAREHOUSE_NAME']
    
    if not params['metrics']:
        if params['semantic_view'] == 'user_activity_semantic':
            params['metrics'] = ['TOTAL_USER_QUERIES', 'AVG_USER_EXECUTION_TIME']
        elif params['semantic_view'] == 'query_performance_semantic':
            params['metrics'] = ['TOTAL_QUERIES', 'AVG_EXECUTION_TIME']
        elif params['semantic_view'] == 'cost_analysis_semantic':
            params['metrics'] = ['TOTAL_COST', 'AVG_DAILY_COST']
        elif params['semantic_view'] == 'resource_utilization_semantic':
            params['metrics'] = ['TOTAL_CREDITS_USED', 'AVG_CREDITS_PER_HOUR']
        elif params['semantic_view'] == 'security_monitoring_semantic':
            params['metrics'] = ['TOTAL_USER_ACTIVITY', 'SUSPICIOUS_ACTIVITY']
        else:
            params['metrics'] = ['TOTAL_CREDITS', 'TOTAL_QUERIES']
    
    # Ensure we have at least one metric that exists in the semantic view
    if not params['metrics']:
        params['metrics'] = ['TOTAL_QUERIES']  # Fallback metric
    
    return params

def generate_insights(df: pd.DataFrame, query: str) -> List[str]:
    """Generate AI-powered insights from the data"""
    insights = []
    
    if df.empty:
        return ["No data available for the specified query."]
    
    # Cost insights
    if 'TOTAL_CREDITS' in df.columns:
        total_credits = df['TOTAL_CREDITS'].sum()
        avg_credits = df['TOTAL_CREDITS'].mean()
        
        if total_credits > 100:
            insights.append(f"💰 **High Cost Alert**: Total credits consumed: {total_credits:.2f} (${total_credits * 0.0004:.2f})")
        
        if 'WAREHOUSE_NAME' in df.columns:
            top_warehouse = df.groupby('WAREHOUSE_NAME')['TOTAL_CREDITS'].sum().idxmax()
            insights.append(f"🏭 **Top Consumer**: {top_warehouse} is consuming the most credits")
    
    # Performance insights
    if 'AVG_EXECUTION_TIME' in df.columns:
        avg_time = df['AVG_EXECUTION_TIME'].mean()
        if avg_time > 30000:  # 30 seconds
            insights.append(f"⚡ **Performance Issue**: Average execution time is {format_duration(avg_time)}")
        elif avg_time > 10000:  # 10 seconds
            insights.append(f"⚠️ **Moderate Performance**: Average execution time is {format_duration(avg_time)}")
        else:
            insights.append(f"✅ **Good Performance**: Average execution time is {format_duration(avg_time)}")
        
        # Query type specific insights
        if 'QUERY_TYPE' in df.columns:
            query_performance = df.groupby('QUERY_TYPE')['AVG_EXECUTION_TIME'].mean().sort_values(ascending=False)
            slowest_type = query_performance.index[0]
            slowest_time = query_performance.iloc[0]
            insights.append(f"🔍 **Slowest Query Type**: {slowest_type} queries take {format_duration(slowest_time)} on average")
    
    if 'SLOW_QUERIES' in df.columns:
        slow_count = df['SLOW_QUERIES'].sum()
        if slow_count > 0:
            insights.append(f"🐌 **Slow Queries**: {slow_count} slow queries detected")
    
    # Usage pattern insights
    if 'USAGE_HOUR' in df.columns and 'TOTAL_CREDITS' in df.columns:
        hourly_usage = df.groupby('USAGE_HOUR')['TOTAL_CREDITS'].sum()
        peak_hour = hourly_usage.idxmax()
        insights.append(f"📊 **Peak Usage**: Hour {peak_hour} shows highest activity")
    
    # Trend insights
    if 'USAGE_DATE' in df.columns and 'TOTAL_CREDITS' in df.columns:
        daily_credits = df.groupby('USAGE_DATE')['TOTAL_CREDITS'].sum()
        if len(daily_credits) > 1:
            trend = daily_credits.iloc[-1] - daily_credits.iloc[0]
            if trend > 0:
                insights.append("📈 **Trend**: Credit consumption is increasing")
            elif trend < 0:
                insights.append("📉 **Trend**: Credit consumption is decreasing")
    
    return insights

def create_visualization(df: pd.DataFrame, dimensions: List[str], metrics: List[str]) -> go.Figure:
    """Create appropriate visualization based on data"""
    if df.empty:
        return go.Figure().add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
    
    # Time series chart
    if 'USAGE_DATE' in df.columns and metrics:
        metric = metrics[0]
        daily_data = df.groupby('USAGE_DATE')[metric].sum().reset_index()
        fig = px.line(daily_data, x='USAGE_DATE', y=metric,
                     title=f"{metric} Over Time",
                     labels={metric: metric.replace('_', ' ').title()})
        return fig
    
    # Bar chart for categorical data
    elif dimensions and metrics:
        dim = dimensions[0]
        metric = metrics[0]
        bar_data = df.groupby(dim)[metric].sum().reset_index()
        fig = px.bar(bar_data, x=dim, y=metric,
                    title=f"{metric} by {dim}",
                    labels={metric: metric.replace('_', ' ').title(), dim: dim.replace('_', ' ').title()})
        return fig
    
    # Scatter plot for two metrics
    elif len(metrics) >= 2:
        fig = px.scatter(df, x=metrics[0], y=metrics[1],
                        title=f"{metrics[1]} vs {metrics[0]}",
                        labels={metrics[0]: metrics[0].replace('_', ' ').title(),
                               metrics[1]: metrics[1].replace('_', ' ').title()})
        return fig
    
    # Default table view
    else:
        fig = go.Figure(data=[go.Table(
            header=dict(values=list(df.columns)),
            cells=dict(values=[df[col] for col in df.columns])
        )])
        return fig

def chat_interface():
    """Main chat interface for natural language queries"""
    st.markdown('<h1 class="main-header">❄️ Snowflake Semantic Analytics Chat</h1>', unsafe_allow_html=True)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar with connection status and quick actions
    with st.sidebar:
        st.title("🔧 Configuration")
        
        # Connection status
        conn = get_snowflake_connection()
        if conn:
            st.success("✅ Connected to Snowflake")
        else:
            st.error("❌ Connection failed")
            return
        
        st.markdown("---")
        st.title("💡 Quick Actions")
        
        # Predefined queries
        st.subheader("Common Questions")
        quick_queries = [
            "Show me warehouse costs for the last week",
            "Which warehouses are consuming the most credits?",
            "What's the average query execution time?",
            "Show me user activity by hour",
            "Which query types are most common?",
            "What's the cost trend over the last month?",
            "Show me user performance analysis",
            "Which users have the most suspicious activity?",
            "What's the resource utilization by warehouse?",
            "Show me slow query performance"
        ]
        
        for query in quick_queries:
            if st.button(query, key=f"quick_{query[:20]}"):
                st.session_state.user_input = query
                st.rerun()
        
        st.markdown("---")
        st.title("📊 Available Metrics")
        st.write("**Dimensions:**")
        for dim in get_available_dimensions():
            st.write(f"• {dim}")
        
        st.write("**Metrics:**")
        for metric in get_available_metrics():
            st.write(f"• {metric}")
    
    # Main chat area
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Check for quick action input or chat input
    prompt = None
    if "user_input" in st.session_state and st.session_state.user_input:
        prompt = st.session_state.user_input
        # Clear the session state to prevent reprocessing
        st.session_state.user_input = None
    
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process the query
        with st.chat_message("assistant"):
            with st.spinner("Analyzing your query..."):
                # Parse natural language query
                params = parse_natural_language_query(prompt)
                
                # Execute semantic query
                try:
                    df = execute_semantic_query(
                        dimensions=params['dimensions'],
                        metrics=params['metrics'],
                        filters=params['filters'],
                        semantic_view=params['semantic_view']
                    )
                except Exception as e:
                    st.error(f"Error executing query: {e}")
                    # Try with fallback metrics
                    st.info("Trying with fallback metrics...")
                    fallback_metrics = ['TOTAL_QUERIES'] if 'TOTAL_QUERIES' in get_available_metrics() else ['TOTAL_CREDITS']
                    df = execute_semantic_query(
                        dimensions=params['dimensions'],
                        metrics=fallback_metrics,
                        filters=params['filters'],
                        semantic_view=params['semantic_view']
                    )
                
                if df is not None and not df.empty:
                    # Generate insights
                    insights = generate_insights(df, prompt)
                    
                    # Create comprehensive response
                    response = f"✅ **Query Results:**\n\n"
                    response += f"**Semantic View:** {params['semantic_view'].replace('_', ' ').title()}\n"
                    response += f"**Dimensions:** {', '.join(params['dimensions'])}\n"
                    response += f"**Metrics:** {', '.join(params['metrics'])}\n"
                    response += f"**Records:** {len(df)}\n\n"
                    
                    # Add concise answer based on the query type
                    if 'avg' in prompt.lower() or 'average' in prompt.lower() or 'timing' in prompt.lower():
                        if 'AVG_EXECUTION_TIME' in params['metrics']:
                            avg_time = df['AVG_EXECUTION_TIME'].mean()
                            response += f"**📊 Answer:** The average execution time across all query types is **{format_duration(avg_time)}**.\n\n"
                        elif 'AVG_USER_EXECUTION_TIME' in params['metrics']:
                            avg_time = df['AVG_USER_EXECUTION_TIME'].mean()
                            response += f"**📊 Answer:** The average user execution time is **{format_duration(avg_time)}**.\n\n"
                    elif 'cost' in prompt.lower() or 'spend' in prompt.lower():
                        if 'TOTAL_COST' in params['metrics']:
                            total_cost = df['TOTAL_COST'].sum()
                            response += f"**📊 Answer:** Total cost is **${total_cost:,.2f}**.\n\n"
                        elif 'TOTAL_CREDITS' in params['metrics']:
                            total_credits = df['TOTAL_CREDITS'].sum()
                            response += f"**📊 Answer:** Total credits consumed is **{total_credits:,.2f}** (${total_credits * 0.0004:.2f}).\n\n"
                    elif 'query' in prompt.lower() and ('count' in prompt.lower() or 'number' in prompt.lower()):
                        if 'TOTAL_QUERIES' in params['metrics']:
                            total_queries = df['TOTAL_QUERIES'].sum()
                            response += f"**📊 Answer:** Total number of queries is **{total_queries:,.0f}**.\n\n"
                    else:
                        # Generic answer
                        response += f"**📊 Answer:** Found **{len(df)}** records with the requested data.\n\n"
                    
                    # Show insights
                    if insights:
                        response += "**🔍 AI Insights:**\n"
                        for insight in insights:
                            response += f"• {insight}\n"
                        response += "\n"
                    
                    # Display the response
                    st.markdown(response)
                    
                    # Create visualization
                    fig = create_visualization(df, params['dimensions'], params['metrics'])
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show data preview
                    with st.expander("📋 Data Preview"):
                        st.dataframe(df.head(10), use_container_width=True)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                else:
                    error_msg = "❌ No data found for your query. Try rephrasing or check the available metrics in the sidebar."
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Always show chat input at the end
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat input box - always visible
    if prompt := st.chat_input("Ask me anything about your Snowflake usage...", key="main_chat_input"):
        st.session_state.user_input = prompt
        st.rerun()

def dashboard_view():
    """Traditional dashboard view"""
    st.markdown('<h1 class="main-header">📊 Snowflake Monitoring Dashboard</h1>', unsafe_allow_html=True)
    
    # Quick metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Get overview data
    overview_data = execute_semantic_query(
        dimensions=["WAREHOUSE_NAME"],
        metrics=["TOTAL_CREDITS", "TOTAL_QUERIES"]
    )
    
    if overview_data is not None and not overview_data.empty:
        total_credits = float(overview_data['TOTAL_CREDITS'].sum())
        total_queries = float(overview_data['TOTAL_QUERIES'].sum()) if 'TOTAL_QUERIES' in overview_data.columns else 0
        active_warehouses = overview_data['WAREHOUSE_NAME'].nunique()
        estimated_cost = total_credits * 0.0004
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_credits:,.2f}</div>
                <div class="metric-label">Total Credits</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_queries:,}</div>
                <div class="metric-label">Total Queries</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{active_warehouses}</div>
                <div class="metric-label">Active Warehouses</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{format_currency(estimated_cost)}</div>
                <div class="metric-label">Estimated Cost</div>
            </div>
            """, unsafe_allow_html=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🏭 Warehouse Usage")
        
        if overview_data is not None and not overview_data.empty:
            warehouse_summary = overview_data.groupby('WAREHOUSE_NAME')['TOTAL_CREDITS'].sum().reset_index()
            fig = px.pie(warehouse_summary, values='TOTAL_CREDITS', names='WAREHOUSE_NAME',
                        title="Credits by Warehouse")
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📊 Warehouse Activity")
        
        if overview_data is not None and not overview_data.empty and 'TOTAL_QUERIES' in overview_data.columns:
            warehouse_activity = overview_data.groupby('WAREHOUSE_NAME').agg({
                'TOTAL_CREDITS': 'sum',
                'TOTAL_QUERIES': 'sum'
            }).reset_index()
            
            fig = px.scatter(warehouse_activity, x='TOTAL_QUERIES', y='TOTAL_CREDITS',
                           text='WAREHOUSE_NAME', title="Warehouse Activity Overview",
                           labels={'TOTAL_QUERIES': 'Total Queries', 'TOTAL_CREDITS': 'Total Credits'})
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application function"""
    # Navigation
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.selectbox(
        "Choose Interface",
        ["💬 Chat Interface", "📊 Dashboard View"]
    )
    
    # Page routing
    if page == "💬 Chat Interface":
        chat_interface()
    elif page == "📊 Dashboard View":
        dashboard_view()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Powered by Snowflake Semantic Views & Streamlit | "
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
