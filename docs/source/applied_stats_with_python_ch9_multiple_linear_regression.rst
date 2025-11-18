.. _applied_stats_with_python_ch9_multiple_linear_regression:

Applied Statistics with Python – Chapter 9
==========================================

Multiple linear regression
--------------------------

This chapter mirrors the **“Multiple Linear Regression”** chapter from the
original R notes. The statistical ideas are the same, but we’ll express them in
Python-first language and keep R alongside as a translation layer.

By the end of this chapter you should be comfortable with:

* Building and interpreting linear regression models with **more than one
  predictor**.
* Understanding the **matrix formulation** of regression.
* Using summary output to:

  * obtain **standard errors** and **t-tests** for each coefficient,
  * construct **confidence intervals** and **prediction intervals**,
  * run **global F-tests** for the significance of regression,
  * and compare **nested models** with ANOVA F-tests.

* Connecting these ideas back to simulation: checking a theoretical sampling
  distribution with code.

Throughout we will:

* Treat **R**’s ``lm()`` as the reference implementation, and
* Show Python equivalents using ``pandas`` and ``statsmodels``.

9.1 From simple to multiple regression
--------------------------------------

In simple linear regression (SLR) we had one predictor:

.. math::

   Y_i = \beta_0 + \beta_1 x_i + \varepsilon_i, \qquad
   \varepsilon_i \sim N(0, \sigma^2).

Graphically, this is a **line** through a cloud of points.

In multiple linear regression (MLR) we allow several predictors:

.. math::

   Y_i = \beta_0 + \beta_1 x_{i1} + \beta_2 x_{i2} + \cdots
         + \beta_{p-1} x_{i,p-1} + \varepsilon_i.

For two predictors you can picture a **plane** in 3-D space; for more predictors,
geometry is harder to visualize but the algebra scales cleanly.

Key idea: each :math:`\beta_j` is a **partial slope**:

* :math:`\beta_j` measures the change in the mean response for a one-unit change
  in :math:`x_j`, **holding all other predictors fixed**.

That “holding others fixed” interpretation is new in MLR and central to reading
regression output correctly.

9.2 Auto MPG example
--------------------

We’ll again use a car-fuel-efficiency dataset. In the R notes it’s read directly
from the UCI Machine Learning Repository and cleaned into a data frame
``autompg`` with columns:

* ``mpg`` – miles per gallon (response),
* ``cyl`` – number of cylinders,
* ``disp`` – engine displacement,
* ``hp`` – horsepower,
* ``wt`` – weight,
* ``acc`` – acceleration,
* ``year`` – model year.

In PyStatsV1, you can either:

* read the data from a local CSV we include, or
* follow the R code closely by reading from the URL and cleaning in Python.

A minimal Python version might look like:

.. code-block:: python

   import pandas as pd

   url = (
       "http://archive.ics.uci.edu/ml/machine-learning-databases/"
       "auto-mpg/auto-mpg.data"
   )

   cols = ["mpg", "cyl", "disp", "hp", "wt", "acc", "year", "origin", "name"]
   autompg = pd.read_csv(
       url,
       delim_whitespace=True,
       names=cols,
       na_values="?",
       comment="#",
   )

   # Drop rows with missing horsepower and the Plymouth Reliant row,
   # then drop unused columns to match the R notes
   autompg = autompg.dropna(subset=["hp"])
   autompg = autompg[autompg["name"] != "plymouth reliant"]
   autompg = autompg[["mpg", "cyl", "disp", "hp", "wt", "acc", "year"]]
   autompg["hp"] = autompg["hp"].astype(float)

   autompg.info()

This gets us to the same cleaned structure as in R.

9.3 Fitting a multiple regression model
---------------------------------------

We’ll start with a two-predictor model: mpg as a function of weight and year.

Model:

.. math::

   Y_i = \beta_0 + \beta_1 \text{wt}_i + \beta_2 \text{year}_i + \varepsilon_i.

R version
^^^^^^^^^

.. code-block:: r

   mpg_model <- lm(mpg ~ wt + year, data = autompg)
   summary(mpg_model)

Python version (statsmodels)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We’ll use the formula API, which understands ``"mpg ~ wt + year"`` like ``lm()``.

.. code-block:: python

   import statsmodels.formula.api as smf

   mpg_model = smf.ols("mpg ~ wt + year", data=autompg).fit()
   print(mpg_model.summary())

You should see:

* estimates for ``Intercept``, ``wt``, and ``year``,
* standard errors and t-values,
* residual standard error (``sigma``),
* :math:`R^2` and adjusted :math:`R^2`,
* and an F-statistic testing whether the regression as a whole is useful.

