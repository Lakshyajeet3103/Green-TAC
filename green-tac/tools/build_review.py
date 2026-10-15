#!/usr/bin/env python3
"""Build offline review documents from recorded experiment evidence."""
import csv
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'review'
OUT.mkdir(exist_ok=True)
metrics = list(csv.DictReader((ROOT / 'data/model_metrics.csv').open()))
scenarios = json.loads((ROOT / 'data/results/adaptive/scenarios.json').read_text())
validation = json.loads((ROOT / 'data/model_validation.json').read_text())
study_dir = (ROOT / validation['source']).parent
meta = json.loads((study_dir / 'metadata.json').read_text())
hybrid = [r for r in scenarios if r['mode'] == 'runtime_fit_energy_proxy']


def table(headers, rows):
    return '<table><thead><tr>' + ''.join('<th>'+html.escape(str(x))+'</th>' for x in headers) + '</tr></thead><tbody>' + ''.join('<tr>'+''.join('<td>'+html.escape(str(x))+'</td>' for x in row)+'</tr>' for row in rows)+'</tbody></table>'


def mdtable(headers, rows):
    return '| ' + ' | '.join(headers) + ' |\n| ' + ' | '.join('---' for _ in headers) + ' |\n' + '\n'.join('| ' + ' | '.join(str(x) for x in row) + ' |' for row in rows)


