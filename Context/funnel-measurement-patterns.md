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
- **Session window buffer:** `+1 day` is sufficient when completion happens during authentication (e.g., a consent click). For funnels where completion is a downstream product screen reached after authentication and a credit pull (e.g., a loan marketplace page), extend to `+3 days` — the post-auth sequence can span multiple sessions if the user returns. Check the funnel doc's `## Session Window` section for the validated buffer.

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

## Pattern 7 — Cross-Funnel Cohort Classification

Classifies each funnel entrant into a user-type cohort based on which signal screens they hit, then measures per-cohort conversion. Useful for understanding funnel mix across time periods or between funnels.

**Three cohorts (auth funnels):**
- **🔵 Phone match:** recognized at OTP → skips PII and TOS entirely (ChatGPT: 66.4% of OTP users; LBE: <1%)
- **🟠 PII/credential match:** existing user identified via email (DUP_EMAIL) or Prove without TOS — routed to login
- **🟢 New user:** hit `termsContinue` (TOS acceptance = net-new account)
- **Bouncer:** no classification signal, no completion

**Priority order:** 🔵 > 🟠 > 🟢 > Bouncer. Apply as a CASE WHEN chain.

```sql
WITH entries AS (
  SELECT user_cookieId, MIN(DATE(ts)) AS entry_date, '[funnel_label]' AS funnel
  FROM `[event_table]`
  WHERE DATE(ts) BETWEEN '[start]' AND '[end]'
    AND [entry_filter]
  GROUP BY user_cookieId
  -- UNION ALL additional funnels with different date windows here
),

screens AS (
  SELECT e.user_cookieId, e.funnel,
    -- 🔵 Phone match: OTP recognized → skips PII entirely (no personalInfo, no login, no TOS)
    MAX(CASE WHEN be.system_eventCode = 'phoneVerificationContinue'
              AND NOT EXISTS (SELECT 1 FROM ...) THEN 1 ELSE 0 END) AS phone_match,
    -- 🟠 PII/cred: hit email-recognition or login screens
    MAX(CASE WHEN be.content_screen LIKE 'login%' OR be.content_screen LIKE 'ump%'
              OR be.system_eventCode = 'duplicateEmailRedirectToLogin' THEN 1 ELSE 0 END) AS saw_login,
    -- 🟢 New user: TOS acceptance
    MAX(CASE WHEN be.system_eventCode = 'termsContinue'              THEN 1 ELSE 0 END) AS saw_tos,
    MAX(CASE WHEN [completion_condition]                              THEN 1 ELSE 0 END) AS completed
  FROM entries e
  JOIN `[event_table]` be
    ON be.user_cookieId = e.user_cookieId
    AND DATE(be.ts) BETWEEN e.entry_date AND DATE_ADD(e.entry_date, INTERVAL 3 DAY)
  WHERE DATE(be.ts) BETWEEN '[earliest_entry_start]' AND '[latest_entry_end_plus_3d]'  -- static partition filter
  GROUP BY e.user_cookieId, e.funnel
),

classified AS (
  SELECT *,
    CASE
      WHEN saw_login   = 1 AND saw_tos = 0 THEN 'phone_match_🔵'
      WHEN saw_login   = 1                 THEN 'pii_cred_match_🟠'
      WHEN saw_tos     = 1                 THEN 'new_user_🟢'
      ELSE 'bouncer'
    END AS cohort
  FROM screens
)

SELECT funnel, cohort,
  COUNT(*)                                                              AS users,
  ROUND(COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY funnel) * 100, 1) AS pct_of_funnel,
  COUNTIF(completed = 1)                                               AS completers,
  ROUND(SAFE_DIVIDE(COUNTIF(completed = 1), COUNT(*)) * 100, 1)       AS conv_pct
FROM classified
GROUP BY funnel, cohort
ORDER BY funnel, cohort
```

**NOTE: Prefer math over running this query when flowchart step counts are available.** See "Math-First Cohort Estimation" below.

**Multi-funnel note:** When using UNION ALL across funnels with different date windows, the static partition filter in the `screens` join must span all windows combined (e.g., `BETWEEN '2025-09-01' AND '2026-03-15'`). If windows are far apart, split into separate queries per time period — a single 6-month scan is expensive.

**Bouncer sub-segmentation (proxy only):** Bouncers have no clean cohort signal, but can be roughly typed by last screen:
- Saw `personalInfo` impression → likely new-user analog
- Saw `phoneInfoContinueSubmitError` → likely phone match analog (phone already registered)
- Reached OTP but dropped → apply OTP-signal cohort split as a proxy

Label these estimates as proxies in any output — they are inferred, not directly measured.

**Validated findings (Mar 2026):**
- ChatGPT: ~73% of OTP users are 🔵 phone match → drives 65% overall CVR
- LBE funnels: 🔵 phone match is <1%; 70–78% are bouncers → ceiling on overall CVR
- 🟢 new users convert at ~62–98% when the path works; LBE Intuit Sep '25 0% was a `proveVerificationPending` bug (fixed Mar '26)
- CK-origin matchFailed rate is 18% of entry (vs ~2–4% for other LBE funnels) — largest single drop opportunity

