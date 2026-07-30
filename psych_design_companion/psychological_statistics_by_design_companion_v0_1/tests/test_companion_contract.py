from __future__ import annotations
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_study_index_has_ten_nonpublic_synthetic_studies():
    data=json.loads((ROOT/'STUDY_INDEX.json').read_text())
    assert [x['study_id'] for x in data['studies']] == [f'SWL-S{i:02d}' for i in range(1,11)]
    assert data['status']=='release_candidate_implemented_not_public'
    assert data['synthetic_only'] is True and data['real_data_authorized'] is False
def test_no_placeholder_contract_text():
    text=(ROOT/'STUDY_INDEX.json').read_text().lower()
    assert 'to be copied' not in text and 'not yet implemented' not in text
