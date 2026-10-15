# Research workflow

## Current review evidence

The 15 October 2026 review uses `data/runtime_study/measurements.csv`, not the
legacy process-inclusive timings in `data/measurements.csv`. The study has 31
programs, three strategies and five in-process timed batches per combination.
Raw samples and hardware/compiler metadata are stored beside the measurements.

`python run.py fit --python PATH_TO_PYTHON_WITH_SKLEARN` fits the three runtime
models, validates by program, saves held-out predictions and exports raw-feature
coefficients for C++. The current models lose to a training-mean reference on
held-out MAE. They are exploratory, and physical energy models remain absent.

`python run.py adaptive-demo` saves both fitted-runtime/proxy-energy scenarios
and a proxy-only control in `data/results/adaptive/`. These demonstrate decision
behavior; they do not measure carbon reduction or held-out policy performance.

`python tools/build_review.py` regenerates the report and offline presentation
under `review/` from the saved evidence. See `review/README.md` for opening them.

## 1. Build and verify

```bash
python build.py test
```

## 2. Inspect all strategies

```bash
python run.py compare benchmarks/cse.c
```

This runs baseline, lightweight, and DAG/CSE on the same input and prints the TAC plus static metrics.

## 3. Create the benchmark corpus

The repository includes a 120-program synthetic corpus. To regenerate it deterministically:

```bash
python run.py dataset --count 120
```

The categories are arithmetic, CSE-heavy, constant-heavy, loop-heavy, and mixed.

## 4. Collect empirical compiler/runtime data

```bash
python run.py collect --runs 50 --clean
```

The measurement CSV records timing always. Physical energy is recorded only when a supported provider is available.

On the current Windows/MSYS2 setup used during development, the Linux RAPL provider is unavailable, so the energy fields remain blank. This is intentional.

## 5. Calibration dataset

The energy model should be trained from `data/measurements.csv`, after real energy measurements are available. The model inputs are static program/TAC features; the targets are compile energy, runtime energy, and runtime.

Use:

```bash
python tools/fit_model.py data/measurements.csv data/model.csv
```

The script validates on held-out **programs**, then fits final coefficients on all usable measured rows.

## 6. Carbon-intensity context

Grid carbon intensity is a separate dataset. It is not the target for the code-energy model. Use an external source such as Ember India, Electricity Maps (academic access where eligible), or the official Great Britain Carbon Intensity API.

The selector combines energy estimates with compile/runtime carbon-intensity values:

```text
CO2e = compile_energy * compile_CI
     + N * runtime_energy * runtime_CI
```

with the appropriate J-to-kWh conversion.

## 7. Evaluate the research claim

Compare:

```text
Always baseline
Always lightweight
Always DAG
Green adaptive selector
```

Primary metrics:

- runtime
- runtime energy
- compile time
- compile energy
- total energy
- CO2e
- TAC instruction count
- temporary variables
- CSEs
- runtime-overhead constraint
- selector prediction error

Use separate train/test programs and report the hardware, OS, compiler version, run count, energy provider, and carbon-intensity source.
