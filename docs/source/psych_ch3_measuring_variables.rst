.. _psych_ch3:

Psychological Science & Statistics – Chapter 3
==============================================

Defining and Measuring Variables: How Concepts Become Data
----------------------------------------------------------

Psychology studies things we cannot directly see: attention, emotion,
memory, stress, prejudice, personality, motivation. These are *concepts*,
but our statistical tools require *numbers*. Chapter 3 shows how
psychologists translate ideas into measurable variables, and how good
measurement determines the quality of scientific conclusions.

This chapter has five goals:

* explain conceptual vs. operational definitions,
* introduce the four scales of measurement (NOIR),
* describe reliability and why consistency matters,
* explain validity and how we know a measure works,
* connect these ideas to a short PyStatsV1 lab.

Most of the statistical mistakes students struggle with later trace back
to measurement problems introduced here.

3.1 Conceptual vs. operational definitions
------------------------------------------

A **conceptual definition** is the idea you care about.  
A **operational definition** is how you *measure* that idea.

Examples:

* *Conceptual*: Anxiety  
  *Operational*: Score on the GAD-7 questionnaire.

* *Conceptual*: Aggression  
  *Operational*: Number of noise blasts delivered in a competitive reaction-time task.

* *Conceptual*: Working memory  
  *Operational*: Number of items correctly recalled in a digit-span test.

Why operational definitions matter:

* They determine what the data actually represent.
* Different operationalizations can lead to different conclusions.
* Clarity allows replication — another researcher must be able to reproduce your measure.

A strong research question always pairs both:

::

    Conceptual definition → Operational definition → Data

3.2 Scales of measurement (NOIR)
--------------------------------

Not all numbers behave the same way statistically. Psychologists classify
variables into four **scales of measurement**, often remembered as **NOIR**:

**Nominal (names)**  
    Categories with no numeric meaning.  
    *Examples:* gender identity, therapy type, favorite color.

**Ordinal (rank order)**  
    Ordered categories, but distances between ranks are unknown.  
    *Examples:* symptom severity ratings (“mild / moderate / severe”), Likert scales.

**Interval (equal units)**  
    Numeric scales with equal steps, but no true zero.  
    *Examples:* temperature in °C or °F, many psychological test scores.

**Ratio (meaningful zero)**  
    All properties of interval scales plus a true zero.  
    *Examples:* reaction time, number of errors, hours slept.

Why NOIR matters:

* Some statistical tests **require** interval or ratio data.
* Treating ordinal data as interval is common — but needs justification.
* Ratio scales allow multiplicative statements (“twice as fast”).

3.3 Reliability: consistency of measurement
-------------------------------------------

A measure must be **reliable** to be useful. Reliability asks:

**“If we measured the same thing again, would we get a similar result?”**

Three major forms:

**Test–retest reliability**  
    Are scores stable across time?  
    Important for traits (e.g., personality).

**Inter-rater reliability**  
    Do two observers agree?  
    Important for coding behavior or scoring essays.

**Internal consistency**  
    Do items on a questionnaire measure the same underlying construct?  
    Measured with statistics like **Cronbach’s alpha**.

Rules of thumb:

* Reliability near **0.70** is acceptable in early research.
* Low reliability puts an upper bound on validity.
* Reliability is necessary — but not sufficient — for good measurement.

3.4 Validity: accuracy of measurement
-------------------------------------

If reliability is about consistency, **validity** is about truth.

A measure is valid if it accurately captures the construct it claims to measure.

Major forms of validity:

**Face validity**  
    Does the measure *look* like it measures the construct?

**Content validity**  
    Does it cover all relevant aspects of the construct?

**Criterion validity**  
    Do scores predict something they should predict?  
    *Example:* A depression score predicting therapist diagnoses.

**Convergent validity**  
    Does it correlate with other measures of the same construct?

**Discriminant validity**  
    Does it *not* correlate with measures of different constructs?

Key idea:

::

    A test can be reliable but not valid.
    A test cannot be valid unless it is reliable.

3.5 PyStatsV1 lab: exploring variable types
-------------------------------------------

Let’s look at a tiny example dataset (from a future chapter’s lab) and
use PyStatsV1 conventions to understand variable types.

.. code-block:: python

    import pandas as pd

    # Example dataset (placeholder path)
    data = pd.read_csv("data/study1_sleep_anxiety.csv")

    print(data.head())
    print("\nVariable types:")
    print(data.dtypes)

This simple script begins the habit of **inspecting** variables before
analyzing them — a crucial skill for psychological researchers.

In full PyStatsV1 labs, students will:

* classify variables using NOIR,
* identify operational definitions,
* check reliability (e.g., Cronbach’s alpha),
* assess validity using correlations and scatterplots.

Measurement is where scientific thinking meets statistical reasoning.

3.6 What you should take away
-----------------------------

By the end of this chapter you should be able to:

* distinguish conceptual and operational definitions,
* classify variables into nominal, ordinal, interval, or ratio,
* explain why reliability matters and name its three major forms,
* describe common types of validity and why no single type is sufficient,
* see how PyStatsV1 helps document and inspect variables before analysis.

In later chapters, we will build statistical tests on top of this
foundation. Sound conclusions require sound measurement.

