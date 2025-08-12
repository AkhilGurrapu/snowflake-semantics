# Snowflake Semantic Analytics - Complete Architecture & Implementation Guide

This is a sophisticated **AI-powered business intelligence dashboard** built with **Streamlit in Snowflake (SiS)** that leverages **Cortex Analyst** for natural language query processing. This document provides a comprehensive guide to the architecture, implementation, and end-to-end workflow.

## **App Overview and Purpose**

This application serves as an intelligent analytics interface that allows users to:
- Ask questions about Snowflake usage in plain English
- Get AI-generated SQL queries and insights
- View traditional dashboard metrics
- Analyze warehouse performance, costs, and user activity

## **Complete Architecture Overview**

### **High-Level Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   Cortex        │    │   Semantic      │    │   Physical      │
│   in Snowflake  │───▶│   Analyst       │───▶│   Views         │───▶│   Tables        │
│   (SiS)         │    │   AI Engine     │    │   (Business     │    │   (Raw Data)    │
└─────────────────┘    └─────────────────┘    │   Layer)        │    └─────────────────┘
```

### **Key Technologies and Dependencies**

#### **SiS-Specific Components**
- **Streamlit in Snowflake (SiS)**: Native Snowflake web interface framework
- **Snowpark Session**: `get_active_session()` for database connectivity
- **_snowflake Module**: Native SiS API calling capabilities
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive data visualizations

#### **AI Integration Stack**
- **Cortex Analyst REST API**: Snowflake's AI service powered by Claude-3.5-Sonnet
- **Semantic Views**: Pre-defined business logic layers in Snowflake
- **Natural Language Processing**: Intent recognition and SQL generation

## **Configuration and Styling**

### **Page Setup**
```python
st.set_page_config(
    page_title="Snowflake Semantic Analytics - AI-Powered Business Intelligence",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)
```

### **Custom CSS Styling**
The app includes extensive custom CSS for:
- **Dark theme interface** with modern, clean design
- **Concise answer display** with prominent metric highlighting
- **SQL dropdown** for collapsible technical details
- **Smart chart containers** with automatic visualization
- **Expanded data preview** with full table visibility
- **Status indicators** with clean badge styling
- **Responsive design** elements for all screen sizes

## **End-to-End Workflow - Step by Step**

### **Complete Request Flow When User Asks: "What's our total Snowflake usage?"**

#### **Step 1: User Input Processing**
```python
user_query = "What's our total Snowflake usage?"
semantic_views = get_available_semantic_views()  # Gets all 6 semantic views
```

#### **Step 2: SiS Session & Authentication Setup**
```python
# Native SiS session management
session = get_active_session()

# Extract account information for API calls  
account_info = session.sql("SELECT CURRENT_ACCOUNT() as account, CURRENT_REGION() as region").collect()
account_url = f"{account}.{region}.snowflakecomputing.com"

# Authentication inherits from SiS session context
token = get_cortex_analyst_token()  # Returns "sis_session_auth"
```

#### **Step 3: Cortex Analyst API Call (The Critical Part)**
```python
# Create request payload with all semantic views
request_body = {
    "messages": [{
        "role": "user",
        "content": [{"type": "text", "text": user_query}]
    }],
    "semantic_models": [
        {"semantic_view": "SNOWFLAKE_MONITORING.MONITORING_SEMANTIC.snowflake_monitoring_semantic"},
        {"semantic_view": "SNOWFLAKE_MONITORING.MONITORING_SEMANTIC.cost_analysis_semantic"},
        {"semantic_view": "SNOWFLAKE_MONITORING.MONITORING_SEMANTIC.query_performance_semantic"},
        {"semantic_view": "SNOWFLAKE_MONITORING.MONITORING_SEMANTIC.user_activity_semantic"},
        {"semantic_view": "SNOWFLAKE_MONITORING.MONITORING_SEMANTIC.resource_utilization_semantic"},
        {"semantic_view": "SNOWFLAKE_MONITORING.MONITORING_SEMANTIC.security_monitoring_semantic"}
    ]
}

