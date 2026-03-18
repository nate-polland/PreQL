# PreQL

PreQL is a Claude Code based tool for Credit Karma analysts and PMs. You ask a question in plain English and PreQL works with you to write the SQL, validate it, run it, and explain what it found.

---

## How it works

PreQL has three core functions:

1. For existing funnels & tables, ask any question and PreQL will generate and run a query to get you insights.
2. If you want to analyze a funnel or table not yet documented, PreQL will work with you to map the new information end-to-end so you can get insights faster.
3. As you (or others) build new table/funnel mappings, you can push them back into the GitHub repo for others to use.

---

## Built-in commands

| Command | What it does |
|---|---|
| `/funnel-discovery` | Maps a new product funnel end-to-end and saves it as a reusable doc |
| `/funnel-decomposition` | Decomposes a documented funnel into cohorts — % of users and completion rate |
| `/experiment-design` | Power calculation + hypothesis doc + Darwin setup checklist |
| `/metric-investigation` | Diagnoses an unexpected metric movement — data quality first |
| `/add-table-schema` | Documents a new BigQuery table for the team |
| `/data-lineage` | Traces where a table comes from and whether it's reliable |
| `/contribute` | Push local changes back to the shared repo |
| `/sync` | Pull the latest updates from GitHub safely |
| `/help-preql` | Full overview of all commands and capabilities |

Type `/help-preql` at any time to see the complete list.

---

## Getting started

1. Install **Claude** via Workspace ONE Intelligent Hub (search "Claude")
2. Open Claude
3. Copy the contents of **Tab 2** and paste it into the chat — Claude handles the rest

---

## Questions?

- Slack: **#preql** for PreQL questions, **#cmty-claude** for Claude questions
- In-tool: type `/help-preql` at any time
