# Business Context: Revenue Aging

## The Rule
Never report final revenue for any period ending within the aging window of `CURRENT_DATE()`.

## Aging Windows by Vertical
| Vertical | Aging Buffer | Reason |
|---|---|---|
| Credit Cards | 7 days | Faster partner reporting |
| Personal Loans | 30 days | Slower funding cycle |
| All others / unknown | 14 days | Safe default |

**Default:** Use 14 days when the query spans multiple verticals or vertical is unspecified.

**For Darwin experiments:** Use the per-vertical window when the experiment's vertical is known. Add the aging buffer to `rampEndDate` (or `CURRENT_DATE()` if live) when joining to FTRE. See `Context/experiment-analysis.md`.

## SQL Implementation
```sql
-- Default (multi-vertical or unknown)
CAST(clickdate AS DATE) < DATE_SUB(CURRENT_DATE(), INTERVAL 14 DAY)

-- PL-specific
CAST(clickdate AS DATE) < DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)

-- CC-specific
CAST(clickdate AS DATE) < DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY)
```

## Exception
If user explicitly requests un-aged data, omit the filter but add:
```sql
-- WARNING: Revenue aging filter removed per user request.
-- Recent data is incomplete and will change as partners report.
```

## Required Caveat
Always note the aging window used when presenting revenue data.
