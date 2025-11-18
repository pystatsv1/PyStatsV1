Applied Statistics with Python – Chapter 6
==========================================

Resources for Python, R, and reproducible workflows
---------------------------------------------------

The earlier chapters moved quickly through Python, R, and basic statistical
ideas. This chapter is not required for the rest of PyStatsV1, but it collects
resources you can use to go deeper:

- tutorials for learning Python and R,
- books that go beyond this mini-textbook,
- cross-language “cheatsheets”,
- and tooling for reproducible work (RStudio, Jupyter, Quarto, etc.).

Use this as a menu: you do **not** need to read everything here. Pick one or
two resources that match your current level and goals.


6.1 Beginner tutorials and references
=====================================

If you’re just getting comfortable with code, you want **short, hands-on**
introductions where you can type and run examples immediately.

Python-focused
--------------

- **Official Python Tutorial**

  The tutorial in the Python documentation walks through basic syntax,
  control flow, functions, and modules.

  https://docs.python.org/3/tutorial/

- **Scientific Python “quick start” guides**

  Short introductions to NumPy, pandas, Matplotlib, and the scientific
  Python ecosystem. Good for bridging from “I know basic Python” to
  “I can do data analysis.”

  https://numpy.org/doc/stable/user/quickstart.html  
  https://pandas.pydata.org/docs/getting_started/index.html  
  https://matplotlib.org/stable/tutorials/index.html

- **JupyterLab / notebooks**

  Interactive environment for mixing code, narrative, and plots. Very
  helpful for experimentation and teaching.

  https://jupyter.org/

R-focused
---------

These mirror the resources listed in the original R chapter, but with brief
comments about how they complement PyStatsV1.

- **Try R (interactive tutorial)**

  Short, browser-based introduction to R syntax and objects. Nice if you
  want to see R once without installing anything.

- **Quick-R (Kabacoff)**

  Web-based reference for common R tasks: importing data, basic plots,
  regression, etc. Handy if you already know the statistics and just want
  to remember “how do I do this in R?”.

- **R Tutorial (Chi Yau)**

  A mix of tutorial and reference that covers core language features plus
  common data analysis tasks.

- **R Programming for Data Science (Roger Peng)**

  Free online book that builds R from the ground up, with an emphasis on
  good programming habits.

  https://bookdown.org/rdpeng/rprogdatascience/


6.2 Intermediate references
===========================

Once you’re comfortable running code and reading error messages, the next step
is to learn **data analysis workflows** and **programming patterns**.

Python-focused
--------------

- **Python for Data Analysis (Wes McKinney)**

  The pandas “founder’s book”. Great for learning how to manipulate data
  frames, handle time series, and write reusable analysis code.

- **Think Stats / Think Bayes (Allen Downey)**

  Statistics books that use Python from the start, with an emphasis on
  simulation and computation rather than hand algebra.

- **Statistical Thinking in Python (various tutorials)**

  Many online courses and notebooks walk through hypothesis testing,
  regression, and visualization in Python. PyStatsV1 chapters can be a
  complementary “worked examples” resource.

R-focused
---------

- **R for Data Science (Wickham & Grolemund)**

  A modern introduction to data wrangling, visualization, and modeling
  in the **tidyverse** ecosystem. Pairs nicely with PyStatsV1 if you want
  to see the same ideas in both R and Python.

  https://r4ds.had.co.nz/

- **The Art of R Programming (Norman Matloff)**

  Gentle but thorough introduction to R as a programming language (control
  flow, functions, object types), as opposed to just a statistics tool.


6.3 Advanced references
=======================

These are for when R or Python has become part of your regular toolkit and you
want to think about performance, internals, or large projects.

R-focused
---------

- **Advanced R (Hadley Wickham)**

  Deep dive into R’s object system, environments, functional programming,
  and metaprogramming. Helps explain *why* some R code behaves in surprising
  ways.

- **The R Inferno (Patrick Burns)**

  A humorous but very technical guide to R’s “gotchas”. Useful if you write
  a lot of complex R or maintain other people’s R code.

- **Efficient R Programming (Gillespie & Lovelace)**

  Focuses on writing R code that is fast and scalable, and on using R tools
  efficiently day to day.

Python-focused
--------------

- **Scientific Python ecosystem docs**

  NumPy, SciPy, pandas, and Matplotlib all have detailed documentation that
  covers vectorization, broadcasting, and performance tips.

- **Probabilistic programming / Bayesian methods**

  Libraries like PyMC, Stan (via CmdStanPy), or NumPyro provide powerful
  tools for Bayesian modeling. These are beyond the scope of PyStatsV1,
  but worth exploring if you continue into advanced applied statistics.


6.4 Cross-language comparisons
==============================

If you already know another language, sometimes the fastest way to learn is
via a **“Rosetta stone”** that shows equivalent idioms side by side.

Examples mentioned in the original R chapter include:

- **Numerical computing comparison**

  Cheat sheets comparing MATLAB, NumPy, Julia, and R for common numerical
  and matrix operations.

- **R vs Stata vs SAS**

  Short documents that show how the same data analysis is written in each
  language.

For Python + R specifically, useful patterns to practice are:

- indexing and slicing in NumPy vs R,
- data frame operations in pandas vs ``dplyr``,
- plotting with Matplotlib/Seaborn vs ``ggplot2``.

In PyStatsV1 we deliberately write code in a way that makes these parallels
easier to see: plain, explicit scripts in both languages rather than opaque
one-liners.


6.5 IDEs, notebooks, and literate programming
=============================================

A big part of modern applied statistics is organising code, text, and plots in
a single **reproducible document**.

R side
------

- **RStudio**

  Widely used IDE for R (and now other languages). Integrates console,
  editor, plots, and package management in one window.

- **RMarkdown**

  Framework for combining narrative text, R code, and output into a single
  report (HTML, PDF, slides, etc.). The original notes for this book are
  written with RMarkdown.

Python side
-----------

- **Jupyter notebooks / JupyterLab**

  Interactive notebooks where you can mix Python code, Markdown, LaTeX
  equations, and plots. Excellent for exploratory analysis and teaching.

- **VS Code, PyCharm, and other editors**

  For larger projects, an editor or IDE with good Python support
  (linting, debugging, Git integration) can make a big difference.

Bridging tools
--------------

- **Quarto**

  A modern, language-agnostic framework for literate programming that
  supports both Python and R in the same ecosystem. If you like RMarkdown
  + RStudio, Quarto + VS Code/Jupyter gives a similar experience for Python.

No single tool is “the right one”. The best setup is whatever makes it easy for
you to:

1. write clear code,
2. keep data and outputs organised,
3. rerun everything later and get the same results.


6.6 How PyStatsV1 fits into this ecosystem
==========================================

PyStatsV1 is **not** trying to replace full textbooks or advanced courses.
Instead, it aims to be:

- a **bridge** between R-first teaching materials and Python,
- a repository of **worked examples** that you can run, edit, and extend,
- and a place where you can practice **reproducible workflows** without a
  heavy framework.

You might use this chapter as follows:

- If you’re brand new to coding, pair the PyStatsV1 chapters with one of the
  beginner Python or R tutorials.
- If you already know R well, skim the Python resources to see how the
  same ideas look in NumPy/pandas.
- If you’re comfortable in Python, use the R resources when you need to read
  or adapt R-heavy applied work.

Most importantly: **don’t feel obligated to read everything.** Choose one or
two resources that look approachable, and treat PyStatsV1 as your sandbox for
trying ideas out in real code.
