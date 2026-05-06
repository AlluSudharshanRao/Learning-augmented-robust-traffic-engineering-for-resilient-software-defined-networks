# Discussion of Results

## The Final Project Now Has Three Strong Stories

The latest tuned results make the project stronger because it now supports
three distinct but connected conclusions:

1. a meaningful ML comparison
2. a meaningful robust-routing comparison
3. a meaningful uncertainty-aware optimization extension

This is better than relying on only one novelty angle.

## Story 1: The ML Comparison Now Has a Real Winner

The project now compares:

- `Linear AR`
- `Moving Average`
- `LSTM`
- `Transformer`

The most important ML takeaway is still:

- the best forecasting model is not automatically the best routing model

But the tuned sweep now gives a stronger result:

- `Linear AR` often has the lowest RMSE
- `Transformer` is now the strongest pure ML model for nominal routing
- `LSTM` remains competitive and still contributes to the uncertainty-aware
  robust method

This is a better final-project story than the earlier untuned version because
the newer model now matters in the downstream network objective, not only in
the forecasting comparison.

## Story 2: Why the Transformer Now Matters

The tuned Transformer does not just improve prediction error. In the latest
results it also improves downstream congestion performance:

- on Abilene at load `1.0`, `Transformer` beats `LSTM` on nominal utilization
- on NSFNET at load `1.0`, `Transformer` beats `LSTM` on both nominal
  utilization and critical-failure re-optimization
- on the sample topology at load `1.0`, `Transformer` also beats `LSTM` on
  both metrics

That means the aggressive tuning round was worthwhile. It changed the project
from "Transformer is only a baseline" to "Transformer is the strongest pure ML
method in the latest sweep."

## Story 3: Why the Uncertainty-Aware Method Still Matters

The uncertainty-aware method remains important because it adds something the ML
comparison alone cannot provide:

- a decision layer that accounts for prediction uncertainty before optimization

This is still the project's strongest optimization-side contribution.

The final role split is now clearer:

- `Transformer` is the strongest pure nominal-routing ML method
- `LSTM` is still a strong recurrent baseline and supports the uncertainty-aware
  routing extension
- `uncertainty_aware_lstm_robust_lp` is the strongest advanced LP-family method

## What the Results Now Say Academically

The project can now support a more mature claim:

- newer sequence models can matter for downstream traffic engineering
- tuning choices are important
- prediction quality and routing quality are related, but not identical
- robustness still needs an explicit optimization layer even with better ML

That gives the report a stronger methodological arc:

- compare classical forecasting
- compare deep recurrent forecasting
- compare Transformer-based forecasting
- then show why robust optimization is still necessary after prediction

## Final Interpretation

The clearest final interpretation is:

1. The tuned `Transformer` is the strongest pure ML-routing method in the
   latest sweep.
2. `LSTM` remains a credible baseline and is still central to the
   uncertainty-aware robust extension.
3. `uncertainty_aware_lstm_robust_lp` remains the strongest optimization-side
   contribution.
4. Therefore, the project now contributes both a stronger ML-comparison story
   and a strong optimization/robustness story.
