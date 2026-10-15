#!/usr/bin/env python3
"""Collect a balanced timing-only study using timers inside generated native code.

No energy is inferred from time. Existing measurements are never overwritten.
The reported runtime is the median of repeated batch times per invocation at -O0.
"""
import argparse
import csv
import hashlib
import json
import platform
import random
import statistics
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from measure import DEFAULT_COMPILER, FEATURES, HEADER, ROOT, find_cc, parse_features

HARNESS = r'''
#ifdef _WIN32
#include <windows.h>
static double now_s(void) {
    LARGE_INTEGER t, f;
    QueryPerformanceCounter(&t);
    QueryPerformanceFrequency(&f);
    return (double)t.QuadPart / (double)f.QuadPart;
}
#else
#include <time.h>
static double now_s(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}
#endif
static volatile int sink = 0;
int main(void) {
    for (int i = 0; i < 10; ++i) sink |= program();
    unsigned long long runs = 50;
    double elapsed = 0;
    do {
        double start = now_s();
        for (unsigned long long i = 0; i < runs; ++i) sink |= program();
        elapsed = now_s() - start;
        if (elapsed >= MIN_SECONDS || runs >= 100000000ULL) break;
        runs *= 2;
    } while (1);
    for (int sample = 0; sample < SAMPLE_COUNT; ++sample) {
        double start = now_s();
        for (unsigned long long i = 0; i < runs; ++i) sink |= program();
        elapsed = now_s() - start;
        printf("%llu,%.12g\n", runs, elapsed * 1000.0 / (double)runs);
    }
    return sink;
}
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--per-category', type=int, default=6)
    ap.add_argument('--samples', type=int, default=5)
    ap.add_argument('--min-batch-ms', type=float, default=30)
    ap.add_argument('--out', default='data/runtime_study')
    args = ap.parse_args()
    if args.per_category < 4 or args.samples < 3 or args.min_batch_ms <= 0:
        raise SystemExit('Use at least 4 programs/category, 3 samples, and a positive batch duration.')
    out = ROOT / args.out
    out.mkdir(parents=True, exist_ok=True)
    csv_path = out / 'measurements.csv'
    if csv_path.exists():
        raise SystemExit(f'{csv_path} already exists. Use a new --out directory.')
    cc = find_cc(None)
    categories = ('arithmetic', 'constant', 'cse', 'loop', 'mixed')
    programs = []
    rng = random.Random(42)
    for category in categories:
        candidates = sorted((ROOT / 'benchmarks/generated').glob(f'{category}_*.c'))
        if len(candidates) < args.per_category:
            raise SystemExit(f'Not enough {category} programs.')
        programs.extend(rng.sample(candidates, args.per_category))
    programs.append(ROOT / 'benchmarks/cse.c')
    jobs = [(p, s) for p in programs for s in ('baseline', 'lightweight', 'dag')]
    rng.shuffle(jobs)
    metadata = {
        'started_utc': datetime.now(timezone.utc).isoformat(),
        'os': platform.platform(), 'machine': platform.machine(),
        'processor': platform.processor(), 'python': sys.version,
        'cc': cc, 'cc_version': subprocess.check_output([cc, '--version'], text=True).splitlines()[0],
        'native_flags': ['-O0'], 'timer': 'QueryPerformanceCounter' if sys.platform == 'win32' else 'CLOCK_MONOTONIC',
        'runtime_definition': 'median in-process batch milliseconds per invocation; includes call/loop/sink overhead',
        'compile_definition': 'Green TAC source-to-C invocation wall time; excludes downstream native compiler',
        'energy_provider': 'not used; energy calibration pending',
        'samples': args.samples, 'minimum_batch_ms': args.min_batch_ms,
        'warmup_invocations': 10, 'seed': 42,
        'compiler_sha256': hashlib.sha256(DEFAULT_COMPILER.read_bytes()).hexdigest(),
        'programs': {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in programs},
    }
    (out / 'metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    import time
    with csv_path.open('w', newline='') as f, (out / 'samples.csv').open('w', newline='') as sf:
        writer = csv.writer(f); writer.writerow(HEADER)
        samples_writer = csv.writer(sf)
        samples_writer.writerow(['program', 'strategy', 'sample', 'batch_runs', 'runtime_ms'])
        for index, (source, strategy) in enumerate(jobs, 1):
            rel = source.relative_to(ROOT).as_posix()
            features = parse_features(subprocess.check_output(
                [str(DEFAULT_COMPILER), 'features', rel, '--machine'], cwd=ROOT, text=True))
            cfile = out / f'{source.stem}_{strategy}.c'
            binary = cfile.with_suffix('.exe' if sys.platform == 'win32' else '.bin')
            start = time.perf_counter()
            subprocess.run([str(DEFAULT_COMPILER), 'c', rel, strategy, str(cfile)],
                           check=True, cwd=ROOT, stdout=subprocess.DEVNULL)
            compile_s = time.perf_counter() - start
            text = cfile.read_text()
            if text.count('int main(void){') != 1:
                raise RuntimeError('Unexpected generated C main function')
            harness = HARNESS.replace('MIN_SECONDS', repr(args.min_batch_ms / 1000)).replace('SAMPLE_COUNT', str(args.samples))
            cfile.write_text(text.split('int main(void){')[0] + harness)
            subprocess.run([cc, str(cfile), '-O0', '-o', str(binary)], check=True, cwd=ROOT)
            raw = subprocess.check_output([str(binary)], text=True, timeout=120)
            values = []
            for sample, line in enumerate(raw.splitlines(), 1):
                runs, value = line.split(','); values.append(float(value))
                samples_writer.writerow([rel, strategy, sample, runs, value])
            if len(values) != args.samples or not all(v > 0 for v in values):
                raise RuntimeError('Invalid internal timings')
            writer.writerow([rel, source.stem.split('_')[0], strategy, compile_s, '',
                             statistics.median(values), ''] + [features[k] for k in FEATURES])
            f.flush(); sf.flush()
            print(f'{index}/{len(jobs)} {rel} {strategy}: {statistics.median(values):.8f} ms', flush=True)
    metadata['completed_utc'] = datetime.now(timezone.utc).isoformat()
    metadata['measurement_sha256'] = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    (out / 'metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
