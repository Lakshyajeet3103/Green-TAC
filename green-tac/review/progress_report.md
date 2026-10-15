# Green TAC prototype progress report

15 October 2026

## Review purpose and conclusion

This report supports the 75 percent implementation and prototype review. Green TAC now provides an executable compiler, three optimization strategies, strict feature collection, runtime model fitting, held-out validation and reproducible adaptive decisions. The runtime model is exploratory: validation found it less accurate than a constant-mean reference. Physical energy calibration and measured carbon reduction remain pending. The 75 percent milestone is a project review target, not a statistically measured completion percentage or an awarded score.

## Problem and objectives

Optimization requires compilation work but can reduce work during execution. Green TAC investigates which optimization strategy minimizes the combined carbon cost for a program's expected number of executions, while satisfying a configurable predicted runtime limit. The prototype translates a small integer C-like language into Three-Address Code, considers baseline, lightweight and local DAG common-subexpression elimination, and exports the selected TAC or generated C.

The proposed contribution combines compilation energy, repeated runtime energy, separate grid carbon intensities for the two phases, and a runtime constraint in one strategy selector. These are the project's intended contributions. This review does not establish novelty against the literature or claim a new optimization algorithm.

## Implementation and scope

| Component | Status | Evidence or scope |
| --- | --- | --- |
| Frontend and TAC | Implemented | Assignments, arithmetic, comparisons, if and while |
| Optimization | Implemented and tested | Baseline, lightweight and local DAG CSE |
| Feature collection | Implemented and checked | Ten features with strict CSV validation |
| Runtime fitting | Implemented | Three fitted models with held-out evidence |
| Runtime accuracy | Needs improvement | All fits lose to the mean reference |
| Adaptive selection | Demonstrated | Execution-count and carbon-ratio scenarios |
| Physical energy | Pending | No measured energy or carbon-saving claim |
| Policy evaluation | Pending | Measured adaptive versus fixed-policy comparison |

The C++17 frontend consists of a lexer, parser, AST and TAC generator. Lightweight optimization performs constant folding, algebraic simplification and copy propagation. The DAG strategy adds conservative local common-subexpression elimination. Python scripts build the compiler, collect measurements, fit models and assemble evidence. Generated C is compiled with GCC at -O0 for this experiment.

The handwritten CSE example contains 21 baseline TAC instructions and 13 binary operations. Lightweight retains 21 instructions and reduces binary operations to 8. DAG produces 19 instructions and 6 binary operations, a 9.5 percent instruction reduction. This is a static code-size result, not an energy-saving measurement.

## Runtime measurement method

The fresh study contains 31 programs and 93 program-strategy measurements. Six programs are sampled deterministically from each of five generated categories: arithmetic, constant-heavy, CSE-heavy, loops and mixed control flow. The handwritten CSE example adds one program. The repository contains 120 generated programs; this study measures a balanced subset, not the entire corpus.

Each native executable performs 10 warmup invocations, then calibrates its batch size toward at least 30 milliseconds, with a cap of 100 million invocations. Five batches provide 465 raw samples. The stored runtime is their median divided by batch invocation count. The timer runs inside the process, excluding process startup. Function calls, loop control and the volatile sink remain inside the timed region. These tiny workloads are sensitive to that overhead, host noise and clock variation. Batch repeats are not independent process-level trials.

Environment: Windows-11-10.0.26300-SP0; Intel64 Family 6 Model 186 Stepping 2, GenuineIntel; gcc.EXE (Rev8, Built by MSYS2 project) 15.2.0. Native code uses -O0 and QueryPerformanceCounter. Compile time measures the Green TAC source-to-C process, including its startup and file output, and excludes GCC native compilation. No physical energy provider is used in this study. Energy columns stay blank.

Measurement data and metadata: `data/runtime_study/measurements.csv`, `samples.csv` and `metadata.json`. The metadata records the compiler hash, source hashes, timer, sampling settings, environment and timestamps. Dataset SHA256: `c15f289121ef4de66d61ebc7e833c529ebfd0fc0a927c7cd2625509b571bb954`.

## Runtime model and validation

