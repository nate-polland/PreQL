# Schema: Event Data (FTEE)

**Table:** `prod-ck-abl-data-53.dw.fact_tracking_event_ext`
**Alias:** `FTEE`
**Grain:** One row per event. Multiple events per user per day.
**Purpose:** Bridge table between BigEvent (impression data) and FTRE (revenue data). Unlike FTRE, FTEE is not dependent on partner reporting — it captures CK-side click events in near real-time with no aging delay.
**CLICK-ONLY:** FTEE is triggered post-click only. It does not contain impression data. Use BigEvent for reach/impression analysis.
**US Filter:** Always apply `country = 'US'` and `tuFakeUserClick = 0`.
**Join to BigEvent:** `FTEE.impressionId = BE.content_impressionId` (preferred). `FTEE.beImpressionId` is 25% null — avoid as join key.

## Key Identifiers
- `trackingeventId` (INTEGER) — auto-increment ID; joins to FTRE's `trackingEventId`
- `impressionId` (STRING) — FlakeID created at content creation time
- `impressionIdV2` (STRING) — v2 impression identifier
- `beImpressionId` (STRING) — BigEvent impression ID
- `beImpressionIdV2` (STRING) — v2 BigEvent impression ID
- `recommendationId` (STRING) — Jarvis recommendation ID
- `parent_impressionid` (STRING) — impressionId of PQ Personal Loan clicks that lead to monetizable clicks
- `numericId` (INTEGER) — user identifier; primary join key
- `traceId` (STRING) — UUID for user's session
- `cookieId` (STRING) — web only
- `sessAutoId` (INTEGER) — auto session ID

## Event Details
- `eventCode` (STRING) — event type (e.g., `TakeCCOffer`, `ViewDetails`)
- `eventTs` (INTEGER) — epoch timestamp of event
- `eventDate` (STRING) — date of event (`YYYY-MM-DD`)
- `eventtime` (STRING) — time of event
- `ismonetizable` (BOOLEAN) — whether the event is monetizable
- `isLightbox` (BOOLEAN) — lightbox click
- `isEasyApply` (BOOLEAN) — easy apply flow
- `tuFakeUserClick` (INTEGER) — fake user click; filter `= 0` for production queries

## Offer / Content
- `contentid` (STRING) — unique ID of content
- `partner` (STRING) — partner name
- `vertical` (STRING) — vertical name
- `LOB` (STRING) — line of business
- `approvalBadge` (STRING) — approval probability badge
- `offerRank` (INTEGER) — offer rank on screen
- `sectionRank` (INTEGER) — section rank on screen
- `screen` / `section` (STRING) — page context
- `providerId` (STRING) — partner ID
- `productId_click` (STRING) — product ID mapped to contentId clicked
- `lbCategory_click` (STRING) — lightbox category
- `variantId` (STRING) — content variant ID

## Credit Context at Event Time
- `TUScore` (INTEGER) — Transunion Vantage3 score
- `TUScoreBand` (STRING) — score band
- `FICOscore` (INTEGER), `FICOdate` (DATE), `FICOscoreband` (STRING)
- `age` (INTEGER), `ageBand` (STRING)
- `scoreBand` (STRING) — score band `'<500'` to `'760+'`

## DO NOT USE
- `TUScore_Mono`, `TUScoreBand_Mono` — do not use
- `TUScore_IDLV2`, `TUScoreBand_IDLV2` — do not use
