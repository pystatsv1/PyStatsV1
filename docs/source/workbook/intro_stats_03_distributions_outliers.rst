Intro Stats 3 - Distributions and outliers
==========================================

This is Part 3 of the **Intro Stats case study pack**.

Before doing “formal” inference, it helps to look at the **shape** of the data.

Two common questions:

* Are the scores roughly bell-shaped, or skewed?
* Are there extreme values that might be mistakes or unusual cases?

In this part you will:

1. visualize distributions by group (histograms + boxplots),
2. learn what “skew” and “outlier” mean in plain language,
3. use a simple, transparent outlier rule (IQR), and
4. practice with a couple of worked mini-examples.

Why this matters
----------------

Many statistical tools (like t-tests and confidence intervals) *work best* when:

* the data are roughly symmetric (not extremely skewed), and
* a few extreme values are not dominating the story.

You do not need “perfect” bell curves to do inference.
But you *do* want to know what the data look like, so you can:

* spot mistakes (data-entry errors),
* understand unusual cases (real outliers),
* choose robust alternatives when needed, and
* communicate results honestly.

Run
---

From inside your workbook folder:

.. code-block:: bash

   pystatsv1 workbook run intro_stats_03_distributions_outliers

Or directly:

.. code-block:: bash

   python scripts/intro_stats_03_distributions_outliers.py

What gets created
-----------------

Outputs go to:

* ``outputs/case_studies/intro_stats/``

You should see:

* ``score_distributions.png`` - per-group histogram + boxplot
* ``outliers_iqr.csv`` - rows flagged as outliers using the IQR rule

Inspect
-------

Step 1: read the picture first
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open ``score_distributions.png`` and look for:

**Histograms**

* Is each group’s distribution roughly symmetric, or skewed?
* Is one group “wider” (more variable) than the other?

**Boxplots**

* Do the medians (middle lines) differ?
* Are the boxes (middle 50%) similar sizes?
* Do whiskers differ a lot?

**Extreme points**

* Any dots far from the rest of the data?
* If yes, are they in one group or both?

Step 2: read the outlier table
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open ``outliers_iqr.csv``.

If it is empty, that is fine.
If it has rows, note:

* which group(s) the outliers are in,
* whether the values look plausible,
* whether the outliers would change the story.

Concepts (plain language)
-------------------------

Distribution
~~~~~~~~~~~~

A **distribution** is how values are spread out.

Three quick “shape words” you will see a lot:

* **symmetric**: left and right sides look similar
* **right-skewed**: a few unusually *high* values stretch the right tail
* **left-skewed**: a few unusually *low* values stretch the left tail

Outliers
~~~~~~~~

An **outlier** is a value far from most of the data.

Outliers can happen for many reasons:

* **typo** (e.g., 800 instead of 80)
* **unit mix-up** (e.g., percent vs points)
* **real extreme case** (someone truly unusual)

Outlier detection is not “auto-delete.”
It is “worth a closer look.”

The IQR rule
~~~~~~~~~~~~

A quick way to flag potential outliers is the **IQR rule**:

* :math:`IQR = Q3 - Q1` (the middle 50% spread)
* outlier if:

  * :math:`value < Q1 - 1.5\times IQR` or
  * :math:`value > Q3 + 1.5\times IQR`

This is transparent and easy to explain.
It is not perfect, but it is a good first pass.

Worked mini-examples
--------------------

Worked example A: what the IQR rule is doing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Suppose a small set of scores:

.. code-block:: text

   10, 11, 12, 12, 13, 14, 15, 30

Most scores are around 10–15, but one score is 30.

* The **middle** of the data is near 12–14.
* The value 30 is far away, so it may be flagged as an outlier.

Key lesson: the IQR rule compares a value to the “middle 50%” range.

Worked example B: outlier vs “valid extreme”
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Imagine two situations:

1) A score of 30 on a test that is out of 100.
2) A score of 300 on that same test.

Which one is more likely to be a typo?

Usually:

* 30 might be a valid low score.
* 300 is impossible and almost certainly a data-entry error.

So your first question should often be:
“Is this value even possible?”

Good practice (what to do if you find an outlier)
-------------------------------------------------

If you find an outlier, don’t delete it just because it is inconvenient.
Instead, ask:

1) **Is it a typo or data-entry error?**
   If yes, fix it (and document the fix).

2) **Is it a valid extreme case?**
   If yes, keep it, but acknowledge it.

3) **Does it change conclusions?**
   Try a simple sensitivity check:

   * run the analysis with the outlier included
   * run again with it excluded (only if exclusion is justified)
   * compare the results

In real reporting, you would write something like:

* “Results were similar with and without the extreme value” (robust)
* or “Results depended heavily on one extreme value” (fragile)

Using your own data (student workflow)
--------------------------------------

If you want to use this chapter’s script on your own dataset:

Your CSV needs columns:

* ``id`` (unique identifier)
* ``group`` (e.g., ``control`` / ``treatment``)
* ``score`` (numeric)

Option 1: Replace the rows in ``data/intro_stats_scores.csv``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is the simplest way to reuse the exact same scripts.

1) Back up the original file:

.. code-block:: bash

   cp data/intro_stats_scores.csv data/intro_stats_scores_backup.csv

2) Edit the file (Notepad works fine):

.. code-block:: bash

   notepad data/intro_stats_scores.csv

3) Paste your own rows (keeping the same header):

.. code-block:: text

   id,group,score
   1,control,71
   2,control,69
   3,treatment,80
   4,treatment,78

4) Run the distributions/outliers script:

.. code-block:: bash

   pystatsv1 workbook run intro_stats_03_distributions_outliers

5) Inspect:

* ``outputs/case_studies/intro_stats/score_distributions.png``
* ``outputs/case_studies/intro_stats/outliers_iqr.csv``

When you are done, restore the original dataset:

.. code-block:: bash

   mv data/intro_stats_scores_backup.csv data/intro_stats_scores.csv

Then rerun to get back to the canonical pack:

.. code-block:: bash

   pystatsv1 workbook run intro_stats_03_distributions_outliers

Option 2: Use the general “My Own Data” scaffold
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you do not want to match the Intro Stats column names, use:

.. code-block:: bash

   pystatsv1 workbook run my_data_01_explore
   pystatsv1 workbook check my_data

This is a great first pass to find missing values, types, and weird entries.

Reproducibility checkpoint
--------------------------

Run the chapter twice and confirm the same outputs appear:

.. code-block:: bash

   pystatsv1 workbook run intro_stats_03_distributions_outliers
   pystatsv1 workbook run intro_stats_03_distributions_outliers

If you changed the dataset for practice, remember:

* pack tests may fail until you restore the original data.

Next
----

Go to :doc:`intro_stats_04_confidence_intervals` to compute a 95% confidence interval for the mean difference.
