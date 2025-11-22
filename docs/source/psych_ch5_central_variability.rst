.. _psych_ch5:

Psychological Science & Statistics – Chapter 5
==============================================

Central Tendency and Variability: Summarizing What We See
---------------------------------------------------------

Chapter 4 was about *looking* at data—frequency tables and graphs that show
the overall shape of a distribution. In this chapter we take the next step:

*Can we describe that distribution with a few meaningful numbers?*

Psychology relies heavily on this kind of summary. We say things like:

* "On average, the treatment group slept longer than the control group."
* "There was a lot of variability in stress scores."
* "Most participants were near the mean, but a few scored far out in the tails."

This chapter introduces:

* measures of **central tendency** (where the distribution is centered), and
* measures of **variability** (how spread out the scores are).

We will keep connecting these ideas back to the sleep-study dataset and
other realistic psychological examples.

5.1 Why central tendency and variability both matter
----------------------------------------------------

If you only know the *average* of a set of scores, you know almost nothing
about how individuals actually behaved.

Imagine two classes that took the same exam:

* Class A: Most students scored between 78 and 82.  
* Class B: Half the students scored around 50 and the other half around 100.

Both classes could have the **same mean**, but the stories these data tell
are very different.

To understand a distribution, we need **both**:

* a number that summarizes "typical" or "central" performance, and
* a number that summarizes how much scores vary around that center.

5.2 Measures of central tendency: mean, median, mode
-----------------------------------------------------

There are three classic measures of central tendency.

The mean (arithmetic average)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **mean** is what most people casually call the "average". It is defined as

.. math::

   \bar{x} = \frac{1}{N} \sum_{i=1}^N x_i,

where :math:`x_i` are the individual scores and :math:`N` is the number of
participants.

*Psychology use case:* We often report the mean reaction time, mean depression
score, mean hours of sleep, etc.

**Strengths**

* Uses *all* the data.
* Works well with many statistical models (especially those based on the Normal
  distribution).

**Weaknesses**

* Extremely sensitive to **outliers** (one person who barely slept can drag
  down the mean sleep hours).
* Can be misleading for heavily skewed distributions.

The median (the middle score)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **median** is the value that splits the distribution in half:

* 50% of scores are at or below the median.
* 50% are at or above.

To find the median, sort the scores from smallest to largest, then pick the
middle one (or average the two middle scores if there are an even number of
observations).

**Strengths**

* Robust against outliers and skewed data.
* Often a better description of "typical" behavior when the distribution is
  highly skewed (e.g., income, number of social media followers).

The mode (most frequent score)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **mode** is simply the most common value in a distribution.

* For continuous variables (like reaction time), the mode is often less useful.
* For categorical variables (e.g., study method, therapy type), the mode tells
  you which category is most popular.

**In practice**

In applied psychology, we usually report **mean** and **standard deviation**
for roughly symmetric, continuous variables, and we may report **median** and
a measure of spread (e.g., interquartile range) when the distribution is skewed.

5.3 The problem with averages: when the mean misleads
-----------------------------------------------------

The mean can give a false sense of what is "typical".

Example: Sleep and outliers
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Suppose we measured hours of sleep last night for 10 participants:

.. math::

   6, 6.5, 7, 7, 7.5, 8, 8, 8.5, 9, 2

Most participants slept between 6 and 9 hours, but one person only slept 2.
The mean is

.. math::

   \bar{x} = \frac{6 + 6.5 + \dots + 9 + 2}{10} = 7.1 \text{ hours (approx).}

The median, however, is 7.5 hours.

*If you were designing a sleep intervention, which number better captures what
is typical in this group?*

This demonstrates:

* **Outliers** can pull the mean away from where most data lie.
* Reporting the median alongside the mean can help detect this problem.
* Graphs (like histograms) are essential companions to numerical summaries.

5.4 Measures of variability: range, IQR, variance, SD
-----------------------------------------------------

Central tendency tells us *where* scores cluster. Variability tells us
*how tightly* they cluster.

The range
~~~~~~~~~

The **range** is the simplest measure:

.. math::

   \text{Range} = \text{Maximum} - \text{Minimum}.

It shows the width of the distribution but is extremely sensitive to outliers.

The interquartile range (IQR)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **interquartile range (IQR)** focuses on the middle 50% of the data:

* :math:`Q_1` (first quartile): 25th percentile.
* :math:`Q_3` (third quartile): 75th percentile.

.. math::

   \text{IQR} = Q_3 - Q_1.

A large IQR means scores are spread out; a small IQR means participants are
relatively similar.

The variance and standard deviation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The **variance** and **standard deviation (SD)** go beyond extremes and
quantiles by using all the data.

For a **sample** of scores :math:`x_1, \dots, x_N`, the sample variance is

.. math::

   s^2 = \frac{1}{N - 1} \sum_{i=1}^N (x_i - \bar{x})^2.

The standard deviation is the square root:

