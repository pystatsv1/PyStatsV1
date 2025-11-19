.. _applied_stats_with_python_ch18_beyond:

Applied Statistics with Python – Chapter 18
===========================================

Beyond: where to go after this mini-book
----------------------------------------

You’ve worked through a full mini-sequence on regression:

* basic Python and R workflows,
* simple and multiple linear regression,
* diagnostics, transformations, and model building,
* logistic regression, ANOVA, and experimental design ideas.

That already covers a large chunk of what many “Applied Regression” courses
offer. But it’s really just the start.

In this chapter we sketch possible next steps and how PyStatsV1 can support
them. Think of this as a **roadmap**, not a checklist: you do *not* need to
explore everything here. Pick the paths that match your goals and curiosity.

18.1 Where you can go next
--------------------------

Broadly, there are three directions you can grow:

* **Deeper modeling.**  More regression variants, more careful inference,
  and richer models for complex data.
* **Stronger computing skills.**  Better data workflows, reproducible
  reports, and tools for working with larger or messier datasets.
* **Domain-focused practice.**  Applying these ideas in fields like
  psychology, ecology, economics, sports science, public health, or
  business analytics.

PyStatsV1 is designed to help you bridge **R ↔ Python** and connect textbook
ideas to code, so you can move along any of these paths with less friction.

18.2 Python ecosystem: beyond the basics
----------------------------------------

In these notes we mainly used:

* :mod:`numpy` for arrays and numerical work,
* :mod:`pandas` for tabular data,
* :mod:`statsmodels` for regression and ANOVA,
* :mod:`matplotlib` for plotting.

From here you might explore:

* **SciPy** for numerical optimization, distributions, and signal processing.
* **Seaborn** or **plotnine** for higher-level, statistically oriented
  visualizations.
* **scikit-learn** for predictive modeling:
  cross-validation, pipelines, regularization, trees, ensembles, etc.
* **JupyterLab** or **VS Code** for a smoother notebook / editor workflow.

PyStatsV1 later chapters and case studies will assume you are comfortable
moving between plain Python scripts, notebooks, and command-line tools.

18.3 R + Python “dual citizenship”
----------------------------------

Many applied statistics resources are still written with R in mind. Rather
than choosing one language forever, it can be powerful to become a
**bilingual analyst**:

* Use **R** when you want:
  * quick, high-level modeling with tidyverse-style data pipelines;
  * packages that are deeply integrated with specific scientific domains;
  * RMarkdown / Quarto documents and Shiny apps.

* Use **Python** when you want:
  * to integrate statistics into larger software systems;
  * access to the broader machine-learning and data-science ecosystem;
  * easier deployment to production systems and web backends.

The cross-language patterns in this mini-book (formulas, model objects,
simulation code) are meant to make it easy to translate between the two.

18.4 Tidy data and data workflows
---------------------------------

In many of our examples, the data was already “clean”: each row was a single
observation, each column a variable, with no missing values or awkward
encodings.

Real projects are rarely that kind.

A large part of practical statistics is:

* reshaping data between **wide** and **long** forms;
* handling missing values and outliers;
* joining multiple tables; and
* encoding dates, times, and categorical variables consistently.

In Python, this often means getting comfortable with:

* :mod:`pandas` methods like ``melt``, ``pivot``, ``merge``, and ``groupby``,
* writing small, reusable helper functions for common cleaning steps,
* documenting your choices so analyses remain reproducible.

Later PyStatsV1 material will lean more on these “data tidying” skills.

18.5 Visualization: telling the story
-------------------------------------

Throughout the chapters we used relatively simple plots: scatterplots, line
plots, residual plots, and a few specialized diagnostics.

To go further, you could:

* Learn a **grammar-of-graphics** style library (``plotnine`` in Python or
  ``ggplot2`` in R) to build complex plots from a small set of ideas
  (geoms, aesthetics, facets, scales).
* Practice turning model output into **story-driven graphics**:
  prediction bands, effect plots, partial dependence plots, and
  before/after comparisons.
* Experiment with **interactive** visualizations for teaching or
  exploratory work using tools like Altair, Bokeh, or Plotly.

A good exercise: re-implement the regression diagnostics from earlier chapters
using a different visualization library and compare what feels easier or harder.

18.6 Reproducible reports and small web apps
--------------------------------------------

Statistics becomes much more valuable when results can be **shared and
re-run** easily:

* For **reports and notes**, you can use:
  * Jupyter notebooks exported to HTML or PDF,
  * Quarto documents that mix code and prose in either R or Python,
  * plain Markdown + Makefiles (as in PyStatsV1) for lightweight automation.

* For **interactive exploration**, you might try:
  * **Streamlit** or **Dash** in Python,
  * **Shiny** in R.

A natural extension of PyStatsV1 is to wrap some of the core examples
(e.g. Auto MPG, seat position, logistic regression case studies) in small
web apps where sliders and dropdowns control model inputs.

