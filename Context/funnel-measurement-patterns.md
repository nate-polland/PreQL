# Funnel Measurement Patterns

Generic SQL patterns for measuring documented funnels. Refer to the relevant `Funnels/` doc for the entry filter, completion anchor, stitch key, session window, and step names before applying these templates.

---

## Pattern 1 — Point-in-Time Conversion (Sequential Event Table)

Use when the source is a sequential event table (one row per event with timestamps). Anchors on session start date.

```sql
-- Step 1: Entry population — all sessions that started the funnel in the date range
WITH entry_sessions AS (
  SELECT
    [stitch_key],                        -- e.g., user_cookieId for cross-auth funnels
    MIN(ts) AS session_start_ts,
    DATE(MIN(ts)) AS cohort_date
  FROM [event_table]
  WHERE DATE(ts) BETWEEN '[start]' AND '[end]'
    AND [entry_screen_filter]            -- e.g., content_screen = 'seamless-registration'
    AND [entry_population_filter]        -- e.g., request_refUrl LIKE '%chatgpt%'
  GROUP BY 1
),

-- Step 2: For each session, determine which funnel steps were reached
session_steps AS (
  SELECT
    e.[stitch_key],
    e.cohort_date,
    MAX(CASE WHEN ev.[step_A_condition] THEN 1 ELSE 0 END) AS reached_step_A,
    MAX(CASE WHEN ev.[step_B_condition] THEN 1 ELSE 0 END) AS reached_step_B,
    -- ... add one line per step
    MAX(CASE WHEN ev.[completion_condition] THEN 1 ELSE 0 END) AS completed
  FROM entry_sessions e
  JOIN [event_table] ev
    ON ev.[stitch_key] = e.[stitch_key]
    AND ev.ts BETWEEN e.session_start_ts
                  AND TIMESTAMP_ADD(e.session_start_ts, INTERVAL [window_minutes] MINUTE)
    AND DATE(ev.ts) BETWEEN '[start]' AND DATE_ADD('[end]', INTERVAL 1 DAY)  -- +1 day buffer
  GROUP BY 1, 2
)

-- Step 3: Funnel counts
SELECT
  COUNT(*)                                              AS entered_funnel,
  SUM(reached_step_A)                                  AS reached_step_A,
  SUM(reached_step_B)                                  AS reached_step_B,
  SUM(completed)                                       AS completed,
  ROUND(SUM(reached_step_A) / COUNT(*), 3)             AS step_A_rate,
  ROUND(SUM(reached_step_B) / SUM(reached_step_A), 3) AS step_A_to_B_rate,
  ROUND(SUM(completed) / COUNT(*), 3)                  AS overall_conversion
FROM session_steps
```

**Notes:**
- Use `completed` in the denominator for cross-step rates only when measuring "of those who reached A, how many reached B"
- For cross-auth funnels: gate stitch key on `COUNT(DISTINCT numericId) = 1` per stitch key before joining (see `Context/cross-table-joins.md`)
- Always add at least 1 day of buffer on the event join date range to catch sessions that span midnight

---

## Pattern 2 — Time-Series / Weekly Trend

Extend Pattern 1 by grouping on `cohort_date`. Anchor on **session start date**, not completion date — this gives stable weekly cohorts even if some sessions complete the next day.

```sql
-- After session_steps CTE from Pattern 1:
SELECT
  DATE_TRUNC(cohort_date, WEEK)                          AS cohort_week,
  COUNT(*)                                               AS entered_funnel,
  SUM(reached_step_A)                                    AS reached_step_A,
  SUM(completed)                                         AS completed,
  ROUND(SUM(completed) / NULLIF(COUNT(*), 0), 3)        AS conversion_rate
FROM session_steps
GROUP BY 1
ORDER BY 1
```

**Caveat:** The most recent partial week will have incomplete conversion — note this in results. Use `DATE_TRUNC(CURRENT_DATE(), WEEK)` as a cutoff or flag the partial week explicitly.

---

## Pattern 3 — Dropoff Classification

