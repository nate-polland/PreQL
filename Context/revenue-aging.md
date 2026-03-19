# Business Context: Revenue / Metric Aging

## The Rule
Never report final revenue (or other lagging metrics) for any period ending within the aging window of `CURRENT_DATE()`. Recent data is incomplete and will change as partners or systems report.

## Aging Windows

Aging windows vary by revenue type, product vertical, and partner reporting cycles. Document your team's aging windows here:

| Metric / Vertical | Aging Buffer | Reason |
|---|---|---|
| [e.g., Credit Cards] | [e.g., 7 days] | [e.g., Faster partner reporting] |
| [e.g., Personal Loans] | [e.g., 30 days] | [e.g., Slower funding cycle] |
| Default (unknown vertical) | [e.g., 14 days] | Safe default when vertical is unspecified |

**Default:** Use your team's documented default aging window when the query spans multiple verticals or vertical is unspecified.

**For experiments:** Apply the per-vertical aging window when the experiment's vertical is known. Add the aging buffer to the experiment end date when joining to revenue.

## SQL Implementation
```sql
-- Default aging filter (adjust interval to your team's documented default)
CAST([date_field] AS DATE) < DATE_SUB(CURRENT_DATE(), INTERVAL [N] DAY)
```

## Exception
If user explicitly requests un-aged data, omit the filter but add:
```sql
-- WARNING: Revenue aging filter removed per user request.
-- Recent data is incomplete and will change as partners report.
```

## Required Caveat
Always note the aging window used when presenting revenue data.
