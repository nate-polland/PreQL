# PreQL

PreQL is a BigQuery analytics tool for CreditKarma analysts and PMs. You ask a question in plain English — PreQL writes the SQL, validates it against the team's business logic, runs it, and explains what it found.

---

## How it works

Every query goes through three steps automatically:

**1. Interpret**
PreQL reads your question and identifies the right tables, metrics, filters, and time window. It defaults to US-only, last 30 days, daily granularity — and states its assumptions before running anything.

**2. Generate & Validate**
A SQL generation agent writes the query. A separate BI validation agent then checks it against the team's standards before it runs — geography filters, partition pruning, revenue aging windows, dedup flags, join keys, aggregation grain. If there's a methodology issue (e.g., reference date anchoring, population precision), it flags it and asks how you want to handle it rather than silently making a choice.

**3. Present**
You get a plain-English summary, any caveats, and the final SQL — ready to copy into BigQuery if you want it.

---

## Built-in commands

| Command | What it does |
|---|---|
| `/help-preql` | Overview of capabilities and commands |
| `/onboard` | Guided setup walkthrough (connection check, orientation, sample query) |
| `/funnel-discovery` | Maps a product funnel end-to-end and saves it as a reusable doc |
| `/add-table-schema` | Documents a new BigQuery table for the team |

`/funnel-discovery` and `/add-table-schema` are interactive workflows — they ask questions, run diagnostics, and write documentation that becomes available to everyone on the team.

---

## Getting started

**Before you begin (one-time, ~15 min):**

1. Complete the **GenAI Tools for our Workforce** training — this gates access to Claude.
2. **Request BigQuery access** if you don't have it: [Airlock BigQuery access request](https://airlock.static.corp.creditkarma.com/bigquery_access/index.html#how-do-i-get-access-to-airlock-bigquery) — takes 1–2 days, so start early.
3. Install **Homebrew** and **Claude Code** via Workspace ONE Intelligent Hub (search "Homebrew" and "Claude Code").

**Then:**

1. Open Terminal, type `claude`, press Enter
2. Copy the contents of **Tab 2** and paste it into the chat
3. Claude walks you through the rest automatically

---

## Questions?

- Slack: **#preql** for PreQL questions, **#cmty-claude** for Claude questions
- In-tool: type `/help-preql` at any time
