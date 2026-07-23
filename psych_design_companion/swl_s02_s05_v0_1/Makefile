PYTHON ?= python3
ROOT := $(abspath .)
REPO_ROOT := $(abspath ../..)

.PHONY: audit python-only r-check parity figures all

audit:
	$(PYTHON) $(REPO_ROOT)/tools/check_psych_design_swl_s02_s05.py --root $(ROOT)

python-only: audit
	$(PYTHON) scripts/python/run_all.py --root $(ROOT)

r-check: audit
	Rscript scripts/r/run_all.R $(ROOT) $(ROOT)/outputs/r

parity: python-only r-check
	$(PYTHON) scripts/python/compare_r_results.py --root $(ROOT)

figures: audit
	$(PYTHON) scripts/python/generate_figures.py --root $(ROOT)

all: parity figures
	@echo "PYSTATSV1_PSYCH_DESIGN_SWL_S02_S05_ALL_OK"
