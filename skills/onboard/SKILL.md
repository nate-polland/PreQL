---
name: onboard
description: |
  First-time setup check and guided orientation for new PreQL users. Verifies BigQuery connection, walks through fixes if needed, then gives a brief orientation and runs a sample query.

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

## Step 1 — Check BigQuery Connection

Run a cheap test query to verify BQ is connected and accessible:

```sql
SELECT 1 AS connection_test
```

**If it succeeds:** Tell the user their connection is working. Move to Step 2.

**If it fails:** Walk through the fix:

1. Check if `gcloud` is authenticated:
   ```bash
   gcloud auth list
   ```
   If no active account is shown, run:
   ```bash
   gcloud auth login
   ```
   Then retry the BQ test query.

2. If that still fails, check if the MCP BigQuery server is configured:
   ```bash
   claude mcp list
   ```
   If `bigquery` is not listed, run:
   ```bash
   claude mcp add bigquery --scope user --transport stdio -- uvx mcp-server-bigquery --project prod-ck-abl-data-53 --location US
   ```
   Then restart Claude Code and try again.

3. If the user gets an "Access Denied" error specifically on `prod-ck-abl-data-53`, they need to request Airlock BigQuery access via SailPoint:
   > https://airlock.static.corp.creditkarma.com/bigquery_access/index.html#how-do-i-get-access-to-airlock-bigquery

   Let them know to request access and come back once it's approved — this can take a day or two.

---

## Step 2 — Quick Orientation (skippable)

Ask: "Want a quick orientation, or would you rather just start asking questions?"

If they want the orientation, give a 3-sentence summary:

> PreQL translates plain-English questions into validated BigQuery SQL. You ask a question, it interprets what you're after, generates and validates the SQL, and returns a summary with the query. It knows your team's tables, join patterns, and business logic — you don't need to.

Then mention the two most useful built-in commands:
- `/funnel-discovery` — maps a product funnel interactively and saves the doc
- `/add-table-schema` — documents a new BigQuery table for the team

Tell them they can type `/help-preql` at any time to get a full overview of what PreQL can do.

---

## Step 3 — Sample Query (skippable)

Ask: "Want to try a quick sample query to see how it works?"

If yes, suggest this one (or let them pick their own):

> "How many new members registered last month, broken down by platform?"

Run it through the normal pipeline: interpret → generate SQL → validate → present results. After the result, briefly note: "This is what every query looks like — a plain-English summary, caveats, and the SQL below it."

If they'd rather use their own question, go for it.

---

## Done

Close by letting them know:
- They can ask data questions in plain English at any time
- `/help-preql` is always available for a refresher
- `ONBOARDING.md` in the repo has the full written setup guide
