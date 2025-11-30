Chapter 13 – Factorial Designs and the Two-Way ANOVA 
===================================================

In Chapters 10–12 you learned how to compare two or more groups on **one**
independent variable (IV):

* independent-samples *t*-tests for two groups (between-subjects),
* paired-samples *t*-tests for repeated measures (within-subjects),
* one-way ANOVA for three or more groups on a single factor.

In real psychological research, however, we rarely care about just one factor
at a time. We ask questions like:

* Does a training program help **more** under high stress than low stress?
* Does a therapy work **better for some age groups than others**?
* Does feedback style interact with **time pressure** to affect performance?

These questions involve **more than one independent variable**. The standard
tool is the **factorial design**, analyzed with a **two-way ANOVA** (for two
factors).

Our goals in this chapter are to help you:

* understand the logic of factorial designs and the 2 × 2 notation,
* distinguish **main effects** from **interactions**,
* interpret interactions as **"differences of differences"**,
* see examples of spreading vs. crossover interactions,
* appreciate the idea of **simple main effects** as follow-up tests, and
* run and interpret a two-way ANOVA using PyStatsV1 on a balanced design.

Design Logic: Two Factors at Once
---------------------------------

We will use a simple 2 × 2 example throughout.

Suppose a lab studies a stress-management training program. Participants are
randomly assigned to:

* **Training** factor (Factor A)
  - ``control`` – no training
  - ``cbt`` – brief cognitive–behavioral training

and then complete a challenging task either under:

* **Context** factor (Factor B)
  - ``low_stress`` – quiet room, no time pressure
  - ``high_stress`` – noisy room, strict time pressure

The dependent variable is a continuous ``stress_score`` (higher = more stress).

This design has **two factors** (Training and Context), each with **two
levels**, so we call it a **2 × 2 factorial design**.

Notation for Factorial Designs
------------------------------

A shorthand like **2 × 2** tells you:

* **the number of levels of each factor**, and
* how many experimental **cells** there are.

Examples:

* 2 × 2

  * Factor A has 2 levels, Factor B has 2 levels.
  * Total cells: :math:`2 \times 2 = 4` (control/low, control/high, cbt/low,
    cbt/high).

* 2 × 3

  * Factor A has 2 levels, Factor B has 3 levels.
  * Total cells: :math:`2 \times 3 = 6`.

* 2 × 2 × 2

  * Three factors, each with 2 levels.
  * Total cells: :math:`2 \times 2 \times 2 = 8`.

In this chapter we focus on the **two-way** case (two factors). The ideas
generalize to more complex designs, but two-way ANOVA is the workhorse for
most undergraduate research projects.

Main Effects
------------

A **main effect** is the overall effect of **one factor, averaging over the
levels of the other factor**.

* The **main effect of Training** asks:

  > On average across both Context conditions, do participants in ``cbt``
  > differ from those in ``control``?

* The **main effect of Context** asks:

  > On average across both Training conditions, do participants in
  > ``high_stress`` differ from those in ``low_stress``?

We compute **marginal means** to answer these questions. For example:

* Mean stress in ``control``:
  average of (control, low_stress) and (control, high_stress).
* Mean stress in ``cbt``:
  average of (cbt, low_stress) and (cbt, high_stress).

If those marginal means differ, there is evidence of a main effect for that
factor.

Interactions: The “It Depends” Effect
-------------------------------------

The most important idea in factorial designs is the **interaction**.

An **interaction** occurs when **the effect of one factor depends on the level
of the other factor**.

In our example, we ask:

*Does the benefit of CBT training depend on whether the context is
low-stress or high-stress?*

Mathematically, we can think of an interaction as a **difference of
differences**.

Let:

* :math:`\bar{X}_{\text{control, low}}` be the mean stress for control/low,
* :math:`\bar{X}_{\text{control, high}}` for control/high,
* :math:`\bar{X}_{\text{cbt, low}}` for cbt/low,
* :math:`\bar{X}_{\text{cbt, high}}` for cbt/high.

Compute the Training effect within each Context:

.. math::

   \text{Training effect at low stress}
   = \bar{X}_{\text{control, low}} - \bar{X}_{\text{cbt, low}},

