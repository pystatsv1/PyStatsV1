
Chapter 17 – Mixed-Model Designs
================================

Learning goals
--------------

In this chapter you will learn how to:

* describe the logic of *mixed-model* (split-plot) designs,
* distinguish between **between-subjects** and **within-subjects** factors,
* understand why mixed designs have different error terms for different effects,
* interpret a mixed ANOVA table (Group, Time, and Group × Time),
* and use :mod:`pystatsv1` and :mod:`pingouin` to analyze a simple treatment study.

By the end of the chapter, you should be able to read a mixed ANOVA output and
explain, in plain language, what each line means for a psychology research
question.

17.1 The hybrid design: between-subjects + within-subjects
----------------------------------------------------------

So far in Track B you have seen:

* **Between-subjects** designs (Chapters 10, 12, 13), where each participant
  belongs to one condition only; and
* **Within-subjects** designs (Chapters 11 and 14), where the *same*
  participants are measured repeatedly (e.g., Pre, Post, Follow-up).

A **mixed-model design** combines these two ideas. A classic example is a
treatment study where:

* people are randomly assigned to a **Group** (Treatment vs Control), and
* everyone is measured at multiple **Time** points (Pre, Post, Follow-up).

.. note::

   In psychology, mixed designs are extremely common. Any longitudinal study
   that compares two or more groups over time is likely to be a mixed model.

Terminology
~~~~~~~~~~~

**Between-subjects factor**
    A factor where different participants belong to different levels.
    In this chapter, ``group`` (``"control"`` vs ``"treatment"``) is a
    between-subjects factor.

**Within-subjects factor**
    A factor where each participant is measured at *each* level.
    In this chapter, ``time`` (``"pre"``, ``"post"``, ``"followup"``) is a
    within-subjects factor.

**Mixed design**
    A design that includes at least one between-subjects factor and at least
    one within-subjects factor. Sometimes called a *split-plot* design.

Why use a mixed design?
~~~~~~~~~~~~~~~~~~~~~~~

Mixed designs give you the best of both worlds:

* You can look at **group differences** (Treatment vs Control).
* You can look at **change over time** (Pre vs Post vs Follow-up).
* You can test whether the **pattern of change over time is different
  for each group** (the Group × Time *interaction*).

This is usually the main scientific question:

*Did the treatment group improve more over time than the control group?*

17.2 The split-plot logic and error terms
-----------------------------------------

In a pure between-subjects ANOVA (Chapter 13), all error comes from
**differences between participants** within each condition.

In a pure repeated-measures ANOVA (Chapter 14), a lot of that individual
difference error is removed because each person acts as their own control.

In a **mixed** design, we have both types of variation:

* differences **between participants** (some students are generally more
  anxious than others), and
* differences **within participants over time** (everyone may change from
  Pre to Post to Follow-up).

A mixed ANOVA therefore has different error terms for different effects:

* The **Group** effect (Treatment vs Control) uses an error term based on
  *between-subject* variability.
* The **Time** effect and the **Group × Time interaction** use an error term
  based on *within-subject* variability.

You do **not** have to compute these error terms by hand in this chapter.
Instead, we focus on:

* understanding the design,
* structuring the data correctly,
* and learning how to read the output from a trusted library
  (here, :mod:`pingouin`).

17.3 Example: Treatment vs control across three time points
-----------------------------------------------------------

We will work with a simple, synthetic example that mimics a common
clinical psychology design.

Scenario
~~~~~~~~

A clinical psychologist wants to test whether a new cognitive-behavioural
program reduces anxiety compared to a waitlist control group.

* Participants are randomly assigned to **Treatment** or **Control**.
* Everyone completes an anxiety scale at three time points:

  * ``pre``   – before treatment starts,
  * ``post``  – immediately after treatment, and
  * ``followup`` – three months later.

Hypotheses
~~~~~~~~~~

* **Group main effect**:

  *H0*: There is no overall difference in anxiety between Treatment and Control.  
  *H1*: One group has higher average anxiety than the other.

* **Time main effect**:

  *H0*: Average anxiety is the same at Pre, Post, and Follow-up.  
  *H1*: Average anxiety changes over time (e.g., decreases after treatment).

* **Group × Time interaction** (the most important):

  *H0*: The pattern of change over time is the same for both groups.  
  *H1*: The pattern of change over time is *different* (e.g., Treatment
  improves more from Pre to Post and maintains gains at Follow-up).

