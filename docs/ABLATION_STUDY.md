# Ablation Study

## Scope

The focused ablation study is stored under:

- `outputs/ablations_final/`

It was designed to strengthen the final presentation without changing the core
project architecture.

Settings:

- topologies:
  - `abilene`
  - `nsfnet`
- load scale:
  - `1.0`
- seeds:
  - `7`
  - `11`
  - `13`

Families studied:

- `transformer`
- `uncertainty`
- `robust`

Key summary artifacts:

- `report_assets/tables/best_method_by_topology_load.csv`
- `report_assets/tables/ml_vs_routing_tradeoff.csv`
- `report_assets/tables/robustness_tradeoff_summary.csv`
- `report_assets/tables/uncertainty_multiplier_sensitivity.csv`

## What We Varied

### 1. Transformer tuning settings

Variants:

- `base`
- `tuned_a`
- `tuned_b`
- `tuned_c`

Goal:

- determine whether a tuned Transformer can outperform the LSTM baseline on the
  downstream routing objective

### 2. Uncertainty multiplier

Variants:

- `0.1`
- `0.25`
- `0.4`
- `0.5`

Goal:

- measure how aggressively uncertainty inflation should be used before robust
  optimization

### 3. Robust LP scenario count and weights

Variants:

- `nominal_s2`
- `balanced_s3`
- `conservative_s4`

Goal:

- understand how robust-scenario count and nominal vs worst-case weighting
  affect congestion and resilience

## Main Findings

### Transformer tuning

Most important table:

- `report_assets/tables/ml_vs_routing_tradeoff.csv`

Key findings:

- On `NSFNET`, `tuned_b` is the strongest Transformer setting.
- On `NSFNET`, `tuned_b` beats `LSTM` on:
  - nominal max utilization
  - critical-failure re-optimization utilization
  - and prediction RMSE
- On `Abilene`, no Transformer variant dominates `LSTM` on every metric.
- On `Abilene`, `tuned_b` comes closest on nominal routing, but `LSTM` remains
  slightly stronger or more stable overall depending on which metric is
  prioritized.

Interpretation:

- Transformer success is topology-dependent.
- Tuning matters a lot.
- The final report should not present the Transformer as universally better
  everywhere, but it can confidently say that a tuned Transformer is highly
  competitive and clearly best on NSFNET.

### Uncertainty multiplier sensitivity

Most important table:

- `report_assets/tables/uncertainty_multiplier_sensitivity.csv`

Key findings:

- On `NSFNET`, `0.1` is the best multiplier across the tested settings.
- On `NSFNET`, larger multipliers steadily worsen:
  - nominal utilization
  - critical-failure re-optimization
  - and slightly worsen disruption/fairness
- On `Abilene`, `0.1` gives the best nominal and re-optimization performance.
- On `Abilene`, `0.25` gives the best fixed-failure disruption and fairness
  tradeoff.

Interpretation:

- There is no single perfect multiplier for every topology and every metric.
- `0.1` is the best conservative global choice if nominal and re-optimization
  performance are prioritized.
- `0.25` remains a reasonable balanced setting when the presentation wants to
  emphasize failure-side fairness on Abilene.

### Robust LP scenario / weight sensitivity

Most important table:

- `report_assets/tables/robustness_tradeoff_summary.csv`

Key findings:

- On `NSFNET`, `conservative_s4` is dramatically stronger than the other robust
  settings.
- On `NSFNET`, `conservative_s4` sharply improves:
  - nominal utilization
  - fixed-failure disruption
  - and fairness
- On `NSFNET`, `conservative_s4` slightly worsens re-optimization for
  `robust_current_demand_lp`, but the `uncertainty_aware_lstm_robust_lp`
  version still remains better than `current_demand_lp`.
- On `Abilene`, `conservative_s4` hurts resilience-side metrics and fairness.
- On `Abilene`, `balanced_s3` or `nominal_s2` are more stable.

Interpretation:

- Robustness design is strongly topology-dependent.
- More conservative scenario coverage is not automatically better everywhere.
- This is a valuable final-presentation point because it shows the project is
  identifying real tradeoffs rather than producing one universal winner.

## Best Overall Methods in the Ablation Set

Most important table:

- `report_assets/tables/best_method_by_topology_load.csv`

Current summary:

- On `Abilene`, the best nominal method in the ablation set is `LSTM` under the
  `transformer:tuned_a` configuration, while the best resilience result comes
  from `uncertainty_aware_lstm_robust_lp` under `robust:balanced_s3`.
- On `NSFNET`, the best nominal and resilience results both come from
  `uncertainty_aware_lstm_robust_lp` under `robust:conservative_s4`.

## How To Use This in the Presentation

Good presentation message:

1. Transformer tuning matters, and the tuned model is clearly strongest on
   NSFNET.
2. Uncertainty inflation has a visible sensitivity curve, so the robust method
   is not a black box.
3. Robust scenario design changes the outcome materially, especially on NSFNET.
4. The project therefore includes not just a winning method, but a clear
   explanation of why and when it works.

## Recommended Slide Assets

Use these figures:

- `report_assets/figures/transformer_ablation_nominal.png`
- `report_assets/figures/transformer_ablation_tradeoff.png`
- `report_assets/figures/uncertainty_multiplier_sensitivity.png`
- `report_assets/figures/robustness_tradeoff.png`
