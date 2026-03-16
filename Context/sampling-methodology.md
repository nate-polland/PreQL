# Sampling Methodology

## When to Sample
- Any query touching BigEvent (BE) — always sample first
- Any cross-table join not yet documented in `cross-table-joins.md`
- Any new field, filter, or pattern not previously validated

## How to Sample

### Time-Window Sampling (default)
Use a 1-hour or 1-day `ts` window on BE. This is the cheapest way to validate shape, null rates, and filter behavior.

```sql
-- 1-hour sample on BE
WHERE ts BETWEEN TIMESTAMP_MILLIS(UNIX_MILLIS(TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)))
  AND TIMESTAMP_MILLIS(UNIX_MILLIS(CURRENT_TIMESTAMP()))
```

For non-BE tables, use a 1-day partition filter (`activitydate`, `clickdate`).

### Row-Limited Sampling (for variant comparisons)
When comparing groups (e.g., Darwin variants), sample a fixed number per group to validate join logic before scaling:

```sql
-- 500 users per variant
SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY groupName ORDER BY numericId) AS rn
  FROM darwin_table
  WHERE first_bin_flag = true AND reseed_flag = 0
) WHERE rn <= 500
```

### TABLESAMPLE (last resort)
BigQuery's `TABLESAMPLE SYSTEM (N PERCENT)` is non-deterministic and doesn't respect partition pruning well. Prefer time-window sampling. Use TABLESAMPLE only when you need a random cross-section of unpartitioned data.

## Workflow
1. Run the sample query
2. Check: Does the filter return data? What's the row count? Null rates on join keys?
3. Report findings to user: "Sample returned X rows. [Key finding]. Proceeding with full query."
4. Only then scale to full time window

## Cost Guardrails
- BE queries without `ts` filter will scan terabytes. Never run one.
- FDMA full-history scans (e.g., `MAX(activitydate)` across all time) are unavoidable for some segment queries but expensive. Warn the user these will be slow.
- Multi-day BE joins to FTEE/FTRE: sample 1 day first, then scale.
