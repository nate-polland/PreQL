---
name: setup
description: |
  First-time team configuration workflow. Walks through populating PreQL's core config files for a new team or environment: analytics environment, business context, revenue/metric aging, geography defaults, and key table paths. Run this once when setting up PreQL for a new team — not for individual user onboarding (use /onboard for that).

  Trigger phrases: "/setup", "set up preql for my team", "configure preql", "first time team setup", "populate the config files", "configure for our environment"
---

# PreQL Team Setup

You are helping configure PreQL for a new team. The goal is to populate the core config files so PreQL understands the team's analytics environment, business context, and data model.

**Work interactively.** Ask one section at a time. Write answers into the right files as you go — don't batch everything at the end.

At any point, the user can say "skip" to leave a section as a placeholder and come back later.

---

## Before Starting

Tell the user:

> "I'm going to walk you through configuring PreQL for your team. This takes about 10–15 minutes and covers your analytics environment, business context, and data model. You can skip any section and fill it in later. Let's start with your data warehouse."

---

## Section 1 — Analytics Environment

Ask:

1. **What data warehouse are you using?** (e.g., BigQuery, Snowflake, Redshift, Databricks, DuckDB, other)
2. **What is your project/database/account identifier?** (e.g., BigQuery project ID, Snowflake account name, Redshift cluster endpoint)
3. **What is the default dataset/schema/database for your team's tables?** (e.g., `dw`, `analytics`, `prod`)
4. **What region or location is your warehouse in?** (e.g., US, EU, us-east-1 — matters for query routing)
5. **Do you have an async query script set up?** (For BigQuery: `bq_async.sh` is included — just needs your project ID. For other warehouses, you'll need to set up an equivalent.)

After collecting answers, update `CLAUDE.md`:

- In the **Query Execution** section, add a note about the specific async tool/script for this environment
- Add a new **## Environment** section near the top with:

```markdown
## Environment

- **Warehouse:** [BigQuery / Snowflake / Redshift / etc.]
- **Project / Account:** [identifier]
- **Default dataset / schema:** [name]
- **Location / Region:** [location]
- **Async execution:** [bq_async.sh / custom script / not configured]
```

If BigQuery: update `bq_async.sh` with the project ID:
```bash
export BQ_PROJECT=[project_id]
```
Or tell the user to set `BQ_PROJECT` as an environment variable before running the script.

Tell the user what you wrote and confirm before moving on.

---

## Section 2 — Business Context

Ask:

1. **What does your company/team do?** (1–2 sentences — e.g., "We're a fintech app that helps consumers improve their credit and find financial products.")
2. **Who are your users?** (e.g., "Registered members who connect their financial accounts")
3. **What are the 2–3 most important metrics your team tracks?** (e.g., "Registration CVR, revenue per user, 30-day retention")
4. **What is your primary revenue model?** (e.g., "We earn revenue when users click on and are approved for financial products — pay-per-approval")
5. **Are there any key business terms that have specific definitions your team uses?** (e.g., "Dormant = no login in 90+ days", "Conversion = account created AND first login")

Create `Context/business-context.md` with the collected information:

```markdown
# Business Context

## Company / Product Overview
[What the company/team does, who the users are]

## Key Metrics
| Metric | Definition |
|---|---|
| [metric 1] | [definition] |
| [metric 2] | [definition] |
| [metric 3] | [definition] |

## Revenue Model
[How revenue is generated — be specific enough that SQL queries can apply the right filters and caveats]

## Key Business Terms
| Term | Definition |
|---|---|
| [term] | [definition] |

---

*Last updated: [date]*
```

Also add any metric-specific terms to `Context/term-disambiguation.md` if they would affect how queries are written (e.g., if "conversion" means something specific in SQL terms).

Tell the user what you wrote and confirm before moving on.

---

## Section 3 — Revenue / Metric Aging

Ask:

1. **Do you track revenue or other metrics that have a reporting lag?** (i.e., data from last week may still be incomplete today)
2. **If yes: what is the lag, and does it vary by product/vertical?**
   - Example: "Credit card revenue is typically complete within 7 days; personal loan revenue takes up to 30 days"
3. **What's a safe default aging window to use when the vertical is unknown?**

Update `Context/revenue-aging.md` with real values in the aging windows table. Replace the placeholder rows with actual verticals and aging buffers.

If no revenue aging applies (e.g., the team doesn't track revenue, or all metrics are real-time), update the file to note this:

```markdown
## Note
This team's metrics do not require an aging buffer — all data is complete within [X hours/days] of the event date.
```

Tell the user what you wrote and confirm before moving on.

---

## Section 4 — Geography Defaults

Ask:

1. **Does your product operate in a single country or multiple?**
2. **What is the default geography filter for queries?** (e.g., "US only", "US + Canada", "global — no filter")
3. **For each table, is geography stored as a column? If so, what are the column name and filter expression?**
   - Example: `country = 'US'` or `(user_country IS NULL OR UPPER(user_country) = 'US')`
   - Note any tables where US users have a NULL country code (common in some event tables)

Update `Schema/00-global-sql-standards.md` — replace the geography section placeholder with real defaults:

```markdown
## Geography / Population Scope

**Default:** [e.g., "Filter to US only unless the user specifies otherwise" or "No geography filter — product is US-only by design"]

Per-table geography filters:
| Table | Field | Filter | Notes |
|---|---|---|---|
| [table] | `[field]` | `[expression]` | [e.g., "US users have NULL country"] |
```

Tell the user what you wrote and confirm before moving on.

---

## Section 5 — Key Tables

Ask:

> "What are the 2–3 most important tables your team queries regularly? We'll stub out schema docs for each so PreQL knows they exist. You can fill in full details with `/add-table-schema` later."

For each table mentioned:

1. **Full table path** (e.g., `project.dataset.table_name`)
2. **What does one row represent?** (grain — e.g., "one event per user per action", "one row per user per day")
3. **What is the partition/date key?** (e.g., `event_date`, `created_at`)
4. **What is the primary user identifier?** (e.g., `user_id`, `cookie_id`)
5. **What is this table mainly used for?** (e.g., "Behavioral event tracking", "Revenue/conversion tracking")

For each table, create a stub `Schema/[tablename].md`:

```markdown
---
status: stub
created: [date]
---

# [Table Name]

**Full path:** `[project.dataset.table_name]`
**Grain:** [one row per ...]
**Partition key:** `[field]` ([type])
**Primary user ID:** `[field]`
**Purpose:** [what this table is used for]

---

## Columns

*Not yet documented. Run `/add-table-schema` to explore and document this table fully.*

---

## Join Keys

*Not yet validated. See `Context/cross-table-joins.md` after running `/add-table-schema`.*

---

## Caveats

*Not yet documented.*
```

If the user mentions cross-table join patterns they already know about, add stub entries to `Context/cross-table-joins.md`.

Tell the user what you created and confirm before moving on.

---

## Section 6 — Experiment Framework (Optional)

Ask: "Does your team run A/B experiments? If so, what platform or table do they live in?"

If yes:
1. **What is the experiment table path?** (e.g., `project.dataset.experiments`)
2. **What does one row represent?** (e.g., "one user assignment")
3. **What are the key fields?** (experiment ID, variant/arm, assignment timestamp, user ID, any flags for clean assignment)
4. **What filters are required for clean analysis?** (e.g., "first_exposure = true AND not_reassigned = true")

Create a stub `Schema/[experiment_table].md` and add the experiment table to `Context/experiment-analysis.md` with the specific table path and filter fields.

If no: skip.

---

## Done

After completing all sections, tell the user:

> "PreQL is now configured for your team. Here's what was set up:"

List every file that was created or updated.

Then say:

> "Next steps:
> - Run `/add-table-schema` to fully document each of your key tables — this is what enables PreQL to write accurate SQL against them
> - Run `/funnel-discovery` to map your first product funnel
> - Ask a plain-English data question to see how it all works together
>
> Individual users joining the team should run `/onboard` to verify their connection and get oriented."
