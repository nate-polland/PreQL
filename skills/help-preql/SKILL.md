---
name: help-preql
description: |
  Overview of what PreQL can do, how to use it, and available commands. A reference that any user can invoke at any time.

  Trigger phrases: "/help-preql", "how do I use this", "what can you do", "what does PreQL do", "show me the commands", "what are my options"
---

# PreQL — How to Use This Tool

Display the following as a clean, readable overview. Keep it conversational — this is a reference, not a manual.

---

## What PreQL Is

PreQL translates plain-English questions into validated SQL. You ask a question, it figures out the right tables and logic, generates the SQL, validates it, and returns a plain-English summary alongside the query.

**Data warehouse access is read-only.** PreQL cannot write, modify, or delete data.

---

## How to Ask Questions

Just type your question. Examples:

- *"How many new users registered last month, broken down by platform?"*
- *"What was the signup funnel conversion rate over the last 30 days?"*
- *"Did experiment X significantly improve registration completion rate?"*
- *"How many dormant users reactivated in Q1?"*

**Tips:**
- Be specific about time windows — "last 30 days", "Q1 2025"
- Name the metric you care about — "conversion rate", "revenue", "registrations"
- You don't need to know which table — PreQL figures that out
- Ask follow-ups freely — you can refine any answer in the same session

---

## Built-in Commands

| Command | What it does |
|---|---|
| `/funnel-discovery` | Maps an unfamiliar product funnel end-to-end and saves a reusable doc |
| `/funnel-decomposition` | Decomposes a documented funnel into path-based cohorts — % of users and completion rate |
| `/update-funnel` | Updates an existing funnel doc with new findings, step counts, or flowchart changes |
| `/experiment-design` | Power calculation + hypothesis doc + experiment setup checklist before shipping an experiment |
| `/metric-investigation` | Diagnoses an unexpected metric movement — data quality first, then dimension breakdown |
| `/add-table-schema` | Documents a new data warehouse table so the team can query it |
| `/update-table-schema` | Updates an existing schema doc (new fields, validated flags, join key changes) |
| `/data-lineage` | Traces where a table comes from, how it's built, and whether it's reliable |
| `/contribute` | Push local changes (new schemas, funnels, fixes) back to GitHub |
| `/sync` | Pull the latest updates from GitHub safely, handling local changes and conflicts |
| `/onboard` | Setup check + guided orientation for new users |
| `/help-preql` | This overview |

---

## What PreQL Knows

PreQL has pre-loaded knowledge of your team's key tables, join patterns, and business logic:

- **Tables:** All tables documented in `Schema/` — add new ones with `/add-table-schema`
- **Business rules:** Revenue aging, partition safety, join key validation (see `Context/`)
- **Funnel docs:** Documented product funnels in `Funnels/` — add new ones with `/funnel-discovery`
- **Segment definitions:** User population definitions in `Segments/`

---

## What to Expect in Responses

Every answer follows the same structure:
1. **Plain-English summary** — what the query measures and what it found
2. **Caveats** — any approximations, exclusions, or limitations to know about
3. **SQL** — clean, copy-pasteable query at the bottom

---

## Contributing

If you document a new table or funnel, it can be shared with the whole team via a GitHub PR. See `CONTRIBUTING.md` in the repo for details.

---

## Keeping PreQL Up to Date

New schemas, funnels, and skills get added regularly. Run `/sync` to pull the latest safely — it handles local changes, conflicts, and re-links any new skills automatically.

You can also pull manually if you prefer:
```bash
cd path/to/PreQL && git pull && bash scripts/install-skills.sh
```
