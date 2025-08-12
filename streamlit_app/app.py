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
import base64

# Page configuration
st.set_page_config(
    page_title="Snowflake Semantic Analytics - AI-Powered Business Intelligence",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, clean interface
st.markdown("""
<style>
    /* Dark theme with clean design */
    .main {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    
    .stApp {
        background-color: #1a1a1a !important;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #00d4ff, #0099cc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem 0;
    }
    
    /* Clean chat container */
    .chat-container {
        background: #2d2d2d;
        border-radius: 12px;
        padding: 24px;
        margin: 20px 0;
        border: 1px solid #404040;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    /* User message styling */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 18px 18px 4px 18px;
        margin: 12px 0;
        max-width: 85%;
        margin-left: auto;
        font-size: 16px;
        line-height: 1.4;
    }
    
    /* Assistant message styling */
    .assistant-message {
        background: #3a3a3a;
        color: #ffffff;
        padding: 20px;
        border-radius: 18px 18px 18px 4px;
        margin: 12px 0;
        max-width: 85%;
        border: 1px solid #404040;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    /* Concise answer styling */
    .concise-answer {
        background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin: 16px 0;
        font-size: 18px;
        font-weight: 600;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,212,255,0.3);
    }
    
    /* SQL dropdown styling */
    .sql-dropdown {
        background: #2a2a2a;
        border: 1px solid #404040;
        border-radius: 8px;
        margin: 12px 0;
    }
    
    .sql-content {
        background: #1e1e1e;
        color: #00ff00;
        padding: 16px;
        border-radius: 6px;
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 14px;
        line-height: 1.5;
        border: 1px solid #404040;
        margin: 8px 0;
    }
    
    /* Chart container */
    .chart-container {
        background: #2d2d2d;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        margin: 16px 0;
        border: 1px solid #404040;
    }
    
    /* Data preview styling */
    .data-preview {
        background: #2d2d2d;
        border-radius: 12px;
        padding: 20px;
        margin: 16px 0;
        border: 1px solid #404040;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 25px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102,126,234,0.4);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #404040;
        padding: 14px 20px;
        background: #2d2d2d;
        color: #ffffff;
        font-size: 16px;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #2d2d2d !important;
    }
    
    .sidebar .sidebar-content {
        background-color: #2d2d2d;
        color: #ffffff;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 12px rgba(102,126,234,0.3);
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
    
    /* AI insights styling */
    .ai-insights {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 16px;
        border-radius: 10px;
        margin: 12px 0;
        border-left: 4px solid #ff7f0e;
        color: #333;
    }
    
    /* Status indicators */
    .status-success {
        background: linear-gradient(135deg, #a8e6cf 0%, #dcedc1 100%);
        color: #2d5a2d;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
    }
    
    .status-error {
        background: linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%);
        color: #d63031;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 14px;
    }
    
    /* Hide Streamlit elements */
    .stDeployButton {
        display: none;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #2d2d2d;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #764ba2;
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

def get_cortex_analyst_token():
    """Get authentication token for Cortex Analyst API"""
    config = load_config()
    if not config:
        return None
    
    try:
        # Read token from file
        token_path = Path("/Users/akhilgurrapu/Documents/Projects/semanticSnowflake/snowflake-pat.token")
        with open(token_path, 'r') as f:
            token = f.read().strip()
        
        return token
    except Exception as e:
        st.error(f"Error reading token: {e}")
        return None

def call_cortex_analyst_api(user_query: str, semantic_views: List[str]) -> Dict[str, Any]:
    """
    Call Cortex Analyst REST API to understand user query and generate SQL
    """
    token = get_cortex_analyst_token()
    if not token:
        return None
    
    config = load_config()
    if not config:
        return None
    
    # Prepare the request payload
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_query
                    }
                ]
            }
        ],
        "semantic_models": [
            {"semantic_view": f"{config['database']}.{config['schema']}.{view}"} 
            for view in semantic_views
        ],
        "stream": False
    }
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Make the API call
    try:
        url = f"https://{config['account']}.snowflakecomputing.com/api/v2/cortex/analyst/message"
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Cortex Analyst API error: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error calling Cortex Analyst API: {e}")
        return None

def extract_sql_from_cortex_response(cortex_response: Dict[str, Any]) -> Optional[str]:
    """Extract SQL statement from Cortex Analyst response"""
    try:
        if 'message' in cortex_response and 'content' in cortex_response['message']:
            for content in cortex_response['message']['content']:
                if content.get('type') == 'sql' and 'statement' in content:
                    return content['statement']
        return None
    except Exception as e:
        st.error(f"Error extracting SQL from Cortex response: {e}")
        return None

def extract_text_from_cortex_response(cortex_response: Dict[str, Any]) -> Optional[str]:
    """Extract text explanation from Cortex Analyst response"""
    try:
        if 'message' in cortex_response and 'content' in cortex_response['message']:
            for content in cortex_response['message']['content']:
                if content.get('type') == 'text' and 'text' in content:
                    return content['text']
        return None
    except Exception as e:
        st.error(f"Error extracting text from Cortex response: {e}")
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

def execute_raw_sql_query(sql_query: str) -> Optional[pd.DataFrame]:
    """Execute raw SQL query from Cortex Analyst"""
    conn = get_snowflake_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute(sql_query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        
        df = pd.DataFrame(results, columns=columns)
        cursor.close()
        return df
        
    except Exception as e:
        st.error(f"Error executing SQL query: {e}")
        return None

def get_available_semantic_views() -> List[str]:
    """Get available semantic views"""
    return [
        "snowflake_monitoring_semantic",
        "query_performance_semantic", 
        "cost_analysis_semantic",
        "user_activity_semantic",
        "resource_utilization_semantic",
        "security_monitoring_semantic"
    ]

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

def generate_insights(df: pd.DataFrame, query: str) -> List[str]:
    """Generate AI-powered insights using vectorized operations"""
    insights = []
    
    if df.empty:
        return ["No data available for the specified query."]
    
    # Vectorized analysis for better performance
    if 'TOTAL_CREDITS' in df.columns:
        total_credits = float(df['TOTAL_CREDITS'].sum())
        if total_credits > 100:
            insights.append(f"💰 High credit consumption: {total_credits:.2f} credits")
        
        if 'WAREHOUSE_NAME' in df.columns:
            top_warehouse = df.groupby('WAREHOUSE_NAME')['TOTAL_CREDITS'].sum().idxmax()
            insights.append(f"🏭 Top consumer: {top_warehouse}")
    
    if 'AVG_EXECUTION_TIME' in df.columns:
        avg_time = float(df['AVG_EXECUTION_TIME'].mean())
        if avg_time > 30000:
            insights.append(f"⚡ Performance issue: {format_duration(avg_time)}")
        elif avg_time > 10000:
            insights.append(f"⚠️ Moderate performance: {format_duration(avg_time)}")
        else:
            insights.append(f"✅ Good performance: {format_duration(avg_time)}")
    
    if 'SLOW_QUERIES' in df.columns:
        slow_count = float(df['SLOW_QUERIES'].sum())
        if slow_count > 0:
            insights.append(f"🐌 {slow_count:.0f} slow queries detected")
    
    if 'USAGE_HOUR' in df.columns and 'TOTAL_CREDITS' in df.columns:
        peak_hour = df.groupby('USAGE_HOUR')['TOTAL_CREDITS'].sum().idxmax()
        insights.append(f"📊 Peak usage: Hour {peak_hour}")
    
    if 'USAGE_DATE' in df.columns and 'TOTAL_CREDITS' in df.columns:
        daily_credits = df.groupby('USAGE_DATE')['TOTAL_CREDITS'].sum()
        if len(daily_credits) > 1:
            trend = daily_credits.iloc[-1] - daily_credits.iloc[0]
            if trend > 0:
                insights.append("📈 Credit consumption increasing")
            elif trend < 0:
                insights.append("📉 Credit consumption decreasing")
    
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
    """Main chat interface with Cortex Analyst integration"""
    st.markdown('<h1 class="main-header">❄️ Snowflake AI-Powered Semantic Analytics</h1>', unsafe_allow_html=True)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Sidebar with connection status and quick actions
    with st.sidebar:
        st.title("🔧 Configuration")
        
        # Connection status
        conn = get_snowflake_connection()
        if conn:
            st.markdown('<div class="status-success">✅ Connected to Snowflake</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-error">❌ Connection failed</div>', unsafe_allow_html=True)
            return
        
        st.markdown("")  # Add spacing
        
        # Cortex Analyst status
        token = get_cortex_analyst_token()
        if token:
            st.markdown('<div class="status-success">✅ Cortex Analyst Ready</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-error">❌ Cortex Analyst not configured</div>', unsafe_allow_html=True)
            return
        
        st.markdown("---")
        st.title("🤖 AI-Powered Queries")
        
        # Natural Language Queries
        st.subheader("Ask Anything About Your Snowflake Data")
        st.info("💡 Try asking questions like:")
        st.markdown("""
        - "What's our total Snowflake usage?"
        - "Which warehouses cost the most?"
        - "Show me slow queries"
        - "Who are the most active users?"
        - "Any suspicious activity?"
        - "What's our peak usage time?"
        """)
        
        st.markdown("---")
        st.title("📊 Available Semantic Views")
        semantic_views = get_available_semantic_views()
        for view in semantic_views:
            st.write(f"• {view}")
        
        st.markdown("---")
        st.title("🔍 How It Works")
        st.info("""
        1. **AI Understanding**: Cortex Analyst interprets your natural language
        2. **Smart Selection**: Automatically chooses the best semantic view
        3. **SQL Generation**: Creates optimized SQL queries
        4. **Enhanced Results**: Provides insights and visualizations
        """)
    
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
        
        # Process the query with Cortex Analyst
        with st.chat_message("assistant"):
            with st.spinner("🤖 AI is analyzing your query..."):
                # Step 1: Call Cortex Analyst API
                semantic_views = get_available_semantic_views()
                cortex_response = call_cortex_analyst_api(prompt, semantic_views)
                
                if cortex_response:
                    # Extract AI interpretation and SQL
                    ai_interpretation = extract_text_from_cortex_response(cortex_response)
                    generated_sql = extract_sql_from_cortex_response(cortex_response)
                    
                    # Display AI interpretation
                    if ai_interpretation:
                        st.markdown(f"""
                        <div class="ai-insights">
                            <strong>🤖 AI Interpretation:</strong><br>
                            {ai_interpretation}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Display generated SQL in dropdown
                    if generated_sql:
                        with st.expander("🔍 View Generated SQL", expanded=False):
                            st.markdown(f"""
                            <div class="sql-content">
                                {generated_sql}
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Step 2: Execute the generated SQL
                        with st.spinner("📊 Executing query..."):
                            df = execute_raw_sql_query(generated_sql)
                            
                            if df is not None and not df.empty:
                                # Generate insights
                                insights = generate_insights(df, prompt)
                                
                                # Create comprehensive response
                                response = f"✅ **Query Results:**\n\n"
                                response += f"**Records Found:** {len(df)}\n\n"
                                
                                # Create concise answer first
                                concise_answer = ""
                                
                                # Extract the most relevant metric for concise answer
                                if 'TOTAL_COST' in df.columns:
                                    total_cost = float(df['TOTAL_COST'].sum())
                                    concise_answer = f"💰 **Total Cost:** {format_currency(total_cost)}"
                                elif 'TOTAL_CREDITS' in df.columns:
                                    total_credits = float(df['TOTAL_CREDITS'].sum())
                                    concise_answer = f"💳 **Total Credits:** {total_credits:,.2f}"
                                elif 'AVG_EXECUTION_TIME' in df.columns:
                                    avg_time = float(df['AVG_EXECUTION_TIME'].mean())
                                    concise_answer = f"⏱️ **Average Execution Time:** {format_duration(avg_time)}"
                                elif 'TOTAL_QUERIES' in df.columns:
                                    total_queries = float(df['TOTAL_QUERIES'].sum())
                                    concise_answer = f"📊 **Total Queries:** {total_queries:,.0f}"
                                else:
                                    concise_answer = f"📊 **Records Found:** {len(df)}"
                                
                                # Display concise answer prominently
                                st.markdown(f"""
                                <div class="concise-answer">
                                    {concise_answer}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Create detailed response
                                response = f"**📋 Detailed Analysis:**\n\n"
                                
                                # Provide comprehensive summary
                                if 'TOTAL_COST' in df.columns:
                                    total_cost = float(df['TOTAL_COST'].sum())
                                    response += f"• **Total Cost:** {format_currency(total_cost)}\n"
                                elif 'TOTAL_CREDITS' in df.columns:
                                    total_credits = float(df['TOTAL_CREDITS'].sum())
                                    response += f"• **Total Credits:** {total_credits:,.2f}\n"
                                
                                if 'AVG_EXECUTION_TIME' in df.columns:
                                    avg_time = float(df['AVG_EXECUTION_TIME'].mean())
                                    response += f"• **Average Execution Time:** {format_duration(avg_time)}\n"
                                
                                if 'TOTAL_QUERIES' in df.columns:
                                    total_queries = float(df['TOTAL_QUERIES'].sum())
                                    response += f"• **Total Queries:** {total_queries:,.0f}\n"
                                
                                if 'WAREHOUSE_NAME' in df.columns:
                                    unique_warehouses = df['WAREHOUSE_NAME'].nunique()
                                    response += f"• **Active Warehouses:** {unique_warehouses}\n"
                                
                                response += f"\n**📊 Data Summary:** Found **{len(df)}** records with the requested data.\n\n"
                                
                                # Show insights
                                if insights:
                                    response += "**🔍 AI Insights:**\n"
                                    for insight in insights:
                                        response += f"• {insight}\n"
                                    response += "\n"
                                
                                # Display the detailed response
                                st.markdown(response)
                                
                                # Show insights
                                if insights:
                                    st.markdown("**🔍 AI Insights:**")
                                    for insight in insights:
                                        st.markdown(f"• {insight}")
                                    st.markdown("")
                                
                                # Create visualization if data supports it
                                if len(df) > 1 and any(col in df.columns for col in ['TOTAL_COST', 'TOTAL_CREDITS', 'AVG_EXECUTION_TIME', 'TOTAL_QUERIES']):
                                    st.markdown("**📈 Data Visualization:**")
                                    fig = create_visualization(df, [], [])
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                # Show expanded data preview
                                st.markdown("**📊 Data Preview:**")
                                st.dataframe(df, use_container_width=True)
                                
                                # Add assistant response to chat history
                                st.session_state.messages.append({"role": "assistant", "content": response})
                                
                            else:
                                error_msg = "❌ No data found for your query. The AI-generated SQL didn't return any results."
                                st.markdown(f'<div class="status-error">{error_msg}</div>', unsafe_allow_html=True)
                                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    else:
                        error_msg = "❌ Cortex Analyst couldn't generate SQL for your query. Try rephrasing your question."
                        st.markdown(f'<div class="status-error">{error_msg}</div>', unsafe_allow_html=True)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                else:
                    error_msg = "❌ Failed to connect to Cortex Analyst. Please check your configuration."
                    st.markdown(f'<div class="status-error">{error_msg}</div>', unsafe_allow_html=True)
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
                <div class="metric-value">{total_credits:,.0f}</div>
                <div class="metric-label">Total Credits</div>
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
        ["🤖 AI Chat Interface", "📊 Dashboard View"]
    )
    
    # Page routing
    if page == "🤖 AI Chat Interface":
        chat_interface()
    elif page == "📊 Dashboard View":
        dashboard_view()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Powered by Snowflake Cortex Analyst & Semantic Views | "
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
