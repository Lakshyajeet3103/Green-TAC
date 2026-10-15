#!/usr/bin/env python3
"""Fit scaled Ridge models with held-out program validation and raw coefficient export."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

FEATURES = ['instructions', 'binary_ops', 'branches', 'labels', 'temporaries',
            'memory_ops', 'comparisons', 'basic_blocks', 'max_expr_depth', 'common_subexpressions']
TARGETS = ['compile_energy_j', 'runtime_energy_j', 'runtime_ms']


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('measurements')
    ap.add_argument('output')
    ap.add_argument('--metrics-output', default='data/model_metrics.csv')
    ap.add_argument('--predictions-output', default='data/model_predictions.csv')
    ap.add_argument('--validation-output', default='data/model_validation.json')
    args = ap.parse_args()
    try:
        import numpy as np
        import sklearn
        from sklearn.linear_model import Ridge
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        from sklearn.model_selection import GroupShuffleSplit
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        raise SystemExit('Install tools/requirements.txt in the Python environment used for fitting.')
    with open(args.measurements, newline='') as f:
        reader = csv.DictReader(f)
        missing = set(FEATURES + TARGETS + ['program', 'strategy']) - set(reader.fieldnames or [])
        if missing:
            raise SystemExit('Measurement CSV is missing required columns: ' + ', '.join(sorted(missing)))
        rows = list(reader)
    if not rows:
        raise SystemExit('No measurements found')
    out, metrics, predictions, splits, skipped = [], [], [], [], []
    for strategy in ('baseline', 'lightweight', 'dag'):
        for metric in TARGETS:
            usable = []
            for row in rows:
                if row['strategy'] != strategy:
                    continue
                try:
                    y = float(row[metric]); x = [float(row[f]) for f in FEATURES]
                    if not row['program'] or not math.isfinite(y) or y < 0 or not all(math.isfinite(v) and v >= 0 for v in x):
                        continue
                except (TypeError, ValueError):
                    continue
                usable.append((row['program'], x, y))
            usable.sort(key=lambda item: item[0])
            programs = sorted({g for g, _, _ in usable})
            if len(programs) < 20:
                skipped.append({'strategy': strategy, 'metric': metric, 'unique_programs': len(programs), 'reason': 'requires at least 20 unique programs'})
                print(f'Skip {strategy}/{metric}: {len(programs)} usable programs (minimum 20).')
                continue
            X = np.array([x for _, x, _ in usable]); y = np.array([y for _, _, y in usable])
            groups = np.array([g for g, _, _ in usable])
            train, test = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42).split(X, y, groups))
            train_programs = sorted(set(groups[train])); test_programs = sorted(set(groups[test]))
            assert not set(train_programs) & set(test_programs)
            model = make_pipeline(StandardScaler(), Ridge(alpha=1.0)).fit(X[train], y[train])
            raw = model.predict(X[test]); pred = np.maximum(0, raw)
            truth = y[test]; reference = np.full(len(test), y[train].mean())
            mae = float(mean_absolute_error(truth, pred)); reference_mae = float(mean_absolute_error(truth, reference))
            metrics.append({'strategy': strategy, 'metric': metric, 'rows': len(y),
                            'unique_programs': len(programs), 'train_programs': len(train_programs),
                            'test_programs': len(test_programs), 'mae': mae,
                            'rmse': float(mean_squared_error(truth, pred) ** 0.5),
                            'r2': float(r2_score(truth, pred)), 'mean_reference_mae': reference_mae,
                            'beats_mean_reference': mae < reference_mae,
                            'clipped_predictions': int((raw < 0).sum())})
            for i, prediction, ref in zip(test, pred, reference):
                predictions.append({'program': groups[i], 'strategy': strategy, 'metric': metric,
                                    'measured': y[i], 'predicted': prediction, 'mean_reference': ref})
            splits.append({'strategy': strategy, 'metric': metric, 'train_programs': train_programs, 'test_programs': test_programs})
            final = make_pipeline(StandardScaler(), Ridge(alpha=1.0)).fit(X, y)
            scaler = final.named_steps['standardscaler']; linear = final.named_steps['ridge']
            coefficients = linear.coef_ / scaler.scale_
            intercept = float(linear.intercept_ - np.dot(coefficients, scaler.mean_))
            assert np.allclose(final.predict(X), X @ coefficients + intercept)
            output_metric = metric.removesuffix('_j')
            out.append((strategy, output_metric, 'intercept', intercept))
            out.extend((strategy, output_metric, f, float(c)) for f, c in zip(FEATURES, coefficients))
    if not out:
        raise SystemExit('No model could be fitted; existing model files were not changed.')
    for path in (args.output, args.metrics_output, args.predictions_output, args.validation_output):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', newline='') as f:
        writer = csv.writer(f); writer.writerow(['# strategy', 'metric', 'feature', 'coefficient']); writer.writerows(out)
    for path, records in ((args.metrics_output, metrics), (args.predictions_output, predictions)):
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(records[0])); writer.writeheader(); writer.writerows(records)
    validation = {'source': args.measurements, 'source_sha256': hashlib.sha256(Path(args.measurements).read_bytes()).hexdigest(),
                  'sklearn_version': sklearn.__version__, 'model': 'StandardScaler then Ridge alpha=1',
                  'split': 'GroupShuffleSplit by program, test_size=0.2, random_state=42',
                  'validation_predictions': 'Clipped at zero, matching C++ selector',
                  'export': 'Refit on all usable rows; raw-feature coefficients. Held-out metrics use training-only models.',
                  'limitations': ['Synthetic programs may share templates across splits.',
                                 'A single small holdout does not establish generalization to real applications.',
                                 'Runtime constraint checks are predictions, not guarantees.'],
                  'splits': splits, 'skipped': skipped}
    Path(args.validation_output).write_text(json.dumps(validation, indent=2))
    for item in metrics:
        print(f"{item['strategy']}/{item['metric']}: MAE={item['mae']:.8g}, RMSE={item['rmse']:.8g}, R2={item['r2']:.4f}, beats mean={item['beats_mean_reference']}")
    print(f'Wrote model: {args.output}')


if __name__ == '__main__':
    main()
