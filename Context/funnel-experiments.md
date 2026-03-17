# Funnel Experiments

How to overlay a Darwin experiment on a documented funnel. The funnel doc always represents the **control** path. Experiments are documented as a delta.

---

## When to Document

Add an experiment overlay to a funnel doc when:
- An experiment modifies any funnel step (entry, screens, completion)
- The test arm has a different entry point, screen flow, or completion criteria
- You need to compare per-arm conversion rates through the funnel

## Where to Document

In the `## Experiments` section of the existing funnel doc — not as a new funnel.

```markdown
### Experiment [ID] — [brief description]
- **Date range:** [rampStartDate] to [rampEndDate or "ongoing"]
- **Arms:** control ([N] users), [arm name] ([N] users)
- **What changed:**
  - [Screen X] replaced by [Screen Y] in test arm
  - [New screen Z inserted between A and B]
- **Darwin join:** `mt_final_{ID}` on `numericId`, filter `first_bin_flag = true AND reseed_flag = 0`
```

Only document the delta — what is structurally different in the test arm vs. control.

## Query Pattern: Per-Arm Funnel Comparison

1. **Get experiment population** — join Darwin to funnel population by `numericId` within the experiment date window. Filter `first_bin_flag = true AND reseed_flag = 0`.
2. **Split by arm** — `groupName` distinguishes control vs test.
3. **Run funnel per arm** — control uses the standard funnel query. Test arms with structural changes need a modified query matching the test arm path.
4. **Compare step-by-step** — for each step, report `users_reached`, `conversion_rate` per arm.

See `Context/funnel-measurement-patterns.md` Pattern 4 (Multi-Path) and Pattern 6 (Statistical Significance) for the SQL templates.

## Key Constraints

- **Darwin join is post-auth only** — `numericId` is the join key, meaning only authenticated users are in the experiment population. For funnels starting unauthenticated, this creates survivorship bias in the denominator. Document this caveat when reporting.
- **Darwin `cookieId`/`deviceId` are NULL for USER-type experiments** (validated). Cannot stitch pre-auth funnel events to experiment arms without `numericId`.
- **Never mix control and test arm users** in a single funnel query.
- **Test arm entry points** — if the test arm uses a different entry filter, the control funnel query cannot be reused. Document the test arm entry filter and run separately.
- **Post-filters** — check `inPostFilter` if configured. Ask experiment owner before including.

## What NOT to Do

- Do not create a new funnel doc for a test arm — document the delta in the existing funnel
- Do not overwrite the control funnel definition
- Do not assume pre-auth identifiers are available in Darwin — check `testType` first
