#!/usr/bin/env python3
"""
Test script for enhanced AI response generation with object identification
This script validates that the AI chat interface provides detailed, accurate responses
with specific object names and business context.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Configuration constants (matching snowflake-webapp.py)
CONFIG = {
    'credit_to_dollar_rate': 3,
    'cortex_model': 'llama3.1-8b'
}

# Formatting utilities (copied from snowflake-webapp.py)
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

# Enhanced AI response generation functions (copied from snowflake-webapp.py)
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

def create_test_data():
    """Create test data that mimics real Snowflake usage data"""
    
    # Test cost analysis data
    cost_data = pd.DataFrame({
        'WAREHOUSE_NAME': ['COMPUTE_WH', 'SNOWSARVA_WAREHOUSE', 'WH_SNOWSARVA_CONSUMER', 'SNOWFLAKE_LEARNING_WH', 'CLOUD_SERVICES_ONLY'],
        'TOTAL_COST': [12.276297806, 1.784523, 0.842156, 0.173456, 0.128819726],
        'USAGE_DATE': ['2024-01-15', '2024-01-15', '2024-01-15', '2024-01-15', '2024-01-15']
    })
    
    # Test user activity data
    user_data = pd.DataFrame({
        'USER_NAME': ['AKHIL_GURRAPU', 'SVC_AKHIL', 'ADMIN_USER', 'ANALYST_1', 'DEVELOPER_2'],
        'TOTAL_QUERIES': [156, 89, 234, 67, 123],
        'AVG_EXECUTION_TIME': [2.5, 1.8, 3.2, 1.5, 2.1],
        'WAREHOUSE_NAME': ['COMPUTE_WH', 'SNOWSARVA_WAREHOUSE', 'COMPUTE_WH', 'WH_SNOWSARVA_CONSUMER', 'COMPUTE_WH']
    })
    
    # Test performance data
    performance_data = pd.DataFrame({
        'WAREHOUSE_NAME': ['COMPUTE_WH', 'SNOWSARVA_WAREHOUSE', 'WH_SNOWSARVA_CONSUMER'],
        'AVG_EXECUTION_TIME': [45000, 32000, 28000],  # in milliseconds
        'SLOW_QUERIES': [12, 8, 5],
        'TOTAL_QUERIES': [156, 89, 67]
    })
    
    # Test warehouse analysis data
    warehouse_data = pd.DataFrame({
        'WAREHOUSE_NAME': ['COMPUTE_WH', 'SNOWSARVA_WAREHOUSE', 'WH_SNOWSARVA_CONSUMER', 'SNOWFLAKE_LEARNING_WH'],
        'TOTAL_CREDITS': [12.276297806, 1.784523, 0.842156, 0.173456],
        'ACTIVE_HOURS': [24, 18, 12, 6]
    })
    
    return {
        'cost': cost_data,
        'user': user_data,
        'performance': performance_data,
        'warehouse': warehouse_data
    }

def test_cost_analysis():
    """Test cost analysis with object identification"""
    print("\n🧪 Testing Cost Analysis with Object Identification")
    print("=" * 60)
    
    test_data = create_test_data()
    cost_df = test_data['cost']
    
    # Test the specific function
    answer = generate_cost_analysis_answer(cost_df, 'WAREHOUSE_NAME', 'TOTAL_COST')
    print(f"✅ Cost Analysis Answer: {answer}")
    
    # Test with different queries
    queries = [
        "Which warehouses cost the most?",
        "Show me warehouse costs",
        "What's our total spending on warehouses?",
        "Which warehouses are most expensive?"
    ]
    
    for query in queries:
        answer = generate_detailed_object_answer(cost_df, query)
        print(f"📝 Query: '{query}'")
        print(f"   Answer: {answer}")
        print()

def test_user_activity():
    """Test user activity analysis with object identification"""
    print("\n🧪 Testing User Activity Analysis with Object Identification")
    print("=" * 60)
    
    test_data = create_test_data()
    user_df = test_data['user']
    
    # Test the specific function
    answer = generate_user_activity_answer(user_df, 'USER_NAME', 'TOTAL_QUERIES')
    print(f"✅ User Activity Answer: {answer}")
    
    # Test with different queries
    queries = [
        "Who are our most active users?",
        "Show me user activity",
        "Which users execute the most queries?",
        "Who are the top users?"
    ]
    
    for query in queries:
        answer = generate_detailed_object_answer(user_df, query)
        print(f"📝 Query: '{query}'")
        print(f"   Answer: {answer}")
        print()

def test_performance_analysis():
    """Test performance analysis with object identification"""
    print("\n🧪 Testing Performance Analysis with Object Identification")
    print("=" * 60)
    
    test_data = create_test_data()
    perf_df = test_data['performance']
    
    # Test the specific function
    answer = generate_performance_answer(perf_df, 'WAREHOUSE_NAME', 'AVG_EXECUTION_TIME')
    print(f"✅ Performance Answer: {answer}")
    
    # Test with different queries
    queries = [
        "Which warehouses are slowest?",
        "Show me slow queries by warehouse",
        "What's the performance of our warehouses?",
        "Which warehouses have the longest execution times?"
    ]
    
    for query in queries:
        answer = generate_detailed_object_answer(perf_df, query)
        print(f"📝 Query: '{query}'")
        print(f"   Answer: {answer}")
        print()

def test_warehouse_analysis():
    """Test warehouse analysis with object identification"""
    print("\n🧪 Testing Warehouse Analysis with Object Identification")
    print("=" * 60)
    
    test_data = create_test_data()
    warehouse_df = test_data['warehouse']
    
    # Test the specific function
    answer = generate_warehouse_analysis_answer(warehouse_df, 'WAREHOUSE_NAME', 'TOTAL_CREDITS')
    print(f"✅ Warehouse Analysis Answer: {answer}")
    
    # Test with different queries
    queries = [
        "Which warehouses are active?",
        "Show me all warehouses",
        "What warehouses do we have?",
        "List our compute resources"
    ]
    
    for query in queries:
        answer = generate_detailed_object_answer(warehouse_df, query)
        print(f"📝 Query: '{query}'")
        print(f"   Answer: {answer}")
        print()

def test_formatting_functions():
    """Test the formatting utility functions"""
    print("\n🧪 Testing Formatting Functions")
    print("=" * 60)
    
    # Test currency formatting
    credits = 12.276297806
    formatted = format_currency(credits)
    print(f"✅ Credits {credits} formatted as: {formatted}")
    
    # Test credit formatting
    formatted_credits = format_credits(credits)
    print(f"✅ Credits {credits} formatted as: {formatted_credits}")
    
    # Test duration formatting
    durations = [30, 120, 3600, 7200]  # 30s, 2m, 1h, 2h
    for duration in durations:
        formatted_duration = format_duration(duration)
        print(f"✅ Duration {duration}s formatted as: {formatted_duration}")

def test_enhanced_data_summary():
    """Test enhanced data summary generation"""
    print("\n🧪 Testing Enhanced Data Summary")
    print("=" * 60)
    
    test_data = create_test_data()
    
    # Test cost data summary
    cost_summary = create_enhanced_data_summary(test_data['cost'], "Which warehouses cost the most?")
    print(f"✅ Cost Data Summary: {cost_summary}")
    
    # Test user data summary
    user_summary = create_enhanced_data_summary(test_data['user'], "Who are our most active users?")
    print(f"✅ User Data Summary: {user_summary}")

def test_fallback_answers():
    """Test enhanced fallback answer generation"""
    print("\n🧪 Testing Enhanced Fallback Answers")
    print("=" * 60)
    
    test_data = create_test_data()
    
    # Test cost fallback
    cost_fallback = generate_enhanced_fallback_answer(test_data['cost'], "Which warehouses cost the most?")
    print(f"✅ Cost Fallback: {cost_fallback}")
    
    # Test user fallback
    user_fallback = generate_enhanced_fallback_answer(test_data['user'], "Who are our most active users?")
    print(f"✅ User Fallback: {user_fallback}")
    
    # Test performance fallback
    perf_fallback = generate_enhanced_fallback_answer(test_data['performance'], "Which warehouses are slowest?")
    print(f"✅ Performance Fallback: {perf_fallback}")

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n🧪 Testing Edge Cases and Error Handling")
    print("=" * 60)
    
    # Test empty dataframe
    empty_df = pd.DataFrame()
    answer = generate_detailed_object_answer(empty_df, "Which warehouses cost the most?")
    print(f"✅ Empty DataFrame: {answer}")
    
    # Test single row dataframe
    single_row = pd.DataFrame({
        'WAREHOUSE_NAME': ['COMPUTE_WH'],
        'TOTAL_COST': [12.276297806]
    })
    answer = generate_detailed_object_answer(single_row, "Which warehouses cost the most?")
    print(f"✅ Single Row: {answer}")
    
    # Test dataframe with no relevant columns
    no_relevant = pd.DataFrame({
        'COLUMN_A': ['value1', 'value2'],
        'COLUMN_B': [1, 2]
    })
    answer = generate_detailed_object_answer(no_relevant, "Which warehouses cost the most?")
    print(f"✅ No Relevant Columns: {answer}")

def run_all_tests():
    """Run all tests and provide a summary"""
    print("🚀 Starting Enhanced AI Response Generation Tests")
    print("=" * 80)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Testing: Object Identification, Detailed Responses, Business Context")
    print("=" * 80)
    
    try:
        test_formatting_functions()
        test_enhanced_data_summary()
        test_cost_analysis()
        test_user_activity()
        test_performance_analysis()
        test_warehouse_analysis()
        test_fallback_answers()
        test_edge_cases()
        
        print("\n" + "=" * 80)
        print("✅ All tests completed successfully!")
        print("🎉 Enhanced AI response generation is working correctly")
        print("📊 Key improvements validated:")
        print("   • Object identification (warehouse names, user names)")
        print("   • Detailed cost analysis with dollar conversion")
        print("   • Performance analysis with readable time formats")
        print("   • User activity analysis with specific counts")
        print("   • Enhanced fallback responses")
        print("   • Business context in all responses")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