Identifies where non-completers exited and whether it was organic (quit on an impression) or a disappearance (last event was an action — submitted/clicked but next screen never fired).

```sql
-- After session_steps CTE, add:
non_completers AS (
  SELECT e.[stitch_key]
  FROM entry_sessions e
  JOIN session_steps s USING ([stitch_key])
  WHERE s.completed = 0
),

last_events AS (
  SELECT
    e.[stitch_key],
    ev.content_screen   AS last_screen,
    ev.system_eventType AS last_event_type,   -- 1/4 = impression, 2/3 = action
    ROW_NUMBER() OVER (PARTITION BY e.[stitch_key] ORDER BY ev.ts DESC) AS rn
  FROM non_completers e
  JOIN [event_table] ev
    ON ev.[stitch_key] = e.[stitch_key]
    AND ev.ts BETWEEN ...  -- same window as session_steps
)

SELECT
  last_screen,
  CASE
    WHEN last_event_type IN (1, 4) THEN 'organic_dropout'  -- saw screen, left
    WHEN last_event_type IN (2, 3) THEN 'disappearance'    -- acted, next screen never fired
  END AS dropout_type,
  COUNT(*) AS users,
  ROUND(COUNT(*) / SUM(COUNT(*)) OVER (), 3) AS pct_of_dropoffs
FROM last_events
WHERE rn = 1
GROUP BY 1, 2
ORDER BY users DESC
```

---

## Pattern 4 — Multi-Path Funnel (Separate + Rollup)

When a funnel has distinct user paths (e.g., returning vs. new users), measure each path separately first, then roll up to total. Mixing paths in a single query loses visibility into where each segment drops.

```sql
-- Identify path at the session_steps level using a distinguishing signal:
session_steps AS (
  SELECT
    e.[stitch_key],
    e.cohort_date,
    -- Path classifier — use a screen that's exclusive to one path
    MAX(CASE WHEN ev.content_screen = '[path_A_exclusive_screen]' THEN 1 ELSE 0 END) AS is_path_A,
    MAX(CASE WHEN ev.[step_condition] THEN 1 ELSE 0 END) AS reached_step,
    MAX(CASE WHEN ev.[completion_condition] THEN 1 ELSE 0 END) AS completed
  FROM entry_sessions e
  JOIN [event_table] ev ON ...
  GROUP BY 1, 2
)

-- Per-path view:
SELECT
  CASE WHEN is_path_A = 1 THEN 'Path A' ELSE 'Path B / Other' END AS path,
  COUNT(*) AS entered,
  SUM(completed) AS completed,
  ROUND(SUM(completed) / COUNT(*), 3) AS conversion_rate
FROM session_steps
GROUP BY 1

UNION ALL

-- Rollup:
SELECT 'Total' AS path, COUNT(*), SUM(completed), ROUND(SUM(completed)/COUNT(*),3)
FROM session_steps
```

---

## Pattern 5 — Pre-Aggregated Table Funnel Counts

For tables with binary flags per user (one row per user, no timestamps). Shows population-level step coverage but cannot give ordering or timing.

```sql
SELECT
  COUNT(*)                                          AS total_users,
  SUM([step_A_flag])                                AS reached_step_A,
  SUM([step_B_flag])                                AS reached_step_B,
  SUM([completion_flag])                            AS completed,
  ROUND(SUM([step_A_flag]) / COUNT(*), 3)           AS step_A_rate,
  ROUND(SUM([completion_flag]) / COUNT(*), 3)       AS overall_conversion
FROM [summary_table]
WHERE [date_filter]
  AND [population_filter]
```

**Limitation:** Cannot distinguish path order or classify organic vs. disappearance dropout — go to the underlying event table for that.

---

## Pattern 6 — Statistical Significance for Conversion Rate (A/B Test)

For binary KPIs (converted: yes/no), use a two-proportion z-test. Run this in Python after pulling counts from BigQuery.

