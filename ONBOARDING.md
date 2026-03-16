# Getting Started with PreQL

PreQL is an AI-powered analytics tool for CreditKarma analysts and PMs. You ask a question in plain English — PreQL finds the right data, writes validated BigQuery SQL, and returns a plain-English summary alongside the query.

---

## What PreQL Can Do

- **Ad-hoc data questions** — registrations, revenue, engagement, user segments
- **Funnel analysis** — map a product funnel, measure conversion rates, classify dropoff
- **Experiment analysis** — measure A/B test results with statistical significance
- **Schema documentation** — help document new BigQuery tables for the team

## How It Works

You interact with PreQL through a chat interface inside Claude Code. Under the hood, it:

1. **Interprets** your question — clarifies assumptions, identifies relevant tables
2. **Generates SQL** — writes BigQuery-ready SQL against your data
3. **Validates** — checks for correctness, partition safety, and methodology
4. **Presents results** — plain-English summary, caveats, and the final SQL

BigQuery access is **read-only**. PreQL cannot write, modify, or delete data.

---

## Prerequisites

Before setting up PreQL, you'll need:

1. **BigQuery access** via Airlock (see below)
2. **Claude Code** — the CLI tool that runs PreQL
3. **Git** — to clone the PreQL repository
4. **gcloud CLI** — to authenticate with Google

---

## Step 1 — Get BigQuery Access

If you don't already have access to `prod-ck-abl-data-53`, submit a SailPoint request via Airlock:

> **Airlock access request:** https://airlock.static.corp.creditkarma.com/bigquery_access/index.html#how-do-i-get-access-to-airlock-bigquery

Follow the steps under *"How do I get access to Airlock BigQuery?"*:
1. Verify you need access to `prod-ck-abl-data-53` (Airlock BigQuery)
2. Submit a self-service request in SailPoint
3. Once approved, verify access by opening the BigQuery console and querying the project

If you already have BigQuery access and get an "Access Denied" error on a specific table, follow the instructions under *"When I try to query a view under ABL (prod-ck-abl-data-53), I get an 'Access Denied' error"* on the same page.

---

## Step 2 — Install Claude Code

In your terminal:

```bash
npm install -g @anthropic-ai/claude-code
```

> Requires Node.js. If you don't have it: `brew install node`

---

## Step 3 — Clone the PreQL Repository

If you're new to Git, follow the internal Git setup guide first:
> **[Internal Git Setup Guide — link here]**

Once Git is ready:

```bash
git clone [PREQL_REPO_URL] ~/Documents/PreQL
cd ~/Documents/PreQL
```

> Replace `[PREQL_REPO_URL]` with the actual GitHub URL (shared separately).

---

## Step 4 — Set Up BigQuery Connection

Connect Claude Code to BigQuery:

```bash
claude mcp add bigquery --scope user --transport stdio -- uvx mcp-server-bigquery --project prod-ck-abl-data-53 --location US
```

---

## Step 5 — Authenticate with Google

```bash
gcloud auth login
```

> If `gcloud` is not found: `brew install --cask google-cloud-sdk`, then re-run.

This opens a browser window. Sign in with your CreditKarma Google account.

---

## Step 5b — Install Skills

PreQL's built-in commands (`/onboard`, `/funnel-discovery`, etc.) are installed as skills linked from the repo. Run once after cloning:

```bash
bash scripts/install-skills.sh
```

Because these are symlinks, pulling future updates to the repo automatically updates the skills — no need to re-run.

---

## Step 6 — Open PreQL

```bash
cd ~/Documents/PreQL
claude
```

Type `/onboard` to run the setup check and get a guided orientation.

---

## Tips for Best Results

- **Be specific about time windows** — "last 30 days" or "Q1 2025" works better than "recently"
- **Name the metric you care about** — "conversion rate", "revenue", "registrations"
- **You don't need to know the table** — PreQL figures that out from your question
- **Ask follow-ups** — you can refine or extend any answer in the same session
- **New table? Use `/add-table-schema`** — documents it for you and everyone else
- **New funnel? Use `/funnel-discovery`** — maps it interactively and saves the doc

---

## Contributing Back

If you document a new table or funnel, it can be shared with the whole team. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to submit a PR.

---

## Questions / Issues

Ping [owner/channel TBD] or open a GitHub issue in the PreQL repo.
