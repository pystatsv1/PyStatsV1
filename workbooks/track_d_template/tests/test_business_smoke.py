from __future__ import annotations

import importlib

import pytest


MODULES = [
    # A few representative Track D scripts (imports should be safe).
    "scripts.d00_peek_data",
    "scripts.business_ch01_accounting_measurement",
    "scripts.business_ch02_double_entry_and_gl",
    "scripts.business_ch14_regression_driver_analysis",
    "scripts.business_ch23_communicating_results_governance",
    # Simulators
    "scripts.sim_business_ledgerlab",
    "scripts.sim_business_nso_v1",
]


@pytest.mark.parametrize("mod_name", MODULES)
def test_track_d_modules_import(mod_name: str) -> None:
    mod = importlib.import_module(mod_name)
    assert mod is not None


@pytest.mark.parametrize(
    "mod_name",
    [
        "scripts.business_ch01_accounting_measurement",
        "scripts.business_ch02_double_entry_and_gl",
        "scripts.business_ch14_regression_driver_analysis",
        "scripts.business_ch23_communicating_results_governance",
        "scripts.sim_business_ledgerlab",
        "scripts.sim_business_nso_v1",
    ],
)
def test_track_d_modules_define_main(mod_name: str) -> None:
    mod = importlib.import_module(mod_name)
    assert hasattr(mod, "main"), f"{mod_name} has no main()"
    assert callable(getattr(mod, "main"))
