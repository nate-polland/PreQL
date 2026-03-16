# Segment: [Segment Name]

**Author:** [Your Name]
**Created:** [YYYY-MM-DD]
**Last Validated:** [YYYY-MM-DD]

## Plain English Definition
[Describe who is in this segment in plain English. No SQL. Write it as you'd explain it to a non-technical stakeholder.]

Example: "Users who registered on the platform and have never had a credit file (thin file at registration)."

## Primary Table
[Which table identifies this population? Usually `userstatus_ext` for demographic segments, `fact_member_active_daily` for behavioral segments, or `fact_tracking_revenue_ext` for revenue segments.]

## SQL Filter
[The exact WHERE clause or subquery needed to identify this segment. This will be inserted into queries by the Product Analyst Agent.]

```sql
-- Example:
numericId IN (
  SELECT DISTINCT numericId
  FROM `prod-ck-abl-data-53.dw.userstatus_ext`
  WHERE isDuplicate = 0
    AND isFakeuser = 0
    AND [your_condition_here]
)
```

## Important Caveats
- [Any date sensitivity? E.g., "This flag changes daily — always use the most recent snapshot"]
- [Any known data quality issues?]
- [Any columns that seem related but should NOT be used?]

## Example Use Cases
- [Sample question this segment was built to answer]
- [Another example question]
