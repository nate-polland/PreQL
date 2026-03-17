---
name: add-table-schema
description: |
  Interactive workflow for documenting a new BigQuery table schema. Use when a user wants to add a new table to the Schema/ directory, or when a query references an undocumented table.

  Trigger phrases: "add this table", "document this table", "new table schema", "add schema for", or when a query uses a table with no Schema/ file.
---

# Add Table Schema Workflow

You are a Senior Data Analyst helping document a new BigQuery table. Work interactively with the user. The goal is a useful, accurate schema file — not an exhaustive one. Start with what's needed and expand over time.

## Phase 1 — Collect Business Context First

**Before querying anything**, ask the user:
1. **What will this table be used for?** (What questions do you want to answer with it?)
2. **What other tables does it connect to?** (Joins, enrichment, validation)
3. **Is there a specific query or use case you're starting from?** If yes, use that to guide which fields to prioritize — but don't persist specific filter values in the schema doc. Filters inform understanding, not documentation.

This context guides the entire exploration. Do not skip it.

## Phase 2 — Pull Raw Schema

1. Pull all columns from `INFORMATION_SCHEMA.COLUMNS`:
   ```sql
   SELECT column_name, data_type, is_nullable
   FROM `[project].[dataset].INFORMATION_SCHEMA.COLUMNS`
   WHERE table_name = '[table_name]'
   ORDER BY ordinal_position
   ```
2. Check partition and table options:
   ```sql
   SELECT option_name, option_value
   FROM `[project].[dataset].INFORMATION_SCHEMA.TABLE_OPTIONS`
   WHERE table_name = '[table_name]'
   ```
3. **Start small** — sample 3–5 rows with a tight date filter before running any population-wide queries:
   ```sql
   SELECT * FROM `[table]` WHERE [date_col] >= '[recent_date]' LIMIT 5
   ```

## Phase 3 — Determine Grain

What does one row represent? This is the most important thing to get right.

1. Start with a hypothesis based on the column names
2. Count total rows vs distinct combinations of candidate keys:
   ```sql
   SELECT COUNT(*) AS total,
     COUNT(DISTINCT key1) AS distinct_key1,
     COUNT(DISTINCT CONCAT(CAST(key1 AS STRING), CAST(key2 AS STRING))) AS distinct_key1_key2
   FROM `[table]`
   WHERE [date_col] BETWEEN '[start]' AND '[end]'
   ```
3. If total >> distinct key combos, widen the key until you find what makes rows unique
4. **Check for high-null identifiers** — a key column with 90% nulls (e.g., `numericId` in pre-auth tables) may be expected behavior, not a data quality issue. Document the null rate and what it means.

## Phase 4 — Validate Join Keys

For each candidate join key to existing tables:
1. Check null rate in the new table
2. Test match rate against the related table on a small population
3. Document coverage: "X% of rows join to [table] on [key]"
4. If multiple join keys exist (e.g., numericId for auth users, cookieId for pre-auth), document both with their scope

## Phase 5 — Validate Flag Semantics

For binary INT64 columns (0/1 flags), never assume the name reflects the meaning:
1. Pick a flag and find rows where it = 1
2. Cross-reference against a ground truth (e.g., does `account_created = 1` correspond to records in matchedMembers?)
3. If the flag is inverted, document prominently with ⚠️ and the validation evidence
4. Flag sibling columns with similar naming patterns as potentially inverted too

## Phase 6 — Enrich

After the initial exploration, investigate any field or relationship where the meaning or behavior is uncertain. Enrichment is targeted — pick a specific question (e.g., "does this flag really mean what the name implies?", "what happens when this join key is null?") and find evidence.

**For each uncertain field or relationship:**
1. Identify 3–5 rows that exercise the uncertain behavior (e.g., rows where a flag = 1, rows where a join key is null)
2. Cross-reference against a related table or ground truth to confirm semantics
3. Document findings — update the column definition, add a caveat, or flag as inverted

**Common enrichment targets:**
- Binary flags with ambiguous names → validate against ground truth (Phase 5)
- Join keys with partial coverage → trace the null population to understand why
- Timestamp fields → are they event time or write time? Check for batch patterns.
- Columns that look like they duplicate another table's field → compare values to see if they diverge

Do not skip enrichment to write the schema faster. Wrong definitions are worse than missing ones.

## Phase 7 — Validate

After enrichment, validate the overall schema by sampling random records — not filtered to any specific population or flag value. The goal is to catch field behaviors or patterns that targeted enrichment missed.

**Sample size:** scale with schema complexity. A table with 10 columns and simple grain needs fewer samples than one with 80 columns, multiple join keys, and binary flags.

| Schema complexity | Columns | Flags/joins | Suggested sample |
|---|---|---|---|
| Simple | <20 | 0–2 | 10–15 records |
| Moderate | 20–50 | 3–5 | 25–40 records |
| Complex | 50+ | 6+ | 50–100 records |

Present the suggested sample size to the user with rationale before running.

**Validation checks:**
1. Sample N random records (recent date window, no other filters)
2. For each record, verify that documented fields match their definitions — do flag values align with the cross-referenced ground truth? Do join keys connect as expected?
3. Look for any column with unexpected values (nulls where coverage was documented as 100%, values outside expected ranges, etc.)
4. If anything new surfaces, enrich that specific finding before finalizing

**Checkpoint:** present any new findings to the user. If none, the schema is validated.

## Phase 8 — Write the Schema File

File: `Schema/[tablename].md`

Required sections (always):
- Table path, alias, grain, purpose, partition key (or "None — full scan")
- Critical caveats (null key populations, inverted flags, batch vs real-time, etc.)
- All columns — name and type for every column. Add a definition only where you know it. Leave undescribed columns as name + type only — they're still useful for field discovery.
- Join key section: validated joins with coverage rates

Optional sections (add as needed):
- Mandatory filters (e.g., `isDuplicate = 0`, `country = 'US'`)
- DO NOT USE fields
- Validated queries (e.g., correct completion condition for a funnel)

**Log every column from INFORMATION_SCHEMA**, even if undescribed. A column name with no definition is still useful — it tells future users the field exists in this table and can be investigated. Do not use a "Fields Not Yet Documented" catch-all — just list them inline with name + type.

## Phase 9 — Update Related Files

After writing the schema:
1. If the table introduces new cross-table join patterns, add to `Context/cross-table-joins.md`
2. If the table is used in a funnel, add to the relevant `Funnels/[name].md` Tables section
3. If a funnel open question is answered by this table, resolve it in the funnel doc

## Key Rules
- **READ ONLY — ABSOLUTE RULE.** SELECT only. No writes.
- Business context before querying — always Phase 1 first
- Start small, then grow — cheap sample before population-wide queries
- Log all columns; define what you know, leave the rest as name + type
- Validate flag semantics — never assume 1 = true/success
- Validate join keys with actual match rates before documenting them
- Filters from a user's query inform understanding but are never persisted in schema docs

## Sharing Your Work

The schema you just documented is saved locally and available to you immediately. It is **not yet shared** with the rest of the team. When you're ready to contribute it back to the shared repo, run `/contribute` and PreQL will walk you through the process.
