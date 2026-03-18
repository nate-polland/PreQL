# Revenue Attribution

Validated: 2026-03-18 (sample date: 2026-03-10, US, tuFakeUserClick=0)

---

## Attribution Chain Coverage

The full chain is: funnel impression (BigEvent) → click (FTEE) → revenue (FTRE)

| Link | Coverage | Notes |
|---|---|---|
| FTRE → FTEE | **98.8%** | 1.2% of FTRE rows have no FTEE match (deep-link clicks, legacy traffic pre-BE rollout). 98.6% of conversion events specifically are matched. |
| FTEE impressionId | **100%** non-null | Every FTEE click has an `impressionId` populated — the preferred join key to BigEvent (`be.content_impressionId = ftee.impressionId`). |
| FTEE beImpressionId | **69.5%** non-null | Secondary join path to BigEvent; avoid using this — has 30.5% null rate. |
| FTRE numericId | **100%** non-null | All revenue events are tied to an authenticated user. Safe to aggregate at user level. |
| FTEE numericId | **100%** non-null | All click events are tied to an authenticated user. |
| FTEE cookieId | **53.2%** non-null | Only half of FTEE clicks have a cookieId. Pre-auth session tracing is incomplete via FTEE alone. |

**Implication:** The FTRE→FTEE→BE chain is highly complete (98.8% at the click level). The gap is at the **pre-auth funnel → revenue** attribution layer: anonymous funnel entrants (BigEvent, cookieId only) cannot be traced forward to FTRE directly because the stitch key changes at authentication. See "Registration → Revenue Attribution" below.

---

## Revenue Event Type Hierarchy

`isConversion = 1` is the gating flag — all revenue comes from conversion events. Never filter on other flags alone.

| Event type | Avg revenue/event | Notes |
|---|---|---|
| `isConversion=1, isFunded=1` | ~$404 | Funded loans — highest value. Primarily PL and Auto Refi. |
| `isConversion=1, isApproval=1, isFunded=0` | ~$108 | Approved but not yet funded — largest revenue bucket by total. |
| `isConversion=1, isApplication=0` | ~$39 | Lead-based or non-application conversions (insurance, auto purchase). |
| `isConversion=0` | $0 | Applications, approvals with isConversion=0 carry no revenue. Do not sum these. |

**isConversion=0 events:** These are real events (applications, approvals) that were not converted into revenue — e.g., declined applications, incomplete applications, or partner events that don't trigger a CK payout. They are valuable for funnel measurement but irrelevant for revenue calculations.

---

## payoutExclusion — Correct Filter

`payoutExclusion` is an INT64 field with three states:

| Value | Meaning | Include in revenue? |
|---|---|---|
| `NULL` | Exclusion tracking not applicable to this event type (common for insurance, auto, mortgage) | **Yes** |
| `0` | Applicable and NOT excluded | **Yes** |
| `1` | Applicable and EXCLUDED from payout | **No** — 3.7% of rows, primarily PL (~$400K/day) |

**Correct filter:** `(payoutExclusion IS NULL OR payoutExclusion = 0)`

**Do NOT use:** `payoutExclusion IS NULL` alone — this drops 29% of rows ($2.5M/day) that are valid revenue events with `payoutExclusion = 0`. PL and CC are the primary verticals with `payoutExclusion = 0` events.

The schema doc note ("check before summing `amount`") is referring to filtering out `payoutExclusion = 1`. The correct interpretation is: exclude only the `= 1` rows.

---

## Revenue by Vertical (Feb 2026, aged)

| Vertical | Revenue (15 days) | Conversions | Revenue / Conversion |
|---|---|---|---|
| Credit Cards | $32.5M | 194K | $167 |
| Auto Insurance | $9.8M | 232K | $42 |
| Personal Loans | $7.5M | 21.8K | $343 |
| Auto Refinance | $1.9M | 3.7K | $503 |
| Mortgage | $1.0M | 10.6K | $95 |
| Auto Purchase | $578K | 17.7K | $33 |
| Life Insurance | $64K | 94 | $679 |

Credit Cards dominates total revenue; Personal Loans and Auto Refinance dominate per-conversion value.

---

## Registration → Revenue Attribution

**Goal:** Attribute revenue to users who registered (or reactivated) via a specific funnel entry point — e.g., "LBE Intuit registrants who converted on a financial product within 30 days."

**Why the direct chain breaks:** LBE/ChatGPT funnel entrants arrive anonymously (cookieId in BigEvent). The stitch key changes at authentication (new numericId issued). FTRE uses numericId, not cookieId — so you cannot join pre-auth funnel events directly to FTRE.

**Recommended path via SRRF:**
```sql
-- Step 1: Get registrants from the target funnel and their post-auth numericId
registrants AS (
  SELECT
    srrf.numericid,
    DATE(srrf.session_start_ts) AS registration_date  -- confirm timestamp field name in srrf.md
  FROM `[srrf_table]` srrf
  WHERE DATE([partition_field]) BETWEEN '[start]' AND '[end]'
    AND [funnel entry filter]   -- e.g., content_feature = 'LBESeamlessRegistration'
    AND srrf.numericid IS NOT NULL
),

-- Step 2: Join to FTRE by numericId within a time window post-registration
revenue AS (
  SELECT
    r.numericid,
    SUM(ftre.amount_USD) AS revenue_usd,
    COUNTIF(ftre.isConversion = 1) AS conversions,
    MIN(CAST(ftre.clickdate AS DATE)) AS first_conversion_date
  FROM registrants r
  JOIN `prod-ck-abl-data-53.dw.fact_tracking_revenue_ext` ftre
    ON ftre.numericId = r.numericid
    AND CAST(ftre.clickdate AS DATE) BETWEEN r.registration_date
                                         AND DATE_ADD(r.registration_date, INTERVAL 30 DAY)
  WHERE CAST(ftre.clickdate AS DATE) BETWEEN '[start]' AND DATE_ADD('[end]', INTERVAL 30 DAY)
    AND ftre.country = 'US'
    AND ftre.tuFakeUserClick = 0
    AND (ftre.payoutExclusion IS NULL OR ftre.payoutExclusion = 0)
  GROUP BY 1
)
```

**Caveats:**
- SRRF has `numericid IS NOT NULL` only for ~10% of rows (post-auth sessions); pre-auth anonymous sessions don't have it
- The 30-day window is a convention — adjust based on product context
- Revenue aging still applies: use `CAST(ftre.clickdate AS DATE) < DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY)` as a trailing cutoff (or vertical-specific windows)
- This measures revenue from registrants, not revenue *caused by* registration — correlation only unless the funnel is compared against a control

---

## Open Questions

- What does `payoutExclusion = 0` specifically represent vs NULL? Likely a partner-tagging difference (credit partners tag all events; insurance/auto don't). Needs confirmation from data engineering.
- The 1.2% FTRE→FTEE orphans: are these concentrated in specific verticals or partners? Not yet profiled.
- FTEE cookieId 53.2% coverage: which platforms / event types lack cookieId? Knowing this would clarify which funnel-to-revenue bridges are available.
