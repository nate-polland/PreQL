# ChatGPT Embedded Content Product

CK content (Credit Factors, Offers) is embedded inside ChatGPT (and soon Claude). This doc covers how to track and analyze this population.

---

## BigEvent Surfaces

| Surface | `content_screen` | `content_section` | What it shows |
|---|---|---|---|
| Credit Factors widget | `credit-factor-chatgpt-widget` | `credit-factors` (or NULL) | Credit factor cards |
| Offers (CC) | `lbe-openai-chatgpt` | `lbe-openai-chatgpt-cc` | Credit Card offers |
| Offers (CC, no offer) | `lbe-openai-chatgpt` | `lbe-openai-chatgpt-cc-no-offer` | CC section when no offers available |
| Offers (PL) | `lbe-openai-chatgpt` | `lbe-openai-chatgpt-pl` | Personal Loan offers |

**Event types used:**
- `system_eventType = 1` → impression
- `system_eventType = 2` → click
- `system_eventType = 4` → enhanced impression (viewability)

**Standard BE filters apply:** Always filter `ts`, apply US country filter `(user_country IS NULL OR UPPER(user_country) = 'US')`.

---

## Base Population

**Current approach (temporary):** Use the consent table to identify users who opted in to share data with ChatGPT/Claude.

```sql
-- Users who consented to ChatGPTConsent (~9.6K as of 2026-03-13)
SELECT DISTINCT data.numericId.value AS numericId
FROM `prod-ck-abl-data-53.service_bus_streaming_etl.usermanagement_opt_in_etl`
WHERE data.consentInfo.product = 'ChatGPTConsent'
  AND data.consentInfo.consentAction = 'Consented'
```

> **Caveat:** This may not be the best population definition long-term. It's the fastest proxy available. Revisit whether a BE-based or registration-based definition is more accurate.

---

## Key Metrics

### DAU (Daily Active Users)
Count distinct `user_dwNumericId` per day on ChatGPT surfaces:
```sql
COUNT(DISTINCT user_dwNumericId)
-- WHERE content_screen IN ('credit-factor-chatgpt-widget', 'lbe-openai-chatgpt')
-- AND system_eventType IN (1, 2, 4)  -- impressions, clicks, enhanced impressions
```

Split by user type using `user_hasAuth`:
- `user_hasAuth = true` → logged-in CK member (most Offers traffic)
- `user_hasAuth IS NULL` → auth status unknown (most Credit Factors traffic)
- `user_hasAuth = false` → explicitly unauthenticated (rare in observed data)

### Click Rate
```
clicks / impressions
-- WHERE system_eventType = 2 (clicks) / system_eventType = 1 (impressions)
```

### Sessions
**Definition:** 60-minute inactivity gap = new session.

Per-user session assignment uses `ts` ordered by time, with a new session starting when the gap from the previous event exceeds 60 minutes. Use `LAG()` window function over `ts` partitioned by `user_dwNumericId`.

---

## Attribution: ChatGPT → CK Login Funnel

Users can click through from ChatGPT to land on Credit Karma. Since consistent URL redirect tracing may not exist, analysts use **time-based proxies**:

1. **Click → Login (2-min window):** A CK login event within 2 minutes of a ChatGPT click is attributed to that click.
2. **Login → Credit Tab (2-min window):** A credit tab visit within 2 minutes of login is attributed to the ChatGPT-originated session.

> **Caveat:** These are proxies. They avoid needing to string together trace/cookie/session IDs but may over- or under-attribute. Confirm with the analyst if tighter attribution is available.

---

## Revenue Attribution (Proxy, Validated 2026-03-14)

Same-day proxy: ChatGPT offer clicker → FTRE revenue on the same `clickdate`. Standard 14-day aging filter applied.

**Results (last 90 days, as of 2026-03-14):**
- 146 total offer clickers; 4 with same-day revenue (2.7%)
- CC: 3 users, $442.50 — all `isConversion = 1`, `isFunded = 0` (correct for CC — conversion is the terminal signal)
- PL: 1 user, $285.00 — `isFunded = 1` (correct for PL)
- Total attributed revenue: $727.50

**Query notes:**
- Use `vertical` field (not `LOB`) to categorize — LOB can contain non-vertical values (e.g., "ITA")
- For CC, use `isConversion = 1` as the completion signal; for PL, use `isFunded = 1`
- Population is tiny; results are directional only, not statistically meaningful

---

## Known Tracking Gap: BE → FTEE (Validated 2026-03-13)

**ChatGPT offer clicks do NOT flow to FTEE.** The `content_impressionId` from ChatGPT BigEvent clicks has zero matches in `fact_tracking_event_ext.impressionId`. This was validated both via direct join and via a 10-minute time-window match on the same user — zero FTEE events found for any ChatGPT clicker.

**Impact:** Revenue attribution via the standard BE → FTEE → FTRE chain is impossible for ChatGPT offers. Revenue analysis requires either:
1. Time-based proxy attribution (see Attribution section above)
2. Engineering fix to wire ChatGPT click tracking into FTEE

---

## V1 vs V2

The analyst queries distinguish V1 and V2 versions. Key differences:
- **V1:** Credit Factors widget (`credit-factor-chatgpt-widget`) and Offers (`lbe-openai-chatgpt`)
- **V2:** Same surfaces with updated offer logic; V2 queries use additional section filtering on `content_section` for `-pl` and `-cc`

When querying, always ask the user which version context they need, or default to including both.

---

## Tables Used

| Table | Purpose |
|---|---|
| `kafka_sponge.sponge_BigEvent` | Impressions, clicks, pageviews on ChatGPT surfaces |
| `service_bus_streaming_etl.usermanagement_opt_in_etl` | Consent-based population (temporary) |
| `dw.fact_member_active_daily` (FDMA) | Login activity for DAU cross-reference |
| `dw.userstatus_ext` | Demographics for consented population |
