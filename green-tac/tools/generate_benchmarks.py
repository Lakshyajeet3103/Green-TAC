#!/usr/bin/env python3
"""Generate a deterministic benchmark corpus for Green TAC experiments."""
from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def write(path:Path, lines:list[str], category:str, seed:int, manifest):
    path.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    manifest.append({'program':str(path.relative_to(ROOT)).replace('\\','/'),'category':category,'seed':seed})


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--count',type=int,default=120); ap.add_argument('--seed',type=int,default=42); ap.add_argument('--out',default='benchmarks/generated'); args=ap.parse_args()
    rng=random.Random(args.seed)
    out=ROOT/args.out; out.mkdir(parents=True,exist_ok=True)
    manifest=[]
    per=max(1,args.count//5)
    for i in range(per):
        n=rng.randint(3,12)
        lines=[f'a = {rng.randint(1,20)};',f'b = {rng.randint(1,20)};']
        for j in range(n): lines.append(f'x{j} = x{j-1} + a;' if j else 'x0 = a + b;')
        lines.append(f'y = x{n-1} * 2;')
        write(out/f'arithmetic_{i:03d}.c',lines,'arithmetic',args.seed+i,manifest)

    for i in range(per):
        repeats=rng.randint(2,8); lines=['a = 3;','b = 5;']
        terms=[f'(a + b)' for _ in range(repeats)]
        lines.append(f'x = {" + ".join(terms)};')
        lines.append(f'y = (a + b) * {rng.randint(2,9)};')
        write(out/f'cse_{i:03d}.c',lines,'cse',args.seed+1000+i,manifest)

    for i in range(per):
        count=rng.randint(3,10); lines=[f'x = {rng.randint(1,20)};']
        for _ in range(count):
            a,b=rng.randint(2,50),rng.randint(2,50)
            lines.append(f'y = {a} * {b};')
            lines.append('z = y + 0;')
        write(out/f'constant_{i:03d}.c',lines,'constant',args.seed+2000+i,manifest)

    for i in range(per):
        limit=rng.randint(50,500); step=rng.randint(1,5)
        lines=[f'x = 0;',f'while (x < {limit}) {{',f'    x = x + {step};','}']
        write(out/f'loop_{i:03d}.c',lines,'loop',args.seed+3000+i,manifest)

    for i in range(per):
        v=rng.randint(1,30)
        lines=[f'a = {v};',f'b = {rng.randint(1,30)};', 'x = (a + b) * (a + b);', 'if (x > 20) {', '    y = x * 2;', '} else {', '    y = x + 1;', '}']
        write(out/f'mixed_{i:03d}.c',lines,'mixed',args.seed+4000+i,manifest)

    with (ROOT/'data/benchmark_manifest.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['program','category','seed']); w.writeheader(); w.writerows(manifest)
    print(f'Generated {len(manifest)} benchmarks in {out}')
    print(f'Manifest: {ROOT/"data/benchmark_manifest.csv"}')

if __name__=='__main__': main()
