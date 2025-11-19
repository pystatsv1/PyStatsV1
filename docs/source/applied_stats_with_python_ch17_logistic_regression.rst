.. _applied_stats_with_python_ch17_logistic_regression:

Applied Statistics with Python – Chapter 17
===========================================

Logistic regression and classification
--------------------------------------

So far, our regression chapters have focused on *numeric* response variables and
ordinary least squares (OLS). In many applications, however, the response is
binary:

* disease vs no disease,
* spam vs non-spam,
* success vs failure, and so on.

In this chapter we:

* introduce **generalized linear models (GLMs)** as an extension of OLS,
* develop **logistic regression** for binary responses,
* show how to **fit, interpret, and test** logistic models in Python, and
* use logistic regression as a **classifier**, including evaluation metrics such as
  misclassification rate, sensitivity, and specificity.

Throughout, we will mirror the R notes but work in Python using:

* :mod:`numpy` and :mod:`pandas` for data handling,
* :mod:`statsmodels` for logistic regression and GLMs, and
* :mod:`scikit-learn` for classification workflows and cross-validation.

.. contents::
   :local:
   :depth: 2


17.1 Generalized linear models
------------------------------

Ordinary linear regression assumes

* a *Normal* distribution for the response given the predictors, and
* a mean that is a **linear combination** of the predictors:

  .. math::

     Y \mid X = x \sim N(\mu(x), \sigma^2), \qquad
     \mu(x) = \beta_0 + \beta_1 x_1 + \cdots + \beta_{p-1} x_{p-1}.

A **generalized linear model (GLM)** keeps the linear predictor

.. math::

   \eta(x) = \beta_0 + \beta_1 x_1 + \cdots + \beta_{p-1} x_{p-1}

but allows:

* different choices of distribution for :math:`Y \mid X = x`, and
* a **link function** :math:`g(\cdot)` connecting the linear predictor to the mean:

  .. math::

     \eta(x) = g\big( E[Y \mid X = x] \big).

For example:

* **Linear regression**

  * Distribution: Normal
  * Link: identity :math:`g(\mu) = \mu`

* **Poisson regression**

  * Distribution: Poisson (counts)
  * Link: log :math:`g(\lambda) = \log \lambda`

* **Logistic regression**

  * Distribution: Bernoulli (binary)
  * Link: logit :math:`g(p) = \log \{p / (1 - p)\}`


17.2 Binary responses and the logistic model
-------------------------------------------

Suppose we have a binary response coded as

.. math::

   Y = \begin{cases}
   1, & \text{event occurs (``yes'', ``spam'', ``disease'')} \\
   0, & \text{otherwise (``no'', ``not spam'', ``no disease'')}.
   \end{cases}

Define

.. math::

   p(x) = P(Y = 1 \mid X = x).

With a **logistic regression model** we assume

.. math::

   \log \left( \frac{p(x)}{1 - p(x)} \right)
      = \beta_0 + \beta_1 x_1 + \cdots + \beta_{p-1} x_{p-1}.

The left-hand side is the **log-odds** (logit). Applying the inverse logit gives

.. math::

   p(x) = \frac{\exp\{\eta(x)\}}{1 + \exp\{\eta(x)\}}
        = \frac{1}{1 + \exp\{-\eta(x)\}}.

This guarantees :math:`0 < p(x) < 1`, which is exactly what we want from a
probability.

Where is the error term?
~~~~~~~~~~~~~~~~~~~~~~~~

In the OLS model we write

.. math::

   Y = \beta_0 + \beta_1 x_1 + \cdots + \beta_q x_q + \varepsilon,
   \qquad \varepsilon \sim N(0, \sigma^2),

or equivalently

.. math::

   Y \mid X = x \sim N(\mu(x), \sigma^2).

The Normal distribution has two parameters, :math:`\mu(x)` and :math:`\sigma^2`,
so we estimate both.

In logistic regression the conditional distribution is **Bernoulli** with mean
:math:`p(x)`. The distribution has a *single* parameter, so we only need to
estimate :math:`p(x)` (through the :math:`\beta` coefficients). There is no
separate :math:`\sigma^2` parameter.


