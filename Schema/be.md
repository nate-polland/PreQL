# Schema: Behavioral Event Data (BigEvent / BE)

**Table:** `prod-ck-abl-data-53.kafka_sponge.sponge_BigEvent`
**Alias:** `BE`
**Grain:** One row per event. Multiple events per user per day. Not all users appear every day.
**CRITICAL:** This is an extremely large table. **Always filter on `ts` (TIMESTAMP) first.** Restrict to the tightest possible time window before any other filtering.

**MCP TIMEOUT WARNING:** The BigQuery MCP connection times out at ~60s. Any query that joins BigEvent (even for a small population) will time out via MCP. Use `bq_async.sh` for all BE joins — see `CLAUDE.md` for the async workflow.

## User Identifier
- `user_dwNumericId` (INT64) — **use this for all joins to FTRE, FDMA, userStatus**. This is the obfuscated DW numeric ID, equivalent to `numericId` in other tables. Also exposed as `ckNumericId` (same value, different column name).
- `user_userMetaDataId` (INTEGER) — internal CK Mono ID. NOT the same as `numericId`. Do not use for joins to DW tables.
- `user_cookieId` (STRING) — cookie ID, web only
- `user_deviceId` (STRING) — device ID, mobile only
- `user_traceId` (STRING) — **Primary cross-auth session stitch key** (validated 2026-03-14). Persists across the unauthenticated→authenticated boundary; ~99% populated on funnel screens. Maps 1:1 to numericId within a session. Use to join pre-auth events (NULL numericId) to post-auth events for the same user. See `Context/chatgpt-auth-funnel.md`.
- `glid` (STRING) — newer session identifier replacing traceId; more scalable. **Auth-only: ~0% populated for unauthenticated users.** Do NOT use for cross-auth funnel stitching.
- `user_hasAuth` (BOOLEAN) — true if user was authenticated at time of event

## Geography
- `user_country` (STRING) — **US users have NULL**; non-US users are tagged (e.g., `'CA'`, `'ca'`, `'uk'`). US filter: `(user_country IS NULL OR UPPER(user_country) = 'US')`. Do NOT use `user_country = 'US'` — no rows match. Canadian traffic is ~0.2% of events.

## Joining BE to FTEE
**Best join key:** `content_impressionId` (BE) = `impressionId` (FTEE)
- `FTEE.impressionId` is 0% null — preferred
- `FTEE.beImpressionId` is 25% null — avoid; loses 1 in 4 click events
- See `Context/cross-table-joins.md` for full join patterns and partner ID mapping

## Timestamp
- `ts` (TIMESTAMP) — **mandatory filter field**; timestamp of event receipt. Use directly — do NOT wrap in `TIMESTAMP_MILLIS()`. Filter pattern: `ts BETWEEN TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL N DAY) AND CURRENT_TIMESTAMP()`. Extract date with `DATE(ts)`.
- `system_tsEvent` (TIMESTAMP) — timestamp fired on device (may be unreliable — device clock skew possible)

## Event Classification
- `system_eventType` (INTEGER) — type of event:
  - `1` = Impression (any pixel of item rendered)
  - `2` = Click
  - `3` = PageView
  - `4` = Enhanced Impression (center pixel rendered — more reliable viewability signal)
  - `6` = Navigation Event
  - `7` = Swipe Event
- `system_eventContent` (INTEGER) — content category:
  - `1` = Offer
  - `2` = Navigation
  - `4` = Advice Card
  - `5` = UNS (Universal Notification Service)
  - `7` = Portal
- `system_eventCode` (STRING) — further designation (e.g., `TakeCCOffer`, `ViewDetails`)

## Offer / Content Fields
- `content_contentId` (STRING) — unique ID of content displayed
- `content_providerId` (STRING) — **internal partner slug** (lowercase, e.g., `'prosper'`, `'plskopos'`). NOT the same as `partner` in FTEE/FTRE. See `Context/cross-table-joins.md` for the full mapping. Canadian partners may have `'CAN'` prefix (e.g., `'CANPLSpringFinancial'`) — exclude with US country filter.
- `content_contentType` (STRING) — type of content (e.g., `CC`, `PLoan`, `AdviceCard`)
- `content_approvalLabel` (STRING) — approval probability badge label
- `content_impressionId` (STRING) — FlakeID created at time of content creation
- `content_recommendationId` (STRING) — Recommendation ID from Jarvis (recsys)
- `content_sectionRank` (INTEGER) — order rank of section on screen
- `content_contentRank` (INTEGER) — rank of content within section
- `content_screen` (STRING) — screen name where content resides
- `content_section` (STRING) — section name
- `content_feature` (STRING) — feature context (e.g., Registration, Login, Dashboard)
- `content_trackingEventId` (INTEGER) — legacy tracking event ID; joins to FTRE/FTEE
- `content_variantId` (STRING) — content variant ID for personalized offers

## Impression ID Fields
- `content_impressionId` (STRING) — **recommended for impression-level analysis**; FlakeID, ~0% null rate, unique per event
- `content_recommendationId` (STRING) — Jarvis recommendation ID; ~1.7% null rate; one ID may span multiple impression rows (user saw same recommendation multiple times)
- `impressionIdV2` (STRING) — v2 impression identifier; ~1.7% null rate; similar cardinality to recommendationId
- `ijmpressionidv2` (STRING) — **DO NOT USE; confirmed 100% null in production**
- `oicRecommendationIds` (STRING) — OIC recommendation IDs

## User ID Null Rates (validated on PL impressions)
- `user_dwNumericId` — **0.003% null**. Use this for user counts and joins.
- `user_userMetaDataId` — ~41% null. Do not use for reach analysis or joins to DW tables.

## ITA / LB / PQ Classification (Personal Loans)
Use `flex_intField33` to identify offer type for Personal Loan clicks:
```sql
CASE
  WHEN (flex_intField33 IS NULL AND LOWER(content_approvalLabel) = 'pre-qualified') OR flex_intField13 = 3 THEN 'PQ'
  WHEN flex_intField33 = 1 THEN 'ITA'
  WHEN flex_intField33 > 1 THEN 'LB'
END AS offer_type
```

## Platform
- `platform_platform` (STRING) — `Web`, `MWeb`, `Android`, or `iOS`
- `platform_browser` (STRING) — Chrome, Safari, Firefox, etc.
- `platform_os` (STRING) — Windows, iOS, Android, MacOS
- `platform_deviceType` (STRING)
- `platform_appVersion` (STRING) — mobile app version

## Key Flex Fields for Offer Analysis
- `flex_intField33` (INTEGER) — certainty decision for approval odds (ITA/LB/PQ classification)
- `flex_intField42` (INTEGER) — count of PL offers served
- `flex_intField46` (INTEGER) — approval odds integer (0–100)
- `flex_intField28` (INTEGER) — page number of impression
- `flex_strField25` (STRING) — high-level RecSys response ID
- `flex_strField26` (STRING) — individual offer-level ID in RecSys (important for PL)

## DO NOT USE
- `flex_intField12` — reserved for pipeline use
- `flex_numField50` — reserved for tracking team
- `flex_strField50` — reserved for partial hydration
- `system_tsEvent` — unreliable due to device clock skew; use `ts` instead
