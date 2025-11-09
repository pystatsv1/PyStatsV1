.PHONY: ch13
ch13:
\tpython scripts/sim_stroop.py
\tpython scripts/ch13_stroop_within.py --save-plots
\tpython scripts/sim_fitness_2x2.py
\tpython scripts/ch13_fitness_mixed.py --save-plots
