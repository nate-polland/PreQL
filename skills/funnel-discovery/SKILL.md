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

1. **Know your table type** before querying:
   - **Sequential event tables** (e.g., BigEvent): one row per event with timestamps — can build per-user ordered paths directly
   - **Pre-aggregated summary tables** (e.g., SRRF): one row per user with binary flags — shows what steps were hit but not timestamps or ordering. Use these to understand path patterns; go to the event table for sequential traces.
2. **Sample the completion anchor** (LIMIT 5, tight date window) — confirm field names, timestamp format, and that the filter returns expected records
3. **Validate the anchor table** — before building anything on it, check:
   - Daily volume regularity (2–3 weeks) — zero-volume days followed by spikes indicate batch writes, not real-time tracking
   - Field completeness — are the join keys (numericId, traceId, cookieId, etc.) populated?
   - Timestamp reliability — is the timestamp when the event occurred, or when the record was written?
   - For binary flags: validate semantics against a ground truth table — flags can be inverted (e.g., `1` = failure, not success). Always check before assuming.
   - If the anchor fails these checks, find a better one before proceeding
4. **Find a tight time window** — use a 1–3 day window with stable, representative volume. Target 20–100 completers. Avoid `LIMIT` across a wide date range.
5. **Confirm the window with the user** before running any joins.

### Query Execution
The BigQuery MCP connection times out at ~60s. For large event table joins, use the project's async script (`bq_async.sh`). For smaller tables, MCP is fine.

**Use async for:** any query joining large event tables on non-partition keys, multi-CTE funnels, anything likely >30s. Refer to `CLAUDE.md` for the exact async script path and usage for this project.

**Use MCP for:** counts, schema checks, INFORMATION_SCHEMA, small tables.

## Phase 3 — Handle Unauthenticated Users

If users start unauthenticated:
1. **Identify available session identifiers** on the completion event — check null rates for traceId, cookieId, deviceId, numericId
2. **Choose the stitch key** — for BigEvent funnels, `user_traceId` is the cross-auth stitch key (`glid` is auth-only and will miss pre-auth events). For other tables, use `cookieId` or whichever ID is populated pre-auth.
3. **Validate stitch key completeness and cardinality** — two checks required:
   - *Completeness*: for a few users (3, then 3 more), find another ID associated with their stitch key. Search for events on that secondary ID where stitch key is NULL. If you find funnel events, the stitch key is missing sessions.
   - *Cardinality*: count how many distinct users (numericIds) map to each stitch key value. A stitch key that maps to multiple users (shared device, browser reset) will corrupt session attribution. Check both directions: stitch key → numericId AND numericId → stitch key.
4. **No single ID may cover the full session** — if the funnel crosses auth boundaries or page reloads, define the session as a combination of IDs: use a fine-grained ID (e.g., traceId) within a single auth state, and a persistent ID (e.g., cookieId) to bridge across boundaries. Gate cross-boundary stitching on 1:1 cardinality per the persistent ID, and document the session definition explicitly in the funnel doc.
5. **Re-run Phase 2** using the validated stitch key(s)

## Phase 4 — Build the Funnel Top-Down

The mental model is always top-down, even if data discovery required starting from the end. Building the funnel has two stages: **structure first, then counts.**

### Stage 1: Build the structure (small sample)

Start with 1–2 users. Build their full per-user ordered event sequences. Understand their paths. Then validate with 3–4 more. Only widen after structure is stable.

1. **Establish the start** — for known completers, what's the earliest event in their session? Work backward from the completion event during discovery, then anchor here going forward.
2. **Establish end points** — the completion event, plus all dropout points
3. **Build per-user ordered paths** — pull all events ordered by timestamp. Do NOT aggregate first — you lose the sequential structure.
4. **Derive step-to-step transitions** — from per-user paths, extract every consecutive step pair (A → B). This produces the directed graph.
5. **Investigate rare paths before discarding** — a single-user path in a small sample may represent a real segment at scale, a query artifact, or a tracking gap. Walk the raw sequence to determine which.
6. **Disambiguate user types with the user** — never assume user types based on path length. Ask what distinguishes new vs returning users (e.g., a TOS screen, a specific flag, absence of numericId). Validate that distinguishing events actually appear in data.
7. **Visualize as a flowchart** — generate a directed graph using Python (`graphviz`). Use `splines=true` with `xlabel` for edge labels. Use `rank=same` subgraphs for row control. Always `open` the rendered image in Preview for the user to review.

