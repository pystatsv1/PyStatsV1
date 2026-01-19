from __future__ import annotations

import importlib


def test_trackd_imports() -> None:
    mod = importlib.import_module("pystatsv1.trackd")
    assert mod is not None
