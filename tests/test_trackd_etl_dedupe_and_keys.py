from __future__ import annotations

import pandas as pd

from pystatsv1.trackd.etl import analyze_gl_preparation, prepare_gl_monthly_summary, prepare_gl_tidy


def _sample_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Smallest useful GL + COA inputs.

    - GL journal uses (txn_id, date, description, account_id, dc, amount)
    - Chart of accounts omits normal_side, which ETL should infer from account_type
    - doc_id/line_no are also omitted and should be synthesized safely
    """

    gl_journal = pd.DataFrame(
        [
            {
                "txn_id": "t1",
                "date": "2025-01-05",
                "description": "Sale (cash)",
                "account_id": "1000",
                "dc": "D",
                "amount": 100.0,
            },
            {
                "txn_id": "t1",
                "date": "2025-01-05",
                "description": "Sale (cash)",
                "account_id": "4000",
                "dc": "C",
                "amount": 100.0,
            },
        ]
    )

    chart_of_accounts = pd.DataFrame(
        [
            {"account_id": "1000", "account_name": "Cash", "account_type": "Asset"},
            {
                "account_id": "4000",
                "account_name": "Sales Revenue",
                "account_type": "Revenue",
            },
        ]
    )

    return gl_journal, chart_of_accounts


def test_prepare_gl_tidy_builds_stable_gl_line_id_and_signs() -> None:
    gl_journal, chart_of_accounts = _sample_inputs()

    gl_tidy = prepare_gl_tidy(gl_journal=gl_journal, chart_of_accounts=chart_of_accounts)

    # stable deterministic line IDs (txn_id + within-txn line number)
    assert set(gl_tidy["gl_line_id"]) == {"t1-1", "t1-2"}

    # raw_amount is debit - credit; amount is sign-aligned to account normal_side
    assert list(gl_tidy["raw_amount"]) == [100.0, -100.0]
    assert list(gl_tidy["amount"]) == [100.0, 100.0]

    # debit/credit columns should be populated consistently
    assert list(gl_tidy["debit"]) == [100.0, 0.0]
    assert list(gl_tidy["credit"]) == [0.0, 100.0]

    # ETL should infer normal_side from account_type when missing
    assert list(gl_tidy["normal_side"]) == ["debit", "credit"]

    # doc_id should be synthesized when missing (defaults to txn_id)
    assert list(gl_tidy["doc_id"]) == ["t1", "t1"]


def test_prepare_gl_monthly_summary_keys_unique_and_expected_totals() -> None:
    gl_journal, chart_of_accounts = _sample_inputs()
    gl_tidy = prepare_gl_tidy(gl_journal=gl_journal, chart_of_accounts=chart_of_accounts)

    monthly = prepare_gl_monthly_summary(gl_tidy)

    # expected contract (subset)
    for col in [
        "month",
        "account_id",
        "account_name",
        "account_type",
        "normal_side",
        "debit",
        "credit",
        "net_change",
        "n_lines",
    ]:
        assert col in monthly.columns

    # unique grouping keys
    assert (
        monthly[["month", "account_id", "normal_side"]].duplicated().sum() == 0
    )

    # one row per account in the month
    assert set(monthly["account_id"]) == {"1000", "4000"}

    # net_change is positive for both accounts after normal-side alignment
    m = monthly.set_index("account_id")
    assert float(m.loc["1000", "net_change"]) == 100.0
    assert float(m.loc["4000", "net_change"]) == 100.0


def test_analyze_gl_preparation_returns_outputs_and_summary_counts() -> None:
    gl_journal, chart_of_accounts = _sample_inputs()

    outputs = analyze_gl_preparation(gl_journal=gl_journal, chart_of_accounts=chart_of_accounts)

    assert outputs.gl_tidy.shape[0] == 2
    assert outputs.gl_monthly_summary.shape[0] == 2

    assert outputs.summary["metrics"]["n_gl_lines"] == 2
    # raw amounts should balance to zero (a valid double-entry transaction)
    assert outputs.summary["checks"]["gl_balances_raw_amount_sum_zero"] is True
