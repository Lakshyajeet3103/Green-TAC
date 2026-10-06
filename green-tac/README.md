# 🌱 Green TAC

**Carbon-Aware Adaptive Three-Address Code Optimization for Green Compilation**

Green TAC is a small research compiler that translates a tiny C-like language into
**Three-Address Code (TAC)**, applies one of several optimization strategies, and
**chooses the strategy that minimizes estimated CO₂e** — taking into account
compilation energy, runtime energy, how often the program will run, and the
carbon intensity of the electricity grid at compile time vs. run time.

- The compiler itself is written in **C++17**.
- **Python** is used only for building, benchmarking, data collection, model
  calibration, and analysis.
- No CMake, Ninja, Make, LLVM, or Visual Studio project is needed — just a C++
  compiler and Python.

---

## Table of contents

- [Quick start](#quick-start)
- [Prerequisites](#prerequisites)
- [Command reference](#command-reference)
- [Input language](#input-language)
- [Compiler pipeline](#compiler-pipeline)
- [Optimization strategies](#optimization-strategies)
- [Carbon model and strategy selection](#carbon-model-and-strategy-selection)
- [Project layout](#project-layout)
- [Research workflow](#research-workflow)
- [Energy measurement](#energy-measurement)
- [Carbon-intensity datasets](#carbon-intensity-datasets)
- [Further documentation](#further-documentation)

---

## Quick start

```bash
python build.py          # compile the C++ sources into bin/
python run.py test       # build and run the unit tests
python run.py demo       # full walkthrough on benchmarks/cse.c
```

`run.py` builds the compiler automatically the first time you use it.

## Prerequisites

| Requirement | Used for | Notes |
|---|---|---|
| C++17 compiler (`g++`, `c++`, or `clang++`) | Building the compiler | Must be on `PATH`. On Windows, an **MSYS2 UCRT64** terminal works well. |
| C compiler (`gcc`) | Benchmark measurement | Compiles the C code generated from TAC. |
| Python 3.8+ | `build.py`, `run.py`, `tools/` | Standard library only for build/run. |
| `pandas`, `numpy`, `scikit-learn`, `matplotlib` | Analysis, model fitting, plots | `pip install -r tools/requirements.txt` |

## Command reference

All commands are run through [`run.py`](run.py):

| Command | What it does |
|---|---|
| `python run.py build` | Build `bin/green_tac(.exe)` |
| `python run.py test` | Build and run the unit tests (`tests/test_main.cpp`) |
| `python run.py info` | Show whether a physical energy provider (RAPL) is available |
| `python run.py demo [file]` | Features + strategy table + TAC for every strategy + green selection |
| `python run.py tac <file> --strategy <baseline\|lightweight\|dag>` | Print TAC for one strategy |
| `python run.py compare <file>` | Side-by-side metrics table and TAC for all strategies |
| `python run.py green <file> [options]` | Run the carbon-aware selector (see below) |
| `python run.py c <file> --strategy <s> [--output out.c]` | Emit compilable C from the optimized TAC |
| `python run.py dataset [--count N]` | Regenerate the synthetic benchmark corpus |
| `python run.py collect [--runs N] [--clean]` | Measure timing/energy for every benchmark × strategy |
| `python run.py analyze [--csv path]` | Summarize a measurements CSV |
| `python run.py plot [--csv path]` | Write plots to `data/results/` |

### Selector options (`green`)

| Option | Default | Meaning |
|---|---|---|
| `--model` | `data/model.csv` | Calibrated cost-model coefficients |
| `--compile-ci` | `400` | Grid carbon intensity during compilation (gCO₂e/kWh) |
| `--runtime-ci` | `400` | Grid carbon intensity during execution (gCO₂e/kWh) |
| `--executions` | `1000` | Expected number of times the program will run |
| `--max-runtime-overhead` | `0.10` | Max allowed runtime slowdown vs. baseline (10%) |

Example:

```bash
python run.py green benchmarks/cse.c --compile-ci 700 --runtime-ci 200 --executions 10000
```

The compiled binary can also be called directly:

```text
green_tac tac <file> <baseline|lightweight|dag>
green_tac compare <file>
green_tac features <file>
green_tac c <file> <baseline|lightweight|dag> <out.c>
green_tac select <file> [model.csv] [compileCI] [runtimeCI] [executions] [maxRuntimeOverhead]
green_tac info
green_tac energy-check
green_tac demo [file]
```

## Input language

Source files (e.g. [`benchmarks/mixed.c`](benchmarks/mixed.c)) use a minimal
C-like syntax with integer variables:

```c
a = 2;
b = 3;
x = (a + b) * (a + b);
if (x > 10) {
    y = x * 2;
} else {
    y = x + 1;
}
```

Supported constructs:

- **Statements:** assignment `id = expr;`, `if (expr) { ... } [else { ... }]`, `while (expr) { ... }`
- **Operators:** `+ - * / %`, comparisons `== != < <= > >=`, parentheses
- **Operands:** integer literals and identifiers (no declarations needed)

## Compiler pipeline

```text
Source program
    -> Lexer                 (src/lexer.cpp)
    -> Parser -> AST         (src/parser.cpp, src/ast.cpp)
    -> Baseline TAC          (src/tac.cpp)
    -> Candidate strategies  (src/optimizer.cpp)
         - baseline
         - lightweight
         - DAG / CSE
    -> Feature extraction    (src/features.cpp)
    -> Empirical cost model  (src/selector.cpp, data/model.csv)
    -> Carbon calculation    (src/carbon.cpp)
    -> Green strategy selection
    -> Final TAC
    -> Optional generated C  (src/codegen_c.cpp)
```

## Optimization strategies

| Strategy | Transformations |
|---|---|
| **baseline** | Straightforward TAC generation, no optimization |
| **lightweight** | Constant folding, algebraic simplification, copy propagation |
| **dag** | Lightweight + local common-subexpression elimination (DAG-based) |

More aggressive optimization usually costs more compile-time energy but may save
runtime energy. Whether it pays off depends on how often the program runs and
how “dirty” the grid is at each phase — that trade-off is what Green TAC models.

## Carbon model and strategy selection

For each strategy *i*:

$$
E_{total}(i) = E_{compile}(i) + N \cdot E_{runtime}(i)
$$

$$
CO_2e(i) = \frac{E_{compile}(i) \cdot CI_{compile} + N \cdot E_{runtime}(i) \cdot CI_{runtime}}{3.6 \times 10^{6}}
$$

where energy is in joules, carbon intensity (CI) is in gCO₂e/kWh, and *N* is the
expected execution count.

The selector picks the strategy with the **lowest CO₂e** among those whose
predicted runtime is within `max-runtime-overhead` of the baseline.

> **Why two carbon intensities?** If the same CI applied to both phases, it would
> just be a common multiplier and could never change the ranking. Separate
> compile-time and runtime CI values make the selection genuinely carbon-aware.

### Calibrated model vs. proxy fallback

- `data/model.csv` holds linear-model coefficients (`strategy,metric,feature,coefficient`)
  for `compile_energy`, `runtime_energy`, and `runtime_ms`, fitted from real measurements.
- The repository **ships without fabricated coefficients**. When a metric is not
  calibrated, the selector falls back to a transparent, feature-based **proxy**
  and clearly labels the output as `partial / proxy fallback`.
- Proxy numbers are for demonstration only and must not be reported as measured energy.

## Project layout

```text
green-tac/
├── build.py                 # Build script (g++/clang++ only, no build system)
├── run.py                   # One-command runner for everything
├── include/greentac/        # Public headers
├── src/                     # Compiler sources (lexer, parser, TAC, optimizer, selector, ...)
├── tests/test_main.cpp      # Unit tests
├── benchmarks/              # Hand-written example programs
│   └── generated/           # Synthetic corpus (arithmetic, cse, constant, loop, mixed)
├── tools/                   # Python scripts
│   ├── generate_benchmarks.py
│   ├── run_benchmarks.py    # Runs measure.py over the corpus
│   ├── measure.py           # Timing + (optional) RAPL energy for one benchmark/strategy
│   ├── analyze_results.py
│   ├── fit_model.py         # Calibrates data/model.csv from measurements
│   ├── plot_results.py
│   ├── fetch_carbon_dataset.py
│   └── requirements.txt
├── data/
│   ├── measurements.csv     # Empirical measurements (git-ignored)
│   ├── model.csv            # Fitted cost-model coefficients
│   ├── benchmark_manifest.csv
│   ├── carbon/              # External grid carbon-intensity data
│   └── results/             # Generated C, executables, plots
├── bin/                     # Build output
├── PROJECT_SPEC.md
└── RESEARCH_WORKFLOW.md
```

## Research workflow

```bash
# 1. Build and verify
python build.py test

# 2. Inspect strategies on one program
python run.py compare benchmarks/cse.c

# 3. (Re)generate the 120-program benchmark corpus
python run.py dataset --count 120

# 4. Collect measurements for every benchmark × strategy
python run.py collect --runs 50 --clean

# 5. Summarize and plot
python run.py analyze
python run.py plot

# 6. Calibrate the cost model (requires real energy data)
pip install -r tools/requirements.txt
python tools/fit_model.py data/measurements.csv data/model.csv
```

`fit_model.py` validates on held-out **programs** (not repeated runs of the same
program) and writes metrics to `data/model_metrics.csv`. Avoid fitting many
features to a tiny dataset.

### Evaluation

Compare four policies — **always baseline**, **always lightweight**,
**always DAG**, and **green adaptive selection** — reporting compile time/energy,
runtime/energy, total energy, CO₂e, TAC instruction count, temporaries, CSE count,
runtime-overhead compliance, and selector prediction error. Also report hardware,
OS, compiler version, run count, energy provider, and carbon-intensity source.

The main research question: *does adaptive selection reduce total carbon compared
with fixed policies while keeping runtime acceptable?*

## Energy measurement

Source code has no single fixed energy value — it depends on the compiled
implementation, hardware, workload, and environment. Green TAC therefore keeps
**physical measurements separate from proxy estimates**.

- On **Linux** with a powercap/RAPL `energy_uj` counter, the measurement scripts
  record real package energy.
- On unsupported systems (e.g. Windows/MSYS2), energy columns are left **blank**
  and must not be filled with invented values. Timing is always recorded.

Check the provider with:

```bash
python run.py info
```

## Carbon-intensity datasets

Grid carbon data is kept separate from compiler-energy training data
(see [`data/carbon/README.md`](data/carbon/README.md)).

| Source | Granularity | Link |
|---|---|---|
| **Ember – India** | Monthly, national/state | <https://ember-energy.org/data/india-electricity-data/> (`python tools/fetch_carbon_dataset.py`) |
| **Electricity Maps** | Hourly by zone (academic access) | <https://app.electricitymaps.com/docs/reference/carbon-intensity> |
| **GB Carbon Intensity API** | Hourly historical/forecast, Great Britain | <https://api.carbonintensity.org.uk/> |

## Further documentation

- [`PROJECT_SPEC.md`](PROJECT_SPEC.md) — research objective and formal specification
- [`RESEARCH_WORKFLOW.md`](RESEARCH_WORKFLOW.md) — step-by-step experimental workflow
- [`data/README.md`](data/README.md) — data file formats
- [`data/carbon/README.md`](data/carbon/README.md) — carbon-data strategy