Data structure
~~~~~~~~~~~~~~

As with Chapter 14, we will work with both **wide** and **long** formats.

*Wide format* (one row per participant)::

   subject  group  anxiety_pre  anxiety_post  anxiety_followup
   -----------------------------------------------------------
   01       control      52.3         50.1              48.7
   02       control      47.8         49.2              48.9
   03       treatment    51.9         40.6              38.2
   ...

*Long format* (one row per person *per time point*)::

   subject    group     time      anxiety
   --------------------------------------
   control_01 control   pre        52.3
   control_01 control   post       50.1
   control_01 control   followup   48.7
   treat_01   treatment pre        51.9
   treat_01   treatment post       40.6
   treat_01   treatment followup   38.2
   ...

Most mixed ANOVA functions (including :func:`pingouin.mixed_anova`) expect the
**long** format with columns that label:

* the **within-subjects factor** (``time``),
* the **between-subjects factor** (``group``), and
* the **dependent variable** (``anxiety``).

17.4 PyStatsV1 lab – structuring and analyzing a mixed design
-------------------------------------------------------------

The Chapter 17 lab is implemented in the script
:mod:`scripts.psych_ch17_mixed_models`.  It has three main responsibilities:

1. **Simulate a mixed design dataset** where Treatment improves more than
   Control over time.
2. **Reshape the data** into both wide and long formats.
3. **Run a mixed ANOVA with :mod:`pingouin`** and save clean outputs for
   students to inspect.

Simulating the data
~~~~~~~~~~~~~~~~~~~

The function :func:`simulate_mixed_design_dataset` constructs a dataset with:

* two groups (``"control"`` and ``"treatment"``),
* three time points (``"pre"``, ``"post"``, ``"followup"``),
* and an anxiety outcome designed so that:

  * both groups start with similar anxiety at ``pre``,
  * the treatment group shows a strong drop from ``pre`` to ``post``, and
  * the control group changes very little.

To keep the lab deterministic and testable, the simulation uses a fixed random
seed by default.

Running the mixed ANOVA
~~~~~~~~~~~~~~~~~~~~~~~

The core analysis uses :func:`pingouin.mixed_anova` applied to the long-format
data::

   import pingouin as pg

   aov = pg.mixed_anova(
       data=long_df,
       dv="anxiety",
       within="time",
       between="group",
       subject="subject",
   )

The resulting table contains separate rows for:

* the **Group** main effect,
* the **Time** main effect, and
* the **Group × Time** interaction.

For each effect, you get:

* degrees of freedom (``DF1``, ``DF2``),
* F-statistic (``F``),
* p-value (``p-unc``),
* and effect size metrics such as partial eta-squared (``np2``).

When the simulation is working correctly, you should see:

* a modest or small **Group** main effect,
* a clear **Time** main effect (participants change over time), and
* a strong **Group × Time** interaction (Treatment improves more than Control).

Saved outputs
~~~~~~~~~~~~~

When you run the lab via the Makefile target::

   make psych-ch17

the script will:

* print key results to the console,
* save the simulated long-format data to::

    data/synthetic/psych_ch17_mixed_design_long.csv

* save the wide-format data to::

    data/synthetic/psych_ch17_mixed_design_wide.csv

* save the mixed ANOVA table to::

    outputs/track_b/ch17_mixed_anova.csv

* and create an interaction plot (group means over time) at::

    outputs/track_b/ch17_group_by_time_means.png

Instructors can use these files for in-class demonstrations, and students can
use them for homework or project work without having to re-run the simulation.

Connection to future chapters
-----------------------------

Mixed-model designs sit at the intersection of several ideas you have already
seen:

* **Factorial logic** from Chapter 13 (main effects and interactions),
* **Repeated-measures logic** from Chapter 14 (within-subject error terms),
* and **Regression logic** from Chapters 15–16 (predicting outcomes from
  multiple sources of information).

The next chapters extend these ideas further:

* Chapter 18 shows how to statistically control for a *covariate* using
  ANCOVA.
* Chapter 19 introduces non-parametric alternatives for situations where
  standard ANOVA assumptions are not met.
* Chapter 20 brings everything together in a full PyStatsV1 project.

For now, the goal is not to master every technical detail of mixed-model
mathematics, but to develop a solid *conceptual* understanding and a reliable,
reproducible workflow for analyzing the kinds of treatment-over-time studies
that are central to modern psychological science.
