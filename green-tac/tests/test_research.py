"""Checks for collected research evidence and Python/C++ model integration."""
import csv
import json
import math
import statistics
import subprocess
import unittest
from collections import defaultdict
from pathlib import Path

from tools.measure import DEFAULT_COMPILER, ROOT, FEATURES, parse_features


class ResearchEvidenceTests(unittest.TestCase):
    @unittest.skipUnless((ROOT / 'data/runtime_study/metadata.json').exists(), 'Run the runtime study first')
    def test_samples_match_measurements(self):
        meta = json.loads((ROOT / 'data/runtime_study/metadata.json').read_text())
        self.assertIn('completed_utc', meta)
        samples = defaultdict(list)
        with (ROOT / 'data/runtime_study/samples.csv').open() as f:
            for row in csv.DictReader(f):
                samples[row['program'], row['strategy']].append(float(row['runtime_ms']))
        with (ROOT / 'data/runtime_study/measurements.csv').open() as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), len(meta['programs']) * 3)
        for row in rows:
            values = samples[row['program'], row['strategy']]
            self.assertEqual(len(values), meta['samples'])
            self.assertAlmostEqual(statistics.median(values), float(row['runtime_ms']), places=12)
            self.assertEqual(row['runtime_energy_j'], '')
            self.assertEqual(row['compile_energy_j'], '')

    @unittest.skipUnless((ROOT / 'data/model_validation.json').exists(), 'Fit the model first')
    def test_no_program_leakage_and_no_energy_coefficients(self):
        validation = json.loads((ROOT / 'data/model_validation.json').read_text())
        holdouts = []
        for split in validation['splits']:
            self.assertFalse(set(split['train_programs']) & set(split['test_programs']))
            self.assertGreaterEqual(len(split['train_programs']), 16)
            holdouts.append(split['test_programs'])
        self.assertEqual(len(holdouts), 3)
        self.assertTrue(all(h == holdouts[0] for h in holdouts))
        with (ROOT / 'data/model.csv').open() as f:
            rows = list(csv.reader(f))[1:]
        self.assertEqual({row[1] for row in rows}, {'runtime_ms'})

    @unittest.skipUnless((ROOT / 'data/model_validation.json').exists(), 'Fit the model first')
    def test_exported_model_predictions_match_cpp(self):
        features = parse_features(subprocess.check_output(
            [str(DEFAULT_COMPILER), 'features', 'benchmarks/cse.c', '--machine'], cwd=ROOT, text=True))
        coefficients = defaultdict(dict)
        with (ROOT / 'data/model.csv').open() as f:
            for strategy, metric, feature, coefficient in list(csv.reader(f))[1:]:
                if metric == 'runtime_ms':
                    coefficients[strategy][feature] = float(coefficient)
        output = subprocess.check_output([str(DEFAULT_COMPILER), 'select', 'benchmarks/cse.c',
                                          'data/model.csv', '700', '200', '3', '0.1'], cwd=ROOT, text=True)
        checked = 0
        for line in output.splitlines():
            cells = [cell.strip() for cell in line.split('|')]
            if len(cells) == 8 and cells[1] in coefficients:
                coeff = coefficients[cells[1]]
                expected = max(0, coeff['intercept'] + sum(coeff[k] * features[k] for k in FEATURES))
                self.assertAlmostEqual(float(cells[4]), expected, delta=5.1e-10)
                checked += 1
        self.assertEqual(checked, 3)


if __name__ == '__main__':
    unittest.main()