Do not pre-filter to completers — dropoffs are the primary insight.

### Stage 2: Validate and expand

- Expand to a full day, then 3 days — confirm no new paths emerge
- **Visualize and checkpoint with the user** — render the funnel and present it before counts. Do not proceed to counts until the user confirms structure.
- **Define KPIs with the user** before writing measurement queries. At minimum: overall conversion rate (entry → completion). Also ask: step-by-step rates? By user type/path? Trending over time? These answers determine which pattern to use — see `Context/funnel-measurement-patterns.md`.
- Only then populate with counts (volumes, drop-off rates per step, per path if applicable)

## Phase 5 — Identify Dropoff Population

Two types of drop-off:
- **Organic drop-off**: user saw a step impression but never proceeded (quit, abandoned) — last event was an impression (`system_eventType IN (1, 4)`)
- **Disappearance**: user completed an action on step A, but step B never fired (possible technical failure or tracking gap) — last event was an action (`system_eventType IN (2, 3)`)

Steps:
1. Count users who reached early steps but NOT the completion event
2. Use pre-auth identifiers (cookieId, traceId) for unauthenticated dropoffs
3. For each non-completer, find their last event and classify as organic vs. disappearance based on `system_eventType`
4. Group by last screen + dropout type — this surfaces the primary dropout locations

See `Context/funnel-measurement-patterns.md` Pattern 3 for the SQL template.

## Phase 6 — Document

Create `Funnels/[funnel-name].md` with a metadata header and add an entry to `Funnels/_index.md`.

Metadata header:
```
---
created: [date]
last_validated: [date]
data_window: [dates used for validation]
status: active
---
```

Document contents:
- Completion anchor (table, filter, timestamp field) — note reliability caveats
- Entry point and filters
- Session stitch method and validated coverage
- Session window (user estimate + buffer, note if empirically validated)
- User types and validated paths (with sample size)
- Step/screen map table
- Timing from entry point
- Drop-off paths and types (organic vs disappearance)
- Open questions / things not yet validated
- Tables used
- Experiments (optional — omit section entirely if no experiments are attached)

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
- **Darwin join:** `[experiment table]` on `numericId`, filter `first_bin_flag = true AND reseed_flag = 0`
```

Only document the delta — what is structurally different in the test arm vs. control. Screens that are identical need not be listed.

### Query pattern for per-arm funnel comparison

1. **Get experiment population** — join Darwin table to the funnel population by `numericId` within the experiment date window. Filter to `first_bin_flag = true AND reseed_flag = 0`.
2. **Split by arm** — group by `groupName` (control vs. test variants)
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
- Investigate rare paths before discarding
- For pre-aggregated tables: binary flag patterns show what paths were hit, but go to the underlying event table for per-user timestamps and ordering
- When tracing cross-auth sessions: identify which session identifier persists across the auth boundary (e.g., cookieId). A new session ID (traceId) is typically created at authentication AND at page reloads/errors — TOS and other pre-auth steps may be on a different session ID than the completion event. A traceId change is NOT automatically a dropout — check whether the cookieId is shared and the time gap is consistent with a reload. Stitch via cookieId to connect the full journey.
- Document everything to Funnels/ so future queries work without re-exploration
- Refer to the project's `CLAUDE.md` and `Schema/` for table names, event field names, and stitch key specifics

## Sharing Your Work

The funnel doc you just created is saved locally and available to you immediately. It is **not yet shared** with the rest of the team. When you're ready to contribute it back to the shared repo, run `/contribute` and PreQL will walk you through the process.