17.2.1 Why not OLS on a 0/1 outcome?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If :math:`Y \in \{0, 1\}`, the conditional mean is

.. math::

   E[Y \mid X = x] = P(Y = 1 \mid X = x) = p(x).

You might think we can simply fit an ordinary linear regression of :math:`Y` on
:math:`X` and interpret the fitted values as estimated probabilities. The
problem:

* the OLS fitted line is linear in :math:`x`, so fitted values can be **less than 0**
  or **greater than 1**, which makes no sense as probabilities;
* the Normal error assumption is a poor match to a Bernoulli variable.

Logistic regression solves both issues: probabilities are constrained to
:math:`(0, 1)` and the Bernoulli model correctly reflects the 0/1 nature of the
data.


17.2.2 Simulating logistic data in Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is a direct translation of the R simulation used in the original notes.

.. code-block:: python

   import numpy as np
   import pandas as pd

   rng = np.random.default_rng(42)

   def sim_logistic_data(sample_size=25, beta_0=-2.0, beta_1=3.0) -> pd.DataFrame:
       x = rng.normal(size=sample_size)
       eta = beta_0 + beta_1 * x
       p = 1 / (1 + np.exp(-eta))          # inverse logit
       y = rng.binomial(n=1, p=p, size=sample_size)
       return pd.DataFrame({"y": y, "x": x})

   df = sim_logistic_data()
   df.head()

We can now compare an OLS fit to a logistic fit:

.. code-block:: python

   import statsmodels.api as sm
   import statsmodels.formula.api as smf
   import matplotlib.pyplot as plt

   # ordinary least squares
   ols_mod = smf.ols("y ~ x", data=df).fit()

   # logistic regression (GLM with binomial family + logit link)
   logit_mod = smf.glm(
       "y ~ x", data=df,
       family=sm.families.Binomial()
   ).fit()

   x_grid = np.linspace(df["x"].min(), df["x"].max(), 200)
   grid = pd.DataFrame({"x": x_grid})

   plt.scatter(df["x"], df["y"], s=20)
   plt.plot(x_grid, ols_mod.predict(grid), label="OLS")
   plt.plot(x_grid, logit_mod.predict(grid), linestyle="--", label="Logistic")
   plt.xlabel("x")
   plt.ylabel("Estimated probability")
   plt.legend()
   plt.grid(True)

The logistic curve stays between 0 and 1; the OLS line does not.


17.3 Fitting logistic regression in Python
------------------------------------------

We use :mod:`statsmodels` to estimate logistic regression models. The syntax
parallels :func:`glm` in R.

Basic fit
~~~~~~~~~

.. code-block:: python

   import statsmodels.formula.api as smf
   import statsmodels.api as sm

   # binary response y, predictors x1, x2, ...
   logit_mod = smf.glm(
       "y ~ x1 + x2",
       data=df,
       family=sm.families.Binomial()
   ).fit()

   print(logit_mod.summary())

Key outputs:

* coefficient estimates :math:`\hat\beta_j`,
* standard errors and Wald :math:`z` statistics,
* approximate p-values for tests :math:`H_0: \beta_j = 0`,
* deviance and information criteria (AIC / BIC).

Wald tests
~~~~~~~~~~

A single-parameter hypothesis

.. math::

   H_0 : \beta_j = 0 \quad \text{vs} \quad H_1 : \beta_j \neq 0

is tested with a **Wald statistic**

.. math::

   z = \frac{\hat\beta_j}{\operatorname{SE}(\hat\beta_j)}
   \approx N(0, 1),

reported in the summary as ``z`` and ``P>|z|``.

Likelihood-ratio tests
~~~~~~~~~~~~~~~~~~~~~~

To compare a **reduced** model to a **full** model, we can use a
likelihood-ratio test (LRT), the GLM analogue of the regression F-test.

.. code-block:: python

   reduced = smf.glm("y ~ x1 + x2", data=df,
                     family=sm.families.Binomial()).fit()

   full = smf.glm("y ~ x1 + x2 + x3 + x4", data=df,
                  family=sm.families.Binomial()).fit()

   lr_stat, lr_pvalue, df_diff = full.compare_lr_test(reduced)
   print(lr_stat, df_diff, lr_pvalue)

