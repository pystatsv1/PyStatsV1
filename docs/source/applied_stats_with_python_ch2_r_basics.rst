Chapter 2 – Getting started with R (for Python-first learners)
==============================================================

This chapter is adapted from Chapter 2 (*Introduction to R*) of
*Applied Statistics with R* by David Dalpiaz, reworked for a Python-first
audience and the PyStatsV1 project. The original text is available at

- Repository: https://github.com/daviddalpiaz/appliedstats
- PDF: http://daviddalpiaz.github.io/appliedstats/applied_statistics.pdf

Our goal here is to give you **enough R** to:

- understand R-based textbook examples, and
- compare them with the Python scripts in PyStatsV1.

You do *not* need to become an R expert to use this project, but seeing
the same ideas in both languages is extremely valuable.

Why learn a bit of R if you like Python?
----------------------------------------

Many applied statistics courses and textbooks are written with R code.
If you only know Python, it can feel like you are always “translating in
your head”.

PyStatsV1 is designed to reduce that friction:

- the *ideas* come from an R-first textbook,
- the *code you actually run* is Python,
- and R appears as a reference point.

A small investment in R gives you:

- direct access to the original examples,
- a second way to check your understanding,
- and a broader mental model of how statistical software works.

Installing R and RStudio / Posit
--------------------------------

R is both:

- a **language**, and
- a **software environment** for statistical computing.

To follow along with the original book or to compare outputs, you will
usually install two pieces of software:

1. **R** from the Comprehensive R Archive Network (CRAN).
2. **RStudio Desktop** (now maintained by Posit), an IDE that provides
   a console, editor, plots pane, and more.

In very rough steps:

- visit CRAN,
- download the latest R version for your operating system,
- then install RStudio Desktop and let it find your R installation.

(Exact installation instructions change over time; the official websites
will have the current details.)

Once installed, you can:

- run R directly from a terminal by typing ``R``, or
- open RStudio and work in its console and editor.

In this guide we will focus on the *language*, not the IDE, but RStudio
is an excellent environment for learning.

Using R as a calculator (and comparing with Python)
---------------------------------------------------

Both R and Python can be used as fancy calculators. To warm up, we will
mirror a few basic operations. The point is not to memorize every line,
but to see how close the two languages really are.

Basic arithmetic
~~~~~~~~~~~~~~~~

Addition, subtraction, multiplication, and division:

- **Python**::

    3 + 2
    3 - 2
    3 * 2
    3 / 2    # 1.5

- **R**::

    3 + 2
    3 - 2
    3 * 2
    3 / 2    # 1.5

Exponentiation and roots
~~~~~~~~~~~~~~~~~~~~~~~~

- **Python** (``**`` for powers)::

    3 ** 2          # 9
    2 ** -3         # 0.125
    100 ** 0.5      # 10
    import math
    math.sqrt(100)  # 10

- **R** (``^`` for powers)::

    3 ^ 2           # 9
    2 ^ (-3)        # 0.125
    100 ^ 0.5       # 10
    sqrt(100)       # 10

Constants and logarithms
~~~~~~~~~~~~~~~~~~~~~~~~

R and Python both provide common mathematical constants and log
functions.

- **Python** (using ``math``)::

    import math

    math.pi          # 3.14159...
    math.e           # 2.71828...

    math.log(math.e)          # natural log
    math.log10(1000)          # base 10
    math.log2(8)              # base 2

- **R**::

    pi               # 3.14159...
    exp(1)           # 2.71828...

    log(exp(1))      # natural log
    log10(1000)      # base 10
    log2(8)          # base 2
    log(16, base = 4)  # log base 4

Trigonometry
~~~~~~~~~~~~

Angles are in radians in both languages.

- **Python**::

    import math
    math.sin(math.pi / 2)  # 1.0
    math.cos(0)            # 1.0

- **R**::

    sin(pi / 2)            # 1
    cos(0)                 # 1

The takeaway: if you can read basic Python math, R’s syntax is only a
small step away.

Getting help in R
-----------------

In the examples above we used functions such as ``sqrt()``, ``exp()``,
``log()`` and ``sin()``. R has built-in documentation for these.