For each strategy, a StandardScaler and Ridge regression with alpha 1 use ten baseline TAC features to predict runtime in milliseconds. The scaler and validation model fit only the training programs. A fixed GroupShuffleSplit with seed 42 reserves 7 of 31 programs for testing and uses the remaining 24 for training. All strategies use the same held-out program identities. No program appears on both sides of a split. Program-level separation does not prevent shared synthetic templates across splits.

Predictions are clipped at zero to match the C++ selector. The reference predictor uses the training-set mean. After validation, final coefficients are refitted on all 31 programs and converted back to raw-feature coefficients for C++. The metrics below belong to the training-only validation models, not the final full-data fit.

| Strategy | MAE ns | RMSE ns | R squared | Mean reference MAE ns |
| --- | --- | --- | --- | --- |
| baseline | 12.80 | 14.01 | -139.15 | 9.02 |
| lightweight | 12.46 | 13.63 | -118.16 | 8.90 |
| dag | 12.73 | 13.84 | -194.40 | 9.13 |

One nanosecond is 0.000001 milliseconds. All three models have higher MAE than the mean reference and strongly negative R squared. The fitting and export pipeline works, but the current features and dataset do not support a reliable runtime predictor. Negative R squared means the prediction errors exceed the variance-based reference used by that metric. The seven-program holdout is small and has little runtime variation. Static instruction features omit loop bounds and execution frequencies, so structurally similar programs can have different runtimes that the model cannot distinguish.

The fitted model remains available for an explicitly exploratory demonstration. Its 10 percent predicted runtime constraint does not establish a measured 10 percent slowdown guarantee. Improving feature coverage, benchmark diversity and repeated evaluation is required before using this selector as a reliable performance policy.

Evidence: `data/model.csv`, `data/model_metrics.csv`, `data/model_predictions.csv` and `data/model_validation.json`. Energy targets were skipped because there are zero usable physical energy rows. The exported model contains only runtime_ms coefficients.

## Adaptive decision evidence

The selector minimizes:

`CO2e = (E_compile * CI_compile + N * E_runtime * CI_runtime) / 3600000`

Energy is in joules and carbon intensity is in grams CO2e per kWh. For this demonstration, both energy terms use hand-defined feature proxies; the resulting carbon values are illustrative, not measured emissions. Carbon intensities are hypothetical scenarios, not a fetched live grid dataset. Runtime predictions use the fitted exploratory model. The runtime limit is 10 percent above the predicted baseline.

For the same `benchmarks/cse.c` input:

| Executions | Compile CI | Runtime CI | Selected |
| --- | --- | --- | --- |
| 1 | 700 | 200 | baseline |
| 3 | 700 | 200 | lightweight |
| 10 | 700 | 200 | dag |

At one expected execution, changing the carbon context gives:

| Compile CI | Runtime CI | Selected |
| --- | --- | --- |
| 700 | 200 | baseline |
| 200 | 200 | lightweight |
| 700 | 700 | lightweight |
| 200 | 700 | dag |

Holding runtime intensity at 200 while reducing compile intensity from 700 to 200 changes baseline to lightweight. Holding compile intensity at 700 while increasing runtime intensity from 200 to 700 also changes baseline to lightweight. Changing both from 700/200 to 200/700 selects DAG. Applying the same intensity to both phases at 200/200 and 700/700 selects lightweight in both cases: a shared multiplier cannot change the ranking.

All three candidates pass the predicted runtime constraint for these demonstrations. The proxy-only control run produces the same choices. These scenarios verify selector behavior, not energy savings, model generalization or superiority over fixed policies. The demo input is included in the runtime training data and is not held-out policy evidence.

Evidence: `data/results/adaptive/scenarios.csv`, `scenarios.json` and the per-scenario console transcripts. Each transcript explicitly identifies proxy energy and lists runtime eligibility.

## Verification

The compiler builds with C++17 and warning flags. The C++ tests pass, including new assertions for execution-count changes, carbon-ratio changes and rejection of candidates exceeding the runtime limit. Six Python regression and evidence tests pass. They check feature completeness, rejection of legacy CSV headers, sample medians, empty energy fields, program split separation and agreement between exported coefficients and C++ predictions. The adaptive demo asserts expected proxy scenario outcomes and checks that selected candidates are allowed.