Interpreting the coefficients
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using the R output notation, suppose we get:

* :math:`\hat\beta_0 \approx -14.6`
* :math:`\hat\beta_1 \approx -0.0066` for weight
* :math:`\hat\beta_2 \approx 0.76` for year

Interpretations:

* **Intercept**: expected mpg for a car of weight 0 made in year 0. This is
  physically meaningless, but needed algebraically. Intercepts often have poor
  real-world meaning but are still part of the model.

* **Weight slope**: for a one-unit increase in weight (one pound in these data),
  expected mpg **decreases** by about 0.0066, **holding model year fixed**.

* **Year slope**: for a one-unit increase in model year (one year newer),
  expected mpg **increases** by about 0.76, **holding weight fixed**.

Notice how every slope interpretation now includes “for a fixed value of the
other predictor”.

9.4 Matrix formulation of regression
------------------------------------

Matrix notation lets us handle any number of predictors cleanly.

We stack the response values into a vector :math:`Y`, the predictors into a
design matrix :math:`X`, the coefficients into a vector :math:`\beta`, and the
errors into a vector :math:`\varepsilon`:

.. math::

   Y = X \beta + \varepsilon.

* :math:`Y` is :math:`n \times 1`,
* :math:`X` is :math:`n \times p` (first column all ones for the intercept),
* :math:`\beta` is :math:`p \times 1`,
* :math:`\varepsilon` is :math:`n \times 1`.

The least squares estimate of :math:`\beta` is:

.. math::

   \hat\beta = (X^\top X)^{-1} X^\top y.

The fitted values and residuals are:

.. math::

   \hat y = X \hat\beta, \qquad e = y - \hat y.

The residual variance estimate (mean squared error) is:

.. math::

   s_e^2 = \frac{e^\top e}{n - p},

where :math:`n` is the sample size and :math:`p` is the number of :math:`\beta`
parameters (including the intercept). Compare this to SLR:

* SLR had :math:`p = 2` and denominator :math:`n - 2`,
* here we allow general :math:`p`, so the denominator is :math:`n - p`.

Python check
^^^^^^^^^^^^

We can verify that ``statsmodels`` is doing exactly this:

.. code-block:: python

   import numpy as np

   y = autompg["mpg"].to_numpy()
   X = np.column_stack([
       np.ones(len(autompg)),   # intercept
       autompg["wt"].to_numpy(),
       autompg["year"].to_numpy(),
   ])

   XtX_inv = np.linalg.inv(X.T @ X)
   beta_hat = XtX_inv @ X.T @ y

   print(beta_hat)                 # matches mpg_model.params

   y_hat = X @ beta_hat
   e = y - y_hat
   n, p = X.shape
   s_e = np.sqrt((e @ e) / (n - p))
   print(s_e, mpg_model.mse_resid**0.5)

9.5 Sampling distribution of :math:`\hat\beta`
----------------------------------------------

Under the normal-error assumptions of the linear model:

* :math:`\varepsilon \sim N(0, \sigma^2 I)`,

we can show (using multivariate normal theory) that:

.. math::

   \hat\beta \sim N\!\bigl(\beta,\, \sigma^2 (X^\top X)^{-1}\bigr).

Consequences:

* :math:`E[\hat\beta] = \beta` – each coefficient estimate is **unbiased**.
* The covariance matrix of :math:`\hat\beta` is :math:`\sigma^2 (X^\top X)^{-1}`.
  The diagonal elements give the variances of individual coefficients.

If we call :math:`C = (X^\top X)^{-1}`, then

.. math::

   \operatorname{Var}(\hat\beta_j) = \sigma^2 C_{jj},
   \qquad
   SE(\hat\beta_j) = s_e \sqrt{C_{jj}}.

Each coefficient has a t-distribution after standardization:

.. math::

   \frac{\hat\beta_j - \beta_j}{s_e \sqrt{C_{jj}}}
   \sim t_{n-p}.

In practice we rarely compute :math:`C` by hand; we read standard errors from
software.

* R: ``summary(mpg_model)$coef``
* Python: ``mpg_model.params`` and ``mpg_model.bse``

9.6 Testing individual coefficients
-----------------------------------

To test whether a specific predictor is useful in the presence of the others, we
typically test

.. math::

   H_0: \beta_j = 0 \quad \text{vs} \quad H_1: \beta_j \neq 0.

Test statistic:

.. math::

   t = \frac{\hat\beta_j - 0}{SE(\hat\beta_j)}
     = \frac{\hat\beta_j}{s_e \sqrt{C_{jj}}}
   \sim t_{n-p} \quad \text{under } H_0.

