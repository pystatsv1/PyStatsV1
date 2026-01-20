from __future__ import annotations

from pathlib import Path

import pytest

import scripts._business_schema as shim
import scripts._business_etl as etl_shim
import scripts._business_recon as recon_shim
import scripts._mpl_compat as mpl_shim
import scripts._reporting_style as style_shim
from pystatsv1.trackd._errors import TrackDSchemaError
from pystatsv1.trackd import etl as trackd_etl
from pystatsv1.trackd import mpl_compat as trackd_mpl
from pystatsv1.trackd import recon as trackd_recon
from pystatsv1.trackd import reporting_style as trackd_reporting_style
from pystatsv1.trackd import schema as trackd_schema


def test_business_schema_shim_exports_trackd_schema() -> None:
    # The shim should re-export the package implementation (same function objects).
    assert shim.validate_schema is trackd_schema.validate_schema
    assert shim.assert_schema is trackd_schema.assert_schema


def test_business_etl_shim_exports_trackd_etl() -> None:
    # The shim should re-export the package implementation (same function objects).
    assert etl_shim.prepare_gl_tidy is trackd_etl.prepare_gl_tidy
    assert etl_shim.build_gl_tidy_dataset is trackd_etl.build_gl_tidy_dataset
    assert etl_shim.prepare_gl_monthly_summary is trackd_etl.prepare_gl_monthly_summary
    assert etl_shim.analyze_gl_preparation is trackd_etl.analyze_gl_preparation


def test_business_recon_shim_exports_trackd_recon() -> None:
    # The shim should re-export the package implementation (same function objects).
    assert recon_shim.write_json is trackd_recon.write_json
    assert recon_shim.build_cash_txns_from_gl is trackd_recon.build_cash_txns_from_gl
    assert recon_shim.bank_reconcile is trackd_recon.bank_reconcile
    assert recon_shim.ar_rollforward_vs_tb is trackd_recon.ar_rollforward_vs_tb
    assert recon_shim.BankReconOutputs is trackd_recon.BankReconOutputs


def test_mpl_compat_shim_exports_trackd_mpl_compat() -> None:
    # The shim should re-export the package implementation (same function objects).
    assert mpl_shim.ax_boxplot is trackd_mpl.ax_boxplot


def test_reporting_style_shim_exports_trackd_reporting_style() -> None:
    # The shim should re-export the package implementation (same function objects).
    assert style_shim.style_context is trackd_reporting_style.style_context
    assert style_shim.save_figure is trackd_reporting_style.save_figure
    assert style_shim.plot_time_series is trackd_reporting_style.plot_time_series
    assert style_shim.plot_bar is trackd_reporting_style.plot_bar
    assert style_shim.plot_histogram_with_markers is trackd_reporting_style.plot_histogram_with_markers
    assert style_shim.plot_ecdf is trackd_reporting_style.plot_ecdf
    assert style_shim.plot_waterfall_bridge is trackd_reporting_style.plot_waterfall_bridge
    assert style_shim.FigureSpec is trackd_reporting_style.FigureSpec
    assert style_shim.FigureManifestRow is trackd_reporting_style.FigureManifestRow


def test_business_schema_shim_validate_schema_report_shape(tmp_path: Path) -> None:
    report = shim.validate_schema(tmp_path, dataset=trackd_schema.DATASET_NSO_V1)

    assert isinstance(report, dict)
    assert report["ok"] is False
    assert "missing_tables" in report
    assert "tables" in report


def test_business_schema_shim_assert_schema_is_friendly(tmp_path: Path) -> None:
    with pytest.raises(TrackDSchemaError) as ei:
        shim.assert_schema(tmp_path, dataset=trackd_schema.DATASET_NSO_V1)

    msg = str(ei.value)
    assert "Track D dataset schema check failed" in msg
    assert "Missing CSV files" in msg


def test_track_d_template_business_schema_is_a_shim() -> None:
    root = Path(__file__).resolve().parents[1]
    template = root / "workbooks" / "track_d_template" / "scripts" / "_business_schema.py"
    assert template.exists()

    text = template.read_text(encoding="utf-8")
    assert "pystatsv1.trackd.schema" in text
    assert "validate_schema" in text
    assert "assert_schema" in text


def test_track_d_template_business_etl_is_a_shim() -> None:
    root = Path(__file__).resolve().parents[1]
    template = root / "workbooks" / "track_d_template" / "scripts" / "_business_etl.py"
    assert template.exists()

    text = template.read_text(encoding="utf-8")
    assert "pystatsv1.trackd.etl" in text
    assert "prepare_gl_tidy" in text
    assert "build_gl_tidy_dataset" in text
    assert "prepare_gl_monthly_summary" in text
    assert "analyze_gl_preparation" in text


def test_track_d_template_business_recon_is_a_shim() -> None:
    root = Path(__file__).resolve().parents[1]
    template = root / "workbooks" / "track_d_template" / "scripts" / "_business_recon.py"
    assert template.exists()

    text = template.read_text(encoding="utf-8")
    assert "pystatsv1.trackd.recon" in text
    assert "write_json" in text
    assert "build_cash_txns_from_gl" in text
    assert "bank_reconcile" in text
    assert "ar_rollforward_vs_tb" in text


def test_track_d_template_mpl_compat_is_a_shim() -> None:
    root = Path(__file__).resolve().parents[1]
    template = root / "workbooks" / "track_d_template" / "scripts" / "_mpl_compat.py"
    assert template.exists()

    text = template.read_text(encoding="utf-8")
    assert "pystatsv1.trackd.mpl_compat" in text
    assert "ax_boxplot" in text
    assert "__all__" in text
    assert "import *" not in text


def test_track_d_template_reporting_style_is_a_shim() -> None:
    root = Path(__file__).resolve().parents[1]
    template = root / "workbooks" / "track_d_template" / "scripts" / "_reporting_style.py"
    assert template.exists()

    text = template.read_text(encoding="utf-8")
    assert "pystatsv1.trackd.reporting_style" in text
    assert "style_context" in text
    assert "save_figure" in text
    assert "__all__" in text
    assert "import *" not in text


def test_repo_level_business_etl_shim_is_explicit() -> None:
    root = Path(__file__).resolve().parents[1]
    shim_path = root / "scripts" / "_business_etl.py"
    assert shim_path.exists()

    text = shim_path.read_text(encoding="utf-8")
    assert "pystatsv1.trackd.etl" in text
    assert "__all__" in text
    assert "import *" not in text


def test_repo_level_business_recon_shim_is_explicit() -> None:
    root = Path(__file__).resolve().parents[1]
    shim_path = root / "scripts" / "_business_recon.py"
    assert shim_path.exists()

    text = shim_path.read_text(encoding="utf-8")
    assert "pystatsv1.trackd.recon" in text
    assert "__all__" in text
    assert "import *" not in text


def test_repo_level_mpl_compat_shim_is_explicit() -> None:
    root = Path(__file__).resolve().parents[1]
    shim_path = root / "scripts" / "_mpl_compat.py"
    assert shim_path.exists()

    text = shim_path.read_text(encoding="utf-8")
    assert "pystatsv1.trackd.mpl_compat" in text
    assert "__all__" in text
    assert "import *" not in text


def test_repo_level_reporting_style_shim_is_explicit() -> None:
    root = Path(__file__).resolve().parents[1]
    shim_path = root / "scripts" / "_reporting_style.py"
    assert shim_path.exists()

    text = shim_path.read_text(encoding="utf-8")
    assert "pystatsv1.trackd.reporting_style" in text
    assert "__all__" in text
    assert "import *" not in text
