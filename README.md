# Green TAC

**Carbon-Aware Adaptive Three-Address Code Optimization for Green Compilation**

A small research compiler written in **C++**, with **Python only for building, benchmarking, data collection, calibration, and analysis**. No CMake, Ninja, Makefile, LLVM, or Visual Studio project is required.

## Quick start

From an MSYS2 UCRT64 terminal (or another terminal where `g++` is on PATH):

```bash
python build.py
python run.py test
python run.py demo
```

That is enough to build and exercise the compiler.

## Useful commands

### Generate TAC with any strategy

```bash
python run.py tac benchmarks/cse.c --strategy baseline
python run.py tac benchmarks/cse.c --strategy lightweight
python run.py tac benchmarks/cse.c --strategy dag
```

### Compare all strategies at once

```bash
python run.py compare benchmarks/cse.c
```

This prints a formatted table plus the TAC for all three strategies.

### Run the carbon-aware selector

```bash
python run.py green benchmarks/cse.c --compile-ci 700 --runtime-ci 200 --executions 10000
```

### Build / tests / environment info

```bash
python run.py build
python run.py test
python run.py info
```

## Compiler pipeline

```text
Source program
    -> Lexer
    -> Parser
    -> AST
    -> Baseline TAC
    -> Candidate strategies
         - baseline
         - lightweight
         - DAG/CSE
    -> Empirical cost model
    -> Carbon calculation
    -> Green strategy selection
    -> Final TAC
    -> Optional generated C
```

## Energy vs carbon: important methodology

Source code does not have one fixed energy value. Energy depends on the compiled implementation, hardware, workload, and runtime environment.

The project therefore keeps **physical energy measurements** separate from proxy estimates.

For strategy i:

```text
E_total = E_compile + N * E_runtime
```

and:

```text
CO2e = E_compile * CI_compile / 3.6e6
     + N * E_runtime * CI_runtime / 3.6e6
```

where energy is in joules, carbon intensity is in gCO2e/kWh, and N is expected execution count.

If the same carbon intensity is applied to every phase, it is only a common multiplier and cannot change the strategy ranking. The project therefore supports separate compilation and runtime carbon intensities.

## Experimental data

Generate a larger benchmark corpus:

```bash
python tools/generate_benchmarks.py --count 120
```

This creates arithmetic, CSE-heavy, constant-heavy, loop-heavy, and mixed programs plus `data/benchmark_manifest.csv`.

Collect measurements for every strategy:

```bash
python tools/run_benchmarks.py --runs 50 --clean
```

Then summarize:

```bash
python tools/analyze_results.py data/measurements.csv
```

## Energy measurement

On Linux systems exposing a supported powercap/RAPL `energy_uj` counter, the measurement scripts can record physical energy. On unsupported systems, energy is left blank and must not be replaced by invented values.

Check the current provider:

```bash
python run.py info
```

## Energy-model calibration

After collecting enough real energy measurements:

```bash
pip install -r tools/requirements.txt
python tools/fit_model.py data/measurements.csv data/model.csv
```

The script writes validation metrics to `data/model_metrics.csv`.

Do not fit a 10-feature model to a tiny dataset. For research, split by **program**, not repeated runs of the same program.

## Carbon-intensity datasets

Keep grid data separate from compiler-energy training data.

### India / Ember

Ember's India electricity dataset includes carbon intensity and covers national/state data. Download the raw monthly dataset with:

```bash
python tools/fetch_carbon_dataset.py
```

Source page:
https://ember-energy.org/data/india-electricity-data/

### Hourly option / Electricity Maps

Eligible academic users can access historical carbon-intensity datasets/API. The API supports hourly historical carbon intensity by zone, subject to access and terms:

https://app.electricitymaps.com/docs/reference/carbon-intensity

### Great Britain

The official Great Britain Carbon Intensity API provides historical/forecast carbon-intensity endpoints:

https://api.carbonintensity.org.uk/

See `data/carbon/README.md` for the data strategy.

## Research evaluation

Compare four policies:

1. Always baseline
2. Always lightweight
3. Always DAG
4. **Green adaptive selection**

Report:

- compilation time
- compilation energy (measured)
- runtime
- runtime energy (measured)
- total energy
- CO2e
- TAC instruction count
- temporaries
- CSE count
- runtime-overhead constraint
- selector prediction error

The main research question is whether the adaptive policy reduces total estimated/measured carbon compared with fixed policies while maintaining acceptable runtime.
=======
# Green-TAG

