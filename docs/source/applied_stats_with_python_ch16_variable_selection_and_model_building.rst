.. _applied_stats_with_python_ch16_variable_selection_and_model_building:

Applied Statistics with Python – Chapter 16
===========================================

Variable selection and model building
-------------------------------------

The previous chapter showed how **collinearity** between predictors can make
regression models unstable. One common remedy is to **fit a smaller model**:
drop some predictors so the remaining ones are less redundant.

That raises a new question:

    *Given many possible models, how do we choose a “good” one?*

In the original R notes, this chapter uses tools like ``AIC()``, ``BIC()``,
``step()``, and ``regsubsets()`` from the **faraway** and **leaps** packages.
Here we will:

* translate those ideas into **Python-first** code using
  :mod:`statsmodels` and :mod:`scikit-learn`,
* separate **quality criteria** (AIC, BIC, adjusted :math:`R^2`,
  cross-validated RMSE) from **search procedures** (backward, forward,
  stepwise, exhaustive),
* use a couple of running examples (seat position and Auto MPG) to see
  model selection in action, and
* revisit the distinction between models for **explanation** and models
  for **prediction**.

Throughout, you can imagine that we already have two cleaned CSV files:

* ``data/seatpos.csv`` with a response ``hipcenter`` and several body
  measurements as predictors.
* ``data/autompg.csv`` with ``mpg`` and car attributes
  (cylinders, displacement, horsepower, weight, acceleration, model year,
  domestic / non-domestic).

16.1 Quality criteria: balancing fit and complexity
---------------------------------------------------

So far we have used **residual plots**, :math:`R^2`, and RMSE to judge a single
model’s fit. If we try to *compare* models using plain :math:`R^2` or RMSE,
we run into a problem:

*Adding predictors can never make :math:`R^2` worse, and almost never makes RMSE
worse.* A huge, overfitted model will always win.

We need criteria that reward **good fit** but **penalize complexity**.
In this chapter we will use four:

* **AIC** (Akaike Information Criterion)
* **BIC** (Bayesian Information Criterion)
* **Adjusted :math:`R^2`**
* **Cross-validated RMSE** (for prediction)

In all cases, “smaller is better” except that **larger** adjusted
:math:`R^2` is better.

16.1.1 AIC and BIC in Python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For a linear regression with :math:`n` observations, :math:`p` parameters
(including the intercept), and residual sum of squares :math:`\mathrm{RSS}`,
the R notes write AIC and BIC as

.. math::

   \mathrm{AIC} = n \log\!\left(\frac{\mathrm{RSS}}{n}\right) + 2p

   \mathrm{BIC} = n \log\!\left(\frac{\mathrm{RSS}}{n}\right)
                  + (\log n)\, p.

*The first term measures fit; the second term penalizes model size.*

In **statsmodels**, both are built in:

.. code-block:: python

    import pandas as pd
    import statsmodels.api as sm

    df = pd.read_csv("data/seatpos.csv")
    y = df["hipcenter"]
    X = df[["Age", "Weight", "HtShoes", "Ht", "Seated", "Arm", "Thigh", "Leg"]]
    X = sm.add_constant(X)

    model = sm.OLS(y, X).fit()

    model.aic      # Akaike Information Criterion
    model.bic      # Bayesian Information Criterion

Smaller AIC / BIC means “better” under that criterion. BIC usually prefers
**smaller** models than AIC because its penalty :math:`(\log n)p` is larger
than :math:`2p` once :math:`\log n > 2`.

If you have RSS, :math:`n`, and :math:`p` directly, you can compute them by hand:

.. code-block:: python

    import numpy as np

    def aic_from_rss(rss: float, n: int, p: int) -> float:
        return n * np.log(rss / n) + 2 * p

    def bic_from_rss(rss: float, n: int, p: int) -> float:
        return n * np.log(rss / n) + np.log(n) * p

16.1.2 Adjusted :math:`R^2`
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plain :math:`R^2` is

.. math::

   R^2 = 1 - \frac{\mathrm{SSE}}{\mathrm{SST}}
       = 1 - \frac{\sum (y_i - \hat y_i)^2}{\sum(y_i - \bar y)^2}.

Adjusted :math:`R^2` adds a penalty for the number of parameters:

.. math::

   R^2_\mathrm{adj}
     = 1 - \frac{\mathrm{SSE} / (n - p)}{\mathrm{SST} / (n - 1)}
     = 1 - \frac{n - 1}{n - p} (1 - R^2).

Unlike plain :math:`R^2`, adjusted :math:`R^2` can **decrease** when you add
a useless predictor.

In statsmodels you get it for free:

.. code-block:: python

    model.rsquared        # R^2
    model.rsquared_adj    # adjusted R^2

16.1.3 Cross-validated RMSE
~~~~~~~~~~~~~~~~~~~~~~~~~~~

AIC, BIC, and adjusted :math:`R^2` all use :math:`p` explicitly.
**Cross-validation** instead asks a predictive question:

    *How well would this model perform on new data?*

The R notes focus on **leave-one-out cross-validation** (LOOCV):

1. For each observation :math:`i`, fit the model **without** that point.
2. Predict :math:`\hat y_{[i]}` for the left-out point.
3. Compute the LOOCV residual :math:`e_{[i]} = y_i - \hat y_{[i]}`.
4. Define

   .. math::

      \mathrm{RMSE}_{\mathrm{LOOCV}}
      = \sqrt{\frac{1}{n} \sum_{i=1}^n e_{[i]}^2 }.

In Python we usually use :mod:`scikit-learn` for cross-validation:

.. code-block:: python

    import numpy as np
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import cross_val_score, LeaveOneOut

    def loocv_rmse(X, y):
        model = LinearRegression()
        loo = LeaveOneOut()
        # By convention, cross_val_score *maximizes* a score, so we use
        # negative MSE and flip the sign.
        neg_mse_scores = cross_val_score(
            model, X, y,
            cv=loo,
            scoring="neg_mean_squared_error",
        )
        mse = -neg_mse_scores.mean()
        return np.sqrt(mse)

    X = df[["Age", "Weight", "HtShoes", "Ht", "Seated", "Arm", "Thigh", "Leg"]]
    y = df["hipcenter"]

    loocv_rmse(X, y)

For larger data sets, **5-fold or 10-fold** cross-validation is more common:

.. code-block:: python

    from sklearn.model_selection import KFold

    def kfold_rmse(X, y, k=5, random_state=0):
        model = LinearRegression()
        kf = KFold(n_splits=k, shuffle=True, random_state=random_state)
        neg_mse_scores = cross_val_score(
            model, X, y,
            cv=kf,
            scoring="neg_mean_squared_error",
        )
        mse = -neg_mse_scores.mean()
        return np.sqrt(mse)

16.1.4 Which criterion should I use?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A rule of thumb:

* For **explanation** and **interpretable models**, prefer criteria that
  strongly penalize complexity:

  * BIC,
  * adjusted :math:`R^2`.

* For **prediction**, emphasize **cross-validated RMSE** (or another
  predictive metric). AIC can also be a compromise.

In the rest of the chapter we will often compare several criteria side-by-side.

16.1.5 R vs Python: quality criteria
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Concept
     - R notes
     - Python (statsmodels / scikit-learn)
   * - AIC / BIC
     - ``AIC(fit)``, ``BIC(fit)``
     - ``fit.aic``, ``fit.bic``
   * - Adjusted :math:`R^2`
     - ``summary(fit)$adj.r.squared``
     - ``fit.rsquared_adj``
   * - LOOCV RMSE
     - manual function with ``hatvalues(fit)``
     - ``LeaveOneOut`` + ``cross_val_score`` (or manual loop)

16.2 Search procedures: which models to consider?
-------------------------------------------------

A **model selection procedure** has two ingredients:

1. A **quality criterion** (AIC, BIC, adjusted :math:`R^2`,
   cross-validated RMSE, …).
2. A **search strategy** to explore the huge space of possible models.

With :math:`p` candidate predictors, there are :math:`2^p` possible subsets.
For :math:`p = 8`, that is already 256 models; for :math:`p = 15` it is
over 32,000.

The R chapter introduces four strategies:

* backward selection,
* forward selection,
* stepwise selection,
* exhaustive (all-subsets) search.

We will sketch Python versions using statsmodels.

Helper: fit a model on a given subset
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We’ll write a tiny helper that:

* takes a list of predictor names,
* fits a linear regression with an intercept,
* returns a chosen metric (AIC, BIC, adjusted :math:`R^2`, or CV-RMSE).

