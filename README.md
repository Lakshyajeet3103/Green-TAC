# Green TAC

Carbon-aware Three-Address Code generation and optimization for a small C-like language.
The compiler is written in C++17. Python drives builds, tests and research tooling.

## Setup and run

Install Python 3.10+ and a C++17 compiler (`g++`, `c++` or `clang++`) on your PATH.
The basic compiler needs no third-party Python packages.

```powershell
git clone https://github.com/Lakshyajeet3103/Green-TAC.git
cd Green-TAC/green-tac
python build.py
python run.py test
python -m unittest discover -s tests -p "test_*.py"
python run.py steps benchmarks/cse.c
```

Using a ZIP? Extract it, enter `Green-TAC-main/green-tac`, then run the build
and demo commands above. Git is not required. See the [ZIP setup steps](SETUP.md#option-a-zip-download-no-git-required).

For Windows compiler installation, Linux/macOS setup, optional analysis packages
and troubleshooting, follow the [step-by-step setup guide](SETUP.md).
All `build.py` and `run.py` commands run from the `green-tac/` directory.

## Two complete examples

```powershell
# Nested Boolean if/else with short-circuit evaluation
python run.py steps benchmarks/cse.c

# Constant folding, algebraic simplification, copy propagation, CSE and a while loop
python run.py steps benchmarks/optimization_showcase.c
python run.py compare benchmarks/optimization_showcase.c

# Carbon-aware decision for the optimization example
python run.py green benchmarks/optimization_showcase.c --compile-ci 700 --runtime-ci 200 --executions 10000
```

The Boolean example retains 22 TAC instructions. The optimization example reduces
30 instructions to 27 and binary operations from 13 to 6 under DAG/CSE.
These are static compiler-output counts. Energy and carbon currently use labeled
proxy estimates where physical energy models are unavailable.

## Supported language

- Integer arithmetic: `+`, `-`, `*`, `/`, `%`, and parentheses
- Assignments and comparisons: `<`, `<=`, `>`, `>=`, `==`, `!=`
- Boolean expressions: `&&`, `||`, `!`, `true`, `false`, with short-circuit evaluation
- `if`, `if/else`, `else if`, `while`, and nested bodies enclosed in braces

The compiler accepts this small language, rather than arbitrary C programs.
`for`, `do/while`, `break`, and `continue` are not implemented.

## Documentation

- [Detailed project README and command reference](green-tac/README.md)
- [Setup guide](SETUP.md)
- [Research workflow](green-tac/RESEARCH_WORKFLOW.md)
- [Project specification](green-tac/PROJECT_SPEC.md)
- [Project manuscript](manuscript/Green_TAC_Manuscript.docx)
- [Final presentation with both complete walkthroughs](output/Green-TAC%20Final%20Presentation%20-%20Two%20Examples.pptx)
