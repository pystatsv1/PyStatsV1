Applied Statistics with Python – Chapter 5
==========================================

Probability and statistics in Python and R
------------------------------------------

This chapter mirrors the **“Probability and Statistics in R”** chapter from the
R notes. We’ll keep the *statistical* ideas the same, but express them in
Python-first terms.

By the end of this chapter you should be comfortable with:

- using library functions to work with common distributions,
- translating between **pdf / cdf / quantile / random draws**,  
- performing basic **t-tests** in Python (one-sample and two-sample),
- and using **simulation** to understand probability results.

Where the R notes show functions like ``dnorm()``, ``qbinom()``, or
``t.test()``, we’ll highlight the Python equivalents from:

- :mod:`scipy.stats`
- :mod:`numpy.random`
- and a few plain-Python helper functions.


5.1 Probability in Python (and R)
=================================

5.1.1 Distribution helpers: pdf, cdf, quantiles, random draws
-------------------------------------------------------------

In the R book you see the pattern:

- ``dname`` – density or pmf (pdf),
- ``pname`` – cumulative distribution function (cdf),
- ``qname`` – quantile function,
- ``rname`` – random draws.

For example, ``dnorm()``, ``pnorm()``, ``qnorm()``, ``rnorm()`` for the Normal
distribution, or ``dbinom()``, ``pbinom()`` and so on.

In Python, the roles are similar but the interface is a little different.

The most convenient toolkit is :mod:`scipy.stats`. Each distribution is an
object with methods and “frozen” versions.

For a Normal distribution with mean 2 and standard deviation 5:

.. code-block:: python

    import numpy as np
    from scipy import stats

    dist = stats.norm(loc=2, scale=5)

    # pdf (density) at x = 3
    pdf_at_3 = dist.pdf(3)

    # cdf at x = 3, P(X <= 3)
    cdf_at_3 = dist.cdf(3)

    # 97.5th percentile (quantile)
    q_975 = dist.ppf(0.975)

    # random sample of size n = 10
    sample = dist.rvs(size=10, random_state=42)

The mapping to the R notation is:

- R ``dnorm(x, mean, sd)`` → Python ``stats.norm(mean, sd).pdf(x)``
- R ``pnorm(q, mean, sd)`` → Python ``stats.norm(mean, sd).cdf(q)``
- R ``qnorm(p, mean, sd)`` → Python ``stats.norm(mean, sd).ppf(p)``
- R ``rnorm(n, mean, sd)`` → Python ``stats.norm(mean, sd).rvs(size=n)``


5.1.2 Other families: binomial, t, Poisson, chi-square, F
---------------------------------------------------------

The R chapter lists a family of distributions with the same ``d/p/q/r`` pattern.
In Python you will typically reach for:

- :class:`scipy.stats.binom` for binomial,
- :class:`scipy.stats.t` for Student’s t,
- :class:`scipy.stats.poisson` for Poisson,
- :class:`scipy.stats.chi2` for chi-square,
- :class:`scipy.stats.f` for F.

**Example – Binomial probability**

Compute :math:`P(Y = 6)` when :math:`Y \sim \text{Binomial}(n=10, p=0.75)`:

.. code-block:: python

    from scipy import stats

    # pmf (probability mass function) for a Binomial
    prob_y_eq_6 = stats.binom(n=10, p=0.75).pmf(6)

In R the same calculation would use ``dbinom(x = 6, size = 10, prob = 0.75)``.

Notice again:

- R’s “d” for discrete distributions is really the **pmf**,  
- Python exposes this as ``pmf`` for discrete and ``pdf`` for continuous.

You can explore other distributions in :mod:`scipy.stats` in exactly the same
way: create the frozen distribution object, then call ``pdf``, ``cdf``,
``ppf``, and ``rvs``.


5.2 Hypothesis tests in Python
==============================

The R notes briefly review hypothesis testing and then demonstrate t-tests.  
We’ll match that structure here, but show both:

- the **formula** (to demystify the test statistic), and
- the **convenience function** from :mod:`scipy.stats`.


5.2.1 One-sample t-test
------------------------

Set-up: we observe :math:`x_1, \dots, x_n` and want to test

.. math::

   H_0: \mu = \mu_0
   \quad \text{vs} \quad
   H_1: \mu \neq \mu_0,

assuming the data are approximately Normal with unknown variance.