---

## Math-First Cohort Estimation

When a funnel doc has documented step counts, **derive cohort splits mathematically** rather than running a query. Run a query only when a key count is missing, the math produces an implausible result, or per-cohort CVR can't be back-calculated. When unsure, ask the user before running.

**Cohort % from first signal:**
1. Find the earliest step where cohorts diverge (OTP skip-PII for 🔵, DUP_EMAIL for 🟠, TOS for 🟢)
2. Read the count at that step from the flowchart doc
3. Cohort entry % = `first_signal_count / total_entry_count`
4. Pre-signal droppers: apply the same cohort split ratio backward (they're assumed to have the same mix)

**CVR back-calculation:**
- Cat3 completions ≈ `new_accounts_created × post_auth_cvr` (post_auth_cvr = `completions / post_auth_entry`)
- Cat1 completions = `total_completions − Cat2_completions − Cat3_completions`
- Per-cohort CVR = `cohort_completions / cohort_entry_count`

**When math isn't enough — run a query:**
- 🔵 phone match count is not in the flowchart (it's implied, not counted)
- Post-auth CVR differs materially by cohort (i.e., one cohort has higher drop at offer quality / marketplace steps)
- Validating a new funnel for the first time

---

## Pattern 8 — Drop-off by Cohort × Step

Extends Pattern 3 (dropout classification) with cohort labels. Produces a matrix of drop-off step × cohort — useful for identifying which cohort is responsible for the biggest absolute drop at each step, and for building targeted experiment or re-engagement populations.

```sql
-- After session_steps CTE (from Pattern 1) and classified CTE (from Pattern 7):
non_completers AS (
  SELECT s.[stitch_key], s.cohort_date
  FROM session_steps s
  WHERE s.completed = 0
),

last_events AS (
  SELECT
    nc.[stitch_key],
    nc.cohort_date,
    ev.content_screen   AS last_screen,
    ev.system_eventType AS last_event_type,
    ROW_NUMBER() OVER (PARTITION BY nc.[stitch_key] ORDER BY ev.ts DESC) AS rn
  FROM non_completers nc
  JOIN [event_table] ev
    ON ev.[stitch_key] = nc.[stitch_key]
    AND ev.ts BETWEEN [session_start_ts] AND [session_end_ts]  -- same window as session_steps
  WHERE DATE(ev.ts) BETWEEN '[start]' AND '[end + buffer]'     -- partition filter first
),

drop_classified AS (
  SELECT
    le.[stitch_key],
    le.last_screen,
    CASE
      WHEN le.last_event_type IN (1, 4) THEN 'organic_dropout'
      WHEN le.last_event_type IN (2, 3) THEN 'disappearance'
    END AS dropout_type,
    cl.cohort  -- from Pattern 7 classified CTE
  FROM last_events le
  LEFT JOIN classified cl USING ([stitch_key])
  WHERE le.rn = 1
)

SELECT
  cohort,
  last_screen,
  dropout_type,
  COUNT(*)                                                              AS users,
  ROUND(COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY cohort) * 100, 1) AS pct_of_cohort_drops,
  ROUND(COUNT(*) / SUM(COUNT(*)) OVER () * 100, 1)                    AS pct_of_all_drops
FROM drop_classified
GROUP BY 1, 2, 3
ORDER BY cohort, users DESC
```

**How to read the output:**
- `pct_of_cohort_drops` — within a given cohort, where does most of the drop happen? (tells you where to focus for that cohort)
- `pct_of_all_drops` — across the full funnel, how much of total drop-off does this cohort × step cell represent? (tells you the absolute opportunity size)
- Sort by `pct_of_all_drops DESC` to find the highest-leverage intervention point across all cohorts

**Tip:** Use this output to generate experiment hypotheses. A cell where `pct_of_all_drops` is high and the cohort has high completion potential (low-CVR cohort, large population) is the highest-priority target. See `Context/drop-off-to-experiment.md` for the hypothesis framing template.

---

## General Rules

- **Always anchor on session start date** for cohort measurement, not completion date
- **Always add 1-day buffer** on event table joins to catch sessions spanning midnight
- **Never mix completers and non-completers in the same step count** — entry population is the denominator; completers are a subset
- **For cross-auth funnels:** apply the 1:1 cardinality gate on the stitch key before all joins (Pattern 1 note above)
- **Partial periods:** always flag the most recent week/day as potentially incomplete in results
- **Large event table joins:** use async script — refer to `CLAUDE.md` for path and usage
- **Ordered vs. unordered funnels:** Pattern 1 measures step *reach*, not step *sequence*. The `MAX(CASE WHEN ...)` flags capture whether a step was ever hit — not whether it was hit before or after another step. For ordered funnels this is fine (the sequence is enforced by the product). For unordered funnels (where users can complete steps in any order or skip to completion), do not infer sequence from the presence of a flag. If order matters, use `ROW_NUMBER()` or timestamp comparisons to confirm sequencing explicitly.