metric_rows = [[r['strategy'], f"{float(r['mae'])*1e6:.2f}", f"{float(r['rmse'])*1e6:.2f}", f"{float(r['r2']):.2f}", f"{float(r['mean_reference_mae'])*1e6:.2f}"] for r in metrics]
metric_headers = ['Strategy', 'MAE ns', 'RMSE ns', 'R squared', 'Mean reference MAE ns']
usage_rows = [[r['executions'], r['compile_ci'], r['runtime_ci'], r['selected']] for r in hybrid[:3]]
ci_rows = [[r['compile_ci'], r['runtime_ci'], r['selected']] for r in [hybrid[0], hybrid[3], hybrid[4], hybrid[5]]]
status_rows = [
    ['Frontend and TAC', 'Implemented', 'Assignments, arithmetic, comparisons, if and while'],
    ['Optimization', 'Implemented and tested', 'Baseline, lightweight and local DAG CSE'],
    ['Feature collection', 'Implemented and checked', 'Ten features with strict CSV validation'],
    ['Runtime fitting', 'Implemented', 'Three fitted models with held-out evidence'],
    ['Runtime accuracy', 'Needs improvement', 'All fits lose to the mean reference'],
    ['Adaptive selection', 'Demonstrated', 'Execution-count and carbon-ratio scenarios'],
    ['Physical energy', 'Pending', 'No measured energy or carbon-saving claim'],
    ['Policy evaluation', 'Pending', 'Measured adaptive versus fixed-policy comparison'],
]
report = f'''# Green TAC prototype progress report

15 October 2026

## Review purpose and conclusion

This report supports the 75 percent implementation and prototype review. Green TAC now provides an executable compiler, three optimization strategies, strict feature collection, runtime model fitting, held-out validation and reproducible adaptive decisions. The runtime model is exploratory: validation found it less accurate than a constant-mean reference. Physical energy calibration and measured carbon reduction remain pending. The 75 percent milestone is a project review target, not a statistically measured completion percentage or an awarded score.

## Problem and objectives

Optimization requires compilation work but can reduce work during execution. Green TAC investigates which optimization strategy minimizes the combined carbon cost for a program's expected number of executions, while satisfying a configurable predicted runtime limit. The prototype translates a small integer C-like language into Three-Address Code, considers baseline, lightweight and local DAG common-subexpression elimination, and exports the selected TAC or generated C.

The proposed contribution combines compilation energy, repeated runtime energy, separate grid carbon intensities for the two phases, and a runtime constraint in one strategy selector. These are the project's intended contributions. This review does not establish novelty against the literature or claim a new optimization algorithm.

## Implementation and scope

{mdtable(['Component', 'Status', 'Evidence or scope'], status_rows)}

The C++17 frontend consists of a lexer, parser, AST and TAC generator. Lightweight optimization performs constant folding, algebraic simplification and copy propagation. The DAG strategy adds conservative local common-subexpression elimination. Python scripts build the compiler, collect measurements, fit models and assemble evidence. Generated C is compiled with GCC at -O0 for this experiment.

The handwritten CSE example contains 21 baseline TAC instructions and 13 binary operations. Lightweight retains 21 instructions and reduces binary operations to 8. DAG produces 19 instructions and 6 binary operations, a 9.5 percent instruction reduction. This is a static code-size result, not an energy-saving measurement.

## Runtime measurement method

The fresh study contains 31 programs and 93 program-strategy measurements. Six programs are sampled deterministically from each of five generated categories: arithmetic, constant-heavy, CSE-heavy, loops and mixed control flow. The handwritten CSE example adds one program. The repository contains 120 generated programs; this study measures a balanced subset, not the entire corpus.

Each native executable performs 10 warmup invocations, then calibrates its batch size toward at least 30 milliseconds, with a cap of 100 million invocations. Five batches provide 465 raw samples. The stored runtime is their median divided by batch invocation count. The timer runs inside the process, excluding process startup. Function calls, loop control and the volatile sink remain inside the timed region. These tiny workloads are sensitive to that overhead, host noise and clock variation. Batch repeats are not independent process-level trials.

Environment: {meta['os']}; {meta['processor']}; {meta['cc_version']}. Native code uses -O0 and QueryPerformanceCounter. Compile time measures the Green TAC source-to-C process, including its startup and file output, and excludes GCC native compilation. No physical energy provider is used in this study. Energy columns stay blank.

Measurement data and metadata: `data/runtime_study/measurements.csv`, `samples.csv` and `metadata.json`. The metadata records the compiler hash, source hashes, timer, sampling settings, environment and timestamps. Dataset SHA256: `{meta['measurement_sha256']}`.

## Runtime model and validation

For each strategy, a StandardScaler and Ridge regression with alpha 1 use ten baseline TAC features to predict runtime in milliseconds. The scaler and validation model fit only the training programs. A fixed GroupShuffleSplit with seed 42 reserves 7 of 31 programs for testing and uses the remaining 24 for training. All strategies use the same held-out program identities. No program appears on both sides of a split. Program-level separation does not prevent shared synthetic templates across splits.

Predictions are clipped at zero to match the C++ selector. The reference predictor uses the training-set mean. After validation, final coefficients are refitted on all 31 programs and converted back to raw-feature coefficients for C++. The metrics below belong to the training-only validation models, not the final full-data fit.

{mdtable(metric_headers, metric_rows)}

One nanosecond is 0.000001 milliseconds. All three models have higher MAE than the mean reference and strongly negative R squared. The fitting and export pipeline works, but the current features and dataset do not support a reliable runtime predictor. Negative R squared means the prediction errors exceed the variance-based reference used by that metric. The seven-program holdout is small and has little runtime variation. Static instruction features omit loop bounds and execution frequencies, so structurally similar programs can have different runtimes that the model cannot distinguish.

The fitted model remains available for an explicitly exploratory demonstration. Its 10 percent predicted runtime constraint does not establish a measured 10 percent slowdown guarantee. Improving feature coverage, benchmark diversity and repeated evaluation is required before using this selector as a reliable performance policy.

Evidence: `data/model.csv`, `data/model_metrics.csv`, `data/model_predictions.csv` and `data/model_validation.json`. Energy targets were skipped because there are zero usable physical energy rows. The exported model contains only runtime_ms coefficients.

## Adaptive decision evidence

The selector minimizes:

`CO2e = (E_compile * CI_compile + N * E_runtime * CI_runtime) / 3600000`

Energy is in joules and carbon intensity is in grams CO2e per kWh. For this demonstration, both energy terms use hand-defined feature proxies; the resulting carbon values are illustrative, not measured emissions. Carbon intensities are hypothetical scenarios, not a fetched live grid dataset. Runtime predictions use the fitted exploratory model. The runtime limit is 10 percent above the predicted baseline.

For the same `benchmarks/cse.c` input:

{mdtable(['Executions', 'Compile CI', 'Runtime CI', 'Selected'], usage_rows)}

At one expected execution, changing the carbon context gives:

{mdtable(['Compile CI', 'Runtime CI', 'Selected'], ci_rows)}

Holding runtime intensity at 200 while reducing compile intensity from 700 to 200 changes baseline to lightweight. Holding compile intensity at 700 while increasing runtime intensity from 200 to 700 also changes baseline to lightweight. Changing both from 700/200 to 200/700 selects DAG. Applying the same intensity to both phases at 200/200 and 700/700 selects lightweight in both cases: a shared multiplier cannot change the ranking.

All three candidates pass the predicted runtime constraint for these demonstrations. The proxy-only control run produces the same choices. These scenarios verify selector behavior, not energy savings, model generalization or superiority over fixed policies. The demo input is included in the runtime training data and is not held-out policy evidence.

Evidence: `data/results/adaptive/scenarios.csv`, `scenarios.json` and the per-scenario console transcripts. Each transcript explicitly identifies proxy energy and lists runtime eligibility.

## Verification

The compiler builds with C++17 and warning flags. The C++ tests pass, including new assertions for execution-count changes, carbon-ratio changes and rejection of candidates exceeding the runtime limit. Six Python regression and evidence tests pass. They check feature completeness, rejection of legacy CSV headers, sample medians, empty energy fields, program split separation and agreement between exported coefficients and C++ predictions. The adaptive demo asserts expected proxy scenario outcomes and checks that selected candidates are allowed.

This test coverage establishes the tested behaviors. It is not exhaustive compiler semantic equivalence testing. The generated programs return zero, and the current study does not compare observable final variable values across strategies.

## Review rubric mapping

{mdtable(['Rubric item', 'Evidence prepared'], [['Implementation and prototype progress 5 marks', 'Compiler demo, timing study, runtime fit, validation and adaptive transcripts'], ['Novelty 2 marks', 'Proposed combined compilation/runtime carbon objective and runtime constraint'], ['Documentation and progress report 1 mark', 'This report plus reproducible data and commands'], ['Presentation and Q and A 2 marks', 'Offline slide deck with speaker notes and the questions below']])}

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
'''
report = report.replace('data/runtime_study/', study_dir.relative_to(ROOT).as_posix() + '/')
(OUT / 'progress_report.md').write_text(report, encoding='utf-8')
# A self-contained printable report with basic Markdown conversion.
lines = report.splitlines(); body = []; i = 0
while i < len(lines):
    line = lines[i]
    if line.startswith('```'):
        code=[]; i+=1
        while i<len(lines) and not lines[i].startswith('```'):
            code.append(lines[i]); i+=1
        body.append('<pre>'+html.escape('\n'.join(code))+'</pre>')
    elif line.startswith('| '):
        rows=[]
        while i<len(lines) and lines[i].startswith('| '):
            rows.append([s.strip() for s in lines[i].strip('|').split('|')]); i+=1
        body.append(table(rows[0], rows[2:])); continue
    elif line.startswith('#'):
        n=len(line)-len(line.lstrip('#')); body.append(f'<h{n}>'+html.escape(line[n:].strip())+f'</h{n}>')
    elif line.strip():
        body.append('<p>'+html.escape(line).replace('**','').replace('`','')+'</p>')
    i+=1
