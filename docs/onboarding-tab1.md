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
| `/help-preql` | Overview of capabilities and commands |
| `/onboard` | Guided setup walkthrough (connection check, orientation, sample query) |
| `/funnel-discovery` | Works with you to map a new product funnel end-to-end and saves it as a reusable doc |
| `/add-table-schema` | Works with you to document a new BigQuery table for the team |
| `/contribute` | Push local changes (new schemas, funnels, fixes) back to the shared repo |

`/funnel-discovery` and `/add-table-schema` are interactive workflows — they ask questions, run diagnostics, and write documentation that becomes available to everyone on the team.

---

## Getting started

1. Install **Claude** via Workspace ONE Intelligent Hub (search "Claude")
2. Open Claude
3. Copy the contents of **Tab 2** and paste it into the chat — Claude handles the rest

---

## Questions?

- Slack: **#preql** for PreQL questions, **#cmty-claude** for Claude questions
- In-tool: type `/help-preql` at any time
