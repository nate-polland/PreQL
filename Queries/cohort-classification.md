---
created: 2026-03-18
last_validated: 2026-03-18
status: final
funnels: lbe-intuit-2025.md, lbe-ck-origin-2025.md
pattern: Pattern 7 — Cross-Funnel Cohort Classification
---

# Cross-Funnel Cohort Classification

Classifies each funnel entrant into a user-type cohort based on which signal screens they hit, then measures per-cohort size and conversion. Useful for comparing funnel mix across variants or time periods.

**Columns needed:** `user_cookieId`, `ts`, `DATE(ts)`, `content_screen`, `system_eventCode`, `system_eventType`, `request_url`, `request_refUrl`
**Output shape:** one row per (funnel, cohort) combination with user count and completers
**Join key:** `user_cookieId`

## Cohort signals

| Cohort | Signal | Notes |
|---|---|---|
| Cat1 — Recognized login | `content_screen LIKE 'login%'` OR `LIKE 'ump%'` | Existing user recognized at entry or mid-flow |
| Cat2a — Match failed | `system_eventCode = 'matchFailedReturn'` | Existing user, Prove couldn't verify |
| Cat3 — New user | `system_eventCode = 'termsContinue'` | TOS acceptance = net-new account |
| Cat2b — Prove-returning | Completed; no login, TOS, or matchFailed | Existing user recognized by Prove, skips TOS |
| Bouncer | None of the above | Dropped before any signal screen |

**Priority order:** Cat1 > Cat2a > Cat3 > Cat2b > Bouncer (apply as CASE WHEN chain)

## SQL — LBE Sep 2025 (both variants)

```sql
WITH entries AS (
  SELECT user_cookieId, MIN(DATE(ts)) AS entry_date, 'LBE_Intuit_Sep2025' AS funnel
  FROM `prod-ck-abl-data-53.kafka_sponge.sponge_BigEvent`
  WHERE DATE(ts) BETWEEN '2025-09-01' AND '2025-09-03'
    AND content_screen = 'seamless-registration'
    AND request_url    = '/signup/lbe'
    AND request_refUrl LIKE '%intuit%'
  GROUP BY user_cookieId

  UNION ALL

  SELECT user_cookieId, MIN(DATE(ts)) AS entry_date, 'LBE_CK_Sep2025' AS funnel
  FROM `prod-ck-abl-data-53.kafka_sponge.sponge_BigEvent`
  WHERE DATE(ts) BETWEEN '2025-09-01' AND '2025-09-03'
    AND content_screen = 'seamless-registration'
    AND request_url    = '/signup/lbe'
    AND request_refUrl LIKE '%creditkarma.com%'
    AND request_refUrl NOT LIKE '%intuit%'
  GROUP BY user_cookieId
),

screens AS (
  SELECT
    e.user_cookieId,
    e.funnel,
    MAX(CASE WHEN be.content_screen LIKE 'login%' OR be.content_screen LIKE 'ump%' THEN 1 ELSE 0 END) AS saw_login,
    MAX(CASE WHEN be.system_eventCode = 'matchFailedReturn'                          THEN 1 ELSE 0 END) AS saw_matchfailed,
    MAX(CASE WHEN be.system_eventCode = 'termsContinue'                              THEN 1 ELSE 0 END) AS saw_tos,
    MAX(CASE WHEN be.content_screen = 'personal-loan-marketplace'
             AND be.system_eventType = 1                                             THEN 1 ELSE 0 END) AS completed
  FROM entries e
  JOIN `prod-ck-abl-data-53.kafka_sponge.sponge_BigEvent` be
    ON be.user_cookieId = e.user_cookieId
    AND DATE(be.ts) BETWEEN e.entry_date AND DATE_ADD(e.entry_date, INTERVAL 3 DAY)
  WHERE DATE(be.ts) BETWEEN '2025-09-01' AND '2025-09-06'   -- static partition filter
  GROUP BY e.user_cookieId, e.funnel
),

classified AS (
  SELECT *,
    CASE
      WHEN saw_login       = 1 THEN 'Cat1_recognized_login'
      WHEN saw_matchfailed = 1 THEN 'Cat2a_match_failed'
      WHEN saw_tos         = 1 THEN 'Cat3_new_user'
      WHEN completed       = 1 THEN 'Cat2b_prove_returning'
      ELSE                          'Bouncer'
    END AS cohort
  FROM screens
)

SELECT
  funnel,
  cohort,
  COUNT(*)                                                              AS users,
  ROUND(COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY funnel) * 100, 1) AS pct_of_funnel,
  COUNTIF(completed = 1)                                               AS completers,
  ROUND(SAFE_DIVIDE(COUNTIF(completed = 1), COUNT(*)) * 100, 1)       AS conv_pct
FROM classified
GROUP BY funnel, cohort
ORDER BY funnel, cohort
```

## Notes

- Run via `bq_async.sh` — BigEvent join, will exceed MCP timeout
- To add more funnels: UNION ALL in the `entries` CTE; extend the static partition filter in `screens` to cover all date windows
- When date windows are far apart (e.g., Sep 2025 + Mar 2026), split into separate queries — a single 6-month scan is expensive
- `personal-loan-landing` fires simultaneously with `personal-loan-marketplace` (modal overlay) — safe to use either as completion anchor; `personal-loan-marketplace` preferred
- For ChatGPT: completion anchor is `content_screen IN ('link-chatgpt', 'link-mcp')` + `system_eventType = 2` + `system_eventCode = 'agreeClick'`