**Step 1 — Pull counts from BQ** (using Pattern 1 or 4, split by experiment arm):
```sql
SELECT
  arm,
  COUNT(*)        AS n,
  SUM(completed)  AS completers
FROM session_steps
JOIN [darwin_table] d ON [stitch_key] = d.numericId
  AND first_bin_flag = true AND reseed_flag = 0
GROUP BY arm
```

**Step 2 — Run z-test in Python:**
```python
from scipy import stats
import numpy as np

# Inputs from BQ results
n_control   = ...   # total entered funnel, control arm
n_test      = ...   # total entered funnel, test arm
c_control   = ...   # completers, control arm
c_test      = ...   # completers, test arm

p_control = c_control / n_control
p_test    = c_test    / n_test

stat, p_value = stats.proportions_ztest(
    [c_test, c_control],
    [n_test, n_control],
    alternative='two-sided'   # change to 'larger'/'smaller' if directional hypothesis
)

# 95% confidence interval on the difference
diff = p_test - p_control
se   = np.sqrt(p_control*(1-p_control)/n_control + p_test*(1-p_test)/n_test)
ci_lower, ci_upper = diff - 1.96*se, diff + 1.96*se

alpha = 0.05  # adjust as needed

print(f"Control: {p_control:.1%} ({n_control:,} users)")
print(f"Test:    {p_test:.1%} ({n_test:,} users)")
print(f"Lift:    {diff:+.1%} ({diff/p_control:+.1%} relative)")
print(f"95% CI:  [{ci_lower:+.1%}, {ci_upper:+.1%}]")
print(f"p-value: {p_value:.4f} → {'SIGNIFICANT' if p_value < alpha else 'not significant'} at α={alpha}")
print()

# Plain-English conclusion
if p_value < alpha:
    print(
        f"CONCLUSION: The test arm converted at {p_test:.1%} vs {p_control:.1%} in control "
        f"(a {diff:+.1%} difference). This result IS statistically significant (p={p_value:.3f}). "
        f"We are 95% confident the true effect is between {ci_lower:+.1%} and {ci_upper:+.1%}. "
        f"{'The entire CI is above zero, so the direction of the effect is reliable.' if ci_lower > 0 else 'The CI crosses zero, so while significant, the direction of the true effect is uncertain — interpret cautiously.'}"
    )
else:
    print(
        f"CONCLUSION: The test arm converted at {p_test:.1%} vs {p_control:.1%} in control "
        f"(a {diff:+.1%} difference). This result is NOT statistically significant (p={p_value:.3f}). "
        f"The 95% confidence interval [{ci_lower:+.1%}, {ci_upper:+.1%}] includes zero, meaning the "
        f"observed difference could plausibly be due to chance. We cannot conclude the test arm "
        f"performs differently — more data or a longer run is needed before making a decision."
    )
```

**Before running — confirm with user:**
- Significance threshold (default α = 0.05)
- One-tailed or two-tailed (default: two-tailed; use one-tailed only if hypothesis is directional)
- Multiple KPIs being tested simultaneously? If yes, apply Bonferroni correction: `alpha_adjusted = alpha / n_tests`

**Caveats:**
- Requires clean arm separation — never mix users across arms
- Darwin `cookieId` and `deviceId` columns are **NULL for USER-type experiments** (validated on mt_final_71788 — 100% null). For standard USER-type experiments, the join is `numericId` only, meaning the experiment population is inherently post-auth. For funnels starting unauthenticated, this creates a survivorship bias in the denominator — the experiment can only measure users who authenticated. Check `testType` on the Darwin table before assuming pre-auth identifiers are available.
- Partial experiment periods (ramping up or recently ended) require date filtering to a stable ramp window

---

## General Rules

- **Always anchor on session start date** for cohort measurement, not completion date
- **Always add 1-day buffer** on event table joins to catch sessions spanning midnight
- **Never mix completers and non-completers in the same step count** — entry population is the denominator; completers are a subset
- **For cross-auth funnels:** apply the 1:1 cardinality gate on the stitch key before all joins (Pattern 1 note above)
- **Partial periods:** always flag the most recent week/day as potentially incomplete in results
- **Large event table joins:** use async script — refer to `CLAUDE.md` for path and usage
