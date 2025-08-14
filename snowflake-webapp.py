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

def check_semantic_view_exists(semantic_view: str) -> bool:
    """Check if semantic view exists"""
    session = get_snowflake_session()
    if not session:
        return False
    
    try:
        # Try to show the semantic view
        query = f"SHOW SEMANTIC VIEWS LIKE '{semantic_view}' IN {CONFIG['semantic_schema']}"
        result = session.sql(query).collect()
        return len(result) > 0
    except Exception:
        try:
            # Alternative check - try to query information schema
            schema_parts = CONFIG['semantic_schema'].split('.')
            query = f"""
            SELECT table_name 
            FROM {schema_parts[0]}.information_schema.tables 
            WHERE table_schema = '{schema_parts[1]}' 
            AND table_name = '{semantic_view.upper()}'
            """
            result = session.sql(query).collect()
            return len(result) > 0
        except Exception:
            return False

def get_semantic_view_info(semantic_view: str) -> Dict[str, Any]:
    """Get information about available dimensions and metrics in a semantic view"""
    session = get_snowflake_session()
    if not session:
        return {}
    
    info = {"dimensions": [], "metrics": [], "tables": [], "exists": False, "can_query": False}
    
    # First check if semantic view exists
    info["exists"] = check_semantic_view_exists(semantic_view)
    
    if not info["exists"]:
        return info
    
    # Use the recommended SHOW commands to discover structure
    try:
        # Method 1: Get dimensions using SHOW SEMANTIC DIMENSIONS
        try:
            dim_result = session.sql(f"SHOW SEMANTIC DIMENSIONS IN {CONFIG['semantic_schema']}.{semantic_view}").collect()
            table_names = set()
            for row in dim_result:
                row_dict = row.as_dict()
                name = row_dict.get('name', '')
                table_name = row_dict.get('table_name', '')
                if table_name:
                    table_names.add(table_name)
                    info["dimensions"].append(f"{table_name}.{name}")
                else:
                    info["dimensions"].append(name)
            
            # Store unique table names
            info["tables"] = list(table_names)
        except Exception as e:
            st.warning(f"Could not get semantic dimensions: {e}")
        
        # Method 2: Get metrics using SHOW SEMANTIC METRICS  
        try:
            metric_result = session.sql(f"SHOW SEMANTIC METRICS IN {CONFIG['semantic_schema']}.{semantic_view}").collect()
            for row in metric_result:
                row_dict = row.as_dict()
                name = row_dict.get('name', '')
                table_name = row_dict.get('table_name', '')
                if table_name:
                    info["metrics"].append(f"{table_name}.{name}")
                else:
                    info["metrics"].append(name)
        except Exception as e:
            st.warning(f"Could not get semantic metrics: {e}")
            
    except Exception as e:
        st.warning(f"Could not get semantic view structure: {e}")
    
    # Test if we can query with what we found
    if info["dimensions"] or info["metrics"] or info["tables"]:
        info["can_query"] = True
    else:
        # Try a simple wildcard query as last resort
        try:
            # Try the documented approach: use *.* for all dimensions and metrics
            test_query = f"SELECT * FROM SEMANTIC_VIEW({CONFIG['semantic_schema']}.{semantic_view} DIMENSIONS *.* METRICS *.*) LIMIT 1"
            session.sql(test_query).collect()
            info["can_query"] = True
        except Exception as e:
            info["can_query"] = False
            st.warning(f"Cannot query semantic view: {e}")
    
    return info

