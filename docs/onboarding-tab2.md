# PreQL Setup

You are setting up PreQL for a new user. **Start immediately — run each check automatically and only pause when the user needs to take an action.** Don't ask for permission to proceed between steps. Narrate briefly what you're doing as you go.

---

## Step 1 — Connect to GitHub

Run immediately:

```bash
gh auth status --hostname code.corp.creditkarma.com
```

**If already authenticated:** proceed to Step 2.

**If `gh` is not installed:** tell the user to install it via **Workspace ONE Intelligent Hub** (search "GitHub CLI"), then wait for confirmation and re-run.

**If not authenticated:** tell the user: "I need to connect to CreditKarma's GitHub — a browser window will open and you'll just need to sign in with your CreditKarma account." Then run:

```bash
gh auth login --hostname code.corp.creditkarma.com
```

When prompted, select:
- **Protocol:** HTTPS
- **Authenticate Git with your GitHub credentials?** Yes
- **How to authenticate:** Login with a web browser

Wait for them to confirm the browser sign-in completed, then verify:

```bash
gh auth status --hostname code.corp.creditkarma.com
```

**If login fails / no GitHub account:** tell the user they'll need access to CreditKarma's GitHub first. Ask them to reach out to their manager or #it-help on Slack to get a `code.corp.creditkarma.com` account, then come back and re-run setup.

---

## Step 2 — Connect to BigQuery

Try to run this query immediately using the BigQuery MCP tool:

```sql
SELECT 1 AS connection_test
```

**If it succeeds:** tell the user their data access is already set up and proceed to Step 3.

**If the BigQuery MCP tool is not available / not configured:** proceed to Step 3 — you'll complete BigQuery setup in Step 5 after cloning the repo.

**If it fails with "Access Denied":** tell the user: "You don't have access to the data warehouse yet — we'll need to request it before you can run queries. It takes a few minutes to submit and your manager just needs to approve it, which usually happens within 1–2 business days."

Walk them through it:
1. Open [SailPoint](https://iam.int.creditkarma.com/identityiq/home.jsf) in their browser
   - Can't reach it? Confirm Global Protect VPN is connected to `CK-US-WEST-GW` or `CK-US-EAST-GW` (not "Best Available")
   - Login error? Clear cookies at `chrome://settings/content/siteDetails?site=https://iam.int.creditkarma.com/` and retry
2. Click **Manage My Access**, search for **"Airlock ABL BQ Access"**, and submit the request
3. Tell them: "Your manager will get an email to approve it. Once approved, come back and run `/onboard` to verify the connection. Let's keep going with the rest of setup in the meantime."

Continue to Step 3 regardless.

---

## Step 3 — Clone the PreQL Repository

Check if git and gcloud are installed:

```bash
git --version && gcloud --version
```

For anything missing:
- **git:** install via Homebrew — `brew install git` (install Homebrew first via **Workspace ONE Intelligent Hub** if needed)
- **gcloud:** `brew install --cask google-cloud-sdk`

Create the folder and clone:

```bash
mkdir -p ~/Documents/Claude\ Code && git clone https://code.corp.creditkarma.com/nate-polland-ck/PreQL ~/Documents/Claude\ Code/PreQL
```

If `~/Documents/Claude Code/PreQL` already exists, ask: "Looks like PreQL is already installed — is this a re-run or a fresh machine?" If re-run, skip to Step 6 to verify your connection is still working.

---

## Step 4 — Authenticate with Google

Run both commands — the first gives CLI access, the second sets up long-lived credentials so they won't need to re-authenticate every session:

```bash
gcloud auth login
```

```bash
gcloud auth application-default login
```

Tell the user a browser window will open for each — they should sign in with their CreditKarma Google account both times. Wait for them to confirm both completed before moving on.

---

## Step 5 — Install Skills and Connect BigQuery

```bash
cd ~/Documents/Claude\ Code/PreQL && bash scripts/install-skills.sh
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

**Important:** Tell the user they need to fully quit and reopen Claude for the BigQuery connection to take effect. Ask them to reopen it, paste this setup doc again, and reply "continue from Step 6" to pick up where they left off.

---

## Step 6 — Verify the BigQuery Connection

Run a quick test:

```sql
SELECT 1 AS connection_test
```

**If it succeeds:** proceed to Step 7.

**If it fails, diagnose by error type:**

**Auth error / not authenticated:**
Run `gcloud auth list` to check for an active account. If none shown, go back to Step 4 and re-authenticate. Make sure to run both `gcloud auth login` and `gcloud auth application-default login`.

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

## Step 7 — Install the PreQL Launcher

Tell the user:

> "Last step — I'm going to create a **PreQL** icon on your Desktop. Once it's in your Dock, you'll be able to open PreQL with a single click, without needing to open Claude manually. Want me to set that up? (You can skip this if you'd prefer.)"

If they want to skip, jump to Step 8.

If they confirm, run:

```bash
cat > ~/Desktop/PreQL.command << 'EOF'
#!/bin/bash
open -a "Claude" "$HOME/Documents/Claude Code/PreQL"
EOF
chmod +x ~/Desktop/PreQL.command
```

Then apply the PreQL icon:

```bash
pip3 install pyobjc-framework-Cocoa -q && python3 - << 'PYEOF'
import AppKit, os
image_path = os.path.expanduser("~/Documents/Claude Code/PreQL/assets/PreQL Logo.png")
file_path = os.path.expanduser("~/Desktop/PreQL.command")
image = AppKit.NSImage.alloc().initWithContentsOfFile_(image_path)
AppKit.NSWorkspace.sharedWorkspace().setIcon_forFile_options_(image, file_path, 0)
print("Icon applied.")
PYEOF
```

Tell the user:

> "A **PreQL** icon just appeared on your Desktop — can you see it?"

Wait for confirmation, then say:

> "To add it to your Dock:
> 1. Click and hold the **PreQL** icon on your Desktop
> 2. Drag it to the right side of your Dock, past the divider line
> 3. Let me know when it's there!"

Wait for confirmation, then say:

> "Let's test it. Double-click **PreQL** in your Dock.
>
> **Heads up:** macOS may show a security warning the first time — right-click → **Open** → **Open**. You'll only see this once.
>
> Once Claude opens, come back here and let me know!"

Wait for confirmation before moving to Step 8.

---

## Step 8 — Done

Tell the user setup is complete. Then say:

> "You're all set. From now on, click **PreQL** in your Dock (or Desktop) to get started — or open Claude and navigate to your PreQL folder.
>
> A few things you can do right now:
> - Ask a data question in plain English — e.g. *'How many new members registered last month, broken down by platform?'*
> - Type `/help-preql` to see everything PreQL can do
> - Type `/onboard` anytime to re-run this setup or check your connection
>
> Want to try a sample query, or is there something specific you want to look into?"

If they want a sample query, run: *"How many new members registered last month, broken down by platform?"* through the full pipeline and show them the result.
