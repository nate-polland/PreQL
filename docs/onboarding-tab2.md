# PreQL Setup

You are setting up PreQL for a new user. **Start immediately — run each check automatically and only pause when the user needs to take an action (e.g., install something, complete a browser auth flow).** Don't ask for permission to proceed between steps. Narrate briefly what you're doing as you go.

---

## Step 0 — Check BigQuery Access

Try to run this query immediately using the BigQuery MCP tool:

```sql
SELECT 1 AS connection_test
```

**If it succeeds:** tell the user their data access is already set up and proceed to Step 1.

**If the BigQuery MCP tool is not available / not configured:** skip this check and proceed to Step 1 — access will be verified at the end of setup in Step 6.

**If it fails with "Access Denied":** tell the user: "You don't have access to the data warehouse yet — we'll need to request it before you can run queries. It takes a few minutes to submit and your manager just needs to approve it, which usually happens within 1–2 business days."

Walk them through it:
1. Open [SailPoint](https://iam.int.creditkarma.com/identityiq/home.jsf) in their browser
   - Can't reach it? Confirm Global Protect VPN is connected to `CK-US-WEST-GW` or `CK-US-EAST-GW` (not "Best Available")
   - Login error? Clear cookies at `chrome://settings/content/siteDetails?site=https://iam.int.creditkarma.com/` and retry
2. Click **Manage My Access**, search for **"Airlock ABL BQ Access"**, and submit the request
3. Tell them: "Your manager will get an email to approve it. Once approved, come back and run `/onboard` to verify the connection. Let's keep going with the rest of setup now."

Continue to Step 1 regardless — everything except the final connection test can be completed while waiting for approval.

---

## Step 1 — Check Prerequisites

Run immediately:

```bash
git --version && node --version && gcloud --version && gh --version
```

For anything missing:
- **git** or **Node.js:** install via **Workspace ONE Intelligent Hub** on your Mac (search "Homebrew"), then run `brew install git` or `brew install node` as needed
- **gcloud:** `brew install --cask google-cloud-sdk`
- **gh (GitHub CLI):** install via **Workspace ONE Intelligent Hub** (search "GitHub CLI")

Tell the user what to install, wait for them to confirm it's done, then re-run the checks before moving on.

---

## Step 2 — Authenticate with GitHub

Run immediately:

```bash
gh auth status --hostname code.corp.creditkarma.com
```

**If already logged in:** proceed to Step 3.

**If not logged in:** tell the user: "I need to connect to CreditKarma's GitHub — a browser window will open and you'll just need to sign in with your CreditKarma account." Then run:

```bash
gh auth login --hostname code.corp.creditkarma.com
```

When prompted, select:
- **Protocol:** HTTPS
- **Authenticate Git with your GitHub credentials?** Yes
- **How to authenticate:** Login with a web browser

Wait for them to confirm the browser sign-in completed, then verify before moving on:

```bash
gh auth status --hostname code.corp.creditkarma.com
```

---

## Step 3 — Clone the PreQL Repository

```bash
git clone https://code.corp.creditkarma.com/nate-polland-ck/PreQL ~/Documents/PreQL
```

If `~/Documents/PreQL` already exists, ask: "Looks like the repo is already cloned — is this a re-run or a fresh machine?" If re-run, skip to Step 6 to verify your connection is still working.

---

## Step 4 — Authenticate with Google

```bash
gcloud auth login
```

Tell the user a browser window will open — they should sign in with their CreditKarma Google account. Wait for them to confirm it completed before moving on.

---

## Step 5 — Install Skills and Connect BigQuery

```bash
cd ~/Documents/PreQL && bash scripts/install-skills.sh
```

All 4 skills should show as linked. If any show warnings, follow the instructions in the script output.

Then connect BigQuery. Run:

```bash
claude mcp list
```

**If `bigquery` is already listed:** proceed to Step 6.

**If not listed:** run:

```bash
claude mcp add bigquery --scope user --transport stdio -- uvx mcp-server-bigquery --project prod-ck-abl-data-53 --location US
```

If this fails because `uvx` is not found, first run `pip install uv`, then retry.

**Important:** Tell the user they need to fully quit and reopen Claude Code for the BigQuery connection to take effect. Ask them to reopen it, paste this setup doc again, and reply "continue from Step 6" to pick up where they left off.

---

## Step 6 — Verify the Connection

Run a quick test:

```sql
SELECT 1 AS connection_test
```

**If it succeeds:** setup is complete — proceed to Step 7.

**If it fails, diagnose by error type:**

**Auth error / not authenticated:**
Run `gcloud auth list` to check for an active account. If none shown, go back to Step 4 and re-authenticate.

**"Access Denied" on `prod-ck-abl-data-53` (no access to the project at all):**
The user needs to request Airlock BigQuery access via SailPoint:
1. Go to [SailPoint](https://iam.int.creditkarma.com/identityiq/home.jsf) → **Manage My Access**
2. Search for **"Airlock ABL BQ Access"** and submit the request
3. Manager approval required — typically 1–2 business days

Let them know to come back once approved — everything else is already set up.

If they have trouble logging into SailPoint, try clearing cookies: open `chrome://settings/content/siteDetails?site=https://iam.int.creditkarma.com/` and click **Clear data**. Also confirm Global Protect VPN is connected to `CK-US-WEST-GW` or `CK-US-EAST-GW` (not "Best Available").

Full SailPoint instructions: https://airlock.static.corp.creditkarma.com/sailpoint/#request-access-through-sailpoint

**"Access Denied" on a specific dataset or view (general project access works, but a specific query fails):**
The user has project-level access but not to that specific dataset. To get it:
1. Note the dataset name from the error (format: `project:dataset.table`)
2. Look up the required Google group in the [Airlock Access Catalog](https://airlock.static.corp.creditkarma.com/index.html) — search for the dataset name and check "Access Info Tag"
3. Request that group in [SailPoint](https://iam.int.creditkarma.com/identityiq/home.jsf) (search by group name, without `@creditkarma.com`)
4. Manager approval required

For questions: `#airlock_access_control` on Slack.

---

## Step 7 — Create the PreQL Launcher

Create a double-clickable launcher, put it on the Desktop, and apply the PreQL logo as its icon:

```bash
cat > ~/Desktop/PreQL.command << 'EOF'
#!/bin/bash
open -a "Claude" "$HOME/Documents/PreQL"
EOF
chmod +x ~/Desktop/PreQL.command
```

Then apply the icon:

```bash
pip3 install pyobjc-framework-Cocoa -q && python3 - << 'PYEOF'
import AppKit, os
image_path = os.path.expanduser("~/Documents/PreQL/assets/PreQL Logo.png")
file_path = os.path.expanduser("~/Desktop/PreQL.command")
image = AppKit.NSImage.alloc().initWithContentsOfFile_(image_path)
AppKit.NSWorkspace.sharedWorkspace().setIcon_forFile_options_(image, file_path, 0)
print("Icon applied.")
PYEOF
```

Tell the user:

> "A **PreQL** icon just appeared on your Desktop — you should see it there now. Can you confirm?"

Wait for confirmation, then say:

> "To keep it handy, let's add it to your Dock:
> 1. Find the **PreQL** icon on your Desktop
> 2. Click and hold it, then drag it to the right side of your Dock — past the divider line (that's where files and folders live)
> 3. Let me know when it's there!"

Wait for confirmation, then say:

> "Now let's do a test launch. Double-click **PreQL** in your Dock.
>
> **Heads up:** macOS may show a security warning the first time — if it does, right-click the icon → **Open** → **Open**. You'll only see this once.
>
> Once Claude opens, come back here and let me know — we're almost done!"

Wait for them to confirm Claude opened successfully before moving to Step 8.

---

## Step 8 — Done

Tell the user setup is complete. Then say:

> "You're ready to use PreQL. From now on, just double-click **PreQL** in your Dock (or Desktop) to get started.
>
> Ask data questions in plain English — for example: 'How many new members registered last month, broken down by platform?'
>
> Type `/help-preql` at any time to see what's available."

Then ask: "Want to try a sample query, or is there something specific you want to look into?"

If they want a sample query, run: *"How many new members registered last month, broken down by platform?"* through the full pipeline and show them the result.
