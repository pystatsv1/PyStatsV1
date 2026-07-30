#!/usr/bin/env python3
"""Run SWL-S07: baseline-adjusted group comparison under the registered ANCOVA model.

Dataset: data/swl_s07_baseline_adjusted_intervention.csv
Registered target: intervention minus comparison adjusted post-performance difference at the overall baseline mean
This script analyzes the governed synthetic fixture only.
"""
from __future__ import annotations
from companion_runtime import run_registered_study
STUDY_ID = 'SWL-S07'
DATASET = 'data/swl_s07_baseline_adjusted_intervention.csv'
REGISTERED_ESTIMAND = ['intervention minus comparison adjusted post-performance difference at the overall baseline mean']
if __name__ == '__main__':
    run_registered_study(STUDY_ID)
