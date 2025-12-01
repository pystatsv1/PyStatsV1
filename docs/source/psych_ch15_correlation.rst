Chapter 15 – Correlation
==========================

In the previous chapters you learned how to *compare groups* using
t-tests and ANOVA.  Those designs are built around **experimental**
questions:

*Does changing X cause a difference in Y?*

In this chapter we turn to **association** questions:

*Do X and Y move together?  If so, how strongly and in what direction?*

Correlation is the workhorse of non-experimental psychology.
It is used to study relationships between naturally occurring variables
such as stress, sleep, depression, and exam performance.  You will see
correlation again in the next chapter as the foundation of
**linear regression**.

This chapter focuses on three big ideas:

* how to quantify the direction and strength of a linear relationship,
* how to read and interpret scatterplots,
* and why **correlation does not imply causation**.

At the end, the PyStatsV1 lab shows how to compute and visualise
correlations in Python using both NumPy/pandas and the
:mod:`pingouin` statistics library.


15.1 What Is a Correlation?
---------------------------

A **correlation** is a number that describes how two variables are
related.  In this chapter we focus on the most common measure:
the **Pearson product–moment correlation**, usually written as :math:`r`.

Pearson's :math:`r` tells you two things:

* **Direction** – whether high scores on one variable tend to go with
  high scores on the other (a *positive* correlation), or with low
  scores on the other (a *negative* correlation).
* **Strength** – how tightly the points cluster around a straight line.

The value of :math:`r` always lies between -1 and +1:

* :math:`r = +1.00` – a perfect positive linear relationship
* :math:`r = -1.00` – a perfect negative linear relationship
* :math:`r = 0` – no linear relationship

In real data, :math:`r` is almost never exactly -1, 0, or +1.  Instead
we see values like :math:`r = .10` (a weak relationship) or
:math:`r = .60` (a moderately strong relationship).


15.2 Computing Pearson's r
--------------------------

Conceptually, Pearson's :math:`r` is the **standardized covariance**
between two variables:

.. math::

   r = \frac{\text{cov}(X, Y)}{s_X s_Y}

Here :math:`\text{cov}(X, Y)` is the covariance between :math:`X` and
:math:`Y`, and :math:`s_X` and :math:`s_Y` are their sample standard
deviations.  Covariance captures whether high values of :math:`X`
tend to go with high (or low) values of :math:`Y`.  Dividing by the
standard deviations rescales the covariance to the familiar
-1 to +1 range.

In practice, you will almost always compute :math:`r` using software.
However, it is important to understand the basic ingredients:

1. Convert :math:`X` and :math:`Y` to **z-scores**.
2. Multiply the paired z-scores :math:`z_X z_Y` for each participant.
3. Average these cross-products.

The resulting average is exactly Pearson's :math:`r`.  When most
participants have the **same sign** of :math:`z_X` and :math:`z_Y`,
the cross-products are positive and :math:`r` is positive.  When
participants tend to have opposite signs (high on one variable,
low on the other), :math:`r` is negative.


15.3 Scatterplots and Visual Intuition
--------------------------------------

Before computing any correlation, you should **plot the data**.

A **scatterplot** places one variable on the x-axis and the other on
the y-axis.  Each participant is one point.

Scatterplots help you answer questions that the single number :math:`r`
cannot:

* Is the relationship **linear** or curved?
* Are there **outliers** that might distort the correlation?
* Does the variability change across the range of :math:`X`?

For example, a strong curved relationship can produce
:math:`r \approx 0` even though :math:`X` clearly predicts :math:`Y`.
Likewise, a single extreme outlier can produce a large :math:`r` that
does not represent the pattern for most participants.

.. important::

   **Always inspect a scatterplot before interpreting a correlation.**
   The number :math:`r` is helpful, but it is not a substitute for
   looking at the data.


15.4 Correlation Does Not Imply Causation
-----------------------------------------

Psychology students often hear the slogan:
**"Correlation does not imply causation."**
It is worth unpacking why this is true.

