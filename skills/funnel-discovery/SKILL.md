---
name: funnel-discovery
description: |
  Interactive funnel discovery workflow. Use when the user wants to map an unfamiliar product funnel — identifies steps, user paths, session stitching needs, dropoff points, and generates a reusable Funnels/ doc.

  Trigger phrases: "build a funnel", "map this funnel", "what screens do users see", "funnel for [product/flow]", "analyze [X] flow", or any request to understand an end-to-end user journey.
---

# Funnel Discovery Workflow

You are a Senior Product Analyst helping to reverse-engineer and document a product funnel. Work interactively with the user through these phases. This skill is fully table-agnostic and reusable — funnels may be sourced from any event table, pre-aggregated summary table, consent table, or any combination. Do not assume any specific table names, project IDs, or column names. Refer to the project's `CLAUDE.md` and `Schema/` files for table-specific details.

## Phase 1 — Define the Funnel

Ask the user:
1. **What is the completion event?** (e.g., consent table record, specific BigEvent click, flag in a summary table)
2. **What table/screen defines a completer?** Get the exact table, filter, and timestamp field
3. **What type of table is the data source?** Sequential event table (one row per event with timestamps — can trace per-user paths directly) or pre-aggregated summary table (one row per user with binary flags — shows what steps were hit but not ordering or timing; must go to the underlying event table for sequential traces)?
4. **Do users start authenticated or unauthenticated?** If unauthenticated: identify the cross-auth stitch key available in the source table (e.g., `user_traceId` in BigEvent, `cookieId` in summary tables)
5. **Approximate time window?** Ask the user how long the funnel typically takes. They'll have a rough idea. Add a buffer (e.g., if they say 5-10 minutes, start with 15). Refine empirically as data comes in.
6. **New vs returning users?** If both, expect multiple paths
7. **What are the KPIs?** Every user will have different goals. Ask explicitly — don't assume. Common options:
   - Overall conversion rate (entry → completion)
   - Step-by-step conversion rates
   - Drop-off by screen (and organic vs. disappearance breakdown)
   - Conversion by user type / path
   - Trend over time (weekly, daily)
   - Experiment comparison (control vs. test arm)

   The KPIs determine the query structure. Nail them here before building anything.

## Phase 2 — Align Before Querying

Before writing any SQL, present your understanding of the key query assumptions back to the user and ask them to confirm or correct. Cover:

- **What you know**: completion anchor (table, filter, timestamp), stitch key, any known step names
- **What you're assuming**: session window duration, population scope (US only? all users?), mapping vs measuring intent, whether multiple user paths are expected
- **What you're uncertain about**: any field names, join keys, or step names that haven't been validated in data yet

Present this as a short bullet summary — not a list of questions. Let the user correct what's wrong rather than answering each item individually. Wait for confirmation before writing any SQL.

## Phase 2b — Cheap Diagnostics First

Only after Phase 2 alignment is confirmed:

**Query planning rule — required before writing any SQL.** For every query, state a brief plan first:
- **Table + partition filter** — which table, which `DATE(ts)` range
- **Columns needed** — only what the query output requires; no extras
- **Join key** — how tables connect, and whether 1:1 cardinality is assumed
- **Expected output shape** — one row per what? (user, session, screen, day?)
- **Expected order of magnitude** — rough row count expectation

State this before writing SQL. It catches join-key mismatches and column overselection before compute is spent, and gives the user a chance to redirect.

1. **Know your table type** before querying:
   - **Sequential event tables** (e.g., BigEvent): one row per event with timestamps — can build per-user ordered paths directly
   - **Pre-aggregated summary tables** (e.g., SRRF): one row per user with binary flags — shows what steps were hit but not timestamps or ordering. Use these to understand path patterns; go to the event table for sequential traces.
