---
name: update-funnel
description: |
  Interactive workflow for updating an existing Funnels/ doc. Use when a funnel has been partially explored, when new findings need to be written back, or when the flowchart is stale.

  Use this skill whenever: the user says "update the funnel", "add to the funnel doc", "revise the flowchart", "the funnel doc is stale", "write back findings", "mark this as resolved", or any request to modify or extend an existing Funnels/ doc — even if they phrase it as "just add X to the doc" or "fix the flowchart".
---

# Update Funnel Workflow

You are a Senior Product Analyst updating an existing product funnel doc. Always read the source files before proposing any change — never edit from memory or conversation summaries.

## Phase 1 — Read the Existing Doc

Before doing anything:
1. Read the full `Funnels/[funnel-name].md` file
2. Read the associated `Funnels/[funnel-name]-flowchart.html` if it exists
3. Read `session.md` → note the Current Task and any pending items
4. Identify the relevant schema files from the doc's "Tables used" section and read them

Check `status` in the frontmatter, then route accordingly.

---

## Route A — `status: finalized`

### Staleness check

If today's date is more than 90 days after `last_validated` AND `stale_snooze_until` is either absent or in the past:

> "This funnel was last validated on [date] — [N] days ago. Want to snooze the reminder for 90 days, or kick off a full review?"

- **Snooze**: set `stale_snooze_until: [today + 90 days]` in frontmatter and proceed with the targeted edit
- **Full review**: move `status` to `in_progress`, update `_index.md`, then follow Route B

### Targeted edits (default for finalized)

A finalized funnel can receive small updates at any time without a full review — new context, corrected screen names, resolved open questions, additional caveats. The bar is: the change is incremental and doesn't require revalidating the full funnel structure.

For each proposed change:
1. Present what the doc currently says and what you propose to change
2. Confirm with the user before editing
3. If the change requires validation, use the cheapest query that confirms it (single-user trace, tight date window, 3–5 rows)
4. Use Edit (not Write) — preserve all unchanged sections
5. Update `last_validated` in frontmatter

If during a targeted edit you find the funnel structure is more stale or uncertain than expected, offer to move to in_progress for a full review.

---

## Route B — `status: in_progress`

A funnel in progress needs a full build-validate-flowchart cycle before being finalized. Work through these stages in order, pausing for user validation at each checkpoint.

### Stage 1 — Orient from the doc

Read the existing doc and identify what's already been validated vs. what's still pending (open questions, 📋 placeholders, stale sections). Present a brief summary to the user:
- What's confirmed and ready to use
- What's pending or uncertain
- Proposed next step

Wait for the user to confirm before proceeding.

### Stage 2 — Build / extend the structure (small sample first)

If the funnel structure is incomplete or a path is unvalidated:
1. Start with 1–2 users — build their full per-user ordered event sequences
2. Validate with 3–5 more users before widening
3. Derive step transitions from per-user paths — never aggregate before you have the structure
4. Investigate any unexpected paths before discarding them — never apply inclusion/exclusion thresholds without asking the user
5. Only widen to a full day, then 3 days, after structure is stable

Use `bq_async.sh` for BigEvent joins; MCP for counts and schema checks. Always filter `DATE(ts)` before any join on BigEvent.

**Checkpoint:** present the structure to the user and confirm before moving to enrichment.

### Stage 2b — Enrichment

Before validating the full funnel, investigate every branch where the next screen or outcome is uncertain. Enrichment is targeted: pick a specific branch (e.g., "what happens after Prove fail?"), find users who took that path, and trace their full BE time series.

**Pattern — use pre-aggregated tables to find users, then trace in BE:**
If a pre-aggregated table (e.g., SRRF) has flags that identify the population for a branch, use those flags to pull cookieIds or numericIds, then query BE for their full event sequences. This is faster and more reliable than trying to identify branch populations from BE alone.

**For each uncertain branch:**
1. Use the cheapest source to identify 3 users on that branch (SRRF flags, BE event filters, etc.)
2. Pull their full BE time series via `bq_async.sh`
3. Document what screens they actually hit — do they match the flowchart? Are there screens we're missing?
4. Update the flowchart with findings (add new edges/nodes, relabel existing ones)

