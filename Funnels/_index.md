# Funnels Index

| Funnel | File | Status | Last Validated |
|---|---|---|---|
| ChatGPT Auth | `chatgpt-auth.md` | active | 2026-03-18 |
| LBE / Intuit Auth | `lbe-intuit.md` | active | 2026-03-18 |
| LBE / Intuit Auth — Sep 2025 | `lbe-intuit-2025.md` | active | 2026-03-17 |
| LBE / CK-Internal-Origin — Sep 2025 | `lbe-ck-origin-2025.md` | active | 2026-03-18 |

---

## Cross-Funnel Cohort Summary

Query-confirmed numbers. % of users = cohort population (classified + allocated drops) / anchor. Completion rate = direct-queried completers / cohort population.

| Funnel | Anchor (n) | Cohort | % of users | Completion rate |
|---|---|---|---|---|
| ChatGPT Auth (Jan–Mar '26) | OTP Submit (10,429) | 🔵 Phone match | 66.4% | 83.7% |
| | | 🟠 PII/cred match | 28.0% | 54.1% |
| | | 🟢 New user | 5.9% | 18.4% |
| LBE Intuit Mar '26 (Mar 1–3) | Entry (3,912) | 🔵 Phone match | 0.6% | 12.0% |
| | | 🟠 PII/cred match | 42.9% | 10.9% |
| | | 🟢 New user | 56.5% | 11.5% |
| LBE CK-Origin Sep '25 (Sep 1–3) | Entry (2,278) | 🟠 PII/cred match | 88.4% | 6.3% |
| | | 🟢 New user | 11.6% | 18.9% |

**Key reads:**
- ChatGPT is the only funnel where cohort strongly predicts completion rate — the phone-match shortcut (66% of users) drives the 72% overall CVR
- LBE Intuit completes nearly uniformly across cohorts (~11%) — drop-off is pre-classification; only 12.8% of the new-user cohort ever reaches TOS
- CK-Origin new users (11.6% of funnel) convert 3× better than existing users (18.9% vs 6.3%) — high intent once through the login gauntlet; Cat2 problem is login friction, not post-auth
