Intro Stats 1 - Descriptives and group summaries
================================================

This is Part 1 of the **Intro Stats case study pack**.

You have one dataset and one research question:

* **Dataset:** ``data/intro_stats_scores.csv``
* **Question:** Do students in the **treatment** group score higher than students in the **control** group?

In this part you will:

1. confirm the dataset loaded correctly,
2. compute simple descriptive statistics,
3. create your first reproducible outputs (a table + a plot), and
4. practice by doing a couple of **worked descriptive-statistics problems**.

Big picture
-----------

Descriptive statistics are your *first lens* on the data.

They answer questions like:

* What is the typical score in each group?
* How much do scores vary?
* What is the difference between groups *in the sample we observed*?

At this stage, you are not “proving” anything.
You are building a clear, reproducible summary that everyone can inspect.

Run
---

From inside your workbook folder:

.. code-block:: bash

   pystatsv1 workbook run intro_stats_01_descriptives

If you want to run the script directly:

.. code-block:: bash

   python scripts/intro_stats_01_descriptives.py

What gets created
-----------------

The script writes outputs to:

* ``outputs/case_studies/intro_stats/``

You should see:

* ``group_summary.csv`` - group sizes + mean/SD + mean difference
* ``group_means.png`` - a quick visual comparison of group means

Inspect
-------

Open the table (CSV) and answer these questions:

* Are there two groups (``control`` and ``treatment``)?
* Are the group sizes reasonable?
* Is the treatment mean higher than the control mean?
* What is the mean difference (treatment minus control)?

Then open the plot (PNG) and check:

* Does it match the direction you saw in the table?
* Is the difference “big”, “small”, or “somewhere in between” by eye?

Concepts (plain language)
-------------------------

**Descriptive statistics** summarize what you observed.

Mean
~~~~

The **mean** is the arithmetic average:

.. math::

   \bar{x} = \frac{x_1 + x_2 + \cdots + x_n}{n}

If a group mean is higher, that group scored higher *on average* in your sample.

Standard deviation (SD)
~~~~~~~~~~~~~~~~~~~~~~~

The **standard deviation (SD)** measures spread:

* **Small SD**: scores cluster tightly around the mean
* **Large SD**: scores vary widely

SD matters because two groups can have the same mean difference but very different variability.

Mean difference
~~~~~~~~~~~~~~~

A simple effect summary for this part is:

.. math::

   \Delta = \bar{x}_{treatment} - \bar{x}_{control}

A positive :math:`\Delta` means the treatment group is higher on average.

Worked problems
---------------

These are “by hand” practice problems. Use a calculator if you want.
Then compare with what the script produces.

Worked problem A: mean and mean difference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Suppose we run a tiny experiment:

* control scores:  68, 72, 75, 70
* treatment scores: 80, 78, 84, 82

1) Compute each group mean.

2) Compute the mean difference:

.. math::

   \Delta = \bar{x}_{treatment} - \bar{x}_{control}

**Check yourself**

* control mean: :math:`(68+72+75+70)/4 = 71.25`
* treatment mean: :math:`(80+78+84+82)/4 = 81.00`
* mean difference: :math:`81.00 - 71.25 = 9.75`

Interpretation (one sentence):
“The treatment group scored about 9.75 points higher than the control group, on average, in this sample.”

Worked problem B: why SD matters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now consider two “treatment” groups that have the same mean but different spread:

* treatment A: 80, 80, 80, 80
* treatment B: 70, 90, 70, 90

1) What is the mean of each?

2) Which has a bigger SD (more variability)?

**Check yourself**

* Both means are 80.
* Treatment B has much larger SD because values swing far from the mean.

Why this matters: a mean difference without variability can be misleading.
Later parts of the pack add **uncertainty** around the mean difference.

Reproducibility checkpoint
--------------------------

A big idea in PyStatsV1 is that you can rerun the same analysis any time and get the same artifacts.

Try this:

.. code-block:: bash

   # run twice
   pystatsv1 workbook run intro_stats_01_descriptives
   pystatsv1 workbook run intro_stats_01_descriptives

You should see the same printed results, and the output files should be overwritten deterministically.

Then run the check:

.. code-block:: bash

   pystatsv1 workbook check intro_stats

If the check passes, your pack is installed correctly and your artifacts look as expected.

Using your own data (student workflow)
--------------------------------------

You have two easy options:

Option 1: Use the “My Own Data” template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you want to explore *your own CSV* with the general scaffold:

.. code-block:: bash

   pystatsv1 workbook run my_data_01_explore
   pystatsv1 workbook check my_data

This produces generic tables/plots under ``outputs/my_data/`` and helps you verify your CSV is “clean”.

Option 2: Use this Intro Stats script with your own file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Intro Stats scripts expect a CSV like:

* ``id`` (integer)
* ``group`` (text, e.g., ``control`` / ``treatment``)
* ``score`` (numeric)

If your dataset has those same columns, you can replace the rows in
``data/intro_stats_scores.csv`` with your own rows and rerun the pack.

Example: reproduce a worked problem by editing the CSV
------------------------------------------------------

This example shows how you can **edit a CSV using a text editor** (like Notepad)
and then run the script to confirm the results match a worked problem.

Step 1: make a backup
~~~~~~~~~~~~~~~~~~~~~

From inside your workbook folder:

.. code-block:: bash

   cp data/intro_stats_scores.csv data/intro_stats_scores_backup.csv

Step 2: edit the CSV in Notepad
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Open the file in Notepad:

.. code-block:: bash

   notepad data/intro_stats_scores.csv

Replace the file contents with this tiny dataset (Worked problem A):

.. code-block:: text

   id,group,score
   1,control,68
   2,control,72
   3,control,75
   4,control,70
   5,treatment,80
   6,treatment,78
   7,treatment,84
   8,treatment,82

Save and close Notepad.

Step 3: rerun the descriptives script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pystatsv1 workbook run intro_stats_01_descriptives

Now open:

* ``outputs/case_studies/intro_stats/group_summary.csv``

You should see:

* control mean ≈ **71.25**
* treatment mean ≈ **81.00**
* mean difference ≈ **9.75**

Step 4: run the check
~~~~~~~~~~~~~~~~~~~~~

Because you changed the dataset, the “expected pattern” tests may fail (that’s normal).
So for this small practice dataset, your “check” is simply verifying the output table values.

When you are done practicing, restore the original dataset:

.. code-block:: bash

   mv data/intro_stats_scores_backup.csv data/intro_stats_scores.csv

Then rerun and check again:

.. code-block:: bash

   pystatsv1 workbook run intro_stats_01_descriptives
   pystatsv1 workbook check intro_stats

That final check should pass after restoring the original dataset.

Common pitfalls
---------------

* **“score” column treated like text**: make sure scores are plain numbers (no commas).
* **Extra spaces**: avoid ``control `` (trailing space) vs ``control``.
* **Mixed group names**: keep group labels consistent (case-sensitive).

Next
----

Go to :doc:`intro_stats_02_simulation` to learn why “difference in means” needs uncertainty around it.