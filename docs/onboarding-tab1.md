# PreQL

**Ask your data questions in plain English. Get back validated SQL and a plain-English answer.**

PreQL is an AI analytics tool built for CreditKarma analysts and PMs. Instead of writing (or waiting for) BigQuery SQL, you describe what you want to know — and PreQL handles the rest.

---

## What It Looks Like

You type a question. PreQL figures out the right data, writes and validates the query, and returns:

- **A plain-English summary** of what the result means
- **Any caveats** you should know about (e.g., data lags, approximations)
- **The SQL**, ready to copy into BigQuery if you want it

**Example questions PreQL can answer:**

> *"How many new members registered last month, broken down by platform?"*

> *"What was the ChatGPT registration funnel conversion rate over the last 30 days?"*

> *"Did experiment 71788 significantly improve registration completion rate?"*

> *"How many dormant users reactivated in Q1?"*

You don't need to know which table to use. You don't need to know SQL. You just need to know what you want to find out.

---

## What It Can Do

| Use case | What to ask |
|---|---|
| Registration / engagement metrics | "How many new members registered last week by platform?" |
| Revenue analysis | "What was personal loan revenue last month vs. the month before?" |
| Funnel measurement | "Walk me through the ChatGPT registration funnel conversion rates" |
| Experiment results | "Was experiment 71788 statistically significant for registration completion?" |
| Segment analysis | "How do dormant users compare to active users on credit score?" |

PreQL also has guided workflows for documenting new funnels (`/funnel-discovery`) and new data tables (`/add-table-schema`) — so what you build becomes available to the whole team.

---

## Getting Started

**Prerequisites (one-time, ~15 min total):**

1. **Complete the GenAI Tools for our Workforce training** if you haven't — this gates access to Claude.
2. **Request BigQuery access** if you don't have it yet: [Airlock BigQuery access request](https://airlock.static.corp.creditkarma.com/bigquery_access/index.html#how-do-i-get-access-to-airlock-bigquery) — takes 1–2 days to approve, so start early.
3. **Install Homebrew and Claude Code** via **Workspace ONE Intelligent Hub** on your Mac (search "Homebrew" and "Claude Code").

**Then:**
1. Open Terminal, type `claude`, press Enter
2. Copy the contents of **Tab 2** of this document and paste it into the chat
3. Claude will walk you through the rest automatically

---

## Questions?

- **Slack:** `#preql` for PreQL questions, `#cmty-claude` for Claude questions
- **In-tool:** Once set up, type `/help-preql` at any time
