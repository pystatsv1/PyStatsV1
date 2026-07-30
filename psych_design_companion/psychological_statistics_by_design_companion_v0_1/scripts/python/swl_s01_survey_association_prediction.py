#!/usr/bin/env python3
"""Run SWL-S01: association and within-domain prediction.

Dataset: data/swl_s01_student_well_being_survey.csv
Registered target: Pearson association between sleep quality and academic confidence; regression coefficients predicting assessment performance within the observed predictor domain
This script analyzes the governed synthetic fixture only.
"""
from __future__ import annotations
from companion_runtime import run_registered_study
STUDY_ID = 'SWL-S01'
DATASET = 'data/swl_s01_student_well_being_survey.csv'
REGISTERED_ESTIMAND = ['Pearson association between sleep quality and academic confidence', 'regression coefficients predicting assessment performance within the observed predictor domain']
if __name__ == '__main__':
    run_registered_study(STUDY_ID)
