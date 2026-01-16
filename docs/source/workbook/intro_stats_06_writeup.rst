Intro Stats - Interpretation write-up template
==============================================

In a real course, you do not stop at “I ran the script.”
You write a short interpretation.

This pack includes a tiny template you can copy and fill in:

* ``writeups/intro_stats_interpretation_template.md``

Why a template?
---------------

Beginners often know how to compute numbers but are not sure what to *say*.
A template gives you a safe structure:

* what the question was,
* what you found (with numbers),
* what it means in plain language,
* what you are *not* claiming.

How to use it
-------------

From the repo root (or your workbook starter folder), copy the template:

.. code-block:: bash

   cp writeups/intro_stats_interpretation_template.md writeups/intro_stats_my_writeup.md

Open ``writeups/intro_stats_my_writeup.md`` in your editor and fill in the blanks.

What to include (minimum)
-------------------------

* **Descriptives:** group means and SDs (from Part 1)
* **Uncertainty:** a CI for the mean difference (from Part 4)
* **Test:** a p-value from the permutation test (from Part 5)
* **Effect size:** Cohen’s d or Hedges’ g (from Part 5)

Optional:

* a sentence about outliers (from Part 3)
* a sentence about limitations (“small sample”, “single school”, etc.)

Check
-----

When you want to confirm the pack is still working end-to-end:

.. code-block:: bash

   pystatsv1 workbook check intro_stats

That test is a “smoke test” - it confirms the dataset and basic effect pattern match the lesson.
