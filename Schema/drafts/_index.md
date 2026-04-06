# Schema Drafts Index

Tables in `Schema/drafts/` are mapper-generated or partially investigated. Structural metadata is ~80% reliable; operational rules (filters, joins, business logic) are surfaced as candidates and have NOT been fully validated. **Nothing here is gospel — use with caution and document any corrections.**

Graduated tables (validated, moved to `Schema/`) are not listed here.

---

## Confidence Key

| Signal | Meaning |
|--------|---------|
| 🟢 **Ready** | Structure + operational rules validated by live query. Safe defaults documented. Use as-is. |
| 🟡 **Caution** | Structure confirmed; operational rules partially validated or unverified. Use with caveats noted in the doc. |
| 🔴 **Research required** | Structure inferred from mapper only; no live validation. Verify fields before building a query. |
| ⚫ **Tombstone** | Table retired or superseded. Do not use. |

---

## Graduated (moved to Schema/)

| Table | Schema File | Notes |
|-------|-------------|-------|
| *(add graduated tables here as you validate them)* | | |

---

## Drafts by Domain

Add your team's draft tables here as you discover and document them. Organize by domain.

### [Domain 1 — e.g., Identity / Members]

| File | Table | Ready? | Status | Key Confidence |
|------|-------|--------|--------|----------------|
| | | | mapper | |

### [Domain 2 — e.g., Events / Engagement]

| File | Table | Ready? | Status | Key Confidence |
|------|-------|--------|--------|----------------|
| | | | mapper | |

### [Domain 3 — e.g., Revenue / Conversion]

| File | Table | Ready? | Status | Key Confidence |
|------|-------|--------|--------|----------------|
| | | | mapper | |

---

*Use `/add-table-schema` to document a new table. Use `/table-mapper` to batch-document a queue of tables. Update status and confidence notes here after each investigation.*
