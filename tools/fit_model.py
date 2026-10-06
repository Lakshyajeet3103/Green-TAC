#!/usr/bin/env python3
"""Fit empirical cost models with benchmark-level train/test validation."""
from __future__ import annotations
import argparse,csv,math,sys
from pathlib import Path
FEATURES=["instructions","binary_ops","branches","labels","temporaries","memory_ops","comparisons","basic_blocks","max_expr_depth","common_subexpressions"]
TARGETS=["compile_energy_j","runtime_energy_j","runtime_ms"]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('measurements'); ap.add_argument('output'); ap.add_argument('--metrics-output',default='data/model_metrics.csv'); args=ap.parse_args()
    try:
        import numpy as np
        from sklearn.linear_model import Ridge
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        from sklearn.model_selection import GroupShuffleSplit
    except ImportError: raise SystemExit('Install: pip install -r tools/requirements.txt')
    with open(args.measurements,newline='') as f: rows=list(csv.DictReader(f))
    if not rows: raise SystemExit('No measurements found')
    out=[]; metric_rows=[]
    strategies=sorted(set(r['strategy'] for r in rows))
    for strategy in strategies:
        rr=[r for r in rows if r['strategy']==strategy]
        for metric in TARGETS:
            usable=[]
            for r in rr:
                try:
                    y=float(r[metric]); X=[float(r.get(f,0) or 0) for f in FEATURES]
                    if not math.isfinite(y): continue
                except (TypeError,ValueError): continue
                usable.append((r.get('program', ''),X,y))
            unique_programs=sorted(set(g for g,_,_ in usable))
            if len(unique_programs)<20:
                print(f'skip {strategy}/{metric}: need at least 20 unique programs, got {len(unique_programs)}',file=sys.stderr); continue
            X=np.array([x for _,x,_ in usable],dtype=float); y=np.array([y for _,_,y in usable],dtype=float); groups=np.array([g for g,_,_ in usable])
            splitter=GroupShuffleSplit(n_splits=1,test_size=0.2,random_state=42)
            train_idx,test_idx=next(splitter.split(X,y,groups))
            model=Ridge(alpha=1.0).fit(X[train_idx],y[train_idx])
            pred=model.predict(X[test_idx]); truth=y[test_idx]
            metric_rows.append({'strategy':strategy,'metric':metric,'rows':len(y),'unique_programs':len(unique_programs),'test_programs':len(set(groups[test_idx])),'mae':float(mean_absolute_error(truth,pred)),'rmse':float(mean_squared_error(truth,pred)**0.5),'r2':float(r2_score(truth,pred)) if len(truth)>=2 else float('nan')})
            # Final production coefficients use all available real measurements.
            final=Ridge(alpha=1.0).fit(X,y)
            output_metric=metric.removesuffix('_j') if metric.endswith('_j') else metric
            out.append((strategy,output_metric,'intercept',float(final.intercept_)))
            for f,c in zip(FEATURES,final.coef_): out.append((strategy,output_metric,f,float(c)))
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    with open(args.output,'w',newline='') as f:
        w=csv.writer(f); w.writerow(['# strategy','metric','feature','coefficient']); w.writerows(out)
    with open(args.metrics_output,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['strategy','metric','rows','unique_programs','test_programs','mae','rmse','r2']); w.writeheader(); w.writerows(metric_rows)
    print(f'Wrote calibrated model: {args.output}'); print(f'Wrote validation metrics: {args.metrics_output}')
if __name__=='__main__': main()
