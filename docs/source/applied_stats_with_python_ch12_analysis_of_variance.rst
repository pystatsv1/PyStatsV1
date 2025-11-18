Applied Statistics with Python – Chapter 12
===========================================

Analysis of variance (ANOVA) and experiments
--------------------------------------------

This chapter parallels the “Analysis of Variance” material from the R notes,
but is written for a Python-first audience.

So far in the mini-book we have mostly:

* worked with **numeric predictors** (chapters on simple and multiple regression),
* treated real data sets as if they were “just given,” without asking how they
  were produced.

Here we:

* draw a sharp line between **observational** and **experimental** data,
* show how experiments naturally lead to **ANOVA models**,
* connect classical ANOVA to the regression tools you have already seen,
* and map the R functions to Python:

  * R: ``t.test()``, ``aov()``, ``pairwise.t.test()``, ``TukeyHSD()``
  * Python: :mod:`scipy.stats`, :mod:`statsmodels` formula API, and
    :mod:`statsmodels.stats.multicomp`.

The key message:

*Regression tools are not only for observational data; in experimental settings
we use the same modelling ideas, but we are allowed to make much stronger
causal statements because the predictors are under our control.*

12.1 Experiments: observational vs experimental data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The most important question about a data set is **how it was generated**.

Observational study
  *Both* predictors and response are observed.
  No one controlled who received which level of a predictor.

  Examples: hospital records, government surveys, user-behaviour logs.

Experiment
  The analyst **chooses** the levels of one or more predictors, applies them to
  subjects, then observes the response.

  Examples: drug vs placebo trials, A/B tests on a website, training
  interventions for athletes.

Terminology for experiments
---------------------------

In experimental settings we rename things slightly:

* **Factors** – predictors that are controlled by the experimenter
  (treatment group, diet, machine setting, etc.).
* **Levels** – possible values of a factor (control vs treatment, A/B/C, low /
  medium / high).
* **Subjects** – experimental units (people, animals, plots of land, machines…).
* **Randomization** – subjects are randomly assigned to factor levels.

Randomization is crucial:

* it balances **unobserved** variables across groups on average;
* it justifies treating observations as independent draws from a model.

Throughout this chapter we will:

* write models in symbols,
* show the equivalent R formula (for reference),
* and give the Python version with :mod:`statsmodels`.

12.2 Two-sample t-test as a tiny experiment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The simplest experimental design is a **two-group experiment**:

* one factor (for example “group”) with two levels: control and treatment;
* subjects randomly assigned to a level;
* one numeric response measured after treatment.

Mathematical model
------------------

We assume

.. math::

   Y_{1j} \sim N(\mu_1, \sigma^2), \quad
   Y_{2j} \sim N(\mu_2, \sigma^2),

for subjects in groups 1 and 2 respectively.

We test

.. math::

   H_0: \mu_1 = \mu_2
   \quad \text{vs} \quad
   H_1: \mu_1 \ne \mu_2.

In Chapter 5 we met the **two-sample t-test** for this situation.

R vs Python
-----------

R (formula interface):

.. code-block:: r

   t.test(sleep ~ group, data = melatonin, var.equal = TRUE)

Python (using :mod:`scipy.stats`):

.. code-block:: python

   import numpy as np
   from scipy import stats

   control = melatonin.loc[melatonin["group"] == "control", "sleep"]
   treatment = melatonin.loc[melatonin["group"] == "treatment", "sleep"]

   t_stat, p_value = stats.ttest_ind(control, treatment, equal_var=True)

The important conceptual link:

*The two-sample t-test is a special case of one-way ANOVA with two groups.*
The next section generalizes to any number of groups.

12.3 One-way ANOVA
~~~~~~~~~~~~~~~~~~

12.3.1 Model and intuition
--------------------------

Suppose we have one factor with :math:`g` levels (groups), such as four diets
A, B, C, and D. With :math:`n_i` observations in group :math:`i`, we write

.. math::

   Y_{ij} = \mu_i + \varepsilon_{ij}, \qquad
   \varepsilon_{ij} \sim N(0, \sigma^2), \quad i = 1,\dots,g.

