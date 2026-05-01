# Discussion of Results

## Core Interpretation

The final results support two main claims.

First, the project's learning-augmented traffic-engineering idea works well for
nominal routing. Across all evaluated topologies and load levels, the LSTM-based
method gives the lowest nominal maximum link utilization.

Second, robust optimization is useful, but only in a topology-dependent way.
The robust LP is not uniformly better than the standard LP. Instead, its
benefit depends on whether the network structure makes failure-side service
preservation an important challenge.

That means the results are strong precisely because they are not artificially
perfect. They show where each method helps and where its impact is limited.

## Why LSTM Wins Nominal Routing

An interesting outcome of the project is that the LSTM is not the best method
for prediction RMSE, but it is still the best method for nominal routing.

The most reasonable interpretation is:

- the LSTM does not need the most accurate pointwise prediction of every demand
  entry
- it only needs to estimate the traffic pattern well enough for the optimizer
  to spread traffic more effectively

This matters because the downstream optimization problem is congestion-focused,
not prediction-error-focused. In other words, the model that best supports the
routing objective is not necessarily the model with the lowest forecasting
error.

That is one of the clearest contributions of the project.

## Why Robustness Helps More on NSFNET Than on Abilene

The benchmark comparison shows a clear difference between Abilene and NSFNET.

On Abilene:

- the robust LP leaves nominal utilization unchanged
- changes in re-optimization utilization are small and mixed
- fixed-failure disruption and fairness change only slightly

This suggests that the current failure-scenario design does not meaningfully
reshape the routing solution on Abilene. The network may already be structured
so that the standard LP can find a solution with limited room for robust
improvement.

On NSFNET:

- the robust LP leaves nominal utilization unchanged
- fixed-failure disrupted demand decreases by about `0.018`
- fixed-failure fairness increases by about `0.016`

That is a meaningful and consistent resilience improvement. The likely
interpretation is that NSFNET offers more routing diversity, so the robust LP
can exploit alternate structure to protect commodities against critical
failures.

## Re-Optimization Versus Fixed-Routing Resilience

The project evaluates failures in two different ways:

- re-optimization after a failure
- fixed-routing stress without immediate rerouting

This distinction is important.

If a controller is allowed to reroute immediately after failure, then a network
may appear resilient even if the original routing plan was fragile. By contrast,
the fixed-routing evaluation shows how much demand is disrupted before recovery
actions can help.

That makes the fixed-routing metrics especially valuable for the final report,
because they capture the inherent vulnerability of the pre-failure routing
decision.

The robust LP is most convincing on exactly those fixed-routing metrics for
NSFNET.

## What the Mixed Results Mean Academically

The mixed topology-dependent results are not a weakness. They make the project
more believable.

If every method improvement had been uniformly positive across all networks and
all metrics, the final story would be less convincing. Instead, the project now
shows:

- a consistently strong predictive-routing result through LSTM
- a selective but real robustness benefit on NSFNET
- a clear explanation of where the robust LP still needs refinement

That is a strong course-project outcome because it combines implementation,
evaluation, and honest interpretation.

## Final Takeaway

The final takeaway can be stated simply:

- use `lstm` when the primary goal is nominal traffic engineering quality
- use `robust_current_demand_lp` when failure-side service preservation matters
  and the topology supports meaningful robust rerouting structure
- evaluate both prediction quality and routing quality, because they are not the
  same thing

This gives the project a balanced conclusion rather than a one-method-fits-all
claim.
