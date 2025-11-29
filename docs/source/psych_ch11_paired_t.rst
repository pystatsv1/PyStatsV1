Chapter 11 – Within-Subjects Designs and the Paired-Samples *t*-Test
====================================================================

In Chapter 8, you learned the logic of hypothesis testing using a simulation-based
one-sample *t*-test.

In Chapter 9, you connected that simulation intuition to the analytic one-sample
*t*-test and 95% confidence intervals for a single mean.

In Chapter 10, you extended those ideas to comparing **two independent groups**
using the independent-samples *t*-test (pooled vs. Welch). That was a classic
**between-subjects** design: each person appeared in only one condition.

In this chapter, we move to **within-subjects** designs. Instead of asking
whether two different groups of people differ, we ask whether the **same people
change over time** or across conditions.

Our goals are to help you:

* understand when a paired-samples *t*-test is appropriate,
* see why within-subjects designs can be more statistically powerful,
* recognize design threats specific to repeated measures
  (practice, fatigue, carryover),
* understand basic counterbalancing strategies, and
* run and interpret a paired-samples *t*-test using PyStatsV1.

Design Logic: Repeated Measures and Matched-Subjects
----------------------------------------------------

Suppose a lab wants to know whether a short training module improves
performance on a problem-solving test. Each participant completes the test:

* once **before** the training (pre-test), and
* once **after** the training (post-test).

We record a continuous score (for example, number of problems solved). The key
design feature is:

    The same people produce both the pre and post scores.

This is a **within-subjects** (or **repeated-measures**) design. A closely
related idea is a **matched-subjects** design, where participants are paired on
important characteristics (for example, age, IQ, baseline performance) and each
member of the pair receives a different condition. Analytically, each pair is
treated like a "unit", similar to a person measured twice.

In both cases, the data naturally form **pairs**:

* (pre, post) for each participant, or
* (score in condition A, score in condition B) for each matched pair.

From Chapter 1’s perspective:

* **Construct validity**: Does the test measure the construct (skill, ability)
  we care about?
* **External validity**: Would the training effect generalize beyond this sample
  and this test?
* **Statistical validity**: Is the observed change statistically reliable?
  (This is where the *t*-test lives.)
* **Internal validity**: Are we justified in saying the **training** caused the
  change, or could some other factor (for example, practice, fatigue) explain
  the difference?

The paired-samples *t*-test is a tool for statistical validity. To protect
internal validity, we also need to think carefully about design issues unique
to repeated measures.

The Power of “Self-Control”: Reducing Individual Differences Error
------------------------------------------------------------------

Why bother with within-subjects designs?

In a between-subjects design (Chapter 10), people differ in many ways that have
nothing to do with the experiment: baseline ability, motivation, prior
knowledge, sleep, and so on. Those differences inflate the variability of
scores within each group, which shows up as **error variance** in the
denominator of the *t*-statistic.

In a within-subjects design, we focus on **difference scores** for each person:

.. math::

   D_i = X_{i,\text{post}} - X_{i,\text{pre}}.

If person :math:`i` is generally high-performing, they tend to be high at both
pre and post. When we subtract, that stable "true ability" component largely
cancels out. What is left in the difference is:

    Difference = Condition Effect + Residual Noise

By removing stable between-person differences, we:

* shrink the variability of the difference scores,
* shrink the standard error of the mean difference, and
* make it easier to detect a real effect (greater **power**).

This is sometimes called the **"self-control"** idea:

    Each participant serves as their own control condition.

The paired-samples *t*-test is the analytic tool that formalizes this idea.

Issues: Practice Effects, Fatigue, and Carryover
------------------------------------------------

Within-subjects designs are statistically powerful, but they have their own
**design risks**. Three big ones are:

* **Practice effects**

  Participants might improve simply because they have seen the test before.
  On the second attempt, they know the format, remember some items, or adopt
  better strategies. Improvement may reflect **familiarity with the test**, not
  the training.

