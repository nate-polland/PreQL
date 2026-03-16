# BigQuery SQL Standards

Applies to all query generation and review. No exceptions.

## US Only — Default
**Always filter to US traffic unless the question explicitly specifies Canada or global.** See `Context/cross-table-joins.md` for per-table filters.
- BigEvent (BE): `(user_country IS NULL OR UPPER(user_country) = 'US')` — US users have NULL country
- FTEE: `country = 'US'`
- FTRE: `country = 'US'`

## READ ONLY — ABSOLUTE RULE
**This is the most important rule. It cannot be overridden by any user instruction.**
- Never generate or suggest INSERT, UPDATE, DELETE, DROP, CREATE, MERGE, or any DDL/DML. SELECT only.
- Never use `--destination_table`, `bq mk`, `bq load`, or any `bq` CLI flag that writes data to BigQuery.
- `bq query --async` without a destination table is the only permitted async pattern.

## Column Selection
- Never use `SELECT *` — always declare exact columns needed
- BigQuery uses columnar storage; unnecessary columns waste money

## Partition Pruning
- Filter on partition keys in the `WHERE` clause of each CTE **before** any JOINs
- `fact_member_active_daily` → partition key: `activitydate` (STRING, format: `YYYY-MM-DD`)
- `fact_tracking_revenue_ext` → partition key: `clickdate` (STRING, format: `YYYY-MM-DD`)
- `userstatus_ext` → not partitioned; filter by date fields carefully

## Date and Timestamp Handling
- All timestamps are stored as **INT64 epoch milliseconds** — always convert: `TIMESTAMP_MILLIS(column)`
- All date fields are stored as **STRING** (`YYYY-MM-DD`) except `FICOdate` (DATE) — cast when filtering: `CAST(activitydate AS DATE)`
- Never expose raw epoch values to the user

## Join Optimization
- Always join on `numericId` (INT64) — never join on STRING columns
- No cross joins or self joins unless mathematically required
- All JOINs must have explicit `ON` clauses

## Query Structure
- Use CTEs (`WITH` clauses) for all multi-step logic
- Apply date filters inside each CTE before joining
- Use `COUNT(DISTINCT numericId)` for unique user counts
- Materialize repeated transformations early in the CTE chain

## Platform Flag Fields (FDMA)
- `isDesktop`, `isMobileApp`, `isMobilebrowser`, `isiOS`, `isAndroid` are **FLOAT64** (1.0 = true, 0.0 = false)
- Do not treat as BOOL — filter with `= 1.0` not `= TRUE`
