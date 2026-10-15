# Data layout

## `measurements.csv`
Empirical compiler/benchmark data collected on the target machine. This is the main training/evaluation dataset for predicting runtime/energy cost. It should contain one or more rows per program and strategy.

Required fields include:

```text
program, category, strategy, compile_time_s, compile_energy_j,
runtime_ms, runtime_energy_j,
```

plus the static program features.

The collector reads `green_tac features <file> --machine`, which exports all ten
baseline TAC features as `name=value` lines. These baseline features are shared
by the three strategy rows, matching the selector's model inputs. Human-readable
feature summaries remain available without `--machine`.

Collection rejects missing/invalid features and incompatible existing CSV
headers before appending. Older timing-only CSVs must be preserved separately
and measurements recollected; the model fitter rejects missing feature columns.

When physical energy measurement is unavailable, the energy columns are left blank. Do not fill them with made-up numbers.

## `model.csv`
Coefficients learned from real measurements by `tools/fit_model.py`.

The current file contains only runtime models. Their held-out errors are saved
in `model_metrics.csv`; all three currently lose to the training-mean reference.
`model_predictions.csv` records each held-out prediction. `model_validation.json`
records the dataset hash, train/test program identities and fitting method.

## `runtime_study/`

This timing-only dataset uses the timer inside the generated native executable
to exclude process startup. `measurements.csv` contains 93 median observations
from 31 programs and three strategies. `samples.csv` contains the five raw
batches per observation. `metadata.json` records compiler/hardware details,
sampling settings, source hashes and completion status. Do not merge these
runtime values with the legacy process-inclusive measurements.

## `results/adaptive/`

Scenario CSV/JSON files and actual compiler transcripts for changing execution
count and compile/runtime carbon intensity. Energy and derived carbon remain
explicit proxies. These are mechanism demonstrations, not measured policy
savings. `proxy_only_model.csv` intentionally contains no fitted coefficients
and provides a reproducible proxy-only control.

## `carbon/`
External electricity carbon-intensity data. This is not training data for the code-energy model.

## `benchmark_manifest.csv`
Metadata for generated benchmarks.
