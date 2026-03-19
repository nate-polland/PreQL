---
name: update-table-schema
description: |
  Interactive workflow for updating an existing Schema/ doc. Use when a table schema has new fields, a field description is wrong, a flag has been newly validated, or a join key coverage rate has changed.

  Use this skill whenever: the user says "update the schema", "add a field to the schema", "the schema is stale", "validate this flag", "add a join key", "fix this field description", "mark this flag as inverted", or any request to modify an existing Schema/ file — even if they phrase it as "just add X" or "the schema is missing Y".
---

# Update Table Schema Workflow

You are a Senior Data Analyst updating an existing data warehouse table schema doc. Always read the source file before proposing any change. Schema docs without frontmatter are treated as `finalized` by default.

## Phase 1 — Read the Existing Doc

Before doing anything:
1. Read the full `Schema/[tablename].md` file
2. Identify the project + dataset + table path from the doc header
3. Note existing caveats, inverted flags, and join key coverage rates

Check `status` in the frontmatter (default `finalized` if absent), then route accordingly.

---

## Route A — `status: finalized`

### Staleness check

If today's date is more than 90 days after `last_validated` AND `stale_snooze_until` is either absent or in the past:

> "This schema was last validated on [date] — [N] days ago. Want to snooze the reminder for 90 days, or kick off a full review?"

- **Snooze**: set `stale_snooze_until: [today + 90 days]` in frontmatter and proceed with the targeted edit
- **Full review**: move `status` to `in_progress`, then follow Route B

### Targeted edits (default for finalized)

A finalized schema can receive small updates at any time — new field descriptions, corrected flag semantics, updated join key coverage rates, new caveats. The bar is: the change is incremental and doesn't require revalidating the full schema.

For each proposed change:
1. Present what the doc currently says and what you propose to change
2. Confirm with the user before editing
3. If the change requires validation, sample cheaply first (3–5 rows, tight date window)
4. Use Edit (not Write) — preserve all unchanged sections
5. Update `last_validated` in frontmatter

---

## Route B — `status: in_progress`

A schema in progress needs a full validate-then-document cycle before being finalized. Work through these stages in order, pausing for user confirmation at each checkpoint.

### Stage 1 — Orient from the doc

Review the existing doc and identify what's confirmed vs. uncertain:
- Fields with unknown definitions or unvalidated semantics
- Flags that may be inverted (especially `regLog_*` prefix pattern)
- Join keys without coverage rates
- Anything marked with ⚠️ or noted as unvalidated

Present a summary and proposed next step. Wait for user confirmation.

### Stage 2 — Diff against current schema (cheap)

Pull the column list from INFORMATION_SCHEMA:
```sql
SELECT column_name, data_type, is_nullable
FROM `[project].[dataset].INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = '[table_name]'
ORDER BY ordinal_position
```

Compare to the existing doc:
- **New columns**: in INFORMATION_SCHEMA but not in the doc
- **Removed columns**: in the doc but not in INFORMATION_SCHEMA
- **Type changes**: present in both with different types

Present the diff. Confirm which changes to address before proceeding.

### Stage 3 — Start small, validate, then expand

For any field or flag that needs validation:

**Start with a small sample (3–5 rows):**
```sql
SELECT [column], [related fields]
FROM `[table]`
WHERE DATE([partition_key]) = '[recent_date]'
  AND [relevant filter]
LIMIT 5
```

Use this to understand what values look like before running population-wide queries.

**For binary flags — validate semantics against ground truth:**
- Never assume `1` = true/success. Flags can be inverted (e.g., `regLog_account_created = 0` means success).
- Compare the flag to a known-good anchor: a completion event, a matched record in another table, or a timestamp that only exists for successes.
- Sample 3–5 confirmed positives and 3–5 confirmed negatives. Does the flag match?

**For join key coverage — validate on a small population first:**
```sql
-- Match rate on a small recent sample
SELECT
  COUNT(*) AS total,
  COUNTIF([join_key] IN (SELECT [key] FROM `[other_table]` WHERE ...)) AS matched,
  COUNTIF([join_key] IN (SELECT [key] FROM `[other_table]` WHERE ...)) / COUNT(*) AS match_rate
