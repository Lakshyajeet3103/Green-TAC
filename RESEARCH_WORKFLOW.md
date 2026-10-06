# Research workflow

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
