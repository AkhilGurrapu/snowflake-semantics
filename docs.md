# Complete Beginner's Guide to Semantic Views in Snowflake

## Table of Contents
1. [What is a Semantic Layer?](#what-is-a-semantic-layer)
2. [What are Semantic Views in Snowflake?](#what-are-semantic-views-in-snowflake)
3. [Why Do You Need Semantic Views?](#why-do-you-need-semantic-views)
4. [Key Components of Semantic Views](#key-components-of-semantic-views)
5. [Simple Example: Creating Your First Semantic View](#simple-example-creating-your-first-semantic-view)
6. [How to Query Semantic Views](#how-to-query-semantic-views)
7. [Real-World Use Cases](#real-world-use-cases)
8. [Best Practices](#best-practices)

## What is a Semantic Layer?

Think of a semantic layer like a **translator** between you (who speaks business language) and your database (which speaks technical language).

### Real-World Analogy
Imagine you're at a restaurant in a foreign country:
- **You** want to order "a large pepperoni pizza with extra cheese"
- **The kitchen** needs to know "Item ID 127, Size L, Topping IDs 45,67, Extra Flag=1"
- **The waiter** acts as your semantic layer - translating your business request into kitchen language

In data terms:
- **You** want "total revenue by region for this quarter" 
- **The database** has tables like `FACT_SALES`, `DIM_GEOGRAPHY`, `DIM_TIME` with cryptic column names
- **The semantic layer** translates your business question into the right SQL joins and calculations

## What are Semantic Views in Snowflake?

Semantic Views are Snowflake's native implementation of the semantic layer concept. They are **database objects** (like tables or views) that store business definitions and relationships.

### Key Features:
- **Schema-level objects** - They live in your database alongside tables and views
- **Business-friendly** - Use terms like "customer_name" instead of "C_CUST_NM_TX"  
- **AI-ready** - Work with Cortex Analyst for natural language queries
- **Consistent** - One definition that everyone uses

## Why Do You Need Semantic Views?

### The Problem Without Semantic Views:

**Scenario**: You want to calculate "Monthly Revenue" for a report.

**Traditional Approach**:
```sql
-- Person A writes this:
SELECT 
  DATE_TRUNC('month', order_date) as month,
  SUM(amount) as monthly_revenue
FROM orders 
WHERE status = 'completed'
GROUP BY 1;

-- Person B writes this:
SELECT 
  DATE_PART('month', created_date) as month,
  SUM(total_price) as monthly_revenue  
FROM sales_transactions
WHERE payment_status = 'paid'
GROUP BY 1;
```

**Result**: Two different "Monthly Revenue" numbers! 🤦‍♂️

### The Solution With Semantic Views:

You define "Monthly Revenue" **once** in the semantic view:
```sql
-- In the semantic view definition
METRICS (
  orders.monthly_revenue AS SUM(amount) 
  -- Only from completed orders, using order_date
)
```

Now **everyone** gets the same number when they ask for "Monthly Revenue".

## Key Components of Semantic Views

### 1. **Logical Tables**
- Business-friendly names for your physical database tables
- Example: `customers` instead of `DIM_CUSTOMER_MASTER_TBL`

### 2. **Relationships** 
- Pre-defined joins between tables
- No more remembering which key joins to which table!

### 3. **Dimensions**
- Categories that describe your data (the "who", "what", "where", "when")
- Examples: customer_name, product_category, region, order_date

### 4. **Facts**
- Raw measurable values
- Examples: quantity_sold, unit_price, discount_amount

### 5. **Metrics**
- Calculated business measures (usually aggregations of facts)
- Examples: total_revenue, average_order_value, customer_count

## Simple Example: Creating Your First Semantic View

Let's create a semantic view for a simple e-commerce scenario with customers and orders.

### Step 1: Your Physical Tables
```sql
-- You have these tables in your database:
CUSTOMERS (C_CUSTKEY, C_NAME, C_COUNTRY, C_PHONE)
ORDERS (O_ORDERKEY, O_CUSTKEY, O_ORDERDATE, O_TOTALPRICE, O_STATUS)
```

### Step 2: Create the Semantic View
```sql
CREATE SEMANTIC VIEW ecommerce_analytics

-- Define logical tables with business-friendly names
TABLES (
  customers AS CUSTOMERS 
    PRIMARY KEY (C_CUSTKEY),
  orders AS ORDERS 
    PRIMARY KEY (O_ORDERKEY)
)

-- Define how tables relate to each other  
RELATIONSHIPS (
  orders(O_CUSTKEY) REFERENCES customers(C_CUSTKEY)
)

-- Define dimensions (categories for analysis)
DIMENSIONS (
  customers.customer_name AS C_NAME,
  customers.customer_country AS C_COUNTRY,
  orders.order_date AS O_ORDERDATE,
  orders.order_status AS O_STATUS
)

-- Define facts (raw measurable values)
FACTS (
  orders.order_amount AS O_TOTALPRICE
)

-- Define metrics (calculated business measures)
METRICS (
  orders.total_revenue AS SUM(O_TOTALPRICE),
  orders.average_order_value AS AVG(O_TOTALPRICE),
  customers.customer_count AS COUNT(C_CUSTKEY),
  orders.order_count AS COUNT(O_ORDERKEY)
);
```

### Step 3: What Just Happened?

You just created a **business-friendly interface** to your data! Now instead of:
- Writing complex JOINs every time
- Remembering that "revenue" means `SUM(O_TOTALPRICE)` 
- Using cryptic column names like `C_CUSTKEY`

Your users can simply ask for "total revenue by customer country" in plain business terms.

## How to Query Semantic Views

### New Semantic SQL Syntax:
```sql
SELECT * FROM SEMANTIC_VIEW(
  view_name
  DIMENSIONS dimension1, dimension2, ...
  METRICS metric1, metric2, ...
)
WHERE condition
ORDER BY column;
```

### Example Queries:

**Question**: "What's our total revenue by country?"
```sql
SELECT * FROM SEMANTIC_VIEW(
  ecommerce_analytics
  DIMENSIONS customers.customer_country
  METRICS orders.total_revenue
);
```

**Question**: "Show me monthly revenue for 2023"
```sql
SELECT * FROM SEMANTIC_VIEW(
  ecommerce_analytics  
  DIMENSIONS orders.order_date
  METRICS orders.total_revenue
)
WHERE order_date >= '2023-01-01' 
  AND order_date < '2024-01-01'
ORDER BY order_date;
```

**Question**: "What's the average order value by country?"
```sql
SELECT * FROM SEMANTIC_VIEW(
  ecommerce_analytics
  DIMENSIONS customers.customer_country  
  METRICS orders.average_order_value
)
ORDER BY average_order_value DESC;
```

### Natural Language with Cortex Analyst:
You can also ask in plain English:
- "Show me total revenue by country"
- "What's our average order value this year?"
- "Which countries have the most customers?"

## Real-World Use Cases

### 1. **Retail Analytics**
- **Dimensions**: product_category, store_location, time_period, customer_segment
- **Metrics**: sales_revenue, profit_margin, inventory_turnover, customer_lifetime_value

### 2. **Healthcare Analytics**  
- **Dimensions**: patient_demographics, treatment_type, hospital_department, diagnosis_code
- **Metrics**: readmission_rate, average_length_of_stay, treatment_cost, patient_satisfaction

### 3. **Financial Services**
- **Dimensions**: account_type, customer_segment, transaction_category, risk_level  
- **Metrics**: total_deposits, loan_default_rate, customer_acquisition_cost, portfolio_return

### 4. **Marketing Analytics**
- **Dimensions**: campaign_type, channel, audience_segment, geographic_region
- **Metrics**: conversion_rate, cost_per_acquisition, return_on_ad_spend, engagement_rate

## Best Practices

### 1. **Start Simple**
- Begin with 3-5 key tables
- Focus on your most important business metrics
- Add complexity gradually

### 2. **Use Business Language**
- Name things how business users talk about them
- Avoid technical jargon in dimension/metric names
- Add descriptions and synonyms

### 3. **Define Metrics Once**
- Create one authoritative definition for each business concept
- Include the business logic in comments
- Make sure stakeholders agree on definitions

### 4. **Plan Your Relationships**
- Understand your data model first
- Define primary keys properly
- Test relationships before going live

### 5. **Document Everything**
- Add comments explaining business logic
- Include synonyms for different terms people might use
- Create user guides for your semantic views

### 6. **Governance**
- Have a clear process for changes
- Version control your semantic views
- Regular reviews with business stakeholders

## Getting Started Checklist

- [ ] **Identify your key business questions**
  - What metrics do people ask for most often?
  - What dimensions do they want to slice by?

- [ ] **Map your physical data model**  
  - Which tables contain the data you need?
  - How do they relate to each other?
  - What are the primary/foreign keys?

- [ ] **Define business terms**
  - Get stakeholders to agree on metric definitions
  - Document the business logic clearly
  - Identify synonyms people might use

- [ ] **Start with a pilot**
  - Choose 2-3 tables to begin with
  - Focus on 5-10 key metrics
  - Test with a small group of users

- [ ] **Iterate and expand**
  - Gather feedback from users
  - Add more tables and metrics based on needs
  - Refine definitions based on real usage

## Summary

Semantic Views in Snowflake are like having a **smart translator** that converts business questions into database queries. They provide:

- **Consistency** - One definition for each business concept
- **Simplicity** - Business users can self-serve without SQL knowledge  
- **Speed** - No more waiting for IT to write complex queries
- **AI-Ready** - Works with Cortex Analyst for natural language queries
- **Governance** - Centralized control over business definitions

Start simple, think in business terms, and remember - you're building a bridge between business questions and data answers!

# Understanding Semantic Views in Snowflake: A Complete Beginner's Guide to Modern Data Analytics
As organizations increasingly rely on data-driven decision making, the complexity of data structures often creates barriers between business users and the insights they need. Semantic views in Snowflake represent a revolutionary approach to solving this fundamental challenge, serving as an intelligent translation layer that converts business questions into precise database queries. This comprehensive guide explores semantic views from first principles, providing beginners with both theoretical understanding and practical implementation knowledge.
## Understanding Semantic Layers: The Foundation Concept
A semantic layer functions as a **business representation layer** that sits between raw data storage systems and end users, translating complex technical data structures into meaningful business concepts. Think of it as a sophisticated translator that enables business users to interact with data using familiar terminology rather than cryptic database schemas.[1][2][3]

### The Core Problem Semantic Layers Solve
Traditional data warehousing approaches create significant barriers between business users and data insights. When organizations store critical business concepts like "gross revenue" in database columns with technical names like `amt_ttl_pre_dsc`, business users struggle to locate and interpret relevant information. Furthermore, without centralized definitions, different teams often develop inconsistent calculations for the same business metric, leading to conflicting reports and erroneous decision-making.[4][5]

### How Semantic Layers Transform Data Access
Semantic layers eliminate these challenges by creating **unified business definitions** that standardize metrics and calculations across the entire organization. Rather than requiring each user to understand complex database schemas and write technical queries, the semantic layer provides a business-friendly interface that automatically handles underlying complexity. This transformation enables **self-service analytics** where business users can explore data independently without requiring technical expertise or constant IT support.[2][6][1]

The semantic layer approach delivers several critical advantages over traditional data access methods. It **eliminates data movement** by querying information directly from source systems, reducing both infrastructure costs and data latency. Organizations typically experience **70% lower infrastructure costs** compared to traditional data warehouse architectures while gaining access to real-time insights. Most importantly, semantic layers create **consistent metrics and KPIs** across all data sources, ensuring that when marketing defines "customer lifetime value," everyone throughout the organization uses identical calculations regardless of underlying data complexity.[7]

## Snowflake Semantic Views: Native Implementation of Semantic Intelligence
Snowflake semantic views represent the platform's native implementation of semantic layer concepts, introduced as **schema-level objects** that store semantic model information directly within the database. Unlike external semantic layer solutions, Snowflake semantic views are **database-native objects** that follow the same security, governance, and access control patterns as traditional tables and views.[8][4]

### Key Architectural Components
Semantic views in Snowflake consist of several essential architectural elements that work together to create a comprehensive business abstraction layer. **Logical tables** provide business-friendly names and aliases for physical database tables, allowing users to work with concepts like "customers" and "orders" rather than cryptic table names. **Relationships** define pre-established connections between logical tables, eliminating the need for users to manually specify complex joins in every query.[9][4]

The semantic view structure incorporates three primary data concept types that mirror real-world business analysis patterns. **Facts** represent row-level attributes that capture specific business events or transactions, such as individual sales amounts or quantities purchased. **Dimensions** provide categorical attributes that answer "who," "what," "where," and "when" questions, enabling users to filter and group data by meaningful business categories. **Metrics** transform raw data into actionable business indicators through aggregation and calculation, representing key performance indicators like total revenue or customer count.[4]

### Integration with Snowflake Ecosystem
Semantic views integrate seamlessly with Snowflake's broader AI and analytics ecosystem, particularly with **Cortex Analyst** for natural language query processing. This integration enables users to ask business questions in plain English, such as "Show me total sales by region for the past quarter," without writing SQL code. The semantic view automatically translates these natural language requests into optimized database queries that leverage the pre-defined business logic and relationships.[8]

The architecture also supports **Semantic SQL**, a specialized query syntax that allows users to reference business concepts directly in SQL statements. This approach provides flexibility for technical users while maintaining the business-friendly abstraction that makes data accessible to non-technical stakeholders.[10][8]

## Practical Implementation: Creating Your First Semantic View
Understanding semantic views requires hands-on experience with their creation and usage. The following comprehensive example demonstrates the complete process of building a semantic view from initial planning through implementation and querying.

### Planning Your Semantic Model
Before creating a semantic view, organizations must carefully design their business data model by identifying key entities, relationships, and metrics. This process begins with understanding what business entities exist in your data (customers, products, orders, transactions) and how these entities relate to each other through foreign key relationships. Organizations should also clearly define which metrics are important to their business and what dimensions they use to analyze these metrics.[4]

### Step-by-Step Implementation Example
Consider a typical e-commerce scenario with customers, orders, and product data stored in traditional database tables with technical naming conventions. The physical tables might include `CUSTOMER_MASTER_TBL` with columns like `C_CUSTKEY` and `C_CUST_NM_TX`, alongside `ORDER_FACT_TBL` containing `O_ORDERKEY`, `O_CUSTKEY`, and `O_TOT_AMT`.[11]

The semantic view creation process transforms this technical complexity into business-friendly concepts:

```sql
CREATE SEMANTIC VIEW ecommerce_analytics
TABLES (
  customers AS CUSTOMER_MASTER_TBL 
    PRIMARY KEY (C_CUSTKEY),
  orders AS ORDER_FACT_TBL 
    PRIMARY KEY (O_ORDERKEY)
)
RELATIONSHIPS (
  orders(O_CUSTKEY) REFERENCES customers(C_CUSTKEY)
)
DIMENSIONS (
  customers.customer_name AS C_CUST_NM_TX,
  customers.customer_region AS C_REGION_CD,
  orders.order_date AS O_ORDER_DT
)
METRICS (
  orders.total_revenue AS SUM(O_TOT_AMT),
  orders.average_order_value AS AVG(O_TOT_AMT),
  customers.customer_count AS COUNT(C_CUSTKEY)
);
```

This semantic view definition establishes business-friendly aliases for physical tables, pre-defines the relationship between customers and orders, creates meaningful dimension names, and establishes consistent metric calculations that can be reused across all analyses.[11]
## Querying Semantic Views: From Complex SQL to Natural Language
Once created, semantic views enable multiple query approaches that cater to different user skill levels and preferences. The **Semantic SQL** approach allows users to reference business concepts directly in SQL statements using specialized syntax.[8]

### Semantic SQL Syntax
The Semantic SQL approach uses a distinctive syntax structure that explicitly separates dimensions (categories for analysis) from metrics (calculated values):

```sql
SELECT * FROM SEMANTIC_VIEW(
  ecommerce_analytics
  DIMENSIONS customers.customer_region, orders.order_date
  METRICS orders.total_revenue, orders.average_order_value
)
WHERE order_date >= '2023-01-01'
ORDER BY total_revenue DESC;
```

This query structure eliminates the need for users to understand table joins, column names, or aggregation logic while still providing the flexibility of SQL for filtering and sorting results.[8]

### Natural Language Integration
Snowflake's integration with **Cortex Analyst** enables users to ask questions in natural language that are automatically translated into semantic SQL queries. Users can ask questions like "What are our top-selling products by region this quarter?" and receive accurate results without writing any code. The semantic view provides the necessary context and definitions that enable Cortex Analyst to generate precise queries and avoid the hallucinations common in AI-powered analytics systems.[12][8]

## Advanced Concepts and Enterprise Applications
### Window Function Metrics and Complex Calculations
Semantic views support sophisticated analytical concepts including **window function metrics** that enable advanced calculations like running totals, rankings, and time-series analyses. These advanced metrics can incorporate complex business logic while maintaining the business-friendly abstraction that makes them accessible to end users.[13]

Window function metrics use specialized syntax that allows partitioning by dimensions or excluding specific dimensions from calculations:

```sql
METRICS (
  orders.running_total_revenue AS SUM(total_revenue) 
    OVER (PARTITION BY customer_region ORDER BY order_date),
  orders.revenue_rank AS RANK() 
    OVER (PARTITION BY customer_region ORDER BY total_revenue DESC)
)
```

This capability enables sophisticated analytical scenarios while maintaining the semantic layer's core benefit of abstracting technical complexity from business users.[13]

### Integration with Business Intelligence Tools
Modern semantic views serve as **universal semantic layers** that can power multiple analytical endpoints simultaneously. Organizations using multiple BI tools like Tableau, Power BI, and Looker can leverage a single semantic view definition to ensure consistent metrics across all platforms. This approach eliminates the traditional problem of "semantic layer sprawl" where different tools develop incompatible definitions for the same business concepts.[14][15][1]

The integration extends beyond traditional BI tools to support **embedded analytics**, **AI agents**, and **custom applications** that require programmatic access to business metrics. This versatility makes semantic views a foundational component of modern data architecture rather than a tool-specific solution.[15][16]

## Real-World Applications and Industry Use Cases
### Healthcare Analytics Implementation
Healthcare organizations leverage semantic views to integrate diverse data sources including electronic health records, lab results, and imaging systems. A typical healthcare semantic view might define logical tables for patients, treatments, diagnoses, and outcomes, with dimensions like patient_demographics, treatment_type, and hospital_department. Key metrics could include readmission_rate, average_length_of_stay, and patient_satisfaction_scores.[17][2]
This integration enables healthcare professionals to access comprehensive patient views through natural language queries like "Show me readmission rates by diagnosis for patients over 65" without requiring technical expertise in database querying.[18]

### Financial Services Risk Management
Financial institutions implement semantic views to transform complex risk management processes that traditionally require months of manual data compilation. A comprehensive risk management semantic view integrates data from multiple legacy applications, defining relationships between risks, controls, policies, and compliance requirements.[18]

The semantic layer enables risk analysts to quickly answer critical questions like "What are the related controls and policies relevant to a given risk in my business?" through intuitive interfaces rather than complex multi-system queries. Organizations report dramatic improvements in efficiency, with comprehensive risk reports that previously required two months now generated in minutes.[18]

### Retail and E-Commerce Analytics
Retail organizations use semantic views to consolidate data from point-of-sale systems, e-commerce platforms, and customer loyalty programs. The semantic layer enables consistent analysis across channels by defining unified metrics for concepts like customer_lifetime_value, inventory_turnover, and cross_sell_effectiveness.[19][2]

Store managers can use natural language queries to monitor inventory levels and sales trends, asking questions like "Which products are trending upward in the Northeast region?" without understanding the underlying data complexity.[2]

## Benefits and Transformation Impact
### Performance and Cost Optimization
Organizations implementing semantic views typically experience **70% reduction in infrastructure costs** compared to traditional data warehouse approaches. This cost reduction stems from eliminating expensive ETL processes and reducing the need for data duplication across systems. The semantic layer approach enables **direct querying** of source systems, eliminating the storage and compute costs associated with maintaining centralized data warehouses.[7]

Query performance improvements are equally significant, with semantic views enabling **sub-second response times** for complex analytical queries through intelligent aggregation and caching strategies. The pre-defined relationships and optimized query patterns built into semantic views eliminate the performance overhead of ad-hoc joins and calculations.[20]

### Organizational Transformation
The implementation of semantic views drives fundamental organizational changes in how teams interact with data. **Self-service analytics** capabilities reduce the burden on technical teams while enabling business users to answer their own questions. This transformation typically reduces ad-hoc data requests to IT teams by 60-80%, allowing technical resources to focus on strategic initiatives rather than repetitive query generation.[5][21]

The standardization of business definitions creates **organizational alignment** around key metrics and KPIs. When everyone uses the same calculation for concepts like "monthly recurring revenue" or "customer acquisition cost," organizations eliminate the confusion and inconsistencies that plague traditional BI implementations.[3][5]

## Implementation Best Practices and Getting Started
### Planning and Design Principles
Successful semantic view implementation begins with **collaborative design sessions** involving both business stakeholders and technical teams. Organizations should start by identifying the 5-10 most critical business questions that require data analysis, then work backwards to understand the required metrics, dimensions, and data sources.

The design process should prioritize **business language** over technical precision, using terminology that matches how stakeholders naturally discuss their work. Semantic views should include comprehensive synonyms and descriptions to accommodate different ways people might reference the same concepts.[9]

### Phased Implementation Approach
Organizations should adopt a **pilot-first strategy** that

[1] https://www.atscale.com/glossary/semantic-layer/
[2] https://www.ibm.com/think/topics/semantic-layer
[3] https://www.gooddata.com/blog/what-is-a-semantic-layer/
[4] https://docs.snowflake.com/en/user-guide/views-semantic/overview
[5] https://www.getdbt.com/blog/semantic-layer-introduction
[6] https://www.databricks.com/glossary/semantic-layer
[7] https://www.knowi.com/blog/why-semantic-layers-are-replacing-traditional-data-warehouses-in-2025/
[8] https://www.snowflake.com/en/engineering-blog/native-semantic-views-ai-bi/
[9] https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/semantic-model-spec
[10] https://docs.snowflake.com/en/user-guide/views-semantic/querying
[11] https://docs.snowflake.com/en/user-guide/views-semantic/example
[12] https://quickstarts.snowflake.com/guide/snowflake-semantic-view/index.html
[13] https://docs.snowflake.com/en/sql-reference/sql/create-semantic-view
[14] https://www.sigmacomputing.com/blog/snowflake-semantic-views-launch
[15] https://cube.dev/blog/business-intelligence-with-universal-semantic-layer
[16] https://hex.tech/blog/introducing-snowflake-semantic-sync-aisql/
[17] https://www.castordoc.com/ai-strategy/semantic-data-real-world-examples-and-applications
[18] https://enterprise-knowledge.com/top-semantic-layer-use-cases-and-applications-with-realworld-case-studies/
[19] https://datavid.com/blog/semantic-data-model-examples
[20] https://solutionsreview.com/business-intelligence/semantic-intelligence-the-missing-layer-in-scalable-ai-and-bi-systems/
[21] https://www.lightdash.com/blogpost/what-is-semantic-bi
[22] https://docs.snowflake.com/en/user-guide/views-semantic/validation-rules
[23] https://docs.snowflake.com/en/release-notes/2025/other/2025-04-17-semantic-views
[24] https://www.reddit.com/r/snowflake/comments/1ldo4ui/semantic_model_vs_semantic_view/
[25] https://hakkoda.io/resources/semantic-layer-in-snowflake/
[26] https://www.youtube.com/watch?v=V6RshK2twis
[27] https://www.atscale.com/blog/getting-started-with-a-semantic-layer-with-snowflake/
[28] https://docs.snowflake.com/en/sql-reference/sql/desc-semantic-view
[29] https://hevodata.com/learn/getting-started-with-snowflake-semantic-layer/
[30] https://docs.snowflake.com/en/sql-reference/sql/show-semantic-views
[31] https://www.reddit.com/r/snowflake/comments/1kgubfo/snowflake_releases_semantic_views_towards_a/
[32] https://www.linkedin.com/posts/vrainardi_snowflake-datawarehouse-dataanalysis-activity-7339908234180255744-bgO6
[33] https://docs.getdbt.com/guides/sl-snowflake-qs
[34] https://intone.com/the-role-of-semantic-data-modeling-in-modern-data-management/
[35] https://enterprise-knowledge.com/the-top-3-ways-to-implement-a-semantic-layer/
[36] https://www.gooddata.com/blog/what-a-semantic-data-model/
[37] https://omni.co/blog/bi-semantic-layer-on-top-of-dbt
[38] https://www.actian.com/semantic-data-model/
[39] https://www.dataversity.net/data-catalog-semantic-layer-data-warehouse-the-three-key-pillars-of-enterprise-analytics/
[40] https://en.wikipedia.org/wiki/Semantic_data_model
[41] https://tabulareditor.com/blog/semantic-models-in-simple-terms
[42] https://www.reddit.com/r/BusinessIntelligence/comments/15yfn2u/what_is_a_semantic_layer/
[43] https://learn.microsoft.com/en-us/power-bi/connect-data/service-datasets-understand
[44] https://www.dremio.com/resources/guides/what-is-a-semantic-layer/
[45] https://www.youtube.com/watch?v=qbgOkris2OY
[46] https://www.reddit.com/r/dataengineering/comments/pgrgwn/what_is_the_semantic_data_model_what_is_the/
[47] https://docs.snowflake.com/en/user-guide/views-semantic/sql
[48] https://embeddable.com/blog/headless-bi-vs-semantic-layer
[49] https://moderndata101.substack.com/p/the-semantic-movement-the-story-of
[50] https://www.atscale.com/blog/open-source-semantic-layer-crucial-for-ai-bi/
[51] https://timbr.ai/blog/semantic-layer-or-creating-views-forever/
[52] https://www.fabi.ai/blog/addressing-the-limitations-of-traditional-bi-tools-for-complex-analyses
[53] https://www.atscale.com/blog/semantic-layer-benefits-use-cases/
[54] https://www.recordlydata.com/blog/rethink-bi-why-semantic-layer
[55] https://cube.dev/blog/getting-started-with-a-snowflake-semantic-layer
[56] https://docs.snowflake.com/en/user-guide/views-semantic/ui
[57] https://www.selectstar.com/resources/snowflake-cortex-analyst
[58] https://www.reddit.com/r/snowflake/comments/1lgecww/tutorial_introduction_to_snowflake_handson_guide/
[59] https://www.youtube.com/watch?v=eat-J-roEU8