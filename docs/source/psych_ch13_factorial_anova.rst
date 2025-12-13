Track C – Chapter 13: Factorial Designs (Two-Way ANOVA)
=======================================================

Scenario: Study Strategy x Test Environment
-------------------------------------------

In this lab, you will work with data from a **2x2 between-subjects factorial design**.

- Factor A: **Study Strategy**

  - Flashcards
  - Concept Mapping

- Factor B: **Test Environment**

  - Quiet room
  - Distracting (background chatter + music)

- Dependent Variable: **Test score** (0–100) on a standardized memory test.

The population is set up so that:

- Students using **Concept Mapping** score higher overall than those using **Flashcards**.
- Students tested in a **Quiet** room score higher overall than those in a **Distracting**
  environment.
- There is an **interaction**: Concept Mapping benefits more from a Quiet environment
  than Flashcards do.

Learning goals
--------------

By the end of this lab, you should be able to:

- Explain what a **main effect** and an **interaction** mean in a 2x2 design.
- Draw and interpret **interaction plots**.
- Run a basic **two-way ANOVA** in Python.
- Connect the ANOVA table back to the design (Which effect is which?).

Generating the data with PyStatsV1
----------------------------------

If you have PyStatsV1 installed from PyPI, you can generate the Chapter 13 data
without cloning the GitHub repository.

In a terminal:

.. code-block:: bash

   python -m venv pystatsv1-env
   # On Windows (Git Bash):
   source pystatsv1-env/Scripts/activate
   # On macOS/Linux:
   # source pystatsv1-env/bin/activate

   pip install pystatsv1

Now run the Chapter 13 simulator:

.. code-block:: bash

   python -m scripts.psych_ch13_factorial_anova \
       --n-per-cell 30 \
       --seed 123 \
       --outdir data/psych_ch13

(If you installed PyStatsV1 globally rather than working from the GitHub clone,
make sure you run the script from a folder where the Python interpreter can find
the ``scripts`` module in your environment.)

This will create two CSV files:

- ``data/psych_ch13/psych_ch13_factorial_data.csv`` – one row per participant
- ``data/psych_ch13/psych_ch13_factorial_summary.csv`` – cell means and standard deviations

Suggested analysis steps
------------------------

1. **Load the data** into a pandas DataFrame.
2. **Inspect cell means** using ``groupby`` (this should match the summary CSV).
3. **Plot the interaction**:

   - X-axis: Study Strategy (Flashcards vs Concept Mapping)
   - Lines: Environment (Quiet vs Distracting)
   - Y-axis: Mean test score

4. **Fit a two-way ANOVA model** using your preferred library (for example,
   :mod:`statsmodels`) and identify:

   - Main effect of Study Strategy
   - Main effect of Environment
   - Study Strategy × Environment interaction

5. **Write a short APA-style result paragraph** that describes the pattern of
   means, the ANOVA results, and the interaction.

Connection to Chapter 13 concepts
---------------------------------

- The **main effects** tell you whether one factor matters *on average*,
  collapsing across the other factor.
- The **interaction** tests the "it depends" question:
  Does the effect of Study Strategy depend on the Test Environment?

This lab is designed to reinforce:

- 13.2 Notation and design structure (2x2 factorial designs)
- 13.3 Main Effects
- 13.4 Interactions (spreading vs crossover)
- 13.5 Simple Main Effects (follow-up questions you might ask after
  finding an interaction)
