---
status: finalized
last_validated: 2026-03-15
---

# Schema: Seamless Registration Raw Funnel (SRRF)

**Table:** `prod-ck-abl-data-53.dw.seamless_registration_raw_funnel`
**Alias:** `SRRF`
**Grain:** One row per user × event_date × affiliate channel
**Purpose:** Tracks backend events across the seamless registration flow — both pre-auth (anonymous) and post-auth (matched) steps. Use for registration funnel analysis and identity verification diagnostics.
**Partition Key:** `event_date` (DATE) — always filter this first

## Critical: NULL numericid rows
~90% of rows have `numericid IS NULL` — these are pre-auth/anonymous sessions where registration was started but the user was not yet matched. Filter `numericid IS NOT NULL` to limit to matched/registered users.

## Key Identifiers
- `affiliateAssociationId` (STRING) — identifies the partner/acquisition channel; use to segment by affiliate (e.g. filter `LIKE '%openai%'` for ChatGPT-referred users)
- `referrer` (STRING) — referring source
- `event_date` (DATE) — date of registration event; always filter first
- `cookieId` (STRING) — cookie identifier; present for pre-auth rows where numericid is null
- `affiliateName` (STRING) — human-readable affiliate name (e.g. `'Intuit'`)
- `numericid` (INT64, nullable) — join key to matchedMembers and other tables; NULL = pre-auth session. **Validated join: `completed_toa = 1` users match to `matchedMembers.validationTs` at 94% (29/31 OpenAI users, Feb–Mar 2026)**

## Registration Flow Flags (INT64, 0/1 unless noted)
- `sr_nmm` (INT64) — seamless registration new matched member; `1` = user was newly matched during this flow
- `viewed_sr_entrypoint` (INT64)
- `saw_login` (INT64)
- `started_login` (INT64)
- `saw_loginClick` (INT64)
- `clicked_loginClick` (INT64)
- `login_send_SMS_code` (INT64)
- `started_sr` (INT64) — user began seamless registration
- `load_personal_info_page` (INT64)
- `saw_personal_info` (INT64)
- `submitted_personal_info` (INT64) — PII submitted
- `personal_info_otc_error` (INT64)
- `otc_successful` (INT64) — one-time code (OTP) verified successfully
- `submitted_phone_verification` (INT64)
- `phone_verification_error` (INT64)
- `prove_verification_pending` (INT64) — DOB + phone sent to Prove vendor for identity verification (triggered when user fails phone/email match)
- `match_fail` (INT64) — user failed phone/email match; triggers Prove flow
- `match_fail_clicked` (INT64) — user acknowledged match failure and continued
- `prove_fail` (INT64) — Prove identity check failed (no profile returned). ⚠️ **Unreliable:** 0 observed in ChatGPT funnel 3-day sample (2026-03-10 to 2026-03-12) despite known Prove failures. Use alternative signals (`shortPersonalInfoSubmitError` + `pageLevelError` in BE, or `match_fail` in SRRF) instead.
- `phone_verification_success` (INT64)
- `completed_toa` (INT64) — Terms of Agreement accepted at end of new account creation flow (post-Prove, pre-account creation); distinct from ChatGPT product consent screen
- `see_financial_info` (INT64)
- `complete_financial_info` (INT64)
- `viewed_confirm_pi` (INT64)
- `saw_info_not_correct` (INT64)
- `clicked_info_not_correct` (INT64)
- `clicked_confirm_info` (INT64)

## Credit Context
- `scoreBand` (STRING) — credit score band at time of registration

## Page Errors (INT64, 0/1)
- `pageError_anonymous` (INT64)
- `pageError_dup_phone` (INT64)
- `pageError_invalid_phone` (INT64)
- `pageError_not_support_phone` (INT64)
- `pageError_unknown_record` (INT64)

## OTC Errors (INT64, 0/1)
- `otcError_other` (INT64)
- `otcError_no_phone` (INT64)
- `otcError_phone_invalid` (INT64)
- `otcError_challenge_limit` (INT64)
- `otcError_duplicate_phone` (INT64)
- `otcError_unsupported_phone` (INT64)
- `otcError_call_failed` (INT64)
- `otcError_blocked_by_request` (INT64)
- `otcError_blocked_by_vendor` (INT64)
- `otcError_block_deactivated_number` (INT64)
- `otcError_block_high_risk_score` (INT64)
- `otcError_fraud_check_failed` (INT64)

## PII Errors (INT64, 0/1)
- `piiError_other` (INT64)
- `piiError_duplicate_user` (INT64)
- `piiError_piiproviderdata_failed` (INT64)
- `piiError_otc_code_invalid` (INT64)
- `piiError_otc_code_limit` (INT64)
- `piiError_otc_code_expired` (INT64)
- `piiError_fraud_failed` (INT64)
- `piiError_create_member_failed` (INT64)

## Identity Verification (Prove Vendor)
- `total_prove_call` (INT64) — total calls made to Prove vendor; **use this as the reliable indicator of Prove being invoked** (validated: `prove_verification_pending` does not fire reliably for OpenAI users)
- `success_prove_call` (INT64) — successful Prove calls
- `prove_verification_pending` (INT64) — ⚠️ unreliable: observed zero for OpenAI users even when `total_prove_call > 0`; logging gap suspected

## Registration Outcome
- `signup_dup_phone` (INT64)
- `signup_dup_ssn` (INT64)
- `toaError` (INT64)
- `regLog_account_created` (INT64) — ⚠️ INVERTED FLAG: `1` = account creation **failed**, `0` = account creation **succeeded**. Validated: `account_created=0` + `completed_toa=1` matches matchedMembers at 92% across affiliates; `account_created=1` matches at <1%. Use `completed_toa = 1` AND `regLog_account_created = 0` as the new-user completion condition.
- `regLog_ssn_lookup_success` (INT64)
- `regLog_report_pull_creditfreeze` (INT64)
- `clicked_login_click_dup_ssn` (INT64)
- `clicked_login_click_dup_phone` (INT64)
- `clicked_login_click_other` (INT64)
- `saw_marketplace_login` (INT64)

## Marketplace Activity (Post-Registration)
- `applications` (INT64)
- `approvals` (INT64)
- `conversions` (INT64)
- `revenue` (FLOAT64)
- `nmm_applications` (INT64)
- `nmm_approvals` (INT64)
- `nmm_conversions` (INT64)
- `nmm_revenue` (FLOAT64)

## Offer Engagement
- `saw_lbe_offer` (INT64)
- `clicked_lbe_offer` (INT64)
- `saw_nmm_plm_offer` (INT64)
- `clicked_nmm_plm_offer` (INT64)
- `lbe_offer_imps` (INT64)
- `lbe_offer_clicks` (INT64)
- `nmm_plm_offer_imps` (INT64)
- `nmm_plm_offer_clicks` (INT64)