FROM `[table]`
WHERE DATE([partition_key]) BETWEEN '[start]' AND '[end]'
LIMIT 1000
```

**Expand after small sample looks stable:**
- Widen to 3 days, then a full week
- Confirm findings hold before documenting

**Checkpoint:** present validation findings to the user before editing the doc.

### Stage 4 — Enrich

After the initial validation pass, investigate fields or patterns that are uncertain or where the small sample raised questions:

1. **Cross-reference with related tables** — if a field is a join key, pull a small sample from the target table and confirm the join semantics (inner vs left, 1:1 vs 1:many)
2. **Trace flag interactions** — if multiple flags exist on the same table (e.g., `total_prove_call`, `success_prove_call`, `completed_toa`), sample users who have different flag combinations to understand the state machine
3. **Check for silent filters** — if the table is built by an ETL, check whether the ETL applies filters that narrow the population (e.g., `content_feature` filter, inner join on another table). Use `/data-lineage` if the ETL source is unknown.
4. **Validate field completeness on the population you care about** — a field may be 100% populated overall but NULL for your specific cohort (e.g., pre-auth users)

Present enrichment findings before proceeding.

### Stage 5 — Validate (random sample)

Run a broader validation pass on a random sample from the table to catch issues the targeted investigation missed:

| Schema complexity | Columns | Flags/joins | Suggested sample |
|---|---|---|---|
| Simple | <20 | 0–2 | 10–15 records |
| Moderate | 20–50 | 3–5 | 25–40 records |
| Complex | 50+ | 6+ | 50–100 records |

For each sampled record:
1. Verify key fields are populated and have expected values
2. Cross-check any flags against their ground truth source
3. Confirm join keys resolve to the expected target table records
4. Note any surprises — new field values, unexpected NULLs, or flag combinations not seen in the small sample

Present findings to the user. Never apply inclusion/exclusion thresholds without asking — surface everything and let the user decide what's significant.

### Stage 6 — Edit the doc

After user confirmation of each finding:
1. Use Edit (not Write) — preserve all unchanged sections
2. Log new columns in the column table (name + type; add definition only if confirmed)
3. Mark removed columns as deprecated, or remove if user confirms they're gone
4. Add ⚠️ caveats for validated findings (inverted flags, coverage gaps, grain issues)
5. Update join key coverage rates with new figures and validation date

### Stage 7 — Update related files

After editing the schema:
1. If new join patterns are introduced, update `Context/cross-table-joins.md`
2. If the change resolves a funnel open question, update the relevant `Funnels/` doc
3. Append one-line entries to `session.md` for each file edited

### Stage 8 — Finalize

After validation is complete and the user is aligned:
1. Update `last_validated` in frontmatter
2. Ask: "Ready to mark this as finalized?"
3. If yes: set `status: finalized` in frontmatter

---

## Transitions

**finalized → in_progress**: When the user questions accuracy or reliability of a finalized schema, ask before moving: "This would kick off a full review — want to move it to in_progress?" Update frontmatter if confirmed.

**in_progress → finalized**: Only at user confirmation after Stage 8. Never auto-finalize.

---

## Key Rules
- **READ ONLY — ABSOLUTE RULE.** SELECT only. No writes to the data warehouse.
- Always read the existing schema file before proposing changes
- Start small (3–5 rows, tight date window) before any population-wide validation
- Never apply inclusion/exclusion thresholds without asking the user — surface all findings with volumes and let them decide
- Validate flag semantics against ground truth — never assume 1 = true/success
- Confirm each change with the user before editing
- Use Edit, not Write — preserve all unchanged sections
- Schema docs without frontmatter default to `finalized`
- Refer to `CLAUDE.md` for project/environment-specific configuration and async query rules

## Sharing Your Work

Schema updates are saved locally. When ready to contribute back to the shared repo, run `/contribute`.