report_css = 'body{font:16px/1.55 Segoe UI,Arial,sans-serif;color:#202722;max-width:900px;margin:50px auto;padding:0 30px}h1{font-size:34px}h2{font-size:23px;margin-top:32px;color:#000}table{border-collapse:collapse;width:100%;font-size:14px;margin:22px 0}th,td{border:1px solid #d9d9d9;padding:10px;text-align:left}th{background:#dfe8ec;color:black}tr:nth-child(even){background:#f6f8f9}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f6f8f9;padding:18px;font-size:13px}p{overflow-wrap:anywhere}@media print{body{font-size:10pt;margin:0;max-width:none}h1{font-size:24pt}h2{font-size:16pt;break-after:avoid}table{font-size:9pt}tr{break-inside:avoid}pre{font-size:8pt}thead{display:table-header-group}@page{size:A4;margin:18mm}}'
(OUT / 'progress_report.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Green TAC progress report</title><style>'+report_css+'</style><body>'+''.join(body)+'</body></html>', encoding='utf-8')

slides=[]
def slide(title, content, note='', theme=''):
    slides.append((title,content,note,theme))

slide('Green TAC', '<p class="subtitle">Carbon-aware adaptive TAC optimization</p><p class="intro">75 percent prototype review</p><p class="date">15 October 2026</p><p class="cover-note">Working pipeline and decision demonstrations<br>Runtime accuracy and physical energy remain open</p>', 'Introduce the project as a working research prototype. The 75 percent wording names the review milestone, not an independently measured completion score. No measured carbon-saving claim is made.', 'cover')
slide('Problem and objectives', '<p class="lead">Extra compilation work can pay off when a program runs often.</p><ol><li>Generate TAC from a small C-like language.</li><li>Compare three optimization strategies.</li><li>Choose a strategy using compilation and runtime carbon costs.</li><li>Apply a predicted runtime-overhead limit.</li></ol>', 'Explain that the compiler needs the expected execution count and the carbon context for both phases. The main research question is whether adaptive choices can outperform fixed strategies on measured total carbon.')
slide('Compiler pipeline', '<ol class="pipeline"><li><b>Source to TAC</b><span>Lexer, parser, AST and baseline TAC</span></li><li><b>Optimization candidates</b><span>Baseline, lightweight and local DAG CSE</span></li><li><b>Prediction and selection</b><span>Ten features, runtime model and carbon objective</span></li><li><b>Output</b><span>Selected TAC and optional generated C</span></li></ol>', 'The compiler uses C++17. Python handles build, collection, model fitting and reporting. This is a restricted integer language, not a complete C compiler. The selector currently executes every candidate optimizer, so its overhead remains part of the remaining measurement work.')
slide('Optimization evidence', table(['Strategy','TAC instructions','Binary operations'], [['Baseline',21,13],['Lightweight',21,8],['DAG',19,6]])+'<p class="lead">DAG reduces TAC instruction count by 9.5%.</p><p class="footnote">Input: benchmarks/cse.c. Static code result, not measured energy savings.</p>', 'Lightweight folds constants and simplifies expressions. DAG eliminates repeated expressions locally. The instruction count remains 21 for lightweight because assignments remain even when arithmetic is simplified. Source: compiler compare output for benchmarks/cse.c.')
slide('Carbon objective and proposed contribution', '<p class="formula">C = (E<sub>compile</sub> CI<sub>compile</sub> + N E<sub>runtime</sub> CI<sub>runtime</sub>) / (3.6 × 10<sup>6</sup>)</p><p class="lead">Minimize predicted carbon subject to a runtime limit.</p><p class="body">Combine compilation cost, expected reuse and separate carbon intensities for compilation and execution.</p><p class="footnote">Energy in J. Intensity in gCO2e/kWh. Novelty against prior research remains to be established.</p>', 'Read the denominator as 3.6 million. Expected executions N scales runtime cost. The proposed contribution is the combined decision framework, not a claim that constant folding or CSE is new. Current energy values are proxies. Source: src/carbon.cpp and src/selector.cpp.')
slide('Runtime study', '<div class="stats"><div><strong>31</strong><span>programs</span></div><div><strong>93</strong><span>strategy measurements</span></div><div><strong>465</strong><span>timed batches</span></div></div><p class="body">Five benchmark categories and the handwritten CSE example. Ten warmup invocations, adaptive batch size and five samples per strategy.</p><p class="body">In-process timer excludes startup. Median batch time per invocation at GCC -O0.</p><p class="footnote">Windows 11, GCC 15.2.0, QueryPerformanceCounter. Physical energy fields remain blank.</p>', 'Six programs per category plus one example. Batches target at least 30 milliseconds subject to a 100 million invocation cap. The timed region includes function call, loop and volatile sink overhead. These are within-process repeats, not independent process trials. Source: data/runtime_study/metadata.json and samples.csv.')
slide('Runtime validation found poor accuracy', table(metric_headers,metric_rows)+'<p class="body">24 training programs and 7 held-out programs per strategy. StandardScaler and Ridge regression with alpha 1.</p><p class="warning">Every fit loses to the training-mean reference. Treat runtime predictions as exploratory.</p>', 'Values are displayed in nanoseconds for readability; data and the C++ model use milliseconds. Strongly negative R squared indicates poor held-out performance. The small test set has little variation. Features omit loop bounds and dynamic execution counts. Do not describe this as an accurate or production-ready model. Sources: data/model_metrics.csv, model_predictions.csv and model_validation.json.')
slide('Execution count changes the decision', table(['Expected executions','Compile CI','Runtime CI','Selected strategy'],usage_rows)+'<p class="body">Same source, same carbon intensities and a 10% predicted runtime limit.</p><p class="warning">Fitted runtime model with proxy energy. No measured carbon-saving claim.</p>', 'The actual selector chose baseline at one execution, lightweight at three and DAG at ten. All candidates passed the predicted runtime constraint in these examples. The example is in the training dataset, so this is mechanism evidence rather than held-out policy evidence. Source: data/results/adaptive/scenarios.json.')
slide('Carbon intensity changes the decision', table(['Compile CI','Runtime CI','Selected at N = 1'],ci_rows)+'<p class="footnote">Equal CI at 200/200 and 700/700 both select lightweight. Common scaling preserves rankings.</p><p class="warning">Hypothetical CI in gCO2e/kWh. Energy and carbon remain proxies.</p>', 'Compare the first and second rows to isolate compile intensity, then the first and third rows to isolate runtime intensity. Changing both phases to 200/700 selects DAG. Scaling a shared intensity cannot change rankings. Source: data/results/adaptive/scenarios.json.')
slide('Evidence for the prototype review', table(['Review area','Evidence ready'], [['Implementation','Compiler, optimization, collection, fitting and selector'],['Novelty','Combined carbon objective and runtime constraint'],['Documentation','Progress report, methods, data and commands'],['Presentation and Q and A','Reproducible demos and explicit limitations']])+'<p class="body">Build and C++ tests pass. Six Python regression and evidence tests pass.</p>', 'Map these items to the provided rubric without predicting marks. Fitting is implemented, while predictive accuracy is not satisfactory. Physical energy and measured policy comparisons remain outstanding. Tests include feature export, sample medians, split separation and C++ coefficient parity.')
slide('Limitations and remaining work', '<ol><li><b>Runtime accuracy</b> Add execution-sensitive features and broader validation.</li><li><b>Physical energy</b> Collect and calibrate real compile and runtime energy.</li><li><b>Policy comparison</b> Measure adaptive versus fixed choices, including selector overhead.</li><li><b>Correctness and novelty</b> Expand semantic tests and complete the literature comparison.</li></ol>', 'The generated benchmark returns zero rather than exposing final variable values. Current correctness tests are limited. The selector optimizes all candidates, so account for that work before claiming compilation-energy savings. Real carbon data and robust energy counter handling are still pending.')
slide('Live demonstration and questions', '<pre>python run.py demo\npython run.py adaptive-demo\n\npython run.py green benchmarks/cse.c \\\n  --compile-ci 700 --runtime-ci 200 --executions 3</pre><p class="lead">Working prototype with transparent evidence</p><p class="body">Runtime fitting and adaptive behavior are demonstrated. Reliable prediction and measured carbon reduction remain research tasks.</p>', 'For Windows PowerShell, enter the green command on one line; the displayed backslash is only a visual line continuation. Expected selection is lightweight. Key Q&A: Runtime is measured, energy is proxy; a fitted model is not necessarily accurate; the runtime limit applies to predictions; equal carbon multipliers preserve ranking. The report contains expanded answers.')

