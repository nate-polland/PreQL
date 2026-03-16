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

**Before you begin (one-time, ~15 min):**

1. Complete the **GenAI Tools for our Workforce** training — this gates access to Claude.
2. Install **Homebrew** and **Claude Code** via Workspace ONE Intelligent Hub (search "Homebrew" and "Claude Code").

**Then:**

1. Open Claude Code
2. Copy the contents of **Tab 2** and paste it into the chat
3. Claude walks you through the rest automatically

**To launch PreQL after setup:**

Open Terminal and type `preql`. (Tab 2 sets this up for you — it's a shortcut that opens Claude Code in the right place.)

**To get updates (~every 6–8 weeks):**

Open Terminal and run:
```
cd ~/Documents/PreQL && git pull
```

---

## Questions?

- Slack: **#preql** for PreQL questions, **#cmty-claude** for Claude questions
- In-tool: type `/help-preql` at any time
