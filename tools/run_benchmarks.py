#!/usr/bin/env python3
"""Run every benchmark/strategy combination, including generated benchmarks."""
from __future__ import annotations
import argparse, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--runs',type=int,default=50); ap.add_argument('--csv',default='data/measurements.csv'); ap.add_argument('--clean',action='store_true')
    args=ap.parse_args()
    if args.clean:
        p=ROOT/args.csv
        if p.exists(): p.unlink()
    files=sorted((ROOT/'benchmarks').rglob('*.c'))
    if not files: raise SystemExit('No benchmark files found')
    for src in files:
        rel=src.relative_to(ROOT).as_posix()
        for strategy in ('baseline','lightweight','dag'):
            cmd=[sys.executable,str(ROOT/'tools/measure.py'),'--source',rel,'--strategy',strategy,'--runs',str(args.runs),'--csv',args.csv]
            print('\nRUN', ' '.join(cmd), flush=True)
            subprocess.run(cmd,check=True,cwd=ROOT)
if __name__=='__main__': main()