# Keep the displayed command directly pasteable on PowerShell.
title, content, note, theme = slides[-1]
content = content.replace(' \\\n  ', ' ' + chr(96) + '\n  ')
note = 'The command uses a PowerShell backtick for line continuation. Expected selection is lightweight. Runtime is measured, energy is proxy. The runtime model failed its first accuracy evaluation. The report contains expanded Q and A.'
slides[-1] = title, content, note, theme
css = '''*{box-sizing:border-box}html,body{margin:0;background:#14251e;font-family:Segoe UI,Arial,sans-serif;color:#20352b}main{height:calc(100vh - 52px);display:flex;align-items:center;justify-content:center;overflow:hidden}.slide{width:1280px;height:720px;flex-shrink:0;position:relative;background:#f5f7f2;padding:62px 76px;transform:scale(var(--scale,1));transform-origin:center;overflow:hidden}.slide[hidden]{display:none}.slide h1{font-size:43px;line-height:1.15;font-weight:650;margin:0 0 38px;letter-spacing:-1px}.slide p{margin:24px 0}.lead{font-size:31px;line-height:1.35}.body{font-size:27px;line-height:1.42}.footnote{font-size:20px;line-height:1.4;color:#526559}.warning{font-size:23px;line-height:1.4;color:#8b3c1c;font-weight:600}.cover{background:#113e2b;color:#f6f8ef}.cover h1{font-size:84px;margin-top:10px;margin-bottom:14px}.subtitle{font-size:34px;max-width:800px}.intro{font-size:26px;margin-top:64px!important}.date{font-size:22px;color:#c4d7c4}.cover-note{font-size:23px;line-height:1.5;margin-top:62px!important;color:#dce9d9}.slide table{width:100%;border-collapse:collapse;margin:18px 0 30px;font-size:25px}.slide th{text-align:left;color:#205d40;border-bottom:2px solid #376a4d;padding:15px 12px}.slide td{padding:16px 12px;border-bottom:1px solid #c9d4c9}.slide li{font-size:28px;line-height:1.45;margin:20px 0;padding-left:10px}.slide ol{padding-left:32px}.pipeline li{margin:20px 0}.pipeline span{display:block;font-size:24px;color:#5b6a5e}.formula{font-family:Georgia,serif;font-size:32px;line-height:1.6;padding:22px 0}.stats{display:flex;gap:70px;margin:38px 0}.stats strong{display:block;font-size:74px;font-weight:600;color:#206844}.stats span{font-size:24px}.slide pre{font:23px/1.7 Consolas,monospace;white-space:pre-wrap;margin:32px 0 42px}.num{position:absolute;bottom:24px;right:35px;font-size:17px;color:#6c7d6f}.cover .num{color:#c4d7c4}nav{height:52px;display:flex;align-items:center;justify-content:center;gap:18px;color:#e7eee7;font-size:14px}button{background:transparent;color:inherit;border:1px solid #749381;padding:6px 14px;cursor:pointer;font:inherit}button:focus{outline:2px solid white}#notes{display:none;position:fixed;bottom:60px;left:5%;right:5%;background:#fff;color:#20352b;padding:26px;border:2px solid #36684c;font-size:20px;line-height:1.5;z-index:20}#notes.open{display:block}@media print{html,body{background:white}main{display:block;height:auto;overflow:visible}.slide,.slide[hidden]{display:block;transform:none!important;width:1280px;height:720px;break-after:page;print-color-adjust:exact;-webkit-print-color-adjust:exact}.slide:last-child{break-after:auto}nav,#notes{display:none!important}@page{size:1280px 720px;margin:0}}'''
sections=[]
for i,(title, content, note, theme) in enumerate(slides,1):
    sections.append(f'<section class="slide {theme}" aria-label="Slide {i}: {html.escape(title)}"'+(' hidden' if i>1 else '')+'><h1>'+html.escape(title)+'</h1>'+content+f'<span class="num">{i:02} / {len(slides):02}</span></section>')
