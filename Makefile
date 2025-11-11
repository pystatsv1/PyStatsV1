.DEFAULT_GOAL := help

PYTHON := python
SEED ?= 123
OUT_SYN := data/synthetic
OUT_CH13 := outputs/ch13
OUT_CH14 := outputs/ch14

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  ch13       - full Chapter 13 run (sim + analysis + plots)"
	@echo "  ch13-ci    - tiny, fast CI smoke for Chapter 13"
	@echo "  ch14       - full Chapter 14 A/B t-test (sim + analysis + plots)"
	@echo "  ch14-ci    - tiny, fast CI smoke for Chapter 14"
	@echo "  lint       - ruff check"
	@echo "  lint-fix   - ruff check with fixes"
	@echo "  test       - pytest"
	@echo "  clean      - remove generated outputs"

# --- CI smokes (small, deterministic) ---
.PHONY: ch13-ci
ch13-ci:
	$(PYTHON) -m scripts.sim_stroop --n-subjects 6 --n-trials 10 --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch13_stroop_within --datadir $(OUT_SYN) --outdir $(OUT_CH13) --save-plots --seed $(SEED)
	$(PYTHON) -m scripts.sim_fitness_2x2 --n-per-group 10 --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch13_fitness_mixed --datadir $(OUT_SYN) --outdir $(OUT_CH13) --save-plots --seed $(SEED)

.PHONY: ch14-ci
ch14-ci:
	$(PYTHON) -m scripts.sim_ch14_tutoring --n-per-group 10 --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch14_tutoring_ab --datadir $(OUT_SYN) --outdir $(OUT_CH14) --seed $(SEED)

# --- Full demos ---
.PHONY: ch13
ch13:
	$(PYTHON) -m scripts.sim_stroop --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch13_stroop_within --datadir $(OUT_SYN) --outdir $(OUT_CH13) --save-plots --seed $(SEED)
	$(PYTHON) -m scripts.sim_fitness_2x2 --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch13_fitness_mixed --datadir $(OUT_SYN) --outdir $(OUT_CH13) --save-plots --seed $(SEED)

.PHONY: ch14
ch14:
	$(PYTHON) -m scripts.sim_ch14_tutoring --n-per-group 50 --seed $(SEED) --outdir $(OUT_SYN)
	$(PYTHON) -m scripts.ch14_tutoring_ab --datadir $(OUT_SYN) --outdir $(OUT_CH14) --seed $(SEED)

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
	@echo "Removing generated outputs in $(OUT_SYN), $(OUT_CH13), $(OUT_CH14)"
	-@rm -rf $(OUT_SYN) $(OUT_CH13) $(OUT_CH14)