def execute_semantic_view_query(semantic_view: str, dimensions: List[str] = None, metrics: List[str] = None, where_clause: str = None) -> Optional[pd.DataFrame]:
    """Execute semantic view query with proper syntax"""
    session = get_snowflake_session()
    if not session:
        return None
    
    # SEMANTIC_VIEW requires at least one of DIMENSIONS, METRICS, or FACTS
    # Note: Plain wildcards (*) are not supported, need table.* format
    if not dimensions and not metrics:
        # Cannot proceed without knowing table names for wildcards
        st.error("Cannot query semantic view without knowing dimensions, metrics, or table names")
        return None
    
    try:
        # Build semantic view query
        parts = ["SELECT * FROM SEMANTIC_VIEW("]
        parts.append(f"    {CONFIG['semantic_schema']}.{semantic_view}")
        
        if dimensions:
            parts.append(f"    DIMENSIONS {', '.join(dimensions)}")
        
        if metrics:
            parts.append(f"    METRICS {', '.join(metrics)}")
        
        parts.append(")")
        
        if where_clause:
            parts.append(f"WHERE {where_clause}")
        
        sql_query = "\n".join(parts)
        
        result = session.sql(sql_query).collect()
        return pd.DataFrame([row.as_dict() for row in result]) if result else pd.DataFrame()
    except Exception as e:
        st.error(f"Semantic view query failed: {e}")
        # Fallback to a simple query that should work
        try:
            fallback_query = f"SHOW COLUMNS IN {CONFIG['semantic_schema']}.{semantic_view}"
            session.sql(fallback_query).collect()
            st.info("Semantic view exists but query syntax may need adjustment")
        except Exception:
            st.error(f"Semantic view {semantic_view} may not exist or is not accessible")
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
    
    found_views = []
    
    try:
        # First try to show semantic views directly
        query = f"SHOW SEMANTIC VIEWS IN {CONFIG['semantic_schema']}"
        result = session.sql(query).collect()
        if result:
            found_views = [row['name'].lower() for row in result if 'name' in row.as_dict()]
    except Exception:
        try:
            # Fallback: try to get views from information schema
            schema_parts = CONFIG['semantic_schema'].split('.')
            query = f"""
            SELECT table_name 
            FROM {schema_parts[0]}.information_schema.tables 
            WHERE table_schema = '{schema_parts[1]}' 
            AND (table_type = 'VIEW' OR table_type = 'SEMANTIC VIEW')
            AND table_name LIKE '%SEMANTIC%'
            """
            result = session.sql(query).collect()
            if result:
                found_views = [row['TABLE_NAME'].lower() for row in result]
        except Exception:
            pass
    
    # If we found actual views, return them, otherwise use fallback
    if found_views:
        return found_views
    
    # Fallback to known views
    return [
        "sample_warehouse_usage",  # Simple test view from account usage
        "simple_test_view",        # Ultra simple test view with hardcoded data
        "cost_analysis_semantic",  # Your existing views
        "snowflake_monitoring_semantic",
        "query_performance_semantic", 
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
    """Generate intelligent answer with detailed context and object names"""
    if df.empty:
        return "No data found for your query."
    
    try:
        # Enhanced data analysis with object identification
        detailed_answer = generate_detailed_object_answer(df, user_query)
        if detailed_answer:
            return detailed_answer
        
        # Fallback to LLM if detailed analysis fails
        data_summary = create_enhanced_data_summary(df, user_query)
        
        prompt = f"""
        Question: {user_query}
        Data: {data_summary}
        
        Provide a concise, focused answer that includes:
        1. Specific object names (warehouse names, user names, etc.)
        2. Key numbers with proper formatting (credits as "X credits ($Y)")
        3. Brief comparison or pattern if relevant
        4. One actionable insight if applicable
        
        For costs: multiply credits by {CONFIG['credit_to_dollar_rate']} for dollars.
        Format credits as "X credits ($Y)" where Y = X × {CONFIG['credit_to_dollar_rate']}.
        Format durations as readable time (e.g., "2.5 minutes" not "150000ms").
        Keep under 50 words. Be direct and actionable.
        """
        
        result = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                '{CONFIG['cortex_model']}',
                '{prompt.replace("'", "''")}'
            ) as answer
        """).collect()
        
        if result:
            answer = result[0]['ANSWER'].strip().strip('"')
            return answer if answer else generate_enhanced_fallback_answer(df, user_query)
            
    except Exception:
        pass
    
    return generate_enhanced_fallback_answer(df, user_query)

def generate_detailed_object_answer(df: pd.DataFrame, user_query: str) -> str:
    """Generate detailed answer with specific object identification"""
    if df.empty:
        return None
    
    # Identify column types for better analysis
    warehouse_cols = [col for col in df.columns if 'warehouse' in col.lower()]
    user_cols = [col for col in df.columns if 'user' in col.lower()]
    cost_cols = [col for col in df.columns if any(term in col.lower() for term in ['cost', 'credit', 'spend'])]
    time_cols = [col for col in df.columns if any(term in col.lower() for term in ['time', 'duration', 'execution'])]
    query_cols = [col for col in df.columns if 'query' in col.lower()]
    date_cols = [col for col in df.columns if any(term in col.lower() for term in ['date', 'time'])]
    
    query_lower = user_query.lower()
    
    # Cost analysis with warehouse identification
    if any(term in query_lower for term in ['cost', 'spend', 'billing', 'usage', 'credit']) and warehouse_cols and cost_cols:
        return generate_cost_analysis_answer(df, warehouse_cols[0], cost_cols[0])
    
    # User activity analysis
    if any(term in query_lower for term in ['user', 'who', 'person', 'account']) and user_cols:
        return generate_user_activity_answer(df, user_cols[0], query_cols[0] if query_cols else None)
    
    # Performance analysis
    if any(term in query_lower for term in ['slow', 'performance', 'time', 'execution']) and warehouse_cols and time_cols:
        return generate_performance_answer(df, warehouse_cols[0], time_cols[0])
    
    # Warehouse analysis
    if any(term in query_lower for term in ['warehouse', 'compute', 'resource']) and warehouse_cols:
        return generate_warehouse_analysis_answer(df, warehouse_cols[0], cost_cols[0] if cost_cols else None)
    
    # General analysis with object identification
    return generate_general_analysis_answer(df, warehouse_cols, user_cols, cost_cols)

def generate_cost_analysis_answer(df: pd.DataFrame, warehouse_col: str, cost_col: str) -> str:
    """Generate detailed cost analysis with specific warehouse names"""
    if df.empty:
        return "No cost data found."
    
    # Get top 3 warehouses by cost
    top_warehouses = df.nlargest(3, cost_col)
    
    answers = []
    for idx, row in top_warehouses.iterrows():
        warehouse_name = row[warehouse_col]
        cost_val = row[cost_col]
        
        if isinstance(cost_val, (int, float)):
            dollars = cost_val * CONFIG['credit_to_dollar_rate']
            answers.append(f"{warehouse_name}: {cost_val:.2f} credits (${dollars:.2f})")
        else:
            answers.append(f"{warehouse_name}: {cost_val}")
    
    if len(answers) == 1:
        return f"The {answers[0]}."
    elif len(answers) == 2:
        return f"Top warehouses by cost: {answers[0]} and {answers[1]}."
    else:
        return f"Top warehouses by cost: {answers[0]}, {answers[1]}, and {answers[2]}."

def generate_user_activity_answer(df: pd.DataFrame, user_col: str, query_col: str = None) -> str:
    """Generate detailed user activity analysis with specific user names"""
    if df.empty:
        return "No user activity data found."
    
    # Get top 3 users
    if query_col and query_col in df.columns:
        # Sort by query count if available
        top_users = df.nlargest(3, query_col)
    else:
        # Just take first 3 users
        top_users = df.head(3)
    
    answers = []
    for idx, row in top_users.iterrows():
        user_name = row[user_col]
        if query_col and query_col in row:
            query_count = row[query_col]
            answers.append(f"{user_name}: {query_count} queries")
        else:
            answers.append(user_name)
    
    if len(answers) == 1:
        return f"Top user: {answers[0]}."
    elif len(answers) == 2:
        return f"Top users: {answers[0]} and {answers[1]}."
    else:
        return f"Top users: {answers[0]}, {answers[1]}, and {answers[2]}."

def generate_performance_answer(df: pd.DataFrame, warehouse_col: str, time_col: str) -> str:
    """Generate detailed performance analysis with specific warehouse names"""
    if df.empty:
        return "No performance data found."
    
    # Get top 3 warehouses by execution time (assuming higher is slower)
    top_warehouses = df.nlargest(3, time_col)
    
    answers = []
    for idx, row in top_warehouses.iterrows():
        warehouse_name = row[warehouse_col]
        time_val = row[time_col]
        
        if isinstance(time_val, (int, float)):
            formatted_time = format_duration(time_val)
            answers.append(f"{warehouse_name}: {formatted_time}")
        else:
            answers.append(f"{warehouse_name}: {time_val}")
    
    if len(answers) == 1:
        return f"Slowest warehouse: {answers[0]}."
    elif len(answers) == 2:
        return f"Slowest warehouses: {answers[0]} and {answers[1]}."
    else:
        return f"Slowest warehouses: {answers[0]}, {answers[1]}, and {answers[2]}."

def generate_warehouse_analysis_answer(df: pd.DataFrame, warehouse_col: str, cost_col: str = None) -> str:
    """Generate detailed warehouse analysis with specific warehouse names"""
    if df.empty:
        return "No warehouse data found."
    
    warehouses = df[warehouse_col].unique()
    
    if cost_col and cost_col in df.columns:
        # Include cost information if available
        total_cost = df[cost_col].sum()
        if isinstance(total_cost, (int, float)):
            dollars = total_cost * CONFIG['credit_to_dollar_rate']
            return f"Active warehouses: {', '.join(warehouses[:3])}. Total usage: {total_cost:.2f} credits (${dollars:.2f})."
        else:
            return f"Active warehouses: {', '.join(warehouses[:3])}."
    else:
        return f"Active warehouses: {', '.join(warehouses[:3])}."

def generate_general_analysis_answer(df: pd.DataFrame, warehouse_cols: list, user_cols: list, cost_cols: list) -> str:
    """Generate general analysis with object identification"""
    if df.empty:
        return "No data found."
    
    # Identify key objects in the data
    objects = []
    
    if warehouse_cols:
        warehouses = df[warehouse_cols[0]].unique()
        if len(warehouses) <= 3:
            objects.append(f"warehouses: {', '.join(warehouses)}")
        else:
            objects.append(f"warehouses: {', '.join(warehouses[:2])} and {len(warehouses)-2} others")
    
    if user_cols:
        users = df[user_cols[0]].unique()
        if len(users) <= 3:
            objects.append(f"users: {', '.join(users)}")
        else:
            objects.append(f"users: {', '.join(users[:2])} and {len(users)-2} others")
    
    if cost_cols:
        total_cost = df[cost_cols[0]].sum()
        if isinstance(total_cost, (int, float)):
            dollars = total_cost * CONFIG['credit_to_dollar_rate']
            objects.append(f"total: {total_cost:.2f} credits (${dollars:.2f})")
    
    if objects:
        return f"Found {len(df)} records with {', '.join(objects)}."
    else:
        return f"Found {len(df)} records."

def create_enhanced_data_summary(df: pd.DataFrame, user_query: str) -> str:
    """Create enhanced data summary with context for better AI responses"""
    if df.empty:
        return "No data"
    
    # Identify query type for better context
    query_lower = user_query.lower()
    is_cost_query = any(term in query_lower for term in ['cost', 'spend', 'billing', 'usage', 'credit'])
    is_user_query = any(term in query_lower for term in ['user', 'who', 'person', 'account'])
    is_performance_query = any(term in query_lower for term in ['slow', 'performance', 'time', 'execution'])
    is_warehouse_query = any(term in query_lower for term in ['warehouse', 'compute', 'resource'])
    
    summary = [f"Query Type: {'Cost' if is_cost_query else 'User' if is_user_query else 'Performance' if is_performance_query else 'Warehouse' if is_warehouse_query else 'General'}"]
    summary.append(f"Columns: {', '.join(df.columns)}")
    summary.append(f"Total Rows: {len(df)}")
    
    # Add detailed row information with context (limit to 3 rows for conciseness)
    for idx, row in df.head(3).iterrows():
        row_data = []
        for col in df.columns:
            if col in row and pd.notna(row[col]):
                value = row[col]
                # Format values based on column type
                if 'cost' in col.lower() or 'credit' in col.lower():
                    if isinstance(value, (int, float)):
                        dollars = value * CONFIG['credit_to_dollar_rate']
                        row_data.append(f"{col}: {value:.2f} credits (${dollars:.2f})")
                    else:
                        row_data.append(f"{col}: {value}")
                elif 'time' in col.lower() or 'duration' in col.lower():
                    if isinstance(value, (int, float)):
                        row_data.append(f"{col}: {format_duration(value)}")
                    else:
                        row_data.append(f"{col}: {value}")
                else:
                    row_data.append(f"{col}: {value}")
        if row_data:
            summary.append(f"Row {idx + 1}: {', '.join(row_data)}")
    
    # Add insights based on data
    if len(df) > 1:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            top_col = numeric_cols[0]
            if 'cost' in top_col.lower() or 'credit' in top_col.lower():
                max_val = df[top_col].max()
                min_val = df[top_col].min()
                avg_val = df[top_col].mean()
                summary.append(f"Insights: Max {top_col}: {max_val:.2f} credits (${max_val * CONFIG['credit_to_dollar_rate']:.2f}), Min: {min_val:.2f} credits (${min_val * CONFIG['credit_to_dollar_rate']:.2f}), Avg: {avg_val:.2f} credits (${avg_val * CONFIG['credit_to_dollar_rate']:.2f})")
            else:
                max_val = df[top_col].max()
                min_val = df[top_col].min()
                avg_val = df[top_col].mean()
                summary.append(f"Insights: Max {top_col}: {max_val}, Min: {min_val}, Avg: {avg_val:.2f}")
    
    return " | ".join(summary)

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

def generate_enhanced_fallback_answer(df: pd.DataFrame, user_query: str) -> str:
    """Generate enhanced rule-based fallback answer with detailed context and object identification"""
    if df.empty:
        return "No data found for your query."
    
    # Identify column types for better analysis
    cost_cols = [col for col in df.columns if any(term in col.lower() for term in ['cost', 'credit', 'price', 'spend'])]
    warehouse_cols = [col for col in df.columns if 'warehouse' in col.lower()]
    user_cols = [col for col in df.columns if 'user' in col.lower()]
    time_cols = [col for col in df.columns if any(term in col.lower() for term in ['time', 'duration', 'execution'])]
    query_cols = [col for col in df.columns if 'query' in col.lower()]
    
    # Get top 3 rows for better context
    top_rows = df.head(3)
    
    # Generate detailed answer based on query type and data
    query_lower = user_query.lower()
    
    if cost_cols and warehouse_cols:
        # Cost analysis with specific warehouse names
        warehouse_col = warehouse_cols[0]
        cost_col = cost_cols[0]
        
        if len(top_rows) > 1:
            # Multiple warehouses with specific names
            answers = []
            for idx, row in top_rows.iterrows():
                warehouse = row[warehouse_col]
                cost_val = row[cost_col]
                if isinstance(cost_val, (int, float)):
                    dollars = cost_val * CONFIG['credit_to_dollar_rate']
                    answers.append(f"{warehouse}: {cost_val:.2f} credits (${dollars:.2f})")
                else:
                    answers.append(f"{warehouse}: {cost_val}")
            
            if len(answers) > 1:
                return f"Top warehouses by cost: {', '.join(answers[:2])}"  # Show only top 2
            else:
                return f"{answers[0]}"
        else:
            # Single warehouse with specific name
            warehouse = top_rows.iloc[0][warehouse_col]
            cost_val = top_rows.iloc[0][cost_col]
            if isinstance(cost_val, (int, float)):
                dollars = cost_val * CONFIG['credit_to_dollar_rate']
                return f"{warehouse} warehouse has {cost_val:.2f} credits (${dollars:.2f})"
            return f"{warehouse} warehouse has {cost_val}"
    
    elif user_cols and query_cols:
        # User activity analysis with specific user names
        user_col = user_cols[0]
        query_col = query_cols[0]
        
        if len(top_rows) > 1:
            answers = []
            for idx, row in top_rows.iterrows():
                user = row[user_col]
                queries = row[query_col]
                answers.append(f"{user}: {queries} queries")
            
            return f"Top users by query count: {', '.join(answers[:2])}"  # Show only top 2
        else:
            user = top_rows.iloc[0][user_col]
            queries = top_rows.iloc[0][query_col]
            return f"Top user {user} executed {queries} queries"
    
    elif time_cols and warehouse_cols:
        # Performance analysis with specific warehouse names
        warehouse_col = warehouse_cols[0]
        time_col = time_cols[0]
        
        if len(top_rows) > 1:
            answers = []
            for idx, row in top_rows.iterrows():
                warehouse = row[warehouse_col]
                time_val = row[time_col]
                if isinstance(time_val, (int, float)):
                    answers.append(f"{warehouse}: {format_duration(time_val)}")
                else:
                    answers.append(f"{warehouse}: {time_val}")
            
            return f"Warehouse performance: {', '.join(answers[:2])}"  # Show only top 2
        else:
            warehouse = top_rows.iloc[0][warehouse_col]
            time_val = top_rows.iloc[0][time_col]
            if isinstance(time_val, (int, float)):
                return f"{warehouse} warehouse has {format_duration(time_val)} average execution time"
            return f"{warehouse} warehouse has {time_val}"
    
    elif user_cols:
        # User-focused query with specific user names
        user_col = user_cols[0]
        if len(top_rows) > 1:
            users = [row[user_col] for _, row in top_rows.iterrows()]
            return f"Top users: {', '.join(users[:2])}"  # Show only top 2
        else:
            return f"Top user: {top_rows.iloc[0][user_col]}"
    
    elif warehouse_cols:
        # Warehouse-focused query with specific warehouse names
        warehouse_col = warehouse_cols[0]
        if len(top_rows) > 1:
            warehouses = [row[warehouse_col] for _, row in top_rows.iterrows()]
            return f"Active warehouses: {', '.join(warehouses[:2])}"  # Show only top 2
        else:
            return f"Active warehouse: {top_rows.iloc[0][warehouse_col]}"
    
    # Default response with more context and object identification
    if len(df) > 1:
        # Try to identify key objects in the data
        objects = []
        for col in df.columns[:2]:  # Look at first 2 columns
            if col in top_rows.iloc[0] and pd.notna(top_rows.iloc[0][col]):
                value = top_rows.iloc[0][col]
                objects.append(f"{col}={value}")
        
        if objects:
            return f"Found {len(df)} results. Top record: {', '.join(objects)}"
        else:
            return f"Found {len(df)} results with data in columns: {', '.join(df.columns[:3])}"
    else:
        # Single result with object identification
        objects = []
        for col in df.columns[:2]:  # Look at first 2 columns
            if col in df.iloc[0] and pd.notna(df.iloc[0][col]):
                value = df.iloc[0][col]
                objects.append(f"{col}={value}")
        
        if objects:
            return f"Found {len(df)} result: {', '.join(objects)}"
        else:
            return f"Found {len(df)} result with data in columns: {', '.join(df.columns[:3])}"

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
    """Comprehensive Snowflake monitoring dashboard"""
    st.markdown('<h1 class="main-header">📊 Snowflake Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Get session
    session = get_snowflake_session()
    if not session:
        st.error("❌ Unable to connect to Snowflake")
        return
    
    # Get all available semantic views
    semantic_views = get_available_semantic_views()
    
    # Dashboard configuration
    st.sidebar.header("📊 Dashboard Settings")
    
    # Time range selector
    time_range = st.sidebar.selectbox(
        "📅 Time Range",
        ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days"]
    )
    
    # Refresh data button
    if st.sidebar.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Overview KPI Section
    st.markdown("## 🎯 Key Performance Indicators")
    render_kpi_section(semantic_views, time_range)
    
    # Main dashboard sections
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏭 Warehouse Performance", 
        "💰 Cost Analysis", 
        "⚡ Query Performance", 
        "👥 User Activity", 
        "🔒 Security Monitoring"
    ])
    
    with tab1:
        render_warehouse_performance(semantic_views, time_range)
    
    with tab2:
        render_cost_analysis(semantic_views, time_range)
    
    with tab3:
        render_query_performance(semantic_views, time_range)
    
    with tab4:
        render_user_activity(semantic_views, time_range)
    
    with tab5:
        render_security_monitoring(semantic_views, time_range)

def query_semantic_view_data(semantic_view: str, dimensions: List[str] = None, metrics: List[str] = None, limit: int = 1000) -> Optional[pd.DataFrame]:
    """Query semantic view data with proper syntax based on scripts.sql definitions"""
    session = get_snowflake_session()
    if not session:
        return None
    
    # Define correct semantic view queries based on actual CLI testing results
    semantic_queries = {
        "cost_analysis_semantic": {
            "dimensions": ["costs.usage_date", "costs.warehouse_name", "costs.cost_category"],
            "metrics": ["costs.total_cost", "costs.avg_daily_cost", "costs.compute_vs_cloud_ratio", "costs.high_cost_days"]
        },
        "resource_utilization_semantic": {
            "dimensions": ["resources.warehouse_name", "resources.usage_date", "resources.usage_hour"],
            "metrics": ["resources.total_credits_used", "resources.avg_credits_per_hour", "resources.compute_credits", "resources.cloud_credits"]
        },
        "query_performance_semantic": {
            "dimensions": ["queries.query_type", "queries.warehouse_name", "queries.warehouse_size", "queries.user_name", "queries.usage_date"],
            "metrics": ["queries.total_queries", "queries.avg_execution_time", "queries.slow_queries", "queries.total_data_scanned", "queries.avg_queue_time"]
        },
        "user_activity_semantic": {
            "dimensions": ["users.user_name"],
            "metrics": ["users.total_user_queries", "users.avg_user_execution_time", "users.slow_query_count", "users.data_scan_volume"]
        },
        "user_activity_queries_semantic": {
            "dimensions": ["user_queries.query_type", "user_queries.warehouse_name"],
            "metrics": []
        },
        "security_monitoring_semantic": {
            "dimensions": ["security_users.user_name"],
            "metrics": ["security_users.total_user_activity", "security_users.avg_user_execution_time", "security_users.user_data_access", "security_users.suspicious_activity", "security_users.long_running_queries"]
        }
    }
    
    try:
        # Get predefined dimensions and metrics for this semantic view
        view_config = semantic_queries.get(semantic_view, {})
        
        # Use provided dimensions/metrics or defaults
        final_dimensions = dimensions if dimensions else view_config.get("dimensions", [])[:3]
        final_metrics = metrics if metrics else view_config.get("metrics", [])[:3]
        
        # Build the query with correct syntax
        query_parts = [f"SELECT * FROM SEMANTIC_VIEW({CONFIG['semantic_schema']}.{semantic_view}"]
        
        if final_dimensions:
            query_parts.append(f"DIMENSIONS {', '.join(final_dimensions)}")
        
        if final_metrics:
            query_parts.append(f"METRICS {', '.join(final_metrics)}")
        
        query_parts.append(f") LIMIT {limit}")
        
        query = " ".join(query_parts)
        
        result = session.sql(query).collect()
        return pd.DataFrame([row.as_dict() for row in result]) if result else pd.DataFrame()
        
    except Exception as e:
        st.warning(f"Failed to query {semantic_view}: {e}")
        return None

def render_kpi_section(semantic_views: List[str], time_range: str):
    """Render the main KPI overview section with correct semantic view queries"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Total Credits from cost_analysis_semantic
    with col1:
        cost_data = query_semantic_view_data("cost_analysis_semantic", metrics=["costs.total_cost"])
        total_credits = 0
        
        if cost_data is not None and not cost_data.empty:
            # Get the numeric column (should be the last column since metrics come after dimensions)
            numeric_cols = cost_data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                total_credits = float(cost_data[numeric_cols[0]].sum())
            else:
                # If no numeric columns found, try the last column
                last_col = cost_data.columns[-1]
                try:
                    total_credits = float(cost_data[last_col].sum())
                except:
                    total_credits = 0
            
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_credits:,.1f}</div>
            <div class="metric-label">Total Credits</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Total Queries from query_performance_semantic
    with col2:
        query_data = query_semantic_view_data("query_performance_semantic", metrics=["queries.total_queries"])
        total_queries = 0
        
        if query_data is not None and not query_data.empty:
            # Get the numeric column
            numeric_cols = query_data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                total_queries = float(query_data[numeric_cols[0]].sum())
            else:
                # If no numeric columns found, try the last column
                last_col = query_data.columns[-1]
                try:
                    total_queries = float(query_data[last_col].sum())
                except:
                    total_queries = 0
            
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_queries:,.0f}</div>
            <div class="metric-label">Total Queries</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Active Warehouses from resource_utilization_semantic
    with col3:
        warehouse_data = query_semantic_view_data("resource_utilization_semantic", dimensions=["resources.warehouse_name"])
        if warehouse_data is not None and not warehouse_data.empty and len(warehouse_data.columns) > 0 and len(warehouse_data) > 0:
            active_warehouses = warehouse_data.iloc[:, 0].nunique()
        else:
            active_warehouses = 0
            
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{active_warehouses}</div>
            <div class="metric-label">Active Warehouses</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Estimated Cost
    with col4:
        estimated_cost = total_credits * CONFIG['credit_to_dollar_rate']
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${estimated_cost:,.2f}</div>
            <div class="metric-label">Estimated Cost</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Avg Query Time from query_performance_semantic
    with col5:
        perf_data = query_semantic_view_data("query_performance_semantic", metrics=["queries.avg_execution_time"])
        avg_time = 0
        
        if perf_data is not None and not perf_data.empty:
            # Get the numeric column
            numeric_cols = perf_data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                avg_time = float(perf_data[numeric_cols[0]].mean())
            else:
                # If no numeric columns found, try the last column
                last_col = perf_data.columns[-1]
                try:
                    avg_time = float(perf_data[last_col].mean())
                except:
                    avg_time = 0
        
        avg_time_formatted = format_duration(avg_time / 1000) if avg_time > 0 else "0s"
            
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{avg_time_formatted}</div>
            <div class="metric-label">Avg Query Time</div>
        </div>
        """, unsafe_allow_html=True)

def render_warehouse_performance(semantic_views: List[str], time_range: str):
    """Render warehouse performance section with proper semantic view queries"""
    st.markdown("### 🏭 Warehouse Performance Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("💰 Credit Usage by Warehouse")
        
        data = query_semantic_view_data(
            "resource_utilization_semantic",
            dimensions=["resources.warehouse_name"],
            metrics=["resources.total_credits_used"]
        )
        
        if data is not None and not data.empty and len(data.columns) >= 2 and len(data) > 0:
            # Create pie chart with proper column handling
            try:
                warehouse_col = data.columns[0]  # First column (warehouse name)
                credits_col = data.columns[1]    # Second column (credits)
                
                fig = px.pie(
                    data, 
                    values=credits_col,
                    names=warehouse_col,
                    title="Credits by Warehouse",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create chart: {e}")
                st.dataframe(data, use_container_width=True)
        else:
            st.info("No warehouse performance data available")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("⚡ Total Credits by Warehouse")
        
        data = query_semantic_view_data(
            "resource_utilization_semantic",
            dimensions=["resources.warehouse_name"],
            metrics=["resources.total_credits_used"]
        )
        
        if data is not None and not data.empty and len(data.columns) >= 2 and len(data) > 0:
            # Create bar chart with proper column handling
            try:
                warehouse_col = data.columns[0]  # First column (warehouse name)
                efficiency_col = data.columns[1]  # Second column (efficiency)
                
                fig = px.bar(
                    data,
                    x=warehouse_col,
                    y=efficiency_col,
                    title="Total Credits by Warehouse",
                    color_discrete_sequence=["#00d4ff"]
                )
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create chart: {e}")
                st.dataframe(data, use_container_width=True)
        else:
            st.info("No utilization data available")
        st.markdown('</div>', unsafe_allow_html=True)

def render_cost_analysis(semantic_views: List[str], time_range: str):
    """Render cost analysis section"""
    st.markdown("### 💰 Cost Analysis & Trends")
    
    # Find cost analysis semantic view
    cost_semantic = next((view for view in semantic_views if "cost_analysis" in view.lower()), None)
    
    if not cost_semantic:
        st.warning("Cost analysis semantic view not found")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📈 Cost Trend Over Time")
        
        data = query_semantic_view_data(
            cost_semantic,
            dimensions=["costs.usage_date", "costs.warehouse_name"],
            metrics=["costs.total_cost"]
        )
        
        if data is not None and not data.empty and len(data) > 0:
            # Create line chart
            try:
                date_col = None
                for col in data.columns:
                    if 'date' in col.lower():
                        date_col = col
                        break
                
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                if date_col and len(numeric_cols) > 0:
                    fig = px.line(
                        data,
                        x=date_col,
                        y=numeric_cols[0],
                        color='WAREHOUSE_NAME' if 'WAREHOUSE_NAME' in data.columns else None,
                        title="Daily Credit Consumption",
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(data, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create chart: {e}")
                st.dataframe(data, use_container_width=True)
        else:
            st.info("No cost trend data available")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🏷️ Cost Categories")
        
        data = query_semantic_view_data(
            cost_semantic,
            dimensions=["costs.cost_category"],
            metrics=["costs.total_cost"]
        )
        
        if data is not None and not data.empty and len(data) > 0:
            # Create donut chart
            try:
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                object_cols = data.select_dtypes(include=[object]).columns
                
                if len(numeric_cols) > 0 and len(object_cols) > 0:
                    fig = px.pie(
                        data,
                        values=numeric_cols[0],
                        names=object_cols[0],
                        title="Cost Distribution by Category",
                        hole=0.4,
                        color_discrete_sequence=["#ff6b6b", "#feca57", "#48dbfb"]
                    )
                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(data, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create chart: {e}")
                st.dataframe(data, use_container_width=True)
        else:
            st.info("No cost category data available")
        st.markdown('</div>', unsafe_allow_html=True)

def render_query_performance(semantic_views: List[str], time_range: str):
    """Render query performance section"""
    st.markdown("### ⚡ Query Performance Metrics")
    
    # Find query performance semantic view
    query_semantic = next((view for view in semantic_views if "query_performance" in view.lower()), None)
    
    if not query_semantic:
        st.warning("Query performance semantic view not found")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🐌 Query Performance Distribution")
        
        data = query_semantic_view_data(
            query_semantic,
            dimensions=["queries.query_type"],
            metrics=["queries.avg_execution_time", "queries.total_queries"]
        )
        
        if data is not None and not data.empty and len(data) > 0:
            # Create scatter plot
            try:
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                cat_cols = data.select_dtypes(include=[object]).columns
                
                if len(numeric_cols) >= 2 and len(cat_cols) >= 1:
                    fig = px.scatter(
                        data,
                        x=numeric_cols[1],
                        y=numeric_cols[0],
                        color=cat_cols[0],
                        title="Query Performance by Type",
                        size_max=20,
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(data, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create chart: {e}")
                st.dataframe(data, use_container_width=True)
        else:
            st.info("No query performance data available")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🎯 Slow Query Analysis")
        
        data = query_semantic_view_data(
            query_semantic,
            dimensions=["queries.warehouse_name"],
            metrics=["queries.slow_queries", "queries.total_queries"]
        )
        
        if data is not None and not data.empty and len(data) > 0:
            # Create bar chart
            try:
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                object_cols = data.select_dtypes(include=[object]).columns
                
                x_col = object_cols[0] if len(object_cols) > 0 else data.columns[0]
                y_col = numeric_cols[0] if len(numeric_cols) > 0 else data.columns[-1]
                
                fig = px.bar(
                    data,
                    x=x_col,
                    y=y_col,
                    title="Slow Queries by Warehouse",
                    color_discrete_sequence=["#ff6b6b"]
                )
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create chart: {e}")
                st.dataframe(data, use_container_width=True)
        else:
            st.info("No slow query data available")
        st.markdown('</div>', unsafe_allow_html=True)

def render_user_activity(semantic_views: List[str], time_range: str):
    """Render user activity section"""
    st.markdown("### 👥 User Activity Overview")
    
    # Find user activity semantic view
    user_semantic = next((view for view in semantic_views if "user_activity" in view.lower()), None)
    
    if not user_semantic:
        st.warning("User activity semantic view not found")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("👤 Top Active Users")
        
        data = query_semantic_view_data(
            user_semantic,
            dimensions=["users.user_name"],
            metrics=["users.total_user_queries"]
        )
        
        if data is not None and not data.empty and len(data) > 0:
            # Create horizontal bar chart
            try:
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                object_cols = data.select_dtypes(include=[object]).columns
                
                y_col = object_cols[0] if len(object_cols) > 0 else data.columns[0]
                x_col = numeric_cols[0] if len(numeric_cols) > 0 else data.columns[-1]
                
                fig = px.bar(
                    data.head(10),
                    y=y_col,
                    x=x_col,
                    title="Most Active Users",
                    orientation='h',
                    color_discrete_sequence=["#48dbfb"]
                )
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create chart: {e}")
                st.dataframe(data, use_container_width=True)
        else:
            st.info("No user activity data available")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("📊 Top Users by Query Count")
        
        # For user activity, we need to query users table separately from user_queries table
        # due to granularity constraints
        data = query_semantic_view_data(
            user_semantic,
            dimensions=["users.user_name"],
            metrics=["users.total_user_queries"]
        )
        
        if data is not None and not data.empty and len(data) > 0:
            # Create simple bar chart for user activity (no query types due to granularity constraints)
            try:
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                object_cols = data.select_dtypes(include=[object]).columns
                
                y_col = object_cols[0] if len(object_cols) > 0 else data.columns[0]
                x_col = numeric_cols[0] if len(numeric_cols) > 0 else data.columns[-1]
                
                fig = px.bar(
                    data.head(10),
                    y=y_col,
                    x=x_col,
                    title="Top Users by Query Count",
                    orientation='h',
                    color_discrete_sequence=["#48dbfb"]
                )
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create chart: {e}")
                st.dataframe(data, use_container_width=True)
        else:
            st.info("No user query type data available")
        st.markdown('</div>', unsafe_allow_html=True)

def render_security_monitoring(semantic_views: List[str], time_range: str):
    """Render security monitoring section"""
    st.markdown("### 🔒 Security & Access Monitoring")
    
    # Find security monitoring semantic view
    security_semantic = next((view for view in semantic_views if "security_monitoring" in view.lower()), None)
    
    if not security_semantic:
        st.warning("Security monitoring semantic view not found")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("⚠️ Suspicious Activity Detection")
        
        data = query_semantic_view_data(
            security_semantic,
            dimensions=["security_users.user_name"],
            metrics=["security_users.suspicious_activity", "security_users.total_user_activity"]
        )
        
        if data is not None and not data.empty and len(data) > 0:
            # Create bubble chart
            try:
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                cat_cols = data.select_dtypes(include=[object]).columns
                
                if len(numeric_cols) >= 2 and len(cat_cols) >= 1:
                    fig = px.scatter(
                        data,
                        x=numeric_cols[1],
                        y=numeric_cols[0],
                        size=numeric_cols[0],
                        hover_name=cat_cols[0],
                        title="Data Access vs Suspicious Activity",
                        color_discrete_sequence=["#ff6b6b"]
                    )
                    fig.update_layout(
                        template="plotly_dark",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.dataframe(data, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create chart: {e}")
                st.dataframe(data, use_container_width=True)
        else:
            st.info("No security data available")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.subheader("🐌 Long-Running Queries")
        
        data = query_semantic_view_data(
            security_semantic,
            dimensions=["security_users.user_name"],
            metrics=["security_users.long_running_queries", "security_users.avg_user_execution_time"]
        )
        
        if data is not None and not data.empty and len(data) > 0:
            # Create bar chart
            try:
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                object_cols = data.select_dtypes(include=[object]).columns
                
                x_col = object_cols[0] if len(object_cols) > 0 else data.columns[0]
                y_col = numeric_cols[0] if len(numeric_cols) > 0 else data.columns[-1]
                
                fig = px.bar(
                    data.head(10),
                    x=x_col,
                    y=y_col,
                    title="Long-Running Queries by User",
                    color_discrete_sequence=["#feca57"]
                )
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)"
                )
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create chart: {e}")
                st.dataframe(data, use_container_width=True)
        else:
            st.info("No long-running query data available")
        st.markdown('</div>', unsafe_allow_html=True)

@st.cache_data
def get_suggested_queries() -> List[str]:
    """Get enhanced suggested queries for better AI responses with object identification"""
    return [
        "Which warehouses cost the most this week and what are their specific credit usage?",
        "Who are our most active users and how many queries did each user execute?",
        "Show me slow queries by warehouse with specific execution times and warehouse names",
        "What's our peak usage time and which specific warehouses are busiest during those hours?",
        "Identify warehouses with unusual usage patterns and their specific credit consumption",
        "Show me user activity patterns by warehouse name and query type with execution counts",
        "Which users have the longest running queries and what are their specific execution times?",
        "What's the cost trend for each warehouse over time with specific credit amounts?",
        "Show me security events and suspicious activity by user name and warehouse",
        "Which warehouses are underutilized vs overutilized with their specific credit usage?",
        "List all warehouses and their total credit consumption with dollar amounts",
        "Show me the top 5 users by query count with their specific warehouse usage",
        "Which warehouses have the highest average execution time and what are those times?",
        "Display cost analysis by warehouse name with credits and dollar conversion",
        "Show me user activity by warehouse with specific query counts and execution times"
    ]

def try_create_sample_semantic_view():
    """Try to create a simple semantic view for testing if none exist"""
    session = get_snowflake_session()
    if not session:
        return False
    
    try:
        # First ensure the schema exists
        schema_parts = CONFIG['semantic_schema'].split('.')
        if len(schema_parts) == 2:
            try:
                session.sql(f"CREATE SCHEMA IF NOT EXISTS {CONFIG['semantic_schema']}").collect()
            except Exception:
                pass  # Schema might already exist
        
        # Try to create a simple semantic view from account usage
        # Using correct column names: CREDITS_USED (not TOTAL_CREDITS)
        sample_view_sql = f"""
        CREATE OR REPLACE SEMANTIC VIEW {CONFIG['semantic_schema']}.sample_warehouse_usage
        TABLES (
            warehouse_usage AS SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY PRIMARY KEY (START_TIME, WAREHOUSE_ID)
        )
        DIMENSIONS (
            warehouse_usage.WAREHOUSE_NAME AS warehouse_name,
            warehouse_usage.START_TIME AS usage_date
        )
        METRICS (
            warehouse_usage.CREDITS_USED AS credits_used
        )
        """
        session.sql(sample_view_sql).collect()
        st.success("✅ Created sample semantic view: sample_warehouse_usage")
        
        # Clear the cache so it picks up the new view
        get_available_semantic_views.clear()
        
        return True
    except Exception as e:
        st.error(f"Could not create sample semantic view: {e}")
        st.info("This might be due to permissions or the ACCOUNT_USAGE schema not being accessible.")
        
        # Try an even simpler approach with a basic query
        try:
            simple_view_sql = f"""
            CREATE OR REPLACE SEMANTIC VIEW {CONFIG['semantic_schema']}.simple_test_view
            TABLES (
                test_data AS (
                    SELECT 'COMPUTE_WH' as WAREHOUSE_NAME, 10.5 as CREDITS_USED, CURRENT_DATE() as USAGE_DATE
                    UNION ALL
                    SELECT 'LOAD_WH' as WAREHOUSE_NAME, 5.2 as CREDITS_USED, CURRENT_DATE() as USAGE_DATE
                ) PRIMARY KEY (WAREHOUSE_NAME)
            )
            DIMENSIONS (
                test_data.WAREHOUSE_NAME AS warehouse_name,
                test_data.USAGE_DATE AS usage_date
            )
            METRICS (
                test_data.CREDITS_USED AS credits_used
            )
            """
            session.sql(simple_view_sql).collect()
            st.success("✅ Created simple test semantic view: simple_test_view")
            get_available_semantic_views.clear()
            return True
        except Exception as e2:
            st.error(f"Even simple semantic view creation failed: {e2}")
            return False

def render_sidebar_info():
    """Render sidebar information"""
    # Sidebar info removed as requested - keeping function for consistency

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
