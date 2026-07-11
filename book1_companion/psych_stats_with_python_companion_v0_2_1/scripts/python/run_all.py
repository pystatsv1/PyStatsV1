#!/usr/bin/env python3
from __future__ import annotations

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = [
    "ch05_independent_t.py",
    "ch06_paired_t.py",
    "ch07_one_way_anova.py",
    "ch08_two_way_anova.py",
    "ch09_repeated_measures_anova.py",
    "ch10_correlation.py",
    "ch11_regression.py",
    "ch12_apa_reporting.py",
]

if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
for name in SCRIPTS:
    runpy.run_path(str(HERE / name), run_name="__main__")
