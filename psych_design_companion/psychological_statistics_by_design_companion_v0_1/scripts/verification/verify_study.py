#!/usr/bin/env python3
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
PYTHON_SCRIPTS = Path(__file__).resolve().parents[1] / 'python'
if str(PYTHON_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PYTHON_SCRIPTS))
from companion_runtime import (  # noqa: E402
    ROOT,
    normalize_study_id,
    read_r_metrics,
    sha256,
    study_index,
    write_json,
)

def verify(study_id: str):
    sid = normalize_study_id(study_id)
    row = study_index()[sid]
    slug = sid.lower().replace('-', '_')
    out = ROOT / 'outputs' / slug
    py_path = out / 'python_result.json'
    r_path = out / 'r_result.csv'
    if not py_path.is_file():
        raise SystemExit(f'missing Python result: {py_path}')
    if not r_path.is_file():
        raise SystemExit(f'missing independent R result: {r_path}')
    py = json.loads(py_path.read_text(encoding='utf-8'))['reported_fields']
    r = read_r_metrics(r_path)
    policy = json.loads((ROOT / 'VERIFICATION_POLICY.json').read_text(encoding='utf-8'))
    p = next((x for x in policy['studies'] if x['study_id'] == sid))
    rows = []
    failures = []
    for field in p['parity_fields']:
        if field not in py or field not in r:
            failures.append(f'missing field {field}')
            continue
        tolerance = float(p.get('absolute_tolerance_by_field', {}).get(field, p['default_absolute_tolerance']))
        difference = abs(float(py[field]) - float(r[field]))
        passed = difference <= tolerance
        rows.append({'field': field, 'python': float(py[field]), 'r': float(r[field]), 'absolute_difference': difference, 'allowed_absolute_difference': tolerance, 'status': 'pass' if passed else 'fail'})
        if not passed:
            failures.append(f'{field}: difference={difference} allowed={tolerance}')
    payload = {'schema_version': 'psych-design-verification-receipt-v0.1', 'study_id': sid, 'verification_category': row['verification_category'], 'status': 'fail' if failures else 'pass', 'comparisons': rows, 'python_result_sha256': sha256(py_path), 'r_result_sha256': sha256(r_path), 'v4_documented_not_equal_fields': p.get('v4_documented_not_equal_fields', []), 'synthetic_only': True}
    path = out / 'verification_receipt.json'
    write_json(path, payload)
    if failures:
        raise SystemExit('\n'.join(failures))
    print(f"PYSTATSV1_PSYCH_DESIGN_VERIFICATION_OK study={sid} category={row['verification_category']}")
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--study', required=True)
    args = parser.parse_args()
    verify(args.study)
