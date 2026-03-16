# Schema: Experimentation Data (Darwin)

**Table:** `prod-ck-abl-data-53.dwdarwinviews_standard.mt_final_{EXPERIMENT_ID}`
**Alias:** `Darwin`
**Grain:** One row per `numericId × rampId` (online experiments). Validated on `mt_final_71788`: `distinct(numericId, rampId) = total_rows = 47,084`. One row per user for offline experiments.
**CRITICAL:** Every experiment has its own table. You MUST always ask the user for an experiment ID — never use `TABLESUFFIX` literally in a query. Example: `mt_final_12345` for experiment 12345.
**Implementation note:** Each `mt_final_` table is a VIEW over `dwdarwin_staging.mt_final_current` filtered by `testId`. Updated every 6 hours (monitor `#darwin-etl-status`). A view returning 0 rows means the experiment hasn't bucketed users yet or is pending the next pipeline run.
**Join to other tables:** `numericId` (0% null) is the primary join key to FTRE/FTEE. Join with a date filter on `rampStartDate`/`rampEndDate` to scope revenue/events to the experiment window.
**Analysis conventions:** See `Context/experiment-analysis.md` for standard metrics, statistical tests, revenue aging, and sanity checks. Always normalize metrics by user count.

## Online vs Offline Experiments
- **Online:** 1 row per user's first exposure per ramp. Users are bucketed upon a trigger (typically login).
- **Offline:** Users are bulk-assigned before exposure. All users appear at once; new accounts appear in subsequent runs.

## Key Identifiers
- `numericId` (INTEGER) — obfuscated user ID (dwNumericId); joins to other tables. **0% null — always use as primary join key.**
- `cookieId` (STRING) — cookie ID, web only. Not always populated — observed 100% NULL in `mt_final_71788` (USER-type). Population behavior for other experiment types is unvalidated. Not needed for most analyses since `numericId` is the standard join key.
- `deviceId` (STRING) — device ID, mobile only. Not always populated — observed 100% NULL in `mt_final_71788` (USER-type). Population behavior for other experiment types is unvalidated.
- `requestId` (STRING) — unique ID of server request associated with exposure

## Experiment Structure
- `testId` (INTEGER) — experiment ID
- `testName` (STRING) — experiment name
- `groupId` (INTEGER) — variant ID
- `groupName` (STRING) — variant name
- `testType` (STRING) — diversion type: `COOKIE` or `USER`
- `layerid` (INTEGER) — layer the experiment resides in

## Ramp Information
- `rampId` (INTEGER) — ramp ID
- `rampIndex` (INTEGER) — index of ramp in descending chronological order
- `rampStartDate` (DATETIME) — start of ramp (Pacific Time)
- `rampEndDate` (DATETIME) — end of ramp (Pacific Time)
- `layerStartDate` (DATETIME) — start of the layer (Pacific Time)
- `layerEndDate` (DATETIME) — end of the layer (Pacific Time)
- `startDate` (DATETIME) — first time user entered experiment during this ramp (Pacific Time)
- `first_bin_flag` (BOOLEAN) — true if user first entered experiment during this ramp

## Reseeding
- `seed` (INTEGER) — seed associated with the layer
- `seedStartDate` / `seedEndDate` (DATETIME) — seed window
- `previous_seed` (INTEGER) — previous seed if a reseed occurred
- `reseed_flag` (INTEGER) — 1 if reseed occurred in this ramp; 0 otherwise
- **Important:** Always analyze pre- and post-reseed data separately to avoid corrupted results

## User Context at Binning
- `score_at_binning` (FLOAT) — Vantage credit score when user entered experiment. ~3% null.
- `platform_at_binning` (STRING) — Desktop, Mobile App, or Mobile Browser. 0% null.
- `analytics_platform_at_binning` (STRING) — Desktop, iOS, Android, or Mobile Browser. May be 100% null for older experiments.

## Email Campaign Fields
- `isEligible` (INTEGER) — 1 if user eligible for a campaign, 0 otherwise
- `campaignIds` (STRING) — comma-separated campaign IDs user has been eligible for

## Post-Filter Fields

Experiment-specific filters configured by the experiment owner in Darwin. Values are 0/1. If no post-filter was configured for a given source table, the field will be 0 for all users. **Do not apply unless the experiment owner confirms a post-filter was set up.**

- `inPostFilter` (INTEGER) — 1 if user meets the BigEvent (`sponge_BigEvent`) post-filter configured for this experiment
- `inProductUserFacts` (INTEGER) — 1 if user meets the `product_user_factsflat_` post-filter
- `inUserFeatures` (INTEGER) — 1 if user meets the `user_features_` post-filter

Supported diversion types: USER experiments support all three tables; COOKIE experiments support BigEvent only.

## Domain Hierarchy
- `domainId` / `domainName` — domain of the layer
- `parentDomainId` / `parentDomainName` — one level above
- `grantParentDomainId` / `grantParentDomainName` — two levels above

## Unauthenticated Funnel Experiments (Open Question)

USER-type experiments bucket users via `numericId`, which requires authentication. This means:
- The Darwin denominator contains **only users who authenticated** during the ramp window.
- Users who started a funnel pre-auth but never authenticated are **excluded**.
- Conversion rates for funnels with a pre-auth entry point (e.g., registration) will be **biased upward**.
- Whether `cookieId`/`deviceId` could serve as a pre-auth join key for other experiment types is **unvalidated** — this is an open question to resolve when a pre-auth funnel experiment is first needed.
- **If the funnel starts pre-auth, flag this bias explicitly in any experiment analysis and surface the open question.**

## Multi-Layer Note
Users can be in multiple experiments simultaneously — one per layer. Experiments in the same layer cannot overlap (parameters interact); experiments in different layers are orthogonal. When joining Darwin → FTRE/FTEE, you are scoping to one experiment's users; those users may simultaneously appear in other `mt_final_` tables. This is by design and not a data quality issue.