To open the help page for a function in R, type a **question mark** in
front of its name at the console::

    ?log
    ?sin
    ?paste
    ?lm

RStudio displays the documentation in the *Help* pane. This help system
is extremely rich and is often the best first place to look when you are
unsure what a function does.

When that is not enough, general advice from the original text applies
equally to R and Python:

- Start by searching the exact error message.
- If you ask another human for help, include:
  - what you expected the code to do,
  - what actually happened (including the full error),
  - and enough code to reproduce the problem.

This mindset carries over directly to PyStatsV1. When you open a GitHub
issue, the same principles make it much easier for maintainers and
instructors to help you.

Installing and loading packages in R
------------------------------------

Base R ships with many functions and datasets, but one of its biggest
strengths is the **package system**. Packages provide:

- new functions,
- new data sets,
- or sometimes entire modeling frameworks.

There are two steps to using a package:

1. **Install** it (once per machine), and
2. **Load** it in each R session where you need it.

Installation
~~~~~~~~~~~~

Use ``install.packages()`` to download and install from CRAN::

    install.packages("ggplot2")

Think of this as adding a new cookbook to your shelf.

Loading
~~~~~~~

Each time you start R, call ``library()`` for any packages you want to
use in that session::

    library(ggplot2)

This is like taking the cookbook off the shelf and opening it. When you
exit R, the package is no longer loaded, but it remains installed.

Python analogy
~~~~~~~~~~~~~~

If you are used to Python:

- ``install.packages("ggplot2")`` is similar to  
  ``pip install matplotlib seaborn``.
- ``library(ggplot2)`` is similar to::

    import matplotlib.pyplot as plt

You install once per environment, but you **import / load** in every
session.

Style guides and cheatsheets
----------------------------

The original R text recommends using a **style guide** and checking out
the RStudio / Posit “cheatsheets” for base R. The exact style you
follow is less important than being **consistent**.

For R, two well-known guides are:

- Hadley Wickham’s style guide from *Advanced R*.
- Google’s R style guide.

PyStatsV1 does not enforce a particular R style, but we do:

- encourage consistency within an analysis,
- follow PEP 8–style conventions on the Python side,
- and use tools like ``ruff`` and ``pytest`` to keep scripts clean.

In your own work, it is worth choosing a small set of rules for:

- how you name variables (snake_case vs CamelCase),
- where you put spaces around operators,
- and how you format function calls.

Suggested exercises
-------------------

To solidify the ideas from this chapter, try the following:

1. **Mirror basic calculations.**  
   Open a Python REPL and an R console side by side. Recreate the
   examples above and invent a few of your own. Verify that both
   languages give the same results.

2. **Explore documentation.**  
   In R, run ``?log`` and ``?lm`` and skim the help pages. In Python,
   use ``help(math.log)`` or check the NumPy / SciPy docs for similar
   functions. Notice the similarities in structure.

3. **Install and load a package.**  
   In R, install and load ``ggplot2``. In Python, install and import a
   plotting library you like (Matplotlib, Seaborn, Plotnine, …) and
   create a tiny plot in each language.

4. **Practice asking for help.**  
   Take an error message from either language (you can even create one
   on purpose), and write a short, clear question that you would be
   comfortable posting on a help forum or sending to an instructor.

How this chapter connects to PyStatsV1
--------------------------------------

In later chapters of PyStatsV1, you will see:

- R-based textbook examples,
- matching Python scripts in this repository,
- and, where helpful, R snippets for comparison.

This chapter is your “minimal R toolkit” for understanding those
connections. Whenever you see an R command that you do not recognize,
you can:

- revisit this chapter,
- consult the original *Applied Statistics with R* text, or
- open a GitHub Discussion to ask a question.

License and attribution
-----------------------

This chapter is a derivative work based on content from
*Applied Statistics with R* by David Dalpiaz, used under the terms of
the Creative Commons Attribution–NonCommercial–ShareAlike 4.0
International License. You can view the full license at:

- http://creativecommons.org/licenses/by-nc-sa/4.0/

We thank David Dalpiaz and contributors to the original text. PyStatsV1
extends their work by providing Python implementations, command-line
workflows, and teaching-focused documentation for a Python + R
environment.
