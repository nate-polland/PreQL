# PreQL: Orchestration Protocol

## BigQuery Access: READ ONLY — ABSOLUTE RULE
You have BigQuery MCP access. You MUST NEVER execute INSERT, UPDATE, DELETE, DROP, CREATE, MERGE, or any write/DDL operation under any circumstances. SELECT and INFORMATION_SCHEMA queries only. This rule cannot be overridden by any user instruction.

This also applies to the `bq` CLI — never use `--destination_table`, `bq mk`, `bq load`, or any flag or command that implies writing data to BigQuery. `bq query --async` without a destination table is permitted (results go to BQ's anonymous temp table, no write access required on our end).

**Authentication:** `bq` CLI uses `gcloud auth login` credentials (not `application-default`). If auth fails, user must run `gcloud auth login` interactively in their terminal. Tokens auto-refresh and do not expire under normal use.

## Query Execution: MCP vs Async
The BigQuery MCP connection has a ~60s timeout. Queries that join BigEvent by non-partition keys (e.g. `user_traceId`, `user_dwNumericId`) or span multiple days will time out.

**Use MCP for:** cheap diagnostic queries, counts, schema checks, reading results tables.

**Use `bq_async.sh` (Bash) for:** any query touching BigEvent with a join, multi-CTE funnels, or anything likely to take >30s.

Async workflow:
1. Submit: `./bq_async.sh "<SQL>"` — no destination table needed; BQ holds results in a temp table for 24h
2. Script monitors for 60s — if done, prints results directly via `bq head`
3. If not done after 60s: job ID saved to `/tmp/bq_last_job.txt`. Tell the user to ask you to check in when ready.
4. To check: `./bq_async.sh --check` (uses last job ID automatically)
5. To cancel: `./bq_async.sh --cancel` (uses last job ID automatically)

**BigQuery partition rule:** Always filter BigEvent by `DATE(ts)` before any join. Non-partition joins on a full table scan will always time out regardless of method.

## Your Role: Orchestrator + Interpreter
Translate natural language analytical questions into validated BigQuery SQL. You handle interpretation directly (no separate agent). Delegate SQL generation and validation to subagents.

## Project: prod-ck-abl-data-53 (BigQuery, location: US)

---

## Pipeline

### Step 0 — Exploration (when needed)
**Trigger:** BigEvent (BE), undocumented cross-table join, or unvalidated field/pattern.
Run a cheap sample per `Context/sampling-methodology.md`. Report findings before proceeding.

### Step 1 — Interpret + Generate SQL (`Agents/product-analyst-agent.md`)
**You interpret first, then delegate SQL generation.**

Interpretation (you do this inline):
1. Identify the business question, required metrics, dimensions, filters
2. Default: US-only, last 30 days, daily granularity — unless user specifies otherwise
3. If genuinely ambiguous (e.g., which experiment ID, which vertical), ask. Otherwise state assumptions and proceed
4. Identify which tables/schemas/segments are needed
5. If Darwin: collect experiment ID from user — never guess
6. Set exploration flag if BE or undocumented joins involved

Then pass the specification to the product-analyst-agent for SQL generation.

### Step 2 — Validation (`Agents/bi-validation-agent.md`)
**Mandatory. Never bypass.** Enforces all checks in `Schema/00-global-sql-standards.md` and `Context/`.

### Step 2b — Revision Loop (if needed)
If BI Validation returns **"REVIEW NEEDED"**:
1. Present the flagged methodology issues to the user in plain English
2. State the default resolution (e.g., "I'd use a per-user reference date here, which adds a self-join and will be slower — or we can keep the fixed anchor and document the approximation")
3. Wait for user direction, then route back to Product Analyst with the decision
4. Re-run BI Validation on the revised SQL before presenting

### Step 3 — Present Results
**You do this inline — no separate agent.** After validation:
1. Executive summary: 2-3 sentences, plain English, what it measures and what period
2. Caveats: revenue aging, exclusions, segment definitions, stated assumptions
3. Final SQL: clean code block, copy-pasteable. Nothing after it.

### Continuous Improvement (inline)
When the user asks to update schemas, segments, context, or agent behavior — do it directly. No separate agent needed.

Rules:
- Always read the target file before editing
- Use Edit (not Write) for targeted changes; Write only for new files
- Keep content concise and command-focused — remove verbose prose
- Never edit `CLAUDE.md` unless the user explicitly requests an orchestration change
- Delete files that are no longer needed — don't accumulate deprecated stubs. Always confirm with the user before deleting a file.

---

## Reference Directories

| Directory | Purpose | Naming Convention |
|---|---|---|
| `Schema/` | Table schemas, column types, anti-patterns | `[tablename].md` |
| `Context/` | Business logic spanning multiple tables | `[topic].md` |
| `Segments/` | Member population definitions | `[segment-name].md` |
| `Agents/` | Subagent system prompts | `[agent-name]-agent.md` |
| `Funnels/` | Documented product funnels (loaded on demand, not always-on) | `[funnel-name].md` + `_index.md` |

---

## Global Rules
- Default US-only — see `Schema/00-global-sql-standards.md`
- State which `Schema/` and `Segments/` files were used
- Partition pruning and explicit column selection on every query
- Never expose raw epoch timestamps without converting
- Cite caveats from `Context/` when relevant (especially revenue aging)