R version
^^^^^^^^^

.. code-block:: r

   summary(mpg_model)$coef

The ``Estimate``, ``Std. Error``, ``t value``, and ``Pr(>|t|)`` columns give
exactly this test.

Python version
^^^^^^^^^^^^^^

.. code-block:: python

   mpg_model.params      # estimates
   mpg_model.bse         # standard errors
   mpg_model.tvalues     # t statistics
   mpg_model.pvalues     # two-sided p-values

If the p-value for ``wt`` is tiny, we reject :math:`H_0: \beta_{\text{wt}} = 0` and
conclude weight is a useful predictor, *given that year is already in the model*.

This “given that …” interpretation is crucial: the t-test evaluates a coefficient
**conditional on the other predictors in the model**, not in isolation.

9.7 Confidence intervals for coefficients and mean response
-----------------------------------------------------------

Intervals for coefficients
^^^^^^^^^^^^^^^^^^^^^^^^^^

From the sampling distribution we get a :math:`(1-\alpha)` confidence interval:

.. math::

   \hat\beta_j \pm t_{\alpha/2,\, n-p} \cdot SE(\hat\beta_j).

R:

.. code-block:: r

   confint(mpg_model, level = 0.99)

Python:

.. code-block:: python

   mpg_model.conf_int(alpha=0.01)

Intervals for mean response
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Suppose we want the mean mpg for cars with specified predictors
:math:`x_0 = (1, x_{01}, \dots, x_{0,p-1})^\top`. The fitted mean is

.. math::

   \hat y(x_0) = x_0^\top \hat\beta.

Its standard error is

.. math::

   SE\bigl(\hat y(x_0)\bigr)
   = s_e \sqrt{x_0^\top (X^\top X)^{-1} x_0}.

A :math:`(1-\alpha)` confidence interval is

.. math::

   \hat y(x_0) \pm t_{\alpha/2,\, n-p} \cdot
   s_e \sqrt{x_0^\top (X^\top X)^{-1} x_0}.

R:

.. code-block:: r

   new_cars <- data.frame(wt = c(3500, 5000),
                          year = c(76, 81))

   predict(mpg_model, newdata = new_cars,
           interval = "confidence", level = 0.99)

Python:

.. code-block:: python

   new_cars = pd.DataFrame({"wt": [3500, 5000],
                            "year": [76, 81]})

   pred = mpg_model.get_prediction(new_cars)
   pred.summary_frame(alpha=0.01)[["mean", "mean_ci_lower", "mean_ci_upper"]]

9.8 Prediction intervals
------------------------

Prediction intervals account for both:

* uncertainty in the mean, and
* variability of individual observations around that mean.

Standard error:

.. math::

   SE_{\text{pred}}\bigl(\hat y(x_0)\bigr)
   = s_e \sqrt{1 + x_0^\top (X^\top X)^{-1} x_0}.

Prediction interval:

.. math::

   \hat y(x_0) \pm t_{\alpha/2,\, n-p} \cdot
   s_e \sqrt{1 + x_0^\top (X^\top X)^{-1} x_0}.

R:

.. code-block:: r

   predict(mpg_model, newdata = new_cars,
           interval = "prediction", level = 0.99)

Python:

.. code-block:: python

   pred.summary_frame(alpha=0.01)[
       ["obs_ci_lower", "obs_ci_upper"]
   ]

Warning about extrapolation
^^^^^^^^^^^^^^^^^^^^^^^^^^^

With multiple predictors, extrapolation can be subtle. Each new point must be
reasonable **in the joint predictor space**, not just in each coordinate
separately. A car with an unusual combination of weight and year may be far
from the existing data cloud even if its weight and year separately look
“within range”.

Plotting predictors against each other and marking new points is a good
sanity check.

9.9 Significance of regression: global F-test
---------------------------------------------

In SLR, the t-test for the slope and the F-test for the model were equivalent.
In MLR they separate:

* Individual t-tests: “Is this particular predictor useful, given the others?”
* Global F-test: “Is **any** linear relationship present at all?”

Null hypothesis for the global F-test:

.. math::

   H_0: \beta_1 = \beta_2 = \cdots = \beta_{p-1} = 0.

Under :math:`H_0` the model reduces to

.. math::

   Y_i = \beta_0 + \varepsilon_i,

an intercept-only model. The F-statistic is based on the variance decomposition

.. math::

   \text{SST} = \text{SSReg} + \text{SSE},

and compares mean squares:

.. math::

   F =
   \frac{\text{SSReg} / (p-1)}{\text{SSE} / (n-p)}
   \sim F_{p-1,\, n-p} \quad \text{under } H_0.

