---
name: sync
description: |
  Pull the latest PreQL updates from GitHub safely, handling local changes and conflicts. Use this skill whenever a user wants to update their local copy — especially if they have uncommitted work.

  Trigger phrases: "/sync", "pull updates", "get latest", "update preql", "pull from github", "sync my repo"
---

# PreQL Sync

Pull the latest changes from GitHub while preserving any local work. Run through the steps below.

---

## Step 1 — Check Local State

```bash
cd path/to/PreQL
git status
```

Three possible states:
- **Clean** (nothing to commit, working tree clean) → go to Step 2
- **Untracked files only** (new files the user created but hasn't committed) → go to Step 2 (untracked files won't conflict with pull)
- **Modified tracked files** → go to Step 3

---

## Step 2 — Clean Pull

```bash
git pull origin main
```

If this succeeds, skip to Step 4.

If it fails with a merge conflict (rare on a clean tree, but possible if someone force-pushed), tell the user and help them resolve.

---

## Step 3 — Pull With Local Changes

Show the user what's modified:
```bash
git diff --stat
```

Then ask: **"You have local changes. Want me to stash them, pull, then restore? Or would you rather commit your changes to a branch first?"**

### Option A: Stash and restore (most common)

```bash
cd path/to/PreQL
git stash
git pull origin main
git stash pop
```

If `stash pop` reports conflicts:
1. Show which files conflict: `git diff --name-only --diff-filter=U`
2. For each conflicted file, show the conflict markers and help the user pick which version to keep
3. After resolving: `git add [resolved files]` then `git stash drop`

### Option B: Commit to a branch first

```bash
git checkout -b [user-branch-name]
git add [files]
git commit -m "[user's description]"
git checkout main
git pull origin main
```

Tell the user their changes are saved on the branch and they can merge or cherry-pick later. If they want to contribute those changes back, point them to `/contribute`.

---

## Step 4 — Post-Pull Housekeeping

Run the install script to pick up any new skills:
```bash
bash scripts/install-skills.sh
```

This is idempotent — safe to run every time.

---

## Step 5 — Summary

Show what changed:
```bash
git log --oneline -10
```

Highlight anything notable: new skills, updated schemas, new funnel docs. If a file the user was working with was updated, mention it so they can review the changes.

---

## Key Rules
- Never force-pull or reset the user's working tree — always preserve their local work
- If conflicts arise, walk the user through resolution rather than auto-resolving
- `session.md` is gitignored (per-user session state) — it won't conflict
- The install script updates skill symlinks automatically — no manual re-linking needed