The test statistic is

.. math::

   t =
   \frac{\bar{x} - \mu_0}{s / \sqrt{n}}
   \sim t_{n-1} \quad \text{under } H_0,

where :math:`\bar{x}` is the sample mean and :math:`s` the sample standard
deviation.

**Python implementation “by hand”**

We revisit the cereal-box example from the R notes: boxes labelled “16 oz”,
sample of 9 observed weights. (Here we just hard-code the data.)

.. code-block:: python

    import numpy as np
    from scipy import stats

    weights = np.array([15.5, 16.2, 16.1, 15.8, 15.6, 16.0, 15.8, 15.9, 16.2])
    mu_0 = 16

    n = len(weights)
    x_bar = weights.mean()
    s = weights.std(ddof=1)

    t_stat = (x_bar - mu_0) / (s / np.sqrt(n))
    df = n - 1

    # two-sided p-value
    p_value_two_sided = 2 * stats.t.sf(np.abs(t_stat), df=df)

For a **one-sided** alternative (for example :math:`H_1: \mu < \mu_0`):

.. code-block:: python

    p_value_less = stats.t.cdf(t_stat, df=df)       # P(T <= observed)
    p_value_greater = stats.t.sf(t_stat, df=df)     # P(T >= observed)

This mirrors what the R code is doing with ``t.test()`` and ``pt()``.


**Using SciPy’s convenience function**

.. code-block:: python

    # two-sided one-sample t-test against mu_0
    t_stat2, p_value2 = stats.ttest_1samp(weights, popmean=mu_0)

    # SciPy always reports a two-sided p-value; you can halve it
    # for a one-sided test if the sign of t matches your alternative.
    p_value_less = p_value2 / 2 if t_stat2 < 0 else 1 - p_value2 / 2

The important idea: whether you calculate :math:`t` by hand or use a helper
function, the **model assumptions** and **test structure** are the same as in
the R notes.


5.2.2 Two-sample t-test
-----------------------

Now suppose we have two independent samples:

.. math::

   X_1, \dots, X_n \sim N(\mu_x, \sigma^2),
   \quad
   Y_1, \dots, Y_m \sim N(\mu_y, \sigma^2),

and we want to test

.. math::

   H_0: \mu_x - \mu_y = 0
   \quad \text{vs} \quad
   H_1: \mu_x - \mu_y > 0,

under an equal-variance assumption.

The pooled-variance test statistic is

.. math::

   t =
   \frac{\bar{x} - \bar{y}}
        {s_p \sqrt{1/n + 1/m}}, \qquad
   s_p^2 = \frac{(n-1)s_x^2 + (m-1)s_y^2}{n + m - 2}.

**Python implementation “by hand”**

.. code-block:: python

    import numpy as np
    from scipy import stats

    x = np.array([70, 82, 78, 74, 94, 82])
    y = np.array([64, 72, 60, 76, 72, 80, 84, 68])

    n, m = len(x), len(y)
    x_bar, y_bar = x.mean(), y.mean()
    s_x = x.std(ddof=1)
    s_y = y.std(ddof=1)

    s_p = np.sqrt(((n - 1) * s_x**2 + (m - 1) * s_y**2) / (n + m - 2))
    t_stat = (x_bar - y_bar) / (s_p * np.sqrt(1 / n + 1 / m))
    df = n + m - 2

    # one-sided alternative H1: mu_x > mu_y
    p_value = stats.t.sf(t_stat, df=df)

**Using SciPy’s two-sample test**

.. code-block:: python

    t_stat2, p_value_two_sided = stats.ttest_ind(
        x, y, equal_var=True
    )

    # convert to one-sided p-value if desired
    p_value_greater = p_value_two_sided / 2 if t_stat2 > 0 else 1 - p_value_two_sided / 2

SciPy’s :func:`ttest_ind` mirrors R’s ``t.test(x, y, var.equal = TRUE)`` call.

For practical work you will usually:

1. check assumptions (rough normality, similar spreads),  
2. call the SciPy function,  
3. interpret :math:`t`, degrees of freedom, p-value, and confidence interval.


5.3 Simulation in Python
========================

The R chapter ends with simulations that illustrate how probability results
behave in practice. We’ll take the same examples and rewrite them in NumPy.

The pattern you’ll see throughout PyStatsV1 is:

- write small simulation functions,
- loop or vectorize to build many replicates,
- examine histograms and summary statistics.


5.3.1 Paired differences
------------------------

We consider two Normal populations with means :math:`\mu_1 = 6`,
:math:`\mu_2 = 5`, common variance :math:`\sigma^2 = 4`, and sample size
:math:`n = 25` in each group.

From theory, if :math:`\bar{X}_1` and :math:`\bar{X}_2` are the sample means and
:math:`D = \bar{X}_1 - \bar{X}_2`, then

.. math::

   D \sim N(\mu_1 - \mu_2, \sigma^2/n + \sigma^2/n)
     = N(1, 0.32).

We can compute :math:`P(0 < D < 2)` analytically using the Normal cdf:

.. code-block:: python

    from scipy import stats
    import numpy as np

    mu_D = 1.0
    var_D = 0.32
    sd_D = np.sqrt(var_D)

    prob_0_to_2 = stats.norm(mu_D, sd_D).cdf(2) - stats.norm(mu_D, sd_D).cdf(0)

Alternatively we can *simulate* many realizations of :math:`D` and approximate
this probability empirically.

.. code-block:: python

    rng = np.random.default_rng(seed=42)

    n = 25
    num_samples = 10_000

    x1 = rng.normal(loc=6, scale=2, size=(num_samples, n))
    x2 = rng.normal(loc=5, scale=2, size=(num_samples, n))

    diffs = x1.mean(axis=1) - x2.mean(axis=1)

    prob_sim = np.mean((diffs > 0) & (diffs < 2))

    diffs_mean = diffs.mean()
    diffs_var = diffs.var(ddof=1)

Here:

- ``prob_sim`` should be close to ``prob_0_to_2``,
- ``diffs_mean`` should be near 1,
- ``diffs_var`` should be near 0.32.

In later PyStatsV1 chapters we will use this pattern repeatedly to check the
behaviour of estimators and test statistics.


5.3.2 Distribution of a sample mean
-----------------------------------

The second example in the R notes studies the distribution of the sample mean
from a Poisson distribution and connects it to the Central Limit Theorem.

Let :math:`X \sim \text{Poisson}(\mu)` with :math:`\mu = 10`.  
We draw samples of size :math:`n = 50` and compute the sample mean
:math:`\bar{X}`. The CLT suggests

.. math::

   \bar{X} \approx N\left(\mu, \frac{\mu}{n}\right)

for moderately large :math:`n`.

In Python:

.. code-block:: python

    from scipy import stats
    import numpy as np

    rng = np.random.default_rng(seed=1337)

    mu = 10
    sample_size = 50
    num_samples = 100_000

    # each row: one sample of size n
    samples = rng.poisson(lam=mu, size=(num_samples, sample_size))
    x_bars = samples.mean(axis=1)

    # empirical mean and variance
    mean_emp = x_bars.mean()
    var_emp = x_bars.var(ddof=1)

    mean_theory = mu
    var_theory = mu / sample_size

You can then:

- plot a histogram of ``x_bars``,
- overlay a Normal density with mean ``mean_theory`` and variance
  ``var_theory``,
- and check proportions within 1, 2, or 3 standard deviations of the mean.

(We keep plotting code to a minimum here; later chapters will show more
matplotlib examples.)


5.4 What you should take away
=============================

By the end of this chapter (R + Python versions), you should be comfortable
with:

- **Using distribution helpers** to get pdf/pmf, cdf, quantiles, and random
  samples from common distributions in Python and R.
- **Translating between R and Python**: ``d* / p* / q* / r*`` functions in R
  correspond to ``pdf/pmf``, ``cdf``, ``ppf``, and ``rvs`` in
  :mod:`scipy.stats`.
- **Implementing t-tests** both “by hand” from the formulas and using
  convenience functions like :func:`scipy.stats.ttest_1samp` and
  :func:`scipy.stats.ttest_ind`.
- **Using simulation** to:
  - approximate probabilities,
  - understand sampling distributions,
  - and verify theoretical results.

If any of the code in this chapter feels new, try it interactively:

- change parameters (means, variances, sample sizes),
- re-run the simulations,
- see how the distribution of statistics (like :math:`\bar{X}` or the t-statistic)
  responds.

That experimentation will pay off quickly in the PyStatsV1 applied chapters,
where we’ll connect these probability tools directly to real case studies.
