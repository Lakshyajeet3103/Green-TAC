#!/usr/bin/env python3
"""Run reproducible carbon/usage scenarios through the actual C++ selector."""
import csv
import json
import re
import subprocess
from pathlib import Path

from measure import DEFAULT_COMPILER, ROOT

SCENARIOS = [
    ('One execution', 1, 700, 200),
    ('Three executions', 3, 700, 200),
    ('Ten executions', 10, 700, 200),
    ('Cleaner compilation', 1, 200, 200),
    ('Dirtier execution', 1, 700, 700),
    ('Clean compile dirty runtime', 1, 200, 700),
    ('Equal low intensity', 1, 200, 200),
    ('Equal high intensity', 1, 700, 700),
]


def main():
    out = ROOT / 'data/results/adaptive'
    out.mkdir(parents=True, exist_ok=True)
    evidence, records = [], []
    for mode, model in [('runtime_fit_energy_proxy', 'data/model.csv'),
                        ('all_proxy_mechanism_demo', 'data/proxy_only_model.csv')]:
        for index, (label, runs, compile_ci, runtime_ci) in enumerate(SCENARIOS):
            args = ['select', 'benchmarks/cse.c', model, str(compile_ci), str(runtime_ci), str(runs), '0.10']
            output = subprocess.check_output([str(DEFAULT_COMPILER)] + args, cwd=ROOT, text=True)
            (out / f'{mode}_{index+1:02}.txt').write_text(output, encoding='utf-8')
            selected = re.search(r'Selected strategy\s*:\s*(\w+)', output).group(1)
            candidates = []
            for line in output.splitlines():
                parts = [p.strip() for p in line.split('|')]
                if len(parts) == 8 and parts[1] in ('baseline', 'lightweight', 'dag'):
                    candidates.append({'strategy': parts[1], 'compile_energy_proxy': float(parts[2]),
                                       'runtime_energy_proxy': float(parts[3]), 'runtime_ms': float(parts[4]),
                                       'carbon_proxy_g': float(parts[5]), 'allowed': parts[6] == 'yes'})
            assert len(candidates) == 3
            assert next(c for c in candidates if c['strategy'] == selected)['allowed']
            record = {'mode': mode, 'scenario': label, 'executions': runs, 'compile_ci': compile_ci,
                      'runtime_ci': runtime_ci, 'selected': selected, 'energy_status': 'PROXY NOT MEASURED'}
            records.append(record)
            evidence.append(dict(record, candidates=candidates, command='bin/green_tac ' + ' '.join(args)))
    proxy = [r for r in records if r['mode'] == 'all_proxy_mechanism_demo']
    assert [r['selected'] for r in proxy[:3]] == ['baseline', 'lightweight', 'dag']
    assert proxy[3]['selected'] == proxy[4]['selected'] == 'lightweight'
    assert proxy[5]['selected'] == 'dag'
    assert proxy[6]['selected'] == proxy[7]['selected']
    with (out / 'scenarios.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0])); writer.writeheader(); writer.writerows(records)
    (out / 'scenarios.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    print('All scenarios executed. Energy/CO2e are proxy estimates, not measured savings.')
    for r in records:
        print(f"{r['mode']}: {r['scenario']} -> {r['selected']}")


if __name__ == '__main__':
    main()
