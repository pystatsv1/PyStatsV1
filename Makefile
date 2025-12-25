.DEFAULT_GOAL := help

PYTHON := python
SEED ?= 123
OUT_SYN := data/synthetic
OUT_CH13 := outputs/ch13
OUT_CH14 := outputs/ch14
OUT_CH15 := outputs/ch15
OUT_TRACK_D := outputs/track_d
OUT_LEDGERLAB_CH01 := data/synthetic/ledgerlab_ch01
OUT_NSO_V1 := data/synthetic/nso_v1


.PHONY: help
help:
	@echo "Available targets:"
	@echo "  ch13       - full Chapter 13 run (sim + analysis + plots)"
	@echo "  ch13-ci    - tiny, fast CI smoke for Chapter 13"
	@echo "  ch14       - full Chapter 14 A/B t-test (sim + analysis + plots)"
	@echo "  ch14-ci    - tiny, fast CI smoke for Chapter 14"
	@echo "  ch15       - full Chapter 15 reliability (sim + analysis + plots)"
	@echo "  ch15-ci    - tiny, fast CI smoke for Chapter 15"
	@echo "  psych-ch06 - Track B Chapter 6 z-score lab"
	@echo "  psych-ch07 - Track B Chapter 7 sampling lab"
	@echo "  business-sim  - Track D LedgerLab simulator (Chapter 1 core tables)"
	@echo "  business-ch01 - Track D Chapter 1 analysis (accounting as measurement)"
	@echo "  business-ch02 - Track D Chapter 2 analysis (double-entry & GL as database)"
	@echo "  business-nso-sim - Track D NSO v1 simulator (multi-month running case)"
	@echo "  business-validate - Validate Track D dataset schema + basic checks"
	@echo "  business-ch04 - Track D Chapter 4 analysis (assets: inventory + depreciation)"
	@echo "  business-ch05 - Track D Chapter 5 analysis (liabilities + payroll + taxes + debt + equity)"
	@echo "  business-ch06 - Track D Chapter 6 analysis (reconciliations as data validation)"
	@echo "  business-ch07 - Track D Chapter 7 analysis (prepare accounting data for analysis)"
	@echo "  business-ch08 - Track D Chapter 8 analysis (descriptive stats for financial performance)"
	@echo "  business-ch09 - Track D Chapter 9 analysis (plotting/reporting style contract + example figures)"
	@echo "  lint       - ruff check"
	@echo "  lint-fix   - ruff check with fixes"
	@echo "  test       - pytest"
	@echo "  clean      - remove generated outputs"



docs:
	python -m sphinx -b html docs/source docs/build/html


# --- CI smokes (small, deterministic) ---
.PHONY: ch13-ci
ch13-ci:
	$(PYTHON) -m scripts.sim_stroop --n-subjects 6 --n-trials 10 --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch13_stroop_within --data $(OUT_SYN)/psych_stroop_trials.csv --outdir $(OUT_CH13) --save-plots --seed $(SEED)
	$(PYTHON) -m scripts.sim_fitness_2x2 --n-per-group 10 --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch13_fitness_mixed --data $(OUT_SYN)/fitness_long.csv --outdir $(OUT_CH13) --save-plots --seed $(SEED)

.PHONY: ch14-ci
ch14-ci:
	$(PYTHON) -m scripts.sim_ch14_tutoring --n-per-group 10 --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch14_tutoring_ab --datadir $(OUT_SYN) --outdir $(OUT_CH14) --seed $(SEED)

.PHONY: ch15-ci
ch15-ci:
	$(PYTHON) -m scripts.sim_ch15_reliability --n-survey 20 --n-retest 10 --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch15_reliability_analysis --datadir $(OUT_SYN) --outdir $(OUT_CH15) --seed $(SEED)

# --- Full demos ---

.PHONY: psych-ch06
psych-ch06:
	$(PYTHON) -m scripts.psych_ch6_normal_zscores

.PHONY: psych-ch07
psych-ch07:
	$(PYTHON) -m scripts.sim_psych_ch7_sampling

.PHONY: psych-ch08
psych-ch08:
	$(PYTHON) -m scripts.psych_ch8_one_sample_test

.PHONY: psych-ch09
psych-ch09:
	python -m scripts.psych_ch9_one_sample_ci

.PHONY: psych-ch10
psych-ch10:
	python -m scripts.psych_ch10_independent_t

.PHONY: psych-ch11
psych-ch11:
	python -m scripts.psych_ch11_paired_t

.PHONY: psych-ch12
psych-ch12:
	python -m scripts.psych_ch12_one_way_anova

.PHONY: psych-ch13
psych-ch13:
	python -m scripts.psych_ch13_two_way_anova

.PHONY: psych-ch14 test-psych-ch14

# Run the Chapter 14 repeated-measures ANOVA lab script
psych-ch14:
	python -m scripts.psych_ch14_repeated_measures_anova

