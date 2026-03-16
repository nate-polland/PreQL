# PreQL

A conversational BigQuery SQL agent for CreditKarma analysts and PMs. Ask a question in plain English, get back validated SQL with a plain-English summary.

**Runs inside Claude Code. BigQuery access is READ ONLY.**

---

## How to Use

Open this folder in Claude Code and ask your question:

> "How many new users registered last month, broken down by platform?"

> "What was the ChatGPT registration funnel conversion rate last 30 days?"

> "Did experiment 71788 significantly improve registration completion rate?"

Claude walks through a pipeline: interpret → generate SQL → validate → present results.

---

## Setup (First Time)

### 1. Install Claude Code
```bash
npm install -g @anthropic-ai/claude-code
```

### 2. Connect BigQuery
```bash
claude mcp add bigquery --scope user --transport stdio -- uvx mcp-server-bigquery --project prod-ck-abl-data-53 --location US
```

### 3. Authenticate with Google
```bash
gcloud auth login
```
> If `gcloud` is not found: `brew install --cask google-cloud-sdk`

### 4. Open this folder in Claude Code
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
├── Agents/
│   ├── product-analyst-agent.md       # SQL generation
│   └── bi-validation-agent.md         # SQL validation
├── Schema/
│   ├── 00-global-sql-standards.md     # BigQuery cost/safety rules (always applied)
│   ├── be.md                          # BigEvent
│   ├── darwin.md                      # Experimentation (Darwin)
│   ├── ftre.md                        # Revenue
│   ├── ftee.md                        # Engagement events
│   ├── srrf.md                        # Registration
│   ├── matchedmembers.md              # Member matching
│   ├── fdma.md                        # Daily active members
│   ├── userstatus.md                  # User status
│   └── consent.md                     # Consent
├── Context/
│   ├── business-context.md            # Company/product background
│   ├── cross-table-joins.md           # Validated join patterns
│   ├── experiment-analysis.md         # A/B test methodology
│   ├── funnel-measurement-patterns.md # Reusable funnel query patterns
│   ├── revenue-aging.md               # 14-day revenue aging rule
│   ├── sampling-methodology.md        # How to explore unfamiliar tables
│   └── advanced-experiment-topics.md  # Reference: power analysis, SRM, guardrails
├── Funnels/
│   ├── _index.md                      # Index of documented funnels
│   └── chatgpt-auth.md                # ChatGPT → CK registration funnel
└── Segments/
    ├── _template.md                   # Copy this to create a new segment
    ├── churned-users.md
    └── dormant-users.md
```

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add schemas, funnels, segments, and propose changes to core files.