.. math::

   \text{Training effect at high stress}
   = \bar{X}_{\text{control, high}} - \bar{X}_{\text{cbt, high}}.

The **interaction** for Training × Context is the difference between these
two effects:

.. math::

   \text{Interaction (difference of differences)}
   = (\bar{X}_{\text{control, high}} - \bar{X}_{\text{cbt, high}})
     - (\bar{X}_{\text{control, low}} - \bar{X}_{\text{cbt, low}}).

If that difference of differences is zero (within random error), we say there
is **no interaction**. If it is clearly non-zero, we have an interaction: the
effect of training changes across contexts.

Graphical View: Non-Parallel Lines
----------------------------------

Interactions are often easiest to see in a **line graph**:

* Put Context on the x-axis (low vs high).
* Plot mean stress for each Training condition as a separate line.

Then:

* If the lines are **parallel**, the Training effect is similar at low and
  high stress → no interaction (or only a trivial one).
* If the lines **spread apart**, **converge**, or **cross**, the Training
  effect changes with Context → interaction.

Two common patterns:

* **Spreading interaction**

  Training helps under high stress but has little effect under low stress.
  The lines diverge as you move from low to high stress.

* **Crossover interaction**

  Control performs better in low stress, but CBT performs better in high
  stress (or vice versa). The lines literally cross.

Simple Main Effects
-------------------

When an interaction is present, main effects can be hard to interpret on their
own.

For example, suppose CBT reduces stress **only** in the high-stress context.
The overall (marginal) means for Training might still show a "modest" effect,
even though the real story is:

* CBT ≈ control under low stress,
* CBT < control under high stress.

To unpack this, researchers examine **simple main effects**:

* the effect of one factor **at a single level of the other factor**.

Examples:

* Simple effect of Training **within low_stress**:
  compare control vs cbt using only low-stress participants.
* Simple effect of Training **within high_stress**:
  compare control vs cbt using only high-stress participants.
* Simple effect of Context **within control**:
  compare low vs high stress among control participants only.

In practice, simple main effects are often tested with *t*-tests or
one-way ANOVAs conducted **within** a subset of the data, sometimes combined
with Bonferroni or other corrections for multiple tests.

In the PyStatsV1 lab for this chapter, the two-way ANOVA is the primary
analysis. For pedagogical purposes, the script also shows how to compute a few
simple main effects (for example, Training within each Context) using
independent-samples *t*-tests when the interaction is statistically
significant.

The Two-Way ANOVA: Partitioning Variance
----------------------------------------

Factorial ANOVA extends the one-way ANOVA logic from Chapter 12. We still
partition the total variability in the outcome into meaningful components.

Let:

* Factor A = Training (2 levels),
* Factor B = Context (2 levels),
* :math:`Y_{ijk}` be the score for person :math:`k` in cell :math:`(i, j)`,
  where :math:`i` indexes levels of A and :math:`j` indexes levels of B,
* :math:`n_{ij}` be the number of participants in cell :math:`(i, j)`,
* :math:`\bar{Y}_{ij}` be the **cell mean** for cell :math:`(i, j)`,
* :math:`\bar{Y}_{i\cdot}` be the marginal mean for level :math:`i` of A,
* :math:`\bar{Y}_{\cdot j}` be the marginal mean for level :math:`j` of B,
* :math:`\bar{Y}_{\cdot\cdot}` be the **grand mean** across all participants.

Then the total sum of squares can be written as:

.. math::

   SS_{\text{Total}}
   = \sum_{i}\sum_{j}\sum_{k}
     (Y_{ijk} - \bar{Y}_{\cdot\cdot})^2.

For a **balanced** 2 × 2 design (equal :math:`n_{ij}` in each cell), we can
decompose this into:

.. math::

   SS_{\text{Total}} =
   SS_{A} + SS_{B} + SS_{AB} + SS_{\text{Within}},

where:

* :math:`SS_A` captures the main effect of Training,
* :math:`SS_B` captures the main effect of Context,
* :math:`SS_{AB}` captures the interaction,
* :math:`SS_{\text{Within}}` is the within-cell (error) variability.

*Note: For these components to be additive (A + B + AB), the design must be balanced.*

