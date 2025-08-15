-- ========================================
-- CURRENT SNOWFLAKE MONITORING SEMANTIC VIEWS (DEPLOYED)
-- ========================================

-- STEP 1: Create the database and schema
CREATE DATABASE IF NOT EXISTS SNOWFLAKE_MONITORING;
CREATE SCHEMA IF NOT EXISTS SNOWFLAKE_MONITORING.MONITORING_SEMANTIC;
USE DATABASE SNOWFLAKE_MONITORING;
USE SCHEMA MONITORING_SEMANTIC;

-- STEP 2: Create supporting views with proper primary key design
CREATE OR REPLACE VIEW warehouse_usage_base AS
SELECT
  warehouse_name,
  warehouse_id,
  credits_used_compute,
  credits_used_cloud_services,
  credits_used,
  start_time,
  end_time
FROM snowflake.account_usage.warehouse_metering_history
WHERE start_time >= DATEADD(DAY, -90, CURRENT_TIMESTAMP());

CREATE OR REPLACE VIEW query_performance_base AS
SELECT 
    query_id,
    query_text,
    user_name,
    warehouse_name,
    warehouse_size,
    start_time,
    end_time,
    execution_time,
    queued_provisioning_time,
    queued_repair_time,
    queued_overload_time,
    total_elapsed_time,
    bytes_scanned,
    rows_produced,
    credits_used_cloud_services
FROM snowflake.account_usage.query_history
WHERE start_time >= DATEADD('day', -30, CURRENT_TIMESTAMP());

CREATE OR REPLACE VIEW cost_analysis_base AS
SELECT 
    DATE(start_time) as usage_date,
    warehouse_name,
    warehouse_id,
    SUM(credits_used) as daily_credits,
    SUM(credits_used_compute) as daily_compute_credits,
    SUM(credits_used_cloud_services) as daily_cloud_credits,
    COUNT(*) as usage_events
FROM snowflake.account_usage.warehouse_metering_history
WHERE start_time >= DATEADD('day', -90, CURRENT_TIMESTAMP())
GROUP BY 1, 2, 3;

-- STEP 3: Create warehouse dimension table for proper relationships
CREATE OR REPLACE VIEW warehouse_dimension AS
SELECT DISTINCT
    warehouse_name,
    warehouse_id
FROM snowflake.account_usage.warehouse_metering_history
WHERE start_time >= DATEADD(DAY, -90, CURRENT_TIMESTAMP());

-- STEP 4: Create the enhanced semantic view with metadata enrichment (WORKING VERSION)
CREATE OR REPLACE SEMANTIC VIEW snowflake_monitoring_semantic
TABLES (
    warehouses AS warehouse_dimension 
        PRIMARY KEY (warehouse_name),
    
    warehouse_usage AS warehouse_usage_base 
        PRIMARY KEY (warehouse_id, start_time),
    
    query_performance AS query_performance_base 
        PRIMARY KEY (query_id),
    
    cost_analysis AS cost_analysis_base 
        PRIMARY KEY (usage_date, warehouse_name)
)
RELATIONSHIPS (
    warehouse_usage (warehouse_name) REFERENCES warehouses (warehouse_name),
    query_performance (warehouse_name) REFERENCES warehouses (warehouse_name),
    cost_analysis (warehouse_name) REFERENCES warehouses (warehouse_name)
)
DIMENSIONS (
    warehouses.warehouse_name AS warehouse_name
        WITH SYNONYMS = ('warehouse', 'compute resource', 'processing unit', 'compute cluster', 'data warehouse', 'compute warehouse', 'processing warehouse')
        COMMENT = 'Name of the Snowflake warehouse used for data processing and analytics',
    
    warehouse_usage.usage_date AS DATE(start_time)
        WITH SYNONYMS = ('date', 'usage date', 'billing date', 'activity date', 'cost date', 'usage period')
        COMMENT = 'Date when the warehouse was used for data processing',
    
    query_performance.user_name AS user_name
        WITH SYNONYMS = ('user', 'username', 'account', 'user account', 'user id', 'person', 'analyst', 'developer', 'data scientist')
        COMMENT = 'Name of the user who executed the query or performed the activity'
)
METRICS (
    warehouse_usage.total_credits AS SUM(credits_used)
        WITH SYNONYMS = ('total usage', 'total consumption', 'total spend', 'total cost', 'overall credits', 'total billing', 'complete usage')
        COMMENT = 'Total credits consumed by warehouse usage for data processing',
    
    warehouses.warehouse_count AS COUNT(DISTINCT warehouse_name)
        WITH SYNONYMS = ('number of warehouses', 'warehouse total', 'compute resources count', 'active warehouses', 'warehouse inventory')
        COMMENT = 'Total number of unique warehouses in use for data processing',
    
    query_performance.total_queries AS COUNT(*)
        WITH SYNONYMS = ('query count', 'total operations', 'number of queries', 'sql operations', 'data queries', 'analytics queries')
        COMMENT = 'Total number of queries executed across all warehouses'
);

