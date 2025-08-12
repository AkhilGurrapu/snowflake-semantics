# Snowflake Semantic Analytics Documentation

## Overview

This documentation covers the Snowflake Semantic Analytics platform with **Cortex Analyst integration**, providing AI-powered natural language query capabilities for business intelligence.

## Architecture

### Previous Architecture (Keyword Matching)
```
User Query → Keyword Matching → Semantic View Selection → SQL Generation → Results
```

### Current Architecture (Cortex Analyst)
```
User Query → Cortex Analyst → Semantic View Selection → Semantic View Query → Enhanced Results
```

## Core Components

### 1. Cortex Analyst Integration

The application now uses Snowflake's Cortex Analyst REST API to:
- **Understand natural language queries** using AI
- **Automatically select the most appropriate semantic view**
- **Generate optimized SQL queries**
- **Provide AI-powered interpretations**

#### API Endpoint
- **URL**: `https://{account}.snowflakecomputing.com/api/v2/cortex/analyst/message`
- **Method**: POST
- **Authentication**: Bearer token (Programmatic Access Token)

#### Request Structure
```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What's the total cost of our Snowflake usage?"
        }
      ]
    }
  ],
  "semantic_models": [
    {"semantic_view": "DATABASE.SCHEMA.snowflake_monitoring_semantic"},
    {"semantic_view": "DATABASE.SCHEMA.cost_analysis_semantic"},
    {"semantic_view": "DATABASE.SCHEMA.query_performance_semantic"}
  ],
  "stream": false
}
```

#### Response Structure
```json
{
  "request_id": "75d343ee-699c-483f-83a1-e314609fb563",
  "message": {
    "role": "analyst",
    "content": [
      {
        "type": "text",
        "text": "I'll help you find the total cost of your Snowflake usage..."
      },
      {
        "type": "sql",
        "statement": "SELECT SUM(TOTAL_COST) FROM SEMANTIC_VIEW(...)",
        "confidence": {
          "verified_query_used": null
        }
      }
    ]
  }
}
```

### 2. Core Functions

#### `call_cortex_analyst_api(user_query, semantic_views)`
- Makes HTTP POST request to Cortex Analyst API
- Handles authentication and error management
- Returns structured response with AI interpretation and SQL

#### `extract_sql_from_cortex_response(cortex_response)`
- Parses Cortex Analyst response to extract generated SQL
- Handles different response formats
- Returns SQL statement for execution

#### `extract_text_from_cortex_response(cortex_response)`
- Extracts AI interpretation text from response
- Provides user-friendly explanation of what the AI understood

#### `execute_raw_sql_query(sql_query)`
- Executes the AI-generated SQL directly
- Returns pandas DataFrame with results
- Handles execution errors gracefully

### 3. Semantic Views

The application supports multiple semantic views:
- `snowflake_monitoring_semantic` - General monitoring
- `query_performance_semantic` - Performance analysis
- `cost_analysis_semantic` - Cost and billing
- `user_activity_semantic` - User behavior
- `resource_utilization_semantic` - Resource usage
- `security_monitoring_semantic` - Security and access

## User Experience

### 1. AI-Powered Query Understanding
- Users can ask questions in natural language
- No need to know technical details about semantic views
- AI automatically selects the best semantic view

### 2. Transparent Process
- Shows AI interpretation of the query
- Displays generated SQL for transparency
- Provides confidence information

### 3. Enhanced Results
- AI-generated insights from the data
- Automatic visualization selection
- Contextual answers based on query type

### 4. Suggested Questions
The application includes pre-built questions that work well with Cortex Analyst:
- "What's the total cost of our Snowflake usage?"
- "Which warehouses are consuming the most credits?"
- "Show me the average query execution time by warehouse"
- "Who are the most active users?"
- "What's the cost trend over the last month?"

## Configuration Requirements

### 1. Authentication
- Valid Snowflake Programmatic Access Token
- Token stored in `snowflake-pat.token` file
- Proper role permissions (SNOWFLAKE.CORTEX_USER)

