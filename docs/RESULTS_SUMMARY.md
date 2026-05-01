# Results Summary

## Scope

The final consolidated evaluation for the report is stored under:

- `outputs/sweeps_report/`

The sweep covers:

- topologies:
  - `sample`
  - `abilene`
  - `nsfnet`
- load scales:
  - `0.8`
  - `1.0`
  - `1.2`
- seeds:
  - `7`
  - `11`

Key aggregate files:

- `outputs/sweeps_report/all_run_summaries.csv`
- `outputs/sweeps_report/aggregated_summary.csv`
- `outputs/sweeps_report/run_index.csv`

Report-ready assets:

- `outputs/sweeps_report/report_assets/figures/summary_nominal_utilization.png`
- `outputs/sweeps_report/report_assets/figures/summary_critical_fixed_disruption.png`
- `outputs/sweeps_report/report_assets/figures/summary_critical_fixed_fairness.png`
- `outputs/sweeps_report/report_assets/figures/abilene_robust_vs_standard_lp.png`
- `outputs/sweeps_report/report_assets/figures/nsfnet_robust_vs_standard_lp.png`
- `outputs/sweeps_report/report_assets/tables/main_results_load1p0.csv`
- `outputs/sweeps_report/report_assets/tables/robust_lp_direct_comparison.csv`

## Important Limitation

`GEANT2012` remains supported by the topology loader, but it is not part of the
final sweep because the current LP formulation is too expensive on that graph
for the chosen method set and time budget.

That should be stated clearly in the report:

- GEANT2012 support exists
- the final evaluation is focused on the tractable topologies:
  - `sample`
  - `abilene`
  - `nsfnet`

## Methods Compared

The final sweep compares:

- `moving_average`
- `linear_autoregressive`
- `lstm`
- `current_demand_lp`
- `robust_current_demand_lp`

## Main Findings

### 1. LSTM is the strongest nominal-routing method

Across all three topologies and all load levels, `lstm` is the best method for
`nominal_max_utilization`.

This is one of the strongest findings in the project because it is consistent
and easy to communicate:

- the LSTM is not the best forecasting model by RMSE
- but it is the best downstream routing model for nominal congestion

That supports the core project claim that traffic prediction should be judged
through the routing objective, not only through forecasting error.

### 2. Better prediction RMSE does not guarantee better traffic engineering

`current_demand_lp` and `linear_autoregressive` often have lower
`prediction_rmse` than `lstm`, especially on Abilene and NSFNET.

However, `lstm` still gives the best nominal congestion.

This is a valuable result, not a weakness:

- forecasting quality and routing quality are related
- but they are not identical

That helps justify the learning-augmented traffic-engineering framing of the
project.

### 3. The robust LP is topology-dependent

The final tuned robust LP has a cleaner and more believable pattern than the
earlier version:

- on `sample`, it behaves almost like the standard LP
- on `abilene`, it is mostly neutral to slightly mixed
- on `nsfnet`, it clearly improves fixed-failure resilience and fairness

This is exactly the kind of nuanced result that makes the project stronger.

## Topology-Specific Findings

### Sample

Main pattern:

- `lstm` is best for nominal utilization
- robust and standard LP are nearly identical

Interpretation:

- the synthetic sample network is mainly a sanity-check environment
- it is too small and symmetric to highlight the benefit of the robust design

### Abilene

Main pattern:

- `lstm` is best for nominal utilization at every load level
- robust LP leaves nominal utilization unchanged relative to standard LP
- robust LP is mostly neutral, with only small changes on failure metrics

Direct LP comparison:

- nominal utilization delta is effectively `0.0`
- critical-failure re-optimization utilization changes by about `-0.008` to
  `+0.042`
- fixed-routing disrupted fraction changes by about `+0.002` to `+0.004`
- fairness changes are very small, around `0.0` to `+0.002`

Interpretation:

- Abilene does not provide strong evidence for the current robust objective
- but the result is still useful because it shows robustness is not universally
  beneficial

### NSFNET

Main pattern:

- `lstm` is best for nominal utilization at every load level
- robust LP leaves nominal utilization unchanged relative to standard LP
- robust LP clearly improves fixed-failure disruption and fairness

Direct LP comparison:

- nominal utilization delta is effectively `0.0`
- critical-failure re-optimization utilization is unchanged
- fixed-routing disrupted fraction improves by about `0.018`
- fairness improves by about `0.016`

Interpretation:

- NSFNET is the clearest case where explicit robust optimization helps
- the benefit appears on fixed-failure service preservation rather than nominal
  congestion

## Fairness Findings

The final fairness metrics are:

- `critical_failure_fixed_fairness`
- `random_failure_fixed_fairness`

These are Jain's fairness indices computed from the served-ratio distribution
after fixed failures.

Observed pattern:

- fairness differences are small on `sample`
- fairness differences are also small on `abilene`
- fairness improves clearly on `nsfnet` under the robust LP

This is useful because it connects:

- resilient routing
- service continuity
- fair demand treatment under failures

## Best Report Narrative

The strongest final storyline is:

1. `lstm` is the best nominal-routing method across all evaluated topologies.
2. Prediction RMSE alone does not explain routing performance.
3. The robust LP is not a universal winner, but it helps when the topology and
   failure structure make failure-side service preservation important.
4. In the final results, NSFNET is the clearest benchmark showing that robust
   routing improves resilience and fairness without hurting nominal congestion.

## Suggested Final Figures

Use these as the main report figures:

- `report_assets/figures/summary_nominal_utilization.png`
- `report_assets/figures/summary_critical_fixed_disruption.png`
- `report_assets/figures/summary_critical_fixed_fairness.png`
- `report_assets/figures/nsfnet_robust_vs_standard_lp.png`
- `report_assets/figures/abilene_robust_vs_standard_lp.png`
- one representative `worst_failure_case.png` from NSFNET

## Suggested Final Tables

Use these as the main report tables:

- `report_assets/tables/main_results_load1p0.csv`
- `report_assets/tables/nominal_utilization_pivot.csv`
- `report_assets/tables/robust_lp_direct_comparison.csv`
- `report_assets/tables/best_method_by_topology_and_load.csv`
