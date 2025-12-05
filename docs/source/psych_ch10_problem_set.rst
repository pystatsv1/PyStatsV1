Chapter 10 Problem Set – Independent-Samples :math:`t` Test
===========================================================

Where this problem set fits in the story
----------------------------------------

This problem set extends :doc:`psych_ch10_independent_t`, which introduced
between-subjects designs and the independent-samples :math:`t` test.

In Track B you learned how to:

* Design a basic treatment-versus-control experiment.
* Compute and interpret an independent-samples :math:`t` test.
* Report results in APA style, including effect size (Cohen’s :math:`d`).

In **Track C** you will:

* Work through several realistic research scenarios.
* See how each analysis is implemented as reproducible Python code.
* Use the provided solution script as a template for your own studies.

Learning goals
--------------

After completing this problem set, you should be able to:

* Choose an appropriate independent-samples :math:`t` test for a simple
  between-subjects design.
* Run the test in Python (using PyStatsV1 + Pingouin) and interpret the
  results.
* Extract and report the key quantities: group means, mean difference,
  :math:`t`, degrees of freedom, :math:`p`, and Cohen’s :math:`d`.
* Understand how sample size and effect size jointly influence statistical
  significance.

How to run the worked solutions
-------------------------------

From the repository root, run:

.. code-block:: bash

   # Run the solution script for this problem set
   make psych-ch10-problems

   # Run only the tests for this problem set
   make test-psych-ch10-problems

These targets simply wrap:

.. code-block:: bash

   python -m scripts.psych_ch10_problem_set
   pytest tests/test_psych_ch10_problem_set.py

The solution script will:

* Simulate data for each exercise with a fixed random seed.
* Run the independent-samples :math:`t` tests.
* Print concise summaries to the console.
* Save data and results tables under:

  * ``data/synthetic/psych_ch10_*.csv``
  * ``outputs/track_c/ch10_problem_set_results.csv``
  * ``outputs/track_c/ch10_problem_set_group_means.png``

Conceptual warm-up
------------------

Before touching the code, think through these questions:

1. In an independent-samples design, why do we care about **homogeneity of
   variance** between groups?
2. How does increasing sample size affect the standard error of the mean
   difference and the resulting :math:`t` statistic?
3. Why might a result be **statistically significant but not practically
   important**?
4. Give an example of a research question in psychology that is naturally
   answered with an independent-samples :math:`t` test.

Applied exercises
-----------------

Exercise 1 – Stress-reduction workshop vs. waitlist
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A counseling center wants to evaluate a **stress-reduction workshop**.
Students are randomly assigned to:

* ``control`` – waitlist (no workshop yet).
* ``treatment`` – immediate participation in the workshop.

After two weeks, all students complete the same **stress scale**
(higher scores = **more** stress). The question:

   *“Does the workshop reduce average stress relative to the waitlist?”*

Tasks:

1. State appropriate :math:`H_0` and :math:`H_1`.
2. Run an independent-samples :math:`t` test.
3. Report:

   * Group means and mean difference
   * :math:`t`, df, :math:`p`
   * Cohen’s :math:`d`

In code, the worked solution uses:

* :func:`scripts.psych_ch10_problem_set.simulate_independent_t_dataset`
  to generate the data, and
* :func:`scripts.psych_ch10_problem_set.run_independent_t`
  to compute the :math:`t` test.

You can inspect and adapt that code to analyze your own treatment-versus-control
experiments.

Exercise 2 – The curse of small :math:`n`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now imagine the same workshop, but with a **much smaller sample size**.
The effect of the workshop on stress is similar in magnitude to Exercise 1,
but because :math:`n` is smaller, the test has **lower power**.

Tasks:

1. Use the provided code to simulate a smaller sample and run the
   independent-samples :math:`t` test.
2. Compare the resulting :math:`t`, :math:`p`, and Cohen’s :math:`d` with
   Exercise 1.
3. Explain in words how the **same underlying effect** can fail to reach
   significance when you have too few participants.

In code, see:

* :func:`scripts.psych_ch10_problem_set.exercise_1_large_sample`
* :func:`scripts.psych_ch10_problem_set.exercise_2_small_sample`

Exercise 3 – Strong treatment effect
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, consider a scenario where the treatment has a **very strong effect**
on the outcome. This might correspond to a highly effective clinical
intervention or an artificially “clean” lab manipulation.

Tasks:

1. Simulate a dataset with a large effect size and moderate sample size.
2. Run the independent-samples :math:`t` test.
3. Examine:

   * The size of :math:`t` and how close :math:`p` is to zero.
   * The magnitude of Cohen’s :math:`d`.

In code, see:

* :func:`scripts.psych_ch10_problem_set.exercise_3_large_effect`.

Running the Chapter 10 problem set lab
--------------------------------------

To re-run all exercises and regenerate the outputs for this problem set:

.. code-block:: bash

   make psych-ch10-problems

Then inspect:

* ``data/synthetic/psych_ch10_exercise1.csv`` – Stress reduction, large sample
* ``data/synthetic/psych_ch10_exercise2.csv`` – Stress reduction, small sample
* ``data/synthetic/psych_ch10_exercise3.csv`` – Strong effect scenario
* ``outputs/track_c/ch10_problem_set_results.csv`` – Summary table of the three
  :math:`t` tests.
* ``outputs/track_c/ch10_problem_set_group_means.png`` – Group means plot.

Conceptual summary
------------------

* Independent-samples :math:`t` tests compare **mean differences** between two
  unrelated groups.
* **Effect size** and **sample size** jointly determine whether an effect is
  likely to be detected as statistically significant.
* PyStatsV1 solution scripts give you a **reusable template**:
  swap in your own dataset, re-run the analysis, and verify the results
  using the tests.
