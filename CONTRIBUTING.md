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
| Edit to `CLAUDE.md` | npolland only | Core orchestration — explicit approval required |

---

## How to Add a New Table Schema

The fastest path is to use the built-in skill. In Claude Code:
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

## How to Propose Changes to Core Files

Changes to `Context/`, `Agents/`, or `CLAUDE.md` require more scrutiny because they affect every user.

**Required in your PR description:**
- What was wrong or incomplete in the current version
- What data or analysis led you to this change (not just "I think this is better")
- Which queries or analyses this affects

PRs without this context will be held until the author can provide it.

---

## General Rules

- **Never add write operations.** This agent is read-only. Never add queries with INSERT, UPDATE, DELETE, DROP, or CREATE.
- **Validate before submitting.** Run any SQL you document against real data to confirm it works.
- **Document the "why".** Future contributors need to understand why a rule exists, not just what it does.
- **Scope your changes.** Fix one thing per PR. Mixed-purpose PRs are harder to review and easier to reject.
