# Sampling Methodology

## When to Sample
- Any query touching a large event table — always sample first
- Any cross-table join not yet documented in `Context/cross-table-joins.md`
- Any new field, filter, or pattern not previously validated

## How to Sample

### Time-Window Sampling (default)
Use a 1-hour or 1-day partition window on large event tables. This is the cheapest way to validate shape, null rates, and filter behavior.

```sql
-- 1-day sample using the table's partition key
WHERE [partition_key] = '[recent_date]'
```

For very large event tables with timestamp-level partitioning:
```sql
-- 1-hour sample
WHERE [ts_field] BETWEEN TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)
                     AND CURRENT_TIMESTAMP()
```

For non-event tables, use a 1-day partition filter on the table's documented partition key.

### Row-Limited Sampling (for variant comparisons)
When comparing groups (e.g., experiment variants), sample a fixed number per group to validate join logic before scaling:

```sql
-- 500 users per variant
SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY groupName ORDER BY [user_id]) AS rn
  FROM [experiment_table]
  WHERE [standard_filters]
) WHERE rn <= 500
```

### TABLESAMPLE (last resort)
Many warehouses support `TABLESAMPLE SYSTEM (N PERCENT)` — but it is non-deterministic and doesn't respect partition pruning well. Prefer time-window sampling. Use TABLESAMPLE only when you need a random cross-section of unpartitioned data.

## Workflow
1. Run the sample query
2. Check: Does the filter return data? What's the row count? Null rates on join keys?
3. Report findings to user: "Sample returned X rows. [Key finding]. Proceeding with full query."
4. Only then scale to full time window

## Cost Guardrails
- Large event table queries without a partition filter will scan enormous amounts of data. Never run one.
- Full-history scans (e.g., `MAX(date)` across all time) are unavoidable for some segment queries but expensive. Warn the user these will be slow.
- Multi-day event table joins to other tables: sample 1 day first, then scale.