.. code-block:: python

    import itertools
    from typing import List, Literal

    Metric = Literal["aic", "bic", "adj_r2", "loocv_rmse"]

    def evaluate_subset(df, response: str, predictors: List[str],
                        metric: Metric = "aic") -> float:
        """Fit OLS on a subset of predictors and return a scalar score."""
        y = df[response]
        X = sm.add_constant(df[predictors])

        fit = sm.OLS(y, X).fit()

        if metric == "aic":
            return fit.aic
        if metric == "bic":
            return fit.bic
        if metric == "adj_r2":
            # For consistency with AIC/BIC ("smaller is better"), we return
            # negative adjusted R^2 here.
            return -fit.rsquared_adj
        if metric == "loocv_rmse":
            # Use scikit-learn with the *same* predictors
            X_np = df[predictors].to_numpy()
            y_np = y.to_numpy()
            return loocv_rmse(X_np, y_np)

        raise ValueError(f"Unknown metric: {metric}")

16.2.1 Backward selection
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Backward selection** starts from the **full model** and repeatedly **drops**
one predictor at a time if it improves the criterion.

Skeleton implementation:

.. code-block:: python

    def backward_selection(df, response: str, candidates: List[str],
                           metric: Metric = "aic"):
        remaining = list(candidates)
        best_score = evaluate_subset(df, response, remaining, metric)

        improved = True
        while improved and len(remaining) > 1:
            improved = False
            scores = []

            for predictor in remaining:
                trial = [p for p in remaining if p != predictor]
                score = evaluate_subset(df, response, trial, metric)
                scores.append((score, predictor, trial))

            # Pick the *best* (smallest score) among the candidates
            score, predictor_to_drop, trial = min(scores, key=lambda t: t[0])

            if score + 1e-8 < best_score:  # small tolerance
                best_score = score
                remaining = trial
                improved = True

        return remaining, best_score

Example (using the seat position data):

.. code-block:: python

    seat_df = pd.read_csv("data/seatpos.csv")
    predictors = ["Age", "Weight", "HtShoes", "Ht", "Seated",
                  "Arm", "Thigh", "Leg"]

    selected_aic, score_aic = backward_selection(
        seat_df, "hipcenter", predictors, metric="aic"
    )
    selected_bic, score_bic = backward_selection(
        seat_df, "hipcenter", predictors, metric="bic"
    )

    print("Backward AIC:", selected_aic)
    print("Backward BIC:", selected_bic)

Typically:

* AIC keeps **more** predictors.
* BIC keeps a **smaller** set with nearly as good predictive performance.

16.2.2 Forward selection
~~~~~~~~~~~~~~~~~~~~~~~~~

**Forward selection** starts from the **intercept-only** model and
repeatedly **adds** the predictor that most improves the criterion.

.. code-block:: python

    def forward_selection(df, response: str, candidates: List[str],
                          metric: Metric = "aic"):
        remaining = list(candidates)
        selected: List[str] = []
        best_score = evaluate_subset(df, response, selected or [remaining[0]], metric)

        improved = True
        while improved and remaining:
            improved = False
            scores = []

            for predictor in remaining:
                trial = selected + [predictor]
                score = evaluate_subset(df, response, trial, metric)
                scores.append((score, predictor, trial))

            score, predictor_to_add, trial = min(scores, key=lambda t: t[0])

            if score + 1e-8 < best_score:
                best_score = score
                selected = trial
                remaining.remove(predictor_to_add)
                improved = True

        return selected, best_score

Forward and backward often find *similar* but not identical models.

16.2.3 Stepwise selection
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Stepwise** selection looks **both directions** at each step:

* try adding each unused predictor;
* also try dropping each currently-included predictor;
* commit the change (add or drop) that best improves the criterion.

Conceptually it is:

.. code-block:: python

    def stepwise_selection(df, response: str, candidates: List[str],
                           metric: Metric = "aic"):
        selected: List[str] = []
        best_score = float("inf")

        while True:
            changed = False

            # 1. Try adding
            add_scores = []
            for p in candidates:
                if p in selected:
                    continue
                trial = selected + [p]
                score = evaluate_subset(df, response, trial, metric)
                add_scores.append((score, ("add", p), trial))

            # 2. Try dropping
            drop_scores = []
            for p in selected:
                trial = [q for q in selected if q != p]
                if not trial:
                    continue
                score = evaluate_subset(df, response, trial, metric)
                drop_scores.append((score, ("drop", p), trial))

            all_scores = add_scores + drop_scores
            if not all_scores:
                break

            score, (action, p), trial = min(all_scores, key=lambda t: t[0])

            if score + 1e-8 < best_score:
                best_score = score
                selected = trial
                changed = True

            if not changed:
                break

        return selected, best_score

