# Results Summary

## Scope

The latest official evaluation is stored under:

- `outputs/sweeps_ml_compare/`

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

- `outputs/sweeps_ml_compare/all_run_summaries.csv`
- `outputs/sweeps_ml_compare/aggregated_summary.csv`
- `outputs/sweeps_ml_compare/run_index.csv`

Latest report assets:

- `outputs/sweeps_ml_compare/report_assets/figures/summary_nominal_utilization.png`
- `outputs/sweeps_ml_compare/report_assets/figures/summary_critical_fixed_disruption.png`
- `outputs/sweeps_ml_compare/report_assets/figures/summary_critical_fixed_fairness.png`
- `outputs/sweeps_ml_compare/report_assets/figures/abilene_lp_family_comparison.png`
- `outputs/sweeps_ml_compare/report_assets/figures/nsfnet_lp_family_comparison.png`
- `outputs/sweeps_ml_compare/report_assets/figures/ml_nominal_comparison.png`
- `outputs/sweeps_ml_compare/report_assets/figures/ml_prediction_rmse_comparison.png`
- `outputs/sweeps_ml_compare/report_assets/tables/main_results_load1p0.csv`
- `outputs/sweeps_ml_compare/report_assets/tables/ml_comparison_load1p0.csv`
- `outputs/sweeps_ml_compare/report_assets/tables/robust_lp_direct_comparison.csv`
- `outputs/sweeps_ml_compare/report_assets/tables/best_method_by_topology_and_load.csv`

## Important Limitation

`GEANT2012` is still supported by the topology loader, but it is not part of
the latest sweep because the current LP formulation remains too expensive for
the chosen time budget.

## Methods Compared

The latest sweep compares:

- `moving_average`
- `linear_autoregressive`
- `lstm`
- `transformer`
- `current_demand_lp`
- `robust_current_demand_lp`
- `uncertainty_aware_lstm_robust_lp`

## Main Findings

### 1. The tuned Transformer is now the strongest pure nominal-routing ML method

After the aggressive tuning round, `transformer` becomes the strongest pure
ML-routing method in the latest sweep. It wins
`nominal_max_utilization` in 6 of the 9 topology/load combinations in
`best_method_by_topology_and_load.csv`, including all three topologies at
load `1.0`.

### 2. The ML comparison is now stronger, not weaker

The updated ML-comparison sweep still supports the key modeling lesson:

- lower prediction RMSE does not automatically imply better traffic engineering

But the tuned Transformer now improves the practical story:

- `Linear AR` often has the best RMSE
- `Transformer` now has the best pure nominal routing quality at load `1.0`
- `LSTM` remains competitive and still powers the uncertainty-aware robust
  method

### 3. The Transformer is now a headline ML result

The Transformer is no longer just a modern baseline:

- it trains correctly
- it predicts valid traffic matrices
- it integrates cleanly with routing and failure evaluation
- it now outperforms `LSTM` on nominal routing in the latest tuned sweep

That gives the final report a stronger ML section because we can now compare:

- classical predictors
- recurrent deep learning
- Transformer-based sequence modeling

and show that tuning the newer model can matter.

## ML Comparison at Load 1.0

### Abilene

- `Linear AR` RMSE: `0.5613`
- `Transformer` RMSE: `0.6768`
- `LSTM` RMSE: `1.0219`

- `Transformer` nominal utilization: `0.9039`
- `LSTM` nominal utilization: `0.9104`
- `Linear AR` nominal utilization: `0.9949`

Interpretation:

- `Linear AR` is still the best forecaster by RMSE
- `Transformer` is now the best pure ML routing model
- `LSTM` remains very close, which keeps the comparison credible

### NSFNET

- `Linear AR` RMSE: `0.5403`
- `Transformer` RMSE: `0.7173`
- `LSTM` RMSE: `1.0472`

- `Transformer` nominal utilization: `0.9650`
- `LSTM` nominal utilization: `0.9775`
- `Linear AR` nominal utilization: `1.1108`

- `Transformer` critical reopt utilization: `1.3442`
- `LSTM` critical reopt utilization: `1.3649`

Interpretation:

- `Linear AR` is again the best forecaster by RMSE
- the tuned `Transformer` gives the strongest pure ML congestion result
- on NSFNET it also slightly beats `LSTM` on critical-failure re-optimization

### Sample

- `Transformer` RMSE: `0.6775`
- `LSTM` RMSE: `0.7631`

- `Transformer` nominal utilization: `0.3526`
- `LSTM` nominal utilization: `0.3740`

- `Transformer` critical reopt utilization: `0.6700`
- `LSTM` critical reopt utilization: `0.7106`

Interpretation:

- the tuned Transformer also leads the synthetic sample topology at load `1.0`
- the advantage is not limited to one benchmark network

## Robust / Uncertainty-Aware Findings

The LP-family story remains strong:

- `robust_current_demand_lp` is a useful resilience baseline
- `uncertainty_aware_lstm_robust_lp` is the strongest advanced LP-family method

On NSFNET at load `1.0`:

- `current_demand_lp` nominal utilization: `1.1255`
- `robust_current_demand_lp` nominal utilization: `1.1255`
- `uncertainty_aware_lstm_robust_lp` nominal utilization: `1.0231`

- `current_demand_lp` critical reopt utilization: `1.5696`
- `uncertainty_aware_lstm_robust_lp` critical reopt utilization: `1.4280`

- `current_demand_lp` critical fixed fairness: `0.7428`
- `robust_current_demand_lp` critical fixed fairness: `0.7584`
- `uncertainty_aware_lstm_robust_lp` critical fixed fairness: `0.7575`

Interpretation:

- the uncertainty-aware method remains worth keeping in the final project
- the improved Transformer result does not weaken the robust-optimization story

## Best Final Narrative

The strongest final storyline is now:

1. The tuned `Transformer` is the strongest pure nominal-routing ML method in
   the latest sweep.
2. `LSTM` remains important because it is competitive on routing and is the
   predictor used by the uncertainty-aware robust method.
3. Prediction RMSE alone still does not explain traffic-engineering quality.
4. `uncertainty_aware_lstm_robust_lp` is the strongest advanced LP-family
   extension and improves the project's novelty and depth.

## Suggested Final Figures

Use these as the main report figures:

- `report_assets/figures/ml_nominal_comparison.png`
- `report_assets/figures/ml_prediction_rmse_comparison.png`
- `report_assets/figures/summary_nominal_utilization.png`
- `report_assets/figures/summary_critical_fixed_disruption.png`
- `report_assets/figures/summary_critical_fixed_fairness.png`
- `report_assets/figures/nsfnet_lp_family_comparison.png`
- `report_assets/figures/abilene_lp_family_comparison.png`

## Suggested Final Tables

Use these as the main report tables:

- `report_assets/tables/ml_comparison_load1p0.csv`
- `report_assets/tables/main_results_load1p0.csv`
- `report_assets/tables/nominal_utilization_pivot.csv`
- `report_assets/tables/robust_lp_direct_comparison.csv`
- `report_assets/tables/best_method_by_topology_and_load.csv`
