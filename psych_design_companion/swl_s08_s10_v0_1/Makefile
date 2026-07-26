PYTHON ?= python

.PHONY: refresh verify r-verify figures
refresh:
	$(PYTHON) ../../../tools/build_psych_design_swl_s08_s10.py

verify:
	$(PYTHON) ../../../tools/check_psych_design_swl_s08_s10.py

r-verify:
	$(PYTHON) ../../../tools/check_psych_design_swl_s08_s10.py --run-r

figures:
	$(PYTHON) scripts/python/generate_figures.py --root .
