from __future__ import annotations

from pathlib import Path

from pystatsv1.cli import main


def test_trackd_byod_init_creates_structure_and_headers(tmp_path: Path, capsys) -> None:
    dest = tmp_path / "byod"

    rc = main(["trackd", "byod", "init", "--dest", str(dest), "--profile", "core_gl"])
    out = capsys.readouterr().out

    assert rc == 0
    assert "BYOD project created" in out

    assert (dest / "tables").is_dir()
    assert (dest / "raw").is_dir()
    assert (dest / "normalized").is_dir()
    assert (dest / "notes").is_dir()
    assert (dest / "config.toml").exists()
    assert (dest / "README.md").exists()

    coa = (dest / "tables" / "chart_of_accounts.csv").read_text(encoding="utf-8").splitlines()[0]
    gl = (dest / "tables" / "gl_journal.csv").read_text(encoding="utf-8").splitlines()[0]

    assert coa == "account_id,account_name,account_type,normal_side"
    assert gl == "txn_id,date,doc_id,description,account_id,debit,credit"


def test_trackd_byod_init_refuses_non_empty_dir_without_force(tmp_path: Path, capsys) -> None:
    dest = tmp_path / "byod"
    dest.mkdir()
    (dest / "keep.txt").write_text("x", encoding="utf-8")

    rc = main(["trackd", "byod", "init", "--dest", str(dest), "--profile", "core_gl"])
    out = capsys.readouterr().out

    assert rc == 1
    assert "Refusing to write into non-empty directory" in out
    assert "--force" in out
