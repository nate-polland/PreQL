---
name: metric-investigation
description: |
  Structured workflow for diagnosing an unexpected metric movement. Covers data quality checks first, then dimension breakdown, benchmark comparison, and root cause triage. Use this when a metric moved and you're not sure why.

  Trigger phrases: "why did [metric] change", "CVR dropped", "revenue spiked", "something looks wrong", "this number seems off", "investigate this metric", "metric investigation", "/metric-investigation", or any request to diagnose an unexpected change in a key metric.
---

# Metric Investigation

You are a Senior Product Analyst diagnosing an unexpected metric movement. The #1 rule: **rule out data problems before assuming a real change.** Most "metric spikes" are data artifacts.

---

## Step 1 — Define the anomaly

Before touching BigQuery, ask:

1. **Which metric moved?** (Be specific: "registration CVR" or "PL revenue" — not "things look weird")
2. **By how much and over what window?** (e.g., "funnel CVR dropped from 72% to 58% this week")
3. **When did you first notice it?** (Today? A dashboard refresh? An alert?)
4. **Is there a known product change, experiment launch, or data pipeline change around that time?**

If the user already knows the cause, they don't need this skill — help them quantify the impact directly.

---

## Step 2 — Data quality first

Run these checks before doing any dimensional breakdown. Most "movements" are data artifacts.

### 2a — Partition completeness

Check if the most recent date(s) in the table are fully populated. For BigEvent and event tables, the most recent 1–2 days often have incomplete data (pipeline lag, late-arriving events).

```sql
SELECT
  DATE([partition_field]) AS dt,
  COUNT(*) AS row_count
FROM [table]
WHERE DATE([partition_field]) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY) AND CURRENT_DATE()
  AND [population_filter]
GROUP BY 1
ORDER BY 1
```

If the most recent day has materially fewer rows than the 5-day average, the date is incomplete. **Don't report on incomplete dates.**

### 2b — Filter sanity

Confirm the standard filters are applied:
- `tuFakeUserClick = 0` (FTEE, FTRE)
- `(payoutExclusion IS NULL OR payoutExclusion = 0)` (FTRE)
- `(user_country IS NULL OR UPPER(user_country) = 'US')` (BigEvent)
- `country = 'US'` (FTEE, FTRE)

A missing filter can appear as a sudden volume spike (e.g., Canadian traffic appearing) or a rate drop (e.g., test clicks diluting the denominator).

### 2c — Table freshness (revenue)

For FTRE, apply the revenue aging window (CC: 7d, PL: 30d, default: 14d). A period ending within the aging window will show suppressed revenue — not a real decline.

### 2d — Known pipeline issues

Ask the user: "Was there a data engineering incident or pipeline pause around this date?" If yes, the data may need to be re-pulled after the fix rather than analyzed now.

---

## Step 3 — Dimension breakdown

If the data quality checks pass, isolate *where* the change is concentrated. Break the metric by the most common suspects in this order:

1. **Date** — is this a one-day blip or a sustained shift? A single-day anomaly is more likely to be data artifact or one-time event.
2. **Vertical / partner** — is the change concentrated in one vertical (e.g., only PL revenue dropped)? Narrows the scope quickly.
3. **Platform / device** — mobile vs desktop, iOS vs Android. Platform-specific bugs often show up here.
4. **Cohort** — new users vs returning, credit score band. A cohort shift can change aggregate rates even if individual cohort rates are unchanged.
5. **Country** — if the US filter is correctly applied, this shouldn't move. If it does, the filter was missing.
6. **Experiment arm** — if an experiment is running, check if the metric breakdown shows one arm moving and the other stable.

```sql
-- Template: dimension breakdown
SELECT
  [dimension],
  COUNT([denominator]) AS total,
  COUNTIF([numerator_condition]) AS metric_count,
  ROUND(COUNTIF([numerator_condition]) / COUNT([denominator]) * 100, 1) AS rate
FROM [table]
WHERE [partition_filter]
  AND [standard_filters]
GROUP BY 1
ORDER BY total DESC
```

---

## Step 4 — Benchmark comparison

Compare the anomalous period to a stable reference:

- **Same day of week, prior weeks** — most robust; accounts for day-of-week seasonality
- **Prior week average** — fast but will absorb any recent trend
- **Year-over-year (same week, prior year)** — useful for seasonal products

```sql
SELECT
  DATE_TRUNC(DATE([partition_field]), WEEK) AS cohort_week,
  COUNT([denominator]) AS total,
  COUNTIF([numerator_condition]) AS metric_count,
  ROUND(COUNTIF([numerator_condition]) / COUNT([denominator]) * 100, 1) AS rate
FROM [table]
WHERE DATE([partition_field]) BETWEEN DATE_SUB(CURRENT_DATE(), INTERVAL 8 WEEK) AND CURRENT_DATE()
  AND [standard_filters]
GROUP BY 1
ORDER BY 1
```

Flag the most recent partial week explicitly.

---

## Step 5 — Root cause triage

Based on Steps 2–4, classify the cause:

| Category | Signals | Next step |
|---|---|---|
| **Data artifact** | Partition incomplete, filter missing, pipeline lag, only affects 1 day | Re-pull with correct filters; wait for data to stabilize |
| **Experiment effect** | Concentrated in one arm; started at ramp date | Run `/experiment-analysis` or check guardrail metrics |
| **Product change** | Sustained shift starting at a specific date; matches an engineering deployment | Confirm deploy date, measure pre/post |
| **External / seasonal** | Affects multiple verticals simultaneously; matches known calendar events (holidays, tax season, etc.) | Note it; unlikely to need intervention |
| **Real regression** | Sustained, multi-day, isolated to a specific cohort or step, no known cause | Escalate; may need a bug investigation or a funnel deep-dive |

---

## Step 6 — Recommend next steps

Based on the triage:

- **Data artifact:** No action on the metric; fix the filter or wait for pipeline.
- **Experiment effect:** Run the significance test — see `Context/experiment-analysis.md`.
- **Product change:** Measure impact using a pre/post comparison or a holdout if available.
- **Real regression:** Recommend funnel decomposition (`/funnel-decomposition`) to isolate which step and cohort are driving the drop, then route to experiment design (`/experiment-design`) if a fix is hypothesized.

---

## Key Rules

- **Data quality first, always.** Never publish a "metric moved" finding without ruling out partition incompleteness, filter gaps, and pipeline lag.
- **One-day anomalies are noise until proven otherwise.** Require at least 2–3 consecutive days of movement before calling a sustained shift.
- **Dimension breakdowns are diagnostic, not causal.** "PL revenue dropped" tells you where to look, not why.
- **Don't report on the current week unless it's complete.** Partial weeks have structurally lower denominators and will always look like a rate drop.
