# Schema: Demographic Data (userstatus)

**Table:** `prod-ck-abl-data-53.dw.userstatus_ext`
**Alias:** `userStatus`
**Grain:** One row per `numericId` per day — not partitioned, filter date fields carefully

## Mandatory Filters (every query)
```sql
WHERE isDuplicate = 0
  AND isFakeuser = 0
```

## Core Identifiers
- `numericId` (INT64) — primary key; use for all joins
- `registrationTs` (INT64) — epoch ms; convert with `TIMESTAMP_MILLIS(registrationTs)`
- `validationTs` (INT64) — epoch ms; user completed registration funnel
- `firstReportTs` (INT64) — epoch ms; first credit report received
- `deactivationTs` (INT64) — epoch ms; account deactivated
- `latestActivityDate` (STRING) — most recent activity date, format `YYYY-MM-DD`

## Credit Attributes
- `firstScore` (INT64) — initial Transunion Vantage3 score
- `recentScore` (INT64) — most recent Transunion Vantage3 score
- `firstScore20` (STRING) — initial score rounded to nearest 20
- `recentScore20` (STRING) — recent score rounded to nearest 20
- `firstScoreCreditBand` (STRING) — band of initial score (e.g., `'560 and below'`)
- `curScoreCreditBand` (STRING) — band of current score
- `curScoreTs` (INT64) — epoch ms of most recent score pull
- `isfirstscoreThinFile` (INT64) — 1 if user had no credit file at join
- `isuserThinFile` (INT64) — 1 if user currently has no credit file
- `thinfileRemovedTs` (INT64) — epoch ms when credit file was established

## Demographics & Geography
- `birthYear` (INT64), `age` (INT64) — year of birth and current age
- `ageBand` (STRING) — categorical age grouping
- `city`, `state`, `zip` (STRING) — current location. **US-only — no country field; no country filter needed.** `state` contains US states + territories (PR, GU, VI) and military codes (AE, AP, AA); no Canadian provinces present.
- `regPlatform` (STRING) — platform used at registration
- `regSubPlatform` (STRING) — sub-platform detail at registration

## Quality Flags
- `isDuplicate` (INT64) — filter `= 0` always
- `isFakeuser` (INT64) — filter `= 0` always

## DO NOT USE — Reliability Classified as Unknown
- `creditSuccessTs`
- `isPreCreditTransient`
- `isPostCreditTransient`
