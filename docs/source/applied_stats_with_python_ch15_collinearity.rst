.. _applied_stats_with_python_ch15_collinearity:

Applied Statistics with Python – Chapter 15
===========================================
Collinearity
------------

This chapter parallels the *Collinearity* chapter from the R notes. Here we
keep the statistical ideas the same, but express them in Python-first terms.

By the end of this chapter you should be able to:

* Recognize **exact collinearity** (perfect linear dependence) in a design
  matrix.
* Diagnose **high collinearity** between predictors using correlations and
  variance inflation factors (VIFs).
* Explain how collinearity affects regression **coefficients, standard errors,
  and interpretation**.
* Distinguish between the impact of collinearity on **explanation** versus
  **prediction**.
* Use **partial correlation** and **added–variable plots** to decide whether a
  new predictor is worth adding to an existing model.

15.1 Exact collinearity: when the design matrix is singular
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We start with an extreme case: one predictor is an exact linear combination of
the others.

In R, the book defines a function that generates three predictors where

.. math::

   x_3 = 2 x_1 + 4 x_2 + 3,

while the response :math:`y` only depends on :math:`x_1` and :math:`x_2`.

In Python, we can do the same:

.. code-block:: python

   import numpy as np
   import pandas as pd
   import statsmodels.formula.api as smf

   rng = np.random.default_rng(42)

   def gen_exact_collin_data(num_samples: int = 100) -> pd.DataFrame:
       x1 = rng.normal(loc=80, scale=10, size=num_samples)
       x2 = rng.normal(loc=70, scale=5, size=num_samples)
       x3 = 2 * x1 + 4 * x2 + 3
       y = 3 + x1 + x2 + rng.normal(loc=0, scale=1, size=num_samples)
       return pd.DataFrame({"y": y, "x1": x1, "x2": x2, "x3": x3})

   exact_collin_data = gen_exact_collin_data()
   exact_collin_data.head()

Here :math:`y` really only “needs” :math:`x_1` and :math:`x_2`.

If we try to fit a model with all three predictors using the usual normal
equations, the matrix :math:`X^\top X` is not invertible:

.. code-block:: python

   import numpy.linalg as la

   X = np.column_stack(
       [
           np.ones(len(exact_collin_data)),          # intercept
           exact_collin_data[["x1", "x2", "x3"]].to_numpy(),
       ]
   )

   la.inv(X.T @ X)   # raises LinAlgError: singular matrix

Statsmodels hides this detail for us and simply drops one column:

.. code-block:: python

   fit = smf.ols("y ~ x1 + x2 + x3", data=exact_collin_data).fit()
   print(fit.summary())

You will see that one coefficient is reported as *not defined* because the
columns are linearly dependent. Internally, statsmodels has fitted an
equivalent model that only uses two of the three predictors.

Key points:

* With **exact collinearity**, there are infinitely many regression coefficient
  vectors :math:`\hat\beta` that produce the *same fitted values*
  :math:`\hat y`.
* The model still predicts well, but the **individual coefficients are not
  uniquely defined**, so they cannot be interpreted.

To see this, fit three smaller models:

.. code-block:: python

   fit1 = smf.ols("y ~ x1 + x2", data=exact_collin_data).fit()
   fit2 = smf.ols("y ~ x1 + x3", data=exact_collin_data).fit()
   fit3 = smf.ols("y ~ x2 + x3", data=exact_collin_data).fit()

   np.allclose(fit1.fittedvalues, fit2.fittedvalues)
   np.allclose(fit2.fittedvalues, fit3.fittedvalues)

The fitted values are identical, but

.. code-block:: python

   fit1.params
   fit2.params
   fit3.params

give quite different coefficients. This is the hallmark of exact collinearity:
**same predictions, wildly different coefficient stories.**

15.2 Collinearity in practice: highly correlated predictors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Exact collinearity is rare in real data. More commonly, we see **strong but not
perfect correlation** between predictors. This is usually called
*multicollinearity*.

The R notes use the ``seatpos`` dataset from the ``faraway`` package. In
PyStatsV1 we will ship a CSV version of this dataset as
``data/seatpos.csv``:

.. code-block:: python

   import pandas as pd

   seatpos = pd.read_csv("data/seatpos.csv")
   seatpos.head()

The response is ``hipcenter`` (seat position). Predictors include:

* ``Age`` – age in years,
* ``Weight`` – weight in pounds,
* ``Ht`` – standing height,
* ``HtShoes`` – height while wearing shoes,
* ``Seated``, ``Arm``, ``Thigh``, ``Leg`` – various body measurements.

