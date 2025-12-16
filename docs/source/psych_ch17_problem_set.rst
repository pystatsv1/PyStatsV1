Track C — Chapter 17 Problem Set (Mixed-Model Designs)
======================================================

This problem set practices the core ideas of **mixed designs**:

- **Between-subjects factor:** ``group`` (Control vs Treatment)
- **Within-subjects factor:** ``time`` (T1, T2, T3)
- **DV:** ``score``

You will interpret:

1. Main effect of **time**
2. Main effect of **group**
3. **Interaction** (group × time)

Run the worked solutions
------------------------

.. code-block:: bash

   make psych-ch17-problems

Run only the tests
------------------

.. code-block:: bash

   make test-psych-ch17-problems

Files and outputs
-----------------

The solution script writes:

- Synthetic datasets: ``data/synthetic/``
- Summaries + plots: ``outputs/track_c/``

Exercises
---------

Exercise 1 — Strong interaction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Control stays flat across time; Treatment improves over time.

Questions:

- Which term (time / group / interaction) is most important here?
- What would you write in an APA-style sentence?

Exercise 2 — Time only
^^^^^^^^^^^^^^^^^^^^^^

Both groups improve similarly over time.

Questions:

- Is there a main effect of time?
- Is there a group effect?
- Is the interaction meaningful?

Exercise 3 — Group only (parallel lines)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Treatment is higher overall; the difference is stable across time.

Questions:

- Is group significant?
- Why is a *non-significant interaction* important here?
