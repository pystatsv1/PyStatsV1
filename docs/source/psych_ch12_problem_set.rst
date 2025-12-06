Chapter 12 Problem Set – One-Way ANOVA
======================================

Where this problem set fits in the story
----------------------------------------

This Track C problem set is linked to **Chapter 12: One-Way ANOVA** in the
Psychological Science & Statistics mini-book (Track B).

* Track B Chapter 12 introduces the *logic* of one-way ANOVA:
  partitioning variance, interpreting the F-ratio, and understanding
  how post-hoc tests localize differences between means.
* Track B Chapter 10 problem set showed how to work with *two groups*
  using independent-samples t-tests.
* This Track C Chapter 12 problem set extends that workflow to *three
  or more groups* using one-way ANOVA.

The PyStatsV1 scripts here turn the conceptual ideas from Chapter 12 into a
*reusable analysis template* that you can adapt for your own studies.

Learning goals
--------------

By working through this problem set and inspecting the solution scripts, you
should be able to:

* Recognize when a one-way ANOVA is appropriate (one categorical predictor,
  three or more groups, continuous outcome).
* Simulate and analyze between-subjects designs with multiple levels of an
  independent variable (e.g., **low**, **medium**, **high** intervention).
* Interpret the ANOVA table: sums of squares, degrees of freedom, mean
  squares, F-statistic, and p-value.
* Inspect group means and effect sizes to distinguish statistical significance
  from practical significance.
* Use PyStatsV1’s solution scripts as a template for running your *own*
  one-way ANOVAs.

How to run the worked solutions
-------------------------------

From the project root (with your virtual environment activated), the Chapter 12
problem-set lab can be re-run with::

   make psych-ch12-problems

Behind the scenes this target calls::

   python -m scripts.psych_ch12_problem_set

This will:

* Simulate three different one-way ANOVA scenarios.
* Run ANOVA for each scenario.
* Save the simulated datasets and a summary CSV of the results.
* Produce a simple group-means plot for quick visual comparison.

Conceptual warm-up
------------------

Before looking at the code, think through these questions:

* Why do we prefer ANOVA instead of running multiple t-tests when comparing
  three or more groups?
* What does it mean, conceptually, to “partition” total variability into
  between-groups and within-groups components?
* How does increasing the number of groups (but holding sample size fixed)
  affect the F-ratio and statistical power?
* How would you explain to a collaborator the difference between a statistically
  significant F and a large, practically meaningful effect?

Applied exercises
-----------------

The script :mod:`scripts.psych_ch12_problem_set` contains three exercises that
mirror common classroom and research scenarios.

Exercise 1 – Classic three-group ANOVA (moderate effect)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Design: Three independent groups (:code:`control`, :code:`low_dose`,
  :code:`high_dose`), equal sample sizes.
* Outcome: Continuous score (e.g., stress reduction, performance, symptom
  change).
* Effect: Moderate treatment effect – the means are separated enough that
  the omnibus F-test is usually significant.

Questions to consider:

* What does the ANOVA table tell you about the overall effect of Group?
* How large is the effect (e.g., partial eta-squared)?
* Which pairwise differences would you expect to be significant in a
  post-hoc analysis?

Exercise 2 – Small effect, borderline significance
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Design: Same three groups as Exercise 1, but with smaller differences
  between group means.
* Effect: Small effect size – the F-test may be non-significant or only
  weakly significant depending on the simulated sample.

Questions to consider:

* How do F and p change compared to Exercise 1?
* Does the conclusion change if you focus on effect size rather than
  p < .05?
* How would you report these results honestly in an APA-style write-up?

Exercise 3 – Unequal n and strong effect
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Design: Three groups with unequal sample sizes (e.g., more participants in
  the control group than in one of the treatment groups).
* Effect: Strong effect size – the F-test is clearly significant, and the
  pattern of means is obvious in the plot.

Questions to consider:

* Does unequal n change your interpretation of the ANOVA table?
* How might unequal n arise in a real study (dropout, recruitment issues)?
* What would you recommend to a collaborator planning a follow-up study?

PyStatsV1 Lab: One-way ANOVA solution scripts
---------------------------------------------

The solution code for these exercises lives in::

   scripts/psych_ch12_problem_set.py

Key pieces to inspect in that module:

* **Data generation helpers** that simulate one-way ANOVA designs with tunable
  effect sizes and sample sizes.
* A **`run_one_way_anova`** function that wraps `pingouin.anova` to produce a
  tidy ANOVA table suitable for teaching.
* A small **`ProblemResult`** dataclass that bundles the simulated data,
  ANOVA table, and metadata (exercise label, group means, effect size, etc.).
* A main routine that writes all datasets and a **summary CSV** so you can
  see the three scenarios side-by-side.

Running the Chapter 12 problem set lab
--------------------------------------

To re-run all exercises and regenerate the outputs for this problem set, use::

   make psych-ch12-problems

Then inspect:

* :file:`data/synthetic/psych_ch12_exercise1.csv` – Three-group design with a
  moderate treatment effect.
* :file:`data/synthetic/psych_ch12_exercise2.csv` – Three-group design with a
  small effect.
* :file:`data/synthetic/psych_ch12_exercise3.csv` – Three-group design with
  unequal n and a strong effect.
* :file:`outputs/track_c/ch12_problem_set_results.csv` – Summary ANOVA table
  (one row per exercise).
* :file:`outputs/track_c/ch12_problem_set_group_means.png` – Group means plot
  for the three exercises.

Conceptual summary
------------------

* One-way ANOVA compares **mean differences across three or more independent
  groups** using a single F-test.
* The F-ratio expresses the *signal-to-noise* logic of variance partitioning:
  how much variability is explained by group membership relative to residual
  variability within groups.
* Sample size, group spacing (effect size), and error variance jointly determine
  whether an effect is likely to be detected as statistically significant.
* PyStatsV1 solution scripts give you a **reusable one-way ANOVA template**:
  swap in your own dataset, re-run the analysis, and verify the results using
  the tests.
