.. _psych_ch4:

Psychological Science & Statistics – Chapter 4
==============================================

Frequency Distributions and Visualization: Finding Patterns in Data
-------------------------------------------------------------------

Before we run statistics, we need to *see* the data. Psychology students
often jump straight to t-tests or correlations, but rigorous researchers begin
with a simpler, essential question:

**“What does the data *look* like?”**

This chapter introduces **Exploratory Data Analysis (EDA)**. These tools allow us
to detect patterns, spot data entry errors (e.g., a participant aged 150), and
determine whether our data meets the assumptions required for complex testing later.

Why this chapter matters
------------------------

Exploratory Data Analysis (EDA) is the first real step of psychological
science. Before testing hypotheses, we must ensure our data are clean,
plausible, and interpretable. Visualizing and tabulating data helps researchers:

* detect errors (e.g., impossible ages or reaction times),
* understand participant behavior patterns,
* diagnose assumptions required for later inferential tests,
* and communicate results clearly using APA-style figures.

This chapter builds the foundation for every analysis that follows.

4.1 Frequency tables: organizing data
-------------------------------------

A **frequency table** counts how many times each value occurs. However, raw counts
aren't always enough. In psychology, we often need two additional columns:

1. **Relative Frequency (%)** – the percentage of the total sample.
2. **Cumulative Frequency** – the running total (helps compute percentiles).

Relative Frequency Formula
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   \text{relative frequency} = \frac{f_i}{N}

   \text{percent} = \frac{f_i}{N} \times 100

Cumulative Frequency Formula
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. math::

   \text{cum } f_i = f_1 + f_2 + \ldots + f_i

Categorical Example
~~~~~~~~~~~~~~~~~~~

Imagine we asked 50 students about their preferred study method:

.. list-table::
   :widths: 40 20 20
   :header-rows: 1

   * - Study Method
     - Frequency (f)
     - Relative Freq (%)
   * - Flashcards
     - 18
     - 36%
   * - Re-reading
     - 12
     - 24%
   * - Practice tests
     - 15
     - 30%
   * - Other
     - 5
     - 10%
   * - **Total**
     - **50**
     - **100%**

*Psychological Insight:* While cognitive science shows retrieval practice
("Practice tests") is highly effective, only 30% of this sample uses it.

Continuous Example (Grouped)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Continuous variables (like reaction time or sleep duration) have too many unique
values to list individually. We group them into **bins** (intervals).

.. list-table:: Sleep Duration (N=100)
   :widths: 30 30 40
   :header-rows: 1

   * - Hours Slept
     - Frequency
     - Cumulative Frequency
   * - 4.0 – 5.9
     - 6
     - 6
   * - 6.0 – 6.9
     - 21
     - 27
   * - 7.0 – 7.9
     - 44
     - 71
   * - 8.0 – 8.9
     - 23
     - 94
   * - 9.0 – 10.0
     - 6
     - 100

.. note::

   **The "Real Limits" Rule:** In PyStatsV1 and most statistical software,
   bins are treated as inclusive of the lower bound and exclusive of the
   upper bound (e.g., ``6.0 <= x < 7.0``).

4.2 Visualizing continuous data: histograms
-------------------------------------------

Numbers are helpful, but humans are visual creatures.

A histogram looks like a bar chart, but the bars **touch**. This signifies that
the variable is continuous—there is no gap between 6.99 hours and 7.00 hours.

Key interpretation checks:

* **Peaks:** Where is the data clustered?
* **Spread:** Tight vs. wide distributions.
* **Outliers:** Lone bars far from the others.

The Frequency Polygon
~~~~~~~~~~~~~~~~~~~~~

If we place a dot at the top-center of every histogram bar and connect the dots,
we get a **Frequency Polygon**.

Why polygons?

* Comparing groups becomes cleaner.
* Two overlaid histograms are messy; two polygons are readable.

.. note::

   **Accessibility Reminder:** Use colorblind-safe palettes (e.g., blue/orange)
   and never encode group differences by color alone. Add labels or line styles.

4.3 Visualizing categorical data: bar charts
--------------------------------------------

For nominal variables, we use **bar charts**.

Rules for APA-Style Bar Charts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Bars **should not** touch (these are discrete categories).
2. Order bars by **frequency**, not alphabetically, unless the categories have a natural order.
3. Keep labeling clean and descriptive.

.. warning::

   **The Prohibition of Pie Charts**

   Pie charts are rarely used in scientific psychology.

   * Humans struggle to compare angles.
   * Small differences are nearly invisible.
   * More than 4 categories = unreadable.

   **Use bar charts instead.**

4.4 The shape of data: skewness and kurtosis
--------------------------------------------