Equivalently,

.. math::

   Y_{ij} = \mu + \alpha_i + \varepsilon_{ij}, \qquad
   \sum_{i=1}^g \alpha_i = 0.

Here:

* :math:`\mu` is the overall mean.
* :math:`\alpha_i` is the **effect** of group :math:`i` (difference from
  the overall mean).
* :math:`\sigma^2` is the common within-group variance.

We test whether the group means are all equal:

.. math::

   H_0: \mu_1 = \mu_2 = \cdots = \mu_g
   \quad \text{vs} \quad
   H_1: \text{at least one } \mu_i \text{ is different}.

ANOVA works by decomposing variability:

* **Between-group** variability – how far the group means are from the overall
  mean.
* **Within-group** variability – how much observations vary around their own
  group mean.

If between-group variation is large relative to within-group variation, the
group means are unlikely to be all the same.

Sums of squares (conceptually)
------------------------------

We can write three key quantities:

* Total variation:

  .. math::

     SS_T = \sum_{i=1}^g \sum_{j=1}^{n_i} (y_{ij} - \bar{y})^2.

* Between-group variation:

  .. math::

     SS_B = \sum_{i=1}^g n_i(\bar{y}_i - \bar{y})^2.

* Within-group variation:

  .. math::

     SS_W = \sum_{i=1}^g \sum_{j=1}^{n_i} (y_{ij} - \bar{y}_i)^2.

These satisfy :math:`SS_T = SS_B + SS_W`.

The ANOVA :math:`F` statistic compares mean squares:

.. math::

   MS_B = \frac{SS_B}{g-1}, \qquad
   MS_W = \frac{SS_W}{N-g}, \qquad
   F = \frac{MS_B}{MS_W},

where :math:`N = \sum_i n_i` is the total sample size.

Under :math:`H_0`, :math:`F` has an :math:`F_{g-1, N-g}` distribution.

12.3.2 One-way ANOVA in Python
------------------------------

Suppose we have a DataFrame with columns:

* ``response`` – numeric outcome,
* ``group`` – categorical factor (diet, treatment, etc.).

Using :mod:`statsmodels`:

.. code-block:: python

   import statsmodels.api as sm
   import statsmodels.formula.api as smf

   model = smf.ols("response ~ C(group)", data=df).fit()
   anova_table = sm.stats.anova_lm(model, typ=2)
   print(anova_table)

Key points:

* ``C(group)`` tells :mod:`statsmodels` to treat ``group`` as categorical.
* The ANOVA table includes sums of squares, degrees of freedom, mean squares,
  :math:`F` statistic and p-value.

R uses

.. code-block:: r

   aov(response ~ group, data = df)

The underlying ideas are the same; both are just linear models with dummy
variables for the groups.

12.3.3 Factor variables and categorical dtype
---------------------------------------------

In R you must ensure the grouping variable is a **factor**; otherwise ANOVA
silently becomes a regression with a numeric predictor.

In Python / pandas:

* Either wrap the variable in ``C()`` in the formula, **or**
* set ``df["group"] = df["group"].astype("category")``.

If you forget and leave it numeric, the model becomes “line through the codes”
(1, 2, 3, …) rather than separate means per group.

12.3.4 Simulating the F distribution in Python
----------------------------------------------

A good sanity check is to simulate from a null model (equal means) and verify
that the empirical distribution of :math:`F` matches the theoretical
:math:`F` distribution.

Skeleton code:

.. code-block:: python

   import numpy as np
   import pandas as pd
   import statsmodels.api as sm
   import statsmodels.formula.api as smf

   rng = np.random.default_rng(seed=123)

   def sim_oneway_F(n_per_group=10, g=4, sigma=1.0):
       # Null model: all means = 0
       groups = np.repeat(np.arange(g), n_per_group)
       y = rng.normal(loc=0.0, scale=sigma, size=g * n_per_group)
       df = pd.DataFrame({"y": y, "group": groups})
       model = smf.ols("y ~ C(group)", data=df).fit()
       table = sm.stats.anova_lm(model, typ=2)
       return table.loc["C(group)", "F"]

   f_stats = np.array([sim_oneway_F() for _ in range(5000)])