-- STEP 5: Create enhanced Cost Analysis Semantic View with rich metadata (WORKING VERSION)
CREATE OR REPLACE SEMANTIC VIEW cost_analysis_semantic
TABLES (
    costs AS cost_analysis_base 
        PRIMARY KEY (usage_date, warehouse_name),
    
    cost_warehouses AS warehouse_dimension 
        PRIMARY KEY (warehouse_name)
)
RELATIONSHIPS (
    costs (warehouse_name) REFERENCES cost_warehouses (warehouse_name)
)
DIMENSIONS (
    costs.usage_date AS usage_date
        WITH SYNONYMS = ('date', 'billing date', 'cost date', 'usage date', 'expense date', 'charge date', 'period')
        COMMENT = 'Date for which the cost analysis is performed and billing calculated',
    
    costs.warehouse_name AS warehouse_name
        WITH SYNONYMS = ('warehouse', 'compute resource', 'processing unit', 'compute cluster', 'data warehouse', 'compute warehouse', 'processing warehouse', 'analytics warehouse')
        COMMENT = 'Name of the Snowflake warehouse being analyzed for costs and usage patterns',
    
    costs.cost_category AS CASE
        WHEN daily_credits > 100 THEN 'HIGH'
        WHEN daily_credits > 20 THEN 'MEDIUM'
        ELSE 'LOW'
    END
        WITH SYNONYMS = ('cost level', 'spending category', 'usage category', 'cost tier', 'expense level', 'billing tier', 'usage tier')
        COMMENT = 'Cost categorization: LOW (<20 credits), MEDIUM (20-100 credits), HIGH (>100 credits) based on daily usage'
)
METRICS (
    costs.total_cost AS SUM(daily_credits)
        WITH SYNONYMS = ('total spend', 'total expense', 'total usage cost', 'total billing', 'overall cost', 'complete cost', 'total charges', 'total credits')
        COMMENT = 'Total cost in credits across all warehouses and time periods for comprehensive cost analysis',
    
    costs.avg_daily_cost AS AVG(daily_credits)
        WITH SYNONYMS = ('average daily spend', 'average daily expense', 'average daily usage', 'daily average cost', 'mean daily cost', 'typical daily cost')
        COMMENT = 'Average daily cost across all warehouses to understand typical usage patterns',
    
    costs.cost_trend AS AVG(daily_credits)
        WITH SYNONYMS = ('cost trend', 'spending trend', 'usage trend', 'cost pattern', 'expense trend', 'billing trend', 'usage pattern')
        COMMENT = 'Trend in daily costs over time to identify usage patterns and cost optimization opportunities',
    
    costs.compute_vs_cloud_ratio AS AVG(daily_compute_credits) / NULLIF(AVG(daily_cloud_credits), 0)
        WITH SYNONYMS = ('compute cloud ratio', 'processing vs services ratio', 'compute efficiency', 'compute to cloud ratio', 'processing efficiency')
        COMMENT = 'Ratio of compute credits to cloud service credits, indicating processing efficiency and resource utilization',
    
    costs.high_cost_days AS COUNT(CASE WHEN daily_credits > 100 THEN 1 END)
        WITH SYNONYMS = ('expensive days', 'high spend days', 'peak cost days', 'cost spike days', 'high usage days', 'expensive periods')
        COMMENT = 'Number of days where daily cost exceeded 100 credits, indicating peak usage or potential optimization opportunities'
);

