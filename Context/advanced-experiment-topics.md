# Advanced Experiment Topics (Reference)

These topics are not part of the standard analysis workflow. Surface them when a user's question specifically calls for it.

---

## Pre-Experiment Power Analysis

Before launching an experiment, you can calculate the minimum sample size needed to detect a given lift.

**Key inputs:**
- `p_baseline` — current conversion rate (from historical data)
- `mde` — minimum detectable effect (smallest lift worth detecting, e.g., 0.02 for 2pp)
- `alpha` — significance threshold (default 0.05)
- `power` — probability of detecting a real effect (default 0.80)

```python
from statsmodels.stats.power import NormalIndPower

analysis = NormalIndPower()
n_per_arm = analysis.solve_power(
    effect_size=(mde / (p_baseline * (1 - p_baseline)) ** 0.5),
    alpha=alpha,
    power=power,
    alternative='two-sided'
)
print(f"Required sample size: {n_per_arm:,.0f} per arm")
```

**Rule of thumb:** Smaller MDEs and lower baseline rates require much larger samples. If the required N exceeds what you'll collect in a reasonable time window, either raise the MDE or accept lower power.

---

## Sample Ratio Mismatch (SRM)

After an experiment runs, verify users were actually split in the expected ratio (e.g., 50/50). If the observed split differs meaningfully from the configured split, all results are untrustworthy — the assignment mechanism may be broken.

```python
from scipy.stats import chisquare

observed = [n_control, n_test]
expected_ratio = [0.5, 0.5]  # adjust to configured split
total = sum(observed)
expected = [total * r for r in expected_ratio]

stat, p = chisquare(observed, f_exp=expected)
if p < 0.01:
    print(f"WARNING: Sample Ratio Mismatch detected (p={p:.4f}). Results are unreliable.")
else:
    print(f"SRM check passed (p={p:.4f}).")
```

Run this before reporting any experiment results.

---

## Guardrail Metrics

Primary metrics are what you're trying to move. Guardrail metrics are things you must not break — even if the primary metric improves.

**Common guardrails:** revenue per user, session error rate, cancellation rate, page load time.

When reporting experiment results, note whether guardrail metrics moved in either direction. A significant negative movement on a guardrail should block a ship decision even if the primary metric is positive.

**Note:** Adding many guardrail metrics inflates false positive rate. Limit to 2–3 that are genuinely load-bearing for the product area.

---

## Novelty Effect

A new UI or feature sometimes gets a short-term engagement spike simply because it's new — users explore it out of curiosity, then behavior normalizes. This inflates early treatment effects.

**How to check:** Break experiment results by week within the experiment window. If the treatment effect is large in week 1 and decays toward zero in weeks 2–3, you're likely seeing novelty. Report the week-3+ effect as the more reliable estimate.

---

## Upstream / Downstream Consistency

If a downstream metric (e.g., completed) improves but the upstream metric feeding it (e.g., reached step A) is flat or negative, that's a red flag. Either:
- The downstream metric definition is wrong, or
- There's a data artifact (e.g., the completion event fires more reliably in test than control)

Always sanity-check that step rates move in a directionally consistent story from top to bottom of the funnel.
