---
name: experiment-design
description: |
  Pre-flight experiment design workflow. Given a funnel, metric, and current performance baseline, calculates required sample size and estimated duration, generates a hypothesis document, and produces a Darwin setup checklist. Use this before running an experiment, not after.

  Trigger phrases: "design an experiment", "how long does this experiment need to run", "power calculation", "sample size", "experiment setup", "how do I test this", "what experiment should I run", "/experiment-design"
---

# Experiment Design

You are a Senior Product Analyst helping design a rigorous experiment before it ships. The goal is: hypothesis doc + sample size estimate + Darwin setup checklist. Nothing gets shipped without these.

---

## Step 1 — Understand the hypothesis

Ask the user:

1. **What user behavior are you trying to change?** (e.g., "reduce drop-off at the OTP step for new users")
2. **What product change are you testing?** (e.g., "simplify the OTP screen by removing secondary CTAs")
3. **Why do you think this change will work?** (What's the causal mechanism? "Users are distracted by secondary options and abandoning before submitting OTP")

If the user comes in with a drop-off analysis already done (e.g., from `/funnel-decomposition` or Pattern 8 from `funnel-measurement-patterns.md`), use that data — don't re-derive it.

---

## Step 2 — Define the metric

Ask:

1. **Primary metric** — the one number this experiment is designed to move. Must be a directly queryable binary or continuous outcome (e.g., "funnel completion rate", "7-day revenue per user").
2. **Guardrail metrics** — metrics that must not worsen (e.g., "downstream revenue per completer", "overall funnel CVR"). These are not the experiment's goal but define the safety envelope.
3. **Directionality** — one-tailed (you expect the change to improve the metric, never harm it) or two-tailed (genuinely uncertain)? Default: two-tailed unless there's a strong directional prior.

---

## Step 3 — Collect inputs for power calculation

You need four numbers:

1. **Baseline conversion rate** (`p_control`) — current conversion rate for the primary metric, measured on a stable recent period. Use data, not guesswork.
2. **Minimum detectable effect (MDE)** — smallest improvement worth shipping (absolute, e.g., 3pp lift from 15% → 18%). Ask the user: "What's the smallest improvement that would change a product decision?"
3. **Weekly cohort volume** (`weekly_n`) — how many users enter the funnel per week? Use a recent 4-week average, excluding any partial weeks.
4. **Number of arms** — typically 2 (control + test). If >2, adjust accordingly.

---

## Step 4 — Run power calculation

Use Python with scipy. Run this after collecting the inputs:

```python
from scipy.stats import norm
import numpy as np

p_control  = [baseline]    # e.g., 0.15
mde        = [mde]         # e.g., 0.03  (absolute lift, e.g., 3pp)
alpha      = 0.05          # significance threshold (confirm with user; default 0.05)
power      = 0.80          # default; 0.90 if the user wants higher confidence
n_arms     = 2

z_alpha = norm.ppf(1 - alpha / (2 if two_tailed else 1))
z_beta  = norm.ppf(power)

p_test  = p_control + mde
p_bar   = (p_control + p_test) / 2

n_per_arm = (z_alpha + z_beta)**2 * 2 * p_bar * (1 - p_bar) / mde**2

weeks_to_run = n_per_arm / (weekly_n / n_arms)

print(f"Required per arm:  {n_per_arm:,.0f} users")
print(f"Total users needed: {n_per_arm * n_arms:,.0f}")
print(f"Weekly cohort:      {weekly_n:,.0f}")
print(f"Estimated duration: {weeks_to_run:.1f} weeks")
```

**Present clearly:**
- Required n per arm
- Estimated run duration at current volume
- What happens if you increase MDE (smaller threshold = shorter run; confirm it's still business-meaningful)

**Duration flags:**
- < 2 weeks: fast. Double-check MDE isn't too large — are you sure a change that big is plausible?
- 2–8 weeks: typical range. Proceed.
- > 8 weeks: long. Consider whether a larger MDE is acceptable, or whether the metric can be proxied with a faster-moving leading indicator.
- > 16 weeks: impractical. Rethink the metric or the cohort scope.

---

## Step 5 — Generate hypothesis document

Fill in this template:

```markdown
## Experiment Hypothesis

**Funnel:** [funnel name]
**Team / Owner:** [name]
**Target launch date:** [date]

### What we're testing
[Product change in one sentence — e.g., "We are simplifying the OTP screen by removing secondary CTAs and adding a progress indicator."]

### Who we're testing it on
[User population — e.g., "LBE Intuit funnel entrants, mobile only, US."]
[Binner type: pre-auth (cookieId) or post-auth (numericId)]

### Why we expect it to work
[Causal mechanism — e.g., "Users are seeing secondary navigation options on the OTP screen and abandoning before submitting. Removing these reduces cognitive load and keeps users on the critical path."]

### Primary metric
[e.g., Funnel completion rate (entry → PLM)]
Baseline: [X%] | MDE: [Ypp] | Target: [Z%]

### Guardrail metrics
- [e.g., Revenue per completer — must not decline by more than 5%]
- [e.g., 7-day re-engagement rate — must hold flat]

### Statistical setup
- Significance threshold: α = [0.05]
- Test type: [two-tailed / one-tailed with direction]
- Power: [0.80]
- Required n per arm: [N]
- Estimated duration: [W weeks] at current volume ([V users/week])

### Pre-registration notes
- Planned subgroup analyses: [none / list them — each one requires Bonferroni correction]
- Stopping rules: [no early stopping unless a guardrail metric triggers]
```

---

## Step 6 — Darwin setup checklist

Before handing off to engineering:

- [ ] **testType confirmed** — `USER` type for post-auth numericId binner. If pre-auth, confirm `cookieId` / `deviceId` binner is available.
- [ ] **first_bin_flag** — analysis must filter to `first_bin_flag = true` to get clean arm assignment
- [ ] **reseed_flag** — filter `reseed_flag = 0` to exclude re-seeded users
- [ ] **rampStartDate** — confirm date; use as lower bound in FTRE/FTEE joins
- [ ] **rampEndDate** — will be NULL while live. Analysis cutoff = agreed end date or `CURRENT_DATE()`
- [ ] **Binner note for USER-type experiments** — `cookieId` and `deviceId` are NULL in Darwin for USER-type experiments (validated). Join is on `numericId` only. This means the experiment population is inherently post-auth — check that your metric denominator uses a post-auth anchor.
- [ ] **Partition safety** — confirm any BigEvent join in the analysis filters by `DATE(ts)` before joining on identifiers

Refer to `Context/experiment-analysis.md` and `Context/funnel-experiments.md` for the full analysis SQL patterns once the experiment is live.

---

## Key Rules

- **Commit to the primary metric before launch.** Deciding the primary metric after seeing results is p-hacking.
- **Don't peek early.** Stopping an experiment before the planned duration because results "look good" inflates Type I error.
- **Multiple KPIs = Bonferroni.** If you test 3 metrics simultaneously at α=0.05, the effective α for each is ~0.017. Adjust or pick one primary metric.
- **Confirm the metric is actually queryable.** Before finalizing the design, verify the SQL exists (or write it) to measure the primary metric from Darwin-joined data. A metric you can't measure is not a metric.
