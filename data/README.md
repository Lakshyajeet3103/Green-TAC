# Data layout

## `measurements.csv`
Empirical compiler/benchmark data collected on the target machine. This is the main training/evaluation dataset for predicting runtime/energy cost. It should contain one or more rows per program and strategy.

Required fields include:

```text
program, category, strategy, compile_time_s, compile_energy_j,
runtime_ms, runtime_energy_j,
```

plus the static program features.

When physical energy measurement is unavailable, the energy columns are left blank. Do not fill them with made-up numbers.

## `model.csv`
Coefficients learned from real measurements by `tools/fit_model.py`.

## `carbon/`
External electricity carbon-intensity data. This is not training data for the code-energy model.

## `benchmark_manifest.csv`
Metadata for generated benchmarks.