Stepwise tends to behave like a hybrid between forward and backward.

16.2.4 Exhaustive search (all subsets)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For **small** numbers of predictors (:math:`p \le 10` or so), you can
simply check **all** subsets and pick the best according to a given
criterion.

.. code-block:: python

    def exhaustive_search(df, response: str, candidates: List[str],
                          metric: Metric = "aic"):
        best_score = float("inf")
        best_subset: List[str] | None = None

        for k in range(1, len(candidates) + 1):
            for subset in itertools.combinations(candidates, k):
                subset = list(subset)
                score = evaluate_subset(df, response, subset, metric)
                if score < best_score:
                    best_score = score
                    best_subset = subset

        return best_subset, best_score

This mirrors the R chapter’s use of ``regsubsets()`` from the **leaps**
package.

16.3 Example: seat position (AIC vs BIC vs LOOCV)
--------------------------------------------------

In the R version, the **seatpos** data from the ``faraway`` package is used
to compare models for the response ``hipcenter``. Assume we have
``data/seatpos.csv`` with the following columns:

* ``hipcenter`` – driver hip center (response),
* ``Age``, ``Weight``, ``HtShoes``, ``Ht``, ``Seated``, ``Arm``, ``Thigh``,
  ``Leg`` – body measurements.

A typical workflow in Python:

#. Fit the **full** model with all eight predictors.
#. Run backward selection with **AIC** and **BIC**.
#. Compare adjusted :math:`R^2` and LOOCV RMSE across the full and selected
   models.

Sketch:

.. code-block:: python

    full_predictors = ["Age", "Weight", "HtShoes", "Ht",
                       "Seated", "Arm", "Thigh", "Leg"]

    # Full model
    y = seat_df["hipcenter"]
    X_full = sm.add_constant(seat_df[full_predictors])
    full_fit = sm.OLS(y, X_full).fit()

    # Backward AIC / BIC
    back_aic, _ = backward_selection(seat_df, "hipcenter", full_predictors, "aic")
    back_bic, _ = backward_selection(seat_df, "hipcenter", full_predictors, "bic")

    # Fit selected models
    X_aic = sm.add_constant(seat_df[back_aic])
    X_bic = sm.add_constant(seat_df[back_bic])

    fit_aic = sm.OLS(y, X_aic).fit()
    fit_bic = sm.OLS(y, X_bic).fit()

    # Compare criteria
    print("Full   adj R^2:", full_fit.rsquared_adj)
    print("AIC    adj R^2:", fit_aic.rsquared_adj)
    print("BIC    adj R^2:", fit_bic.rsquared_adj)

    print("Full   LOOCV RMSE:", loocv_rmse(X_full.iloc[:, 1:].to_numpy(), y.to_numpy()))
    print("AIC    LOOCV RMSE:", loocv_rmse(X_aic.iloc[:, 1:].to_numpy(), y.to_numpy()))
    print("BIC    LOOCV RMSE:", loocv_rmse(X_bic.iloc[:, 1:].to_numpy(), y.to_numpy()))

Typically you will see:

* both AIC and BIC improve **adjusted :math:`R^2`** and **LOOCV RMSE**
  compared to the full model;
* BIC selects a **smaller** subset with only a small loss (or even a gain)
  in predictive performance.

16.4 Higher-order terms: Auto MPG example
-----------------------------------------

The final part of the R chapter returns to the **Auto MPG** data and
considers:

* quadratic terms such as :math:`\mathrm{disp}^2`, :math:`\mathrm{hp}^2`,
  :math:`\mathrm{wt}^2`, :math:`\mathrm{acc}^2`,
* all two-way interactions between first-order terms.

The idea is to show that:

* we can start with a **very rich model** (many terms),
* then use backward selection (often with BIC) to find a smaller model that
  still predicts well,
* and compare LOOCV RMSE between the full and selected models.

In Python we can use **formula syntax** with statsmodels:

.. code-block:: python

    import numpy as np
    import statsmodels.formula.api as smf

    auto_df = pd.read_csv("data/autompg.csv")

    # Log-transform the response as in the R notes
    auto_df["log_mpg"] = np.log(auto_df["mpg"])

    big_formula = (
        "log_mpg ~ (cyl + disp + hp + wt + acc + year + domestic) ** 2"
        " + I(disp ** 2) + I(hp ** 2) + I(wt ** 2) + I(acc ** 2)"
    )

    big_fit = smf.ols(big_formula, data=auto_df).fit()
    big_fit.summary()

Now apply backward selection on this rich model, using BIC or AIC as the
criterion. The search logic is identical; the only difference is that the
candidate “predictors” are now terms from the formula (main effects,
quadratics, interactions) rather than raw columns.

Python does not automatically enforce **hierarchy** (keeping main effects
whenever an interaction is included), so in practice you may want to:

* define groups of terms that must stay together,
* or rely on domain knowledge to simplify the final model.

The main lesson:

*Sometimes a slightly richer model (interactions, quadratic terms) combined
with a strong penalty (BIC or cross-validation) gives the best predictive
performance.*

16.5 Explanation versus prediction
----------------------------------

A central theme of the R chapter is the distinction between models used for:

* **Explanation** – understanding how predictors relate to the response.
* **Prediction** – making accurate forecasts for new observations.

Explanation
~~~~~~~~~~~

For explanation we care about:

* **Interpretability**: How does each predictor affect the response,
  holding others fixed?
* **Parsimony**: Smaller models are easier to explain and reason about.
* **Causality vs association**: Does a predictor *cause* changes in the
  response, or is it just correlated?

We normally:

* favor **BIC** or adjusted :math:`R^2` to penalize complexity,
* inspect diagnostic plots (from previous chapters),
* remember that with **observational data** we detect **associations**,
  not necessarily **causal effects**.

Prediction
~~~~~~~~~~

For pure prediction we care about:

* **out-of-sample error** (cross-validated RMSE),
* robustness to new data.

We are less worried about:

* exact p-values,
* whether effects are causal,
* whether the model is small.

A model can predict well even if it is not a realistic description of the
data-generating process.

A classic analogy: **shoe size** and **reading level** in children are highly
correlated (both driven by age). Shoe size does not *cause* reading ability,
but knowing shoe size still helps predict reading level. For prediction that is
fine; for explanation it is misleading.

16.6 How this connects to PyStatsV1
-----------------------------------

In PyStatsV1 we will continually revisit **model selection**:

* Choosing **which predictors to include** in a regression or GLM.
* Comparing different model families (linear vs logistic vs Poisson).
* Balancing **interpretability** against **predictive performance**.

This chapter gives you a toolkit that we can plug into many later examples:

* computing AIC / BIC / adjusted :math:`R^2`,
* using cross-validation to estimate predictive error,
* exploring backward / forward / stepwise / exhaustive search.

In applied case studies we will often start from a **rich model** suggested by
subject-matter knowledge, then use these tools to trim it down to something:

* scientifically interpretable,
* numerically stable,
* and reasonably accurate for prediction.

16.7 What you should take away
------------------------------

By the end of this chapter (and its R + Python versions), you should be able to:

* Explain why **plain :math:`R^2` and RMSE** are not enough for model
  comparison.
* Compute and interpret:

  * **AIC** and **BIC**,
  * **adjusted :math:`R^2`**,
  * **cross-validated RMSE** (LOOCV or K-fold).

* Implement or adapt **search procedures** in Python:

  * backward selection,
  * forward selection,
  * stepwise selection,
  * exhaustive search for small :math:`p`.

* Use these procedures on real data sets (like **seat position** and
  **Auto MPG**) to find reasonable models.
* Distinguish between models aimed at **explanation** and those aimed at
  **prediction**, and choose criteria that match your goal.
* Recognize that:

  * strong penalties (BIC, adjusted :math:`R^2`) often yield compact,
    interpretable models,
  * cross-validation is the gold standard for estimating predictive error,
  * observational data supports **association**, not automatic
    causal claims.

In later PyStatsV1 chapters, these model-selection tools will support both:

* **observational** regression analyses, and
* upcoming material on **experimental design**, where we can combine
  good designs with good models to make stronger causal statements.