-- STEP 6: Create enhanced User Activity Semantic View with rich metadata (WORKING VERSION)
CREATE OR REPLACE SEMANTIC VIEW user_activity_semantic
TABLES (
    user_activity AS query_performance_base 
        PRIMARY KEY (query_id),

    user_warehouses AS warehouse_dimension 
        PRIMARY KEY (warehouse_name)
)
RELATIONSHIPS (
    user_activity (warehouse_name) REFERENCES user_warehouses (warehouse_name)
)
DIMENSIONS (
    user_activity.user_name AS user_name
        WITH SYNONYMS = ('user', 'username', 'account', 'user account', 'user id', 'person', 'analyst', 'developer', 'data scientist', 'end user')
        COMMENT = 'Name of the user who performed the activity or executed queries',

    user_activity.warehouse_name AS warehouse_name
        WITH SYNONYMS = ('warehouse', 'compute resource', 'processing unit', 'compute cluster', 'data warehouse', 'analytics warehouse')
        COMMENT = 'Warehouse used by the user for their queries and data processing activities',

    user_activity.query_type AS CASE 
        WHEN UPPER(query_text) LIKE 'SELECT%' THEN 'SELECT'
        WHEN UPPER(query_text) LIKE 'INSERT%' THEN 'INSERT'
        WHEN UPPER(query_text) LIKE 'UPDATE%' THEN 'UPDATE'
        WHEN UPPER(query_text) LIKE 'DELETE%' THEN 'DELETE'
        WHEN UPPER(query_text) LIKE 'CREATE%' THEN 'CREATE'
        ELSE 'OTHER'
    END
        WITH SYNONYMS = ('query type', 'operation type', 'sql type', 'command type', 'activity type', 'sql operation', 'data operation')
        COMMENT = 'Type of SQL operation performed by the user: SELECT (read), INSERT (create), UPDATE (modify), DELETE (remove), CREATE (structure), OTHER',

    user_activity.warehouse_size AS warehouse_size
        WITH SYNONYMS = ('size', 'compute size', 'processing power', 'capacity', 'warehouse capacity', 'compute capacity', 'processing capacity')
        COMMENT = 'Size of the warehouse used, indicating processing power and capacity (XS, S, M, L, XL, XXL, XXXL)'
)
METRICS (
    user_activity.total_user_queries AS COUNT(*)
        WITH SYNONYMS = ('user query count', 'total queries per user', 'user operations', 'user activity count', 'query volume per user')
        COMMENT = 'Total number of queries executed by each user for activity analysis',

    user_activity.avg_user_execution_time AS AVG(execution_time)
        WITH SYNONYMS = ('average execution time', 'mean execution time', 'typical execution time', 'user performance', 'query performance')
        COMMENT = 'Average execution time for queries by each user, indicating performance patterns',

    user_activity.slow_query_count AS COUNT(CASE WHEN execution_time > 30000 THEN 1 END)
        WITH SYNONYMS = ('slow queries', 'long running queries', 'performance issues', 'slow operations', 'timeout queries')
        COMMENT = 'Number of queries that took longer than 30 seconds, indicating potential performance issues',

    user_activity.data_scan_volume AS SUM(bytes_scanned)
        WITH SYNONYMS = ('data scanned', 'bytes processed', 'data volume', 'scan volume', 'processed data', 'data consumption')
        COMMENT = 'Total amount of data scanned by each user, indicating data access patterns and resource usage'
);

