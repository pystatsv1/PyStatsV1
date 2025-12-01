Chapter 14 Appendix – Pingouin for Repeated-Measures and Mixed ANOVA
====================================================================

In Chapter 14 you learned how to:

* design a simple repeated-measures experiment (for example, Pre, Post, Followup),
* compute the sums of squares by hand for Time, Subjects, and Residual,
* and run a repeated-measures ANOVA using our own PyStatsV1 helper functions.

In that main chapter, the script optionally **cross-checks** the results with
:mod:`pingouin` if it is installed. This appendix explains:

* what Pingouin is and why it is useful for psychology students,
* how to install it safely,
* how it connects to Chapter 14 (repeated measures) and later chapters
  (mixed ANOVA, ANCOVA, regression, and more),
* and a small example using the Chapter 14 synthetic dataset.

What is Pingouin?
-----------------

`Pingouin <https://pingouin-stats.org/>`_ is an open-source statistical package
written in Python 3 and built on top of NumPy and pandas. It is designed for
users who want **simple but comprehensive** statistical functions without
having to write low-level code.

Some of its capabilities include:

* **ANOVAs**: multi-way between-subjects ANOVA, repeated-measures ANOVA,
  mixed (split-plot) ANOVA, and ANCOVA.
* **Pairwise tests and correlations**: parametric and non-parametric post-hoc
  tests, as well as Pearson, Spearman, robust, partial, distance, and
  repeated-measures correlations.
* **Regression and mediation**: linear and logistic regression, as well as
  mediation analysis with bootstrap confidence intervals.
* **Effect sizes and power**: Cohen’s :math:`d`, partial eta-squared,
  confidence intervals around effects, and power analysis helpers.
* **Other tools**: reliability and consistency measures, circular statistics,
  chi-square tests, and convenience plotting functions (for example, Q–Q plots
  and Bland–Altman plots).

A key advantage for teaching is that most Pingouin functions return a **tidy
pandas DataFrame** with all the usual quantities in one place: test statistic,
degrees of freedom, *p*-value, effect size, confidence intervals, and often a
Bayes factor and power estimate.

For example, while :func:`scipy.stats.ttest_ind` returns only a *t* value and
*p*-value, :func:`pingouin.ttest` returns a table with *t*, *df*, *p*,
Cohen’s :math:`d`, 95% confidence intervals, power, and Bayes factor.

Installation and Dependencies
-----------------------------

Pingouin is a Python 3 package currently tested on Python 3.8–3.11.

Its core dependencies include:

* NumPy
* SciPy
* pandas
* pandas-flavor
* statsmodels
* matplotlib
* seaborn

Some additional features require:

* scikit-learn
* mpmath

The simplest way to install Pingouin in your PyStatsV1 environment is with
``pip``:

.. code-block:: bash

   pip install pingouin

If you prefer ``conda`` and the conda-forge channel:

.. code-block:: bash

   conda install -c conda-forge pingouin

Pingouin is under active development, so it is a good idea to keep it updated:

.. code-block:: bash

   pip install --upgrade pingouin

If you run into issues, check that your Python version and environment are
compatible, and consult the Pingouin documentation and GitHub issues.

Why We Still Teach Sums of Squares
----------------------------------

In the main body of Chapter 14 we derived the repeated-measures ANOVA from
first principles:

.. math::

   SS_{\text{Total}} = SS_{\text{Subjects}} + SS_{\text{Within}}

and

.. math::

   SS_{\text{Within}} = SS_{\text{Time}} + SS_{\text{Residual}}.

This decomposition shows *why* repeated-measures designs are powerful: they
remove stable individual differences (Subjects) from the error term
(Residual), which often leads to larger *F* statistics for Time.

By contrast, a typical between-subjects ANOVA lumps all individual differences
into a single error term. Here you see the contrast explicitly:

* **Between-subjects ANOVA (Chapter 12)**:
  error includes all person-to-person variation.
* **Repeated-measures ANOVA (Chapter 14)**:
  error is shrunk by separating out Subject variability.

Pingouin does not replace this conceptual understanding—it **implements** it in
a robust, well-tested way and extends it to more complex designs.

How Chapter 14 Uses Pingouin
----------------------------

The Chapter 14 lab script (``psych_ch14_repeated_measures_anova.py``)
implements the repeated-measures ANOVA twice:

1. **Manual / PyStatsV1 implementation**

   * compute cell means, sums of squares, degrees of freedom, and *F* by hand,
   * print a table summarizing :math:`SS_{\text{Time}}`, :math:`SS_{\text{Subjects}}`,
     :math:`SS_{\text{Residual}}`, and :math:`SS_{\text{Total}}`,
   * compute a simple eta-squared style effect size for Time.

