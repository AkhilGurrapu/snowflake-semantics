#!/usr/bin/env python3
"""
Natural Language Semantic Queries
Hybrid solution using Cortex Analyst + Semantic Views for true natural language queries
"""

import subprocess
import json
import re
from typing import Dict, Any, Optional

class NaturalLanguageSemanticQueries:
    """
    Natural language queries using Cortex Analyst + Semantic Views
    Maps business questions to semantic view queries
    """
    
    def __init__(self, config_file: str = "config.toml", connection: str = "semantics"):
        self.config_file = config_file
        self.connection = connection
        
        # Define query patterns for common business questions
        self.query_patterns = {
            # Credit consumption patterns
            r"warehouses?.*consuming.*most.*credits?": {
                "sql": "SELECT * FROM SEMANTIC_VIEW(SNOWFLAKE_MONITORING_SEMANTIC DIMENSIONS warehouse_name METRICS total_credits) ORDER BY total_credits DESC",
                "description": "Warehouses with highest credit consumption"
            },
            r"highest.*credit.*consumption": {
                "sql": "SELECT * FROM SEMANTIC_VIEW(SNOWFLAKE_MONITORING_SEMANTIC DIMENSIONS warehouse_name METRICS total_credits) ORDER BY total_credits DESC",
                "description": "Highest credit consumption by warehouse"
            },
            
            # User activity patterns
            r"most.*active.*users?": {
                "sql": "SELECT * FROM SEMANTIC_VIEW(SNOWFLAKE_MONITORING_SEMANTIC DIMENSIONS user_name, warehouse_name METRICS total_queries, avg_execution_time) ORDER BY total_queries DESC",
                "description": "Most active users by query volume"
            },
            r"users?.*running.*most.*queries?": {
                "sql": "SELECT * FROM SEMANTIC_VIEW(SNOWFLAKE_MONITORING_SEMANTIC DIMENSIONS user_name, warehouse_name METRICS total_queries, avg_execution_time) ORDER BY total_queries DESC",
                "description": "Users running most queries"
            },
            
            # Performance patterns
            r"slow.*queries?": {
                "sql": "SELECT * FROM SEMANTIC_VIEW(SNOWFLAKE_MONITORING_SEMANTIC DIMENSIONS user_name, warehouse_name METRICS slow_queries, avg_execution_time) WHERE slow_queries > 0 ORDER BY avg_execution_time DESC",
                "description": "Slow queries that need optimization"
            },
            r"longest.*execution.*time": {
                "sql": "SELECT * FROM SEMANTIC_VIEW(SNOWFLAKE_MONITORING_SEMANTIC DIMENSIONS user_name, warehouse_name METRICS avg_execution_time, total_queries) ORDER BY avg_execution_time DESC",
                "description": "Queries with longest execution time"
            },
            
            # Cost patterns
            r"most.*expensive.*warehouses?": {
                "sql": "SELECT * FROM SEMANTIC_VIEW(SNOWFLAKE_MONITORING_SEMANTIC DIMENSIONS warehouse_name, cost_category METRICS total_daily_spend, cost_trend) ORDER BY total_daily_spend DESC",
                "description": "Most expensive warehouses to operate"
            },
            r"cost.*trend": {
                "sql": "SELECT * FROM SEMANTIC_VIEW(SNOWFLAKE_MONITORING_SEMANTIC DIMENSIONS warehouse_name, cost_category METRICS total_daily_spend, cost_trend) ORDER BY total_daily_spend DESC",
                "description": "Cost trends by warehouse"
            },
            
            # Query type patterns
            r"types?.*of.*queries?": {
                "sql": "SELECT * FROM SEMANTIC_VIEW(SNOWFLAKE_MONITORING_SEMANTIC DIMENSIONS query_type METRICS total_queries, avg_execution_time) ORDER BY total_queries DESC",
                "description": "Query types and their frequency"
            },
            r"most.*frequent.*queries?": {
                "sql": "SELECT * FROM SEMANTIC_VIEW(SNOWFLAKE_MONITORING_SEMANTIC DIMENSIONS query_type METRICS total_queries, avg_execution_time) ORDER BY total_queries DESC",
                "description": "Most frequent query types"
            },
            
            # Warehouse performance patterns
            r"warehouse.*performance": {
                "sql": "SELECT * FROM SEMANTIC_VIEW(SNOWFLAKE_MONITORING_SEMANTIC DIMENSIONS warehouse_name METRICS total_queries, avg_execution_time, total_credits) ORDER BY avg_execution_time ASC",
                "description": "Warehouse performance overview"
            },
            r"best.*performing.*warehouses?": {
                "sql": "SELECT * FROM SEMANTIC_VIEW(SNOWFLAKE_MONITORING_SEMANTIC DIMENSIONS warehouse_name METRICS avg_execution_time, total_queries) ORDER BY avg_execution_time ASC",
                "description": "Best performing warehouses"
            }
        }
    
    def _execute_snowflake_query(self, sql: str) -> Dict[str, Any]:
        """Execute SQL query using Snowflake CLI"""
        try:
            cmd = [
                "snow", 
                "--config-file", self.config_file, 
                "sql", 
                "-c", self.connection, 
                "-q", sql
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return {
                    "success": True,
                    "data": result.stdout,
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "error": result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "data": None,
                "error": "Query timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "error": str(e)
            }
    
    def _get_cortex_analysis(self, question: str) -> str:
        """Get Cortex Analyst's understanding of the question"""
        sql = f"SELECT SNOWFLAKE.CORTEX.COMPLETE('llama2-70b-chat', '{question}') as analysis"
        
        result = self._execute_snowflake_query(sql)
        if result["success"]:
            return result["data"]
        else:
            return f"Error getting Cortex analysis: {result['error']}"
    
    def _find_matching_pattern(self, question: str) -> Optional[Dict[str, Any]]:
        """Find the best matching query pattern for the question"""
        question_lower = question.lower()
        
        for pattern, query_info in self.query_patterns.items():
            if re.search(pattern, question_lower):
                return query_info
        
        return None
    
    def natural_language_query(self, question: str, use_cortex: bool = True) -> Dict[str, Any]:
        """
        Execute natural language query using semantic views
        
        Args:
            question: Natural language question
            use_cortex: Whether to use Cortex Analyst for additional analysis
            
        Returns:
            Dictionary containing SQL, results, and analysis
        """
        print(f"Processing question: {question}")
        print("-" * 50)
        
        # Step 1: Find matching pattern
        pattern_match = self._find_matching_pattern(question)
        
        if not pattern_match:
            return {
                "question": question,
                "error": "No matching query pattern found for this question",
                "sql": None,
                "results": None,
                "cortex_analysis": None
            }
        
        sql = pattern_match["sql"]
        description = pattern_match["description"]
        
        print(f"Matched pattern: {description}")
        print(f"Generated SQL: {sql}")
        print("-" * 50)
        
        # Step 2: Execute the semantic view query
        result = self._execute_snowflake_query(sql)
        
        # Step 3: Get Cortex analysis if requested
        cortex_analysis = None
        if use_cortex:
            print("Getting Cortex Analyst analysis...")
            cortex_analysis = self._get_cortex_analysis(question)
        
        return {
            "question": question,
            "sql": sql,
            "description": description,
            "results": result,
            "cortex_analysis": cortex_analysis
        }
    
    def interactive_mode(self):
        """Interactive mode for natural language queries"""
        print("🎯 Natural Language Semantic Queries")
        print("Ask questions about your Snowflake monitoring data!")
        print("Type 'quit' to exit")
        print("-" * 50)
        
        while True:
            question = input("\n❓ Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            # Process the question
            result = self.natural_language_query(question)
            
            if "error" in result and result["error"]:
                print(f"❌ Error: {result['error']}")
                continue
            
            # Display results
            print(f"\n📊 Results for: {result['description']}")
            if result["results"]["success"]:
                print(result["results"]["data"])
            else:
                print(f"❌ Query failed: {result['results']['error']}")
            
            # Display Cortex analysis if available
            if result.get("cortex_analysis"):
                print(f"\n🤖 Cortex Analyst Analysis:")
                print(result["cortex_analysis"])
            
            print("-" * 50)


def main():
    """Command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Natural Language Semantic Queries")
    parser.add_argument("question", nargs="?", help="Natural language question")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Start interactive mode")
    parser.add_argument("--no-cortex", action="store_true",
                       help="Skip Cortex Analyst analysis")
    
    args = parser.parse_args()
    
    # Initialize the query processor
    nlq = NaturalLanguageSemanticQueries()
    
    if args.interactive:
        nlq.interactive_mode()
    elif args.question:
        # Process single question
        result = nlq.natural_language_query(args.question, use_cortex=not args.no_cortex)
        
        if "error" in result and result["error"]:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"📊 Results for: {result['description']}")
            if result["results"]["success"]:
                print(result["results"]["data"])
            else:
                print(f"❌ Query failed: {result['results']['error']}")
            
            if result.get("cortex_analysis"):
                print(f"\n🤖 Cortex Analyst Analysis:")
                print(result["cortex_analysis"])
    else:
        print("Please provide a question or use --interactive mode")
        parser.print_help()


if __name__ == "__main__":
    main()