### 2. Semantic Views
- All semantic views must be created and accessible
- Proper permissions on semantic views
- Valid database and schema configuration

### 3. Network Access
- HTTPS access to Snowflake REST API
- Proper firewall configuration
- Valid account URL format

## Error Handling

### 1. API Connection Errors
- Graceful fallback with user-friendly messages
- Connection status indicators
- Retry mechanisms for transient failures

### 2. SQL Generation Errors
- Clear error messages when AI can't generate SQL
- Suggestions for rephrasing queries
- Fallback to traditional semantic view queries

### 3. Execution Errors
- Detailed error reporting
- Suggestions for query modification
- Data validation and sanitization

## Benefits

### 1. Improved User Experience
- **Natural Language**: No technical knowledge required
- **Intelligent Selection**: AI chooses the best semantic view
- **Contextual Understanding**: AI understands business context

### 2. Enhanced Accuracy
- **AI-Powered**: Better understanding than keyword matching
- **Semantic Understanding**: Grasps intent, not just keywords
- **Multi-turn Conversations**: Supports follow-up questions

### 3. Better Insights
- **AI Interpretation**: Explains what the AI understood
- **Generated SQL**: Shows the actual query being executed
- **Enhanced Analytics**: AI-powered insights from results

### 4. Scalability
- **Multiple Views**: Supports all semantic views automatically
- **Extensible**: Easy to add new semantic views
- **Maintainable**: Centralized AI logic

## Testing and Validation

### 1. Test Queries
The following queries have been tested and work well:
- Cost analysis queries
- Performance monitoring queries
- User activity queries
- Resource utilization queries
- Security monitoring queries

### 2. Validation Process
1. **API Connection**: Verify Cortex Analyst API access
2. **Token Authentication**: Ensure proper authentication
3. **Semantic View Access**: Confirm all views are accessible
4. **Query Processing**: Test natural language understanding
5. **SQL Generation**: Validate generated SQL correctness
6. **Result Processing**: Verify data retrieval and visualization

## Future Enhancements

### 1. Streaming Responses
- Implement real-time streaming for long-running queries
- Show progress indicators during processing
- Provide incremental results

### 2. Multi-turn Conversations
- Support follow-up questions
- Maintain conversation context
- Enable complex analytical workflows

### 3. Advanced Analytics
- Integrate with Cortex Search for enhanced retrieval
- Add predictive analytics capabilities
- Implement anomaly detection

### 4. Custom Instructions
- Allow users to customize AI behavior
- Support domain-specific terminology
- Enable personalized query preferences

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify token is valid and not expired
   - Check role permissions (SNOWFLAKE.CORTEX_USER)
   - Ensure proper token format
   - **Important**: Use only `Authorization: Bearer {token}` header, do not include `X-Snowflake-Authorization-Token-Type: OAuth`

2. **Cortex Analyst API 401 Errors**
   - Grant the CORTEX_USER role: `GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE ACCOUNTADMIN;`
   - Ensure semantic views exist and are accessible
   - Verify the API endpoint is correct for your region

2. **API Connection Issues**
   - Verify network connectivity
   - Check account URL format
   - Confirm firewall settings

3. **Semantic View Errors**
   - Verify semantic views exist and are accessible
   - Check database and schema permissions
   - Validate semantic view definitions

4. **SQL Generation Failures**
   - Try rephrasing the query
   - Use more specific language
   - Check if the question is within scope of available data

### Debug Information

The application provides detailed debug information:
- API response codes and messages
- Generated SQL statements
- Error stack traces
- Connection status indicators

## Conclusion

The Cortex Analyst integration represents a significant improvement over the previous keyword-matching approach. It provides:

- **Better User Experience**: Natural language queries
- **Improved Accuracy**: AI-powered understanding
- **Enhanced Transparency**: Visible AI interpretation and SQL
- **Greater Flexibility**: Support for complex queries
- **Future-Proof Architecture**: Built for extensibility

This implementation successfully demonstrates how to leverage Snowflake's AI capabilities to create a more intelligent and user-friendly analytics interface.
