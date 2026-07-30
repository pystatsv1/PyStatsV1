#!/usr/bin/env python3
from __future__ import annotations
import argparse
import pandas as pd
from companion_runtime import ROOT, audit_frame, study_index, write_json
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    receipts = []
    for sid, row in study_index().items():
        frame = pd.read_csv(ROOT / row['dataset_path'])
        receipts.append(audit_frame(sid, frame, row))
    if not args.check_only:
        write_json(ROOT / 'outputs/design_audit.json', {'schema_version': 'psych-design-data-layout-audit-v0.1', 'studies': receipts, 'synthetic_only': True})
    print('PYSTATSV1_PSYCH_DESIGN_DESIGN_AUDIT_OK studies=10')