.. math::

   s = \sqrt{s^2}.

Interpretation:

* If scores are tightly clustered around the mean, :math:`s` is small.
* If scores are widely spread out, :math:`s` is large.
* Under many models, most scores fall within about 1–2 standard deviations of
  the mean.

In psychological research reports we almost always see something like:

*“Participants slept an average of 7.2 hours (SD = 1.1).”*

5.5 Degrees of freedom: why divide by N − 1?
--------------------------------------------

You may have noticed that the variance formula uses :math:`N - 1` rather than
:math:`N` in the denominator. This is related to the idea of **degrees of
freedom (df)**.

Informally, degrees of freedom are the number of independent pieces of
information available for estimating a parameter.

For the sample variance:

* Once you know the sample mean :math:`\bar{x}`, the deviations
  :math:`(x_i - \bar{x})` must sum to zero.
* That means if you know :math:`N - 1` of the deviations, the last one is
  already determined.

So there are only :math:`N - 1` independent deviations, and we divide by
:math:`N - 1` to obtain an **unbiased** estimate of the population variance.

This idea of degrees of freedom will appear again in t-tests and ANOVAs
later in the mini-book.

5.6 PyStatsV1 Lab: Summarizing the sleep-study data
---------------------------------------------------

In this lab we return to the **sleep study** dataset. We will:

* compute mean, median, and mode for hours of sleep,
* compute range, IQR, and standard deviation,
* compare summaries across study methods.

Loading the dataset
~~~~~~~~~~~~~~~~~~~

If you have cloned the PyStatsV1 repository, the CSV file will be located in
the ``data`` folder. You can load it with pandas:

.. code-block:: python

   import pandas as pd

   data = pd.read_csv("data/psych_sleep_study.csv")

   print(data.head())
   print(data.dtypes)

You should see variables such as:

* ``participant_id`` – unique ID per participant,
* ``sleep_hours`` – hours of sleep last night (continuous),
* ``study_method`` – preferred study method (categorical),
* ``chronotype`` – morning/evening type (categorical),
* possibly additional variables (e.g., stress score) depending on the simulation.

Overall summaries
~~~~~~~~~~~~~~~~~

First, let us compute basic summaries for the entire sample:

.. code-block:: python

   sleep = data["sleep_hours"]

   mean_sleep = sleep.mean()
   median_sleep = sleep.median()
   mode_sleep = sleep.mode()  # may return more than one value

   print(f"Mean sleep:   {mean_sleep:.2f} hours")
   print(f"Median sleep: {median_sleep:.2f} hours")
   print("Mode(s):")
   print(mode_sleep.values)

   # Measures of spread
   sleep_range = sleep.max() - sleep.min()
   iqr_sleep = sleep.quantile(0.75) - sleep.quantile(0.25)
   sd_sleep = sleep.std(ddof=1)

   print(f"Range: {sleep_range:.2f} hours")
   print(f"IQR:   {iqr_sleep:.2f} hours")
   print(f"SD:    {sd_sleep:.2f} hours")

As you run this code, ask:

* Is the mean close to the median, or are there signs of skewness?
* Does the SD seem small (participants similar) or large (participants differ widely)?
* Do the numbers match what you saw in the histogram from Chapter 4?

Group summaries by study method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Now let us see whether preferred study method is associated with how much
students slept. We compute group-wise means and SDs:

.. code-block:: python

   grouped = (
       data
       .groupby("study_method")["sleep_hours"]
       .agg(["count", "mean", "median", "std"])
       .rename(columns={"std": "sd"})
       .sort_values("mean", ascending=False)
   )

   print(grouped)

This table tells us, for each study method:

* how many students chose it (``count``),
* their average hours of sleep (``mean``),
* the median hours of sleep (``median``),
* how much their sleep varies (``sd``).

You might find, for example, that students who use practice tests have
slightly different sleep patterns than those who rely on re-reading.

Connecting back to research design
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In a real study, we might ask:

* Is study method causing differences in sleep?
* Or are both sleep and study method being influenced by some third variable,
  like stress or personality?

For now, our goal is more modest: using central tendency and variability to
summarize what is happening in this sample.

5.7 What you should take away
-----------------------------

By the end of this chapter and lab you should be able to:

* explain the difference between **mean**, **median**, and **mode**, and when
  each is most appropriate,
* describe why averages can be misleading in the presence of **outliers** or
  **skewed** distributions,
* compute and interpret common measures of variability (range, IQR, variance,
  standard deviation),
* understand, at an intuitive level, why the sample variance uses
  :math:`N - 1` in the denominator (degrees of freedom),
* use Python and pandas to compute these summaries for a realistic
  psychological dataset,
* compare central tendency and spread across groups (e.g., different study
  methods) to generate new research questions.

In the next chapter we connect these ideas to the **Normal distribution**
and **z-scores**, which provide a bridge from descriptive summaries to
probabilities and, eventually, to hypothesis testing.
