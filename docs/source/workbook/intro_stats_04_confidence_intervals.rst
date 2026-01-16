Intro Stats 4 - Confidence intervals
====================================

This is Part 4 of the **Intro Stats case study pack**.

A **confidence interval (CI)** is a range of values that is meant to capture plausible values for a population parameter.

Here the parameter is:

*the difference in mean score between treatment and control.*

In this part you will:

1. learn what a confidence interval is (and what it is *not*),
2. compute two 95% CIs for the mean difference,
3. compare a formula-based method vs a simulation-based method, and
4. practice interpreting results in plain language.

Big picture
-----------

So far, you have a sample difference in means:

* :math:`\bar{x}_{treat} - \bar{x}_{control}`

But samples vary.
If you repeated the study with new students, the difference would not be identical.

A **confidence interval** answers:

**“Given the data we observed, what range of mean differences is plausible?”**

Run
---

From inside your workbook folder:

.. code-block:: bash

   pystatsv1 workbook run intro_stats_04_confidence_intervals

Or directly:

.. code-block:: bash

   python scripts/intro_stats_04_confidence_intervals.py

What gets created
-----------------

Outputs go to:

* ``outputs/case_studies/intro_stats/``

You should see:

* ``ci_mean_diff_welch_95.csv`` - Welch CI endpoints (formula-based)
* ``ci_mean_diff_bootstrap_95.csv`` - bootstrap CI endpoints (simulation-based)

Inspect
-------

Step 1: open both CSVs
~~~~~~~~~~~~~~~~~~~~~~

Open both CI tables and compare:

* Are both intervals mostly above 0?
* Are they similar width?
* If they differ, which one is wider and why might that be?

Step 2: connect to the story
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Remember the research question:

* Do students in the **treatment** group score higher than students in the **control** group?

Now interpret your CI(s):

* If the entire CI is **above 0**, that supports “treatment tends to score higher.”
* If the CI includes **0**, the data are consistent with “no difference” (at least at this sample size).

Concepts (plain language)
-------------------------

What a 95% CI means (the repeated-sampling idea)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A 95% CI is often explained like this:

If you repeated the entire study many times and built a 95% CI each time,
then about 95% of those intervals would include the true population mean difference.

This is a repeated-sampling idea about the *method*, not a probability statement about one interval.

What a 95% CI does *not* mean
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It is **not** correct to say:

* “There is a 95% chance the true mean difference is in this interval.”

That sentence sounds natural, but it is not the classical interpretation.

What you *can* say safely (for this course)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For this Workbook, use plain language that stays accurate:

* “A reasonable range of mean differences, given the data, is from A to B.”
* “This range is mostly above 0, which supports a positive effect.”
* “This range includes 0, so the data do not rule out no difference.”

Welch CI vs bootstrap CI
------------------------

These are two different ways to get uncertainty around the mean difference.

1) Welch t-based CI (formula-based)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Uses a classic formula.
* Good default for comparing means when variances may differ.
* Often taught early in intro stats because it is fast and widely used.

Why “Welch” matters:

* It does **not** assume equal variances between groups.
* That makes it safer in many real datasets.

2) Bootstrap percentile CI (simulation-based)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Uses resampling (simulation).
* Intuition: “What mean differences would we see if we repeatedly resampled from the observed data?”
* Great for beginners because you can *see* uncertainty as repetition.

A percentile CI:

* builds a distribution of simulated mean differences
* takes the 2.5th and 97.5th percentiles as the endpoints

When both agree, that is reassuring.
When they differ, you’ve learned something about sample size, skew, or variability.

Worked problems
---------------

Worked problem A: interpreting a CI in words
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Suppose a CI table shows:

.. code-block:: text

   mean_diff, ci_low, ci_high
   7.2,      2.1,    12.4

A strong plain-language interpretation:

* “We estimate the treatment group scored about 7 points higher than control.”
* “A reasonable range for the true mean difference is about 2 to 12 points.”
* “Because the interval is above 0, the data support higher scores for treatment.”

Worked problem B: what if the CI includes 0?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Suppose you see:

.. code-block:: text

   mean_diff, ci_low, ci_high
   1.3,      -2.5,   5.1

Interpretation:

* “The best estimate is about 1.3 points higher for treatment.”
* “But values from about -2.5 to 5.1 are plausible.”
* “Because 0 is inside the interval, the data are consistent with no difference.”

That does *not* mean “no effect.”
It means the data are not precise enough to rule out zero.

Reproducibility checkpoint
--------------------------

Try rerunning the CI script:

.. code-block:: bash

   pystatsv1 workbook run intro_stats_04_confidence_intervals
   pystatsv1 workbook run intro_stats_04_confidence_intervals

You should get the same files.

**Note:** If a method uses randomness (bootstrap),
it should still be deterministic in this Workbook because the script sets a seed.

Using your own data (student workflow)
--------------------------------------

To use these scripts on your own dataset, you need:

* two groups (control/treatment), and
* a numeric outcome (score).

Option 1: Replace rows in the dataset (fastest)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This reuses the exact same scripts without editing code.

1) Back up the original dataset:

.. code-block:: bash

   cp data/intro_stats_scores.csv data/intro_stats_scores_backup.csv

2) Edit the CSV in Notepad (or any text editor):

.. code-block:: bash

   notepad data/intro_stats_scores.csv

3) Keep the header exactly:

.. code-block:: text

   id,group,score

and paste your rows underneath.

4) Run the CI script:

.. code-block:: bash

   pystatsv1 workbook run intro_stats_04_confidence_intervals

5) Inspect outputs:

* ``outputs/case_studies/intro_stats/ci_mean_diff_welch_95.csv``
* ``outputs/case_studies/intro_stats/ci_mean_diff_bootstrap_95.csv``

6) Restore the original when finished:

.. code-block:: bash

   mv data/intro_stats_scores_backup.csv data/intro_stats_scores.csv

Option 2: Use the general “My Own Data” scaffold
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If your columns do not match ``id,group,score``, use:

.. code-block:: bash

   pystatsv1 workbook run my_data_01_explore
   pystatsv1 workbook check my_data

That workflow helps clean types, missingness, and column naming before doing inference.

Common pitfalls (quick fixes)
-----------------------------

* If your CI is “weirdly huge,” check for outliers (Part 3).
* If your CI is “weirdly tight,” confirm units and data-entry.
* If the bootstrap CI changes run-to-run, confirm the script sets a random seed.

Next
----

Go to :doc:`intro_stats_05_hypothesis_testing` to run a simulation-based hypothesis test and compute an effect size.
