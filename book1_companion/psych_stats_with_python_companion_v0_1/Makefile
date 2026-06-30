PYTHON ?= python3

.PHONY: python-only r-check parity figures all

python-only:
	$(PYTHON) scripts/python/run_all.py
	@echo "BOOK1_COMPANION_PYTHON_OUTPUTS_OK"

r-check:
	Rscript scripts/r/run_all.R
	@echo "BOOK1_COMPANION_R_OUTPUTS_OK"

parity:
	$(PYTHON) scripts/python/compare_results.py --require-r
	@echo "BOOK1_COMPANION_PARITY_OK"

figures:
	$(PYTHON) scripts/python/generate_figures.py
	@echo "BOOK1_COMPANION_FIGURES_OK"

all: python-only r-check parity
	@echo "BOOK1_COMPANION_ALL_OK"
