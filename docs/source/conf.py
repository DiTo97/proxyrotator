import os
import sys


sys.path.insert(0, os.path.abspath("../.."))


# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "saferequests"
author = "Federico Minutoli"
release = "0.1.0"

# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "sphinx_autodoc_typehints"]

templates_path = ["_templates"]
exclude_patterns = []

# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]

master_doc = "index"
