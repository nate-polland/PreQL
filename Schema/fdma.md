---
status: finalized
last_validated: 2026-03-13
---

# Schema: Daily Activity Data (FDMA)

**Table:** `prod-ck-abl-data-53.dw.fact_member_active_daily`
**Alias:** `FDMA`
**Grain:** One row per `numericId` per `activitydate` — tracks unique daily logins
**Geography:** No country column — US-only by design. No country filter needed.
**Partition Key:** `activitydate` (STRING, `YYYY-MM-DD`) — always filter this before joining

## Core Identifiers
- `numericId` (INT64) — primary join key to demographic data
- `activitydate` (STRING) — date of login/activity; cast to DATE when filtering: `CAST(activitydate AS DATE)`
- `originalId` (INT64) — first account's numericId; used only for duplicate user lifecycle mapping

## Cohort Segmentation
- `userSegment` (INT64) — `1` = New Matched Member (joined today), `0` = Returning Matched Member
- `usersegmentMonth` (STRING) — monthly segmentation; identifies users who joined in the current reporting month

## Platform & Device Flags
**CRITICAL:** These are FLOAT64 binary indicators. Filter with `= 1.0`, not `= TRUE`.
- `isDesktop` (FLOAT64)
- `isMobileApp` (FLOAT64)
- `isMobilebrowser` (FLOAT64)
- `isiOS` (FLOAT64)
- `isAndroid` (FLOAT64)

## Credit Context at Time of Activity
- `score` (FLOAT64) — Transunion Vantage3 score at time of login
- `scoreBand` (STRING) — categorical score band at time of login
- `matchedTs` (INT64) — epoch ms; closest timestamp to credit bureau match
- `org_matchedTs` (INT64) — epoch ms; original match timestamp (for duplicate tracking)

## Demographics at Time of Activity
- `age` (FLOAT64) — age at time of activity
- `ageBand` (STRING) — categorical age band at time of activity
