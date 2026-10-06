#!/usr/bin/env python3
"""Friendly one-command runner for Green TAC."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BIN = ROOT / "bin" / ("green_tac.exe" if os.name == "nt" else "green_tac")


def ensure_built() -> None:
    if BIN.exists():
        return
    subprocess.run([sys.executable, str(ROOT / "build.py")], check=True, cwd=ROOT)


def run(cmd: list[str]) -> int:
    return subprocess.run(cmd, cwd=ROOT).returncode


def main() -> int:
    ap = argparse.ArgumentParser(description="Green TAC runner")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("build", help="Build the C++ compiler")
    sub.add_parser("test", help="Build and run tests")

    tac = sub.add_parser("tac", help="Generate TAC with one strategy")
    tac.add_argument("source")
    tac.add_argument("--strategy", choices=["baseline","lightweight","dag"], default="baseline")

    cmp = sub.add_parser("compare", help="Run all strategies and show formatted TAC comparison")
    cmp.add_argument("source")

    green = sub.add_parser("green", help="Run the carbon-aware selector")
    green.add_argument("source")
    green.add_argument("--model", default="data/model.csv")
    green.add_argument("--compile-ci", type=float, default=400.0)
    green.add_argument("--runtime-ci", type=float, default=400.0)
    green.add_argument("--executions", type=float, default=1000.0)
    green.add_argument("--max-runtime-overhead", type=float, default=0.10)

    gen_c = sub.add_parser("c", help="Generate C from one TAC strategy")
    gen_c.add_argument("source")
    gen_c.add_argument("--strategy", choices=["baseline","lightweight","dag"], default="baseline")
    gen_c.add_argument("--output", default="data/results/generated.c")

    info = sub.add_parser("info", help="Show environment/energy-provider status")
    demo = sub.add_parser("demo", help="Run the complete demo on a benchmark")
    demo.add_argument("source", nargs="?", default="benchmarks/cse.c")

    dataset = sub.add_parser("dataset", help="Generate a reproducible benchmark corpus")
    dataset.add_argument("--count", type=int, default=120)

    collect = sub.add_parser("collect", help="Collect timing/energy measurements for all benchmarks")
    collect.add_argument("--runs", type=int, default=50)
    collect.add_argument("--clean", action="store_true")

    analyze = sub.add_parser("analyze", help="Analyze a measurements CSV")
    analyze.add_argument("--csv", default="data/measurements.csv")

    plot = sub.add_parser("plot", help="Create research plots from measurements")
    plot.add_argument("--csv", default="data/measurements.csv")

    args = ap.parse_args()

    if args.cmd == "build":
        return run([sys.executable, str(ROOT / "build.py")])
    if args.cmd == "test":
        return run([sys.executable, str(ROOT / "build.py"), "test"])

    ensure_built()
    if args.cmd == "info":
        return run([str(BIN), "info"])
    if args.cmd == "demo":
        return run([str(BIN), "demo", args.source])
    if args.cmd == "dataset":
        return run([sys.executable, str(ROOT / "tools" / "generate_benchmarks.py"), "--count", str(args.count)])
    if args.cmd == "collect":
        cmd=[sys.executable, str(ROOT / "tools" / "run_benchmarks.py"), "--runs", str(args.runs)]
        if args.clean: cmd.append("--clean")
        return run(cmd)
    if args.cmd == "analyze":
        return run([sys.executable, str(ROOT / "tools" / "analyze_results.py"), args.csv])
    if args.cmd == "plot":
        return run([sys.executable, str(ROOT / "tools" / "plot_results.py"), args.csv])
    if args.cmd == "tac":
        return run([str(BIN), "tac", args.source, args.strategy])
    if args.cmd == "compare":
        return run([str(BIN), "compare", args.source])
    if args.cmd == "green":
        return run([str(BIN), "select", args.source, args.model, str(args.compile_ci), str(args.runtime_ci), str(args.executions), str(args.max_runtime_overhead)])
    if args.cmd == "c":
        return run([str(BIN), "c", args.source, args.strategy, args.output])
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