You can then plot a histogram of ``f_stats`` and overlay an
``scipy.stats.f`` density to see the agreement.

12.3.5 Power via simulation
---------------------------

Because experiments cost time and money, we care about **power**:

.. math::

   \text{Power} = P(\text{reject } H_0 \mid H_0 \text{ false}).

For one-way ANOVA this depends on:

* effect sizes (how far the group means are apart),
* noise level :math:`\sigma`,
* sample size and balance (equal :math:`n_i` helps),
* significance level :math:`\alpha`.

We can use almost the same simulation function as above, but now draw from
unequal means and record how often the ANOVA p-value is below :math:`\alpha`.

Sketch:

.. code-block:: python

   from scipy import stats

   def sim_oneway_p(mu, n_per_group=10, sigma=1.0):
       mu = np.asarray(mu)
       g = len(mu)
       groups = np.repeat(np.arange(g), n_per_group)
       means = np.repeat(mu, n_per_group)
       y = rng.normal(loc=means, scale=sigma, size=g * n_per_group)
       df = pd.DataFrame({"y": y, "group": groups})
       model = smf.ols("y ~ C(group)", data=df).fit()
       table = sm.stats.anova_lm(model, typ=2)
       return table.loc["C(group)", "PR(>F)"]

   p_vals = np.array([sim_oneway_p(mu=[-1, 0, 0, 1], sigma=1.5)
                      for _ in range(1000)])

   power_05 = np.mean(p_vals < 0.05)
   power_01 = np.mean(p_vals < 0.01)

By varying ``mu``, ``sigma``, and sample size you can explore how design
choices affect power.

12.4 Post-hoc comparisons and multiple testing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ANOVA answers a global question:

*“Are all group means equal?”*

If the F-test is significant, we often want to know **which means differ**.

Naive approach
--------------

Run all pairwise two-sample t-tests and look at their p-values. But if there
are many groups, this inflates the **family-wise error rate (FWER)**: the
probability of at least one false positive among the whole family of tests.

Example: with 10 independent tests at :math:`\alpha = 0.05`, the probability
of at least one false positive is much larger than 0.05.

Bonferroni adjustment
---------------------

One simple fix:

*Either* use a stricter per-test level :math:`\alpha / m` for :math:`m` tests,  
*or* multiply each p-value by :math:`m` (capped at 1).

Python:

.. code-block:: python

   from statsmodels.stats.multitest import multipletests

   # pvals: array of unadjusted p-values from pairwise t-tests
   reject, pvals_adj, _, _ = multipletests(pvals, alpha=0.05,
                                           method="bonferroni")

Tukey’s HSD
-----------

For “all pairwise comparisons of group means after one-way ANOVA” there is a
classical procedure: **Tukey’s Honest Significant Difference**.

In Python, :mod:`statsmodels` provides:

.. code-block:: python

   from statsmodels.stats.multicomp import pairwise_tukeyhsd

   tukey = pairwise_tukeyhsd(endog=df["response"],
                             groups=df["group"],
                             alpha=0.05)
   print(tukey.summary())

This reports:

* which pairs of means differ significantly,
* adjusted p-values,
* simultaneous confidence intervals for mean differences.

12.5 Two-way ANOVA and interactions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

One-way ANOVA handles one factor. Real experiments often manipulate **two or
more factors at once**.

Example design:

* factor A: three types of antibiotic (I, II, III),
* factor B: four treatments (A, B, C, D),
* response: survival time of a bacteria cluster.

Model with interaction
----------------------

With factors A and B, levels :math:`i = 1,\dots,I`, :math:`j=1,\dots,J`, and
replicates :math:`k = 1,\dots,K` per cell, we write

.. math::

   Y_{ijk} = \mu + \alpha_i + \beta_j + (\alpha\beta)_{ij} + \varepsilon_{ijk},

where :math:`\varepsilon_{ijk} \sim N(0, \sigma^2)`.

