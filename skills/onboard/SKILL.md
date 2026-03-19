---
name: onboard
description: |
  First-time setup check and guided orientation for new PreQL users. Verifies data warehouse connection, walks through fixes if needed, then gives a brief orientation and runs a sample query.

  Trigger phrases: "/onboard", "set me up", "first time setup", "check my connection", "is my setup working"
---

# PreQL Onboarding

Welcome the user to PreQL, then run through the steps below. **Be conversational and concise — this should feel like a quick orientation, not a manual.**

At any point, if the user says "skip", "I'm good", "I already know this", or similar — stop and ask what they'd like to do instead. The goal is to unblock them quickly, not to be thorough for its own sake.

---

## Step 0 — Check Skills Are Installed

Before anything else, verify the skills install was run. Ask: "Did you run `bash scripts/install-skills.sh` after cloning?"

If no (or they're not sure): tell them to run it from the repo root, then restart Claude Code. The script is idempotent — safe to re-run.

If yes: proceed.

---

## Step 1 — Check Data Warehouse Connection

Run a cheap test query to verify the warehouse is connected and accessible:

```sql
SELECT 1 AS connection_test
```

**If it succeeds:** Tell the user their connection is working. Move to Step 2.

**If it fails:** Walk through the fix:

1. Check if the MCP data warehouse server is configured:
   ```bash
   claude mcp list
   ```
   If the data warehouse MCP is not listed, follow the setup instructions in `README.md` to add it.

2. Check authentication — if using BigQuery:
   ```bash
   gcloud auth list
   ```
   If no active account is shown, run:
   ```bash
   gcloud auth login && gcloud auth application-default login
   ```
   Then retry the test query.

3. If you get an "Access Denied" error: the user needs to request access to the relevant data warehouse project or dataset. Refer them to their team's access request process.

---

## Step 2 — Quick Orientation (skippable)

Ask: "Want a quick orientation, or would you rather just start asking questions?"

If they want the orientation, give a 3-sentence summary:

> PreQL translates plain-English questions into validated SQL. You ask a question, it interprets what you're after, generates and validates the SQL, and returns a summary with the query. It knows your team's tables, join patterns, and business logic — you don't need to.

Then mention a few key commands to get started:
- `/funnel-discovery` — maps a product funnel interactively and saves the doc
- `/funnel-decomposition` — breaks a funnel into cohorts by user path
- `/experiment-design` — power calc + hypothesis doc before shipping an experiment
- `/metric-investigation` — structured workflow when a metric moves unexpectedly

Tell them to type `/help-preql` at any time to see the full list of commands.

---

## Step 3 — Sample Query (skippable)

Ask: "Want to try a quick sample query to see how it works?"

If yes, suggest this one (or let them pick their own):

> "How many new users registered last month, broken down by platform?"

Run it through the normal pipeline: interpret → generate SQL → validate → present results. After the result, briefly note: "This is what every query looks like — a plain-English summary, caveats, and the SQL below it."

If they'd rather use their own question, go for it.

---

## Done

Close by letting them know:
- They can ask data questions in plain English at any time
- `/help-preql` is always available for a refresher
