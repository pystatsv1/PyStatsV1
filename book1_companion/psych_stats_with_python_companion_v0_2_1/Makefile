PYTHON ?= python3

.PHONY: design-audit design-test python-only r-check parity figures all

design-audit:
	$(PYTHON) scripts/python/audit_design_contract.py

design-test:
	$(PYTHON) -m unittest discover -s tests -p 'test_book1_design_contract.py' -v

python-only: design-audit
	$(PYTHON) scripts/python/run_all.py
	@echo "BOOK1_COMPANION_PYTHON_OUTPUTS_OK"

r-check: design-audit
	Rscript scripts/r/run_all.R
	@echo "BOOK1_COMPANION_R_OUTPUTS_OK"

parity: design-audit
	$(PYTHON) scripts/python/compare_results.py --require-r
	@echo "BOOK1_COMPANION_PARITY_OK"

figures: design-audit
	$(PYTHON) scripts/python/generate_figures.py
	@echo "BOOK1_COMPANION_V021_FIGURES_OK"

all: design-audit python-only r-check parity
	@echo "BOOK1_COMPANION_ALL_OK"
