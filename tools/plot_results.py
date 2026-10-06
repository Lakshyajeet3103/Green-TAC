#!/usr/bin/env python3
"""Create simple research plots from measurements.csv."""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ap=argparse.ArgumentParser(); ap.add_argument('csv',default='data/measurements.csv',nargs='?'); ap.add_argument('--out-dir',default='data/results'); args=ap.parse_args()
df=pd.read_csv(args.csv)
out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
for c in ('runtime_ms','runtime_energy_j','compile_energy_j'):
    if c in df: df[c]=pd.to_numeric(df[c],errors='coerce')

if 'runtime_ms' in df:
    ax=df.groupby('strategy')['runtime_ms'].median().plot(kind='bar',title='Median Runtime by Strategy',ylabel='ms per run',xlabel='')
    fig=ax.get_figure(); fig.tight_layout(); fig.savefig(out/'median_runtime.png',dpi=180); plt.close(fig)

if 'runtime_energy_j' in df and df['runtime_energy_j'].notna().any():
    ax=df.groupby('strategy')['runtime_energy_j'].median().plot(kind='bar',title='Median Runtime Energy by Strategy',ylabel='J per run',xlabel='')
    fig=ax.get_figure(); fig.tight_layout(); fig.savefig(out/'median_runtime_energy.png',dpi=180); plt.close(fig)

print(f'Plots written to {out}')
