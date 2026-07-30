#!/usr/bin/env python3
"""Run SWL-S09: categorical association and rank-based distributional shift.

Dataset: data/swl_s09_outcome_distribution_extension.csv
Registered target: intervention minus comparison improvement-risk difference; distributional shift in recovery burden with intervention oriented as lower burden
This script analyzes the governed synthetic fixture only.
"""
from __future__ import annotations
from companion_runtime import run_registered_study
STUDY_ID = 'SWL-S09'
DATASET = 'data/swl_s09_outcome_distribution_extension.csv'
REGISTERED_ESTIMAND = ['intervention minus comparison improvement-risk difference', 'distributional shift in recovery burden with intervention oriented as lower burden']
if __name__ == '__main__':
    run_registered_study(STUDY_ID)
