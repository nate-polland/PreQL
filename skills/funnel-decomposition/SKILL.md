---
name: funnel-decomposition
description: |
  Decomposes a complex product funnel into path-based cohorts, measures each cohort's share of the funnel population (% of users) and completion rate, and identifies which cohorts represent the biggest drop-off opportunities. Designed for funnels with structurally different user paths — not for simple demographic segmentation (age, geography, user segment), which only requires a join to a user attribute table.

  Prerequisite: a Funnels/ doc must exist for the funnel in question. If not, run /funnel-discovery first.

  Trigger phrases: "decompose this funnel", "which path is dropping off", "completion rate by path", "break down the funnel", "who is converting", "analyze drop-off by user type", "funnel decomposition", "complex funnel analysis", or any request to understand funnel performance across structurally different user paths.

  Do NOT trigger for: simple demographic cohorts (new vs returning by account age, geography, credit band) where the answer is a join to a user attribute table. This skill is for funnels where users take meaningfully different routes through the product.
---

# Funnel Decomposition

You are a Senior Product Analyst decomposing a complex product funnel to understand where different types of users drop off. The goal is two metrics per cohort:

1. **% of users** — what fraction of the top-of-funnel population follows this path
2. **Completion rate** — completions / cohort population, where completions are **directly queried per cohort**, not estimated by applying a percentage

Read the relevant `Funnels/` doc before starting. Do not rely on conversation summaries.

---

## Step 0 — Pre-Flight: Can This Be Answered From the Existing Doc?

Before writing any SQL, check whether the persisted Funnels/ doc already has the numbers needed.

**Derive from doc first (no query needed):**
- Cohort % splits when step counts and first-signal counts are in the doc
- CVR for top-level cohorts if already queried and persisted
- Sub-cohort CVR estimates when the weighted check closes (see Math-First section in `Context/funnel-measurement-patterns.md`)

**Require a new query when:**
- The sub-breakdown is not in the doc (e.g., a cohort split by sub-path when only the top-level cohort is persisted)
- The math produces an implausible result (weighted check fails by >1pp)
- Validating a new funnel or a new date window for the first time
- A count is needed that doesn't appear anywhere in the flowchart or cohort table

**Scope the gap before proceeding.** If the answer requires a new sub-breakdown not in the persisted doc, say so explicitly *before* querying: *"This split isn't in the existing analysis — it would require a new query. Want to proceed, or is a math-based estimate sufficient?"* The user may not realize the doc doesn't have it; surfacing that is your job.

**The most common source of wasted work:** going straight to querying, hitting contamination or structural issues, then discovering the doc had the answer (or that an estimate would have been sufficient).

---

## Step 1 — Define Cohorts with the User

Before touching data, agree on what cohorts make sense for this funnel. Ask the user:

1. **What is the analytical question?** Understanding what they want to learn shapes which cohort split is meaningful. Examples:
   - "Did the login-path efficiency change after the redesign?" → cohort by auth path
   - "Do users from different acquisition sources complete at different rates?" → cohort by entry source
   - "How do new vs returning users compare?" → depends on how "new/returning" maps to observable funnel signals

2. **What are the structurally different paths through this funnel?** Look at the Funnels/ doc — are there forks where users see genuinely different screens or flows? Each fork that sends users to a distinct experience is a potential cohort boundary.

3. **What is the first observable signal for each cohort?** A cohort is only useful if you can identify it from data. For each proposed cohort, identify: what event fires first that deterministically places a user in that cohort? If there's no reliable signal, the cohort isn't observable.

