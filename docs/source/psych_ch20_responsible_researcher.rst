Chapter 20 – The Responsible Researcher (Conclusion)
====================================================

Where this chapter fits in the story
------------------------------------

Chapters 1–19 walked you through the **tools** of quantitative psychology:

* From z-scores, :math:`t` tests, and ANOVA,
* Through correlation, regression, and mixed-model designs,
* All the way to ANCOVA and non-parametric alternatives.

Along the way, the PyStatsV1 labs treated each analysis as **production
software**:

* Deterministic simulators with fixed random seeds.
* Re-usable helper functions and command-line entry points.
* Tests that automatically verify key properties of the results.

This final chapter zooms out from individual techniques to the broader
question:

.. epigraph::

   *What does it mean to do responsible, cumulative, and reproducible
   research?*

We will highlight three pillars:

1. **Power analysis** – planning sample sizes before you collect data.
2. **Meta-analysis** – combining evidence across studies.
3. **Clear communication** – writing honest, transparent summaries of
   what your data can (and cannot) support.

The chapter closes with a **final PyStatsV1 project** that guides you
from raw data to an APA-style report, using the tools you developed in
earlier labs.

20.1 Power analysis: Planning samples before you collect data
-------------------------------------------------------------

Why power matters
~~~~~~~~~~~~~~~~~

Every statistical test juggles four quantities:

* **Effect size** (how big the effect really is).
* **Sample size :math:`N`** (how much data you collect).
* **Significance level :math:`\alpha`** (your Type I error rate).
* **Power** (the probability of detecting the effect if it is real).

Once you fix any three of these, the fourth is determined. Power
analysis is about *solving that equation on purpose* instead of hoping
that “:math:`N = 30` per group” will magically be enough.

A study with very low power is problematic because:

* True effects are often *missed* (high Type II error).
* Effects that *are* detected tend to be over-estimated (“winner’s
  curse”).
* Resources (time, money, participant goodwill) can be wasted on studies
  that were never likely to succeed.

A priori vs. post hoc power
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **A priori power analysis** happens *before* you collect data.

  - You specify a meaningful effect size (e.g., :math:`d = 0.5` for a
    medium standardized mean difference).
  - Choose :math:`\alpha` (often 0.05) and desired power (often 0.80).
  - Solve for :math:`N` per group.

* **Post hoc (“observed”) power** is calculated *after* the fact, using
  the effect size observed in your sample.

  - This value is mostly a complicated re-expression of :math:`p` and
    is rarely informative.
  - In PyStatsV1 we emphasize **a priori** planning instead.

In the Chapter 20 lab script, we use :mod:`pingouin` to compute sample
sizes for simple scenarios (e.g., independent-samples :math:`t` tests),
and we write the results to a small **power grid** for inspection.

Practical considerations
~~~~~~~~~~~~~~~~~~~~~~~~

Some practical rules-of-thumb you will see in the wild:

* If you expect a *large* effect (:math:`d \approx 0.8`), smaller
  samples might be OK (but replication still matters).
* If you expect a *small* effect (:math:`d \approx 0.2`), you may need
  hundreds of participants per group to achieve good power.
* In within-subjects designs, power is boosted by lower error variance
  (participants act as their own control).

Power analysis is ultimately **ethical** as well as technical. You are
deciding how many people to involve, how much time to spend, and how
likely your study is to make a cumulative contribution.

20.2 Meta-analysis: The study of studies
----------------------------------------

Individual experiments are noisy. Even well-planned studies will
occasionally miss true effects or overstate them. **Meta-analysis** is a
set of tools for combining evidence across multiple studies.

At a high level:

* Each study contributes an **effect size** (e.g., Cohen’s :math:`d`,
  correlation :math:`r`) and an **estimate of its precision**
  (e.g., a standard error or variance).
* More precise studies (usually those with larger :math:`N`) receive
  **more weight**.
* A combined or **pooled effect size** is computed, along with
  confidence intervals, measures of heterogeneity, and often tests for
  moderation (do effects differ by method, sample, or context?).

Fixed-effect vs. random-effects models
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* In a **fixed-effect** meta-analysis, we assume all studies are
  estimating the *same* underlying true effect.

  - Differences among studies are attributed only to sampling error.
  - The pooled estimate answers the question: “What is the best
    estimate of the common effect size in this set of studies?”

* In a **random-effects** meta-analysis, we allow the true effect to
  *vary* from study to study (e.g., different labs, populations, or
  protocols).

  - We estimate both the *typical* effect and the *heterogeneity* among
    effects.
  - The pooled estimate answers: “What is the average effect across a
    distribution of study contexts?”

In Chapter 20, we keep things simple with a **fixed-effect illustration**:

* We simulate several “published” effect sizes with different sample
  sizes.
* We compute a weighted mean effect size and its confidence interval.
* We calculate a basic heterogeneity statistic (:math:`Q` and :math:`I^2`)
  to flag when the effects are more variable than chance alone would
  predict.

How this connects back to earlier chapters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Earlier chapters focused on **within-study** inference (what can we
conclude from *this* experiment?). Meta-analysis steps back and asks:

* How consistent are the effects across **many** experiments?
* When results disagree, is it due to chance, small samples, or genuine
  differences in context or methods?
* How can we make decisions (in policy, clinical practice, or
  scientific theory) that respect the *whole* body of evidence?

20.3 Communicating results responsibly
--------------------------------------

Statistical tools are only as useful as the **stories we tell** with
them. Responsible communication means:

* Being **transparent** about your methods (design, sampling, analytic
  choices).
* Reporting **effect sizes** and **confidence intervals**, not just
  :math:`p` values.
* Discussing **limitations** and **alternative explanations**.
* Being honest about the **uncertainty** that remains.

