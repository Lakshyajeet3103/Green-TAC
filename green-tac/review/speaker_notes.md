# Green TAC presentation notes

## 1 Green TAC

Introduce the project as a working research prototype. The 75 percent wording names the review milestone, not an independently measured completion score. No measured carbon-saving claim is made.

## 2 Problem and objectives

Explain that the compiler needs the expected execution count and the carbon context for both phases. The main research question is whether adaptive choices can outperform fixed strategies on measured total carbon.

## 3 Compiler pipeline

The compiler uses C++17. Python handles build, collection, model fitting and reporting. This is a restricted integer language, not a complete C compiler. The selector currently executes every candidate optimizer, so its overhead remains part of the remaining measurement work.

## 4 Optimization evidence

Lightweight folds constants and simplifies expressions. DAG eliminates repeated expressions locally. The instruction count remains 21 for lightweight because assignments remain even when arithmetic is simplified. Source: compiler compare output for benchmarks/cse.c.

## 5 Carbon objective and proposed contribution

Read the denominator as 3.6 million. Expected executions N scales runtime cost. The proposed contribution is the combined decision framework, not a claim that constant folding or CSE is new. Current energy values are proxies. Source: src/carbon.cpp and src/selector.cpp.

## 6 Runtime study

Six programs per category plus one example. Batches target at least 30 milliseconds subject to a 100 million invocation cap. The timed region includes function call, loop and volatile sink overhead. These are within-process repeats, not independent process trials. Source: data/runtime_study/metadata.json and samples.csv.

## 7 Runtime validation found poor accuracy

Values are displayed in nanoseconds for readability; data and the C++ model use milliseconds. Strongly negative R squared indicates poor held-out performance. The small test set has little variation. Features omit loop bounds and dynamic execution counts. Do not describe this as an accurate or production-ready model. Sources: data/model_metrics.csv, model_predictions.csv and model_validation.json.

## 8 Execution count changes the decision

The actual selector chose baseline at one execution, lightweight at three and DAG at ten. All candidates passed the predicted runtime constraint in these examples. The example is in the training dataset, so this is mechanism evidence rather than held-out policy evidence. Source: data/results/adaptive/scenarios.json.

## 9 Carbon intensity changes the decision

Compare the first and second rows to isolate compile intensity, then the first and third rows to isolate runtime intensity. Changing both phases to 200/700 selects DAG. Scaling a shared intensity cannot change rankings. Source: data/results/adaptive/scenarios.json.

## 10 Evidence for the prototype review

Map these items to the provided rubric without predicting marks. Fitting is implemented, while predictive accuracy is not satisfactory. Physical energy and measured policy comparisons remain outstanding. Tests include feature export, sample medians, split separation and C++ coefficient parity.

## 11 Limitations and remaining work

The generated benchmark returns zero rather than exposing final variable values. Current correctness tests are limited. The selector optimizes all candidates, so account for that work before claiming compilation-energy savings. Real carbon data and robust energy counter handling are still pending.

## 12 Live demonstration and questions

The command uses a PowerShell backtick for line continuation. Expected selection is lightweight. Runtime is measured, energy is proxy. The runtime model failed its first accuracy evaluation. The report contains expanded Q and A.