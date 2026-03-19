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

| Usage | Meaning |
|---|---|
| **Product context** | Never had an account before — net-new signup |
| **Funnel context** | First time through *this funnel* (regardless of account age) |
| **Registration context** | Registered (account created) in the date range |
| **Reactivated user** | Had account, was dormant, returned |

**Default:** confirm with the user which definition applies. "New user" is ambiguous without context.

---

## "Entry" / "entered funnel"

| Usage | Meaning |
|---|---|
| **Screen impression** | User saw the landing/entry screen |
| **First action** | User took an action on the entry screen |
| **Session start** | First event for this stitch key in the date range |

**Default:** use the impression (screen load) as entry unless the funnel doc specifies otherwise. Action-based entry undercounts users who bounced before interacting.

---

## "Session"

| Usage | Meaning |
|---|---|
| **Page-load ID** | Single page load; resets on navigation (very granular — not a full session) |
| **Browser/cookie ID** | Cross-page session; persists across page reloads; resets if user clears cookies |
| **Authenticated session** | User ID-scoped; persists across devices for logged-in users |

**For cross-auth funnels:** use a persistent cross-page identifier as the session stitch key (spans pre- and post-auth). Always validate 1:1 cardinality before using as a session identifier — see `Context/cross-table-joins.md`.

---

## "User"

The right identifier depends on the auth state. Common identifiers:

| Context | Identifier type |
|---|---|
| Pre-auth / anonymous | Browser/cookie ID or device ID |
| Post-auth / registered | Authenticated user ID (numeric or UUID) |

**Never aggregate on cookie IDs and user IDs interchangeably** — a single user can have multiple cookie IDs (device switches, cleared cookies) and a single cookie ID can briefly cover multiple users (shared device). For authenticated-user counts, use the authenticated user ID.

---

## "Completion"

Completion is funnel-specific and cannot be assumed. Always confirm in the funnel doc — see `Funnels/` for each funnel's completion anchor.

---

## "Dormant" / "Churned"

Generic definitions — adapt thresholds to your team's context:

| Term | Generic Definition |
|---|---|
| **Dormant** | No activity for [X] months (e.g., 3–12 months) |
| **Churned** | No activity for [Y] months (e.g., 12+ months) |

See `Segments/` for your team's specific SQL filters.

---

Add additional term definitions here as your team discovers ambiguities in recurring analyses.
