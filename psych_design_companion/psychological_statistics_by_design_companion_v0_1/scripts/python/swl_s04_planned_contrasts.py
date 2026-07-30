#!/usr/bin/env python3
"""Run SWL-S04: omnibus several-group comparison and two registered planned contrasts.

Dataset: data/swl_s04_three_condition_support.csv
Registered target: guided-condition average minus standard support; guided practice plus feedback minus guided practice
This script analyzes the governed synthetic fixture only.
"""
from __future__ import annotations
from companion_runtime import run_registered_study
STUDY_ID = 'SWL-S04'
DATASET = 'data/swl_s04_three_condition_support.csv'
REGISTERED_ESTIMAND = ['guided-condition average minus standard support', 'guided practice plus feedback minus guided practice']
if __name__ == '__main__':
    run_registered_study(STUDY_ID)