js = '''const slides=[...document.querySelectorAll('.slide')];const notes=NOTES;let index=0;function resize(){document.documentElement.style.setProperty('--scale',Math.min(innerWidth/1280,(innerHeight-52)/720));}function show(i){index=Math.max(0,Math.min(slides.length-1,i));slides.forEach((s,j)=>s.hidden=j!==index);document.getElementById('counter').textContent=(index+1)+' / '+slides.length;document.getElementById('notes').textContent=notes[index];location.hash=String(index+1);}document.getElementById('prev').onclick=()=>show(index-1);document.getElementById('next').onclick=()=>show(index+1);document.getElementById('toggle').onclick=()=>document.getElementById('notes').classList.toggle('open');document.getElementById('full').onclick=()=>{if(!document.fullscreenElement)document.documentElement.requestFullscreen();else document.exitFullscreen();};document.getElementById('print').onclick=()=>window.print();addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();show(index+1);}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();show(index-1);}if(e.key==='Home')show(0);if(e.key==='End')show(slides.length-1);if(e.key.toLowerCase()==='n')document.getElementById('notes').classList.toggle('open');});addEventListener('resize',resize);show((parseInt(location.hash.slice(1))||1)-1);resize();'''.replace('NOTES',json.dumps([s[2] for s in slides]))
deck='<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Green TAC prototype review</title><style>'+css+'</style></head><body><main>'+''.join(sections)+'</main><nav><button id="prev">Previous</button><span id="counter"></span><button id="next">Next</button><button id="toggle">Notes</button><button id="full">Fullscreen</button><button id="print">Print</button><span>Arrow keys to navigate</span></nav><aside id="notes"></aside><script>'+js+'</script></body></html>'
(OUT/'presentation.html').write_text(deck,encoding='utf-8')
(OUT/'speaker_notes.md').write_text('# Green TAC presentation notes\n\n'+'\n\n'.join(f'## {i} {s[0]}\n\n{s[2]}' for i,s in enumerate(slides,1)),encoding='utf-8')
print(f'Built report, printable report, {len(slides)}-slide presentation and speaker notes in {OUT}')