2. **Sample the completion anchor** (LIMIT 5, tight date window) — confirm field names, timestamp format, and that the filter returns expected records
3. **Verify the anchor is funnel-specific** — some screens (consent screens, marketplace pages, login redirects) are shared across multiple integrations. Before building anything on an anchor, cross-check: of all users who hit the anchor screen, what fraction also have the entry filter within the session window? If the anchor has large volume with no plausible entry-cohort match, it's likely shared. Example failure mode: `link-anywhere` appeared to be an LBE completion screen but was shared across all Intuit integrations — only 10 of 3,912 LBE entrants hit it.
4. **Validate the anchor table** — before building anything on it, check:
   - Daily volume regularity (2–3 weeks) — zero-volume days followed by spikes indicate batch writes, not real-time tracking
   - Field completeness — are the join keys (numericId, traceId, cookieId, etc.) populated?
   - Timestamp reliability — is the timestamp when the event occurred, or when the record was written?
   - For binary flags: validate semantics against a ground truth table — flags can be inverted (e.g., `1` = failure, not success). Always check before assuming.
   - If the anchor fails these checks, find a better one before proceeding
5. **Find a tight time window** — use a **3-day window** with stable, representative volume. Target 20–100 completers. Avoid `LIMIT` across a wide date range. Use 3 days (not 1) from the start — rare screens (e.g., branded offer cards, survey flows, 2FA paths) only appear in 3+ day samples; a 1-day window will miss them and force a second join query.
6. **Confirm the window with the user** before running any joins.
7. **Run broad screen inventory as your first event table join** — before any per-user path traces, run:
   ```sql
   GROUP BY [screen_field], [event_code_field], [event_type_field],
   COUNT(DISTINCT [stitch_key]) AS users
   ```
   over the full entry cohort with the extended session window. One async query gives you the complete screen inventory — every screen and volume combination — before you trace a single user. This eliminates the round-trip pattern of "trace user → discover new screen → trace again." Per-user path traces (Phase 4 Stage 1) are then used to understand *ordering and transitions* within the known screen set, not to discover new screens.

### Query Execution
The MCP connection may time out for long-running queries. For large event table joins, use the project's async execution script (see `CLAUDE.md`). For smaller tables, MCP is fine.

**Use async for:** any query joining large event tables on non-partition keys, multi-CTE funnels, anything likely >30s. Refer to `CLAUDE.md` for the exact async script path and usage for this project.

**Use MCP for:** counts, schema checks, INFORMATION_SCHEMA, small tables.

**After every query — validate before interpreting results:**
1. **Non-zero rows** — zero rows means the filter is wrong or the field doesn't exist. Debug before proceeding; don't present empty results as a finding.
2. **Plausible row count** — does the order of magnitude match the plan? A count 10x higher than expected usually means a join is fanning out (missing 1:1 cardinality gate). A count 10x lower usually means the partition filter is too tight or a field value doesn't match.
3. **Spot-check values** — pick 2-3 rows and verify IDs, timestamps, and screen names look realistic. Null-heavy key columns indicate a join key mismatch.
4. **Partition scan (async only)** — verify the query scanned only the intended date range. A full-table scan means `DATE(ts)` didn't push down as a partition filter — rewrite the WHERE clause before widening the window.

## Phase 3 — Handle Unauthenticated Users

If users start unauthenticated:
1. **Identify available session identifiers** on the completion event — check null rates for traceId, cookieId, deviceId, numericId
2. **Choose the stitch key** — for event table funnels, identify which ID persists across the auth boundary. A page-load or trace ID may reset on navigation; a browser/cookie ID typically persists. Check null rates for each candidate to find the best stitch key.
3. **Validate stitch key completeness and cardinality** — two checks required:
   - *Completeness*: for a few users (3, then 3 more), find another ID associated with their stitch key. Search for events on that secondary ID where stitch key is NULL. If you find funnel events, the stitch key is missing sessions.
   - *Cardinality*: count how many distinct users (numericIds) map to each stitch key value. A stitch key that maps to multiple users (shared device, browser reset) will corrupt session attribution. Check both directions: stitch key → numericId AND numericId → stitch key.
