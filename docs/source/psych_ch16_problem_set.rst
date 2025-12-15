Track C — Chapter 16 Problem Set: Linear Regression
===================================================

This problem set mirrors the Chapter 16 topics:

- Prediction with a line of best fit: :math:`\hat{Y} = a + bX`
- Least squares logic (minimizing squared residuals)
- Standard Error of the Estimate (SEE): “how wrong are our predictions on average?”
- Multiple regression and incremental :math:`R^2`

How to run
----------

Run the script directly:

.. code-block:: bash

   python -m scripts.psych_ch16_problem_set

Or run the unit tests:

.. code-block:: bash

   pytest -q tests/test_psych_ch16_problem_set.py


Exercise 1 — Strong simple regression
-------------------------------------

You’re given a dataset with a clear linear relationship between ``x`` and ``y``.

Tasks:

1. Fit a simple linear regression predicting ``y`` from ``x``.
2. Interpret the slope (what does a 1-unit change in ``x`` imply for ``y``?).
3. Report :math:`R^2` and the SEE (standard error of estimate).

Expected pattern:

- The slope is clearly non-zero (very small p-value).
- :math:`R^2` is moderate-to-high.


Exercise 2 — Weak/noisy regression
----------------------------------

You’re given a dataset where the true relationship exists but is weak relative to noise.

Tasks:

1. Fit a simple linear regression predicting ``y`` from ``x``.
2. Compare this model to Exercise 1:
   - What happens to :math:`R^2`?
   - What happens to SEE?

Expected pattern:

- :math:`R^2` is small (close to 0).
- SEE is larger (predictions are less accurate on average).


Exercise 3 — Multiple regression and incremental :math:`R^2`
------------------------------------------------------------

You’re given a dataset with two predictors ``x1`` and ``x2``. The predictors share variance,
but both contribute to predicting ``y``.

Tasks:

1. Fit a simple regression: ``y ~ x1`` and record :math:`R^2`.
2. Fit a multiple regression: ``y ~ x1 + x2`` and record :math:`R^2`.
3. Compute the incremental improvement: :math:`\Delta R^2 = R^2_{(x1,x2)} - R^2_{(x1)}`.
4. Interpret the coefficient for ``x2`` (does it add unique predictive power?).

Expected pattern:

- The multiple regression has meaningfully higher :math:`R^2` than the x1-only model.
- ``x2`` is typically significant, showing unique contribution beyond ``x1``.