Here:

* :code:`lr_stat` is the deviance difference :math:`D`,
* :code:`df_diff` is the difference in degrees of freedom (number of parameters),
* :code:`lr_pvalue` is the p-value under a :math:`\chi^2_{df\_diff}` approximation.


17.3.1 SAheart example: coronary heart disease
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The R notes use the :data:`SAheart` dataset from :mod:`ElemStatLearn`. In
PyStatsV1 we will assume a CSV version is available, for example:

* :file:`data/sa_heart.csv`

with columns:

* ``chd`` – coronary heart disease indicator (1 = present, 0 = absent),
* ``sbp`` – systolic blood pressure,
* ``tobacco`` – lifetime tobacco (kg),
* ``ldl`` – low density lipoprotein cholesterol,
* ``adiposity``, ``famhist``, ``typea``, ``obesity``, ``alcohol``, ``age``.

Reading and preparing the data:

.. code-block:: python

   sa = pd.read_csv("data/sa_heart.csv")

   # make sure chd is 0/1 integers
   sa["chd"] = sa["chd"].astype(int)

Single-predictor model (LDL only)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   chd_ldl = smf.glm(
       "chd ~ ldl", data=sa,
       family=sm.families.Binomial()
   ).fit()

   print(chd_ldl.summary())

A positive coefficient for ``ldl`` indicates that higher LDL is associated with
higher probability of CHD.

Additive model with all predictors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   chd_add = smf.glm(
       "chd ~ sbp + tobacco + ldl + adiposity + C(famhist)"
       " + typea + obesity + alcohol + age",
       data=sa,
       family=sm.families.Binomial()
   ).fit()

   chd_add.summary()

*Note*: ``C(famhist)`` treats ``famhist`` as a categorical predictor.

Comparing models with an LRT:

.. code-block:: python

   lr_stat, lr_pvalue, df_diff = chd_add.compare_lr_test(chd_ldl)
   print(f"LRT stat = {lr_stat:.3f}, df = {df_diff}, p = {lr_pvalue:.3g}")

A very small p-value suggests that the larger additive model explains CHD
substantially better than LDL alone.

Variable selection (briefly)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For a quick backward stepwise fit using AIC we can loop over predictors or use
a small helper; for now we simply note that:

* AIC/BIC from :attr:`result.aic` / :attr:`result.bic` can be compared across
  models.
* We prefer models that balance **good fit** (low deviance) with **parsimony**
  (few predictors).


Confidence intervals for coefficients
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   chd_sel = chd_add  # for now, suppose this is our selected model
   ci_99 = chd_sel.conf_int(alpha=0.01)
   ci_99.columns = ["lower", "upper"]
   ci_99

These are profile-likelihood intervals, analogous to the R output from
``confint``.


Confidence intervals for mean response
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For a new patient we often want an interval for the *predicted probability* of
CHD.

.. code-block:: python

   new_obs = pd.DataFrame(
       {
           "sbp": [148.0],
           "tobacco": [5.0],
           "ldl": [12.0],
           "adiposity": [31.23],
           "famhist": ["Present"],
           "typea": [47],
           "obesity": [28.50],
           "alcohol": [23.89],
           "age": [60],
       }
   )

   # get eta and its standard error
   pred = chd_sel.get_prediction(new_obs)
   summary = pred.summary_frame()   # includes mean, mean_ci_lower, mean_ci_upper
   summary[["mean_ci_lower", "mean", "mean_ci_upper"]]

By default, :mod:`statsmodels` returns intervals on the **link scale**
(log-odds). Using ``transform=True`` we can instead request intervals already
back-transformed to probabilities:

.. code-block:: python

   summary_prob = chd_sel.get_prediction(new_obs).summary_frame(transform=True)
   summary_prob[["mean_ci_lower", "mean", "mean_ci_upper"]]

This provides a confidence interval for :math:`p(x)` between 0 and 1.


17.4 Logistic regression as a classifier
---------------------------------------