Understanding the *shape* helps diagnose phenomena and potential design issues.

Skewness: the tails
~~~~~~~~~~~~~~~~~~~

**Positive Skew (Right Skew)**  
Tail extends to the right.  
*Psychology Context:* **Floor Effects**  
Example: A very difficult memory test — most people score low, but a few score high.

**Negative Skew (Left Skew)**  
Tail extends to the left.  
*Psychology Context:* **Ceiling Effects**  
Example: An exam that was too easy — most people score high, with a small tail of low performers.

Kurtosis: the peak
~~~~~~~~~~~~~~~~~~

Kurtosis describes thickness of tails vs. center.

* **Leptokurtic:** Tall, thin — very similar scores (e.g., elite athletes).
* **Platykurtic:** Flat — large variability (e.g., general population samples).
* **Mesokurtic:** Normal distribution — moderate shape.

4.5 PyStatsV1 Lab: Exploring the sleep study dataset
----------------------------------------------------

In this chapter’s lab we will use the synthetic *sleep study* dataset
you saw earlier in this mini-book plan. It lives in the PyStatsV1
repository and is generated by the helper module
``scripts/sim_psych_sleep_study.py``.

The goal is to give you a repeatable pattern:

* load a realistic psychology dataset in Python,
* inspect its variables,
* and create basic plots that match the ideas in this chapter.

Loading the data
~~~~~~~~~~~~~~~~

From the root of the PyStatsV1 repository, open a Python session or
Jupyter notebook and run:

.. code-block:: python

    from scripts.sim_psych_sleep_study import load_sleep_study

    df = load_sleep_study()
    df.head()

You should see columns like:

* ``id`` – participant ID,
* ``class_year`` – first_year, second_year, third_year, or fourth_year,
* ``sleep_hours`` – average weeknight sleep (hours),
* ``study_method`` – flashcards, rereading, practice_tests, or mixed,
* ``exam_score`` – exam percentage (0–100).

The first time you call :func:`load_sleep_study`, it will create the
CSV file ``data/synthetic/psych_sleep_study.csv``. Later calls simply
read that file so you get the *same* dataset each time.

Frequency tables for study methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let’s build a frequency table for the categorical variable
``study_method``:

.. code-block:: python

    # Frequency (counts)
    freq = df["study_method"].value_counts().rename("f")

    # Relative frequency (percentages)
    rel_freq = (freq / len(df) * 100).round(1).rename("percent")

    # Combine into one DataFrame
    table = (
        pd.concat([freq, rel_freq], axis=1)
        .reset_index()
        .rename(columns={"index": "study_method"})
        .sort_values("f", ascending=False)
    )

    print(table)

This prints a table like:

.. code-block:: text

    study_method         f  percent
    practice_tests      36    30.0
    flashcards          34    28.3
    rereading           30    25.0
    mixed               20    16.7

This mirrors the frequency tables earlier in the chapter, but now the
numbers come from data you could plausibly collect in a real study
skills experiment.

Histogram of sleep hours
~~~~~~~~~~~~~~~~~~~~~~~~

Now make a histogram of the continuous variable ``sleep_hours``:

.. code-block:: python

    import matplotlib.pyplot as plt

    plt.hist(df["sleep_hours"], bins=10, edgecolor="black")
    plt.xlabel("Sleep hours (weeknight average)")
    plt.ylabel("Number of students")
    plt.title("Distribution of sleep duration")
    plt.show()

When you look at the plot, ask:

* Where is the data clustered (what is the *mode*)?
* Are there students sleeping very little or a lot (potential outliers)?
* Does the shape look roughly symmetric, or skewed?

Bar chart for study methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~

For the categorical ``study_method`` variable, use a bar chart:

.. code-block:: python

    freq = df["study_method"].value_counts().sort_values(ascending=False)

    plt.bar(freq.index, freq.values)
    plt.ylabel("Number of students")
    plt.title("Preferred study method")
    plt.xticks(rotation=20)
    plt.show()

Notice that the bars are separated (this is categorical, not continuous)
and we have ordered them from most common to least common.

4.6 What you should take away
-----------------------------

By the end of this chapter and lab you should be able to:

* construct frequency tables for categorical and grouped continuous data,
* choose appropriate visualizations (histograms for continuous data,
  bar charts for categorical data),
* interpret the *shape* of a distribution (center, spread, skewness),
* and run a small, reproducible analysis by loading
  ``load_sleep_study()`` from the PyStatsV1 repository.

In later chapters we will reuse this same dataset when we talk about
measures of central tendency, variability, and eventually
correlation and regression. That way the plots and statistics you see
in the text are always tied to a concrete psychological story.