.DEFAULT_GOAL := help

PYTHON := python
SEED ?= 123
OUT_SYN := data/synthetic
OUT_CH13 := outputs/ch13
OUT_CH14 := outputs/ch14
OUT_CH15 := outputs/ch15

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
	@echo "Removing generated outputs in $(OUT_SYN), $(OUT_CH13), $(OUT_CH14), $(OUT_CH15)"
	-@rm -rf $(OUT_SYN) $(OUT_CH13) $(OUT_CH14) $(OUT_CH15)
