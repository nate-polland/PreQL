# Darwin: Query Conventions

## Step 0: Check Experiment Status First

Always run this before writing any analysis query:

```sql
SELECT testName, testType, rampStartDate, rampEndDate,
  COUNT(*) AS total_users,
  COUNTIF(reseed_flag = 1) AS reseeded_users,
  COUNT(DISTINCT groupName) AS num_variants,
  STRING_AGG(DISTINCT groupName ORDER BY groupName) AS variant_names
FROM `prod-ck-abl-data-53.dwdarwinviews_standard.mt_final_{ID}`
GROUP BY 1, 2, 3, 4
```

- `rampEndDate IS NULL` → experiment still live; use `CURRENT_DATE()` or user-specified cutoff as upper bound
- `reseed_flag > 0` → warn user; analyze pre/post separately or confirm to exclude reseeded users

## Required Clarifying Questions

1. **Experiment ID** — required; never query without it
2. **Which ramp?** — single final ramp (most common) or all ramps combined?
3. **Metric type** — revenue (→ FTRE), clicks (→ FTEE), engagement (→ FDMA), or Darwin-only?
4. **Post-filters** — apply `inPostFilter = 1`? Ask before including.

## Join Keys

| Field | Type | Notes |
|---|---|---|
| `numericId` | INT64 | Always populated for `testType = 'USER'` experiments. Join to BigEvent, FTRE, FTEE, matchedMembers. |
| `cookieId` | STRING | NULL for `testType = 'USER'` experiments (validated on mt_final_71788 — 100% null). Likely populated only for cookie-based experiment types. **Do not assume available.** |
| `deviceId` | STRING | Same as cookieId — NULL for USER-type experiments. |

**For funnels that start unauthenticated:** Darwin joins on `numericId` only (for USER-type experiments), meaning the experiment population is inherently post-auth. Use the session stitching pattern in `Context/cross-table-joins.md` to bridge pre-auth BigEvent events — but the experiment denominator will be auth users only, not full funnel entrants. Check `testType` before assuming `cookieId`/`deviceId` are available.

## Standard Filters

```sql
WHERE first_bin_flag = true
  AND reseed_flag = 0
-- Add: AND rampId = '<id>' for a specific ramp
```

## Metric Normalization

Always divide by user count — group sizes vary by ramp %. Never compare raw sums.

## Revenue Date Window (Darwin → FTRE)

Apply per-vertical aging buffer from `Context/revenue-aging.md`:
- Closed experiment: `DATE_ADD(DATE(rampEndDate), INTERVAL <aging_days> DAY)`
- Live experiment: `CURRENT_DATE()` or user-specified cutoff; caveat revenue as incomplete

## Post-Filter Fields

`inPostFilter`, `inProductUserFacts`, `inUserFeatures` — experiment-specific, configured by the experiment owner. Values are 0/1. Only apply if the experiment owner confirms a post-filter was set up; otherwise these fields are 0 for all users. Always ask before including.

## Sanity Check (always include with results)

```sql
SELECT
  groupName,
  platform_at_binning,
  CASE WHEN score_at_binning < 600 THEN 'Subprime'
       WHEN score_at_binning < 660 THEN 'Near-prime'
       ELSE 'Prime' END AS score_tier,
  COUNT(*) AS users,
  ROUND(COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY groupName), 3) AS pct
FROM `prod-ck-abl-data-53.dwdarwinviews_standard.mt_final_{ID}`
WHERE first_bin_flag = true AND reseed_flag = 0
GROUP BY 1, 2, 3
```

**Red flag:** >2–3pp difference in score tier or platform between variants → possible assignment bug.

## Key Dimensions

`platform_at_binning`, score tier, `vertical` (from FTRE/FTEE), cohort week

## Funnel Experiments

For experiments that modify a product funnel (entry point, screen changes, path changes), see the Experiment Overlay section in the `funnel-discovery` skill. Funnel-based experiments require per-arm funnel queries, not just metric joins — the Darwin join pattern above still applies for population splitting.
