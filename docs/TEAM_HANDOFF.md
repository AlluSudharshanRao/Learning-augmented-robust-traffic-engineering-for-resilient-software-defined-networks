# Team Handoff

## Start Here

If you are joining the project and want the latest state quickly, use these in
order:

1. [README.md](C:/Users/sudha/OneDrive/Desktop/networks/README.md)
2. [docs/RESULTS_SUMMARY.md](C:/Users/sudha/OneDrive/Desktop/networks/docs/RESULTS_SUMMARY.md)
3. [docs/DISCUSSION_OF_RESULTS.md](C:/Users/sudha/OneDrive/Desktop/networks/docs/DISCUSSION_OF_RESULTS.md)
4. [outputs/sweeps_advanced/report_assets](C:/Users/sudha/OneDrive/Desktop/networks/outputs/sweeps_advanced/report_assets)

## Latest Official Results

The latest official evaluation set is:

- [outputs/sweeps_advanced](C:/Users/sudha/OneDrive/Desktop/networks/outputs/sweeps_advanced)

Use this instead of older folders like `outputs/sweeps_report/` or
one-off verification runs when writing the report or slides.

## Latest Main Conclusion

The project currently supports three main takeaways:

- `lstm` is the best pure nominal-routing method
- `robust_current_demand_lp` is a useful resilience baseline
- `uncertainty_aware_lstm_robust_lp` is the strongest advanced LP-family method,
  especially on NSFNET and partially on Abilene

## Most Important Files

Code:

- [src/teproject/experiment.py](C:/Users/sudha/OneDrive/Desktop/networks/src/teproject/experiment.py)
- [src/teproject/predictors.py](C:/Users/sudha/OneDrive/Desktop/networks/src/teproject/predictors.py)
- [src/teproject/optimizer.py](C:/Users/sudha/OneDrive/Desktop/networks/src/teproject/optimizer.py)
- [src/teproject/plotting.py](C:/Users/sudha/OneDrive/Desktop/networks/src/teproject/plotting.py)
- [src/teproject/reporting.py](C:/Users/sudha/OneDrive/Desktop/networks/src/teproject/reporting.py)

Configs:

- [configs/abilene_uncertainty_0p25.json](C:/Users/sudha/OneDrive/Desktop/networks/configs/abilene_uncertainty_0p25.json)
- [configs/nsfnet_uncertainty_0p25.json](C:/Users/sudha/OneDrive/Desktop/networks/configs/nsfnet_uncertainty_0p25.json)

Results and assets:

- [outputs/sweeps_advanced/report_assets/tables/main_results_load1p0.csv](C:/Users/sudha/OneDrive/Desktop/networks/outputs/sweeps_advanced/report_assets/tables/main_results_load1p0.csv)
- [outputs/sweeps_advanced/report_assets/tables/robust_lp_direct_comparison.csv](C:/Users/sudha/OneDrive/Desktop/networks/outputs/sweeps_advanced/report_assets/tables/robust_lp_direct_comparison.csv)
- [outputs/sweeps_advanced/report_assets/figures/nsfnet_lp_family_comparison.png](C:/Users/sudha/OneDrive/Desktop/networks/outputs/sweeps_advanced/report_assets/figures/nsfnet_lp_family_comparison.png)
- [outputs/sweeps_advanced/report_assets/figures/abilene_lp_family_comparison.png](C:/Users/sudha/OneDrive/Desktop/networks/outputs/sweeps_advanced/report_assets/figures/abilene_lp_family_comparison.png)

## Recommended Next Work

If there is more time before final submission, the best next choices are:

- final report writing
- final slide deck
- optional newer ML baseline such as Transformer or GNN
- optional rerouting-cost-aware optimization