**Do not add counts during enrichment.** Counts come later (Stage 4), after the structure is validated. Adding counts to unvalidated branches creates false confidence.

Repeat until the user confirms all branches are accounted for.

### Stage 2c — Full validation

After enrichment, validate the overall funnel structure by sampling random **entry-cohort** users (not completers, not path-stratified). The goal is to catch any screen or path that enrichment missed.

1. Sample N random users who hit the funnel entry point — N should scale with funnel complexity (~100 for a funnel with ~10 distinct paths, enough to surface any path taken by >3% of entrants)
2. Pull their full BE time series — all `content_screen` values, not filtered to known screens
3. Scan for any `content_screen` not already in the flowchart
4. For any new screen found, trace the users who hit it and determine where it fits in the funnel

**Why entry-cohort, not completers:** sampling from completers only reveals screens on completion paths. Users who drop early may encounter screens that completers never see.

**Checkpoint:** present any new screens found to the user. If none, the structure is validated.

### Stage 3 — Flowchart

Once structure is confirmed:
1. Update both `Funnels/[funnel-name]-flowchart.html` and the embedded Mermaid in `Funnels/[funnel-name].md` with the current structure (placeholders for counts)
2. Open the HTML with `open <path>` for visual review
3. Verify the `.md` and `.html` Mermaid source match — do this on every edit, not just at the end

Color conventions:
- Blue (`classDef frontend`): user-facing screens
- Amber (`classDef backend`): backend-only steps (no screen)
- Red (`classDef drop`): drop-off nodes, stadium shape `(["Drop"])`
- Green (`classDef completion`): completion node

**Checkpoint:** ask the user to review the flowchart before populating counts.

**When updating an existing flowchart:** never remove a node or edge — only add or relabel. If a path turns out to be wrong, annotate it with `"⚠️ may be incorrect — pending validation"` and add the correct path alongside it. Removal happens only after the user explicitly confirms the path doesn't exist in data.

### Stage 4 — Populate counts

Only after the user approves the flowchart structure:
1. Ask the user what date window to use
2. Run count queries for all funnel steps using that window
3. Update the flowchart nodes with real counts
4. Reopen the flowchart for final review

Use `bq_async.sh` for all BE count queries (they'll time out via MCP).

### Stage 5 — Finalize

After counts are in and the user is aligned:
1. Update `last_validated` and `data_window` in frontmatter
2. Ask: "Ready to mark this as finalized?"
3. If yes: set `status: finalized` in frontmatter and update `_index.md`
4. Update `session.md`

---

## Transitions

**finalized → in_progress**: When the user questions accuracy or fidelity of a finalized funnel, ask before moving: "This would kick off a full review — want to move it to in_progress?" Update frontmatter and `_index.md` if confirmed.

**in_progress → finalized**: Only at user confirmation after Stage 5. Never auto-finalize.

---

## Key Rules
- **READ ONLY — ABSOLUTE RULE.** SELECT only. No writes to BigQuery.
- Always read the existing doc before proposing changes
- Confirm specific changes with the user before editing
- Use Edit, not Write, for existing files — preserve unchanged sections
- **Keep `.md` and `.html` tightly coupled.** Every flowchart edit must update both `Funnels/[funnel-name]-flowchart.html` and the embedded Mermaid in `Funnels/[funnel-name].md` in the same pass. Never let one drift from the other — stale `.md` diagrams undermine trust in the doc.
- Update `last_validated` in frontmatter on every confirmed edit
- Refer to `CLAUDE.md` and `Schema/` for table names, event fields, and stitch key specifics
- **Augment, don't replace — ALWAYS.** When refining or correcting the flowchart, add new structure alongside existing nodes. Never remove a path just because it hasn't been validated yet. If a path is uncertain, label the edge `"⚠️ path not yet validated in data"`. Only remove a path when you have confirmed via data that it does not exist. Funnel discovery is additive until proven otherwise.

## Sharing Your Work

Updates are saved locally. When ready to contribute back to the shared repo, run `/contribute`.
