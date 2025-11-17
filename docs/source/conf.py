import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath("../../"))

project = "PyStatsV1"
author = "Nicholas Elliott Karlson"
current_year = datetime.now().year
copyright = f"{current_year}, {author}"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

templates_path = ["_templates"]
exclude_patterns = []

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]