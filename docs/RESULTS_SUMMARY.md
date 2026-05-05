# Results Summary

## Scope

The latest advanced evaluation is stored under:

- `outputs/sweeps_advanced/`

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

- `outputs/sweeps_advanced/all_run_summaries.csv`
- `outputs/sweeps_advanced/aggregated_summary.csv`
- `outputs/sweeps_advanced/run_index.csv`

Advanced report assets:

- `outputs/sweeps_advanced/report_assets/figures/summary_nominal_utilization.png`
- `outputs/sweeps_advanced/report_assets/figures/summary_critical_fixed_disruption.png`
- `outputs/sweeps_advanced/report_assets/figures/summary_critical_fixed_fairness.png`
- `outputs/sweeps_advanced/report_assets/figures/abilene_lp_family_comparison.png`
- `outputs/sweeps_advanced/report_assets/figures/nsfnet_lp_family_comparison.png`
- `outputs/sweeps_advanced/report_assets/tables/main_results_load1p0.csv`
- `outputs/sweeps_advanced/report_assets/tables/robust_lp_direct_comparison.csv`

## Important Limitation

`GEANT2012` is still supported by the topology loader, but it is not part of
the advanced sweep because the current LP formulation remains too expensive on
that graph for the chosen time budget.

## Methods Compared

The advanced sweep compares:

- `moving_average`
- `linear_autoregressive`
- `lstm`
- `current_demand_lp`
- `robust_current_demand_lp`
- `uncertainty_aware_lstm_robust_lp`

## Main Findings

### 1. LSTM remains the best pure nominal-routing method

Across all three topologies and all load levels, `lstm` is still the best
method for `nominal_max_utilization`.

That means the advanced uncertainty-aware extension does not replace the
original LSTM result. Instead, it adds a stronger resilience-oriented method to
the project.

### 2. Prediction RMSE and routing quality are still not the same thing

The advanced results preserve the earlier core finding:

- `lstm` does not have the best forecasting RMSE
- but it remains the strongest nominal-routing model

That is still one of the most important conclusions in the project.

### 3. The uncertainty-aware LP is a meaningful advanced addition

The new uncertainty-aware method uses:

- the LSTM forecast
- a residual-based uncertainty estimate
- and a conservative demand inflation step before robust routing

This method gives a stronger LP-family comparison than before:

- on `sample`, it improves resilience-side metrics substantially
- on `abilene`, it improves nominal LP-family behavior and fairness, while
  remaining mixed on disruption
- on `nsfnet`, it improves nominal LP-family behavior, re-optimization
  behavior, and fairness, while staying close to the robust LP on disruption

## Topology-Specific Findings

### Sample

Main pattern:

- `lstm` is still best nominally
- uncertainty-aware robust routing becomes the best LP-family resilience method
- it also improves fairness relative to both standard LP and robust LP

Interpretation:

- even on the synthetic network, uncertainty-aware routing is not just adding
  complexity
- it produces a real resilience-side gain

### Abilene

Main pattern:

- `lstm` remains the best nominal method overall
- uncertainty-aware robust LP is better than both LP baselines on nominal
  utilization
- uncertainty-aware robust LP improves LP-family fairness clearly
- disruption remains mixed

At load `1.0`:

- `current_demand_lp` nominal utilization: `1.0232`
- `robust_current_demand_lp` nominal utilization: `1.0232`
- `uncertainty_aware_lstm_robust_lp` nominal utilization: `0.9999`

- `current_demand_lp` critical fixed disruption: `0.3219`
- `robust_current_demand_lp` critical fixed disruption: `0.3254`
- `uncertainty_aware_lstm_robust_lp` critical fixed disruption: `0.3233`

- `current_demand_lp` critical fixed fairness: `0.6891`
- `robust_current_demand_lp` critical fixed fairness: `0.6892`
- `uncertainty_aware_lstm_robust_lp` critical fixed fairness: `0.6927`

Interpretation:

- on Abilene, the uncertainty-aware method gives a more convincing advanced
  result than the older robust LP alone
- but LSTM is still the strongest single method if the goal is pure nominal
  congestion minimization

### NSFNET

Main pattern:

- `lstm` remains the best nominal method overall
- uncertainty-aware robust LP becomes the strongest advanced LP-family method
- it improves over both LP baselines on nominal utilization, re-optimization,
  and fairness

At load `1.0`:

- `current_demand_lp` nominal utilization: `1.1255`
- `robust_current_demand_lp` nominal utilization: `1.1255`
- `uncertainty_aware_lstm_robust_lp` nominal utilization: `1.0976`

- `current_demand_lp` critical failure reopt utilization: `1.5696`
- `robust_current_demand_lp` critical failure reopt utilization: `1.5696`
- `uncertainty_aware_lstm_robust_lp` critical failure reopt utilization: `1.5304`

- `current_demand_lp` critical fixed disruption: `0.2521`
- `robust_current_demand_lp` critical fixed disruption: `0.2342`
- `uncertainty_aware_lstm_robust_lp` critical fixed disruption: `0.2351`

- `current_demand_lp` critical fixed fairness: `0.7428`
- `robust_current_demand_lp` critical fixed fairness: `0.7584`
- `uncertainty_aware_lstm_robust_lp` critical fixed fairness: `0.7587`

Interpretation:

- on NSFNET, the uncertainty-aware method is strong enough to keep in the final
  project
- it is the best advanced LP-family tradeoff overall

## Best Final Narrative

The strongest final storyline is now:

1. `lstm` is the best method for nominal traffic engineering.
2. Prediction RMSE alone does not explain routing performance.
3. `robust_current_demand_lp` improves resilience on some topologies, but is not
   always enough.
4. `uncertainty_aware_lstm_robust_lp` is a meaningful advanced extension that
   improves the LP-family tradeoff, especially on NSFNET and partially on
   Abilene.

## Suggested Final Figures

Use these as the main report figures:

- `report_assets/figures/summary_nominal_utilization.png`
- `report_assets/figures/summary_critical_fixed_disruption.png`
- `report_assets/figures/summary_critical_fixed_fairness.png`
- `report_assets/figures/nsfnet_lp_family_comparison.png`
- `report_assets/figures/abilene_lp_family_comparison.png`
- one representative `worst_failure_case.png`

## Suggested Final Tables

Use these as the main report tables:

- `report_assets/tables/main_results_load1p0.csv`
- `report_assets/tables/nominal_utilization_pivot.csv`
- `report_assets/tables/robust_lp_direct_comparison.csv`
- `report_assets/tables/best_method_by_topology_and_load.csv`
