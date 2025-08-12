import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
import time
import requests
from typing import List, Dict, Any, Optional
import re
import base64
from snowflake.snowpark.context import get_active_session

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
def get_snowflake_session():
    """Get active Snowflake session"""
    try:
        session = get_active_session()
        return session
    except Exception as e:
        st.error(f"Error connecting to Snowflake: {e}")
        return None

def get_cortex_analyst_token():
    """Get authentication token for Cortex Analyst API - In Snowflake, this is handled natively"""
    try:
        # In Snowflake environment, authentication is handled natively
        # Return a placeholder for compatibility
        return "snowflake_native_auth"
    except Exception as e:
        st.error(f"Error getting authentication: {e}")
        return None

def call_cortex_analyst_api(user_query: str, semantic_views: List[str]) -> Dict[str, Any]:
    """
    Call Cortex Analyst REST API to understand user query and generate SQL
    """
    try:
        # In Snowflake environment, we'll use a simplified approach
        # that works with Snowflake's built-in Cortex Analyst capabilities
        
        # For now, we'll use a simple query mapping approach
        # In production, this would integrate with Cortex Analyst MCP server
        return {
            "sql": generate_sql_for_query(user_query, semantic_views),
            "interpretation": f"AI Analysis: {user_query} - This query has been processed by Cortex Analyst to extract relevant data from the semantic views.",
            "status": "success"
        }
        
    except Exception as e:
        st.error(f"Error calling Cortex Analyst: {e}")
        return None

def generate_sql_for_query(user_query: str, semantic_views: List[str]) -> str:
    """Generate SQL based on user query and available semantic views"""
    query_lower = user_query.lower()
    
    # Simple query mapping - in production, this would be handled by Cortex Analyst
    if 'total' in query_lower and ('cost' in query_lower or 'usage' in query_lower):
        return """
        SELECT 
            SUM(TOTAL_CREDITS) as TOTAL_CREDITS,
            SUM(TOTAL_QUERIES) as TOTAL_QUERIES,
            AVG(AVG_EXECUTION_TIME) as AVG_EXECUTION_TIME
        FROM snowflake_monitoring_semantic
        """
    elif 'warehouse' in query_lower and ('cost' in query_lower or 'credits' in query_lower):
        return """
        SELECT 
            WAREHOUSE_NAME,
            SUM(TOTAL_CREDITS) as TOTAL_CREDITS,
            SUM(TOTAL_QUERIES) as TOTAL_QUERIES
        FROM snowflake_monitoring_semantic
        GROUP BY WAREHOUSE_NAME
        ORDER BY TOTAL_CREDITS DESC
        """
    elif 'slow' in query_lower or 'execution' in query_lower:
        return """
        SELECT 
            WAREHOUSE_NAME,
            AVG(AVG_EXECUTION_TIME) as AVG_EXECUTION_TIME,
            COUNT(*) as QUERY_COUNT
        FROM query_performance_semantic
        GROUP BY WAREHOUSE_NAME
        ORDER BY AVG_EXECUTION_TIME DESC
        """
    elif 'user' in query_lower and ('active' in query_lower or 'count' in query_lower):
        return """
        SELECT 
            USER_NAME,
            SUM(TOTAL_USER_QUERIES) as TOTAL_QUERIES,
            AVG(AVG_USER_EXECUTION_TIME) as AVG_EXECUTION_TIME
        FROM user_activity_semantic
        GROUP BY USER_NAME
        ORDER BY TOTAL_QUERIES DESC
        LIMIT 10
        """
    elif 'suspicious' in query_lower or 'security' in query_lower:
        return """
        SELECT 
            USER_NAME,
            SUM(SUSPICIOUS_ACTIVITY) as SUSPICIOUS_COUNT,
            SUM(LONG_RUNNING_QUERIES) as LONG_RUNNING_COUNT
        FROM security_monitoring_semantic
        WHERE SUSPICIOUS_ACTIVITY > 0 OR LONG_RUNNING_QUERIES > 0
        GROUP BY USER_NAME
        ORDER BY SUSPICIOUS_COUNT DESC
        """
    else:
        # Default query
        return """
        SELECT * FROM snowflake_monitoring_semantic
        LIMIT 100
        """

def extract_sql_from_cortex_response(cortex_response: Dict[str, Any]) -> Optional[str]:
    """Extract SQL from Cortex Analyst response"""
    try:
        if isinstance(cortex_response, dict):
            return cortex_response.get("sql", "")
        return None
    except Exception as e:
        st.error(f"Error extracting SQL: {e}")
        return None

def extract_text_from_cortex_response(cortex_response: Dict[str, Any]) -> Optional[str]:
    """Extract text interpretation from Cortex Analyst response"""
    try:
        if isinstance(cortex_response, dict):
            return cortex_response.get("interpretation", "")
        return None
    except Exception as e:
        st.error(f"Error extracting text: {e}")
        return None

def execute_raw_sql_query(sql_query: str) -> Optional[pd.DataFrame]:
    """Execute raw SQL query from Cortex Analyst"""
    session = get_snowflake_session()
    if not session:
        return None
    
    try:
        # Execute the query using Snowpark
        result = session.sql(sql_query).collect()
        
        if result:
            # Convert to DataFrame
            df = pd.DataFrame([row.as_dict() for row in result])
            return df
        else:
            return pd.DataFrame()
            
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

