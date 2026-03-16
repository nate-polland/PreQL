# DEPRECATED — Moved to `Funnels/chatgpt-auth.md`

# ChatGPT Authentication Funnel

Users arriving at CK content embedded in ChatGPT start unauthenticated. They must complete a registration or login flow to see their personalized data. The completion event is recorded in both BigEvent (`link-chatgpt` click) and the consent table (`usermanagement_opt_in_etl`, product = `ChatGPTConsent`).

## Completion Anchor
- **Consent table:** `service_bus_streaming_etl.usermanagement_opt_in_etl` where `data.consentInfo.product = 'ChatGPTConsent'` and `data.consentInfo.consentAction = 'Consented'`
- **BigEvent:** `content_screen = 'link-chatgpt'`, `system_eventType = 2` (click = "Agree" button)
- Consent timestamp: `TIMESTAMP(data.consentInfo.consentDateTime.value)`

## Session Stitching (Cross-Auth)
Users start unauthenticated — early funnel events have NULL `user_dwNumericId`. Use `user_traceId` to stitch pre-auth and post-auth events:
1. Get numericId + consent_ts from consent table
2. Find `link-chatgpt` event for that numericId → extract `user_traceId`
3. Use `user_traceId` to retrieve all session events (pre-auth + post-auth) in a 2-hour window before consent
- `user_traceId` is ~99% populated on funnel screens and maps 1:1 to numericId
- `glid` is auth-only (~0% for unauthenticated) — do NOT use for this stitch

## User Types

Three distinct user types pass through this funnel:

1. **New users** — no CK account. Must create an account via `seamless-registration` (phone entry → OTP → optionally personal info/DOB). Fully unauthenticated until registration completes.

2. **Returning users with verified phone** — existing CK account with a phone on file. Can be authenticated quickly via `ump-phone-verify` → OTP. Minimal friction path.

3. **Returning users without verified phone** — existing CK account but no verified phone. System attempts to match on email or full PII later in the funnel (`seamless-registration/shortPersonalInfo`). Higher friction; some drop to error states.

## Two User Paths (Validated 2026-03-10, 39-user sample, 61.5% completion)

### New User Path (majority)
`seamless-registration` (phone entry → OTP) → optionally `seamless-registration` (shortPersonalInfo/DOB) → `link-chatgpt` (agreeClick)

### Returning User Path (with 2FA or re-auth required)
`seamless-registration` or `login-web-redirect` → `link-mcp-twofa-enrolled` → `login-web-redirect` → `login-unknown` → `login-unknown-password-disabled-text` → complete or drop

## Known Screen Names (BigEvent `content_screen`)

| Screen | What it is | Path |
|---|---|---|
| `link-chatgpt` | "Allow CK to connect to ChatGPT" — Agree/Cancel | Both |
| `ump-phone-verify` | Phone number entry (screen 1 in mockup) | Existing users |
| `ump-enter-otc` | OTP code entry (screen 2 in mockup) | Existing users |
| `seamless-registration` / `phone-verification` | New user phone entry | New users |
| `seamless-registration` / `personal-info` | Email + DOB identity verify (screen 3) | New users |
| `seamless-registration` / `match-failure` | Identity match failure | Edge case |
| `report-pull-interstitial` | Credit pull loading screen | Existing users |
| `login-options` | Login method selection | Existing users |
| `login-password-options` | Password login | Existing users |
| `login` | Login screen | Existing users |
| `force-2fa-phone-check` / `force-2fa-verify-phone-otc` | Forced 2FA for high-risk login | Edge case |
| `ump-error` | Phone verification error | Edge case |
| `access_unrecog_device` / `change_in_acct_info` | Security screens | Edge case |

## Dropoff Population
~1,095 users hit `link-chatgpt` unauthenticated in last 14 days (no numericId) — these are likely dropoffs at or before consent. Use `user_cookieId` or `user_traceId` to track these.

## Key Funnel Timing (from `link-chatgpt` click backward)
- 0 sec: `link-chatgpt` click (consent)
- ~4–21 sec: OTP entry (`ump-enter-otc`)
- ~3–8 sec: Phone verify (`ump-phone-verify`)
- ~23–65 sec: Registration screens (`seamless-registration`)
- ~29–65 sec: Login screens (existing users)

## Tables
| Table | Role |
|---|---|
| `service_bus_streaming_etl.usermanagement_opt_in_etl` | Completion anchor |
| `kafka_sponge.sponge_BigEvent` | All funnel screen events |
