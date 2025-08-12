-- ========================================
-- CORRECTED SNOWFLAKE MONITORING SEMANTIC VIEWS POC
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



-- STEP 4: Create the corrected semantic view
CREATE OR REPLACE SEMANTIC VIEW snowflake_monitoring_semantic
TABLES (
    -- Warehouse dimension as the parent table
    warehouses AS warehouse_dimension 
        PRIMARY KEY (warehouse_name),
    
    -- Usage data references warehouse dimension
    warehouse_usage AS warehouse_usage_base 
        PRIMARY KEY (warehouse_id, start_time),
    
    -- Query data references warehouse dimension  
    query_performance AS query_performance_base 
        PRIMARY KEY (query_id),
    
    -- Cost analysis references warehouse dimension
    cost_analysis AS cost_analysis_base 
        PRIMARY KEY (usage_date, warehouse_name)
)
RELATIONSHIPS (
    -- All tables reference the warehouse dimension
    warehouse_usage (warehouse_name) REFERENCES warehouses (warehouse_name),
    query_performance (warehouse_name) REFERENCES warehouses (warehouse_name),
    cost_analysis (warehouse_name) REFERENCES warehouses (warehouse_name)
)
FACTS (
    warehouse_usage.credits_consumed AS credits_used,
    warehouse_usage.compute_credits AS credits_used_compute,
    warehouse_usage.cloud_service_credits AS credits_used_cloud_services,
    query_performance.execution_duration AS execution_time,
    query_performance.queue_time AS queued_provisioning_time,
    query_performance.data_scanned AS bytes_scanned,
    query_performance.rows_returned AS rows_produced,
    cost_analysis.total_daily_credits AS daily_credits
)
DIMENSIONS (
    warehouses.warehouse_name AS warehouse_name,
    warehouse_usage.usage_date AS DATE(start_time),
    warehouse_usage.usage_hour AS HOUR(start_time),
    query_performance.warehouse_size AS warehouse_size,
    query_performance.user_name AS user_name,
    query_performance.query_type AS CASE 
        WHEN UPPER(query_text) LIKE 'SELECT%' THEN 'SELECT'
        WHEN UPPER(query_text) LIKE 'INSERT%' THEN 'INSERT'
        WHEN UPPER(query_text) LIKE 'UPDATE%' THEN 'UPDATE'
        WHEN UPPER(query_text) LIKE 'DELETE%' THEN 'DELETE'
        WHEN UPPER(query_text) LIKE 'CREATE%' THEN 'CREATE'
        ELSE 'OTHER'
    END,
    cost_analysis.cost_category AS CASE
        WHEN daily_credits > 100 THEN 'HIGH'
        WHEN daily_credits > 20 THEN 'MEDIUM'
        ELSE 'LOW'
    END
)
METRICS (
    warehouse_usage.total_credits AS SUM(credits_consumed),
    warehouse_usage.avg_credits_per_hour AS AVG(credits_consumed),
    warehouses.warehouse_count AS COUNT(DISTINCT warehouse_name),
    query_performance.avg_execution_time AS AVG(execution_duration),
    query_performance.total_queries AS COUNT(*),
    query_performance.slow_queries AS COUNT(CASE WHEN execution_duration > 60000 THEN 1 END),
    cost_analysis.total_daily_spend AS SUM(total_daily_credits),
    cost_analysis.cost_trend AS AVG(total_daily_credits)
);











-- STEP 5: Create alerts for proactive monitoring
CREATE OR REPLACE ALERT high_credit_consumption_alert
WAREHOUSE = 'SNOWSARVA_WAREHOUSE'
SCHEDULE = 'USING CRON 0 */6 * * * UTC'  -- Every 6 hours
IF (EXISTS (
    SELECT * FROM SEMANTIC_VIEW(
        snowflake_monitoring_semantic
        DIMENSIONS warehouse_name
        METRICS total_credits
        WHERE total_credits > 50  -- Alert if warehouse uses >50 credits in 6 hours
    )
))
THEN 
    CALL SYSTEM$SEND_EMAIL(
        'MONITORING_EMAIL_INTEGRATION',
        'akhilgurrapu151@gmail.com',
        'High Credit Consumption Alert',
        'One or more warehouses have exceeded the credit threshold'
    );

CREATE OR REPLACE ALERT slow_query_alert
WAREHOUSE = 'SNOWSARVA_WAREHOUSE'
SCHEDULE = 'USING CRON 0 */2 * * * UTC'  -- Every 2 hours
IF (EXISTS (
    SELECT * FROM SEMANTIC_VIEW(
        snowflake_monitoring_semantic
        DIMENSIONS user_name, warehouse_name
        METRICS avg_execution_time, slow_queries
        WHERE avg_execution_time > 60000 OR slow_queries > 5
    )
))
THEN
    CALL SYSTEM$SEND_EMAIL(
        'MONITORING_EMAIL_INTEGRATION',
        'admin@company.com',
        'Slow Query Performance Alert',
        'Detected slow-running queries or performance degradation'
    );

-- STEP 6: Sample queries for business users using natural language concepts
-- These queries can now be used with Cortex Analyst

/*
Example natural language queries that Cortex Analyst can understand:

1. "Show me the warehouses with the highest credit consumption this week"
2. "Which users are running the most expensive queries?"
3. "What is the average query execution time by warehouse size?"
4. "Show me the cost trend for each warehouse over the last 30 days"
5. "Which query types are consuming the most credits?"
*/

-- STEP 7: Create a dashboard view for BI tools

-- -- STEP 8: Grant permissions for different user roles
-- GRANT USAGE ON DATABASE SNOWFLAKE_MONITORING TO ROLE MONITORING_ANALYST;
-- GRANT USAGE ON SCHEMA SNOWFLAKE_MONITORING.MONITORING_SEMANTIC TO ROLE MONITORING_ANALYST;
-- GRANT SELECT ON SEMANTIC VIEW snowflake_monitoring_semantic TO ROLE MONITORING_ANALYST;
-- GRANT SELECT ON VIEW monitoring_dashboard TO ROLE MONITORING_ANALYST;

-- -- Business users can now query using business-friendly terms:
-- GRANT USAGE ON DATABASE SNOWFLAKE_MONITORING TO ROLE BUSINESS_ANALYST;
-- GRANT USAGE ON SCHEMA SNOWFLAKE_MONITORING.MONITORING_SEMANTIC TO ROLE BUSINESS_ANALYST;
-- GRANT SELECT ON SEMANTIC VIEW snowflake_monitoring_semantic TO ROLE BUSINESS_ANALYST;

-- STEP 9: Test queries to validate the semantic view
/*
Test the semantic view with sample queries:
*/

-- Query 1: Basic warehouse performance metrics
-- Query 1: Basic warehouse performance metrics
SELECT * FROM SEMANTIC_VIEW(
    snowflake_monitoring_semantic
    DIMENSIONS warehouse_name
    METRICS total_credits, warehouse_count
)
ORDER BY total_credits DESC
LIMIT 10;


-- Query 2: Warehouse performance with size (query-level aggregation)  
SELECT * FROM SEMANTIC_VIEW(
    snowflake_monitoring_semantic
    DIMENSIONS warehouse_name, warehouse_size
    METRICS total_queries, avg_execution_time
)
ORDER BY total_queries DESC
LIMIT 10;


-- Query 4: User activity analysis
SELECT * FROM SEMANTIC_VIEW(
    snowflake_monitoring_semantic
    DIMENSIONS user_name, query_type
    METRICS total_queries, avg_execution_time, slow_queries
)
ORDER BY total_queries DESC
LIMIT 20;