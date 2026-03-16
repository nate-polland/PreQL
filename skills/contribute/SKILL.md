---
name: contribute
description: |
  Helps users push local changes back to the PreQL GitHub repo. Checks what changed, categorizes by contribution tier, and routes to the right workflow — direct commit to main for new files, branch + PR for edits to core files.

  Trigger phrases: "/contribute", "push my changes", "submit my changes", "contribute back", "open a PR", "push to github"
---

# PreQL Contribute

Run `git status` and `git diff --stat` immediately to see what's changed. Then work through the steps below.

---

## Step 1 — Categorize the Changes

Sort every changed or new file into one of these tiers based on `CONTRIBUTING.md`:

**Tier A — Direct to main** (any maintainer):
- New files in `Schema/`, `Funnels/`, `Segments/`, `skills/`

**Tier B — Branch + PR required** (senior maintainer review):
- Edits to existing files in `Schema/`, `Funnels/`, `Segments/`
- Any changes to `Context/`, `Agents/`, or existing `skills/` files

**Tier C — Owner approval only**:
- Any changes to `CLAUDE.md`

Tell the user what you found and which tier each change falls into. If there's a mix of tiers, handle them separately — Tier A changes can go in one commit, Tier B/C need their own PR.

---

## Step 2 — Tier A: Commit Directly to Main

For new files only (no edits to existing core files):

1. **Check for collisions first.** Pull latest and check if any of the new files already exist on `main`:
   ```bash
   cd ~/Documents/Claude\ Code/PreQL
   git fetch origin
   git diff --name-only HEAD origin/main
   ```
   Also check directly:
   ```bash
   git show origin/main:[filepath]
   ```
   - **File doesn't exist on main:** safe to proceed.
   - **File already exists on main:** tell the user: "Someone else already pushed a file at that path. Let me pull it down so you can review it — we'll merge your additions rather than overwrite theirs." Pull, show them the existing content, and help them reconcile before committing.

2. Pull latest before committing:
   ```bash
   git pull origin main
   ```

3. Show the user a summary of what will be committed and ask them to confirm.

4. Stage and commit:
   ```bash
   git add [files]
   git commit -m "[description]"
   ```
   Write a clear commit message: what was added and why (e.g., "Add schema for fact_tracking_revenue_ext", "Document ChatGPT registration funnel").

5. Push:
   ```bash
   git push
   ```
   If the push is rejected (someone pushed between your pull and push), run `git pull --rebase origin main` and push again.

6. Confirm the push succeeded and share the commit URL.

---

## Step 3 — Tier B: Branch + Pull Request

For edits to existing files or any changes to `Context/`, `Agents/`, or `skills/`:

1. Ask the user: "What was wrong or incomplete in the existing version, and what data or analysis led to this change?" — this is required for the PR description per `CONTRIBUTING.md`. Wait for their answer.

2. Create a branch:
   ```bash
   cd ~/Documents/Claude\ Code/PreQL
   git checkout -b [branch-name]
   ```
   Use a descriptive branch name (e.g., `update-darwin-schema`, `fix-revenue-aging-context`).

3. Stage and commit:
   ```bash
   git add [files]
   git commit -m "[description]"
   ```

4. Push the branch:
   ```bash
   git push -u origin [branch-name]
   ```

5. Open a PR:
   ```bash
   gh pr create --title "[title]" --body "[body]"
   ```
   The PR body must include:
   - What was wrong or incomplete in the current version
   - What data or analysis led to this change
   - Which queries or analyses this affects

   Show the user the PR URL when done.

---

## Step 4 — Tier C: CLAUDE.md Changes

If the user has changed `CLAUDE.md`, let them know:

> "Changes to CLAUDE.md require approval from npolland before merging. Open a PR with a description of what you changed and why, and tag npolland for review."

Follow the same branch + PR flow as Tier B, but make clear the PR needs explicit owner sign-off.

---

## Handling Mixed Changes

If the diff includes both Tier A and Tier B/C changes:
1. Handle Tier A first — commit and push the new files to main
2. Then create a separate branch for the Tier B/C edits

Don't mix new files and core edits in a single commit.
