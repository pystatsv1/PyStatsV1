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

4.5 PyStatsV1 Lab: automated visualization
------------------------------------------

In standard Python, APA-style visualization requires multiple steps.  
PyStatsV1 simplifies this to help students focus on psychological interpretation.

Step 1: load your data
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import pystatsv1 as ps

    # Load a sample dataset included in PyStatsV1
    df = ps.datasets.load_sleep_study()

    print(df.head())

Step 2: the ``explore`` module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Frequency table:**

.. code-block:: python

    ps.explore.freq_table(df, column="study_method")

**Histogram:**

.. code-block:: python

    ps.explore.histogram(
        data=df,
        variable="sleep_hours",
        bins=10,
        title="Distribution of Sleep Duration",
        show_stats=True   # overlays mean and SD
    )

Step 3: assessing distribution shape
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    stats = ps.explore.describe_shape(df["sleep_hours"])
    print(stats)

    # Example output:
    # Skewness: -0.45 (Slight negative skew)
    # Kurtosis:  0.12 (Mesokurtic)
    # Interpretation: No major floor or ceiling effects detected.

4.6 What you should take away
-----------------------------

* **Frequency tables** summarize data and should include relative and cumulative percentages.
* **Histograms** (continuous) and **bar charts** (categorical) reveal essential patterns.
* **Skewness** indicates floor or ceiling effects; **kurtosis** reveals variability patterns.
* **PyStatsV1** allows rapid, APA-style EDA through the ``explore`` module.

Next up: **Chapter 5** explores measures of *central tendency* and *variability*—
the foundations of descriptive statistics in psychology.
