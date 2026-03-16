# PreQL Setup

You are setting up PreQL for a new user. **Start immediately — run each check automatically and only pause when the user needs to take an action (e.g., install something, complete a browser auth flow).** Don't ask for permission to proceed between steps. Narrate briefly what you're doing as you go.

---

## Step 1 — Check Prerequisites

Run immediately:

```bash
git --version && node --version && gcloud --version && gh --version
```

For anything missing:
- **git** or **Node.js:** install via **Workspace ONE Intelligent Hub** on your Mac (search "Homebrew"), then `brew install git` / `brew install node`
- **gcloud:** `brew install --cask google-cloud-sdk`
- **gh (GitHub CLI):** install via **Workspace ONE Intelligent Hub** (search "GitHub CLI")

Tell the user what to install, wait for them to confirm it's done, then re-run the checks before moving on.

---

## Step 2 — Check GitHub Auth

Run:

```bash
gh auth status --hostname code.corp.creditkarma.com
```

**If already logged in:** proceed to Step 3.

**If not logged in:** run:

```bash
gh auth login --hostname code.corp.creditkarma.com
```

When prompted:
- **Protocol:** HTTPS
- **Authenticate Git with your GitHub credentials?** Yes
- **How to authenticate:** Login with a web browser

Tell the user a browser window will open — they should sign in with their CreditKarma account. Wait for them to confirm it completed, then verify with `gh auth status` before moving on.

---

## Step 3 — Clone the PreQL Repository

```bash
git clone https://code.corp.creditkarma.com/nate-polland-ck/PreQL ~/Documents/PreQL
```

If `~/Documents/PreQL` already exists, ask: "Looks like the repo is already cloned — is this a re-run or a fresh machine?" If re-run, skip to Step 4 to verify skills are still linked.

---

## Step 4 — Install Skills

```bash
cd ~/Documents/PreQL && bash scripts/install-skills.sh
```

All 4 skills should show as linked. If any show warnings, follow the instructions in the script output.

---

## Step 5 — Check BigQuery Connection

Run:

```bash
claude mcp list
```

**If `bigquery` is listed:** skip to the connection test below.

**If not listed:** run:

```bash
claude mcp add bigquery --scope user --transport stdio -- uvx mcp-server-bigquery --project prod-ck-abl-data-53 --location US
```

If this fails because `uvx` is not found:
```bash
pip install uv
```
Then retry.

Now test the connection:

```sql
SELECT 1 AS connection_test
```

**If it succeeds:** proceed to Step 6.

**If it fails with an auth error:** proceed to Step 6 to authenticate. If it fails with "Access Denied" on `prod-ck-abl-data-53`, the user needs to request Airlock BigQuery access: https://airlock.static.corp.creditkarma.com/bigquery_access/index.html — this takes 1–2 business days. Let them know and wrap up setup for now.

---

## Step 6 — Authenticate with Google (if needed)

Only run this step if the BigQuery test in Step 5 failed.

```bash
gcloud auth login
```

Tell the user a browser window will open — they should sign in with their CreditKarma Google account. Wait for them to confirm it completed, then re-run the connection test from Step 5.

---

## Step 7 — Done

Tell the user setup is complete. Then say:

> "You're ready to use PreQL. Ask data questions in plain English — for example: 'How many new members registered last month, broken down by platform?'
>
> Type `/help-preql` at any time to see what's available. Type `/onboard` for a guided walkthrough."

Then ask: "Want to try a sample query, or is there something specific you want to look into?"

If they want a sample query, run: *"How many new members registered last month, broken down by platform?"* through the full pipeline and show them the result.