* :math:`\alpha_i` – main effect of factor A,
* :math:`\beta_j` – main effect of factor B,
* :math:`(\alpha\beta)_{ij}` – **interaction** between A and B.

Interpretation of interaction:

*The effect of A depends on the level of B (or vice versa).*

Additive model (no interaction)
-------------------------------

If all interaction terms are zero we have

.. math::

   Y_{ijk} = \mu + \alpha_i + \beta_j + \varepsilon_{ijk}.

The difference between two levels of factor A is the same at every level of
factor B.

Model hierarchy and testing strategy
------------------------------------

Typically we proceed in this order:

1. Fit the **full interaction model**.
2. Test whether the interaction is significant.
3. If interaction *is* significant, stop there and interpret it.
4. If interaction is *not* significant, drop it and fit the **additive model**
   with main effects only.
5. Within the additive model you can test main effects and use Tukey-type
   post-hoc comparisons on each factor.

Two-way ANOVA in Python
-----------------------

Assume a DataFrame ``bacteria`` with columns ``time`` (response),
``antibiotic`` (factor A), and ``treat`` (factor B).

Full interaction model:

.. code-block:: python

   import statsmodels.api as sm
   import statsmodels.formula.api as smf

   model_int = smf.ols("time ~ C(antibiotic) * C(treat)", data=bacteria).fit()
   anova_int = sm.stats.anova_lm(model_int, typ=2)
   print(anova_int)

If the ``antibiotic:treat`` row has a small p-value, keep this model and examine
estimated means for each combination.

To get cell means:

.. code-block:: python

   import itertools
   import pandas as pd

   levels_antibiotic = bacteria["antibiotic"].unique()
   levels_treat = bacteria["treat"].unique()

   grid = pd.DataFrame(
       list(itertools.product(levels_antibiotic, levels_treat)),
       columns=["antibiotic", "treat"],
   )
   cell_means = model_int.predict(grid)
   grid["mean_time"] = cell_means
   print(grid)

If the interaction is not significant, fit the additive model:

.. code-block:: python

   model_add = smf.ols("time ~ C(antibiotic) + C(treat)", data=bacteria).fit()
   anova_add = sm.stats.anova_lm(model_add, typ=2)

   print(anova_add)

You can then run Tukey’s HSD separately on ``antibiotic`` and ``treat``.

Interaction plots
-----------------

Before fitting any models, it is helpful to **plot group means**.

In Python you can approximate R’s ``interaction.plot`` using a line plot of
mean response vs one factor, with a separate line for each level of the other
factor (for example with :mod:`seaborn`’s ``pointplot``).

Parallel lines suggest an additive model; clearly crossing lines suggest an
interaction.

12.6 What you should take away
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By the end of this chapter you should be comfortable with:

* clearly distinguishing **observational** vs **experimental** data,
* explaining why experiments (with randomization) are needed for causal
  statements,
* writing down the models for

  * two-sample t-tests,
  * one-way ANOVA,
  * two-way ANOVA with and without interaction,

* reading an ANOVA table: sums of squares, degrees of freedom, mean squares,
  :math:`F` statistics, and p-values,
* using Python tools to perform

  * two-sample t-tests (:mod:`scipy.stats`),
  * one-way ANOVA (:mod:`statsmodels` with ``C(group)``),
  * post-hoc comparisons with multiple-testing corrections,
  * two-way ANOVA and interaction tests,

* understanding the idea of **power** and how simulation can help plan sample
  sizes,
* appreciating that “statistically significant” is not automatically
  “scientifically important” – you still need to think about effect sizes.

12.7 How this connects to PyStatsV1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In later PyStatsV1 chapters and case studies you will see these ideas appear in
several ways:

* using ANOVA as a special case of the linear models you already know,
* connecting experimental designs to regression models with dummy variables,
* simulating power curves before you “run an experiment in code,”
* contrasting what you can say from experimental data versus observational
  data using the same modelling tools.

If you work in psychology, sports science, education, or any field with
interventions, this chapter provides the conceptual bridge from PyStatsV1’s
regression techniques to the world of **experimental design** and **evidence-based
practice**.
