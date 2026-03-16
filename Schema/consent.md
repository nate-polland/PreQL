# Schema: Consent Data (Opt-In ETL)

**Table:** `prod-ck-abl-data-53.service_bus_streaming_etl.usermanagement_opt_in_etl`
**Alias:** `consent`
**Grain:** One row per consent event (user × product × action)
**Structure:** Deeply nested STRUCTs — access fields via dot notation

## Key Fields

### User Identifier
- `data.numericId.value` (INT64) — join key to other tables (`numericId`)

### Consent Info (`data.consentInfo`)
- `product` (STRING) — consent product name (e.g., `'ChatGPTConsent'`)
- `consentAction` (STRING) — `'Consented'` (only value observed for ChatGPT; no revocations in this table)
- `consentDateTime.value` (STRING) — ISO 8601 timestamp of consent event
- `platform` (STRING) — e.g., `'Web'`
- `vertical` (STRING) — e.g., `'Core'`
- `consentVersion` (STRING) — version of consent language shown
- `referrer` (STRING), `callToAction` (STRING)

### Geography (`data.geoArea`)
- `country` (STRING) — e.g., `'United States'` (full name, not ISO code)
- `administrativeArea` (STRING) — state/province

### Metadata (`metadata`)
- `kafkaTimestamp` (INT64) — epoch ms of event ingestion
- `kafkaPartition`, `kafkaOffset` (INT64)

## ChatGPT Population Query
```sql
SELECT DISTINCT data.numericId.value AS numericId
FROM `prod-ck-abl-data-53.service_bus_streaming_etl.usermanagement_opt_in_etl`
WHERE data.consentInfo.product = 'ChatGPTConsent'
  AND data.consentInfo.consentAction = 'Consented'
```

## Caveats
- No revocation records observed — this table may only capture opt-ins, not opt-outs
- ~9.6K ChatGPT consented users as of 2026-03-13; growing daily
- Whether this is the best base population definition is TBD — it's the fastest proxy available
