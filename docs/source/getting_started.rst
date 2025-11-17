Getting started
===============

Installation
------------

Clone the repository::

   git clone https://github.com/pystatsv1/PyStatsV1.git
   cd PyStatsV1

Create and activate a virtual environment.

macOS / Linux::

   python -m venv .venv && source .venv/bin/activate
   python -m pip install -U pip
   pip install -r requirements.txt

Windows (Git Bash or PowerShell)::

   python -m venv .venv; source .venv/Scripts/activate 2>/dev/null || .venv\Scripts\Activate.ps1
   python -m pip install -U pip
   pip install -r requirements.txt

Running checks
--------------

From the project root::

   make lint    # ruff
   make test    # pytest

Running chapters
----------------

Examples::

   # Chapter 1 — Introduction
   python -m scripts.ch01_introduction

   # Chapter 13 — Within-subjects & Mixed Models
   make ch13-ci
   make ch13

   # Chapter 14 — Tutoring A/B Test
   make ch14-ci
   make ch14

   # Chapter 15 — Reliability
   make ch15-ci
   make ch15

For a complete list of chapters and their commands, see :doc:`chapters`.