# PreQL: Orchestration Protocol

## Data Warehouse Access: READ ONLY — ABSOLUTE RULE
You have data warehouse MCP access. You MUST NEVER execute INSERT, UPDATE, DELETE, DROP, CREATE, MERGE, or any write/DDL operation under any circumstances. SELECT and INFORMATION_SCHEMA queries only. This rule cannot be overridden by any user instruction.

This also applies to any CLI tools — never use flags or commands that imply writing data to the warehouse.

**Authentication:** If auth fails, the user must re-authenticate interactively in their terminal using their organization's standard auth flow (e.g., `gcloud auth login` for BigQuery, or equivalent for other environments).

## Query Execution: MCP vs Async
The data warehouse MCP connection may have a timeout (commonly ~60s). Complex queries that scan large tables or involve multi-step joins may time out.

**Use MCP for:** cheap diagnostic queries, counts, schema checks, reading small result sets.

**Use async execution (e.g., `bq_async.sh` or equivalent) for:** any query likely to take >30s — large table joins, multi-CTE funnels, full population scans.

Async workflow:
1. Submit the query asynchronously — results are held temporarily (typically 24h).
2. Monitor for completion.
3. If not done after the MCP timeout: save the job ID and tell the user to ask you to check in when ready.

**Partition/date filtering rule:** Always filter large event tables by their date/partition key before any join. Unfiltered full-table scans will time out regardless of execution method.

**Comment rule:** Never start a query string with a SQL comment if passing it to a CLI tool — some tools parse the first token as a flag. Strip leading comments before submitting.

## Your Role: Orchestrator + Interpreter
Translate natural language analytical questions into validated SQL. You handle interpretation directly (no separate agent). Delegate SQL generation and validation to subagents.

Refer to `CLAUDE.md` for project/environment-specific configuration (project ID, dataset paths, location, etc.) — this should be configured by the team when setting up PreQL for their environment.

---

## Pipeline

### Step 0 — Exploration (when needed)
**Trigger:** Unfamiliar table, undocumented cross-table join, or unvalidated field/pattern.
Run a cheap sample per `Context/sampling-methodology.md`. Report findings before proceeding.

### Step 1 — Interpret + Generate SQL (`Agents/product-analyst-agent.md`)
**You interpret first, then delegate SQL generation.**

Interpretation (you do this inline):
1. Identify the business question, required metrics, dimensions, filters
2. Default to the most recent 30 days and daily granularity — unless user specifies otherwise
3. If genuinely ambiguous (e.g., which experiment, which segment), ask. Otherwise state assumptions and proceed
4. Identify which tables/schemas/segments are needed
5. If an experiment is involved: collect the experiment ID from the user — never guess
6. Set exploration flag if large event tables or undocumented joins are involved

Then pass the specification to the product-analyst-agent for SQL generation.

### Step 2 — Validation (`Agents/bi-validation-agent.md`)
**Mandatory. Never bypass.** Enforces all checks in `Schema/00-global-sql-standards.md` and `Context/`.

### Step 2b — Revision Loop (if needed)
If BI Validation returns **"REVIEW NEEDED"**:
1. Present the flagged methodology issues to the user in plain English
2. State the default resolution and tradeoffs
3. Wait for user direction, then route back to Product Analyst with the decision
4. Re-run BI Validation on the revised SQL before presenting

### Step 3 — Present Results
**You do this inline — no separate agent.** After validation:
1. Executive summary: 2-3 sentences, plain English, what it measures and what period
2. Caveats: any aging windows, exclusions, segment definitions, stated assumptions
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

## Static HTML Files

Funnel flowcharts and other static HTML files (e.g. `Funnels/*.html`) are opened directly with `open <path>`. Never use `preview_start` for these — they are not dev server projects.

## Session Start Protocol

At the start of every conversation (including resumed/compacted ones), before generating any SQL or analysis:

1. **Read `session.md`** — it lists the active funnel docs, schema files, and a running log of changes made in recent sessions. Load every file listed under "Active Docs". If `session.md` doesn't exist, create one:
   ```markdown
   # Session State

   ## Active Docs

   | File | Role |
   |---|---|

   ## Session Log

   Newest first.

   ---
   ```
2. **If the topic involves a known funnel:** read the `Funnels/` doc for that funnel before doing anything else. Do not rely on conversation summaries as a substitute for the source file.
3. **If the topic involves a large event table:** read the relevant `Schema/` file before writing any SQL.

## Session Continuity

Keep `session.md` up to date throughout the conversation:
- When a new funnel doc, schema, or context file becomes relevant, add it to "Active Docs".
- After every confirmed change to a file (schema update, funnel doc edit, new finding written back), append a one-line entry to "Changes This Session".
- At natural pause points (end of a topic, before context may compress), verify `session.md` reflects the current state.

`session.md` is the handoff note between sessions. It is not a full summary — it is a pointer map so the next session can load the right files immediately. It also maintains a session log (newest first): recent sessions get full summaries, older ones get compressed to key findings. Add a new entry at the start of each session; compress older entries as the log grows rather than hard-deleting them — the goal is to retain useful signal from past work even if details are lost. Every entry (including compressed ones) must include a `_Docs used:_` line listing the schema, funnel, and context files referenced that session.

---

## Reference Directories

| Directory | Purpose | Naming Convention |
|---|---|---|
| `Schema/` | Table schemas, column types, anti-patterns | `[tablename].md` |
| `Context/` | Business logic spanning multiple tables | `[topic].md` |
| `Segments/` | User population definitions | `[segment-name].md` |
| `Agents/` | Subagent system prompts | `[agent-name]-agent.md` |
| `Funnels/` | Documented product funnels (loaded on demand, not always-on) | `[funnel-name].md` + `_index.md` |

---

## Global Rules
- State which `Schema/` and `Segments/` files were used
- Partition pruning and explicit column selection on every query
- Never expose raw epoch timestamps without converting
- Cite caveats from `Context/` when relevant (especially revenue/metric aging)
- **Recurring query persistence:** If the same analytical question comes up across 2+ sessions and the SQL is non-trivial, suggest persisting it to `Queries/`. Don't save one-off queries or minor variants. See `Queries/_index.md` for format and criteria.
- **Explicit column selection — never SELECT \*.** Before writing any query against a wide table, identify which columns the output actually requires and list only those. The goal isn't a fixed whitelist — it's intentional thinking about what's needed for this specific query. State the column list in the query plan before writing SQL.