* **Fatigue effects**

  If the tasks are long or demanding, participants can become tired, bored, or
  less attentive over time. Performance might deteriorate at Time 2 even if the
  training helped, simply because participants are exhausted.

* **Carryover effects**

  What happens in the first condition changes how people respond in later
  conditions. In drug studies, the effect of the first dose might still be
  active during the second. In cognitive tasks, strategies learned in one
  condition carry over to the next.

These problems are **not** solved by a different *t*-test formula. They are
**design problems**, not analysis problems.

The paired-samples *t*-test can tell you whether the average difference is
reliably different from zero. It cannot tell you *why* that difference exists.

This connects back to **internal validity**: if practice, fatigue, or carryover
are plausible alternative explanations, your ability to claim a causal effect
is weakened.

Counterbalancing: Controlling for Order Effects
-----------------------------------------------

One of the main tools psychologists use to deal with order-related threats is
**counterbalancing**: systematically varying the order of conditions across
participants so that order effects can be detected or averaged out.

Common strategies include:

* **Simple AB / BA counterbalancing**

  Two conditions, A and B.
  Half the participants receive A then B, the other half B then A.
  Practice or fatigue effects are spread across conditions rather than
  confounded with one specific condition.

* **Full counterbalancing**

  For three conditions A, B, C you could run all possible orders (ABC, ACB,
  BAC, BCA, CAB, CBA).
  This becomes impractical as the number of conditions grows (the number of
  orders grows factorially).

* **Latin square and related designs**

  For many conditions, a Latin square ensures each condition appears in each
  position equally often and follows each other condition equally often, without
  using all possible orders.

How does this apply to a simple pre–post training study?

* You **cannot** undo the training to swap the order (once trained, always
  trained).

* Instead, researchers often:

  - Use **alternate forms** of the test (Form A at pre, Form B at post) and
    counterbalance which form comes first.
  - Include a **control group** that completes the same pre/post testing but
    receives no training (or a placebo training).
  - Add **rest breaks** or shorter test batteries to reduce fatigue.

You will see these ideas again in mixed-model designs (Chapter 17), where
pre–post measurements are combined with separate groups (for example, Training
vs. Control).

The Paired-Samples *t*-Test Formula
-----------------------------------

Mathematically, the paired-samples *t*-test works on the **difference scores**:

* For each participant :math:`i`, compute

  .. math::

     D_i = X_{i,\text{post}} - X_{i,\text{pre}}.

* Let there be :math:`n` participants (so :math:`n` differences).

Define:

* Mean difference

  .. math::

     \bar{D} = \frac{1}{n}\sum_{i=1}^{n} D_i

* Standard deviation of differences

  .. math::

     s_D = \sqrt{\frac{1}{n - 1}\sum_{i=1}^{n}(D_i - \bar{D})^2}

* Standard error of the mean difference

  .. math::

     SE_{\bar{D}} = \frac{s_D}{\sqrt{n}}

The hypotheses are:

.. math::

   H_0 : \mu_D = 0 \quad\text{(no average change)}

.. math::

   H_1 : \mu_D \ne 0 \quad\text{(some average change)}

The paired-samples *t*-statistic is:

.. math::

   t = \frac{\bar{D} - \mu_{D,0}}{s_D / \sqrt{n}},

where :math:`\mu_{D,0}` is the null value for the mean difference (usually 0),
and the degrees of freedom are:

.. math::

   df = n - 1.

Under :math:`H_0`, if the difference scores are approximately Normal and
independent across participants (even though pre and post within a participant
are correlated), this *t*-statistic follows a *t* distribution with
:math:`n - 1` degrees of freedom.

Effect Size: Cohen’s :math:`d_z`
--------------------------------

Just like in independent samples, we need to report the **magnitude** of the
effect, not only whether it is statistically significant.

