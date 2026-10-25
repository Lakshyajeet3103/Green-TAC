"""Regression checks for the compiler-to-measurement feature contract.

Run after building: python -m unittest discover -s tests -p test_measure.py
"""
import csv
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.measure import DEFAULT_COMPILER, FEATURES, HEADER, ROOT, parse_features, validate_csv_header


class FeatureCollectionTests(unittest.TestCase):
    def test_compiler_exports_all_features(self):
        # Keep expected feature counts independent of the editable demo.
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'features.c'
            source.write_text(
                'a = 10 + 20; b = a * 1; c = b + 0; '
                'd = (x + y) * (x + y); e = (x + y) + (x + y); '
                'f = 5 * 6; g = d + f; h = (x + y) * 1;')
            output = subprocess.check_output(
                [str(DEFAULT_COMPILER), 'features', str(source), '--machine'],
                cwd=ROOT, text=True)
        features = parse_features(output)
        self.assertEqual(set(features), set(FEATURES))
        self.assertEqual(features['instructions'], 21)
        self.assertEqual(features['binary_ops'], 13)
        self.assertEqual(features['memory_ops'], 8)
        self.assertEqual(features['comparisons'], 0)

    def test_rejects_missing_or_malformed_features(self):
        valid = '\n'.join(f'{name}=1' for name in FEATURES)
        for output in ('', '  Instructions 21', valid.replace('instructions=1', ''),
                       valid + '\ninstructions=2', valid.replace('instructions=1', 'instructions=nan'),
                       valid.replace('instructions=1', 'instructions=-1')):
            with self.subTest(output=output), self.assertRaises(ValueError):
                parse_features(output)

    def test_rejects_legacy_csv_without_changing_it(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'measurements.csv'
            path.write_text('program,strategy,runtime_ms\nexample,baseline,1\n')
            original = path.read_bytes()
            with self.assertRaises(ValueError):
                validate_csv_header(path)
            self.assertEqual(path.read_bytes(), original)
            with path.open('w', newline='') as f:
                csv.writer(f).writerow(HEADER)
            validate_csv_header(path)


if __name__ == '__main__':
    unittest.main()
