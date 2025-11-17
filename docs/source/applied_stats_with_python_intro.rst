Introduction: How to study applied statistics with Python and R
================================================================

This section of the documentation is inspired by the open textbook
*Applied Statistics with R* by David Dalpiaz (University of Illinois at
Urbana–Champaign), which is available under a
Creative Commons Attribution–NonCommercial–ShareAlike 4.0 license.

PyStatsV1 adapts the **spirit and core ideas** of that text for a
Python-first audience, while still keeping **R in the conversation**.
The goal is not to replace the original book, but to give students and
instructors a way to:

- see familiar R-based ideas expressed in plain Python code,
- run reproducible examples chapter by chapter,
- build intuition by comparing R and Python side by side.

Where the original text says “this book,” you can think of this
documentation plus the PyStatsV1 codebase as **our Python companion
volume**.

About this guide
----------------

This guide is meant to support:

- **Students** in an applied statistics course who are more comfortable
  in Python than in R.
- **Instructors and TAs** who are using an R-first textbook but want to
  demo the same ideas in Python.
- **Practitioners** who want a quick, “textbook style” reference for
  common applied methods implemented as transparent scripts.

The design philosophy is:

- **Code first.** Every idea should have runnable code in both languages.
- **Reproducible by default.** Synthetic data and fixed seeds make it
  easy to rerun examples and explore “what if” questions.
- **Bridging R and Python, not replacing R.** We treat R as a peer
  language, not a rival.

How this relates to the original R text
---------------------------------------

The original *Applied Statistics with R* book was designed for STAT 420
(Methods of Applied Statistics) at UIUC. It is still actively developed
and is an excellent R resource.

PyStatsV1 builds on its **structure and motivations**, but:

- implements examples as plain Python scripts,
- adds reproducible CLI workflows (via ``make``),
- and encourages reading the *R* and *Python* versions together.

A typical workflow might be:

1. Read a section from the original R text to understand the setup.
2. Run the corresponding **PyStatsV1 chapter scripts** to see the same
   ideas in Python.
3. Compare the R and Python output and code style.
4. Try small experiments: change the seed, sample size, or model and
   observe the effect.

Code conventions in this documentation
--------------------------------------

To keep things clear when switching between languages, we use consistent
conventions.

Python code
~~~~~~~~~~~

Python code in the documentation appears in fenced blocks and matches
the scripts in this repository. For example::

   # Python example
   import numpy as np

   rng = np.random.default_rng(123)
   x = rng.normal(loc=0, scale=1, size=100)
   x.mean()

R code
~~~~~~

Occasionally we will show R snippets for comparison. These will be
clearly labeled and follow the usual R console style::

   # R example
   set.seed(123)
   x <- rnorm(100, mean = 0, sd = 1)
   mean(x)

When you see both versions together, the idea is:

- **Same statistical idea, different syntax.**
- Focus on the model and reasoning, not just the language.

Mathematical notation
---------------------

As in the original text, we occasionally use symbols like :math:`p` to
denote the number of :math:`\beta` parameters in a linear model. You do
not need to memorize every symbol immediately; the important point is to
connect:

- the **model equation**,
- the **R implementation**, and
- the **Python implementation**.

Where to report issues or suggest improvements
----------------------------------------------

Just like the original book, this project is a work in progress. You may
encounter:

- typos or unclear explanations,
- small discrepancies between R and Python output,
- places where the documentation could use another example.

If you do, we would love to hear from you.

- Use **GitHub issues** on the PyStatsV1 repository:
  https://github.com/pystatsv1/PyStatsV1/issues
- For general questions or teaching stories, use **GitHub Discussions**:
  https://github.com/pystatsv1/PyStatsV1/discussions

Helpful ways to contribute:

- Suggest rewording a confusing paragraph.
- Point out where the Python code could better match the R text.
- Propose a new small example or diagnostic plot.
- Submit a pull request if you are comfortable with Git and GitHub.

Acknowledgements and license
----------------------------

This guide owes a major intellectual debt to:

- **David Dalpiaz**, author of *Applied Statistics with R*.
- The STAT 420 teaching team and contributors acknowledged in the
  original text.

The original book is available at:

- Repository: https://github.com/daviddalpiaz/appliedstats
- PDF: http://daviddalpiaz.github.io/appliedstats/applied_statistics.pdf

Our adaptation for PyStatsV1 follows the
`Creative Commons Attribution–NonCommercial–ShareAlike 4.0 International
License <http://creativecommons.org/licenses/by-nc-sa/4.0/>`_ of the
original work. In particular:

- You are free to share and adapt this material for **non-commercial**
  purposes.
- You must provide appropriate attribution to the original author.
- Derivative works must use the **same license**.

PyStatsV1 extends this by adding:

- Python implementations of textbook-style analyses,
- command-line workflows and CI tests,
- and documentation tailored to a Python + R learning environment.

Your contributions
------------------

If you contribute a substantial improvement to this documentation or the
associated code and would like to be acknowledged, feel free to open an
issue or pull request and indicate how you would like your name to
appear. We are happy to recognize contributors and, if desired, link to
a GitHub or personal website.

If you care about **open, reproducible statistics education** and want
to learn *why* methods work by seeing them in both R and Python, you’re
exactly the audience this guide was written for.