For paired samples, a common measure is **Cohen’s** :math:`d_z`:

.. math::

   d_z = \frac{\bar{D}}{s_D}

This expresses the mean difference in terms of standard deviation units of the
*difference scores*.

*Note:* There are other ways to calculate :math:`d` for paired samples (for
example, using the average standard deviation of pre and post scores), but
:math:`d_z` is the direct analogue to the *t*-statistic because it uses the
same standard deviation that appears in the denominator of the paired test.

Rough guidelines (Cohen, 1988):

* :math:`d \approx 0.2` – small effect
* :math:`d \approx 0.5` – medium effect
* :math:`d \approx 0.8` – large effect

Reporting example:

    “Participants’ scores improved significantly from pre to post,
    :math:`t(39) = 3.75`, :math:`p = .001`, :math:`d_z = 0.59`, indicating a
    medium-sized effect of the training.”

Confidence Interval for the Mean Difference
-------------------------------------------

A 95% confidence interval for the population mean difference :math:`\mu_D` is:

.. math::

   \bar{D} \pm t^* \cdot \frac{s_D}{\sqrt{n}},

where :math:`t^*` is the critical value from the *t* distribution with
:math:`df = n - 1` at :math:`\alpha = 0.05`.

Interpretation is parallel to Chapter 9:

    If we repeated the study many times, 95% of the resulting confidence
    intervals would contain the true mean difference :math:`\mu_D`.

If a 95% CI for :math:`\mu_D` **does not include 0**, a two-sided paired *t*-test
will reject :math:`H_0 : \mu_D = 0` at :math:`\alpha = 0.05`. If the CI
**does include 0**, the test will fail to reject :math:`H_0`.

What If We (Wrongly) Treated the Data as Independent?
-----------------------------------------------------

A common mistake is to ignore the pairing and run an independent-samples
*t*-test on the pre and post scores as if they came from two different groups.

If we do that:

* Each person’s pre and post scores are separated into different "groups".
* The analysis no longer uses the **within-person correlation**.
* Between-person variability (stable differences in ability) sits in the error
  term.
* The test usually has **less power** (smaller absolute :math:`t`, larger
  :math:`p`).

In the PyStatsV1 Chapter 11 code, we include a function that deliberately
performs this mis-specified independent *t*-test so you can see the difference
in practice.

Take-away: Using the wrong test wastes information and can make real effects
look non-significant.

PyStatsV1 Lab: A Paired *t*-Test for a Training Study
-----------------------------------------------------

In this lab, you will analyze a synthetic pre–post training study using the
paired-samples *t*-test.

You will:

* simulate a repeated-measures dataset with pre and post scores for each
  participant,
* compute:

  - mean pre score and mean post score,
  - difference scores :math:`D_i`,
  - mean difference :math:`\bar{D}`,
  - :math:`s_D`, standard error, *t*-statistic, *p*-value, and 95% CI,
  - Cohen’s :math:`d_z` as an effect size for the mean difference,

* compare the correct paired *t*-test to a mis-specified independent-samples
  *t*-test on the same data, to see the power advantage of using the right
  model.

All code for this lab lives in:

* ``scripts/psych_ch11_paired_t.py``

and the script can optionally write outputs to:

* ``data/synthetic/psych_ch11_paired_training.csv``

Running the Lab Script
----------------------

From the project root, you can run:

.. code-block:: bash

   python -m scripts.psych_ch11_paired_t

If your Makefile defines a convenience target, you can instead run:

.. code-block:: bash

   make psych-ch11

This will:

* simulate a pre–post training dataset (for example, 40 participants),
* compute the paired-samples *t*-test for the mean difference in scores,
* compute Cohen’s :math:`d_z` from the mean difference and :math:`s_D`,
* print:

  - sample size and degrees of freedom,
  - mean pre and post scores,
  - mean difference,
  - *t*-statistic, *p*-value, and a 95% CI for :math:`\mu_D`,
  - Cohen’s :math:`d_z` as an effect size,