15.2.1 Pairwise correlation checks
**********************************

A first check is to look at pairwise scatterplots and correlations:

.. code-block:: python

   import matplotlib.pyplot as plt

   cols = ["Age", "Weight", "HtShoes", "Ht", "Seated", "Arm", "Thigh", "Leg"]
   pd.plotting.scatter_matrix(seatpos[cols], figsize=(8, 8))
   plt.tight_layout()

   seatpos[cols].corr().round(2)

You should see extremely high correlations between many of the size-related
variables, especially ``HtShoes`` and ``Ht`` (essentially the same measurement).

15.2.2 A “kitchen-sink” regression
**********************************

Now fit a multiple regression with all predictors:

.. code-block:: python

   import statsmodels.formula.api as smf

   hip_model = smf.ols("hipcenter ~ Age + Weight + HtShoes + Ht + "
                       "Seated + Arm + Thigh + Leg",
                       data=seatpos).fit()
   print(hip_model.summary())

Typical pattern:

* The **overall F-test** (at the bottom of the summary) says the model is
  highly significant.
* Yet almost all **individual t-tests** for coefficients have large p-values.
* Some coefficients for very similar predictors can even have **opposite
  signs** (for example, ``Ht`` and ``HtShoes``).

This is a classic symptom of collinearity:

* Together the predictors explain a lot of variation in ``hipcenter``.
* But because they are highly correlated with each other, the model struggles
  to attribute variation to any single predictor.

15.2.3 Variance inflation factors (VIFs)
***************************************

To understand the impact on standard errors, we use the **variance inflation
factor**.

For a given predictor :math:`x_j`, let :math:`R_j^2` be the :math:`R^2` from
regressing :math:`x_j` on all the *other* predictors. Then the variance of its
coefficient :math:`\hat\beta_j` can be written as

.. math::

   \mathrm{Var}(\hat\beta_j)
   \;=\;
   \sigma^2 \,
   \underbrace{\frac{1}{1 - R_j^2}}_{\text{variance inflation factor}}
   \cdot
   \frac{1}{S_{x_j x_j}},

where :math:`S_{x_j x_j}` is the sum of squares of :math:`x_j` around its mean.

The **variance inflation factor (VIF)** is

.. math::

   \text{VIF}_j = \frac{1}{1 - R_j^2}.

If :math:`R_j^2` is close to 1 (``x_j`` is well explained by other predictors),
then :math:`\text{VIF}_j` is large and the standard error of :math:`\hat\beta_j`
is inflated.

In Python we can compute VIFs using statsmodels:

.. code-block:: python

   import numpy as np
   from statsmodels.stats.outliers_influence import variance_inflation_factor

   X = hip_model.model.exog
   vif = pd.Series(
       [variance_inflation_factor(X, i) for i in range(X.shape[1])],
       index=hip_model.model.exog_names,
   )
   vif

You should see very large VIFs for several predictors (well above common rules
of thumb such as 5 or 10). That tells us:

* The model’s **coefficients are unstable and hard to interpret**.
* Small changes in the data can lead to large swings in estimated effects.

15.2.4 Collinearity and small perturbations
*******************************************

To see this instability, add a bit of random noise to the response and refit:

.. code-block:: python

   rng = np.random.default_rng(1337)
   noise = rng.normal(loc=0, scale=5, size=len(seatpos))

   hip_model_noise = smf.ols(
       "hipcenter_plus_noise ~ Age + Weight + HtShoes + Ht + "
       "Seated + Arm + Thigh + Leg",
       data=seatpos.assign(hipcenter_plus_noise=seatpos["hipcenter"] + noise),
   ).fit()

   hip_model.params
   hip_model_noise.params

You will often see:

* Coefficients change a lot, sometimes even **flipping sign**.
* But the **fitted values** are quite similar:

.. code-block:: python

   plt.scatter(hip_model.fittedvalues,
               hip_model_noise.fittedvalues,
               alpha=0.7)
   plt.xlabel("Predicted hipcenter (original)")
   plt.ylabel("Predicted hipcenter (with noise)")
   plt.axline((0, 0), slope=1, color="k", linestyle="--")
   plt.tight_layout()

Collinearity therefore:

* Hurts our ability to **explain** the relationship (unstable coefficients),
* But may have **much smaller effect on prediction error**.

15.2.5 A smaller, more stable model
***********************************

Suppose we fit a simpler model using just a few predictors, for example
``Age``, ``Arm``, and ``Ht``:

.. code-block:: python

   hip_model_small = smf.ols("hipcenter ~ Age + Arm + Ht",
                             data=seatpos).fit()
   print(hip_model_small.summary())

   X_small = hip_model_small.model.exog
   vif_small = pd.Series(
       [variance_inflation_factor(X_small, i)
        for i in range(X_small.shape[1])],
       index=hip_model_small.model.exog_names,
   )
   vif_small

Now the VIFs are reasonable and the coefficient for ``Ht`` has a stable sign.

We can compare the large and small models with an F-test:

.. code-block:: python

   import statsmodels.api as sm

   sm.stats.anova_lm(hip_model_small, hip_model)

Often you will find:

* The more complicated model does **not** provide a statistically significant
  improvement in fit.
* The **simpler model** is therefore preferred: easier to interpret and less
  sensitive to noise.

15.3 Partial correlation and added–variable plots
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Suppose we are considering adding another predictor, say ``HtShoes``, to the
smaller model with ``Age``, ``Arm``, and ``Ht``.

A useful diagnostic is the **partial correlation** between the candidate
predictor and the response *after* removing the effect of the existing
predictors.

Procedure:

1. Fit the *current* model and keep the residuals:

   .. code-block:: python

      resid_y = hip_model_small.resid

2. Regress the *candidate* predictor on the existing predictors and keep its
   residuals:

   .. code-block:: python

      ht_shoes_model_small = smf.ols(
          "HtShoes ~ Age + Arm + Ht",
          data=seatpos
      ).fit()
      resid_ht_shoes = ht_shoes_model_small.resid

3. Compute the correlation:

   .. code-block:: python

      np.corrcoef(resid_ht_shoes, resid_y)[0, 1]

If this partial correlation is close to 0, then once we know ``Age``, ``Arm``,
and ``Ht``, the remaining variation in ``HtShoes`` tells us almost nothing
about the remaining variation in ``hipcenter``. Adding ``HtShoes`` is unlikely
to be helpful.

An **added–variable plot** visualizes the same idea:

.. code-block:: python

   plt.scatter(resid_ht_shoes, resid_y, alpha=0.8)
   plt.axhline(0, linestyle="--", color="grey")
   plt.axvline(0, linestyle="--", color="grey")

   # regression line of residuals on residuals
   line = smf.ols(
       "resid_y ~ resid_ht_shoes",
       data=pd.DataFrame({"resid_y": resid_y,
                          "resid_ht_shoes": resid_ht_shoes}),
   ).fit()
   x_grid = np.linspace(resid_ht_shoes.min(), resid_ht_shoes.max(), 100)
   y_grid = line.params["Intercept"] + line.params["resid_ht_shoes"] * x_grid
   plt.plot(x_grid, y_grid)
   plt.xlabel("Residuals of HtShoes (given Age, Arm, Ht)")
   plt.ylabel("Residuals of hipcenter (given Age, Arm, Ht)")
   plt.tight_layout()

A nearly horizontal cloud with a flat regression line indicates that the new
predictor adds little explanatory power once the others are in the model.

15.4 How this connects to PyStatsV1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Collinearity is one of the main reasons why “more predictors” does not always
mean “better model.”

In later PyStatsV1 chapters and case studies you will see:

* Scripts that compute and **report VIFs** alongside regression summaries.
* Examples where we deliberately drop or combine highly correlated predictors
  to stabilize coefficients.
* Model–comparison workflows that balance **good fit**, **interpretability**,
  and **low collinearity**.

When you adapt or extend PyStatsV1 code for your own data, you should:

* check correlations and VIFs early,
* be suspicious of models where small changes in the data flip coefficient
  signs or dramatically change magnitudes,
* prefer smaller, well-behaved models when the goal is explanation.

15.5 What you should take away
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Exact collinearity** means some predictor is an exact linear combination of
  others. The design matrix is singular, the coefficients are not uniquely
  defined, but predictions can still be fine.
* **High collinearity** (multicollinearity) occurs when predictors are highly
  correlated. It inflates standard errors and makes coefficients unstable and
  hard to interpret.
* The **variance inflation factor (VIF)** quantifies how much collinearity
  inflates the variance of :math:`\hat\beta_j`. VIFs above 5–10 are often used
  as warning flags.
* Collinearity can severely damage our ability to **explain** relationships,
  while having relatively little impact on **prediction error**.
* Tools such as **partial correlation** and **added–variable plots** help decide
  whether a new predictor is worth adding to a model that already has several
  correlated variables.
* When in doubt, prefer **simpler models** with reasonably low collinearity,
  especially when the goal is to communicate and interpret effects.
