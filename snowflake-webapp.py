import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from typing import List, Dict, Any, Optional
from snowflake.snowpark.context import get_active_session
import requests  # For token-based authentication fallback

# Configuration constants
CONFIG = {
    'app_title': 'Snowflake Semantic Analytics - AI-Powered Business Intelligence',
    'app_icon': '❄️', 
    'credit_to_dollar_rate': 3,  # 1 credit = $3
    'api_timeout': 30,
    'cortex_model': 'llama3.1-8b',
    'semantic_schema': 'SNOWFLAKE_MONITORING.MONITORING_SEMANTIC'
}

# Page configuration
st.set_page_config(
    page_title=CONFIG['app_title'],
    page_icon=CONFIG['app_icon'],
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
    
    .status-warning {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        color: #e17055;
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
    """Get active Snowflake session with error handling"""
    try:
        return get_active_session()
    except Exception as e:
        st.error(f"Failed to connect to Snowflake: {e}")
        return None

def get_account_info(session) -> Dict[str, str]:
    """Get account and region information from session"""
    try:
        result = session.sql("SELECT CURRENT_ACCOUNT() as account, CURRENT_REGION() as region").collect()
        if result:
            return {
                'account': result[0]['ACCOUNT'],
                'region': result[0]['REGION'],
                'url': f"{result[0]['ACCOUNT']}.{result[0]['REGION']}.snowflakecomputing.com"
            }
    except Exception as e:
        st.error(f"Failed to get account info: {e}")
    return {}

def get_auth_method(session) -> str:
    """Determine the best authentication method for Cortex Analyst"""
    try:
        # Try to get token from session connection
        conn = session._conn
        if hasattr(conn, 'token') and conn.token:
            return conn.token
        
        # Check for SiS environment
        import importlib.util
        if importlib.util.find_spec("_snowflake") is not None:
            return "sis_native"
            
        return None
    except Exception:
        return "sis_native"  # Default to SiS native

def call_cortex_analyst_api(user_query: str, semantic_views: List[str]) -> Dict[str, Any]:
    """Call Cortex Analyst REST API with dynamic authentication"""
    session = get_snowflake_session()
    if not session:
        return None
    
    account_info = get_account_info(session)
    if not account_info:
        return None
        
    auth_method = get_auth_method(session)
    
    if auth_method == "sis_native":
        return call_cortex_analyst_native(user_query, semantic_views, session)
    elif auth_method:
        return call_cortex_analyst_token(user_query, semantic_views, account_info['url'], auth_method)
    else:
        st.error("No valid authentication available")
        return None

def create_cortex_payload(user_query: str, semantic_views: List[str]) -> Dict[str, Any]:
    """Create standardized payload for Cortex Analyst API"""
    return {
        "messages": [{
            "role": "user",
            "content": [{"type": "text", "text": user_query}]
        }],
        "semantic_models": [
            {"semantic_view": f"{CONFIG['semantic_schema']}.{view}"} 
            for view in semantic_views
        ],
        "stream": False
    }

def call_cortex_analyst_token(user_query: str, semantic_views: List[str], account_url: str, token: str) -> Dict[str, Any]:
    """Call Cortex Analyst with token authentication"""
    payload = create_cortex_payload(user_query, semantic_views)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"https://{account_url}/api/v2/cortex/analyst/message",
            headers=headers,
            json=payload,
            timeout=CONFIG['api_timeout']
        )
        
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        st.error(f"API call failed: {e}")
        return None

def call_cortex_analyst_native(user_query: str, semantic_views: List[str], session) -> Dict[str, Any]:
    """Call Cortex Analyst using native SiS capabilities"""
    try:
        import _snowflake
        import json
        
        request_body = create_cortex_payload(user_query, semantic_views)
        
        resp = _snowflake.send_snow_api_request(
            "POST",
            "/api/v2/cortex/analyst/message",
            {}, {}, request_body, None,
            CONFIG['api_timeout']
        )
        
        if resp and resp.get('status') == 200:
            content = resp.get('content', '{}')
            return json.loads(content) if isinstance(content, str) else content
        
        st.error(f"Native API error: {resp}")
        return None
        
    except ImportError:
        st.error("SiS environment required for native calls")
        return None
    except Exception as e:
        st.error(f"Native API call failed: {e}")
        return None

# Response parsing utilities

def extract_from_cortex_response(response: Dict[str, Any], content_type: str) -> Optional[str]:
    """Extract content from Cortex Analyst response by type"""
    try:
        if 'message' in response and 'content' in response['message']:
            for content in response['message']['content']:
                if content.get('type') == content_type:
                    return content.get('statement' if content_type == 'sql' else 'text')
        return None
    except Exception as e:
        st.error(f"Error extracting {content_type}: {e}")
        return None

def extract_sql_from_cortex_response(response: Dict[str, Any]) -> Optional[str]:
    """Extract SQL statement from Cortex Analyst response"""
    return extract_from_cortex_response(response, 'sql')

def extract_text_from_cortex_response(response: Dict[str, Any]) -> Optional[str]:
    """Extract text explanation from Cortex Analyst response"""
    return extract_from_cortex_response(response, 'text')

def execute_sql_query(sql_query: str) -> Optional[pd.DataFrame]:
    """Execute SQL query using Snowpark session"""
    session = get_snowflake_session()
    if not session:
        return None
    
    try:
        result = session.sql(sql_query).collect()
        return pd.DataFrame([row.as_dict() for row in result]) if result else pd.DataFrame()
    except Exception as e:
        st.error(f"Query execution failed: {e}")
        return None

@st.cache_data
def get_available_semantic_views() -> List[str]:
    """Get available semantic views dynamically"""
    session = get_snowflake_session()
    if not session:
        # Fallback to known views
        return [
            "snowflake_monitoring_semantic",
            "query_performance_semantic", 
            "cost_analysis_semantic",
            "user_activity_semantic",
            "resource_utilization_semantic",
            "security_monitoring_semantic"
        ]
    
    try:
        # Try to get views dynamically from the schema
        schema_parts = CONFIG['semantic_schema'].split('.')
        query = f"""
        SELECT table_name 
        FROM {schema_parts[0]}.information_schema.tables 
        WHERE table_schema = '{schema_parts[1]}' 
        AND table_type = 'VIEW'
        AND table_name LIKE '%semantic%'
        """
        result = session.sql(query).collect()
        if result:
            return [row['TABLE_NAME'].lower() for row in result]
    except Exception:
        pass
    
    # Fallback to known views
    return [
        "snowflake_monitoring_semantic",
        "query_performance_semantic", 
        "cost_analysis_semantic",
        "user_activity_semantic",
        "resource_utilization_semantic",
        "security_monitoring_semantic"
    ]

# Formatting utilities
def format_currency(credits: float) -> str:
    """Convert credits to currency display"""
    if pd.isna(credits) or credits == 0:
        return "$0.00 (0 credits)"
    
    dollars = credits * CONFIG['credit_to_dollar_rate']
    return f"${dollars:,.2f} ({credits:,.1f} credits)"

def format_credits(credits: float) -> str:
    """Format credits without currency conversion"""
    if pd.isna(credits) or credits == 0:
        return "0 credits"
    return f"{credits:,.1f} credits"

def format_duration(seconds: float) -> str:
    """Format duration in human readable format"""
    if pd.isna(seconds) or seconds == 0:
        return "0s"
    
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        return f"{seconds/60:.1f}m"
    else:
        return f"{seconds/3600:.1f}h"

def generate_intelligent_answer(df: pd.DataFrame, user_query: str, session) -> str:
    """Generate intelligent answer using Cortex LLM or fallback"""
    if df.empty:
        return "No data found for your query."
    
    try:
        data_summary = create_data_summary(df)
        
        prompt = f"""
        Question: {user_query}
        Data: {data_summary}
        
        Provide a concise answer with specific numbers. 
        For costs: multiply credits by {CONFIG['credit_to_dollar_rate']} for dollars.
        Format: "X credits ($Y)" where Y = X × {CONFIG['credit_to_dollar_rate']}.
        Keep under 25 words.
        """
        
        result = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                '{CONFIG['cortex_model']}',
                '{prompt.replace("'", "''")}'
            ) as answer
        """).collect()
        
        if result:
            answer = result[0]['ANSWER'].strip().strip('"')
            return answer if answer else generate_fallback_answer(df)
            
    except Exception:
        pass
    
    return generate_fallback_answer(df)

def create_data_summary(df: pd.DataFrame) -> str:
    """Create concise data summary for LLM analysis"""
    if df.empty:
        return "No data"
    
    summary = [f"Columns: {', '.join(df.columns[:4])}"]
    
    # Add top 3 rows with key info
    for idx, row in df.head(3).iterrows():
        row_data = []
        for col in df.columns[:4]:
            if col in row and pd.notna(row[col]):
                row_data.append(f"{col}: {row[col]}")
        if row_data:
            summary.append(f"Row {idx + 1}: {', '.join(row_data)}")
    
    summary.append(f"Total: {len(df)} rows")
    return " | ".join(summary)

def generate_fallback_answer(df: pd.DataFrame) -> str:
    """Generate rule-based fallback answer"""
    if df.empty:
        return "No data found"
    
    # Identify column types
    cost_cols = [col for col in df.columns if any(term in col.lower() for term in ['cost', 'credit', 'price'])]
    warehouse_cols = [col for col in df.columns if 'warehouse' in col.lower()]
    user_cols = [col for col in df.columns if 'user' in col.lower()]
    time_cols = [col for col in df.columns if any(term in col.lower() for term in ['time', 'duration', 'execution'])]
    
    first_row = df.iloc[0]
    
    if cost_cols and warehouse_cols:
        cost_val = first_row[cost_cols[0]]
        warehouse = first_row[warehouse_cols[0]]
        if 'credit' in cost_cols[0].lower():
            dollars = cost_val * CONFIG['credit_to_dollar_rate']
            return f"{warehouse} leads with {cost_val:,.1f} credits (${dollars:,.2f})"
        return f"{warehouse} has highest cost: {format_currency(cost_val)}"
    
    elif time_cols and warehouse_cols:
        time_val = first_row[time_cols[0]]
        warehouse = first_row[warehouse_cols[0]]
        return f"{warehouse} has longest time: {format_duration(time_val)}"
    
    elif user_cols:
        return f"Top user: {first_row[user_cols[0]]}"
    
    # Default response
    return f"Found {len(df)} results - top: {df.columns[0]} = {first_row[df.columns[0]]}"

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
        st.subheader("🔍 How It Works (SiS)")
        st.info("""
        1. **Native AI Integration**: Uses Snowflake's CORTEX.ANALYST function
        2. **Semantic View Selection**: Automatically queries appropriate semantic views
        3. **Optimized Queries**: Generates SEMANTIC_VIEW() function calls
        4. **SiS Environment**: Runs entirely within Snowflake infrastructure
        """)
        
        # Dynamic suggested queries
        st.subheader("💡 Try These Questions")
        suggested_queries = get_suggested_queries()
        
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
        auth_method = get_auth_method(session) if session else None
        if auth_method == "sis_native":
            st.markdown('<div class="status-success">✅ Cortex Analyst Ready (SiS Native)</div>', unsafe_allow_html=True)
        elif auth_method:
            st.markdown('<div class="status-success">✅ Cortex Analyst Ready (Token)</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-warning">⚠️ Limited functionality</div>', unsafe_allow_html=True)
    
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
                    # Extract AI interpretation and SQL - exactly like local app.py
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
                        
                        # Execute the generated SQL
                        with st.spinner("📊 Executing query..."):
                            df = execute_sql_query(generated_sql)
                            
                            if df is not None and not df.empty:
                                # Generate intelligent answer
                                session = get_snowflake_session()
                                concise_answer = generate_intelligent_answer(df, prompt, session)
                                st.markdown(f"""
                                <div class="concise-answer">
                                    🎯 <strong>Answer:</strong> {concise_answer}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Show data results
                                st.markdown("**📊 Query Results:**")
                                st.dataframe(df, use_container_width=True)
                                
                                # Create visualization if data supports it
                                if len(df) > 1:
                                    st.markdown("**📈 Data Visualization:**")
                                    fig = create_simple_visualization(df)
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                # Add assistant response to chat history
                                response_content = f"Answer: {concise_answer}\n\nAI Analysis: {ai_interpretation}\n\nData: {len(df)} records found"
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
    st.markdown('<h1 class="main-header">📊 Snowflake Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Get session
    session = get_snowflake_session()
    if not session:
        st.error("❌ Unable to connect to Snowflake")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Get overview data
    base_view = get_available_semantic_views()[0]  # Use first available view
    overview_data = execute_sql_query(f"""
        SELECT 
            WAREHOUSE_NAME,
            SUM(TOTAL_CREDITS) as TOTAL_CREDITS,
            SUM(TOTAL_QUERIES) as TOTAL_QUERIES
        FROM {CONFIG['semantic_schema']}.{base_view}
        GROUP BY WAREHOUSE_NAME
    """)
    
    if overview_data is not None and not overview_data.empty:
        total_credits = float(overview_data['TOTAL_CREDITS'].sum())
        total_queries = float(overview_data['TOTAL_QUERIES'].sum()) if 'TOTAL_QUERIES' in overview_data.columns else 0
        active_warehouses = overview_data['WAREHOUSE_NAME'].nunique()
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{format_credits(total_credits)}</div>
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
            dollar_amount = total_credits * CONFIG['credit_to_dollar_rate']
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">${dollar_amount:,.2f}</div>
                <div class="metric-label">Estimated Cost ({total_credits:,.1f} credits)</div>
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

@st.cache_data
def get_suggested_queries() -> List[str]:
    """Get suggested queries based on available semantic views"""
    return [
        "What's our total Snowflake usage?",
        "Which warehouses cost the most?", 
        "Show me slow queries",
        "Who are the most active users?",
        "Any suspicious activity?",
        "What's the cost trend?"
    ]

def render_sidebar_info():
    """Render sidebar information"""
    st.sidebar.markdown(f"""
    ### {CONFIG['app_icon']} SiS Analytics
    - Native Snowpark Session
    - Cortex Analyst AI
    - Dynamic Semantic Views
    - Credit Rate: 1 = ${CONFIG['credit_to_dollar_rate']}
    """)

def render_footer():
    """Render application footer"""
    st.markdown("---")
    st.markdown(
        f"<div style='text-align: center; color: #666;'>"
        f"{CONFIG['app_icon']} Powered by Snowflake SiS | "
        f"Cortex Analyst | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        "</div>",
        unsafe_allow_html=True
    )

def main():
    """Main application entry point"""
    render_sidebar_info()
    
    # Navigation
    st.sidebar.title("🎯 Navigation")
    page = st.sidebar.selectbox(
        "Choose Interface",
        ["🤖 AI Chat", "📊 Dashboard"]
    )
    
    # Route to appropriate interface
    if page == "🤖 AI Chat":
        chat_interface()
    else:
        dashboard_view()
    
    render_footer()

if __name__ == "__main__":
    main()
