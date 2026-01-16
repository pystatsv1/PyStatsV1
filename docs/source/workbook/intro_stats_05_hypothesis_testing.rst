Intro Stats 5 - Hypothesis testing by simulation and effect size
================================================================

This is Part 5 of the **Intro Stats case study pack**.

By now you have:

* described the data (Part 1),
* visualized distributions and checked for outliers (Part 3),
* estimated uncertainty with simulation (Part 2),
* computed confidence intervals (Part 4).

Now you will run a **hypothesis test** using a simulation method called a
**permutation test**, and you will compute an **effect size**.

You are answering two different questions:

1. **Is the observed difference “rare” under a no-difference world?** (hypothesis test)
2. **How big is the difference in practical terms?** (effect size)

Dataset and research question
-----------------------------

* **Dataset:** ``data/intro_stats_scores.csv``
* **Columns:** ``id``, ``group`` (control/treatment), ``score``
* **Research question:** Do students in the **treatment** group score higher than students in the **control** group?

Run
---

From inside your workbook folder:

.. code-block:: bash

   pystatsv1 workbook run intro_stats_05_hypothesis_testing

Or run the script directly:

.. code-block:: bash

   python scripts/intro_stats_05_hypothesis_testing.py

What gets created
-----------------

Outputs go to:

* ``outputs/case_studies/intro_stats/``

You should see:

* ``permutation_dist.png`` - histogram of shuffled mean differences
* ``permutation_test_summary.csv`` - observed diff + simulated p-value
* ``effect_size.csv`` - Cohen’s d and Hedges’ g

Inspect (what to look for)
--------------------------

1) **The permutation plot**

Open ``permutation_dist.png`` and locate:

* **0** on the x-axis (no mean difference),
* your **observed difference** (a vertical marker or labeled value, depending on the script),
* whether the observed difference is in the “tail” (rare) or near the center (common).

Questions to answer:

* Is the null distribution centered near 0?
* Is your observed difference far out in a tail?
* Does it look rare (only a few shuffled results get that extreme)?

2) **The p-value table**

Open ``permutation_test_summary.csv`` and record:

* the observed mean difference (treatment − control),
* the p-value (simulation-based),
* the number of permutations used.

3) **Effect size**

Open ``effect_size.csv`` and record:

* Cohen’s d
* Hedges’ g

Then answer:

* Is the effect size “small”, “medium”, or “large” (rough guideline)?
* Does the effect size match what you saw visually in Part 1 and Part 3?

Concepts (plain language)
-------------------------

Null hypothesis (H0)
^^^^^^^^^^^^^^^^^^^^

**H0 (null):** group does not matter; any observed difference in means is due to chance.

In other words: the scores are the same “on average” in the population,
and if you repeated the study you would sometimes see a difference just by randomness.

Permutation test (simulation hypothesis test)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A **permutation test** builds a “no group effect” world like this:

* keep the **scores** exactly as observed,
* repeatedly **shuffle the group labels** (control/treatment),
* each shuffle produces a **mean difference** you would expect under H0.

Then:

* compare your real observed mean difference to the shuffled distribution,
* count how often the shuffled differences are **as extreme** (or more extreme) than observed,
* that fraction is the **p-value**.

This is powerful for beginners because it does not require heavy formulas.
It directly simulates what “chance differences” look like.

p-value (what it is and is not)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**p-value:** *If H0 were true, how often would we see a mean difference at least this large (or larger) just by chance?*

Common misunderstandings (avoid these):

* ❌ “The p-value is the probability the null is true.” (No.)
* ❌ “A p-value of 0.03 means there’s a 97% chance treatment works.” (No.)
* ✅ “If there were truly no group effect, a difference this large would be uncommon.”

Effect size (how big is the difference?)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Hypothesis tests answer “is it rare under H0?”.
Effect sizes answer “how big is it?”.

**Cohen’s d** scales the mean difference by the pooled standard deviation:

* d ≈ (mean_treatment − mean_control) / SD_pooled

**Hedges’ g** is a small-sample corrected version of d:

* g is usually slightly smaller than d when sample sizes are small.

Very rough guidelines (context matters!):

* 0.2 ≈ small
* 0.5 ≈ medium
* 0.8 ≈ large

In real work, you interpret effect sizes with domain context (grading scale, stakes, costs, etc.).

Worked problem 1 — compute the observed difference
---------------------------------------------------

Before you look at the script output, do this once by hand:

1) Open the dataset:

* ``data/intro_stats_scores.csv``

2) Take a small subset (first 5 control + first 5 treatment rows) and compute:

* mean_control
* mean_treatment
* mean_diff = mean_treatment − mean_control

Write your calculations down.

Then run:

.. code-block:: bash

   pystatsv1 workbook run intro_stats_05_hypothesis_testing

Compare your hand-computed difference to the program’s observed mean difference.
They should be consistent (your subset uses fewer rows, so it won’t match exactly,
but the sign/direction should).

