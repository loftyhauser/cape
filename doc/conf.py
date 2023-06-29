# -*- coding: utf-8 -*-
#
# pyCart documentation build configuration file, created by
# sphinx-quickstart on Wed Jun 11 08:36:23 2014.
#
# This file is execfile()d with the current directory set to its
# containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import sys
import os
import re
import datetime

# Current date
now = datetime.datetime.now()

# Add the path to the pyCart modules (duh)
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.abspath('../bin'))
sys.path.append(os.path.abspath('.'))

# Import and run auto options documentation
import optdoc
optdoc.make_rsts()

# Save the current time
now = datetime.datetime.now()

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#sys.path.insert(0, os.path.abspath('.'))

# Added to clean up autodoc toctrees
toc_object_entries = False

# -- General configuration ------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.mathjax',
]

# Main title
title = "Manual for CAPE version 1.1"

# Switches
latex_opts = {
    "nasa@tm": False,
    "nasa@tm@sti": False,
    "nasa@tm@interior": False,
    "tna@titlepage": False,
    "tna@memo": False,
    "tna@report": False,
}

# Parameters for the TM
NC = {
    "title": title.replace("&", "\\&"),
    "year": now.year,
    "number": "XXXXXX",
    "month": now.strftime("%m"),
    "monthlong": now.strftime("%B"),
    "type": "TM",
    "typelong": "Technical Memorandum",
    "datescovered": "",
    "grantnumber": "",
    "contractnumber": "",
    "programelementnumber": "",
    "projectnumber": "",
    "tasknumber": "",
    "lnumber": "",
    "workunitnumber": "",
    "nasacenter": "NASA Ames Research Center\\par Moffett Field, CA 94035",
    "category": 1,
    "pages": 1,
    "supplenotes": "",
    "distribution": "Unclassified-Unlimited"
}
# Author information
NC["author"] = (
    "Dalle, Derek J.")
NC["authoraffiliation"] = (
    "Derek J.~Dalle\\\\[-2pt]\n" +
    "Science \\& Technology Corp., Moffett Field, California\\\\[6pt]\n")
# Extended title/abstract
NC["subtitle"] = (
    "A CFD Preprocessing, Run Control, and Postprocessing Assistant for " +
    "Cart3D, FUN3D, and OVERFLOW")
NC["abstract"] = (
    "This manual describes the installation and execution of CAPE " +
    "version 1.1.  The software is a suite of wrappers for computational " +
    "fluid dynamics tools including Cart3D, FUN3D, and OVERFLOW.  At its " +
    "core, CAPE is an attempt to provide a common user interface to the " +
    "three flow solvers.  It also includes many tools for post-processing " +
    "computational fluid dynamics results including data collection, " +
    "analysis, plotting, and database management.")
NC["subjectterms"] = (
    "Computational fluid dynamics; " +
    "Cart3D; OVERFLOW; FUN3D")