18.7 Experimental design and causal questions
---------------------------------------------

In Chapter 12 we drew a sharp line between **observational** and
**experimental** data, and noted that regression alone cannot magically answer
causal questions.

To go further you might explore:

* **Classical experimental design**:
  randomized controlled trials, blocking, factorial designs, and power
  calculations for experiments.
* **A/B testing** and online experimentation: how tech companies use
  controlled experiments to choose between design or policy options.
* **Causal inference**:
  potential outcomes, matching, instrumental variables, and
  graphical approaches (causal DAGs).

For PyStatsV1, this means:

* case studies where we deliberately distinguish “what the regression says”
  from “what we’re allowed to conclude causally”,
* simulated experiments where we know the ground truth and can check
  whether our methods recover it.

18.8 Machine learning and predictive modeling
---------------------------------------------

Logistic regression is already a simple **classification** method. Many modern
machine-learning tools generalize the same ideas:

* regularized linear models (ridge, lasso, elastic net),
* tree-based methods (random forests, gradient boosting),
* support vector machines and kernels,
* cross-validation for honest assessment of predictive performance.

Python’s :mod:`sklearn` makes it relatively easy to:

* wrap preprocessing and modeling in **pipelines**,
* tune hyperparameters with grid search or randomized search, and
* evaluate models using cross-validated metrics.

One good next step is to re-visit familiar datasets (Auto MPG, logistic
regression examples) and compare simple statistical models to more flexible
machine-learning models, being explicit about the trade-off between **insight**
and **pure predictive accuracy**.

18.9 Time series and dependent data
-----------------------------------

All of our regression work assumed **independent** observations. Many real
datasets are not:

* daily sales or web traffic,
* sensor readings over time,
* repeated measurements on the same individual.

Time series analysis introduces tools like:

* autoregressive and moving-average models (AR, MA, ARIMA),
* state-space and Kalman filter models,
* models with seasonal patterns and trend.

Python and R both have rich ecosystems for time series; the main conceptual
shift is learning to think about **serial dependence** and forecasting rather
than treating each row as unrelated to the others.

18.10 Bayesian statistics and probabilistic programming
-------------------------------------------------------

In this mini-book we took a **frequentist** perspective: parameters are fixed,
data are random, and uncertainty is summarized with confidence intervals and
p-values.

A complementary view is **Bayesian**, where:

* parameters are treated as random quantities with prior distributions,
* inference is performed via posterior distributions,
* uncertainty is expressed as credible intervals and full probability
  statements about unknowns.

Modern **probabilistic programming** tools (for example, `Stan` via
``cmdstanpy`` or ``pystan``, or Python libraries such as ``pymc``) make it
possible to:

* write models in a domain-focused way,
* combine complex likelihoods with informative priors,
* propagate uncertainty through hierarchical models.

If you enjoyed the simulation-based arguments in earlier chapters, Bayesian
methods are a natural next step.

18.11 High-performance and large-scale computing
------------------------------------------------

Once models get large or data get big, you may need to think about
performance:

* vectorizing and broadcasting operations in NumPy instead of writing Python
  loops,
* using **Numba** or **Cython** to accelerate critical sections,
* offloading heavy linear algebra to GPUs when appropriate,
* working with out-of-core or distributed data tools (for example, Dask or
  Spark).

The key idea is the same as in Chapter 3: **measure** where time is spent,
then optimize the bottlenecks while keeping code clear and well-tested.

18.12 How this connects to PyStatsV1
------------------------------------

PyStatsV1 is meant to be a **launchpad** for these directions, not an endpoint.

As the project grows, you can expect to see:

* additional chapters and case studies that:
  * use experimental data and A/B-testing-style designs,
  * explore generalized linear models and mixed-effects models,
  * revisit classical examples using Bayesian and machine-learning tools;
* more **teaching-oriented notebooks and scripts** that instructors can drop
  directly into courses;
* community-contributed examples from different domains (epidemiology,
  sports analytics, social science, ecology, etc.).

If you’d like to contribute, good starting points include:

* opening a **Discussion** on GitHub describing a course or project you’d
  like to support;
* filing an issue for:
  * a new chapter idea,
  * a missing example or dataset,
  * or an improvement to the documentation;
* submitting a pull request with:
  * a small new example script,
  * a teaching exercise,
  * or an additional section in this mini-book.

18.13 Final thoughts
--------------------

If you’ve reached this chapter, you’ve already done something substantial:

* learned to connect mathematical models to real data,
* seen how the same ideas appear in both R and Python,
* practiced reading and writing code that documents your analysis.

From here on, the most important step is simply to **keep using these tools**:

* analyze real datasets that matter to you,
* re-fit models when you learn a new technique,
* explain your results to non-statisticians.

PyStatsV1 is here as a companion—part textbook, part codebase, part
community. We hope you’ll use it, question it, and help make it better for the
next wave of learners.
