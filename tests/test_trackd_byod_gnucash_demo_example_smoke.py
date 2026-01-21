from __future__ import annotations

import csv
import shutil
from pathlib import Path

from pystatsv1.cli import main


def test_trackd_byod_gnucash_demo_example_smoke(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    src = repo_root / "examples" / "trackd_byod_gnucash_demo"
    assert src.exists(), "examples/trackd_byod_gnucash_demo is missing"

    proj = tmp_path / "trackd_byod_gnucash_demo"
    shutil.copytree(src, proj)

    rc = main(["trackd", "byod", "normalize", "--project", str(proj)])
    assert rc == 0

    normalized = proj / "normalized"
    gl_path = normalized / "gl_journal.csv"
    coa_path = normalized / "chart_of_accounts.csv"
    assert gl_path.exists()
    assert coa_path.exists()

    with gl_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames is not None
        for col in ("txn_id", "date", "doc_id", "description", "account_id", "debit", "credit"):
            assert col in reader.fieldnames
        rows = list(reader)

    assert rows, "expected normalized gl_journal rows"

    # Spot-check a known account and a known credit-normal split.
    assert any(r["account_id"] == "Assets:Current Assets:Checking" for r in rows)
    assert any(
        r["account_id"] == "Equity:Owner Capital" and r["credit"] == "5000.00" for r in rows
    )

    with coa_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames is not None
        for col in ("account_id", "account_name", "account_type", "normal_side"):
            assert col in reader.fieldnames
        coa_rows = list(reader)

    ids = {r["account_id"] for r in coa_rows}
    assert "Assets:Current Assets:Checking" in ids
    assert "Equity:Owner Capital" in ids

    # Daily totals helper (analysis-ready)
    rc2 = main(["trackd", "byod", "daily-totals", "--project", str(proj)])
    assert rc2 == 0

    daily_path = normalized / "daily_totals.csv"
    assert daily_path.exists()

    with daily_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames is not None
        for col in ("date", "revenue_proxy", "expenses_proxy", "net_proxy"):
            assert col in reader.fieldnames
        daily_rows = list(reader)

    assert daily_rows
    total_rev = sum(float(r["revenue_proxy"] or 0.0) for r in daily_rows)
    assert total_rev > 0.0
