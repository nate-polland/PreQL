# PreQL Setup

You are helping a new user set up PreQL, a BigQuery analytics tool. Work through the steps below in order. Be conversational and tell the user what you're doing at each step. If anything fails, troubleshoot before moving on.

---

## Step 1 — Check Prerequisites

Run these checks:

```bash
git --version
node --version
gcloud --version
```

Report what's installed and what's missing. If anything is missing:
- **git:** `brew install git`
- **Node.js:** `brew install node`
- **gcloud:** `brew install --cask google-cloud-sdk`

Tell the user to install anything missing, then proceed.

---

## Step 2 — Clone the PreQL Repository

```bash
git clone https://code.corp.creditkarma.com/nate-polland-ck/PreQL ~/Documents/PreQL
cd ~/Documents/PreQL
```

If the directory already exists, ask the user whether this is a re-run or a fresh install.

---

## Step 3 — Install Skills

```bash
cd ~/Documents/PreQL
bash scripts/install-skills.sh
```

Confirm all 4 skills were linked successfully. If any show warnings, follow the instructions in the script output.

---

## Step 4 — Connect BigQuery

```bash
claude mcp add bigquery --scope user --transport stdio -- uvx mcp-server-bigquery --project prod-ck-abl-data-53 --location US
```

Tell the user this connects Claude Code to their team's BigQuery project.

If the command fails because `uvx` is not found:
```bash
pip install uv
```
Then retry.

---

## Step 5 — Authenticate with Google

```bash
gcloud auth login
```

Tell the user this will open a browser window — they should sign in with their CreditKarma Google account. Wait for them to confirm it completed successfully.

If `gcloud` auth fails or they get "Access Denied" when querying BigQuery later:
- Have them check Airlock BigQuery access: https://airlock.static.corp.creditkarma.com/bigquery_access/index.html
- BigQuery access requests take 1–2 business days

---

## Step 6 — Verify the Connection

Run a quick test:

```sql
SELECT 1 AS connection_test
```

If it returns a result: setup is complete.
If it fails: troubleshoot auth (Step 5) before continuing.

---

## Step 7 — Open PreQL and Orient the User

Tell the user setup is complete. Then say:

> "You're ready to use PreQL. You can ask data questions in plain English — for example: 'How many new members registered last month, broken down by platform?'
>
> Type `/help-preql` at any time to see what PreQL can do and what commands are available. Type `/onboard` if you want a guided walkthrough."

Then ask: "Would you like to try a sample query, or is there something specific you want to look into?"

If they want a sample query, run: *"How many new members registered last month, broken down by platform?"* through the full pipeline and show them the result.
