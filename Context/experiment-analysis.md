# Experiment Analysis: Query Conventions

## Step 0: Check Experiment Status First

Always run a status check before writing any analysis query:

```sql
SELECT
  testName,
  testType,
  rampStartDate,
  rampEndDate,    -- NULL = experiment still live
  COUNT(*) AS total_users,
  COUNT(DISTINCT groupName) AS num_variants,
  STRING_AGG(DISTINCT groupName ORDER BY groupName) AS variant_names
FROM [experiment_table]
GROUP BY 1, 2, 3, 4
```

- `rampEndDate IS NULL` → experiment still live; use `CURRENT_DATE()` or user-specified cutoff as upper bound
- Check for any reseeding or reassignment flags documented in the schema

## Required Clarifying Questions

1. **Experiment ID** — required; never query without it
2. **Which ramp / phase?** — single final ramp (most common) or combined?
3. **Metric type** — revenue, clicks, engagement, or experiment-only?
4. **Post-filters** — any additional population restrictions? Ask before including.

## Join Keys

Refer to `Context/cross-table-joins.md` for validated join keys between your experiment table and outcome tables (revenue, events, etc.).

## Standard Filters

Apply filters documented in the experiment table's `Schema/` file. Common examples:
```sql
WHERE first_bin_flag = true    -- or equivalent "clean assignment" flag
  AND reseed_flag = 0          -- exclude reassigned users if applicable
```

Check your experiment table's schema — filter names vary by platform.

## Metric Normalization

Always divide by user count — group sizes vary by ramp %. Never compare raw sums between variants.

## Revenue Date Window (Experiment → Revenue)

Apply per-vertical aging buffer from `Context/revenue-aging.md`:
- Closed experiment: add aging buffer to `rampEndDate`
- Live experiment: use `CURRENT_DATE()` or user-specified cutoff; caveat revenue as incomplete

## Sanity Check (always include with results)

```sql
SELECT
  groupName,
  [platform_field],
  COUNT(*) AS users,
  ROUND(COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY groupName), 3) AS pct
FROM [experiment_table]
WHERE [standard_filters]
GROUP BY 1, 2
```

**Red flag:** >2–3pp difference in platform or key demographic between variants → possible assignment bug.

## Pre-Auth vs Post-Auth Experiments

- **Post-auth experiments** (bucketed by authenticated user ID): joining to outcome tables is straightforward on the user ID.
- **Pre-auth experiments** (bucketed by cookie or device ID): authenticated-user joins only work after the user authenticates. The experiment denominator may be larger than what can be matched to outcome tables. Document this caveat when reporting.

Always check what identifier type was used for bucketing before writing join queries.

## Funnel Experiments

For experiments that modify a product funnel, see `Context/funnel-experiments.md`. Funnel-based experiments require per-arm funnel queries, not just metric joins.