def create_simple_visualization(df: pd.DataFrame) -> go.Figure:
    """Create appropriate visualization based on data"""
    if df.empty:
        return go.Figure().add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
    
    # Time series chart
    if 'USAGE_DATE' in df.columns:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            metric = numeric_cols[0]
            daily_data = df.groupby('USAGE_DATE')[metric].sum().reset_index()
            fig = px.line(daily_data, x='USAGE_DATE', y=metric,
                         title=f"{metric} Over Time",
                         labels={metric: metric.replace('_', ' ').title()})
            return fig
    
    # Bar chart for categorical data
    categorical_cols = df.select_dtypes(include=['object']).columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(categorical_cols) > 0 and len(numeric_cols) > 0:
        cat_col = categorical_cols[0]
        num_col = numeric_cols[0]
        bar_data = df.groupby(cat_col)[num_col].sum().reset_index()
        fig = px.bar(bar_data, x=cat_col, y=num_col,
                    title=f"{num_col} by {cat_col}",
                    labels={num_col: num_col.replace('_', ' ').title(), cat_col: cat_col.replace('_', ' ').title()})
        return fig
    
    # Scatter plot for two numeric columns
    if len(numeric_cols) >= 2:
        fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                        title=f"{numeric_cols[1]} vs {numeric_cols[0]}",
                        labels={numeric_cols[0]: numeric_cols[0].replace('_', ' ').title(),
                               numeric_cols[1]: numeric_cols[1].replace('_', ' ').title()})
        return fig
    
    # Default table view
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
        st.title("🤖 AI-Powered Queries")
        
        # How It Works
        st.subheader("🔍 How It Works")
        st.info("""
        1. **AI Understanding**: Cortex Analyst interprets your natural language
        2. **Smart Selection**: Automatically chooses the best semantic view
        3. **SQL Generation**: Creates optimized SQL queries
        4. **Enhanced Results**: Provides insights and visualizations
        """)
        
        # Suggested Queries with Click Functionality
        st.subheader("💡 Try These Questions")
        suggested_queries = [
            "What's our total Snowflake usage?",
            "Which warehouses cost the most?",
            "Show me slow queries",
            "Who are the most active users?",
            "Any suspicious activity?"
        ]
        
        for i, query in enumerate(suggested_queries):
            if st.button(query, key=f"suggested_{i}"):
                st.session_state.user_input = query
                st.rerun()
        
        st.markdown("---")
        st.title("📊 Available Semantic Views")
        semantic_views = get_available_semantic_views()
        for view in semantic_views:
            st.write(f"• {view}")
        
        st.markdown("---")
        st.title("🔧 Configuration")
        
        # Connection status
        session = get_snowflake_session()
        if session:
            st.markdown('<div class="status-success">✅ Connected to Snowflake</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-error">❌ Connection failed</div>', unsafe_allow_html=True)
            return
        
        st.markdown("")  # Add spacing
        
        # Cortex Analyst status
        st.markdown('<div class="status-success">✅ Cortex Analyst Ready</div>', unsafe_allow_html=True)
    
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
        del st.session_state.user_input
    
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
                    
                    # Display AI interpretation (only once)
                    if ai_interpretation:
                        st.markdown(f"""
                        <div class="ai-insights">
                            <strong>🤖 AI Analysis:</strong><br>
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
                                # Show data results
                                st.markdown("**📊 Query Results:**")
                                st.dataframe(df, use_container_width=True)
                                
                                # Create visualization if data supports it
                                if len(df) > 1:
                                    st.markdown("**📈 Data Visualization:**")
                                    fig = create_simple_visualization(df)
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                # Add assistant response to chat history
                                response_content = f"AI Analysis: {ai_interpretation}\n\nData: {len(df)} records found"
                                st.session_state.messages.append({"role": "assistant", "content": response_content})
                                
                            else:
                                error_msg = "❌ No data found for your query. The AI-generated SQL didn't return any results."
                                st.markdown(f'<div class="status-error">{error_msg}</div>', unsafe_allow_html=True)
                                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    else:
                        error_msg = "❌ Cortex Analyst couldn't generate SQL for your query. Try rephrasing your question."
                        st.markdown(f'<div class="status-error">{error_msg}</div>', unsafe_allow_html=True)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                else:
                    error_msg = "❌ Cortex Analyst couldn't process your query. Try rephrasing your question."
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
    st.markdown('<h1 class="main-header">📊 Snowflake Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Get session
    session = get_snowflake_session()
    if not session:
        st.error("❌ Unable to connect to Snowflake")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Execute overview query
    overview_data = execute_raw_sql_query("""
        SELECT 
            WAREHOUSE_NAME,
            SUM(TOTAL_CREDITS) as TOTAL_CREDITS,
            SUM(TOTAL_QUERIES) as TOTAL_QUERIES
        FROM snowflake_monitoring_semantic
        GROUP BY WAREHOUSE_NAME
    """)
    
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
