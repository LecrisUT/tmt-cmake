# noqa: D100
from __future__ import annotations

project = "Tmt CMake"
author = "Cristian Le"

extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinx_togglebutton",
    "sphinx_copybutton",
    "sphinx_prompt",
    "breathe",
    "sphinx.ext.intersphinx",
    "sphinx_tippy",
    "sphinx.ext.todo",
]

templates_path = []
source_suffix = [".md"]
html_theme = "furo"

myst_enable_extensions = [
    "colon_fence",
    "substitution",
    "deflist",
]

intersphinx_mapping = {
    "tmt": ("https://tmt.readthedocs.io/en/stable", None),
}

tippy_rtd_urls = [
    # Only works with RTD hosted intersphinx
    "https://tmt.readthedocs.io/en/stable",
]

copybutton_exclude = ".linenos, .gp, .go"

todo_include_todos = True