# ✅ KEY SUCCESS: Use SiS native API calling method
import _snowflake
resp = _snowflake.send_snow_api_request(
    "POST", 
    "/api/v2/cortex/analyst/message",
    {}, {}, request_body, None, 30
)
```

#### **Step 4: AI Processing Inside Cortex Analyst**
```
1. Natural Language Understanding
   ├── Parses: "What's our total Snowflake usage?"
   ├── Identifies intent: Cost/usage analysis
   └── Maps to business concepts: warehouses, credits, usage

2. Semantic Model Selection (AI Decision)
   ├── Evaluates all 6 provided semantic views
   ├── Chooses: cost_analysis_semantic (best match for "usage")
   └── Loads business context and table relationships

3. SQL Generation (Claude-3.5-Sonnet AI Model)
   ├── Understands cost_analysis_base table structure
   ├── Generates optimized SQL with CTEs and aggregations
   └── Includes proper ordering: ORDER BY total_cost DESC
```

#### **Step 5: Response Processing & Parsing**
```python
# ✅ KEY SUCCESS: Proper response parsing for SiS format
if resp and resp.get('status') == 200:  # Note: 'status' not 'status_code' 
    import json
    content = resp.get('content', '{}')
    response_data = json.loads(content)  # Parse JSON string
    
    # Extract AI components
    ai_interpretation = extract_text_from_cortex_response(response_data)
    generated_sql = extract_sql_from_cortex_response(response_data)
```

#### **Step 6: SQL Execution & Results Display**
```python
# Execute AI-generated SQL using Snowpark
result = session.sql(generated_sql).collect()
df = pd.DataFrame([row.as_dict() for row in result])

# Create automatic visualization
fig = create_simple_visualization(df)

# Display in Streamlit interface
st.dataframe(df, use_container_width=True)
st.plotly_chart(fig, use_container_width=True)
```

## **Core Functions Breakdown**

### **1. SiS Session Management**
```python
@st.cache_resource
def get_snowflake_session():
    """Get active Snowflake session in SiS environment"""
    return get_active_session()
```
- Uses native SiS session management
- No external authentication needed
- Inherits user's Snowflake permissions

### **2. Cortex Analyst Integration (SiS Native)**
```python
def call_cortex_analyst_with_session_auth(user_query: str, semantic_views: List[str], account_url: str, session):
    """Call Cortex Analyst using SiS native capabilities"""
    import _snowflake
    
    resp = _snowflake.send_snow_api_request(
        "POST", "/api/v2/cortex/analyst/message",
        {}, {}, request_body, None, API_TIMEOUT
    )
```

**This is the breakthrough implementation that:**
- Uses SiS native `_snowflake.send_snow_api_request()` method
- Automatically handles authentication within Snowflake infrastructure
- Avoids external network calls and system functions with side effects
- Properly formats semantic view references for Cortex Analyst

### **4. Query Execution Functions**

**Semantic Queries:**
```python
def execute_semantic_query(dimensions: List[str], metrics: List[str], filters: Optional[str] = None):
    """Execute a semantic view query"""
```
- Builds and executes semantic view queries
- Uses Snowflake's `SEMANTIC_VIEW()` function
- Supports dimensions, metrics, and filters

**Raw SQL Execution:**
```python
def execute_raw_sql_query(sql_query: str) -> Optional[pd.DataFrame]:
    """Execute raw SQL query from Cortex Analyst"""
```
- Executes AI-generated SQL queries
- Returns results as pandas DataFrames
- Includes comprehensive error handling

### **5. Data Processing and Insights**

**AI-Powered Insights Generation:**
```python
def generate_insights(df: pd.DataFrame, query: str) -> List[str]:
    """Generate AI-powered insights from the data"""
