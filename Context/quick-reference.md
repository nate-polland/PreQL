# PreQL Quick Reference

One-page cheat sheet. For full docs, see `CLAUDE.md` and `Context/_index.md`.

---

## 5 Rules That Always Apply

| Rule | Detail |
|------|--------|
| **Scope to your population** | Know the geography, product line, or user segment your analysis covers. Apply it consistently across all CTEs. |
| **Partition every query** | Always filter on the partition key before joins. Unpartitioned scans on large event tables will time out or cost a lot. |
| **No `SELECT *`** | Declare the columns you need before writing SQL. Wide tables have 50–200+ columns; pulling all of them is wasteful and slow. |
| **Apply metric aging windows** | Revenue and conversion metrics often have a reporting lag (days to weeks). Always use your team's documented aging window — never query with today as the upper bound. See `Context/revenue-aging.md`. |
| **Aggregation metric ≠ user count** | If your metric uses a fractional or multi-touch attribution model (e.g., `SUM(attributed_weight)`), it will differ from `COUNT(DISTINCT user_id)`. Know which one your dashboard uses. |

---

## Common Join Key Patterns

| You have | Join to | Using |
|----------|---------|-------|
| Event table (authenticated) | Member/user table | Authenticated user ID (e.g., `user_id = member_id`) |
| Event table (anonymous) | Session/cookie table | Browser or cookie ID |
| Attribution/conversion table | Member table | Numeric user ID — verify type (INT vs STRING) matches |
| Notification/message table | Event table | Trace or message ID |
| Pre-auth event | Post-auth event | Cross-auth stitch key — see `Context/cross-table-joins.md` |

**Always verify:** join key null rates before building a full query. A high null rate on a join key means the join will silently drop rows.

---

## Timestamp Patterns

| Situation | Pattern |
|-----------|---------|
| Epoch milliseconds | `TIMESTAMP_MILLIS(ts_column)` → then `DATE(...)` for partition |
| Epoch seconds | `TIMESTAMP_SECONDS(ts_column)` |
| Already a TIMESTAMP | `DATE(ts_column)` directly for partition filtering |
| Already a DATE | Use directly in `WHERE date_col BETWEEN ...` |
| String date | `PARSE_DATE('%Y-%m-%d', date_str)` |

**Never expose raw epoch integers to users** — always convert before surfacing in results.

---

## Which Table for What

This table is a template — replace with your team's actual tables after running `/setup` or `/add-table-schema`.

| Question | Table type | Where to look |
|----------|-----------|---------------|
| Who are our users/members? | Member/identity table | `Schema/[members].md` |
| Daily/monthly active users | Activity fact table | `Schema/[activity].md` |
| Revenue and conversion events | Revenue event table | `Schema/[revenue_events].md` |
| Behavioral events (clicks, screens) | Event log table | `Schema/[events].md` |
| Experiment assignments | Experiment assignment table | `Schema/[experiments].md` |
| Notifications sent/delivered | Notification event table | `Schema/[notifications].md` |
| User demographic/status | User status/profile table | `Schema/[user_status].md` |

---

## Query Debugging Flowchart

```
Query timed out?
  → Add/fix partition filter on the date/time column
  → Scope to 1 day first to validate logic, then expand
  → Use async execution for anything joining large event tables across >1 day

Zero rows returned?
  → Sample one known user first: SELECT * WHERE user_id = [known_id] LIMIT 10
  → Check join key data types (INT vs STRING — cast if needed)
  → Verify partition filter isn't excluding all data

Count doesn't match dashboard?
  → Verify date range matches exactly (dashboards often default to last 30 days)
  → Check dedup/quality flags documented in Schema/ (fake users, test clicks, etc.)
  → Check metric aging window (revenue tables often have a lag)
  → Check any channel or segment filters the dashboard applies by default

Getting duplicate rows?
  → Check the grain of each table you're joining (one row per user? per event? per day?)
  → Add DISTINCT or GROUP BY on the correct key
  → Check if a LEFT JOIN is fanning out (one-to-many join producing extra rows)
```

---

## Available Skills (when to use them)

| You want to... | Skill |
|----------------|-------|
| Map an unfamiliar funnel end-to-end | `/funnel-discovery` |
| Update an existing funnel doc | `/update-funnel` |
| Break down a funnel by user path and drop-off | `/funnel-decomposition` |
| Design an experiment + get sample size | `/experiment-design` |
| Diagnose why a metric moved | `/metric-investigation` |
| Document a new table | `/add-table-schema` |
| Update an existing schema doc | `/update-table-schema` |
| Trace a table's lineage and reliability | `/data-lineage` |
| Push your changes to GitHub | `/contribute` |
| Pull latest PreQL updates | `/sync` |

---

## Schema Confidence at a Glance

- 🟢 **Ready** — validated, use as-is
- 🟡 **Caution** — structure confirmed, operational rules partially verified
- 🔴 **Research required** — mapper only, verify fields before querying
- ⚫ **Tombstone** — retired, do not use

Full draft inventory: `Schema/drafts/_index.md`
Finalized schemas: `Schema/` directory (read directly by table name)