# Run the Chapter 14 unit tests only
test-psych-ch14:
	pytest tests/test_psych_ch14_repeated_measures_anova.py


psych-ch15:
	python -m scripts.psych_ch15_correlation


test-psych-ch15:
	pytest tests/test_psych_ch15_correlation.py


psych-ch15a-pairwise:
	python -m scripts.psych_ch15a_pingouin_pairwise_demo


test-psych-ch15a-pairwise:
	pytest tests/test_psych_ch15a_pingouin_pairwise_demo.py


psych-ch15a-partial:
	python -m scripts.psych_ch15a_pingouin_partial_demo


test-psych-ch15a-partial:
	pytest tests/test_psych_ch15a_pingouin_partial_demo.py


psych-ch16:
	python -m scripts.psych_ch16_regression


test-psych-ch16:
	pytest tests/test_psych_ch16_regression.py


psych-ch16a:
	python -m scripts.psych_ch16a_pingouin_regression_demo


test-psych-ch16a:
	pytest tests/test_psych_ch16a_pingouin_regression_demo.py


psych-ch17:
	python -m scripts.psych_ch17_mixed_models


test-psych-ch17:
	pytest tests/test_psych_ch17_mixed_models.py


psych-ch18:
	python -m scripts.psych_ch18_ancova


test-psych-ch18:
	pytest tests/test_psych_ch18_ancova.py

.PHONY: psych-ch19
psych-ch19:
	python -m scripts.psych_ch19_nonparametrics

.PHONY: test-psych-ch19
test-psych-ch19:
	pytest tests/test_psych_ch19_nonparametrics.py



psych-ch19a:
	python -m scripts.psych_ch19a_rank_nonparametrics

test-psych-ch19a:
	pytest tests/test_psych_ch19a_rank_nonparametrics.py


psych-ch20:
	python -m scripts.psych_ch20_responsible_researcher


test-psych-ch20:
	pytest tests/test_psych_ch20_responsible_researcher.py




# Track C – Chapter 10 problem set (independent t)
psych-ch10-problems:
	python -m scripts.psych_ch10_problem_set

test-psych-ch10-problems:
	pytest tests/test_psych_ch10_problem_set.py


# Track C – Chapter 11 problem set (Paired-samples t tests)
psych-ch11-problems:
	python -m scripts.psych_ch11_problem_set

test-psych-ch11-problems:
	pytest tests/test_psych_ch11_problem_set.py


# Track C – Chapter 12 problem set (one-way ANOVA)
psych-ch12-problems:
	python -m scripts.psych_ch12_problem_set

test-psych-ch12-problems:
	pytest tests/test_psych_ch12_problem_set.py


psych-ch13-problems:
	python -m scripts.psych_ch13_factorial_anova --n-per-cell 30 --seed 123 --outdir data/synthetic/psych_ch13


test-psych-ch13-problems:
	pytest tests/test_psych_ch13_factorial_anova.py


# Track C – Chapter 14 problem set (Repeated-Measures ANOVA)
psych-ch14-problems:
	python -m scripts.psych_ch14_problem_set

test-psych-ch14-problems:
	pytest tests/test_psych_ch14_problem_set.py


# Track C – Chapter 15 problem set (Correlation)
psych-ch15-problems:
	python -m scripts.psych_ch15_problem_set

test-psych-ch15-problems:
	pytest tests/test_psych_ch15_problem_set.py


# Track C – Chapter 16 problem set (linear regression)
psych-ch16-problems:
	python -m scripts.psych_ch16_problem_set

test-psych-ch16-problems:
	pytest tests/test_psych_ch16_problem_set.py

psych-ch17-problems:
	python -m scripts.psych_ch17_problem_set

test-psych-ch17-problems:
	pytest tests/test_psych_ch17_problem_set.py


.PHONY: psych-ch18-problems test-psych-ch18-problems

psych-ch18-problems:
	python -m scripts.psych_ch18_problem_set

test-psych-ch18-problems:
	pytest -q tests/test_psych_ch18_problem_set.py


.PHONY: psych-ch19-problems test-psych-ch19-problems

psych-ch19-problems:
	python -m scripts.psych_ch19_problem_set

test-psych-ch19-problems:
	pytest -q tests/test_psych_ch19_problem_set.py


.PHONY: psych-ch20-problems test-psych-ch20-problems

psych-ch20-problems:
	python scripts/psych_ch20_problem_set.py

test-psych-ch20-problems:
	pytest -q tests/test_psych_ch20_problem_set.py






.PHONY: ch13
ch13:
	$(PYTHON) -m scripts.sim_stroop --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch13_stroop_within --data $(OUT_SYN)/psych_stroop_trials.csv --outdir $(OUT_CH13) --save-plots --seed $(SEED)
	$(PYTHON) -m scripts.sim_fitness_2x2 --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch13_fitness_mixed --data $(OUT_SYN)/fitness_long.csv --outdir $(OUT_CH13) --save-plots --seed $(SEED)