```

**Automatically analyzes data to provide:**
- Cost alerts and optimization suggestions
- Performance bottleneck identification
- Usage pattern analysis
- Trend detection
- Security and anomaly insights

**Utility Functions:**
- `format_currency()`: Formats monetary values
- `format_duration()`: Converts seconds to human-readable time
- `create_visualization()`: Automatically creates appropriate charts

## **User Interfaces**

### **1. AI Chat Interface**
The main interface featuring:

**Sidebar Configuration:**
- Connection status indicators
- Pre-built query suggestions optimized for Cortex Analyst
- Available semantic views listing
- How-it-works explanation

**Chat Flow:**
1. **User Input**: Natural language questions
2. **AI Processing**: Cortex Analyst interprets the query
3. **SQL Generation**: Creates optimized SQL
4. **Execution**: Runs the query against Snowflake
5. **Results**: Displays data, insights, and visualizations
6. **Chat History**: Maintains conversation context

**Natural Language Queries:**

The app supports **any natural language question** about your Snowflake data, with convenient clickable suggestions!

**Quick Start - Click These Questions:**
- "What's our total Snowflake usage?"
- "Which warehouses cost the most?"
- "Show me slow queries"
- "Who are the most active users?"
- "Any suspicious activity?"

**Or Ask Anything Naturally:**
- "What's our peak usage time?"
- "How much data are we scanning?"
- "Which users have the longest running queries?"
- "Show me cost trends over time"
- "Which warehouses are underutilized?"

**The AI handles everything:**
- Query interpretation
- SQL generation
- Data analysis
- Insight generation
- Result presentation
- Automatic visualizations

### **2. Dashboard View**
Traditional BI dashboard featuring:

**Key Metrics Cards:**
- Total Credits consumed
- Total Queries executed
- Active Warehouses count
- Estimated Cost

**Interactive Visualizations:**
- Pie chart for warehouse usage distribution
- Scatter plot for warehouse activity correlation
- Time-series charts for trend analysis

## **Semantic Views Integration**

The app works with predefined semantic views:
- `snowflake_monitoring_semantic`
- `query_performance_semantic`
- `cost_analysis_semantic`
- `user_activity_semantic`
- `resource_utilization_semantic`
- `security_monitoring_semantic`

**Available Dimensions:**
- Warehouse Name, User Name, Query Type
- Warehouse Size, Usage Date/Hour

**Available Metrics:**
- Credits, Queries, Execution Times
- Data Scanned, Queue Times, Costs
- User Activity, Security Metrics

## **How the AI Magic Works**

### **Complete Workflow:**
1. **User Query**: "Which warehouses cost the most?"
2. **Cortex Analyst**: Interprets intent and identifies relevant semantic views
3. **SQL Generation**: Creates optimized query automatically
4. **Execution**: Runs against Snowflake semantic views
5. **AI Insights**: Analyzes results for patterns and anomalies
6. **Visualization**: Creates appropriate charts automatically
7. **Response**: Provides comprehensive answer with context

### **Key Advantages:**
- **No SQL Knowledge Required**: Users ask questions in plain English
- **Intelligent Context**: AI understands business intent
- **Automatic Optimization**: Generated queries are performance-optimized
- **Rich Insights**: Goes beyond raw data to provide actionable intelligence
- **Interactive Experience**: Conversational interface with memory

## **Security and Best Practices**

- **Token-based Authentication**: Uses separate token files
- **Configuration Management**: Centralized config with TOML
- **Error Handling**: Comprehensive exception management
- **Resource Caching**: Optimized performance with Streamlit caching
- **Input Validation**: Sanitized user inputs and API responses

## **Usage Scenarios**

This app is ideal for:
- **Business Analysts** exploring Snowflake usage patterns
- **Finance Teams** monitoring and optimizing costs
- **Data Engineers** identifying performance bottlenecks
- **Security Teams** detecting unusual activity
- **Executives** getting high-level insights without technical complexity

## **Critical Implementation Insights: Why It Failed Before vs. Why It Works Now**

### **❌ Previous Failed Approaches and Why They Failed**

#### **1. Direct CORTEX.ANALYST Function Call**
```python
# ❌ FAILED APPROACH
analyst_sql = f"""
SELECT SNOWFLAKE.CORTEX.ANALYST(
    PARSE_JSON('{json.dumps(conversation)}'),
    PARSE_JSON('{json.dumps(semantic_model_refs)}')
) as result
"""
```
**Failure Reasons:**
- `SNOWFLAKE.CORTEX.ANALYST()` function expects semantic model YAML files on stages
- Our setup uses semantic views, not semantic model files
- JSON escaping caused SQL syntax errors
- Function doesn't support semantic_view references directly

#### **2. SYSTEM$ Functions with Side Effects**
```python
# ❌ FAILED APPROACH  
api_sql = f"""
SELECT SYSTEM$REST(
    'POST', 'https://account.snowflakecomputing.com/api/v2/cortex/analyst/message',
    OBJECT_CONSTRUCT('Authorization', 'Bearer ' || SYSTEM$GET_SNOWFLAKE_PLATFORM_INFO():oauth_access_token),
    PARSE_JSON('{payload}')
) as api_response
"""
```
**Failure Reasons:**
- `SYSTEM$GET_SNOWFLAKE_PLATFORM_INFO()` has side effects
- SiS environment restricts functions with side effects for security
- Error: "Query called from a stored procedure contains a function with side effects"

#### **3. External HTTP Requests**
```python
# ❌ FAILED APPROACH
response = requests.post(
    url="https://account.snowflakecomputing.com/api/v2/cortex/analyst/message",
    headers=headers, 
    json=payload
)
```
**Failure Reasons:**
- SiS environment may restrict external network calls
- Authentication token extraction complexities
- Network boundary and security limitations

### **✅ Current Working Solution - The Breakthrough**

#### **Key Success Factors:**

**1. Native SiS API Method**
```python
# ✅ WORKS: Uses SiS built-in API calling capability
import _snowflake
resp = _snowflake.send_snow_api_request("POST", "/api/v2/cortex/analyst/message", ...)
```
- No external network calls - stays within Snowflake infrastructure
- Native authentication inheritance from SiS session
- No side effects - designed for SiS environment

**2. Proper Response Format Handling**
```python
# ✅ WORKS: Correct SiS response parsing
if resp.get('status') == 200:          # Not 'status_code'
    content = json.loads(resp.get('content'))  # Parse JSON string content
