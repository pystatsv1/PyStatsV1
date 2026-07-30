#!/usr/bin/env python3
"""Run SWL-S02: independent-group mean difference with conditional causal scope.

Dataset: data/swl_s02_structured_study_routine.csv
Registered target: structured_routine minus standard_routine mean post-session performance
This script analyzes the governed synthetic fixture only.
"""
from __future__ import annotations
from companion_runtime import run_registered_study
STUDY_ID = 'SWL-S02'
DATASET = 'data/swl_s02_structured_study_routine.csv'
REGISTERED_ESTIMAND = ['structured_routine minus standard_routine mean post-session performance']
if __name__ == '__main__':
    run_registered_study(STUDY_ID)