Software gives this automatically.

R:

.. code-block:: r

   summary(mpg_model)$fstatistic  # F and df
   # or
   null_mpg_model <- lm(mpg ~ 1, data = autompg)
   anova(null_mpg_model, mpg_model)

Python:

.. code-block:: python

   mpg_model.fvalue, mpg_model.f_pvalue, mpg_model.df_model, mpg_model.df_resid

A tiny p-value says: “At least one predictor has a non-zero slope; the regression
as a whole explains a meaningful amount of variation.”

9.10 Nested model comparisons
-----------------------------

Often we want to compare two models where one is a **subset** of the other.

Example:

* **Reduced (null) model**: ``mpg ~ wt + year``
* **Full model**: ``mpg ~ wt + year + cyl + disp + hp + acc``

Here the reduced model is nested inside the full model. The null hypothesis is:

.. math::

   H_0: \beta_{\text{cyl}} = \beta_{\text{disp}} =
        \beta_{\text{hp}} = \beta_{\text{acc}} = 0.

We use an F-test based on the extra sum of squares explained by the full model.

R:

.. code-block:: r

   null_mpg_model <- lm(mpg ~ wt + year, data = autompg)
   full_mpg_model <- lm(mpg ~ wt + year + cyl + disp + hp + acc,
                        data = autompg)

   anova(null_mpg_model, full_mpg_model)

Python (statsmodels):

.. code-block:: python

   import statsmodels.api as sm

   null_mpg_model = smf.ols("mpg ~ wt + year", data=autompg).fit()
   full_mpg_model = smf.ols("mpg ~ wt + year + cyl + disp + hp + acc",
                            data=autompg).fit()

   sm.stats.anova_lm(null_mpg_model, full_mpg_model)

If the p-value is large, the extra predictors don’t improve the model
significantly given ``wt`` and ``year``.

The global significance-of-regression test from the previous section is a special
case where the reduced model is intercept-only.

9.11 Simulation: checking the sampling distribution
---------------------------------------------------

The R notes close with a simulation study that:

* fixes a design matrix :math:`X`,
* simulates many response vectors from a known linear model,
* refits the regression each time,
* and looks at the empirical distribution of one coefficient.

You can implement the same idea in Python. Sketch:

.. code-block:: python

   import numpy as np
   import pandas as pd
   import statsmodels.api as sm

   rng = np.random.default_rng(1337)

   n = 100
   x1 = np.linspace(1, 10, n)
   x2 = np.linspace(1, 10, n)[::-1]

   beta_true = np.array([5.0, -2.0, 6.0])
   sigma = 4.0

   X = np.column_stack([np.ones(n), x1, x2])

   num_sims = 10_000
   beta2_vals = np.empty(num_sims)

   for i in range(num_sims):
       eps = rng.normal(0, sigma, size=n)
       y = X @ beta_true + eps

       df = pd.DataFrame({"x1": x1, "x2": x2, "y": y})
       fit = smf.ols("y ~ x1 + x2", data=df).fit()
       beta2_vals[i] = fit.params["x2"]

   beta2_vals.mean(), beta2_vals.var()

You should find:

* the mean of ``beta2_vals`` is close to the true :math:`\beta_2`,
* the variance matches :math:`\sigma^2 C_{22}` where :math:`C = (X^\top X)^{-1}`,
* a histogram of ``beta2_vals`` overlaid with the corresponding Normal density
  looks very similar.

This is a concrete demonstration of the theoretical sampling distribution
results from Section 9.5.

9.12 What you should take away
------------------------------

By the end of this chapter (and its R + Python versions), you should be able to:

* Write down and interpret a **multiple linear regression model** with several
  predictors.
* Understand and use the **matrix formulation**:

  * :math:`Y = X \beta + \varepsilon`,
  * :math:`\hat\beta = (X^\top X)^{-1} X^\top y`,
  * residual variance :math:`s_e^2 = e^\top e / (n - p)`.

* Read software output to obtain:

  * coefficient estimates, standard errors, t-tests, and p-values,
  * confidence intervals for coefficients and for mean responses,
  * prediction intervals for new observations,
  * global F-tests for significance of regression,
  * and F-tests comparing **nested models**.

* Recognize that:

  * coefficient interpretations are **conditional** (“holding others fixed”),
  * extrapolation in multiple dimensions can be subtle,
  * and simulation is a powerful way to check theoretical results.

In later PyStatsV1 chapters, these tools will underpin more advanced models
(logistic regression, models with interactions, etc.) and many of the case
studies.