Up to now, we have focused on modelling the probability :math:`p(x)`. To turn
logistic regression into a **classifier**, we map each observation to a class
label.

If we knew the true probabilities, the **Bayes classifier**

.. math::

   C_B(x) = \arg\max_k P(Y = k \mid X = x)

would minimize the probability of misclassification. For a binary response this
reduces to:

.. math::

   C_B(x) =
   \begin{cases}
   1, & p(x) > 0.5,\\
   0, & \text{otherwise}.
   \end{cases}

In practice we replace :math:`p(x)` by its estimate :math:`\hat p(x)` from the
logistic model and use the same rule.

Misclassification rate
~~~~~~~~~~~~~~~~~~~~~~

Given predictions :math:`\hat C(x_i)` on a dataset,
the **misclassification rate** is

.. math::

   \text{Misclass} = \frac{1}{n} \sum_{i=1}^n I\{ y_i \neq \hat C(x_i) \}.

Equivalently, accuracy is :math:`1 - \text{Misclass}`.

Sensitivity and specificity
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A confusion matrix for a binary classifier records:

* true positives (TP),
* false positives (FP),
* true negatives (TN),
* false negatives (FN).

Two important metrics are:

* **Sensitivity** (recall, true positive rate)

  .. math::

     \text{Sens} = \frac{\text{TP}}{\text{TP} + \text{FN}}.

* **Specificity** (true negative rate)

  .. math::

     \text{Spec} = \frac{\text{TN}}{\text{TN} + \text{FP}}.

Changing the probability cutoff :math:`c` in

.. math::

   \hat C(x) =
   \begin{cases}
   1, & \hat p(x) > c,\\
   0, & \hat p(x) \le c,
   \end{cases}

trades off sensitivity and specificity:

* lowering :math:`c` increases sensitivity but decreases specificity,
* raising :math:`c` does the opposite.

In practice, the “best” cutoff depends on the costs of false positives vs false
negatives.


17.4.1 Spam example: email classification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The R notes use the classic ``spam`` dataset from the UCI machine learning
repository. In PyStatsV1 we can assume a CSV file

* :file:`data/spam.csv`

with a binary column ``type`` (``"spam"`` vs ``"nonspam"``) and many engineered
text features.

Train / test split
^^^^^^^^^^^^^^^^^^

Using scikit-learn:

.. code-block:: python

   from sklearn.model_selection import train_test_split
   from sklearn.linear_model import LogisticRegression
   from sklearn.metrics import (
       confusion_matrix, accuracy_score, recall_score
   )

   spam = pd.read_csv("data/spam.csv")

   X = spam.drop(columns=["type"])
   y = (spam["type"] == "spam").astype(int)  # 1 = spam, 0 = non-spam

   X_trn, X_tst, y_trn, y_tst = train_test_split(
       X, y, test_size=0.3, random_state=42, stratify=y
   )

Fit several models of increasing complexity:

.. code-block:: python

   # simple model using only capitalTotal
   caps_mod = LogisticRegression(max_iter=1000)
   caps_mod.fit(X_trn[["capitalTotal"]], y_trn)

   # a small hand-picked model
   few_features = ["edu", "money", "capitalTotal", "charDollar"]
   sel_mod = LogisticRegression(max_iter=1000)
   sel_mod.fit(X_trn[few_features], y_trn)

   # additive model using all predictors
   full_mod = LogisticRegression(
       max_iter=1000, n_jobs=-1
   )
   full_mod.fit(X_trn, y_trn)

   # (an “over-parametrized” model with interactions would usually be handled
   #  via feature engineering; we omit it here for brevity.)

Cross-validated misclassification rate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Instead of relying on training error, use cross-validation:

.. code-block:: python

   from sklearn.model_selection import cross_val_score

   def cv_misclass(model, X, y, cv=5):
       acc = cross_val_score(model, X, y, cv=cv, scoring="accuracy")
       return 1 - acc.mean()

   cv_caps = cv_misclass(caps_mod, X_trn[["capitalTotal"]], y_trn)
   cv_sel  = cv_misclass(sel_mod, X_trn[few_features], y_trn)
   cv_full = cv_misclass(full_mod, X_trn, y_trn)

   print(cv_caps, cv_sel, cv_full)

