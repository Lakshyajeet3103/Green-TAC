#!/usr/bin/env python3
"""Measure timing and, when available, physical energy for one benchmark/strategy.

The generated native program executes the benchmark in-process `runs` times,
which avoids measuring process-startup cost on every run. Physical energy is
blank when no supported provider exists.
"""
from __future__ import annotations

import argparse, csv, glob, os, shutil, subprocess, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_COMPILER = ROOT / "bin" / ("green_tac.exe" if os.name == "nt" else "green_tac")


def rapl_path():
    for p in glob.glob('/sys/class/powercap/**/energy_uj', recursive=True): return p
    return None

def rapl_j(path):
    with open(path) as f: return float(f.read().strip()) / 1e6

def find_cc(preferred):
    if preferred: return preferred
    for name in ("gcc","cc","g++"):
        p=shutil.which(name)
        if p: return p
    raise SystemExit("No C compiler found. Install gcc/g++ or pass --cc.")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--compiler',default=str(DEFAULT_COMPILER))
    ap.add_argument('--source',required=True)
    ap.add_argument('--strategy',choices=['baseline','lightweight','dag'],required=True)
    ap.add_argument('--runs',type=int,default=50)
    ap.add_argument('--cc')
    ap.add_argument('--out-c',default='data/results/generated.c')
    ap.add_argument('--out-bin',default=None)
    ap.add_argument('--csv',default='data/measurements.csv')
    args=ap.parse_args()
    if args.runs < 2: raise SystemExit('--runs should be at least 2')

    compiler=Path(args.compiler)
    if not compiler.exists(): raise SystemExit(f"Compiler executable not found: {compiler}. Run: python build.py")
    out_c=ROOT/args.out_c; out_c.parent.mkdir(parents=True,exist_ok=True)
    suffix='.exe' if os.name=='nt' else ''
    out_bin=ROOT/(args.out_bin or f'data/results/{Path(args.source).stem}_{args.strategy}{suffix}')
    out_bin.parent.mkdir(parents=True,exist_ok=True)
    csv_path=ROOT/args.csv; csv_path.parent.mkdir(parents=True,exist_ok=True)
    cc=find_cc(args.cc); rp=rapl_path()

    e0=rapl_j(rp) if rp else None
    t0=time.perf_counter()
    subprocess.run([str(compiler),'c',args.source,args.strategy,str(out_c)],check=True,cwd=ROOT,stdout=subprocess.DEVNULL)
    compile_s=time.perf_counter()-t0
    e1=rapl_j(rp) if rp else None

    # Generate a C program whose main executes program() args.runs times.
    # Re-generate with the requested loop count so timing measures program work,
    # not repeated process creation.
    source_text=subprocess.check_output([str(compiler),'tac',args.source,args.strategy],text=True,cwd=ROOT)
    # Use the compiler's C command for correctness, then patch the generated main
    # loop to the requested count. This avoids adding another compiler API solely
    # for measurement.
    base_c=out_c.read_text(encoding='utf-8')
    marker='for (int i = 0; i < 1; ++i) rc |= program();'
    out_c.write_text(base_c.replace(marker, f'for (int i = 0; i < {args.runs}; ++i) rc |= program();'),encoding='utf-8')

    subprocess.run([cc,str(out_c),'-O0','-o',str(out_bin)],check=True,cwd=ROOT)
    e2=rapl_j(rp) if rp else None
    t0=time.perf_counter()
    subprocess.run([str(out_bin)],check=True,cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    runtime_s=time.perf_counter()-t0
    e3=rapl_j(rp) if rp else None

    compile_energy=(e1-e0) if (e0 is not None and e1 is not None) else None
    runtime_energy=(e3-e2) / args.runs if (e2 is not None and e3 is not None) else None
    feat_line=subprocess.check_output([str(compiler),'features',args.source],text=True,cwd=ROOT).strip()
    features={}
    for item in feat_line.splitlines():
        for token in item.split(','):
            if '=' in token:
                k,v=token.split('=',1); features[k]=float(v)
    header=['program','category','strategy','compile_time_s','compile_energy_j','runtime_ms','runtime_energy_j']+list(features.keys())
    row=[args.source,Path(args.source).stem.split('_')[0],args.strategy,compile_s,'' if compile_energy is None else compile_energy,(runtime_s*1000/args.runs),'' if runtime_energy is None else runtime_energy]+[features[k] for k in features]
    write_header=not csv_path.exists() or csv_path.stat().st_size==0
    with csv_path.open('a',newline='') as f:
        w=csv.writer(f)
        if write_header:w.writerow(header)
        w.writerow(row)

    print('\nMeasurement')
    print('-----------')
    print(f'Program            : {args.source}')
    print(f'Strategy           : {args.strategy}')
    print(f'Runs               : {args.runs} (inside one process)')
    print(f'Compile time       : {compile_s*1000:.3f} ms')
    print(f'Compile energy     : {"unavailable" if compile_energy is None else f"{compile_energy:.6f} J"}')
    print(f'Runtime per run    : {runtime_s*1000/args.runs:.6f} ms')
    print(f'Runtime energy     : {"unavailable" if runtime_energy is None else f"{runtime_energy:.6f} J"}')
    print(f'Energy provider    : {rp or "none"}')
    print(f'CSV                : {csv_path}')

if __name__=='__main__': main()
