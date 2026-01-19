PYTHON ?= python

.PHONY: help
help:
	@echo "Targets:"
	@echo "  setup         - (re)generate deterministic datasets under data/synthetic (seed=123)"
	@echo "  peek          - print a quick preview of Track D datasets"
	@echo "  test          - run workbook smoke tests"
	@echo "  d01..d23      - run a Track D chapter via wrapper (example: make d14)"

.PHONY: setup
setup:
	$(PYTHON) scripts/d00_setup_data.py

.PHONY: peek
peek:
	$(PYTHON) scripts/d00_peek_data.py

.PHONY: test
test:
	pytest -q

# Pattern rule: make d14 -> runs scripts/d14.py
.PHONY: d01 d02 d03 d04 d05 d06 d07 d08 d09 d10 d11 d12 d13 d14 d15 d16 d17 d18 d19 d20 d21 d22 d23

d%:
	$(PYTHON) scripts/$@.py
