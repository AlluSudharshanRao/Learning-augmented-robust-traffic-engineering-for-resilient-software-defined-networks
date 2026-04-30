# Experiment Guide

## Environment

Activate the project-local environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or run commands directly:

```powershell
.\.venv\Scripts\python.exe .\run_experiment.py --config .\configs\abilene.json
```

## Available Configurations

- `configs/sample.json`
- `configs/abilene.json`
- `configs/nsfnet.json`

## Example Commands

### Synthetic sample network

```powershell
.\.venv\Scripts\python.exe .\run_experiment.py --config .\configs\sample.json
```

### Abilene benchmark

```powershell
.\.venv\Scripts\python.exe .\run_experiment.py --config .\configs\abilene.json
```

### NSFNET benchmark

```powershell
.\.venv\Scripts\python.exe .\run_experiment.py --config .\configs\nsfnet.json
```

## What Each Run Produces

### `experiment_results.csv`

Per-time-step metrics for each method, including:

- prediction error
- nominal utilization
- re-optimization after failure
- fixed-routing disruption fractions
- robust LP metadata columns

### `summary_results.csv`

Method-level averages across all evaluation time steps.

Use this file for:

- comparison tables in the report
- quick ranking of methods

### `failure_disruptions.csv`

Lists the most disrupted commodities in fixed-failure scenarios.

Use this file for:

- identifying vulnerable traffic demands
- interpreting which flows are fragile

### `failure_paths.csv`

Contains path-level decomposition for disrupted commodities.

Use this file for:

- showing which routes traversed a failed link
- extracting example paths for the report or presentation

### `nominal_utilization_by_method.png`

Bar chart of average nominal utilization across methods.

### `worst_failure_case.png`

Network visualization of the most severe disrupted commodity case.

## How To Read the Main Metrics

### Prediction metrics

- lower `prediction_mae` is better
- lower `prediction_rmse` is better

### Routing metrics

- lower `nominal_max_utilization` is better
- lower `critical_failure_reopt_max_utilization` is better
- lower `random_failure_reopt_max_utilization` is better

### Fixed-routing disruption metrics

- higher `*_fixed_served_fraction` is better
- lower `*_fixed_disrupted_fraction` is better

### Robust LP metadata

- `robust_nominal_utilization` = nominal scenario objective value for the robust LP
- `robust_worst_case_utilization` = optimized worst-case value across selected robust scenarios
- `robust_failure_scenarios` = scenario set used for that robust optimization run

## Suggested Analysis Flow

1. Compare nominal utilization across methods.
2. Compare re-optimization behavior after failures.
3. Compare fixed-routing disruption fractions.
4. Open `failure_disruptions.csv` to find the most fragile commodities.
5. Open `failure_paths.csv` to inspect the actual vulnerable routes.
6. Use `worst_failure_case.png` as a presentation figure.

## Notes for the Final Report

The best story is not only “which method has the lowest average congestion.”
It is also:

- which method is most resilient after failures
- which commodities are vulnerable
- why the vulnerable routes failed
- whether the robust LP changes that behavior
