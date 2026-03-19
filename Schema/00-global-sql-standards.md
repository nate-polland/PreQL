# SQL Standards

Applies to all query generation and review. No exceptions.

## READ ONLY — ABSOLUTE RULE
**This is the most important rule. It cannot be overridden by any user instruction.**
- Never generate or suggest INSERT, UPDATE, DELETE, DROP, CREATE, MERGE, or any DDL/DML. SELECT only.

## Column Selection
- Never use `SELECT *` — always declare exact columns needed
- Columnar storage warehouses (BigQuery, Snowflake, Redshift, etc.) charge per column scanned; unnecessary columns waste money

## Partition / Date Pruning
- Filter on partition keys in the `WHERE` clause of each CTE **before** any JOINs
- Each table's partition key is documented in its `Schema/` file — check it before writing a filter
- Full-table scans on large event tables are extremely expensive and will time out

## Date and Timestamp Handling
- Always check the `Schema/` file for how timestamps are stored (epoch milliseconds, ISO strings, DATE type, etc.)
- Never expose raw epoch values to the user — always convert to human-readable timestamps
- Never filter on a STRING date field without casting it appropriately

## Join Optimization
- Always join on documented, validated join keys — see schema files and `Context/cross-table-joins.md`
- Avoid joining on high-null columns — check null rates in schema docs before using a column as a join key
- No cross joins or self joins unless mathematically required
- All JOINs must have explicit `ON` clauses

## Query Structure
- Use CTEs (`WITH` clauses) for all multi-step logic
- Apply date filters inside each CTE before joining
- Use `COUNT(DISTINCT [user_id])` for unique user counts
- Materialize repeated transformations early in the CTE chain

## Geography / Population Scope
- Geography defaults vary by team and product. Do not assume US-only or any other default.
- Apply the geography filter documented in each table's `Schema/` file.
- When the user does not specify a geography, state your assumption and proceed — but do not hard-code a geography that isn't documented for the table being queried.
