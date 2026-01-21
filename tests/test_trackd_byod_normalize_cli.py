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


def test_trackd_byod_normalize_core_gl_adapter_allows_noncanonical_headers_and_cleans_money(
    tmp_path: Path,
    capsys,
) -> None:
    proj = tmp_path / "byod"

    rc_init = main(["trackd", "byod", "init", "--dest", str(proj), "--profile", "core_gl"])
    assert rc_init == 0

    # Switch adapter to core_gl (it tolerates header variations and cleans values).
    cfg_path = proj / "config.toml"
    cfg = cfg_path.read_text(encoding="utf-8")
    cfg_path.write_text(cfg.replace('adapter = "passthrough"', 'adapter = "core_gl"'), encoding="utf-8")

    # Note: headers intentionally use spaces/case, and money uses commas/$/parentheses.
    (proj / "tables" / "chart_of_accounts.csv").write_text(
        "Account ID,Account Name,Account Type,Normal Side,Note\n"
        "1000, Cash ,Asset,Debit, ok \n",
        encoding="utf-8",
    )
    (proj / "tables" / "gl_journal.csv").write_text(
        "Txn ID,Date,Doc ID,Description,Account ID,Debit,Credit,Memo\n"
        't1,2024-01-01,inv-1, Sale ,1000,"$1,234.00",, hi \n'
        "t2,2024-01-02,inv-2, Refund ,1000,(200.00),,\n"
        't3,2024-01-03,inv-3, Payment ,1000,,"$2,000.00",\n',
        encoding="utf-8",
    )

    rc = main(["trackd", "byod", "normalize", "--project", str(proj)])
    out = capsys.readouterr().out.lower()

    assert rc == 0
    assert "adapter: core_gl" in out

    coa_hdr = (proj / "normalized" / "chart_of_accounts.csv").read_text(encoding="utf-8").splitlines()[0]
    gl_lines = (proj / "normalized" / "gl_journal.csv").read_text(encoding="utf-8").splitlines()

    assert coa_hdr.startswith("account_id,account_name,account_type,normal_side")
    assert gl_lines[0].startswith("txn_id,date,doc_id,description,account_id,debit,credit")

    # Money cleanup + whitespace trimming assertions
    import csv
    import io

    reader = csv.DictReader(io.StringIO("\n".join(gl_lines)))
    rows = list(reader)
    assert rows[0]["debit"] == "1234.00"
    assert rows[1]["debit"] == "-200.00"
    assert rows[2]["credit"] == "2000.00"


def test_trackd_byod_normalize_gnucash_gl_adapter_consumes_export_and_emits_core_gl_contract(
    tmp_path: Path,
    capsys,
) -> None:
    proj = tmp_path / "byod"

    rc_init = main(["trackd", "byod", "init", "--dest", str(proj), "--profile", "core_gl"])
    assert rc_init == 0

    # Switch adapter to gnucash_gl.
    cfg_path = proj / "config.toml"
    cfg = cfg_path.read_text(encoding="utf-8")
    cfg_path.write_text(cfg.replace('adapter = "passthrough"', 'adapter = "gnucash_gl"'), encoding="utf-8")

    # A tiny GnuCash "Export Transactions to CSV" example (complex layout; one transaction, two splits).
    (proj / "tables" / "gl_journal.csv").write_text(
        "Date,Transaction ID,Number,Description,Notes,Commodity/Currency,Void Reason,Action,Memo,Full Account Name,Account Name,Amount With Sym.,Amount Num.,Value With Sym.,Value Num.,Reconcile,Reconcile Date,Rate/Price\n"
        "2026-01-20,6d0b834e77b16d5a0eeb0f92f0dd1681,000001,Test,,CURRENCY::CAD,,,,Expenses:Auto:Gas,Gas,\"$10.00\",10.00,\"$10.00\",10.00,n,,1\n"
        "2026-01-20,6d0b834e77b16d5a0eeb0f92f0dd1681,000001,Test,,CURRENCY::CAD,,,,Assets:Current Assets:Cash in Wallet,Cash in Wallet,\"-$10.00\",-10.00,\"-$10.00\",-10.00,n,,1\n",
        encoding="utf-8",
    )

    rc = main(["trackd", "byod", "normalize", "--project", str(proj)])
    out = capsys.readouterr().out.lower()

    assert rc == 0
    assert "adapter: gnucash_gl" in out

    # Ensure outputs exist and are parseable.
    import csv

    gl_path = proj / "normalized" / "gl_journal.csv"
    coa_path = proj / "normalized" / "chart_of_accounts.csv"

    assert gl_path.exists()
    assert coa_path.exists()

    with gl_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2

    # Expense increases => debit; asset decreases => credit.
    exp = next(r for r in rows if r["account_id"].startswith("Expenses"))
    cash = next(r for r in rows if r["account_id"].startswith("Assets"))

    assert exp["debit"] == "10.00"
    assert exp["credit"] in ("", "0.00")

    assert cash["credit"] == "10.00"
    assert cash["debit"] in ("", "0.00")

    with coa_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        coa_rows = list(reader)

    ids = {r["account_id"] for r in coa_rows}
    assert "Expenses:Auto:Gas" in ids
    assert "Assets:Current Assets:Cash in Wallet" in ids
