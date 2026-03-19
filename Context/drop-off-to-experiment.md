# Drop-off to Experiment Hypothesis

A structured path from "we found a drop-off" to "here's an experiment we can run." Use after running Pattern 3 or Pattern 8 from `funnel-measurement-patterns.md` to turn drop-off data into an actionable test.

---

## Step 1 — Diagnose the Drop

Before forming a hypothesis, distinguish between drop types (see Pattern 3):

| Drop type | What it signals | Implication |
|---|---|---|
| **Organic dropout** — last event was an impression (user saw the screen and left) | User chose not to proceed | UX friction, trust, or motivation problem |
| **Disappearance** — last event was an action (user submitted/clicked but next screen never fired) | Technical failure or latency | Engineering fix, not an experiment |
| **Large residual in cohort query** | A path you haven't classified | Map the path first; don't form a hypothesis until you know who these users are |

**Don't run an experiment on a disappearance.** Fix the bug or latency first. Experiments can't fix things users can't see.

---

## Step 2 — Size the Opportunity

Before writing a hypothesis, confirm the drop is worth testing:

```
opportunity = cohort_population × drop_rate × uplift_assumption
```

- `cohort_population` — how many users hit this step per week?
- `drop_rate` — what fraction drop at this specific step within this cohort?
- `uplift_assumption` — what's a plausible improvement? (5pp is optimistic for a UX change; 1–2pp is realistic)

If `opportunity < ~50 incremental completions/week`, the experiment will take a very long time to reach significance. Flag this before proceeding.

---

## Step 3 — Form the Hypothesis

Use this template:

> **Who:** Users in [cohort], at [step], in the [funnel name] funnel.
>
> **What we observe:** [X%] of this cohort drops at [step]. Last event type: [organic dropout / disappearance].
>
> **Root cause hypothesis:** [Why do we think they're dropping? e.g., "The screen asks for too many fields before showing value." / "The error message is ambiguous and users give up."]
>
> **Proposed change:** [What are we testing? e.g., "Reduce the form to 2 required fields and defer optional fields."]
>
> **Predicted effect:** Increase completion rate from [baseline%] to [target%] for this cohort (~[Xpp] lift).
>
> **Primary metric:** [e.g., funnel completion rate, step-to-step rate at the drop point]
>
> **Guardrail metrics:** [e.g., downstream revenue per completer, overall funnel CVR — make sure we're not trading completions for lower-quality users]
>
> **Experiment population:** [How users are allocated — pre-auth: cookieId; post-auth: numericId. Note if the population is a subset of funnel traffic, e.g., LBE Intuit users only]

---

## Step 4 — Identify the Experiment Setup

Key decisions before handing off to engineering:

- **Pre-auth funnel** (user not yet logged in): can your experiment platform bin on cookie/device ID? Note this means re-entry by the same user may land in a different arm. Flag this as a limitation.
- **Post-auth funnel**: bin on authenticated user ID. Cleaner allocation; user is sticky to their arm across sessions.

Check what identifier types your experiment platform supports for bucketing before assuming pre-auth identifiers are available for the join.

**Minimum detectable effect (MDE) estimate:**
```python
from scipy.stats import norm
import numpy as np

baseline = 0.XX   # current completion rate
mde      = 0.XX   # minimum lift worth detecting (absolute, e.g., 0.03 for 3pp)
alpha    = 0.05
power    = 0.80

z_alpha = norm.ppf(1 - alpha / 2)
z_beta  = norm.ppf(power)
p_bar   = (baseline + baseline + mde) / 2

n_per_arm = (z_alpha + z_beta)**2 * 2 * p_bar * (1 - p_bar) / mde**2
print(f"Required: {n_per_arm:.0f} users per arm")
```

Funnel volume is often the binding constraint — verify weekly cohort size before committing to a test duration.

---

## Step 5 — Pre-register the Analysis

Before shipping, document:
1. The primary metric and threshold (e.g., p < 0.05 two-tailed)
2. Whether you're testing one-tailed or two-tailed — and why
3. Any planned subgroup analyses (these inflate Type I error; apply Bonferroni if multiple)
4. The planned run duration (don't peek and stop early)

See `Context/experiment-analysis.md` and `Context/funnel-experiments.md` for the full experiment join and significance-testing patterns.
