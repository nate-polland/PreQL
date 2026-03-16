# Cross-Table Join Keys and Country Filters

**Validated:** 2026-02-03 (2-hour window, PL impressions + click events)
**Methodology:** null rate analysis → join validation → partner mapping

---

## Join Keys: BE → FTEE → FTRE

### BE → FTEE (Impression to Click)

| Join Field | BE Side | FTEE Side | Null Rate (BE) | Null Rate (FTEE) | Recommendation |
|---|---|---|---|---|---|
| **impressionId** | `content_impressionId` | `impressionId` | ~0% | 0% | **USE THIS** |
| beImpressionId | `content_impressionId` | `beImpressionId` | ~0% | 25.3% | Avoid — drops 1 in 4 FTEE rows |
| impressionIdV2 | `impressionIdV2` | `impressionIdV2` | 1.6% | 0% | Secondary option |

**Recommended join:**
```sql
JOIN `prod-ck-abl-data-53.dw.fact_tracking_event_ext` ftee
  ON be.content_impressionId = ftee.impressionId
```

> **Note:** BE impressions are 1-to-many with FTEE clicks (user can click multiple times from one impression). Use `DISTINCT` or aggregate carefully when joining.

### Darwin → FTRE (Experiment to Revenue)

**Check experiment status first** — `rampEndDate` is NULL for live (still-running) experiments. Always run this before writing the join:

```sql
SELECT
  testName, testType,
  rampStartDate, rampEndDate,  -- NULL rampEndDate = experiment still live
  COUNT(*) AS total_users,
  COUNTIF(reseed_flag = 1) AS reseeded_users,
  COUNT(DISTINCT groupName) AS num_variants,
  STRING_AGG(DISTINCT groupName ORDER BY groupName) AS variant_names
FROM `prod-ck-abl-data-53.dwdarwinviews_standard.mt_final_{EXPERIMENT_ID}`
GROUP BY 1, 2, 3, 4
```

Then join using the appropriate end date:

```sql
FROM `prod-ck-abl-data-53.dwdarwinviews_standard.mt_final_{EXPERIMENT_ID}` d
JOIN `prod-ck-abl-data-53.dw.fact_tracking_revenue_ext` ftre
  ON ftre.numericId = d.numericId
  AND CAST(ftre.eventDate AS DATE) >= DATE(d.rampStartDate)
  -- For closed experiments: DATE_ADD(DATE(d.rampEndDate), INTERVAL <aging_days> DAY)
  -- For live experiments: CURRENT_DATE() or a user-specified cutoff
  AND CAST(ftre.eventDate AS DATE) <= <end_date>
  AND ftre.country = 'US'
WHERE d.first_bin_flag = true
  AND d.reseed_flag = 0
```

> **Validated:** 2026-03-13 against experiment 71788 (PL AMA Entrypoint Phase 0). Match rate ~20% of experiment users had PL clicks — reasonable for a PL experiment where not all users browse PL offers.

---

### FTEE → FTRE (Click to Revenue)

| Join Field | FTEE Side | FTRE Side |
|---|---|---|
| **trackingEventId** | `trackingeventId` | `trackingEventId` |

```sql
JOIN `prod-ck-abl-data-53.dw.fact_tracking_revenue_ext` ftre
  ON ftee.trackingeventId = ftre.trackingEventId
```

### Full Chain: BE → FTEE → FTRE

```sql
FROM `prod-ck-abl-data-53.kafka_sponge.sponge_BigEvent` be
JOIN `prod-ck-abl-data-53.dw.fact_tracking_event_ext` ftee
  ON be.content_impressionId = ftee.impressionId
  AND ftee.eventDate = '<date>'
  AND ftee.tuFakeUserClick = 0
JOIN `prod-ck-abl-data-53.dw.fact_tracking_revenue_ext` ftre
  ON ftee.trackingeventId = ftre.trackingEventId
  AND CAST(ftre.eventDate AS DATE) = '<date>'
```

---

## Country Filters — Default to US Only

**Rule:** Always filter to US unless the question explicitly asks about Canada or global traffic.