# Parameters for internal memo
TNA = {
    "year": now.year,
    "number": "00",
    "month": now.strftime("%m"),
    "day": now.strftime("%d"),
    "version": "Version 1",
    "center": "Ames Research Center",
    "branch": "Computational Aerosciences Branch (TNA)",
    "city": "Moffett Field, CA  94035",
    "author": "Ames SLS CFD Team",
    "shortrestriction": ""
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = 'index'

# Please don't go around testing every code definition
doctest_test_doctest_blocks = ''

# ---- DEFAULTS ----------------------------------------------
# Default codes
TNAdef = {
    "year": now.year,
    "number": "00",
    "month": now.strftime("%m"),
    "day": now.strftime("%d"),
    "monthlong": now.strftime("%B"),
    "version": "Version 1",
    "center": "Ames Research Center",
    "branch": "Computational Aerosciences Branch (TNA)",
    "author": "Derek J.~Dalle",
    "city": "Moffett Field, CA  94035",
    "shortrestriction": "",
    "restriction": "",
    "prefix": "TNAS",
    "code": "TNA/S",
    "title": title.replace("&", "\\&"),
    "logo": "NASA_logo.pdf",
}
TNAdef["dayshort"] = "%s" % int(TNA.get("day", TNAdef["day"]))
# Apply defaults
for key in TNAdef:
    TNA.setdefault(key, TNAdef[key])


# Parameters for the TM
NCdef = {
    "title": title,
    "year": now.year,
    "number": "XXXXXX",
    "month": now.strftime("%m"),
    "monthlong": now.strftime("%B"),
    "type": "TM",
    "typelong": "Technical Memorandum",
    "datescovered": "",
    "grantnumber": "",
    "contractnumber": "",
    "programelementnumber": "",
    "projectnumber": "",
    "tasknumber": "",
    "lnumber": "",
    "workunitnumber": "",
    "nasacenter": "%s\\par %s" % (TNA["center"], TNA["city"]),
    "category": 1,
    "pages": 1,
    "supplenotes": "",
    "author": TNA["author"],
    "subtitle": "",
    "abstract": "",
    "restriction": "",
    "distribution": "Unclassified-Unlimited"
}
# Author information
NCdef["authoraffiliation"] = (
    "Derek J.~Dalle, Henry C.~Lee, Jamie G.~Meeroff\\\\[-2pt]\n" +
    "Science \\& Technology Corp., Moffett Field, California\\\\[12pt]\n" +
    "Stuart E.~Rogers\\\\[-2pt]\n" +
    "NASA Ames Research Center, Moffett Field, California")
# Extended title/abstract
NCdef["subjectterms"] = (
    "Space Launch System; Computational fluid dynamics; " +
    "Cart3D; OVERFLOW; FUN3D")
# Apply defaults
for key in NCdef:
    NC.setdefault(key, NCdef[key])

# Memo title
memo = '%s-%4i-%02i' % (TNA["prefix"], int(TNA["year"]), int(TNA["number"])) 
# Memo type
if latex_opts.get("tna@memo"):
    # Memo (as in, not report)
    memotype = "howto"
else:
    # Report (chapters instead of sections)
    memotype = "manual"

# ------------------------------------------------------------

# Active figure numbering
numfig = True
numfig_secnum_depth = 1
numfig_format = {
    'figure': 'Figure %s',
    'table': 'Table %s',
    'code-block': 'Listing %s'
}

# General information about the project.
project = u'CAPE'
copyright = u'2014-2021, Derek J. Dalle'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
version = '1.1'
# The full version, including alpha/beta/rc tags.
release = '1.1prelim2'

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The reST default role (used for this markup: `text`) to use for all
# documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
#keep_warnings = False


# -- General config and abbrevs -------------------------------------------

# Global replacements to place in prolog
rst_prolog = u"""
.. |>| replace:: :menuselection:`-->`
.. |->| replace:: →
.. |check| replace:: ✓
"""


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinxdoc'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#html_theme_options = {
#    "stickysidebar": "false",
#    "sidebarbgcolor": "#000665",
#    "sidebarlinkcolor": "#a0c0ff",
#    "relbarbgcolor": "#000645",
#    "footerbgcolor": "#000665"
#}

# Add any paths that contain custom themes here, relative to this directory.
#html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = "CAPE %s" % release

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = "NASA_logo.png"

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = "NASA_logo_icon.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
#html_extra_path = []

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_domain_indices = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
#html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
#html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = None

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   'da', 'de', 'en', 'es', 'fi', 'fr', 'hu', 'it', 'ja'
#   'nl', 'no', 'pt', 'ro', 'ru', 'sv', 'tr'
#html_search_language = 'en'

# A dictionary with options for the search language support, empty by default.
# Now only 'ja' uses this config value
#html_search_options = {'type': 'default'}

# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
#html_search_scorer = 'scorer.js'

# Output file base name for HTML help builder.
htmlhelp_basename = 'capedoc'

# -- Options for LaTeX output ---------------------------------------------

# Initialize our preamble
preamble = "\\makeatletter\n"
# Loop through the switches
for key in latex_opts:
    # Initialize the variable
    preamble += "\\newif\\if@%s\n" % key
    # Get the value
    v = str(latex_opts[key]).lower()
    # Set it
    preamble += "\\@%s%s\n" % (key, v)
# Loop through the NC parameters
preamble += "\n"
for key in NC:
    preamble += "\\newcommand{\\NC@%s}{%s}\n" % (key, NC[key])
# Loop through the TNA parameters
for key in TNA:
    preamble += "\\newcommand{\\TNA@%s}{%s}\n" % (key, TNA[key])

# Append the TM style file as a raw preamble
preamble += open('nasatm.sty').read()

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    #'papersize': 'letterpaper',
    
    # The font size ('10pt', '11pt' or '12pt').
    #'pointsize': '10pt',
    
    # Additional stuff for the LaTeX preamble.
    'preamble': preamble,
    
    # Latex figure (float) alignment
    #'figure_align': 'htbp',
    
    # Word to use for relase
    'releasename': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (
        'index',
        'cape.tex', 
        NC["title"],
        TNA["author"],
        memotype
    ),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
latex_logo = TNA.get("logo", "NASA_logo.pdf")

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# If true, show page references after internal links.
#latex_show_pagerefs = False

# If true, show URL addresses after external links.
#latex_show_urls = False

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_domain_indices = True


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_title = title.replace(" ", "")
man_pages = [
    ('index', 'cape', u'CAPE Documentation',
     [u'Derek J. Dalle'], 1)
]

# If true, show URL addresses after external links.
#man_show_urls = False


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', 'cape', u'CAPE Documentation',
   u'Derek J. Dalle', 'cape', 'One line description of project.',
   'Miscellaneous'),
]

# Documents to append as an appendix to all manuals.
#texinfo_appendices = []

# If false, no module index is generated.
#texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
#texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
#texinfo_no_detailmenu = False
