# Cross-Table Join Keys

Document validated join keys between your team's tables here. Each entry should include:

- **Join fields** (both sides) with their data types
- **Null rates** on each side — a high-null join key is a red flag
- **Recommendation** — which join key to use and why
- **Validation date and method** — when was this validated and on what data window?

---

## Template

### [Table A] → [Table B]

| Join Field | Table A Side | Table B Side | Null Rate (A) | Null Rate (B) | Recommendation |
|---|---|---|---|---|---|
| [field name] | `[column_a]` | `[column_b]` | ~X% | X% | USE THIS / Avoid — reason |

**Recommended join:**
```sql
JOIN [table_b]
  ON a.[column_a] = b.[column_b]
```

> **Note:** [Any cardinality notes — 1:1, 1:many, etc. and implications]

**Validated:** [date], [method]

---

## Country / Geography Filters

Document the correct geography filter for each table here. Do not assume — geography column naming and null behavior varies by table.

| Table | Geography Field | Filter Syntax | Notes |
|---|---|---|---|
| [table name] | `[field]` | `[filter expression]` | [e.g., "NULL values represent US users"] |

---

## Caveats

- **Join completeness:** Document any known gaps in join coverage here.
- **Partner/source ID mapping:** If tables use internal slugs that differ from display names, document the mapping here.