Worked problem 2 — “tiny permutation test” intuition
-----------------------------------------------------

Here is a tiny dataset with 6 scores.
Imagine 3 students were labeled control and 3 were labeled treatment:

* Scores:  60, 62, 65, 70, 72, 75
* Observed labels (example):
  * control:   60, 62, 65
  * treatment: 70, 72, 75

Observed mean difference:

* mean_treat = (70+72+75)/3 = 72.33
* mean_ctrl  = (60+62+65)/3 = 62.33
* diff = 10.00

If H0 is true, the labels are exchangeable.
So we would reassign **which 3 scores** are “treatment” in all possible ways
(or in many random shuffles) and compute the difference each time.

Key idea:

* Under H0, a difference of 10 points should be rare if groups don’t matter.

Takeaway:

* If you can explain this tiny example in words, you understand the core logic of permutation tests.

One-sided vs two-sided (what “as extreme” means)
------------------------------------------------

The pack’s story is directional:

* “Does treatment score higher than control?”

That is a **one-sided** question.

Sometimes you instead ask:

* “Are the groups different in either direction?”

That is **two-sided**.

Your script will implement one of these choices.
When reading the output, make sure you know which it is.

Rule of thumb:

* one-sided when you truly care about a specific direction **and** that direction was chosen before seeing the data.
* two-sided when you are open to either direction (most common default in many courses).

Reproducibility checkpoint (simulation is still reproducible)
-------------------------------------------------------------

Even though this is simulation-based, you should still get stable outputs.

PyStatsV1 scripts typically set a random seed so that:

* the permutation distribution plot,
* the p-value,
* and the output CSVs

are reproducible from run to run.

Try:

.. code-block:: bash

   pystatsv1 workbook run intro_stats_05_hypothesis_testing
   pystatsv1 workbook run intro_stats_05_hypothesis_testing

You should see consistent results and deterministic files written to the same paths.

(If a course version changes the number of permutations, results may shift slightly,
but the story should remain the same.)

Using your own data (same workflow)
-----------------------------------

You can reuse this exact workflow on your own dataset if you can provide:

* a ``group`` column with exactly two groups, and
* a numeric ``score`` column.

Quickest path: replace the example CSV with your own data **using the same column names**.

**Important:** make a backup first.

Step 1 — backup the dataset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   cp data/intro_stats_scores.csv data/intro_stats_scores_backup.csv

Step 2 — edit the dataset in a text editor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open the CSV with Notepad:

.. code-block:: bash

   notepad data/intro_stats_scores.csv

Replace some (or all) rows with your own values.
Keep the header exactly:

::

   id,group,score

Rules of thumb:

* ``id`` is an integer (1, 2, 3, ...)
* ``group`` is ``control`` or ``treatment`` (spelling matters)
* ``score`` is a number (avoid commas inside numbers)

Step 3 — rerun the analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pystatsv1 workbook run intro_stats_01_descriptives
   pystatsv1 workbook run intro_stats_05_hypothesis_testing

Step 4 — sanity check the outputs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Inspect:

* ``outputs/case_studies/intro_stats/group_summary.csv``
* ``outputs/case_studies/intro_stats/permutation_test_summary.csv``
* ``outputs/case_studies/intro_stats/effect_size.csv``

If the direction or magnitude changed, that’s expected — you changed the data!

Step 5 — restore the original dataset (optional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to go back to the shipped example data:

.. code-block:: bash

   cp data/intro_stats_scores_backup.csv data/intro_stats_scores.csv

Worked “own data” example — reproduce a previously worked result
-----------------------------------------------------------------

Sometimes instructors want you to confirm you can reproduce a known result.

Here is a safe way to do that:

1) Make a backup (if you haven't already):

.. code-block:: bash

   cp data/intro_stats_scores.csv data/intro_stats_scores_backup.csv

2) Edit the CSV in Notepad and make a small, controlled change:

* choose **one** treatment row and increase its score by **+1**
* leave everything else unchanged

Example: if you see a treatment score of ``78``, change it to ``79``.

3) Rerun and confirm:

.. code-block:: bash

   pystatsv1 workbook run intro_stats_01_descriptives
   pystatsv1 workbook run intro_stats_05_hypothesis_testing

What should change?

* The treatment mean should increase slightly.
* The observed mean difference should increase slightly.
* The p-value may change a little (simulation), but the overall story should remain similar.

4) Restore the original file:

.. code-block:: bash

   cp data/intro_stats_scores_backup.csv data/intro_stats_scores.csv

This demonstrates you can:

* edit data safely (backup first),
* rerun reproducibly,
* interpret how outputs respond to small data changes.

Check (tests)
-------------

When you want a quick “did I break anything?” smoke test:

.. code-block:: bash

   pystatsv1 workbook check intro_stats

This confirms the case study pack still matches the lesson expectations.

Next
----

Go to :doc:`intro_stats_06_writeup` for a tiny interpretation template you can fill in.