2. **Optional Pingouin cross-check**

   * if :mod:`pingouin` is available, the script reshapes the data to long
     format and calls :func:`pingouin.rm_anova` with:

     * ``dv="stress"`` (the dependent variable),
     * ``within="time"`` (the repeated factor),
     * ``subject="id"`` (the participant identifier),
     * ``detailed=True`` (to get effect size and sphericity information).

   * the Pingouin output includes:

     * sum of squares, degrees of freedom, *F*,
     * uncorrected *p*-values,
     * a generalized eta-squared style effect size (``ng2``),
     * and an estimate of the sphericity epsilon (``eps``) for the Time factor.

This cross-check confirms that the **hand-calculated ANOVA matches what a
modern stats library reports**, at least for the balanced, well-behaved
designs used in our teaching examples.

Example: Using Pingouin with the Chapter 14 Dataset
---------------------------------------------------

After running the Chapter 14 lab script, you will have a synthetic dataset
saved in:

* ``data/synthetic/psych_ch14_repeated_measures_stress.csv``

with one row per participant and separate columns for ``pre``, ``post``, and
``followup`` stress scores.

The following example shows how you could analyze this dataset directly in a
Python session or Jupyter notebook using Pingouin:

.. code-block:: python

   import pandas as pd
   import pingouin as pg

   # Load the wide-format data simulated by the Chapter 14 lab
   df_wide = pd.read_csv(
       "data/synthetic/psych_ch14_repeated_measures_stress.csv"
   )

   # Wide -> long format: one row per person per time point
   df_long = df_wide.melt(
       id_vars="id",
       value_vars=["pre", "post", "followup"],
       var_name="time",
       value_name="stress",
   )

   # Run repeated-measures ANOVA with Pingouin
   aov = pg.rm_anova(
       data=df_long,
       dv="stress",
       within="time",
       subject="id",
       detailed=True,
   )

   print(aov)

   # Optionally, pretty-print the table
   pg.print_table(aov, floatfmt=".3f")

You should see a table with:

* a row for the Time effect (``Source = "time"``),
* a row for the error term,
* sum of squares (``SS``), degrees of freedom (``DF``), mean squares (``MS``),
  *F*, *p*-value (``p-unc``), generalized eta-squared (``ng2``), and the
  sphericity epsilon (``eps``).

If your manual ANOVA and the Pingouin ANOVA disagree substantially, check:

* that you used the same data (no filtering or different random seeds),
* that the design is still balanced,
* and that the way you computed sums of squares matches the design that
  Pingouin assumes.

Beyond Chapter 14: Mixed ANOVA and ANCOVA
-----------------------------------------

The same ideas extend to more complex designs in later chapters.

* **Mixed (split-plot) ANOVA – Chapter 17**

  If you add a between-subjects factor (for example, treatment group) in
  addition to the repeated Time factor, you can use:

  .. code-block:: python

     aov_mixed = pg.mixed_anova(
         data=df_long,
         dv="stress",
         within="time",      # repeated factor
         between="group",    # between-subjects factor
         subject="id",
         effsize="np2",
         correction=False,   # or True to request a correction
     )

  This produces a table with rows for the main effects of Group and Time and
  the Group × Time interaction, using the appropriate error terms.

* **ANCOVA – Chapter 18**

  Pingouin also links naturally with :mod:`statsmodels` for regression-style
  analyses and ANCOVA, where you add a covariate (such as a pre-test score)
  to control for pre-existing differences between groups.

In both cases, understanding the **logic** of sums of squares from Chapters
12–14 makes it much easier to interpret what these more advanced functions
are doing under the hood.

Summary
-------

In this appendix you:

* saw how Pingouin fits into the PyStatsV1 ecosystem as a higher-level,
  psychology-friendly stats package,
* learned how to install and update Pingouin in a modern Python environment,
* connected the Chapter 14 manual repeated-measures ANOVA to Pingouin’s
  :func:`rm_anova`,
* and previewed how Pingouin can help with mixed ANOVA and more advanced
  analyses in later chapters.

The big picture:

* PyStatsV1 scripts and hand calculations teach you **why** repeated-measures
  designs and ANOVAs work the way they do.
* Pingouin shows you how professional data scientists and quantitative
  psychologists **actually run** these analyses in code.

Both perspectives are valuable. Together, they prepare you to read modern
research articles, run your own studies, and move smoothly between
psychology-focused tools and the broader Python data-science ecosystem.