This test coverage establishes the tested behaviors. It is not exhaustive compiler semantic equivalence testing. The generated programs return zero, and the current study does not compare observable final variable values across strategies.

## Review rubric mapping

| Rubric item | Evidence prepared |
| --- | --- |
| Implementation and prototype progress 5 marks | Compiler demo, timing study, runtime fit, validation and adaptive transcripts |
| Novelty 2 marks | Proposed combined compilation/runtime carbon objective and runtime constraint |
| Documentation and progress report 1 mark | This report plus reproducible data and commands |
| Presentation and Q and A 2 marks | Offline slide deck with speaker notes and the questions below |

## Limitations and remaining work

1. Improve the runtime model. Add features for loop trip counts or measured execution profiles, use larger workloads and validate across independent program families and machines. Keep failed results as a baseline.
2. Collect physical package energy with an appropriate supported provider. Align measurement boundaries, handle energy-counter wraparound and record domain coverage. Calibrate compile and runtime energy without filling blanks with invented values.
3. Account for selector overhead. The current selector optimizes every candidate and the command regenerates the chosen TAC. Native compilation and selector overhead are not yet included in the modeled compilation objective.
4. Evaluate adaptive selection against always-baseline, always-lightweight and always-DAG using held-out measured energy, observed runtime compliance and prediction error. Include suitable uncertainty estimates.
5. Strengthen compiler correctness tests, including control flow, name collisions, integer semantics and observable outputs. Expand beyond the tiny C-like language only after correctness and measurement foundations are stable.
6. Complete a sourced literature comparison before claiming research novelty. Integrate a real external carbon-intensity dataset for empirical carbon scenarios.

## Demonstration commands

Run from the repository root. The fitting environment must contain numpy and scikit-learn.

```powershell
python run.py test
python -m unittest discover -s tests -p 'test_*.py'
python run.py demo
python run.py adaptive-demo
python run.py green benchmarks/cse.c --compile-ci 700 --runtime-ci 200 --executions 1
python run.py green benchmarks/cse.c --compile-ci 700 --runtime-ci 200 --executions 3
python run.py green benchmarks/cse.c --compile-ci 700 --runtime-ci 200 --executions 10
python run.py green benchmarks/cse.c --compile-ci 200 --runtime-ci 700 --executions 1
```

To repeat collection, choose a fresh output directory. The collector refuses to overwrite an existing study. Do not mix process-inclusive legacy timings with the new in-process measurements.

```powershell
python run.py runtime-study --out data/runtime_study_repeat
python run.py fit --csv data/runtime_study_repeat/measurements.csv --python PATH_TO_PYTHON_WITH_SKLEARN
python run.py adaptive-demo
python tools/build_review.py
```

On the current machine, the fitting interpreter is `C:/Users/Lakshyajeet/AppData/Local/Programs/Python/Python313/python.exe`. The default MSYS2 Python does not currently have scikit-learn installed.

## Questions and answers

**Have you measured carbon savings?** No. Runtime is measured; energy and derived carbon are proxy estimates. Physical energy calibration and policy evaluation remain pending.

**Why can carbon intensity change the strategy?** Compilation and runtime have separate intensities. Their ratio changes how the selector values extra compilation work versus execution savings. A common multiplier cannot change the ranking.

**Why do all three strategies appear in the demo?** At low execution counts the proxy compilation cost dominates. As execution count grows, proxy runtime savings justify stronger optimization.

**Does fitting the runtime model mean it is accurate?** No. The held-out results are worse than a constant-mean reference. This is an implemented fitting pipeline with an unsuccessful first predictive model.

**Is the 10 percent runtime limit guaranteed?** No. The selector enforces a limit on predictions. Measured compliance must be evaluated independently.

**Why compile the generated C at -O0?** It reduces interference from downstream optimization when studying TAC choices. Results are specific to this configuration and do not represent optimized production binaries.

**What is ready for the review?** The compiler pipeline, three strategies, valid feature collection, a measured timing study, model fitting and validation, and reproducible adaptive demonstrations. The remaining research validation is explicitly documented.
