---
status: finalized
last_validated: 2026-03-13
---

# Schema: Revenue Data (FTRE)

**Table:** `prod-ck-abl-data-53.dw.fact_tracking_revenue_ext`
**Alias:** `FTRE`
**Grain:** Multiple rows per user per day — event/click level
**Partition Key:** `clickdate` (STRING, `YYYY-MM-DD`) — always filter this before joining

## CRITICAL: Revenue Aging Rule
See `Context/revenue-aging.md` for per-vertical windows (CC 7d, PL 30d, default 14d). Always apply unless user explicitly requests un-aged data.

## Event Metadata
- `trackingEventId` (INT64) — primary event ID linking clicks to partner data
- `impressionId`, `beImpressionId`, `beimpressionIdV2`, `impressionIDV2` (STRING) — impression identifiers
- `recommendationId` (STRING) — Jarvis algorithmic recommendation ID
- `traceId` (STRING) — UUID for a user's unique analytical session
- `eventcode` (STRING) — event type (e.g., `TakeCCOffer`, `ViewDetails`)
- `eventcodelabel` (STRING) — human-readable label for eventcode
- `eventinfo` (STRING) — additional event metadata
- `clickdate` (STRING) — date of click on platform; primary partition key
- `numericId` (INT64) — user identifier; primary join key

## Product & Offer Details
- `partner` / `advertiserName` (STRING) — external financial partner name (e.g., Chase, Amex)
- `vertical` (STRING) — **preferred field for vertical categorization** (e.g., Personal Loans, Credit Cards, Auto Refinance)
- `LOB` (STRING) — line of business; less reliable than `vertical` — can contain non-vertical values (e.g., approval odds tier "ITA"). Use `vertical` instead.
- `offerName` / `offerId` (STRING) — specific product identifiers
- `approvalBadge` (STRING) — probability badge shown to user (e.g., "Excellent", "Good")
- `approvalBadge_external` (STRING) — badge as reported by partner
- `offerRank` / `sectionRank` (INT64) — visual position of offer on screen
- `screen` / `section` / `originationScreen` (STRING) — page context of event

## Funnel Progression Flags
Note: flags are INT64 (0/1) except where noted as BOOL.
- `isApplication` (INT64) — user applied on partner site
- `isApproval` (INT64) — user was approved
- `isLead` (INT64) — lead generated
- `isLocked` (INT64) — rate locked
- `isFunded` (INT64) — loan funded
- `isConversion` (INT64) — successful conversion
- `isDeclined` (INT64) — application declined
- `isIncomplete` (INT64) — application incomplete
- `isLightbox` (BOOL) — offer shown in lightbox format
- `isEasyApply` (BOOL) — easy apply flow used
- `isBillingExcluded` (BOOL) — excluded from billing
- `Velocify_flag` (BOOL) — Velocify lead system flag

## Financial Amounts

### Revenue
- **`amount_USD` (FLOAT64) — USE THIS for revenue.** Sum this field for total revenue calculations.

### Loan Amounts
- `amountApproved` (FLOAT64) — loan amount the bank approved the user for. CK earns ~3% of funded PL loans as revenue.
- `amountFunded` (FLOAT64) — total loan volume originated
- `amountApplied` / `amountLocked` / `amountListed` (FLOAT64) — other funnel stage amounts

### Other Pricing Fields
- `amount` (FLOAT64) — commission paid to platform
- `basePrice` / `lbAmount` / `legacyAmount` (FLOAT64) — pricing components

### DO NOT USE for Revenue
- `lbRevMarEst` (FLOAT64) — lightbox revenue margin estimate; misleading, avoid

## Loan Details
- `loanAPR` (FLOAT64), `loanTerm` (INT64) — APR and term
- `ltv` (FLOAT64) — loan-to-value ratio (auto/mortgage)
- `loanType` (STRING)
- `income` (FLOAT64) — applicant income

## Dates (all STRING except FICOdate)
- `eventdate` (STRING) — date of partner-site application
- `approvalDate` (STRING) — date of approval
- `fundedDate` (STRING) — date of funding
- `decisionDate` (STRING) — date of decision
- `FICOdate` (DATE) — date of FICO score pull (only native DATE column in table)

## Credit Context at Event Time
- `TUScore` (INT64) — Transunion score at click time
- `TUScoreBand` (STRING) — score band at click time
- `FICOscore` (INT64), `FICOscoreband` (STRING) — FICO score and band
- `age` (INT64), `ageBand` (STRING) — age at click time

## Platform Context
- `platform` / `subplatform` (STRING) — platform of click event
- `bePlatform` (STRING) — backend platform
- `channel` / `subChannel` (STRING) — marketing channel
- `osType` (STRING) — operating system

## Columns to Use With Care
- `payoutExclusion` (INT64) — excluded from payout calculations; check before summing `amount`
- `tuFakeUserClick` (INT64) — fake/test user click; filter `= 0` for production queries