Writing the Discussion section
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A good Discussion section typically:

1. **Restates the research questions** in plain language.

   - What did we want to know?
   - How does this connect to theory or prior research?

2. **Summarizes the key findings** without overstating them.

   - Focus on patterns of results, not just individual :math:`p` values.
   - Tie back to effect sizes and confidence intervals.

3. **Integrates with prior work**.

   - Do your results replicate or challenge previous findings?
   - How might they fit into a broader meta-analytic picture?

4. **Acknowledges limitations**.

   - Sample characteristics (e.g., only undergraduates from one
     university).
   - Measurement issues (e.g., self-report scales, ceiling effects).
   - Design constraints (e.g., no true random assignment).

5. **Outlines future directions**.

   - What follow-up studies could clarify the story?
   - How might improved design, larger samples, or different populations
     alter the conclusions?

The aim is not to **sell** your results, but to **situate** them – as
one piece of a collaborative, cumulative effort.

20.4 PyStatsV1 Lab: A final project from raw data to APA report
---------------------------------------------------------------

The last PyStatsV1 lab is different from earlier chapters. Instead of a
single, tightly scripted analysis, you will:

1. Choose a **research question**.
2. Select or import a **dataset**.
3. Design an analysis pipeline using the tools you have already
   implemented.
4. Generate a short **APA-style report** with transparent, reproducible
   code.

The Chapter 20 lab script provides a lightweight scaffold for this
process.

What the Chapter 20 lab script does
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The module :mod:`scripts.psych_ch20_responsible_researcher` includes
three main components:

1. **Power planning helper**

   * Uses :func:`pingouin.power_ttest` to compute required
     per-group sample sizes for different effect sizes and power levels.
   * Writes a small CSV grid,
     :file:`outputs/track_b/ch20_power_grid.csv`, that you can inspect
     or modify as you plan your own study.

2. **Toy meta-analysis simulator**

   * Simulates several “studies” with varying sample sizes and effect
     sizes.
   * Computes a **fixed-effect pooled effect**, confidence interval, and
     basic heterogeneity statistics :math:`Q` and :math:`I^2`.
   * Saves both the per-study table and a one-row summary to:

     - :file:`outputs/track_b/ch20_meta_studies.csv`
     - :file:`outputs/track_b/ch20_meta_summary.csv`

   This is **not** meant to replace real meta-analysis software, but to
   demystify the core ideas using familiar PyStatsV1 tools.

3. **Final project report template**

   * Creates a Markdown template at
     :file:`outputs/track_b/ch20_final_project_template.md`.
   * The template contains section headings and bullet prompts for:

     - Introduction & research questions
     - Methods (design, participants, measures, procedure)
     - Results (with placeholders for tables and figures generated by
       your PyStatsV1 scripts)
     - Discussion (including limitations and future directions)
     - Reproducibility notes (Git commit hash, random seeds, and CLI
       commands used)

   You can open this file in any text editor or import it into a
   reference manager / writing tool.

Suggested project workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~

Here is a possible end-to-end workflow for your final project:

1. **Pick a question**

   * Example: “Does a brief mindfulness exercise reduce stress scores
     relative to a control condition?”
   * Example: “Is there an association between sleep quality and exam
     performance?”

2. **Choose a dataset**

   * Start with one of the PyStatsV1 synthetic datasets (e.g., the
     sleep study or exam performance data), or
   * Import a small real dataset of your own – but keep it simple
     enough to analyze reproducibly in a single notebook or script.

3. **Plan your analysis**

   * Identify the appropriate model (t-test, ANOVA, mixed-model,
     regression, non-parametric alternative, etc.).
   * Use the power helper in Chapter 20 to think about how many
     participants would be needed to replicate or extend your findings.

4. **Run the analysis with PyStatsV1 tools**

   * Reuse simulation and analysis helpers from earlier chapters.
   * Save any intermediate tables or figures in the consistent
     :mod:`data` and :mod:`outputs` directories.

5. **Write the report using the template**

   * Copy :file:`ch20_final_project_template.md` to a new location
     (or new filename) and gradually fill in each section.
   * Whenever you report a result, note which script or function
     produced it.

6. **Record reproducibility details**

   * Save your final notebook or script under version control.
   * Record the Git commit hash and any command-line calls (e.g.,
     ``make psych-ch16``) that reproduce your figures and tables.
   * Share both the **code** and **narrative** with collaborators or
     instructors.

Running the Chapter 20 lab
--------------------------

To run the Chapter 20 lab script from the project root:

.. code-block:: bash

   make psych-ch20

This target runs:

.. code-block:: bash

   python -m scripts.psych_ch20_responsible_researcher

To run only the tests for this chapter:

.. code-block:: bash

   make test-psych-ch20

which wraps:

.. code-block:: bash

   pytest tests/test_psych_ch20_responsible_researcher.py

Conceptual summary
------------------

* Responsible research begins **before** data collection with thoughtful
  design and power analysis.
* Meta-analysis helps synthesize evidence across studies, revealing
  both typical effects and meaningful differences across contexts.
* Clear, honest communication – especially around uncertainty and
  limitations – is as important as any statistical computation.
* The PyStatsV1 ecosystem encourages you to treat your analyses like
  **production software**:

  - Deterministic, version-controlled, and reproducible.
  - Easy to rerun, extend, and audit.
  - Ready to support cumulative, collaborative science.

As you move on to more advanced courses or independent research, you can
treat this mini-book (and its code) as a **launch pad**. The goal is not
to memorize every formula, but to internalize a way of working:

.. epigraph::

   *Don’t just calculate your results — engineer them. We treat statistical analysis like production software. — PyStatsV1 Motto*

