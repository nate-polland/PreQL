# Contributing to PreQL

## Contribution Tiers

Different file types have different review requirements. The table below defines who can merge what.

| What you're changing | Who can merge | Notes |
|---|---|---|
| New `Schema/` file | Any maintainer | Spot-check: table name matches filename, grain documented |
| New `Funnels/` file | Any maintainer | Spot-check: steps validated, open questions noted |
| New `Segments/` file | Any maintainer | SQL filter must work as standalone subquery |
| Edit to existing `Schema/` file | Senior maintainer | Changes should be data-validated, not opinion-based |
| Edit to `Context/` files | Senior maintainer (npolland or delegate) | These are load-bearing — explain what broke or what was wrong |
| Edit to `Agents/` files | Senior maintainer | Changes affect all users' query generation |
| New `skills/` file | Any maintainer | New command for the team — validate it works end-to-end before submitting |
| Edit to existing `skills/` file | Senior maintainer | Changes affect all users' commands — explain what was wrong and what changed |
| Edit to `CLAUDE.md` | npolland only | Core orchestration — explicit approval required |

---

## Available Skills

| Skill | Purpose |
|---|---|
| `/add-table-schema` | Document a new BigQuery table schema |
| `/update-table-schema` | Update an existing Schema/ doc (new fields, flag validation, join key changes) |
| `/funnel-discovery` | Map an unfamiliar product funnel end-to-end |
| `/funnel-decomposition` | Decompose a documented funnel into path-based cohorts — % of users and completion rate per cohort |
| `/update-funnel` | Update an existing Funnels/ doc (new findings, stale flowchart) |
| `/experiment-design` | Power calculation + hypothesis doc + Darwin setup checklist before shipping an experiment |
| `/metric-investigation` | Diagnose an unexpected metric movement — data quality first, then dimensional breakdown |
| `/data-lineage` | Trace where a table comes from and whether it's reliable |
| `/onboard` | First-time setup — verify BigQuery connection and orientation |
| `/contribute` | Push local changes back to the PreQL GitHub repo |
| `/sync` | Pull the latest updates from GitHub, handling local changes and conflicts |
| `/help-preql` | Overview of what PreQL can do and available commands |

---

## How to Add a New Table Schema

Use the built-in skill:
```
/add-table-schema
```
Claude will walk you through documenting the table interactively and create the file in the right place.

**Naming rule:** The file must be named after the exact table (e.g., `Schema/fact_tracking_revenue_ext.md`). This prevents duplicates — the same table can only have one schema file.

Manual path: copy an existing `Schema/` file as a template, fill in the sections, and open a PR.

---

## How to Document a New Funnel

Use the built-in skill:
```
/funnel-discovery
```
Claude will ask you questions about the funnel, map the steps, and create a `Funnels/[funnel-name].md` file. It will also update `Funnels/_index.md`.

---

## How to Add a Member Segment

1. Copy `Segments/_template.md`
2. Name it descriptively: `Segments/low-credit-score.md`
3. Fill in the plain-English definition and SQL filter
4. Validate the filter in BigQuery before opening a PR

---

## How to Create a New Skill

Skills are interactive commands users can invoke with `/skill-name`. They live in `skills/[skill-name]/SKILL.md`.

1. Create `skills/[skill-name]/SKILL.md` following the format of an existing skill
2. Test it end-to-end — run through the full flow yourself before submitting
3. Run `bash scripts/install-skills.sh` to symlink it locally and verify it appears in Claude Code
4. Open a PR — any maintainer can merge a new skill

Once merged, all users get it automatically on their next `git pull` (no re-install needed — symlinks pick it up).

**To propose an improvement to an existing skill**, open a PR with:
- What behavior was wrong or missing
- What you changed and why

---

## How to Propose Changes to Core Files

Changes to `Context/`, `Agents/`, `skills/` (edits, not additions), or `CLAUDE.md` require more scrutiny because they affect every user.

**Required in your PR description:**
- What was wrong or incomplete in the current version
- What data or analysis led you to this change (not just "I think this is better")
- Which queries or analyses this affects

PRs without this context will be held until the author can provide it.

---

## General Rules

- **Read-only.** See `CLAUDE.md` § BigQuery Access for the full rule.
- **Validate before submitting.** Run any SQL you document against real data to confirm it works.
- **Document the "why".** Future contributors need to understand why a rule exists, not just what it does.
- **Scope your changes.** Fix one thing per PR. Mixed-purpose PRs are harder to review and easier to reject.
