.. _psych_ch2_ethics:

Psychological Science & Statistics – Chapter 2
==============================================

Ethics in Research: Why They Matter More Than Ever
--------------------------------------------------

Psychology studies people. That means psychology must protect people.

Every research method, every measurement, and every statistical test is
built on a foundation of *ethical responsibility*. Before we learn how
to analyze data, we need to understand why scientific ethics exist,
where they came from, and why modern research is designed the way it is.

This chapter has five goals:

* show why historical failures shape everything psychologists do today,
* introduce the Belmont Report and the principles used in all human research,
* explain the core elements of the APA ethics code,
* describe data‐specific ethics (p‐hacking, HARKing, replication crisis),
* introduce Open Science and how PyStatsV1 supports ethical transparency.


2.1 Historical failures: why rules exist
----------------------------------------

Modern research ethics were not invented in a classroom—they were built
after real harm occurred. Some landmark cases:

**• Tuskegee Syphilis Study (1932–1972)**  
Participants were *denied treatment* so researchers could “observe” the
progression of disease. The study continued for decades after penicillin
became the known cure.

**• Milgram Obedience Studies (1960s)**  
Participants believed they were delivering painful electric shocks.
Although no physical harm occurred, emotional distress was severe.

**• Stanford Prison Experiment (1971)**  
A simulated prison environment escalated quickly toward psychological
abuse. Oversight and controls were nearly absent.

**• Tearoom Trade Study (1970)**  
There was recorded identifiable information on participants engaging in
private sexual behavior without consent.

These cases illustrate the same theme:

**When research goals overshadow human well-being, ethics are violated.**

The entire system of modern IRB review and ethics training exists
because of these events.


2.2 The Belmont Report
----------------------

After Tuskegee became public in the 1970s, the U.S. formed the National
Commission for the Protection of Human Subjects. The result was the
**Belmont Report**, which introduced the three principles that still
govern research today.

**1. Respect for persons**  
Individuals must be treated as autonomous agents. People with diminished
autonomy (children, prisoners, cognitively impaired individuals) receive
special protection.

**2. Beneficence**  
Researchers must maximize benefits and minimize possible harms.
Participants should never be exposed to unnecessary risk.

**3. Justice**  
The burdens and benefits of research should be distributed fairly.
Vulnerable populations should not be targeted simply because they are
easy to recruit.

Every ethics review board—worldwide—uses these ideas.


2.3 APA Guidelines for psychologists
------------------------------------

The American Psychological Association provides detailed guidance for
researchers. Some core principles:

**• Informed consent**  
Participants must understand what the study involves, any risks, and
their rights—including the right to withdraw at any time.

**• Debriefing**  
If deception is used, it must be justified and followed by a complete,
honest explanation.

**• Protection from harm**  
Psychologists must prevent physical, emotional, and psychological
harm. Risks must be minimized and reasonable.

**• Confidentiality and privacy**  
Data must be stored securely, anonymized where possible, and reported in
a way that does not reveal identities.

**• Avoiding deception unless necessary**  
Deception must have strong justification and must not conceal risk or
prevent consent.

These rules are not obstacles—they are tools that protect participants
and strengthen research quality.


2.4 Data ethics: p-hacking, HARKing, and the replication crisis
---------------------------------------------------------------

Ethics does not stop at participant treatment. It also covers how
researchers *handle data and report results*.

**p-hacking**  
Trying many analyses and only reporting the ones that produce a
significant p-value.

**HARKing (“Hypothesizing After Results are Known”)**  
Presenting exploratory findings as if they were predicted in advance.

**Selective reporting**  
Only publishing studies that “work,” leaving null results hidden in file
drawers.

These practices contributed to psychology’s **replication crisis**,
where many high-profile results could not be reproduced by independent
researchers.

The most postive way to improve the state of research is to increase honesty, transparency, and reproducibility.


2.5 Open Science: pre-registration and data sharing
---------------------------------------------------

Open Science is a movement dedicated to making research:

* transparent,
* reproducible,
* shareable, and
* resistant to questionable research practices.

Key tools include:

**• Pre-registration**  
Researchers publicly record their hypotheses, methods, and planned
analyses *before* collecting data.

**• Registered reports**  
Journals review and accept a study’s methods *before* results exist.

**• Data and code sharing**  
When possible, datasets and analysis scripts are shared so others can
reproduce the work.

**• Reproducible workflows**  
Analyses are performed with code rather than unrecorded menu clicks.

This is where PyStatsV1 begins to shine.


2.6 A small reproducible example (PyStatsV1)
--------------------------------------------

Here is a gentle demonstration of how a reproducible workflow starts in
Python:

.. code-block:: python

    import pandas as pd

    # Replace this after the lab dataset is added
    data = pd.read_csv("data/study1_memory_scores.csv")

    print(data.head())
    print(data.describe())

This tiny script shows how:

* the entire analysis can be reproduced by running the same file,
* every transformation is visible and documented,
* code encourages transparency rather than hidden analytical decisions.


2.7 What you should take away
-----------------------------

By the end of this chapter, you should be able to:

* explain why ethical rules exist in human research,
* summarize the Belmont Report principles (Respect, Beneficence, Justice),
* describe core APA guidelines like informed consent and debriefing,
* identify questionable data practices (p-hacking, HARKing, selective reporting),
* understand the motivation behind the Open Science movement,
* see how PyStatsV1 supports transparent, reproducible workflows.

Before we analyze data, we need to protect the people who provide it.
Ethical research is not just a rule—it is a responsibility.
