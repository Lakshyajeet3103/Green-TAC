#!/usr/bin/env python3
"""Build Green TAC without CMake/Ninja/Make.

Usage:
  python build.py
  python build.py test
  python build.py clean
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
INCLUDE = ROOT / "include"
TEST_SRC = ROOT / "tests" / "test_main.cpp"
BIN = ROOT / "bin"


def find_compiler() -> str:
    candidates = ["g++", "c++", "clang++"]
    for name in candidates:
        path = shutil.which(name)
        if path:
            return path
    raise SystemExit("C++ compiler not found. Install/activate g++ and make sure it is on PATH.")


def run(cmd: list[str]) -> None:
    print("[BUILD]", " ".join(cmd))
    subprocess.run(cmd, check=True, cwd=ROOT)


def main() -> int:
    ap = argparse.ArgumentParser(description="Build Green TAC with a C++ compiler only.")
    ap.add_argument("action", nargs="?", choices=["build", "test", "clean"], default="build")
    args = ap.parse_args()

    if args.action == "clean":
        shutil.rmtree(BIN, ignore_errors=True)
        return 0

    compiler = find_compiler()
    BIN.mkdir(parents=True, exist_ok=True)

    common = [compiler, "-std=c++17", "-O2", "-Wall", "-Wextra", "-pedantic", f"-I{INCLUDE}"]
    sources = sorted(str(p) for p in SRC.glob("*.cpp"))
    if not sources:
        raise SystemExit("No C++ source files found in src/")

    exe = BIN / ("green_tac.exe" if os.name == "nt" else "green_tac")
    run(common + sources + ["-o", str(exe)])

    if args.action == "test":
        test_exe = BIN / ("greentac_tests.exe" if os.name == "nt" else "greentac_tests")
        run(common + [str(TEST_SRC)] + [str(p) for p in sources if p.endswith(".cpp") and not p.endswith("main.cpp")] + ["-o", str(test_exe)])
        run([str(test_exe)])

    print(f"\nBuilt: {exe}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
