# Term Disambiguation

Terms that mean different things depending on context. When a query uses one of these terms, resolve the ambiguity before writing SQL.

---

## "Conversion rate" / CVR

| Usage | Meaning | Correct denominator |
|---|---|---|
| **Overall funnel CVR** | entry → completion | all entrants |
| **Step-level CVR** | step N → step N+1 | users who reached step N |
| **Per-cohort CVR** | completions in cohort / cohort population | cohort total (classified + allocated drops) |
| **Post-auth CVR** | completion after authentication step | users who completed auth |

**Default:** if the user says "conversion rate" without qualification, confirm which of these they mean. The funnel doc usually specifies which denominator is canonical.

---

## "New user" / "new member"

| Usage | Meaning | Signal |
|---|---|---|
| **Product context** | Never had a CK account before | `termsContinue` event; new row in SRRF with `numericid IS NULL` before → `IS NOT NULL` after |
| **Funnel context** | First time through *this funnel* | No prior entry event for this cookieId in a lookback window |
| **Registration context** | Registered (account created) in the date range | SRRF row with `registration_date` in range |
| **Reactivated user** | Had account, was dormant, returned | See `Segments/dormant-users.md` |

**Default:** assume product-context "new user" = net-new CK account. Confirm if the question is about funnel-first-timers or account-age-based cohorts.

---

## "Entry" / "entered funnel"

| Usage | Meaning |
|---|---|
| **Screen impression** | User saw the landing/entry screen (`system_eventType IN (1, 4)`) |
| **First action** | User took an action on the entry screen (`system_eventType IN (2, 3)`) |
| **Session start** | First event for this stitch key in the date range |

**Default:** use the impression (screen load) as entry unless the funnel doc specifies otherwise. Action-based entry undercounts users who bounced before interacting.

---

## "Session"

| Usage | Meaning |
|---|---|
| **traceId** | Single page load; resets on navigation (very granular — not a full session) |
| **cookieId** | Cross-page browser session; persists across traceId resets; resets if user clears cookies |
| **Authenticated session** | numericId-scoped; persists across devices for logged-in users |

**For cross-auth funnels:** use `cookieId` as the session stitch key (spans pre- and post-auth). Always validate 1:1 cardinality before using as a session identifier — see `Context/cross-table-joins.md`.

---

## "User"

| Context | Identifier |
|---|---|
| Pre-auth / anonymous | `user_cookieId` (BigEvent) |
| Post-auth / registered | `user_dwNumericId` (BigEvent) = `numericid` (SRRF) = `numericId` (Darwin, FTEE, FTRE) |
| Device-level | `user_deviceId` (BigEvent) |

**Never aggregate on `cookieId` and `numericId` interchangeably** — a single user can have multiple cookieIds (device switches, cleared cookies) and a single cookieId can briefly cover multiple numericIds (shared device). For authenticated-user counts, use `numericId`.

---

## "Completion"

| Funnel | Completion definition |
|---|---|
| ChatGPT auth | Consent screen action (`toaContinue` or equivalent) |
| LBE funnels | PLM (post-login marketplace) impression — first product screen after auth |
| Registration | SRRF `completed_toa = 1` or `registration_date IS NOT NULL` |

**Always confirm in the funnel doc** — "completion" is funnel-specific and cannot be assumed.

---

## "Dormant" / "Churned"

| Term | Definition |
|---|---|
| **Dormant** | No login activity for 3–12 months |
| **Churned** | No login activity for 12+ months |

See `Segments/dormant-users.md` for the SQL filter.

---

## "Approval Odds" model types

| `flex_intField33` value | Label |
|---|---|
| `1` | ITA (CK's model) |
| `>1` | Lightbox (partner's model) |
| `NULL` + pre-qualified label | PQ (firm offer) |

See `Context/business-context.md`.
