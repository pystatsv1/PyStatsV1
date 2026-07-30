from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools/check_psych_design_release_contract.py"
CONTRACT = ROOT / "psych_design_companion/psych_design_release_contract_v0_1"


def run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(root / "tools/check_psych_design_release_contract.py")], cwd=root, text=True, capture_output=True)


def copy_repo(tmp_path: Path) -> Path:
    dest = tmp_path / "repo"
    shutil.copytree(ROOT, dest, ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", "*.pyc", "outputs", "build"))
    return dest


def test_release_contract_gate_passes() -> None:
    completed = run(ROOT)
    assert completed.returncode == 0, completed.stderr + completed.stdout
    assert "PYSTATSV1_PSYCH_DESIGN_RELEASE_CONTRACT_VERIFY_OK" in (completed.stdout + completed.stderr)


def test_all_ten_studies_are_registered_once() -> None:
    data=json.loads((CONTRACT/"CURRENT_STUDY_ASSET_INVENTORY.json").read_text())
    ids=[row["study_id"] for row in data["studies"]]
    assert ids == [f"SWL-S{i:02d}" for i in range(1,11)]
    assert len(set(ids)) == 10


def test_contract_does_not_claim_release_or_real_data_authorization() -> None:
    data=json.loads((CONTRACT/"COMPANION_RELEASE_CONTRACT.json").read_text())
    assert data["lifecycle"] == {
        "book_binding_authorized": False,
        "contract_frozen": True,
        "portal_release_authorized": False,
        "public_companion_released": False,
        "pypi_release_authorized": False,
        "real_data_authorized": False,
    }


def test_source_batch_mutation_is_detected(tmp_path: Path) -> None:
    repo=copy_repo(tmp_path)
    path=repo/"psych_design_companion/swl_s02_s05_v0_1/data/swl_s02_structured_study_routine.csv"
    path.write_text(path.read_text()+"\n",encoding="utf-8")
    completed=run(repo)
    assert completed.returncode != 0
    assert "preserved source file drift" in (completed.stdout + completed.stderr)


def test_false_command_implementation_claim_is_detected(tmp_path: Path) -> None:
    repo=copy_repo(tmp_path)
    path=repo/"psych_design_companion/psych_design_release_contract_v0_1/COMMAND_INTERFACE_CONTRACT.json"
    data=json.loads(path.read_text())
    data["commands"][0]["implemented"]=True
    path.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    completed=run(repo)
    assert completed.returncode != 0
    assert "incorrectly marked implemented" in (completed.stdout + completed.stderr)


def test_missing_study_path_is_detected(tmp_path: Path) -> None:
    repo=copy_repo(tmp_path)
    path=repo/"psych_design_companion/swl_s08_s10_v0_1/scripts/r/swl_s08.R"
    path.unlink()
    completed=run(repo)
    assert completed.returncode != 0
    assert "missing current_r_script" in (completed.stdout + completed.stderr)
