# Schema: Matched Members (matchedMembers)

**Table:** `prod-ck-abl-data-53.dw.matchedMembers`
**Alias:** matchedMembers
**Grain:** One row per `numericId` — dimension table tracking key lifecycle timestamps for every CK member
**Partition Key:** None — full table scan; filter via JOIN to a partitioned table when possible
**Geography:** US-only by design

## Key Identifiers
- `numericId` (INT64) — primary key; join to FDMA, FTRE, FTEE, SRRF on this field
- `originalId` (INT64) — if user deactivated and re-registered, this links their new numericId back to the previous one

## Lifecycle Timestamps (all INT64, epoch seconds — convert with `TIMESTAMP_SECONDS()`)
- `registrationTs` — user began registration
- `matchedTs` — credit file matched at bureau (user became a matched member)
- `creditSuccessTs` — successful credit pull
- `firstReportTs` — first credit report pulled
- `validationTs` — user confirmed identity and accepted Terms of Agreement; use as completion marker for new account creation. **Validated at 94% match rate against `completed_toa` in SRRF for OpenAI users (2026-02-15 to 2026-03-15)**
- `createdTs` — row created in this table
- `updatedTs` — row last updated
- `deactivationTs` / `deactivationTs_new` — account closed; numericId deprecated on deactivation
- `thinfileRemovedTs` — thin file status resolved

## Quality Flags (INT64, 0/1)
- `isDuplicate` — duplicate account flag; always filter `isDuplicate = 0` for clean member counts
- `isFakeuser` — fake user flag; always filter `isFakeuser = 0` for production queries
- `isPreCreditTransient` — user is in pre-credit transient state
- `isPostCreditTransient` — user is in post-credit transient state
- `isfirstscoreThinFile` — thin file at first score
- `isuserThinFile` — currently a thin file user
- `isDeactivated_masterId` (INT64)

## Duplicate / Re-registration Tracking
When a user closes their account, their `numericId` is deprecated and `deactivationTs` is set. If they return and create a new account, a new `numericId` is issued. The `originalId` field on the new record points back to the prior `numericId`. The `org_*` fields preserve the original timestamp values from the prior account:
- `org_matchedTs`, `org_validationTs`, `org_registrationTs`, `org_deactivationTs`

## Fields Not Yet Documented
- `isCreditInvisible`
