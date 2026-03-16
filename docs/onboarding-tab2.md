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

## Step 2 — Authenticate with GitHub

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

If `~/Documents/PreQL` already exists, ask: "Looks like the repo is already cloned — is this a re-run or a fresh machine?" If re-run, skip to Step 5 to verify skills are still linked.

---

## Step 4 — Authenticate with Google

```bash
gcloud auth login
```

Tell the user a browser window will open — they should sign in with their CreditKarma Google account. Wait for them to confirm it completed before moving on.

---

## Step 5 — Install Skills

```bash
cd ~/Documents/PreQL && bash scripts/install-skills.sh
```

All 4 skills should show as linked. If any show warnings, follow the instructions in the script output.

---

## Step 6 — Connect BigQuery

Run:

```bash
claude mcp list
```

**If `bigquery` is already listed:** skip to Step 7.

**If not listed:** run:

```bash
claude mcp add bigquery --scope user --transport stdio -- uvx mcp-server-bigquery --project prod-ck-abl-data-53 --location US
```

If this fails because `uvx` is not found:
```bash
pip install uv
```
Then retry.

---

## Step 7 — Verify the Connection

Run a quick test:

```sql
SELECT 1 AS connection_test
```

**If it succeeds:** setup is complete — proceed to Step 8.

**If it fails, diagnose by error type:**

**Auth error / not authenticated:**
Run `gcloud auth list` to check for an active account. If none shown, go back to Step 4 and re-authenticate.

**"Access Denied" on `prod-ck-abl-data-53` (no access to the project at all):**
The user needs to request Airlock BigQuery access via SailPoint:
1. Go to [SailPoint](https://iam.int.creditkarma.com/identityiq/home.jsf) → **Manage My Access**
2. Search for **"Airlock ABL BQ Access"** and submit the request
3. Their manager will receive an approval email — approval typically takes 1–2 business days

Let them know to come back once approved — everything else is already set up. Full instructions: https://airlock.static.corp.creditkarma.com/sailpoint/#request-access-through-sailpoint

If they have trouble logging into SailPoint: clear cookies at `chrome://settings/content/siteDetails?site=https://iam.int.creditkarma.com/` and ensure Global Protect VPN is connected to `CK-US-WEST-GW` or `CK-US-EAST-GW` (not "Best Available").

**"Access Denied" on a specific dataset or view (general project access works, but one dataset fails):**
The user has project-level access but not to that specific dataset. To get it:
1. Find the dataset name in the error message (format: `project:dataset.table`)
2. Go to the [Airlock Access Catalog](https://airlock.static.corp.creditkarma.com/index.html) and search for the dataset name
3. Find the required Google group under "Access Info Tag"
4. In [SailPoint](https://iam.int.creditkarma.com/identityiq/home.jsf), search for that group name (without `@creditkarma.com`) and submit a request
5. Manager approval required

Full instructions: https://airlock.static.corp.creditkarma.com/sailpoint/#request-access-through-sailpoint. For questions: `#airlock_access_control` on Slack.

**Table or view not found in ABL:**
The table may not have been added to `prod-ck-abl-data-53` yet — this is a separate issue from permissions. Direct the user to `#airlock_access_control` on Slack for guidance on adding it.

---

## Step 8 — Done

Tell the user setup is complete. Then say:

> "You're ready to use PreQL. Ask data questions in plain English — for example: 'How many new members registered last month, broken down by platform?'
>
> Type `/help-preql` at any time to see what's available. Type `/onboard` for a guided walkthrough."

Then ask: "Want to try a sample query, or is there something specific you want to look into?"

If they want a sample query, run: *"How many new members registered last month, broken down by platform?"* through the full pipeline and show them the result.