* optionally save the dataset as a CSV file for further exploration.

Expected Console Output
-----------------------

Your exact numbers will vary if you change the seed or parameters, but with the
default settings, you will see something like:

.. code-block:: text

   Paired samples t-test for pre–post training study
   n = 40, df = 39
   Mean(pre)  = 72.23
   Mean(post) = 77.67
   Mean diff  = 5.44
   t(39) = 3.75, p = 0.0006
   95% CI for mean diff: [2.51, 8.37]
   Cohen's d_z = 0.59

Focus on:

* **Mean(pre) and Mean(post)**: Did scores increase, and by how much (in raw units)?
* **Mean diff**: The average post–pre difference :math:`\bar{D}`.
* **t-statistic**: How many standard errors the mean difference is from 0.
* **p-value**: Is this difference "rare" under :math:`H_0 : \mu_D = 0`?
* **95% CI**: A range of plausible values for the true mean change.
* **Cohen’s :math:`d_z`**: How large is the effect in standardized units of the
  difference scores?

Your Turn: Practice Scenarios
-----------------------------

As in previous chapters, you can experiment by changing the simulation
parameters in ``psych_ch11_paired_t.py``:

* **Change the mean change**

  Increase or decrease the assumed population mean difference.
  How does this affect :math:`\bar{D}`, :math:`t`, the *p*-value, and
  Cohen’s :math:`d_z`?

* **Change the variability of change**

  Increase ``sd_change`` to make individual change scores more variable.
  What happens to :math:`s_D`, the standard error, the width of the 95% CI,
  and :math:`d_z`?

* **Change the sample size :math:`n`**

  Increase the number of participants (for example, from 20 to 80).
  Observe how the standard error shrinks and the *t*-test becomes more
  sensitive to the same mean difference. Does :math:`d_z` change?

* **Compare paired vs. mis-specified independent tests**

  Use the helper function for the mis-specified independent-samples *t*-test
  (described in the code).
  Compare the *t*-statistics and *p*-values.
  Do you see that the paired test usually produces a larger absolute *t*
  (more power) while Cohen’s :math:`d_z` stays tied to the actual magnitude
  of within-person change?

* **Design reflection**

  Imagine realistic practice or fatigue effects for this training study.
  How might you redesign the study (alternate test forms, control group,
  rest breaks, counterbalancing) to protect internal validity?

Summary
-------

In this chapter you learned:

* when to use a paired-samples *t*-test: whenever your data come in **pairs**
  from the same (or tightly matched) units,
* how within-subjects designs reduce individual differences error and increase
  power by treating each participant as their own control,
* design threats specific to repeated measures: practice effects, fatigue, and
  carryover effects,
* how counterbalancing and related design strategies help control order
  effects,
* how to compute and interpret the paired-samples *t*-statistic, *p*-value,
  95% CI for a mean difference, and Cohen’s :math:`d_z` as an effect size,
  using PyStatsV1.

In the bigger arc:

* Chapter 8: NHST logic with a simulation-based one-sample *t*-test.
* Chapter 9: Analytic one-sample *t*-test and confidence intervals.
* Chapter 10: Independent-samples *t*-test for between-subjects designs.
* Chapter 11: Paired-samples *t*-test for within-subjects designs, with an
  appropriate effect size measure.

Together, these chapters give you a solid toolkit for simple experiments with
one independent variable, whether the design uses independent groups or repeated
measures. In later chapters, you will extend these ideas to more complex
designs and models (ANOVA, regression, mixed models), but the core logic will
remain the same.

Code listing
------------

For reference, the full implementation is included via Sphinx:

.. literalinclude:: ../scripts/psych_ch11_paired_t.py
   :language: python
   :linenos:
   :caption: ``scripts/psych_ch11_paired_t.py`` – simulator and paired *t*-test helpers