-- STEP 7: Create enhanced Query Performance Semantic View with rich metadata (WORKING VERSION)
CREATE OR REPLACE SEMANTIC VIEW query_performance_semantic
TABLES (
    queries AS query_performance_base 
        PRIMARY KEY (query_id),
    
    query_warehouses AS warehouse_dimension 
        PRIMARY KEY (warehouse_name)
)
RELATIONSHIPS (
    queries (warehouse_name) REFERENCES query_warehouses (warehouse_name)
)
DIMENSIONS (
    queries.query_type AS CASE 
        WHEN UPPER(query_text) LIKE 'SELECT%' THEN 'SELECT'
        WHEN UPPER(query_text) LIKE 'INSERT%' THEN 'INSERT'
        WHEN UPPER(query_text) LIKE 'UPDATE%' THEN 'UPDATE'
        WHEN UPPER(query_text) LIKE 'DELETE%' THEN 'DELETE'
        WHEN UPPER(query_text) LIKE 'CREATE%' THEN 'CREATE'
        ELSE 'OTHER'
    END
        WITH SYNONYMS = ('query type', 'operation type', 'sql type', 'command type')
        COMMENT = 'Type of SQL operation being analyzed for performance',
    
    queries.warehouse_name AS warehouse_name
        WITH SYNONYMS = ('warehouse', 'compute resource', 'processing unit')
        COMMENT = 'Warehouse where the query performance is being measured',
    
    queries.warehouse_size AS warehouse_size
        WITH SYNONYMS = ('size', 'compute size', 'processing power', 'capacity')
        COMMENT = 'Size of warehouse used for query execution',
    
    queries.user_name AS user_name
        WITH SYNONYMS = ('user', 'username', 'account', 'user account')
        COMMENT = 'User who executed the query being analyzed',
    
    queries.usage_date AS DATE(start_time)
        WITH SYNONYMS = ('date', 'query date', 'execution date', 'performance date')
        COMMENT = 'Date when the query performance was measured',
    
    queries.usage_hour AS HOUR(start_time)
        WITH SYNONYMS = ('hour', 'time of day', 'execution hour', 'performance hour')
        COMMENT = 'Hour of the day when query performance was measured'
)
METRICS (
    queries.total_queries AS COUNT(*)
        WITH SYNONYMS = ('query count', 'total operations', 'number of queries')
        COMMENT = 'Total number of queries analyzed for performance',
    
    queries.avg_execution_time AS AVG(total_elapsed_time)
        WITH SYNONYMS = ('average query time', 'average response time', 'average processing time')
        COMMENT = 'Average time taken to execute queries in milliseconds',
    
    queries.slow_queries AS COUNT(CASE WHEN total_elapsed_time > 60000 THEN 1 END)
        WITH SYNONYMS = ('slow query count', 'long running queries', 'performance issues')
        COMMENT = 'Number of queries that took longer than 60 seconds to execute',
    
    queries.total_data_scanned AS SUM(bytes_scanned)
        WITH SYNONYMS = ('data scanned', 'bytes processed', 'data volume')
        COMMENT = 'Total amount of data scanned by all queries in bytes',
    
    queries.avg_queue_time AS AVG(queued_provisioning_time)
        WITH SYNONYMS = ('average queue time', 'average wait time', 'average provisioning time')
        COMMENT = 'Average time queries spent waiting in queue before execution'
);

-- STEP 8: Create enhanced Resource Utilization Semantic View with rich metadata (WORKING VERSION)
CREATE OR REPLACE SEMANTIC VIEW resource_utilization_semantic
TABLES (
    resources AS warehouse_usage_base 
        PRIMARY KEY (warehouse_id, start_time),
    
    resource_warehouses AS warehouse_dimension 
        PRIMARY KEY (warehouse_name)
)
RELATIONSHIPS (
    resources (warehouse_name) REFERENCES resource_warehouses (warehouse_name)
)
DIMENSIONS (
    resources.warehouse_name AS warehouse_name
        WITH SYNONYMS = ('warehouse', 'compute resource', 'processing unit', 'compute cluster')
        COMMENT = 'Name of the warehouse being analyzed for resource utilization',
    
    resources.usage_date AS DATE(start_time)
        WITH SYNONYMS = ('date', 'utilization date', 'usage date', 'resource date')
        COMMENT = 'Date when resource utilization was measured',
    
    resources.usage_hour AS HOUR(start_time)
        WITH SYNONYMS = ('hour', 'time of day', 'utilization hour', 'usage hour')
        COMMENT = 'Hour of the day when resource utilization was measured'
)
METRICS (
    resources.total_credits_used AS SUM(credits_used)
        WITH SYNONYMS = ('total usage', 'total consumption', 'total resource usage')
        COMMENT = 'Total credits consumed by warehouse resource utilization',
    
    resources.avg_credits_per_hour AS AVG(credits_used)
        WITH SYNONYMS = ('average usage', 'average consumption', 'average resource usage')
        COMMENT = 'Average credits consumed per hour of warehouse activity',
    
    resources.utilization_efficiency AS AVG(credits_used_compute) / NULLIF(AVG(credits_used), 0)
        WITH SYNONYMS = ('efficiency', 'compute efficiency', 'resource efficiency', 'utilization ratio')
        COMMENT = 'Ratio of compute credits to total credits, indicating resource utilization efficiency',
    
    resources.peak_usage_hours AS COUNT(CASE WHEN credits_used > 10 THEN 1 END)
        WITH SYNONYMS = ('peak hours', 'high usage hours', 'busy hours', 'peak utilization')
        COMMENT = 'Number of hours where usage exceeded 10 credits, indicating peak utilization'
);