4. **No single ID may cover the full session** — if the funnel crosses auth boundaries or page reloads, define the session as a combination of IDs: use a fine-grained ID (e.g., traceId) within a single auth state, and a persistent ID (e.g., cookieId) to bridge across boundaries. Gate cross-boundary stitching on 1:1 cardinality per the persistent ID, and document the session definition explicitly in the funnel doc.
5. **Re-run Phase 2** using the validated stitch key(s)

## Phase 4 — Build the Funnel Top-Down

The mental model is always top-down, even if data discovery required starting from the end. Building the funnel has two stages: **structure first, then counts.**

### Stage 1: Build the structure (small sample)

**Prerequisite:** The broad screen inventory (Phase 2b step 7) must be complete before this stage. You already know every screen that exists in the funnel — per-user path traces here are to understand *ordering and transitions*, not to discover new screens.

Start with 1–2 users. Build their full per-user ordered event sequences. Understand their paths. Then validate with 3–4 more. Only widen after structure is stable.

1. **Establish the start** — for known completers, what's the earliest event in their session? Work backward from the completion event during discovery, then anchor here going forward.
2. **Establish end points** — the completion event, plus all dropout points
3. **Build per-user ordered paths** — pull all events ordered by timestamp. Do NOT aggregate first — you lose the sequential structure.
4. **Derive step-to-step transitions** — from per-user paths, extract every consecutive step pair (A → B). This produces the directed graph.
5. **Investigate rare paths before discarding** — a single-user path in a small sample may represent a real segment at scale, a query artifact, or a tracking gap. Walk the raw sequence to determine which. **Never apply an inclusion/exclusion threshold silently.** Present all findings to the user with their volumes and let them decide what to include or exclude from the flowchart.
6. **Disambiguate user types with the user** — never assume user types based on path length. Ask what distinguishes new vs returning users (e.g., a TOS screen, a specific flag, absence of numericId). Validate that distinguishing events actually appear in data.
7. **Visualize as a flowchart** — write a Mermaid `flowchart TD` diagram and render it via a local HTML file. Do NOT use graphviz or Python for visualization.

   **Rendering:** Create `Funnels/[funnel-name]-flowchart.html` containing the Mermaid diagram with the CDN script (`https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js`). Open with `open "path/to/file.html"` — this opens in the user's default browser without requiring a dev server or Chrome MCP.

   **Color-code every node by type** using `classDef`:
   ```
   classDef frontend fill:#dbeafe,stroke:#3b82f6,color:#1e3a8a
   classDef backend fill:#fef3c7,stroke:#f59e0b,color:#78350f
   classDef drop fill:#fee2e2,stroke:#ef4444,color:#7f1d1d
   classDef completion fill:#dcfce7,stroke:#22c55e,color:#14532d
   ```
   Include a matching HTML legend above the diagram.

   **Classification rule — default to frontend:**
   - **Frontend (blue):** any step where the user sees a screen, enters data, or makes a choice — classify as frontend even if a backend table also tracks the event
   - **Backend (amber):** steps with no user-facing screen — system decisions, vendor API calls, record creation
   - **Drop (red):** all drop-off nodes; use stadium shape `(["Drop"])`
   - **Completion (green):** the single completion node

   **Drop-off nodes:** add an explicit drop branch at every step where users can exit — not just terminal failures. Label the drop edge with the signal that indicates dropout (e.g., error flag name).

   Embed the same Mermaid source in the funnel doc (`.md`) so it renders in markdown viewers. Keep the HTML file in sync with the `.md` source.

Do not pre-filter to completers — dropoffs are the primary insight.

### Stage 2: Enrichment

Before validating the full funnel, investigate every branch where the next screen or outcome is uncertain. Enrichment is targeted: pick a specific branch (e.g., "what happens after a prove fail?"), find users who took that path, and trace their full event sequences.

**Pattern — use pre-aggregated tables to find users, then trace in the event table:**
If a pre-aggregated or summary table has flags that identify the population for a branch, use those flags to pull user IDs, then query the event table for their full sequences. This is faster and more reliable than trying to identify branch populations from event data alone. The specific tables and IDs depend on the funnel — refer to `Schema/` docs for what's available.

