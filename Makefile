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