```
- SiS returns `status` not `status_code`
- Content comes as JSON string, not object

**3. Semantic Views Integration**
```python
# ✅ WORKS: Proper semantic view references
"semantic_models": [{"semantic_view": "DATABASE.SCHEMA.VIEW_NAME"}]
```
- Uses existing semantic views, not semantic model files
- Proper fully-qualified naming convention

**4. Authentication Inheritance**
```python
# ✅ WORKS: No manual token management needed
# Authentication context inherited from SiS session automatically
```

### **Technical Architecture Success Principles**

#### **SiS Ecosystem Understanding**
The breakthrough came from understanding that **SiS has its own ecosystem** with:

1. **Native API Methods**: `_snowflake.send_snow_api_request()` 
2. **Inherited Authentication**: Session context provides authentication
3. **Different Response Formats**: SiS-specific JSON response structure
4. **Security Boundaries**: No external calls or side-effect functions
5. **Semantic Views Support**: Direct integration without file uploads

#### **End Result: Production-Ready Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │    │   SiS Native    │    │   Cortex        │
│   "What's our   │───▶│   API Call      │───▶│   Analyst       │
│   usage?"       │    │   (_snowflake)  │    │   (Claude-3.5)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Visualized    │    │   Snowpark      │    │   Generated     │
│   Results       │◀───│   Execution     │◀───│   SQL Query     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

This creates a **truly native Snowflake experience** where:
- ✅ Authentication is seamless and secure
- ✅ API calls stay within Snowflake infrastructure  
- ✅ Performance is optimized for SiS environment
- ✅ Security boundaries are maintained
- ✅ Integration with semantic views is natural and efficient

The result is a **production-ready, enterprise-grade AI analytics interface** that leverages Snowflake's full ecosystem while providing an intuitive, conversational user experience for business intelligence and data analysis.

## **Implementation Summary**

The combination of Snowflake's semantic layers, Cortex Analyst's AI capabilities, native SiS infrastructure, and Streamlit's interactive interface creates a powerful, user-friendly analytics platform that democratizes data access across the organization while maintaining enterprise security and performance standards.