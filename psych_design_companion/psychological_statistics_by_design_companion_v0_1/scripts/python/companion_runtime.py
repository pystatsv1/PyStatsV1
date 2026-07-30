from __future__ import annotations
import csv
import hashlib
import importlib
import json
import math
import sys
from pathlib import Path
from typing import Any
import pandas as pd
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
MODULES = {'SWL-S01': 'scripts.python.analysis_batches.batch_swl_s01_s06_s07', 'SWL-S06': 'scripts.python.analysis_batches.batch_swl_s01_s06_s07', 'SWL-S07': 'scripts.python.analysis_batches.batch_swl_s01_s06_s07', 'SWL-S02': 'scripts.python.analysis_batches.batch_swl_s02_s05', 'SWL-S03': 'scripts.python.analysis_batches.batch_swl_s02_s05', 'SWL-S04': 'scripts.python.analysis_batches.batch_swl_s02_s05', 'SWL-S05': 'scripts.python.analysis_batches.batch_swl_s02_s05', 'SWL-S08': 'scripts.python.analysis_batches.batch_swl_s08_s10', 'SWL-S09': 'scripts.python.analysis_batches.batch_swl_s08_s10', 'SWL-S10': 'scripts.python.analysis_batches.batch_swl_s08_s10'}

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n', encoding='utf-8', newline='\n')

def study_index() -> dict[str, dict[str, Any]]:
    payload = json.loads((ROOT / 'STUDY_INDEX.json').read_text(encoding='utf-8'))
    return {row['study_id']: row for row in payload['studies']}

def normalize_study_id(value: str) -> str:
    value = value.strip().upper().replace('_', '-')
    if value not in MODULES:
        raise ValueError(f'unknown study ID: {value}; expected SWL-S01 through SWL-S10')
    return value

def audit_frame(study_id: str, frame: pd.DataFrame, row: dict[str, Any]) -> dict[str, Any]:
    key = row['unique_key']
    missing = [name for name in key if name not in frame.columns]
    if missing:
        raise ValueError(f'{study_id}: missing key columns {missing}')
    duplicate_count = int(frame.duplicated(key).sum())
    if duplicate_count:
        raise ValueError(f'{study_id}: duplicate key rows={duplicate_count}')
    actual_levels = {}
    for field, expected in row.get('factor_levels', {}).items():
        if field not in frame.columns:
            raise ValueError(f'{study_id}: missing factor field {field}')
        actual = sorted((str(value) for value in frame[field].dropna().unique()))
        if set(actual) != set(expected):
            raise ValueError(f'{study_id}: factor levels for {field} expected={expected} actual={actual}')
        actual_levels[field] = actual
    unit_key = key[0]
    result = {'study_id': study_id, 'rows': int(len(frame)), 'unique_units': int(frame[unit_key].nunique()), 'unique_keys': int(frame.drop_duplicates(key).shape[0]), 'duplicate_key_rows': duplicate_count, 'factor_levels': actual_levels, 'missing_values_by_column': {name: int(value) for name, value in frame.isna().sum().items() if int(value)}}
    for field in ('expected_rows', 'expected_unique_units', 'expected_unique_keys'):
        actual_name = {'expected_rows': 'rows', 'expected_unique_units': 'unique_units', 'expected_unique_keys': 'unique_keys'}[field]
        if result[actual_name] != int(row[field]):
            raise ValueError(f'{study_id}: {actual_name} expected={row[field]} actual={result[actual_name]}')
    return result

def _compare_reference(study_id: str, fields: dict[str, Any], row: dict[str, Any]) -> None:
    reference = json.loads((ROOT / row['reference_python_result']).read_text(encoding='utf-8'))['reported_fields']
    if set(fields) != set(reference):
        raise ValueError(f'{study_id}: generated result field set differs from governed reference')
    tolerance = 5e-06 if study_id == 'SWL-S08' else 1e-08
    failures = []
    for name, expected in reference.items():
        actual = fields[name]
        if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
            if not math.isclose(float(actual), float(expected), rel_tol=tolerance, abs_tol=tolerance):
                failures.append(f'{name}: expected={expected} actual={actual}')
        elif actual != expected:
            failures.append(f'{name}: expected={expected!r} actual={actual!r}')
    if failures:
        raise ValueError(f'{study_id}: governed result drift\n' + '\n'.join(failures))

def run_registered_study(study_id: str) -> Path:
    study_id = normalize_study_id(study_id)
    row = study_index()[study_id]
    dataset = ROOT / row['dataset_path']
    frame = pd.read_csv(dataset)
    module = importlib.import_module(MODULES[study_id])
    module.validate_dataset(study_id, frame)
    audit = audit_frame(study_id, frame, row)
    fields = module.ANALYZERS[study_id](frame)
    _compare_reference(study_id, fields, row)
    slug = study_id.lower().replace('-', '_')
    out = ROOT / 'outputs' / slug
    result_path = out / 'python_result.json'
    payload = {'schema_version': 'psych-design-runtime-python-result-v0.1', 'study_id': study_id, 'synthetic_only': True, 'companion_version': 'v0.1', 'package_release_candidate': '0.26.0', 'dataset_path': row['dataset_path'], 'dataset_sha256': sha256(dataset), 'design_contract_path': row['design_contract_path'], 'design_contract_sha256': sha256(ROOT / row['design_contract_path']), 'measurement_map_path': row['measurement_map_path'], 'measurement_map_sha256': sha256(ROOT / row['measurement_map_path']), 'analysis_entry_script': row['python_script'], 'analysis_entry_script_sha256': sha256(ROOT / row['python_script']), 'analysis_module': MODULES[study_id], 'analysis_module_sha256': sha256(Path(module.__file__)), 'data_layout_audit': audit, 'reported_fields': fields, 'main_prohibited_inference': row['main_prohibited_inference']}
    write_json(result_path, payload)
    write_json(out / 'data_layout_audit.json', audit)
    maps = []
    for rel in row['apa_source_maps']:
        maps.append({'path': rel, 'sha256': sha256(ROOT / rel), 'payload': json.loads((ROOT / rel).read_text(encoding='utf-8'))})
    write_json(out / 'apa_source_map.json', {'schema_version': 'psych-design-runtime-apa-source-map-v0.1', 'study_id': study_id, 'python_result': 'python_result.json', 'python_result_sha256': sha256(result_path), 'reference_maps': maps, 'matched_limitation': 'matched_limitation.md', 'synthetic_only': True})
    limitations = []
    for rel in row['matched_limitations']:
        payload = json.loads((ROOT / rel).read_text(encoding='utf-8'))
        limitations.append(payload.get('limitation', payload.get('text', 'Matched limitation is recorded in the governed source.')))
    (out / 'matched_limitation.md').write_text('\n\n'.join((f'- {text}' for text in limitations)) + '\n', encoding='utf-8', newline='\n')
    print(f'PYSTATSV1_PSYCH_DESIGN_STUDY_OK study={study_id} result={result_path}')
    return result_path

def read_r_metrics(path: Path) -> dict[str, float]:
    result = {}
    with path.open(newline='', encoding='utf-8') as handle:
        rows = csv.DictReader(handle)
        if rows.fieldnames != ['metric', 'value']:
            raise ValueError(f'{path}: expected metric,value columns')
        for row in rows:
            name = (row.get('metric') or '').strip()
            if not name or name in result:
                raise ValueError(f'{path}: missing or duplicate metric {name!r}')
            value = float(row['value'])
            if not math.isfinite(value):
                raise ValueError(f'{path}: non-finite metric {name}')
            result[name] = value
    return result