**For each uncertain branch:**
1. Use the cheapest source to identify 3 users on that branch (summary table flags, event filters, etc.)
2. Pull their full event time series via async
3. Document what screens they actually hit — do they match the flowchart? Are there screens missing?
4. Update the flowchart with findings (add new edges/nodes, relabel existing ones)

**Do not add counts during enrichment.** Counts come after the structure is validated. Adding counts to unvalidated branches creates false confidence.

Repeat until the user confirms all branches are accounted for.

### Stage 3: Full validation

After enrichment, validate the overall funnel structure by sampling random **entry-cohort** users (not completers, not path-stratified). The goal is to catch any screen or path that enrichment missed.

1. Sample N random users who hit the funnel entry point — N should scale with funnel complexity (~100 for a funnel with ~10 distinct paths, enough to surface any path taken by >3% of entrants)
2. Pull their full event sequences — all screen/step values, not filtered to known screens
3. Scan for any screen not already in the flowchart
4. For any new screen found, trace the users who hit it and determine where it fits in the funnel

**Why entry-cohort, not completers:** sampling from completers only reveals screens on completion paths. Users who drop early may encounter screens that completers never see.

**Checkpoint:** present any new screens found to the user. If none, the structure is validated.

### Stage 4: Expand and populate counts

- Expand to a full day, then 3 days — confirm no new paths emerge
- **Visualize and checkpoint with the user** — update the HTML flowchart and re-open it before counts. Do not proceed to counts until the user confirms structure.
- **Define KPIs with the user** before writing measurement queries. At minimum: overall conversion rate (entry → completion). Also ask: step-by-step rates? By user type/path? Trending over time? These answers determine which pattern to use — see `Context/funnel-measurement-patterns.md`.
- Only then populate with counts (volumes, drop-off rates per step, per path if applicable)

## Phase 5 — Identify Dropoff Population

Two types of drop-off:
- **Organic drop-off**: user saw a step (impression/view event) but never proceeded — last event was a view-type event
- **Disappearance**: user completed an action on step A, but step B never fired (possible technical failure or tracking gap) — last event was an action/submit event

Steps:
1. **Broad scan first** — before filtering to a predefined screen list, run a wide query: for all non-completers, what `content_screen` values did they hit within the session window? Group by screen, order by user count. This surfaces the full set of dropout screens — pre-defining the list from the flowchart alone will miss drops at screens not yet mapped (typically 30–40% of drops in complex funnels).
2. Use the broad scan results to build the predefined screen list for the detailed query
3. Count users who reached early steps but NOT the completion event
4. Use pre-auth identifiers (cookieId, traceId) for unauthenticated dropoffs
5. For each non-completer, find their last event and classify as organic vs. disappearance based on the event type field
6. Group by last screen + dropout type — this surfaces the primary dropout locations

See `Context/funnel-measurement-patterns.md` Pattern 3 for the SQL template.

## Phase 6 — Document

Create `Funnels/[funnel-name].md` with a metadata header and add an entry to `Funnels/_index.md`.

Metadata header:
```
---
created: [date]
last_validated: [date]
data_window: [dates used for validation]
status: in_progress
---
```

Document contents:
- Completion anchor (table, filter, timestamp field) — note reliability caveats
- Entry point and filters
- Session stitch method and validated coverage
- Session window (user estimate + buffer, note if empirically validated)
- User types and validated paths (with sample size)
- Step/screen map table
- Recent Metrics (full step counts — see below)
- Timing from entry point
- Drop-off paths and types (organic vs disappearance)
- Open questions / things not yet validated
- Tables used
- Experiments (optional — omit section entirely if no experiments are attached)

**`## Recent Metrics` section format:** A dated snapshot table of every funnel step with its raw count. Include one row per step — impression count, submit count, terminal drop count. This allows any conversion or drop rate to be calculated from the doc without requerying. Append a new snapshot when counts are refreshed; keep prior snapshots for trend context.

