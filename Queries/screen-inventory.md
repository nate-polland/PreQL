---
created: 2026-03-18
last_validated: 2026-03-18
status: final
funnels: any BigEvent funnel
pattern: Phase 2b broad screen inventory (funnel-discovery SKILL.md step 7)
---

# BigEvent Screen Inventory

Run this as the **first join query** in any new funnel discovery. Returns every screen, event type, and event code hit by the entry cohort within the session window — one query gives you the complete screen inventory before any per-user path traces.

**Columns needed:** `user_cookieId` (or stitch key), `content_screen`, `system_eventType`, `system_eventCode`, `ts`, `DATE(ts)`
**Output shape:** one row per unique (content_screen, system_eventType, system_eventCode) combination
**Join key:** `user_cookieId` (stitch key) from entry cohort CTE to BigEvent

```sql
WITH entry_cohort AS (
  SELECT
    user_cookieId,
    MIN(DATE(ts)) AS entry_date
  FROM `prod-ck-abl-data-53.kafka_sponge.sponge_BigEvent`
  WHERE DATE(ts) BETWEEN '[start]' AND '[end]'
    AND [entry_filter]   -- e.g., content_screen = 'seamless-registration' AND request_url = '/signup/lbe'
  GROUP BY user_cookieId
)

SELECT
  be.content_screen,
  be.system_eventType,
  be.system_eventCode,
  COUNT(DISTINCT be.user_cookieId) AS cookies
FROM entry_cohort e
JOIN `prod-ck-abl-data-53.kafka_sponge.sponge_BigEvent` be
  ON be.user_cookieId = e.user_cookieId
  AND DATE(be.ts) BETWEEN e.entry_date AND DATE_ADD(e.entry_date, INTERVAL 3 DAY)
WHERE DATE(be.ts) BETWEEN '[start]' AND DATE_ADD('[end]', INTERVAL 3 DAY)
GROUP BY 1, 2, 3
ORDER BY cookies DESC
```

## Notes

- Use a **3-day window** from the start — 1-day windows miss rare screens (branded offer cards, survey flows, 2FA paths) that only appear in a larger sample
- The outer `WHERE DATE(be.ts)` clause must be a static date range for partition pruning — don't compute it dynamically inside the query
- Run via `bq_async.sh` — this is a BigEvent join and will exceed MCP's 60s timeout
- Results tell you **what screens exist**; per-user path traces (Phase 4 Stage 1) tell you **ordering and transitions**
- `system_eventType`: 1 = impression, 2 = action/click, 3 = submit, 4 = background impression
- Sort by `cookies DESC` — screens with 1-5 cookies are rare paths worth investigating before excluding
