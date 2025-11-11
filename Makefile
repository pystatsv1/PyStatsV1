# Default target
.DEFAULT_GOAL := help

# Config
PYTHON := python
SEED ?= 123
OUT_SYN := data/synthetic
OUT_CH13 := outputs/ch13

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  ch13        - full Chapter 13 run (sim + analysis + plots)"
	@echo "  ch13-ci     - tiny smoke run for CI (fast)"
	@echo "  lint        - run ruff checks"
	@echo "  lint-fix    - auto-fix with ruff"
	@echo "  test        - run pytest"
	@echo "  clean       - remove generated outputs"

# ---- Fast CI smoke (small n, deterministic) ----
.PHONY: ch13-ci
ch13-ci:
	$(PYTHON) -m scripts.sim_stroop --n-subjects 6 --n-trials 10 --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch13_stroop_within --data $(OUT_SYN)/psych_stroop_trials.csv --outdir $(OUT_CH13) --save-plots --seed $(SEED)
	$(PYTHON) -m scripts.sim_fitness_2x2 --n-per-group 10 --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch13_fitness_mixed --data $(OUT_SYN)/fitness_long.csv --outdir $(OUT_CH13) --save-plots --seed $(SEED)

# ---- Full Chapter 13 demo (default sizes) ----
.PHONY: ch13
ch13:
	$(PYTHON) -m scripts.sim_stroop --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch13_stroop_within --data $(OUT_SYN)/psych_stroop_trials.csv --outdir $(OUT_CH13) --save-plots --seed $(SEED)
	$(PYTHON) -m scripts.sim_fitness_2x2 --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch13_fitness_mixed --data $(OUT_SYN)/fitness_long.csv --outdir $(OUT_CH13) --save-plots --seed $(SEED)

# ---- Quality gates ----
.PHONY: lint
lint:
	ruff check .

.PHONY: lint-fix
lint-fix:
	ruff check . --fix

.PHONY: test
test:
	pytest -q

# ---- Utilities ----
.PHONY: clean
clean:
	@echo "Removing generated outputs in $(OUT_SYN) and $(OUT_CH13)"
	-@rm -rf $(OUT_SYN) $(OUT_CH13)
