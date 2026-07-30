#!/usr/bin/env python3
"""Run SWL-S08: longitudinal treatment-versus-control differential change.

Dataset: data/swl_s08_longitudinal_treatment.csv
Registered target: additional treatment-group change from baseline to post; additional treatment-group change from baseline to follow-up
This script analyzes the governed synthetic fixture only.
"""
from __future__ import annotations
from companion_runtime import run_registered_study
STUDY_ID = 'SWL-S08'
DATASET = 'data/swl_s08_longitudinal_treatment.csv'
REGISTERED_ESTIMAND = ['additional treatment-group change from baseline to post', 'additional treatment-group change from baseline to follow-up']
if __name__ == '__main__':
    run_registered_study(STUDY_ID)