Each component has associated degrees of freedom (df) and a mean square (MS)
obtained by dividing SS by its df. The *F*-tests for each effect are:

.. math::

   F_A = \frac{MS_A}{MS_{\text{Within}}}, \quad
   F_B = \frac{MS_B}{MS_{\text{Within}}}, \quad
   F_{AB} = \frac{MS_{AB}}{MS_{\text{Within}}}.

Effect sizes (for example, :math:`\eta^2` for each effect) can be computed as
the proportion of total variance associated with each SS component. As with
one-way ANOVA, these sample-based measures tend to slightly overestimate the
population effect sizes, but they are helpful descriptive summaries.

Assumptions in the Two-Way ANOVA
--------------------------------

The classical two-way ANOVA relies on similar assumptions to the one-way case:

* **Independence**

  Observations are independent within and across cells (for example, each
  participant appears in only one cell).

* **Normality**

  The outcome scores within each cell are approximately Normally distributed.

* **Equal variances**

  The population variances are roughly equal across cells (homogeneity of
  variance).

* **Balanced design (for our manual calculations)**

  In this chapter, we assume **equal sample sizes in each cell** (for example,
  25 participants per Training × Context combination). This greatly simplifies
  the sums of squares and matches the PyStatsV1 implementation.

.. warning:: Balanced vs. Unbalanced Designs

   The manual calculations and PyStatsV1 helpers in this chapter assume a
   **balanced design** with equal sample sizes in every cell.

   If sample sizes differ (unbalanced), the factors become correlated and
   sums of squares must be computed using more advanced methods (for example,
   Type III sums of squares). Professional software (such as SPSS, SAS, or
   R packages) handles this automatically, but our hand-calculation formulas
   and simple code do **not**.

   For this reason, when you experiment with the Chapter 13 script, keep the
   cell sizes equal. If you need to analyze an unbalanced design in real
   research, use dedicated statistical software and pay close attention to
   how it defines and reports sums of squares.

PyStatsV1 Lab: Two-Way ANOVA on Stress Scores
---------------------------------------------

In this lab, you will analyze a simulated 2 × 2 factorial experiment with:

* Factor A: ``training`` (``control`` vs ``cbt``),
* Factor B: ``context`` (``low_stress`` vs ``high_stress``),
* Dependent variable: ``stress_score``.

You will:

* simulate a balanced dataset with the same :math:`n` in each cell,
* compute:

  - cell means and sample sizes,
  - marginal means for each level of Training and Context,
  - sums of squares :math:`SS_A`, :math:`SS_B`, :math:`SS_{AB}`,
    :math:`SS_{\text{Within}}`, :math:`SS_{\text{Total}}`,
  - corresponding degrees of freedom and mean squares,
  - *F*-statistics and *p*-values for each main effect and the interaction,
  - eta-squared style effect sizes for each effect,

* visualize the interaction with a simple line plot of cell means,
* optionally compute a small set of **simple main effects** (for example,
  Training within each Context) when the interaction is statistically
  significant.

All code for this lab lives in:

* ``scripts/psych_ch13_two_way_anova.py``

and the script can optionally write outputs to:

* ``data/synthetic/psych_ch13_two_way_stress.csv``

Running the Lab Script
----------------------

From the project root, you can run:

.. code-block:: bash

   python -m scripts.psych_ch13_two_way_anova

If your Makefile defines a convenience target, you can instead run:

.. code-block:: bash

   make psych-ch13

This will:

* simulate a balanced 2 × 2 Training × Context dataset,
* print the cell means and sample sizes,
* compute the two-way ANOVA table with *F*-tests for:

  - main effect of Training,
  - main effect of Context,
  - Training × Context interaction,

* report eta-squared style effect sizes for each effect,
* draw (or save) a simple interaction plot of mean stress by Context, with
  separate lines for each Training condition,
* optionally compute and print simple main effects (for example, Training
  within low_stress and within high_stress) when the interaction is
  statistically significant.

Expected Console Output
-----------------------

Your exact numbers will vary if you change the seed or parameters, but with the
default settings you might see output like:

.. code-block:: text

   Two-way ANOVA on stress scores (Training × Context)
   ---------------------------------------------------
   Cell means (n per cell = 25):
     control, low_stress    mean = 17.9
     control, high_stress   mean = 23.4
     cbt,     low_stress    mean = 16.8
     cbt,     high_stress   mean = 18.9

   ANOVA table:
     SS_A  (Training)       =  95.21, df_A  = 1, MS_A  = 95.21,  F_A  =  4.10, p_A  = 0.046
     SS_B  (Context)        = 640.37, df_B  = 1, MS_B  = 640.37, F_B  = 27.56, p_B  < 0.001
     SS_AB (Interaction)    = 118.94, df_AB = 1, MS_AB = 118.94, F_AB =  5.11, p_AB = 0.026
     SS_within              = 1087.42, df_within = 96, MS_within = 11.33
     SS_total               = 1941.94, df_total  = 99

   Effect sizes (eta-squared style):
     eta^2_Training    = 0.049
     eta^2_Context     = 0.330
     eta^2_Interaction = 0.061

   Simple main effects (because interaction is significant):
     Training within low_stress:  t(48) = 0.82,  p = 0.416
     Training within high_stress: t(48) = 2.78,  p = 0.008

   Interaction plot saved to: outputs/track_b/ch13_training_by_context.png

Focus on:

* **Cell means and lines** in the interaction plot:
  are the Training lines parallel, spreading, or crossing?
* **Main effects**: Are there overall differences between Training
  conditions, or between Contexts, when averaging across the other factor?
* **Interaction**: Does the Training effect depend on Context? Are the
  differences between control and cbt larger in one context than the other?
* **Simple main effects**: If the interaction is significant, do follow-up
  tests show that Training matters only under high stress, or in both contexts?

Your Turn: Practice Scenarios
-----------------------------

As in earlier chapters, you can experiment by editing parameters in
``psych_ch13_two_way_anova.py``. Some ideas:

* **Create a pure main-effect scenario**

  Make CBT slightly better than control in **both** contexts by the same
  amount. What happens to the Training main effect and the interaction?

* **Create a spreading interaction**

  Make Training have little effect under low_stress but a strong effect under
  high_stress. How does this change the interaction plot and the *F* for the
  interaction?

* **Create a crossover interaction**

  Make control slightly better under low_stress but cbt clearly better under
  high_stress. Can the overall Training main effect be small or even
  misleading, while the interaction is large?

* **Change the within-cell variability**

  Increase the standard deviation of the simulated scores. Watch how
  :math:`MS_{\text{Within}}` grows and the *F*-statistics shrink even if the
  cell means stay the same.

* **(Do not break the balance!)**

  You can change the **shared** ``n_per_cell`` parameter (for example, 20
  instead of 25), but resist the temptation to give different cells different
  sample sizes. Our manual formulas and PyStatsV1 helpers assume equal sample
  sizes in each cell. For unbalanced designs, you will need more advanced
  tools (for example, Type III sums of squares in specialized software).

Summary
-------

In this chapter you learned:

* why psychologists often use **factorial designs** with more than one
  independent variable,
* how to interpret **main effects** as overall differences for each factor,
* how to interpret **interactions** as "it depends" or **difference of
  differences** effects, often revealed by non-parallel lines in an
  interaction plot,
* why simple main effects are useful follow-ups when interactions are present,
* how the two-way ANOVA partitions variance into main effects, interaction,
  and error for a balanced design,
* how to implement a two-way ANOVA and basic simple main-effects analyses
  using PyStatsV1.

In the bigger arc:

* Chapter 10 introduced independent-samples *t*-tests for two groups.
* Chapter 11 introduced paired-samples *t*-tests for within-subjects designs.
* Chapter 12 extended the between-subjects logic to **three or more groups**
  using one-way ANOVA.
* Chapter 13 generalizes the ANOVA framework to **factorial designs**, where
  more than one independent variable is manipulated at the same time.

Factorial designs are powerful tools. They let you ask richer questions about
how psychological processes behave across different contexts, and they prepare
you for even more complex models (mixed designs, ANCOVA, and beyond) in later
chapters.

For the full Python implementation, see
``scripts/psych_ch13_two_way_anova.py`` in the PyStatsV1 GitHub repository.
