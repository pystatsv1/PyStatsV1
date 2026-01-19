from __future__ import annotations

import json

import matplotlib as mpl
import matplotlib.pyplot as plt

from pystatsv1.trackd import reporting_style
from pystatsv1.trackd.mpl_compat import ax_boxplot


def test_reporting_style_contract_writer(tmp_path) -> None:
    out = tmp_path / "style_contract.json"
    reporting_style.write_contract_json(out)

    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded == reporting_style.STYLE_CONTRACT


def test_ax_boxplot_smoke() -> None:
    # Ensure a non-interactive backend (CI / headless).
    mpl.use("Agg", force=True)

    fig, ax = plt.subplots()
    try:
        ax_boxplot(ax, [1, 2, 3, 4, 5], tick_labels=["x"])
    finally:
        plt.close(fig)
