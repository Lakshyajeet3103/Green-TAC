#!/usr/bin/env python3
"""Summarize measurements and produce a CSV of strategy rankings."""
from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd

ap=argparse.ArgumentParser(); ap.add_argument('csv'); ap.add_argument('--out',default='data/results/strategy_summary.csv'); args=ap.parse_args()
df=pd.read_csv(args.csv)
for col in ('compile_energy_j','runtime_energy_j','runtime_ms','compile_time_s'):
    if col in df: df[col]=pd.to_numeric(df[col],errors='coerce')

print('\n=== Median by strategy ===')
print(df.groupby('strategy')[['compile_energy_j','runtime_energy_j','runtime_ms','compile_time_s']].median(numeric_only=True).to_string())

usable=df.dropna(subset=['runtime_energy_j'])
if not usable.empty:
    best=usable.loc[usable.groupby('program')['runtime_energy_j'].idxmin(), ['program','category','strategy','runtime_energy_j','runtime_ms']]
    print('\n=== Best measured strategy per program (runtime energy) ===')
    print(best.to_string(index=False))
    out=Path(args.out); out.parent.mkdir(parents=True,exist_ok=True); best.to_csv(out,index=False)
    print(f'\nWrote: {out}')
else:
    print('\nNo physical runtime-energy measurements are present yet. Timing-only analysis is still possible.')