Typically you will see:

* the very simple model **underfits** (higher misclassification),
* a moderate-size model performs better,
* an extremely complex model risks **overfitting**.

Confusion matrix on the test set
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pick a preferred model (say ``full_mod``) and evaluate it on the held-out test
set:

.. code-block:: python

   # predicted probabilities for class 1 (spam)
   p_hat = full_mod.predict_proba(X_tst)[:, 1]

   # default cutoff 0.5
   y_pred_50 = (p_hat > 0.5).astype(int)

   cm_50 = confusion_matrix(y_tst, y_pred_50)
   acc_50 = accuracy_score(y_tst, y_pred_50)
   sens_50 = recall_score(y_tst, y_pred_50)   # sensitivity = recall for positive class

   # specificity needs a small helper
   tn, fp, fn, tp = cm_50.ravel()
   spec_50 = tn / (tn + fp)

   print("Confusion matrix (c = 0.5):")
   print(cm_50)
   print(f"Accuracy = {acc_50:.3f}, Sensitivity = {sens_50:.3f}, Specificity = {spec_50:.3f}")

Changing the cutoff to 0.1 or 0.9 illustrates the trade-off:

.. code-block:: python

   for c in [0.1, 0.5, 0.9]:
       y_pred = (p_hat > c).astype(int)
       tn, fp, fn, tp = confusion_matrix(y_tst, y_pred).ravel()
       acc = accuracy_score(y_tst, y_pred)
       sens = recall_score(y_tst, y_pred)
       spec = tn / (tn + fp)
       print(f"Cutoff {c:.1f}: acc={acc:.3f}, sens={sens:.3f}, spec={spec:.3f}")

This matches the behaviour described in the R notes: lower cutoffs favour
sensitivity (catching more spam) at the cost of more false positives; higher
cutoffs do the opposite.


17.5 How this connects to PyStatsV1
-----------------------------------

Logistic regression and GLMs will reappear throughout PyStatsV1:

* Many modern models used in science, health, and industry are **generalized
  linear models**, not just ordinary linear regression.
* In later chapters on **experimental data and causal questions**, logistic
  regression provides a natural way to model binary outcomes (e.g., success vs
  failure) while controlling for covariates.
* For applied work, logistic regression often serves as a **baseline classifier**
  before moving to more complex machine-learning methods. PyStatsV1 will show
  how to compare logistic models with tree-based and other algorithms.
* The ideas of **link functions**, **likelihood-based inference**, and
  **classification metrics** generalize to many other models (Poisson,
  multinomial, etc.).

Exercises and examples built on this chapter will encourage you to:

* fit and interpret logistic models for real binary outcomes,
* compare OLS and logistic regression on the same dataset,
* practice using deviance, AIC, and cross-validated misclassification to choose
  between models, and
* think carefully about which metrics (accuracy, sensitivity, specificity) are
  appropriate for a given applied problem.


17.6 What you should take away
------------------------------

By the end of this chapter (and its R + Python versions), you should be able to:

* Explain how **generalized linear models** extend ordinary linear regression.
* Define and work with the **logistic regression model**:

  * log-odds, odds, probabilities,
  * logit and inverse-logit (sigmoid) transformations.

* Fit logistic regression models in Python using :mod:`statsmodels` and
  :mod:`scikit-learn`.

  * interpret coefficients in terms of log-odds and probabilities;
  * compute Wald tests and likelihood-ratio tests;
  * construct confidence intervals for coefficients and mean response.

* Use logistic regression as a **classifier**:

  * obtain class probabilities :math:`\hat p(x)`,
  * convert them to labels using a cutoff,
  * compute misclassification rate, sensitivity, and specificity,
  * understand how changing the cutoff trades off false positives vs false
    negatives.

* Recognize that many ideas from linear regression (model comparison, variable
  selection, diagnostics) carry over almost unchanged to the logistic setting.

In short: logistic regression is your first step into the broader world of GLMs
and classification methods, and a core tool for applied statistics with PyStatsV1.