-- STEP 9: Create enhanced Security Monitoring Semantic View with rich metadata (WORKING VERSION)
CREATE OR REPLACE SEMANTIC VIEW security_monitoring_semantic
TABLES (
    security_events AS query_performance_base 
        PRIMARY KEY (query_id),
    
    security_users AS query_performance_base 
        PRIMARY KEY (user_name),
    
    security_warehouses AS warehouse_dimension 
        PRIMARY KEY (warehouse_name)
)
RELATIONSHIPS (
    security_events (user_name) REFERENCES security_users (user_name),
    security_events (warehouse_name) REFERENCES security_warehouses (warehouse_name)
)
DIMENSIONS (
    security_users.user_name AS user_name
        WITH SYNONYMS = ('user', 'username', 'account', 'user account', 'user id')
        COMMENT = 'User account being monitored for security events',
    
    security_events.warehouse_name AS warehouse_name
        WITH SYNONYMS = ('warehouse', 'compute resource', 'processing unit')
        COMMENT = 'Warehouse where security events are being monitored',
    
    security_events.query_type AS CASE 
        WHEN UPPER(query_text) LIKE 'SELECT%' THEN 'SELECT'
        WHEN UPPER(query_text) LIKE 'INSERT%' THEN 'INSERT'
        WHEN UPPER(query_text) LIKE 'UPDATE%' THEN 'UPDATE'
        WHEN UPPER(query_text) LIKE 'DELETE%' THEN 'DELETE'
        WHEN UPPER(query_text) LIKE 'CREATE%' THEN 'CREATE'
        ELSE 'OTHER'
    END
        WITH SYNONYMS = ('query type', 'operation type', 'sql type', 'command type', 'security event type')
        COMMENT = 'Type of SQL operation being monitored for security purposes',
    
    security_events.usage_date AS DATE(start_time)
        WITH SYNONYMS = ('date', 'security date', 'event date', 'monitoring date')
        COMMENT = 'Date when security events were monitored',
    
    security_events.usage_hour AS HOUR(start_time)
        WITH SYNONYMS = ('hour', 'time of day', 'event hour', 'security hour')
        COMMENT = 'Hour of the day when security events occurred'
)
METRICS (
    security_users.total_user_activity AS COUNT(*)
        WITH SYNONYMS = ('activity count', 'total events', 'user events', 'security events')
        COMMENT = 'Total number of security events for the user',
    
    security_users.avg_user_execution_time AS AVG(total_elapsed_time)
        WITH SYNONYMS = ('average execution time', 'average response time', 'average processing time')
        COMMENT = 'Average time taken by user queries in milliseconds',
    
    security_users.user_data_access AS SUM(bytes_scanned)
        WITH SYNONYMS = ('data access', 'bytes accessed', 'data volume accessed', 'scan volume')
        COMMENT = 'Total amount of data accessed by user queries in bytes',
    
    security_users.suspicious_activity AS COUNT(CASE WHEN bytes_scanned > 1000000000 THEN 1 END)
        WITH SYNONYMS = ('suspicious events', 'high data access', 'unusual activity', 'anomalies')
        COMMENT = 'Number of events where data access exceeded 1GB (potential security concern)',
    
    security_users.long_running_queries AS COUNT(CASE WHEN total_elapsed_time > 300000 THEN 1 END)
        WITH SYNONYMS = ('long queries', 'extended queries', 'timeout queries', 'performance issues')
        COMMENT = 'Number of queries that ran longer than 5 minutes (potential security concern)'
);

-- STEP 10: Test queries to validate the enhanced semantic views
-- These queries demonstrate the improved metadata and should provide better AI responses

-- Test Query 1: Enhanced cost analysis with context
SELECT * FROM SEMANTIC_VIEW(
    cost_analysis_semantic
    DIMENSIONS warehouse_name, cost_category
    METRICS total_cost, avg_daily_cost, high_cost_days
)
ORDER BY total_cost DESC
LIMIT 5;

-- Test Query 2: Enhanced user activity with context
SELECT * FROM SEMANTIC_VIEW(
    user_activity_semantic
    DIMENSIONS user_name, warehouse_name, query_type
    METRICS total_user_queries, avg_user_execution_time, slow_query_count
)
ORDER BY total_user_queries DESC
LIMIT 5;

-- Test Query 3: Enhanced query performance with context
SELECT * FROM SEMANTIC_VIEW(
    query_performance_semantic
    DIMENSIONS warehouse_name, warehouse_size, query_type
    METRICS total_queries, avg_execution_time, slow_queries
)
ORDER BY avg_execution_time DESC
LIMIT 5;

-- Test Query 4: Enhanced resource utilization with context
SELECT * FROM SEMANTIC_VIEW(
    resource_utilization_semantic
    DIMENSIONS warehouse_name, usage_hour
    METRICS total_credits_used, avg_credits_per_hour, utilization_efficiency
)
ORDER BY total_credits_used DESC
LIMIT 5;

