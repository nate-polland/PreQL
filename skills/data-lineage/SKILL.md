---
name: data-lineage
description: |
  Structured investigation into a BigQuery table's origin, build logic, and reliability. Has two paths: Path 1 (understand this table — what it measures, how it's built, what to watch out for) and Path 2 (find a better upstream table — when the pre-agg isn't covering the right population or the user wants to query raw source directly). Always start with Path 1; offer Path 2 if concerns surface.

  Use this skill whenever: the user says "where does this table come from", "is this table reliable", "what's the lineage of X", "how is this table built", "can I trust these numbers", "this count seems off", "what's the source of truth", "can I query the underlying data directly", or any time a pre-aggregated or summary table is being used and you're not confident it covers the right population. If a count looks wrong, a flag seems inverted, or the user is working from a dashboard or pipeline table, start here.
---

# Data Lineage Investigation

Before starting any investigation, **ask the user what they already know:**

> "Do you have any context on where [table] comes from or how it's built? Or should I trace the lineage?"

If they have context, use it — no need to re-derive what's already known. If they're unsure or the table is undocumented, proceed with Path 1.

There are two paths through this skill. **Always start with Path 1.** After completing it, offer Path 2 if concerns about reliability or coverage surfaced — or if the user specifically wants to query the raw source.

---

## Path 1 — Understand This Table

Goal: document where the table comes from, how it's built, and what it actually measures. This improves context in `Schema/` and helps interpret results correctly. Run this before writing any analysis queries against an undocumented or uncertain table.

### Step 1 — Is it a view or a base table?

```sql
SELECT table_type, ddl
FROM `[project].[dataset].INFORMATION_SCHEMA.TABLES`
WHERE table_name = '[table_name]'
```

- **VIEW**: extract the source reference from the DDL and repeat on it. Keep going until you hit a BASE TABLE or lose access.
- **BASE TABLE**: the table is populated by an external ETL. Move to Step 2.

Proxy views are common in many data platforms — they look like `SELECT * FROM [other_project].[dataset].[table]` with no logic. Follow through them without stopping.

**If you hit a 403 during the chain:** see the **Access Issues** section below before concluding the source is unknown.

### Step 2 — Find the ETL pipeline

Search your team's code repository for the table name. Look for `.sql` files in pipeline directories (Airflow `dags/`, dbt `models/`, etc.). The file with `CREATE OR REPLACE TABLE` or `INSERT INTO [target_table]` is the builder.

```bash
# Example using GitHub CLI (adjust hostname and org as needed):
gh search code "[table_name]" --limit 20

# To read a specific file:
gh api "repos/[org]/[repo]/contents/[path/to/file.sql]" --jq '.content' | base64 -d
```

### Step 3 — Read the ETL SQL

Look for these specifically — they're what determines what the table actually measures:

**Source tables** — What raw tables does the ETL read from? Note whether there are multiple datasets for the same underlying data (e.g., a streaming vs. batch version) — differences between these are often latency only, not a coverage issue. Check your team's data engineering docs for known dataset aliases.

**Cohort filters** — Any `WHERE` clause or `HAVING` that restricts which users or events are included. A filter like `content_feature = 'LBESeamlessRegistration'` excludes users who matched on other features.

**Join type** — `INNER JOIN` silently drops any user who doesn't match both sides. `LEFT JOIN` keeps everyone. An inner join on a secondary table means only users present in both sources appear in the output.

**Grain** — What does one row represent? If rows > distinct users, the table has a sub-user grain and aggregating without deduplication will overcount.

**Data lag** — Does the pipeline run with a lag (e.g., `ds - 2`)? The most recent dates may not yet be fully populated.

**Rolling window** — Does the pipeline delete and rewrite recent data on each run? Historical dates beyond the window may have been removed.

### Step 4 — Document and report

Summarize:
- **Lineage chain**: table A → view B → base table C, built by [repo/file]
- **Raw source**: exact table path the ETL reads from
- **Key filters**: what the ETL applies (cohort filters, join conditions)
- **Grain**: one row per [user/day/session/event]
- **Data lag / rolling window**: if present
- **Caveats for analysis**: what to watch out for when querying this table

If the table has a `Schema/` file, update it with anything newly learned. If not, consider running `/add-table-schema`.

**After completing Path 1:** If the ETL filters seem narrow relative to the analysis, coverage looks suspect, or the user wants to query raw source — offer Path 2:

> "I found that [table] applies [filter X] which may exclude users relevant to your analysis. Want me to trace the upstream raw source to see if that's a better fit?"

---

## Path 2 — Find a Better Upstream Table

Goal: determine whether the raw source table is more appropriate than the pre-agg, and whether it's actually queryable. Run this when Path 1 raises concerns, or when the user explicitly wants to go upstream.

### Step 5 — Validate coverage against raw source

Using the ETL source tables identified in Step 3, run a coverage comparison over a 2–3 day window with stable volume (avoid the last 3–4 days due to pipeline lags):

```sql
-- Pre-aggregated table
SELECT COUNT(DISTINCT [stitch_key]) AS users, COUNTIF([completion_flag] = 1) AS completions
FROM `[pre_agg_table]`
WHERE date BETWEEN '[start]' AND '[end]'
  AND [partner filter if applicable]

-- Raw source
SELECT COUNT(DISTINCT [stitch_key]) AS users
FROM `[raw_source_table]`
WHERE DATE([ts_field]) BETWEEN '[start]' AND '[end]'
  AND [same cohort filter as pre-agg]
```

A gap >10% is worth explaining. Common causes in order of frequency:
1. **Inner join** in the ETL dropping unmatched users
2. **Cohort filter** in the ETL that's narrower than the raw source filter
3. **Data lag** — recent dates not yet populated
4. **Rolling window** — older dates deleted

### Step 6 — Decide and recommend

**Use the pre-agg if:** coverage gap is small and the ETL filters match your analysis. It's faster and pre-validated.

**Use the raw source if:** the ETL filters exclude population you care about, the grain is wrong, or you need a metric the pipeline doesn't compute. Factor in whether the raw source is actually queryable — if access is blocked, document that and recommend the pre-agg with caveats until access is resolved (see Access Issues below).

Recommendation output:
- **Coverage gap**: N% difference vs. raw source, most likely cause
- **Access status**: is the raw source queryable?
- **Recommendation**: use pre-agg as-is / use pre-agg with [caveats] / use raw source with [filter]
- **Open questions**: anything unresolved

---

## Access Issues

When a table returns `Access Denied`:

**1. Check your team's access control system** — many organizations use row-level security, dataset-level permissions, or access control automation. Check if the table is governed by an access catalog or permission system, and request access through the appropriate channel.

**2. Try alternative project paths** — in multi-project data warehouse setups, the same data may be accessible via a proxy view or access-controlled copy in a different project/database. Check with your data engineering team for alternative paths.

**3. Try alternative credentials** — the MCP server may use different credentials than your personal CLI auth. If your warehouse supports it, try the query via CLI using personal credentials to distinguish MCP service account access from personal access issues.

**4. If still blocked:** Direct the user to your team's access request process. Document the block in your summary and recommend using the pre-aggregated table with caveats as a fallback.

---

## Key Rules
- Read-only — SELECT only. No writes to the data warehouse.
- Always run Path 1 first — understand the table before deciding to go upstream
- Follow proxy view chains fully — stopping at the first proxy view misses the real source
- Check JOIN types in the ETL when counts diverge — inner joins are the #1 cause of silent user loss
- When the raw source is blocked, document it and use the pre-agg with caveats rather than leaving the analysis unresolved
- Refer to `CLAUDE.md` for project/environment configuration, MCP vs async guidance, and partition rules