| Table | Country Field | US Filter | Notes |
|---|---|---|---|
| BigEvent (BE) | `user_country` (STRING) | `(user_country IS NULL OR UPPER(user_country) = 'US')` | US users have NULL country; CA users have 'CA' or 'ca'. ~0.2% of events are Canadian. |
| FTEE | `country` (STRING) | `country = 'US'` | 4 CA rows per day (negligible) |
| FTRE | `country` (STRING) | `country = 'US'` | ~0.9% CA revenue |
| FDMA | None | No filter needed | No country column — US-only by design |
| UserStatus | None | No filter needed | No country column — US-only by design; uses US state/zip geography |

**BE US filter note:** US users do not get a country code — their `user_country` is NULL. Only non-US users are tagged. Do NOT filter `user_country = 'US'` (no rows would match). Use `user_country IS NULL` or the full expression above.

---

## Partner ID Mapping: BE → FTEE/FTRE

`content_providerId` in BigEvent uses lowercase internal slugs. `partner` in FTEE/FTRE uses display names.

**Validated via:** `BE.content_impressionId = FTEE.impressionId` join on 2026-02-03

### Personal Loans

| BE `content_providerId` | FTEE/FTRE `partner` | `vertical` | `LOB` | Notes |
|---|---|---|---|---|
| `onemainfinancial` | OneMain | Personal Loans | ITA | |
| `onemainpq` | OneMain | Personal Loans | PQ | Separate PQ product |
| `upstart` | Upstart | Personal Loans | ITA | |
| `sofi` | SoFi | Personal Loans | ITA | |
| `lendingclub` | Lending Club | Personal Loans | ITA | |
| `marlette` | Marlette | Personal Loans | ITA | |
| `upgrade` | Upgrade | Personal Loans | ITA | |
| `avantcredit` | AvantCredit | Personal Loans | ITA | |
| `prosper` | Prosper | Personal Loans | ITA | |
| `plskopos` | SpringLight | Personal Loans | ITA | Main SpringLight product |
| `CANPLSpringFinancial` | SpringLight (CA) | Personal Loans | — | Canadian market — exclude in US queries |
| `bankershealthcaregrouppersonalloan` | BHG Financial | Personal Loans | — | |
| `reachpersonalloan` | Reach Financial | Personal Loans | — | |
| `markiiipersonalloans` | Mark III | Personal Loans | — | |
| `opportunityloans` | OppLoans | Personal Loans | PQ | |
| `rocketpersonalloan` | Rocket Personal Loan | Personal Loans | — | |
| `zendablepersonalloan` | Zendable | Personal Loans | — | |
| `splashfinancialpersonalloan` | Splash Financial | Personal Loans | — | |
| `lendingpoint` | LendingPoint | Personal Loans | — | |
| `avenpersonalloan` | Aven | Personal Loans | — | |
| `discoverpersonalloan` | Discover Personal Loan | Personal Loans | — | |
| `payoff` | Payoff | Personal Loans | — | |
| `pllendmark` | Lendmark | Personal Loans | — | |

### Credit Cards

| BE `content_providerId` | FTEE/FTRE `partner` |
|---|---|
| `CCCapitalOne` | Capital One |
| `CCGenesis` | Genesis |
| `CCCreditOne` | Credit One |
| `CCCitiBank` | CitiBank |
| `CCChase` | Chase Bank USA, NA |
| `CCAtlanticus` | Atlanticus |
| `CCAmericanExpress` | American Express |
| `CCCapitalBank` | Capital Bank |
| `CCDiscover` | Discover Card |
| `CCWellsFargo` | Wells Fargo |
| `CCOneMain` | OneMain Credit Cards |
| `CCAvant` | AvantCredit |
| `CCMissionLane` | LendUp |
| `CCBankofAmerica` | Bank of America |
| `CCUSAA` | USAA |
| `CCPetal` | Petal |
| `ccperpay` | Perpay Credit Cards |
| `ccrobinhood` | Robinhood |
| `ccpaypal` | PayPal |
| `ccseen` | Seen |
| `synovusban` | First Progress |
| `merrickban` | Merrick Bank |
| `selffinancial` | Self Financial |
| `yendo` | Yendo |

