# Query Library

Validated, runnable BigQuery queries with real table names and filters. Unlike `Context/funnel-measurement-patterns.md` (generic templates), these are production-ready with values plugged in — adjust the date window and run.

## When to add a query here

**Do:** Add a query when the same question has come up across 2+ sessions and the SQL is non-trivial to reconstruct. Queries here should save meaningful re-discovery time.

**Don't:** Add one-off queries, minor variants of existing queries, or anything that's straightforwardly derived from the patterns in `Context/funnel-measurement-patterns.md`.

When a funnel is considered complete (structure validated, counts populated, flowchart finalized), finalize its canonical entry and measurement queries here.

---

## Index

| Query | File | Funnel | Pattern Used | Status |
|---|---|---|---|---|
| LBE entry cohort — all variants | [lbe-entry-cohort.md](lbe-entry-cohort.md) | LBE (Intuit + CK-origin) | Entry filter | ✅ Validated |
| BigEvent screen inventory | [screen-inventory.md](screen-inventory.md) | Any BigEvent funnel | Phase 2b broad scan | ✅ Validated |
| Cross-funnel cohort classification | [cohort-classification.md](cohort-classification.md) | LBE Sep 2025 (both variants) | Pattern 7 | ✅ Validated |
