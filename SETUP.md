# Green TAC setup guide

## 1. Install the tools

Use Python 3.10 or later and a C++17 compiler. Git is optional and is needed
only if you choose to clone the repository instead of extracting a ZIP.
The core build and demo use only the Python standard library. A C compiler is needed only to compile emitted
C or run native benchmark measurements.

### Windows with PowerShell

1. Install [Python](https://www.python.org/downloads/windows/) and ensure `python`
   works in a new terminal. See the [official Windows Python guide](https://docs.python.org/3/using/windows.html)
   if your installation uses the `py` launcher instead. You can substitute `py`
   for `python` in the commands below.
2. If you plan to clone rather than use a ZIP, install
   [Git for Windows](https://git-scm.com/download/win). ZIP users can skip this.
3. Install [MSYS2](https://www.msys2.org/) and open its **UCRT64** terminal.
   Install GCC there:

   ```bash
   pacman -S --needed mingw-w64-ucrt-x86_64-gcc
   ```

4. Open PowerShell. For a default MSYS2 installation, make the compiler available
   in the current terminal:

   ```powershell
   $env:Path = "C:\msys64\ucrt64\bin;" + $env:Path
   python --version
   g++ --version
   ```

   If you already use MSYS2 MINGW64, use `C:\msys64\mingw64\bin` instead.
   Use the compiler directory that actually exists on your machine. To avoid
   repeating the PATH command, add that directory to your user PATH in Windows
   Environment Variables and open a new terminal. GCC's runtime DLLs must stay
   available on PATH when running the generated executables.

The GCC package and UCRT64 environment follow the [official MSYS2 setup instructions](https://www.msys2.org/).

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install git python3 python3-venv g++ gcc
python3 --version
g++ --version
```

Use `python3` in place of `python` in the following steps if your system does not
provide the `python` command.

### macOS

Install Git and the Apple C/C++ command-line tools:

```bash
xcode-select --install
```

Install Python 3.10+ from [python.org](https://www.python.org/downloads/macos/).
Check `python3 --version` and `clang++ --version`, then use `python3` below.
The build script detects `c++` or `clang++` when `g++` is unavailable.

## 2. Extract the ZIP or clone the repository

### Option A: ZIP download (no Git required)

1. On the [GitHub repository](https://github.com/Lakshyajeet3103/Green-TAC),
   select the `main` branch, then **Code > Download ZIP**. If someone gives you
   the ZIP directly, use that file instead.
2. Extract the complete ZIP to a normal folder. Run the project from the
   extracted folder, rather than from inside the compressed ZIP viewer.
3. Open a terminal in the extracted folder. A GitHub download usually creates
   a folder named `Green-TAC-main`. From its parent directory, run:

   ```powershell
   cd Green-TAC-main/green-tac
   python build.py
   python run.py test
   python -m unittest discover -s tests -p "test_*.py"
   python run.py steps benchmarks/cse.c
   python run.py steps benchmarks/optimization_showcase.c
   ```

   If your terminal is already inside `Green-TAC-main`, run `cd green-tac`
   first. If the ZIP has a different folder name, use that name instead.

**Rebuild on the recipient's computer** with `python build.py`, even if the ZIP
already contains an executable. Python and a C++17 compiler must be installed
and available on PATH. These examples need no extra Python packages.
For Windows compiler installation and its PATH command, see step 1 above.

### Option B: Git clone

```powershell
git clone https://github.com/Lakshyajeet3103/Green-TAC.git
cd Green-TAC/green-tac
```

If you already cloned the repository, enter its existing `green-tac` directory.
This directory contains `build.py`, `run.py`, `src/`, and `benchmarks/`.

## 3. Build and verify

```powershell
python build.py
python run.py test
python -m unittest discover -s tests -p "test_*.py"
```

The executable is `bin/green_tac.exe` on Windows and `bin/green_tac` on Linux/macOS.
The C++ tests print `All tests passed.` Python tests finish with `OK` (some
research-evidence tests may skip when their optional data files are absent).
Always build after extracting a ZIP, cloning, or changing C++ source. `run.py` automatically builds
only when the executable is absent, not when its sources change.

## 4. Run both presentation examples

### Example 1: nested Boolean if/else

```powershell
python run.py steps benchmarks/cse.c
python run.py compare benchmarks/cse.c
```

The walkthrough shows source, tokens, AST, baseline TAC, lightweight rewrites,
DAG/CSE trace, final TAC and the before/after comparison. The current example
retains **22 instructions** because it has no repeated arithmetic work to remove.

### Example 2: optimization and a while loop

```powershell
python run.py steps benchmarks/optimization_showcase.c
python run.py compare benchmarks/optimization_showcase.c
python run.py green benchmarks/optimization_showcase.c --compile-ci 700 --runtime-ci 200 --executions 10000
```

DAG/CSE reduces **30 instructions to 27** and **13 binary operations to 6**.
The trace also shows constant folding, copy propagation and algebraic simplification.
Energy and CO2e output includes proxy estimates and must not be reported as
measured savings. The fitted runtime model has poor documented holdout accuracy.

For the fixed historical selection scenarios:

```powershell
python run.py adaptive-demo
```

Those scenarios use `benchmarks/adaptive_reference.c`, independently of edits to
`benchmarks/cse.c`.

## 5. Edit your own input

Save a file such as `benchmarks/my_example.c`, then run:

```powershell
python run.py steps benchmarks/my_example.c
python run.py tac benchmarks/my_example.c --strategy dag
```

The `.c` inputs use the project's small language. No `main()` or variable
declarations are needed. `if`/`else` and `while` bodies require braces. Save your
editor buffer before running. Editing an input does not require rebuilding the
compiler. The walkthrough's `0. Source` section shows the exact saved input read.

This is a TAC generator. Its normal output describes code and compiler stages,
rather than printing the numerical value of every source variable.

## 6. Optional research environment

Only analysis, model fitting and plots need the extra packages:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r tools/requirements.txt
.\.venv\Scripts\python.exe run.py analyze
.\.venv\Scripts\python.exe run.py plot
```

On Linux/macOS use `.venv/bin/python` instead of `.\.venv\Scripts\python.exe`.
The analysis commands require a measurements CSV. See the
[research workflow](green-tac/RESEARCH_WORKFLOW.md) for collecting one.

## Troubleshooting

| Symptom | Check or fix |
|---|---|
| `python` is not recognized | Reopen the terminal after installation, or try `py` on Windows / `python3` on Linux/macOS. |
| `C++ compiler not found` | Run `g++ --version` or `clang++ --version` in the same terminal and correct PATH. |
| Missing MinGW DLL or executable exits immediately | Keep the matching MSYS2 `ucrt64/bin` or `mingw64/bin` on PATH, then rebuild. |
| `can't open file build.py` | Run `cd Green-TAC/green-tac` from the clone's parent, or `cd green-tac` from its root. |
| Old source appears in the output | Save the editor file, verify `Get-Content benchmarks/cse.c` in PowerShell, and rerun `steps`. |
| New compiler features are not recognized | Run `python build.py` to replace the existing binary, then rerun the command. |
| No reduction in TAC instruction count | A valid result when there is no applicable reuse. Try `benchmarks/optimization_showcase.c`. |
| Energy measurements are blank on Windows | Physical RAPL energy measurement is unavailable there. Timing still works and proxy estimates are labeled. |