### Auto

| BE `content_providerId` | FTEE/FTRE `partner` | `vertical` |
|---|---|---|
| `carvana` | Carvana | Auto Purchase |
| `truecar` | TrueCar | Auto Purchase |

### Auto Insurance

| BE `content_providerId` | FTEE/FTRE `partner` | Notes |
|---|---|---|
| `Progressive` | Media Alpha | Auto Insurance |
| `Progressive_eo` | Progressive EO | Auto Insurance |
| `State Farm` | Media Alpha | Auto Insurance |
| `Allstate` | Media Alpha | Auto Insurance |
| `Root_eo` | Root EO | Auto Insurance |
| `Geico_eo` | Geico EO | Auto Insurance |

---

## SRRF → matchedMembers

Join on `numericid`. Only valid for rows where `numericid IS NOT NULL` (~10% of SRRF rows; the rest are pre-auth anonymous sessions).

**Validated:** `completed_toa = 1` users match to `matchedMembers.validationTs` at 94% (29/31 OpenAI users, Feb–Mar 2026).

```sql
JOIN `prod-ck-abl-data-53.dw.matchedMembers` mm
  ON srrf.numericid = mm.numericId
WHERE srrf.numericid IS NOT NULL
```

---

## SRRF → BigEvent

Two join paths depending on auth state:

- **Auth users (post-auth events only):** join on `srrf.numericid = be.user_dwNumericId`
- **Cross-auth sessions (pre + post auth):** join via `srrf.cookieId = be.user_cookieId`, gated on `COUNT(DISTINCT numericId) = 1` per cookieId. Approximately 0.1% of cookieIds map to 2+ numericIds (shared device / browser reset) — exclude these or disambiguate by timestamp.

**Note:** A user session can span multiple `user_traceId` values (new traceId issued at page reloads and at the auth boundary). CookieId is the cross-boundary stitch key. Always validate 1:1 cardinality before using cookieId as a session identifier.

---

## NULL Rows in BE (on FTEE join)

When joining BE → FTEE, some rows return `NULL` for `be_providerId`. This means FTEE clicks where the BigEvent impression was not fired (e.g., direct deep-link clicks, older traffic before BE rollout). These are valid clicks and should not be excluded from FTEE/FTRE analysis — just understand they cannot be traced to a specific impression.

---

## Caveats

- **Join completeness:** BE → FTEE on `content_impressionId = impressionId` is the best available join but may still miss some events. The `beImpressionId` field in FTEE (25% null) was intended for this join but has significant population gaps.
- **Partner mapping completeness:** Table above covers only partners observed in a 2-hour window on 2026-02-03. Additional partners may exist for less common verticals (savings, home, etc.). Run the sampling query at the bottom of this file to extend coverage.
- **Canadian providers:** `CANPLSpringFinancial` and any provider IDs starting with `CAN` are Canadian market products. Exclude via `user_country IS NULL` on BE side or `country = 'US'` on FTEE/FTRE.

---

## Sampling Query (extend mapping coverage)

Run this with a different date or vertical filter to discover additional partner mappings:

```sql
SELECT
  be.content_providerId AS be_providerId,
  ftee.partner AS ftee_partner,
  ftee.vertical AS ftee_vertical,
  ftee.LOB AS ftee_lob,
  COUNT(*) AS matched_events
FROM `prod-ck-abl-data-53.kafka_sponge.sponge_BigEvent` be
JOIN `prod-ck-abl-data-53.dw.fact_tracking_event_ext` ftee
  ON be.content_impressionId = ftee.impressionId
WHERE be.ts BETWEEN '<start>' AND '<end>'
  AND (be.user_country IS NULL OR UPPER(be.user_country) = 'US')
  AND ftee.eventDate = '<date>'
  AND ftee.tuFakeUserClick = 0
  AND ftee.country = 'US'
GROUP BY 1, 2, 3, 4
ORDER BY matched_events DESC
```
