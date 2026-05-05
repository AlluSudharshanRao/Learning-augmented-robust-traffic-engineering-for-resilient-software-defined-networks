# Discussion of Results

## Why the Advanced Extension Matters

The uncertainty-aware routing upgrade is the first step that clearly moves the
project beyond a standard course-project baseline and into a more research-like
direction.

Instead of treating the LSTM prediction as a single exact demand estimate, the
advanced method acknowledges that prediction error exists and uses a residual-
based uncertainty estimate to inflate the routing demand conservatively before
robust optimization.

That makes the final project story stronger because it combines:

- predictive modeling
- uncertainty handling
- robust optimization
- and failure-aware evaluation

## What Stayed the Same

The advanced results do not overturn the earlier core finding:

- `lstm` is still the best pure nominal-routing method

This is important because it means the project now has two complementary
messages rather than one:

- `lstm` is best for nominal traffic engineering
- uncertainty-aware robust LP is best when we want a more resilience-oriented
  LP-family controller

## Why the Uncertainty-Aware Method Is Worth Keeping

The uncertainty-aware method is not just an inflated-demand version of the
robust LP. In the advanced sweep, it produces meaningful improvements:

- better LP-family nominal utilization on Abilene and NSFNET
- better LP-family re-optimization behavior on Abilene and NSFNET
- better LP-family fairness on Abilene and NSFNET
- stronger resilience-side behavior than standard LP across all three
  topologies

It does not dominate every metric in every topology, but it improves the
overall tradeoff enough to justify its inclusion in the final project.

## Why Abilene and NSFNET Behave Differently

The advanced results still show topology dependence.

On Abilene:

- the uncertainty-aware method improves the LP-family nominal tradeoff
- it improves fairness
- but disruption improvements are small and mixed

On NSFNET:

- the uncertainty-aware method improves nominal LP-family behavior
- it improves critical-failure re-optimization behavior
- it stays very close to the robust LP on disruption
- it slightly improves fairness over the robust LP

This suggests that NSFNET offers richer structure for uncertainty-aware routing
to exploit, while Abilene remains a more constrained benchmark where the gains
are narrower.

## Why This Is Better Than Only Adding Another ML Model

A newer predictor such as a Transformer or GNN could still be interesting, but
the uncertainty-aware extension is more valuable at this stage because it
improves the actual end-to-end control logic rather than only changing the
forecasting component.

The project now demonstrates that:

- the LSTM forecast can be used not only directly
- but also through an uncertainty-aware decision layer

That is a stronger integration of ML and optimization than a simple model swap.

## Final Interpretation

The final project now has a layered conclusion:

1. `lstm` is the best nominal-routing method.
2. `robust_current_demand_lp` is a meaningful resilience baseline.
3. `uncertainty_aware_lstm_robust_lp` is the strongest advanced LP-family
   extension and makes the final project more novel and more complete.

That gives the project a cleaner final message than before, because we can now
argue that the advanced extension adds real value rather than just extra
implementation complexity.
