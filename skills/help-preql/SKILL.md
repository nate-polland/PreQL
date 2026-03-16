---
name: help-preql
description: |
  Overview of what PreQL can do, how to use it, and available commands. A reference that any user can invoke at any time.

  Trigger phrases: "/help-preql", "how do I use this", "what can you do", "what does PreQL do", "show me the commands", "what are my options"
---

# PreQL — How to Use This Tool

Display the following as a clean, readable overview. Keep it conversational — this is a reference, not a manual.

---

## What PreQL Is

PreQL translates plain-English questions into validated BigQuery SQL. You ask a question, it figures out the right tables and logic, generates the SQL, validates it, and returns a plain-English summary alongside the query.

**BigQuery access is read-only.** PreQL cannot write, modify, or delete data.

---

## How to Ask Questions

Just type your question. Examples:

- *"How many new members registered last month, broken down by platform?"*
- *"What was the ChatGPT registration funnel conversion rate over the last 30 days?"*
- *"Did experiment 71788 significantly improve registration completion rate?"*
- *"How many dormant users reactivated in Q1?"*

**Tips:**
- Be specific about time windows — "last 30 days", "Q1 2025"
- Name the metric you care about — "conversion rate", "revenue", "registrations"
- You don't need to know which table — PreQL figures that out
- Ask follow-ups freely — you can refine any answer in the same session

---

## Built-in Commands

| Command | What it does |
|---|---|
| `/funnel-discovery` | Maps a product funnel interactively and saves a reusable doc |
| `/add-table-schema` | Documents a new BigQuery table so the team can query it |
| `/onboard` | Setup check + guided orientation for new users |
| `/help-preql` | This overview |

---

## What PreQL Knows

PreQL has pre-loaded knowledge of your team's key tables, join patterns, and business logic:

- **Tables:** BigEvent, FTRE (revenue), FTEE (engagement), SRRF (registration), Darwin (experiments), MatchedMembers, and more
- **Business rules:** Revenue aging buffer, US-only defaults, partition safety
- **Funnel docs:** Documented product funnels (e.g., ChatGPT → CK registration)
- **Segment definitions:** Dormant users, churned users, and others

---

## What to Expect in Responses

Every answer follows the same structure:
1. **Plain-English summary** — what the query measures and what it found
2. **Caveats** — any approximations, exclusions, or limitations to know about
3. **SQL** — clean, copy-pasteable query at the bottom

---

## Contributing

If you document a new table or funnel, it can be shared with the whole team via a GitHub PR. See `CONTRIBUTING.md` in the repo for details.
