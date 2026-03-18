# Business Context: Query-Relevant Facts

## Product Strategy

### "Meet members where they are"
CK's core distribution thesis: surface the right financial product at the moment a member is making a financial decision, not later when they think to open the CK app. Key surfaces:
- **Point-of-sale / external surfaces** (e.g., LBE funnels): embedded registration/auth flows on partner sites or third-party apps where the member is already transacting
- **ChatGPT / agentic surfaces**: CK as a participant in agentic workflows where members are increasingly starting; not just for offers but for all atomic product parts

### LBE (Lending Business Engine) funnels
Partner-originated or externally-originated entry points where members register/authenticate into CK from a non-CK surface. Goal is to intercept high-intent moments (e.g., a member shopping for a loan who could benefit from CK's marketplace). Intuit and CK-Internal-Origin are documented variants.

### ChatGPT funnel
Members enter via ChatGPT and authenticate into CK. Tracking architecture: user navigates to CK's domain (standard CK registration/auth funnel), then gets an iframe embedded back in ChatGPT. From a member's perspective it's seamless; from tracking it appears as: ChatGPT → CK domain → CK iframe on ChatGPT. All funnel steps fire on CK's tracking infrastructure.

## User Segments

### Money Mindsets — Primary Segmentation Framework
CK's 5-segment model (Aug 2025, 136.6M CK database). Segments are fully mapped to the CK member database.

| Segment | Share of CK base | Avg credit score | Core financial situation |
|---|---|---|---|
| **Planners** | 39% | 758 | Affluent, family-focused, long-term maximizers; high financial security |
| **Strivers** | 20% | 633 | Young, income-constrained, building foundations; most dormant/churned users |
| **Balancers** | 15% | 620 | Debt-burdened, stretched; aspirational but reactive |
| **Simplifiers** | 11% | 690 | Pragmatic, disengaged, younger; seek automation over management |
| **Protectors** | 15% | 765 | Debt-averse, risk-conscious, older; retirement-focused; 51% churned |

**Re-engagement focus:** Strivers have the largest inactive population (~21.85M churned); Protectors have the highest churn rate (51%). Planners are the largest active segment (9.54M MAU).

**Open question:** Is there a segment field in any table we have access to (e.g., `userStatus`, FDMA, or a separate members table)? The deck says the model is "100% mapped to the CK database" via a typing tool — confirm whether this is accessible for query-time segmentation.

### Dormant / Churned (product analytics definitions)
- **Dormant**: 3–12 months without login activity
- **Churned**: 12+ months without login activity
See `Segments/dormant-users.md` for SQL filter.

## Revenue
- **Use `SUM(amount_USD)` from FTRE** for all revenue calculations
- PL revenue model: CK earns ~3% of funded loan amount. `amountApproved` = loan size, `amount_USD` = CK revenue
- Revenue verticals: Credit Cards, Personal Loans, Auto Refinance, Auto Insurance, Home Refinance, Auto Purchase

## Approval Odds Classification (BigEvent)
Use `flex_intField33` to classify offer type:
- `1` = ITA (CK's own data science model)
- `>1` = Lightbox (partner's underwriting model hosted by CK — higher accuracy)
- `NULL` with pre-qualified label = PQ (firm offer from partner)

## Credit Scores
- CK tracks TransUnion VantageScore 3.0 — this is the `score` field in FDMA, userStatus, Darwin
- FICO scores are different; available in FTRE as `FICOscore` when partner reports it
- These are not interchangeable

## Content Ranking
- Jarvis = recommendation system. `content_recommendationId` in BigEvent
- Position: `content_sectionRank` (section order), `content_contentRank` (within section)
