.DEFAULT_GOAL := help
.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  ch13      - full Chapter 13 run (plots saved)"
	@echo "  ch13-ci   - tiny smoke (fast) for CI"

.PHONY: ch13-ci
ch13-ci:
	python scripts/sim_stroop.py --n-subjects 6 --n-trials 10
	python scripts/ch13_stroop_within.py --save-plots
	python scripts/sim_fitness_2x2.py --n-per-group 5
	python scripts/ch13_fitness_mixed.py --save-plots

.PHONY: ch13
ch13:
	python scripts/sim_stroop.py
	python scripts/ch13_stroop_within.py --save-plots
	python scripts/sim_fitness_2x2.py
	python scripts/ch13_fitness_mixed.py --save-plots

.PHONY: lint format test
lint:
	ruff check .
format:
	black .
test:
	pytest -q || true
