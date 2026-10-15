#!/usr/bin/env python3
"""Download an external electricity-carbon dataset without pretending it is compiler training data.

Default source: Ember India monthly electricity data (CC BY 4.0 on Ember's site).
Use --url for another compatible CSV source.
"""
from __future__ import annotations

import argparse
import urllib.request
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
EMBER_INDIA_MONTHLY=(
    'https://files.ember-energy.org/public-downloads/india_monthly_full_release_long_format.csv'
)


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--url',default=EMBER_INDIA_MONTHLY); ap.add_argument('--output',default='data/carbon/ember_india_monthly.csv'); args=ap.parse_args()
    out=ROOT/args.output; out.parent.mkdir(parents=True,exist_ok=True)
    print('Downloading:',args.url)
    with urllib.request.urlopen(args.url,timeout=60) as r:
        data=r.read()
    out.write_bytes(data)
    print('Saved:',out)
    print('Important: this is a grid carbon-intensity dataset. It does NOT train the code-energy model.')

if __name__=='__main__': main()
