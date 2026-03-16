---
# Segment: Churned Users

**Created:** 2026-03-13

## Plain English Definition
Users whose last login was 12 or more months ago. Distinct from "dormant" users (3–12 months since last login). Churned users have been fully inactive for over a year.

## Primary Table
`prod-ck-abl-data-53.dw.fact_member_active_daily` (FDMA)

## SQL Filter

```sql
-- Churned as of a reference date (e.g., start of analysis window):
-- Last login was 12+ months before <reference_date>
numericId IN (
  SELECT numericId
  FROM `prod-ck-abl-data-53.dw.fact_member_active_daily`
  WHERE CAST(activitydate AS DATE) < DATE_SUB(<reference_date>, INTERVAL 12 MONTH)
  GROUP BY numericId
  HAVING MAX(CAST(activitydate AS DATE)) < DATE_SUB(<reference_date>, INTERVAL 12 MONTH)
)
```

## Important Caveats
- Always define the reference date explicitly — "churned" is relative to the analysis window start
- Use `HAVING MAX(activitydate)` to find the true last login date, not just any login before the threshold
- Combine with an activity filter on the target window to find re-engaged churned users (churned who returned)
