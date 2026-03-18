---
created: 2026-03-18
last_validated: 2026-03-18
status: final
funnels: lbe-intuit.md, lbe-intuit-2025.md, lbe-ck-origin-2025.md
pattern: Entry cohort (Pattern 1 — Step 1)
---

# LBE Entry Cohort — All Variants

Returns one row per unique `user_cookieId` that entered any LBE variant in the date range. Adjust the `WHERE` clause to isolate a specific variant.

**Columns needed:** `user_cookieId`, `ts` (for `MIN` and `DATE`), `request_url`, `request_refUrl`, `content_screen`
**Output shape:** one row per unique entrant cookie
**Join key:** n/a (single table, GROUP BY)

## Intuit-origin

```sql
SELECT
  user_cookieId,
  MIN(ts)        AS first_entry_ts,
  DATE(MIN(ts))  AS entry_date
FROM `prod-ck-abl-data-53.kafka_sponge.sponge_BigEvent`
WHERE DATE(ts) BETWEEN '[start]' AND '[end]'
  AND content_screen = 'seamless-registration'
  AND request_url    = '/signup/lbe'
  AND request_refUrl LIKE '%intuit%'
GROUP BY user_cookieId
```

## CK-internal-origin

```sql
SELECT
  user_cookieId,
  MIN(ts)        AS first_entry_ts,
  DATE(MIN(ts))  AS entry_date
FROM `prod-ck-abl-data-53.kafka_sponge.sponge_BigEvent`
WHERE DATE(ts) BETWEEN '[start]' AND '[end]'
  AND content_screen = 'seamless-registration'
  AND request_url    = '/signup/lbe'
  AND request_refUrl LIKE '%creditkarma.com%'
  AND request_refUrl NOT LIKE '%intuit%'
GROUP BY user_cookieId
```

## All LBE (no origin filter)

```sql
SELECT
  user_cookieId,
  MIN(ts)        AS first_entry_ts,
  DATE(MIN(ts))  AS entry_date
FROM `prod-ck-abl-data-53.kafka_sponge.sponge_BigEvent`
WHERE DATE(ts) BETWEEN '[start]' AND '[end]'
  AND content_screen = 'seamless-registration'
  AND request_url    = '/signup/lbe'
GROUP BY user_cookieId
```

## Notes

- Stitch key: `user_cookieId` (cross-auth; persists pre- and post-authentication)
- Completion anchor: `content_screen = 'personal-loan-marketplace'` + `system_eventType = 1`
- Session window: 3-day buffer from `entry_date` is sufficient for LBE (completions typically within same session; 3-day catches return visits)
- `request_refUrl` is populated at entry; NULL for direct/unknown origin
- Validated entry counts: Intuit-origin Sep 2025 = 483 cookies; CK-origin Sep 2025 = 2,278 cookies; Intuit-origin Mar 2026 = ~2,159 (intuit-only, 3-day window)