Suppose you find a strong positive correlation between time spent
on social media and self-reported anxiety.  At least three causal
stories are possible:

1. **Social media causes anxiety.**
2. **Anxiety causes social media use** (perhaps anxious people are
   more likely to scroll in bed).
3. A **third variable** (e.g., loneliness, insomnia) causes both
   heavy social media use and anxiety.

A correlation alone cannot distinguish between these possibilities.
To make a causal claim, you need an appropriate **research design**,
such as an experiment with random assignment or a carefully controlled
longitudinal study.

In this book we encourage the following mindset:

*Use correlation to describe and explore relationships,  
use experimental design to test causal claims.*


15.5 Partial Correlation: Controlling for a Third Variable
----------------------------------------------------------

Sometimes you want to know whether two variables are related
**after controlling for** another variable.  For example:

* Does study time predict exam score **after controlling for**
  prior GPA?
* Does therapy attendance predict symptom improvement **after controlling
  for** baseline severity?

A **partial correlation** answers questions like these.  It measures
the relationship between :math:`X` and :math:`Y` *after removing the
linear effect* of a third variable (or set of variables).

One way to think about this:

1. Regress :math:`X` on the control variable(s) and keep the residuals.
2. Regress :math:`Y` on the control variable(s) and keep the residuals.
3. Correlate the two sets of residuals.

The resulting partial correlation tells you whether :math:`X` and
:math:`Y` still move together once the shared influence of the control
variable has been removed.

You do not need to implement these regression steps by hand.
Libraries such as :mod:`pingouin` and :mod:`statsmodels` can compute
partial correlations directly from a tidy data frame.


15.6 PyStatsV1 Lab – Correlation in Python
------------------------------------------

The PyStatsV1 lab for this chapter is implemented in the script
:mod:`scripts.psych_ch15_correlation`.  It demonstrates three key
skills:

1. **Simulating data with a known population correlation**

   We use NumPy to simulate pairs of scores from a bivariate normal
   distribution with a specified population correlation (for example,
   :math:`\rho = .50`).  This allows us to check whether our estimation
   procedures recover the true value.

2. **Computing correlations with NumPy and Pingouin**

   The script shows how to compute Pearson's :math:`r` in two ways:

   * using NumPy / pandas:

     .. code-block:: python

        import numpy as np

        r_np = np.corrcoef(df["x"], df["y"])[0, 1]

   * using :mod:`pingouin`, which also returns p-values,
     confidence intervals, Bayes factors, and power:

     .. code-block:: python

        import pingouin as pg

        corr_table = pg.corr(df["x"], df["y"], method="pearson")
        r_pg = corr_table["r"].iloc[0]

   In our automated tests we verify that ``r_np`` and ``r_pg`` are
   essentially identical, and that :mod:`pingouin` recovers the
   population correlation used to generate the data.

3. **Correlation matrices, heatmaps, and partial correlations**

   The script also simulates a small set of psychology variables
   (for example, stress, sleep, anxiety, and exam scores) and then:

   * computes a full correlation matrix,
   * visualises the matrix as a color-coded heatmap,
   * and calculates a partial correlation, such as the association
     between study time and exam performance after controlling
     for motivation.

   These analyses use :mod:`pingouin` helper functions such as
   :func:`pingouin.pairwise_corr` and :func:`pingouin.partial_corr`.

The synthetic data are saved in the
``data/synthetic/psych_ch15_correlation.csv`` file, and the heatmap
is written to
``outputs/track_b/ch15_corr_heatmap.png`` for easy inclusion in slides
or lecture notes.

.. note::

   In Chapters 15–19 we rely increasingly on :mod:`pingouin` and
   :mod:`statsmodels` for the actual statistical computations.
   PyStatsV1 focuses on **simulation, data management, and workflow**,
   while these libraries provide well-tested implementations of
   advanced techniques (correlation, regression, mixed ANOVA, ANCOVA,
   and more).  Our unit tests use simulated data with known answers
   to check that these tools behave as expected in the scenarios we
   teach.
