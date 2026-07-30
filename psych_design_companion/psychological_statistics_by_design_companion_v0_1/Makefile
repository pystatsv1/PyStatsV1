PYTHON ?= python3
STUDY ?=

.PHONY: first-result list-studies design-audit study verify-study packet all-python all-r parity figures reviewer-packets all clean

list-studies:
	$(PYTHON) scripts/python/list_studies.py

design-audit:
	$(PYTHON) scripts/python/design_audit.py

study:
	@test -n "$(STUDY)" || (echo "Set STUDY=SWL-S01 through SWL-S10"; exit 2)
	$(PYTHON) scripts/python/run_study.py --study "$(STUDY)"

verify-study: study
	Rscript scripts/r/run_study.R "$(CURDIR)" "$(STUDY)"
	$(PYTHON) scripts/verification/verify_study.py --study "$(STUDY)"

figures:
	$(PYTHON) scripts/python/generate_figures.py $(if $(STUDY),--study "$(STUDY)",)

packet: verify-study
	$(PYTHON) scripts/python/generate_figures.py --study "$(STUDY)"
	$(PYTHON) scripts/python/build_reviewer_packet.py --study "$(STUDY)"

first-result:
	$(MAKE) packet STUDY=SWL-S02
	@echo "PYSTATSV1_PSYCH_DESIGN_FIRST_RESULT_OK"

all-python: design-audit
	$(PYTHON) scripts/python/run_all.py

all-r:
	Rscript scripts/r/run_all.R "$(CURDIR)"

parity: all-python all-r
	$(PYTHON) scripts/verification/verify_all.py

reviewer-packets: parity figures
	$(PYTHON) scripts/python/build_reviewer_packet.py

all: design-audit reviewer-packets
	@echo "PYSTATSV1_PSYCH_DESIGN_COMPANION_ALL_OK"

clean:
	rm -rf outputs