.PHONY: ch14
ch14:
	$(PYTHON) -m scripts.sim_ch14_tutoring --n-per-group 50 --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch14_tutoring_ab --datadir $(OUT_SYN) --outdir $(OUT_CH14) --seed $(SEED)

.PHONY: ch15
ch15:
	$(PYTHON) -m scripts.sim_ch15_reliability --n-survey 150 --n-retest 40 --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch15_reliability_analysis --datadir $(OUT_SYN) --outdir $(OUT_CH15) --seed $(SEED)


# --- Track D (Business Statistics & Forecasting for Accountants) ---

.PHONY: business-sim
business-sim:
	$(PYTHON) -m scripts.sim_business_ledgerlab --outdir $(OUT_LEDGERLAB_CH01) --seed $(SEED) --month 2025-01 --n-sales 18

.PHONY: business-ch01
business-ch01:
	$(PYTHON) -m scripts.business_ch01_accounting_measurement --datadir $(OUT_LEDGERLAB_CH01) --outdir $(OUT_TRACK_D) --seed $(SEED)

.PHONY: business-ch02
business-ch02:
	$(PYTHON) -m scripts.business_ch02_double_entry_and_gl --datadir $(OUT_LEDGERLAB_CH01) --outdir $(OUT_TRACK_D) --seed $(SEED)

.PHONY: business-ch03
business-ch03: 
	$(PYTHON) -m scripts.business_ch03_statements_as_summaries --datadir $(OUT_LEDGERLAB_CH01) --outdir $(OUT_TRACK_D) --seed $(SEED)

.PHONY: business-nso-sim
business-nso-sim:
	$(PYTHON) -m scripts.sim_business_nso_v1 --outdir $(OUT_NSO_V1) --seed $(SEED) --start-month 2025-01 --n-months 24

.PHONY: business-validate
business-validate:
	$(PYTHON) -m scripts.business_validate_dataset --datadir $(OUT_NSO_V1) --outdir $(OUT_TRACK_D) --seed $(SEED)

.PHONY: business-ch04
business-ch04:
	$(PYTHON) -m scripts.business_ch04_assets_inventory_fixed_assets --datadir $(OUT_NSO_V1) --outdir $(OUT_TRACK_D) --seed $(SEED)

.PHONY: business-ch05
business-ch05:
	$(PYTHON) -m scripts.business_ch05_liabilities_payroll_taxes_equity --datadir $(OUT_NSO_V1) --outdir $(OUT_TRACK_D) --seed $(SEED)

.PHONY: business-ch06
business-ch06:
	$(PYTHON) -m scripts.business_ch06_reconciliations_quality_control --datadir $(OUT_NSO_V1) --outdir $(OUT_TRACK_D) --seed $(SEED)

.PHONY: business-ch07
business-ch07:
	$(PYTHON) -m scripts.business_ch07_preparing_accounting_data_for_analysis --datadir $(OUT_NSO_V1) --outdir $(OUT_TRACK_D) --seed $(SEED)

.PHONY: business-ch08
business-ch08:
	$(PYTHON) -m scripts.business_ch08_descriptive_statistics_financial_performance --datadir $(OUT_NSO_V1) --outdir $(OUT_TRACK_D) --seed $(SEED)

.PHONY: business-ch09
business-ch09:
	$(PYTHON) -m scripts.business_ch09_reporting_style_contract --datadir $(OUT_NSO_V1) --outdir $(OUT_TRACK_D) --seed $(SEED)

.PHONY: business-ch10
business-ch10:
	$(PYTHON) -m scripts.business_ch10_probability_risk --datadir $(OUT_NSO_V1) --outdir $(OUT_TRACK_D) --seed $(SEED)

.PHONY: business-ch11
business-ch11:
	$(PYTHON) -m scripts.business_ch11_sampling_estimation_audit_controls --datadir $(OUT_NSO_V1) --outdir $(OUT_TRACK_D) --seed $(SEED)

business-ch12: ## Run Track D Chapter 12 analysis
	$(PYTHON) -m scripts.business_ch12_hypothesis_testing_decisions --datadir $(OUT_NSO_V1) --outdir $(OUT_TRACK_D) --seed $(SEED)


# --- Quality gates ---
.PHONY: lint
lint:
	ruff check .

.PHONY: lint-fix
lint-fix:
	ruff check . --fix

.PHONY: test
test:
	pytest -q

# --- Utilities ---
.PHONY: clean
clean:
	@echo "Removing generated outputs in $(OUT_CH13), $(OUT_CH14), $(OUT_CH15) + packaging artifacts"
	-@rm -rf $(OUT_CH13) $(OUT_CH14) $(OUT_CH15)
	-@rm -rf dist build


.PHONY: clean-synth
clean-synth:
	@echo "Removing synthetic data in $(OUT_SYN) (may remove tracked fixtures!)"
	-@rm -rf $(OUT_SYN)