**Cohort types for complex auth/registration funnels:**
- Path-based (e.g., existing user via login vs new user via registration vs recognized-phone shortcut)
- Entry-source-based (e.g., Intuit-origin vs CK-internal traffic)
- Feature-availability-based (e.g., users who saw a new screen vs those who didn't)

**When to stop and redirect:** If the proposed cohorts can be answered with a simple join to a user attribute table (e.g., `userStatus`, demographics), this skill is overkill — suggest a simpler query instead. This skill adds value when the cohorts are defined by *what happened in the funnel*, not *who the user is before they entered*.

**Priority rule when a user could belong to multiple cohorts:** Define a priority ordering upfront (e.g., "if a user hits both path A and path B signals, they are path A"). Document it explicitly — you'll need it when signals overlap.

---

## Step 2 — Define the Anchor

The anchor is the **last step where all users share a common path before any forking**. This is the denominator for % of users.

- If there's a single entry screen all users pass through before any path diverges, that's the anchor
- If users fork immediately at entry (different landing screens, different entry sources), entry is the anchor
- If there's a shared step deeper in the funnel (e.g., an OTP screen all users go through before splitting), that's a better anchor — it reduces the unclassified drop allocation problem

If the funnel doc doesn't identify the anchor, find the highest-volume step that precedes any divergence. Confirm with the user before proceeding.

---

## Step 3 — Compute % of Users

### 3a — Classify users at the anchor step

Count how many anchor-step users are directly observable in each cohort. Join anchor-step users to all events in the session window, then flag each user by which cohort signals they fired.

### 3b — Allocate unclassified drops

Users who drop before reaching any classification signal cannot be observed directly. Allocate them proportionally using the **classified mix** — the ratio of classified users across cohorts.

**Which mix to use:**
- If one cohort diverges early (before other cohorts' signals are observable), use the remaining cohorts' mix for unclassified drops — the early-diverging cohort is already captured
- Otherwise, use the overall classified mix

**Formula:**
```
cohort_total = classified + (unclassified × cohort_share_of_classified)
% of users = cohort_total / anchor
```

**Validation:** cohort totals must sum to 99–101% of anchor. If outside this range, find the gap before proceeding.
- >101%: double-counting a cohort or a signal overlap — check priority rules
- <99%: a user path is unaccounted for — look for unmapped screens or missing cohort signals

### 3c — State assumptions explicitly

- **Uniform dropout assumption**: pre-classification drop-off is assumed equal across cohorts absent data to the contrary. If you have reason to believe one cohort drops at a different rate before classification (e.g., error rates visible in the data), use that and document it.
- **Proportional allocation**: unclassified drops split by the observable cohort mix at their exit point.

---

## Step 4 — Compute Completion Rate

### Numerator: direct query per cohort

Find all completers (users who reached the completion event), then classify each by cohort signal — same logic as Step 3a but scoped to completers only.

```sql
-- Template: completer classification
WITH anchor_users AS (
  SELECT DISTINCT [stitch_key]
  FROM [event_table]
  WHERE DATE([ts]) BETWEEN '[start]' AND '[end]'
    AND [anchor filter]
),
completers AS (
  SELECT DISTINCT e.[stitch_key]
  FROM [event_table] e
  INNER JOIN anchor_users a ON e.[stitch_key] = a.[stitch_key]
  WHERE DATE(e.[ts]) BETWEEN '[start]' AND '[end + session buffer]'
    AND e.[completion screen/event filter]
),
events AS (
  SELECT e.[stitch_key], e.[screen], e.[event_code]
  FROM [event_table] e
  INNER JOIN completers c ON e.[stitch_key] = c.[stitch_key]
  WHERE DATE(e.[ts]) BETWEEN '[start]' AND '[end + session buffer]'
),
classified AS (
  SELECT
    [stitch_key],
    MAX(CASE WHEN [cohort_A signal] THEN 1 ELSE 0 END) AS is_cohort_a,
    MAX(CASE WHEN [cohort_B signal] THEN 1 ELSE 0 END) AS is_cohort_b
  FROM events
  GROUP BY [stitch_key]
)
SELECT
  COUNTIF(is_cohort_a = 1)                                 AS cohort_a_completers,
  COUNTIF(is_cohort_b = 1 AND is_cohort_a = 0)             AS cohort_b_completers,
  COUNTIF(is_cohort_a = 0 AND is_cohort_b = 0)             AS residual_completers,
  COUNT(*)                                                   AS total_completers
FROM classified
```

**Residual completers** — no cohort signal observed. If residual is >5% of total completers, it indicates a path you haven't classified. Investigate before accepting results. If small, note it and move on.

**Session stitch key continuity warning:** If the session stitch key resets between entry and completion (e.g., a new user ID or cookie is issued mid-funnel at an authentication or account-creation step), completers in cohorts that go through that step will land on a new stitch key not present in your anchor set. Symptom: `total_completers` from the query is materially below the independently-known completion count. Diagnosis: check whether the cohorts with large stitch losses are those that go through the identity-reset step. Fix: use a backend data source that records completion independently of session continuity (e.g., a registration or transaction log that tracks completion by user ID, not session key) for those cohorts, and use the session-based query for cohorts that don't cross the identity boundary.

### Denominator: anchor × % of users

```
completion_rate = direct_completers / cohort_total
```

where `cohort_total` = classified + allocated drops (from Step 3b).

---

## Step 4b — Completion Window Check

Before accepting completion counts, confirm the query approach is appropriate for this funnel:

**If the analysis window is > 2 weeks AND the completion screen is a regularly visited product surface for existing users** (e.g., a marketplace page that members browse independently), use a **per-user 72h timestamp window** rather than a fixed date range. Fixed windows attribute unrelated return visits as conversions.

```sql
AND b.ts < TIMESTAMP_ADD(e.first_entry_ts, INTERVAL 72 HOUR)
```

See `Context/funnel-measurement-patterns.md` Pattern 10 for the full template.

---

## Step 5 — Validate

**Step 5a — Sample window representativeness** (run before finalising cohort percentages):

Run a day-by-day entry count across your window (Pattern 9 in `funnel-measurement-patterns.md`). If any day in the sample is >2× the surrounding median, flag it — cohort mix and CVR measured on spike-period traffic may not reflect steady-state. Either exclude the spike days or note the caveat explicitly.

**Step 5b — Cohort math checks:**

**Check 1 — Cohorts sum to ~100%:**
```
sum(cohort_total) / anchor ∈ [0.99, 1.01]
```

**Check 2 — Weighted completion rate matches actual funnel completion rate:**
```
Σ (% of users × completion rate) ≈ actual overall completion rate
```
Within 0.5pp is acceptable. Larger gaps mean a cohort's completions or population is wrong — diagnose before presenting.

---

## Step 6 — Interpret and Document

### Optional: Offer time-to-convert analysis

After presenting the main cohort results, ask if the user wants to understand **time-to-convert distribution** within each cohort — i.e., how long it takes from anchor step to completion, broken down by cohort. This is useful when:
- Completion rates look similar across cohorts but the user suspects one cohort takes longer (e.g., they return days later)
- You want to validate whether the session window is tight enough to capture all completers
- You want to identify whether a "slow" cohort is a re-engagement opportunity vs. fundamentally low intent

This is a separate query (timestamp delta from anchor to completion event, bucketed by hours/days), not part of the main decomposition. Offer it as a follow-up, not a default.

### Answer the user's question first

Go back to the analytical question from Step 1. Before listing per-cohort metrics, state in plain English what the data shows relative to what they wanted to learn.

### Interpretation frame

For each cohort:
1. **How big is this cohort?** (% of users — the relevance filter. A 90% drop rate on a 1% cohort is not an optimization priority)
2. **What is their completion rate?** (from first signal, for comparability across cohorts; from anchor, for the weighted check)
3. **Where is the primary drop point?** (Which step accounts for most of this cohort's attrition?)
4. **What does this imply?** (Product action, experiment hypothesis, or further investigation)

### Primary optimization target

**Size × drop-off = opportunity.** A cohort that is 40% of users and completes at 15% is a bigger opportunity than a cohort that is 5% of users and completes at 50%, even if the second rate looks worse in isolation.

### Document findings

Update the funnel doc's `## Cohort Analysis` section:

```markdown
## Cohort Analysis

### Methodology
[anchor step, cohort definitions and first signals, allocation mix, stated assumptions]

### Cohort Population and Completion Rate

| Cohort | Classified | Allocated drops | % of users | Completions (direct) | Completion rate |
|---|---|---|---|---|---|
| [Cohort A] | ... | ... | ...% | ... | ...% |
| [Cohort B] | ... | ... | ...% | ... | ...% |
| **Total** | | | **100%** | [total] | [overall rate] ✓ |

[Validation notes]

### Interpretation
[Lead with the analytical question answer, then 3–4 bullets on opportunity sizing]
```

---

## Key Rules

- **Doc first, queries second** — always check whether the question can be answered from the persisted Funnels/ doc before writing any SQL. See Step 0 and the Math-First section in `Context/funnel-measurement-patterns.md`.
- **Scope new sub-breakdowns explicitly** — if the user asks for a split not present in the existing doc, name the gap and ask whether to proceed before querying.
- **Cohorts first, data second** — agree on what cohorts make sense analytically before writing any SQL. The wrong cohort definition produces correct-looking but useless numbers.
- **Never guess cohort counts** — run queries wherever counts aren't directly observable. State clearly whether a number is queried vs. estimated.
- **Completion numerator must be direct** — do not compute completions by applying a percentage. The count must come from a query that classifies actual completers.
- **Conditional probability chain** — when computing % of users through a multi-step path, multiply each step's rate through the chain. Never use the anchor as the denominator for an intermediate step. Example mistake: `cohort% = (cohort/fork_step) × (path/anchor)` — this skips the `(fork_step/path)` term and inflates the result.
- **Check stitch key continuity** — before querying, confirm that the stitch key you're using to connect entry to completion is the same identifier throughout the session. Any step that issues a new user/session ID is a break point.
- **Run queries async** — any query joining a large event table by session key will timeout via synchronous MCP. Use the async workflow defined in `CLAUDE.md`.
- **Partition pruning first** — always filter by the timestamp partition column before any join.
