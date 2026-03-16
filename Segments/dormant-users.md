---
# Segment: Dormant Users

**Created:** 2026-03-13

## Plain English Definition
Users whose last login was between 3 and 12 months ago. Less disengaged than churned users (12+ months) but no longer regularly active.

## Primary Table
`prod-ck-abl-data-53.dw.fact_member_active_daily` (FDMA)

## SQL Filter

```sql
-- Dormant as of a reference date:
-- Last login was between 3 and 12 months before <reference_date>
numericId IN (
  SELECT numericId
  FROM `prod-ck-abl-data-53.dw.fact_member_active_daily`
  WHERE CAST(activitydate AS DATE) < <reference_date>
  GROUP BY numericId
  HAVING MAX(CAST(activitydate AS DATE)) >= DATE_SUB(<reference_date>, INTERVAL 12 MONTH)
    AND MAX(CAST(activitydate AS DATE)) < DATE_SUB(<reference_date>, INTERVAL 3 MONTH)
)
```

## Important Caveats
- Always define the reference date explicitly — "dormant" is relative to the analysis window start
- Use `HAVING MAX(activitydate)` to capture true last login, not just any login in range
