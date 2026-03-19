# PreQL

A conversational SQL agent for analysts and PMs. Ask a question in plain English, get back validated SQL with a plain-English summary.

**Runs inside Claude Code. Data warehouse access is READ ONLY.**

---

## How to Use

Open this folder in Claude Code and ask your question:

> "How many new users registered last month, broken down by platform?"

> "What was the signup funnel conversion rate over the last 30 days?"

> "Did experiment X significantly improve registration completion rate?"

Claude walks through a pipeline: interpret → generate SQL → validate → present results.

---

## Setup (First Time)

### 1. Install Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Connect your data warehouse
Add your data warehouse as an MCP server. For BigQuery:
```bash
claude mcp add bigquery --scope user --transport stdio -- uvx mcp-server-bigquery --project YOUR_PROJECT_ID --location US
```
Other warehouses (Snowflake, Redshift, etc.) can be connected via their respective MCP servers.

### 3. Authenticate with your warehouse
For BigQuery:
```bash
gcloud auth login && gcloud auth application-default login
```

### 4. Install skills
```bash
bash scripts/install-skills.sh
```

### 5. Configure PreQL for your team
Open the folder in Claude Code and run:
```
/setup
```
This walks through populating the core config files: analytics environment, business context, revenue aging, geography defaults, and key table stubs. **Run this once per team** — individual users run `/onboard` to verify their own connection.

### 6. Open this folder in Claude Code
```bash
cd path/to/PreQL
claude
```

---

## Repository Structure

```
PreQL/
├── CLAUDE.md                          # Orchestration instructions (restricted — see CONTRIBUTING.md)
├── README.md                          # This file
├── CONTRIBUTING.md                    # How to contribute
├── skills/
│   ├── setup/                         # /setup — first-time team configuration
│   ├── onboard/                       # /onboard — individual user setup + orientation
│   ├── help-preql/                    # /help-preql — always-available reference
│   ├── funnel-discovery/              # /funnel-discovery — map a product funnel
│   ├── funnel-decomposition/          # /funnel-decomposition — cohort analysis
│   ├── update-funnel/                 # /update-funnel — update a funnel doc
│   ├── experiment-design/             # /experiment-design — power calc + hypothesis
│   ├── metric-investigation/          # /metric-investigation — diagnose metric movements
│   ├── add-table-schema/              # /add-table-schema — document a new table
│   ├── update-table-schema/           # /update-table-schema — update schema docs
│   ├── data-lineage/                  # /data-lineage — trace table origins
│   ├── contribute/                    # /contribute — push changes to GitHub
│   └── sync/                         # /sync — pull latest updates
├── scripts/
│   └── install-skills.sh             # Symlinks skills/ into ~/.claude/skills/
├── Agents/
│   ├── product-analyst-agent.md       # SQL generation
│   └── bi-validation-agent.md         # SQL validation
├── Schema/
│   └── 00-global-sql-standards.md    # SQL safety and cost rules (always applied)
├── Context/
│   ├── business-context.md            # Company/product context, key metrics, revenue model
│   ├── cross-table-joins.md           # Validated join patterns
│   ├── experiment-analysis.md         # A/B test methodology
│   ├── funnel-measurement-patterns.md # Reusable funnel query patterns
│   ├── revenue-aging.md               # Revenue/metric aging methodology
│   ├── sampling-methodology.md        # How to explore unfamiliar tables
│   ├── term-disambiguation.md         # Terms that mean different things in context
│   ├── drop-off-to-experiment.md      # From drop-off finding to experiment hypothesis
│   ├── funnel-experiments.md          # Experiment overlays on funnels
│   └── advanced-experiment-topics.md  # Reference: power analysis, SRM, guardrails
├── Funnels/
│   └── _index.md                      # Index of documented funnels
├── Queries/
│   └── _index.md                      # Index of saved, validated queries
└── Segments/
    └── _template.md                   # Copy this to create a new segment
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add schemas, funnels, segments, and propose changes to core files.