**Finalization checkpoint:** Before closing out a funnel, ask the user:
1. **Flowchart** — is the flowchart final? Once confirmed, mark `status: final` in the `.md` header and note the date.
2. **Queries** — are there any queries from this discovery (entry cohort, screen inventory, cohort classification, funnel counts) worth persisting? Add validated, runnable versions to `Queries/` following the format in `Queries/_index.md`. Only persist queries that are non-trivial to reconstruct and likely to be reused. Don't add minor variants of existing queries.

Report: "Funnel documented at `Funnels/[funnel-name].md`. Ready for funnel queries."

## Experiment Overlay (Optional)

**Only use this phase when an experiment modifies the funnel.** Most funnels start without one — skip this entirely until an experiment is introduced.

The funnel doc always represents the **control** path. Experiments are documented as a delta on top of that baseline — not as a new full funnel.

### When an experiment is added

**Document in the `## Experiments` section of the funnel doc:**
```
### Experiment [ID] — [brief description]
- **Date range:** [rampStartDate] to [rampEndDate or "ongoing"]
- **Arms:** control ([N] users), [arm name] ([N] users)
- **What changed:**
  - Entry point: [same as control / or: test arm uses different filter/screen]
  - [Screen X] replaced by [Screen Y] in test arm
  - [New screen Z inserted between A and B in test arm]
- **Experiment join:** `[experiment_table]` on `[user_id]`, with standard assignment filters (see `Context/experiment-analysis.md`)
```

Only document the delta — what is structurally different in the test arm vs. control. Screens that are identical need not be listed.

### Query pattern for per-arm funnel comparison

1. **Get experiment population** — join experiment table to the funnel population by user ID within the experiment date window. Apply standard assignment filters (first assignment, no reseeding — see schema docs).
2. **Split by arm** — group by the variant/group field (control vs. test variants)
3. **Run the funnel query per arm** — for control: use the standard funnel query as documented. For test arms with structural changes (different entry point, different screens): modify the query to match the test arm path.
4. **Compare step-by-step** — for each funnel step, report `users_reached`, `users_completed_step`, and `conversion_rate` per arm side by side.

**Important:** If the test arm has a different entry point, the control funnel query cannot be applied to the test arm unchanged. Document what the test arm entry filter is and run it separately.

### What NOT to do
- Do not create a new funnel doc for a test arm variant — document the delta here
- Do not overwrite the control funnel definition
- Do not mix control and test arm users in a single funnel query

## Key Rules
- **READ ONLY — ABSOLUTE RULE.** SELECT only. No writes under any circumstances.
- Always sample cheaply before scaling
- Start with 1–2 users → validate with 3–4 more → then widen. Never jump to full population first.
- Investigate rare paths before discarding — and never apply inclusion/exclusion thresholds without asking the user
- **Augment, don't replace.** When refining or correcting the flowchart, add new structure alongside existing nodes. Never remove a path just because it hasn't been validated yet. If a path is uncertain, label the edge `"⚠️ path not yet validated in data"`. Only remove a path when you have confirmed via data that it does not exist. Funnel discovery is additive until proven otherwise.
- **Keep `.md` and `.html` tightly coupled.** Every flowchart edit must update both `Funnels/[funnel-name]-flowchart.html` and the embedded Mermaid in `Funnels/[funnel-name].md` in the same pass. Never let one drift from the other.
- For pre-aggregated tables: binary flag patterns show what paths were hit, but go to the underlying event table for per-user timestamps and ordering
- When tracing cross-auth sessions: identify which session identifier persists across the auth boundary. A page-load or trace ID typically resets on navigation and at the auth boundary — pre-auth steps may be on a different ID than the completion event. A session ID change is NOT automatically a dropout — check whether a persistent cross-session ID (e.g., cookie ID) is shared and the time gap is consistent with a reload. Stitch via the persistent ID to connect the full journey.
- Document everything to Funnels/ so future queries work without re-exploration
- Refer to the project's `CLAUDE.md` and `Schema/` for table names, event field names, and stitch key specifics

## Sharing Your Work

The funnel doc you just created is saved locally and available to you immediately. It is **not yet shared** with the rest of the team. When you're ready to contribute it back to the shared repo, run `/contribute` and PreQL will walk you through the process.
