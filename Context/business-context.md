# Business Context: Query-Relevant Facts

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
