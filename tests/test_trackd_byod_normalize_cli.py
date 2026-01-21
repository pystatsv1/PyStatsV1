from __future__ import annotations

from pathlib import Path

from pystatsv1.cli import main


def test_trackd_byod_normalize_writes_canonical_outputs(tmp_path: Path, capsys) -> None:
    proj = tmp_path / "byod"

    rc_init = main(["trackd", "byod", "init", "--dest", str(proj), "--profile", "core_gl"])
    assert rc_init == 0

    # Write valid inputs, but scramble column order and add an extra column.
    (proj / "tables" / "chart_of_accounts.csv").write_text(
        "account_type,account_name,account_id,normal_side,extra\n"
        "asset,Cash,1,debit,x\n",
        encoding="utf-8",
    )

    (proj / "tables" / "gl_journal.csv").write_text(
        "credit,debit,account_id,description,doc_id,date,txn_id,extra\n"
        "0,100,1,Example,d1,2025-01-01,t1,y\n",
        encoding="utf-8",
    )

    rc = main(["trackd", "byod", "normalize", "--project", str(proj)])
    out = capsys.readouterr().out

    assert rc == 0
    assert "normalization complete" in out.lower()

    coa_out = (proj / "normalized" / "chart_of_accounts.csv").read_text(encoding="utf-8").splitlines()[0]
    gl_out = (proj / "normalized" / "gl_journal.csv").read_text(encoding="utf-8").splitlines()[0]

    assert coa_out == "account_id,account_name,account_type,normal_side,extra"
    assert gl_out == "txn_id,date,doc_id,description,account_id,debit,credit,extra"


def test_trackd_byod_normalize_requires_config_or_profile(tmp_path: Path, capsys) -> None:
    proj = tmp_path / "byod"
    proj.mkdir()
    (proj / "tables").mkdir()

    rc = main(["trackd", "byod", "normalize", "--project", str(proj)])
    out = capsys.readouterr().out

    assert rc == 1
    assert "missing profile" in out.lower()
