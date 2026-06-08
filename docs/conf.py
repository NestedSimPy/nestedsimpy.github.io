from __future__ import annotations

project = "PyNestedSim"
author = "PyNestedSim contributors"
copyright = "2026, PyNestedSim contributors"

# Docs-only build: no autodoc / viewcode, so the implementation package is NOT
# required to build and is never imported or rendered. The API reference pages
# are hand-written (see docs/api/).
extensions = [
    "myst_parser",
    "sphinx.ext.intersphinx",
    "sphinx_design",
    "sphinx_copybutton",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

myst_enable_extensions = [
    "colon_fence",
    "deflist",
]

exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
]

templates_path = ["_templates"]
html_static_path = ["_static"]
html_theme = "furo"
html_title = "PyNestedSim"
html_css_files = ["custom.css"]
html_logo = "_static/pynestedsim-logo.svg"
html_favicon = "_static/pynestedsim-favicon.svg"
# TODO: point these at the new PUBLIC docs repository once it exists.
DOCS_REPO_URL = "https://github.com/happywhy0928/NestedSimPy_Web"
html_theme_options = {
    "navigation_with_keys": True,
    "source_repository": DOCS_REPO_URL + "/",
    "source_branch": "main",
    "source_directory": "docs/",
    "footer_icons": [
        {
            "name": "GitHub",
            "url": DOCS_REPO_URL,
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "simpy": ("https://simpy.readthedocs.io/en/latest/", None),
}
