from __future__ import annotations

from pathlib import Path


def test_track_d_ch16_20_runstrip_present() -> None:
    """Guardrail: Track D Ch16–Ch20 docs include the PyPI run-strip."""

    docs = Path("docs/source")

    cases = {
        "business_ch16_seasonality_baselines.rst": "d16",
        "business_ch17_revenue_forecasting_segmentation_drivers.rst": "d17",
        "business_ch18_expense_forecasting_fixed_variable_step_payroll.rst": "d18",
        "business_ch19_cash_flow_forecasting_direct_method_13_week.rst": "d19",
        "business_ch20_integrated_forecasting_three_statements.rst": "d20",
    }

    for rel, run_id in cases.items():
        text = (docs / rel).read_text(encoding="utf-8")
        assert ".. include:: _includes/track_d_run_strip.rst" in text
        assert f".. |trackd_run| replace:: {run_id}" in text
