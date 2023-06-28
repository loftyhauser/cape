#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""
:mod:`cape.pyfun.cli_doc`: Create help message for ``pyfun``
=============================================================

This module formats the output of ``pyfun -h`` by filling in some slots
from :mod:`cape.cfdx.cli_doc`.

"""

# Standard library modules
import os
import sys

# CAPE modules
from ..cfdx import cli_doc


# (Automatic) name of executable category
NAME = __name__.split(".")[1]
# (Suggested) tool name
TITLE = NAME[:2] + NAME[2].upper() + NAME[3:]
# Main module name
MODNAME = ".".join(__name__.split(".")[:2])
# reST of main module
MODULE_RST = ":mod:`%s`" % MODNAME
# Name of solver
SOLVER = "FUN3D"

# Detect which executable was used
if len(sys.argv) > 0:
    # Get whatever launched this python session
    _argv0 = sys.argv[0]
    # Get the executable name
    _cmd0 = os.path.split(_argv0)[-1]
else:
    # Not sure how this would happen, but let's just call it "python"
    _cmd0 = "python"

# Detect if specific executable was called (e.g. 'pycart3')
if _cmd0.startswith(NAME):
    # Use the specific calling function
    CMD = _cmd0
else:
    # Just use the main category
    CMD = NAME

# Check for specified version
if CMD.endswith("2"):
    # Forced Python 2.7
    PYVERSION = "2.7 "
elif CMD.endswith("3"):
    # Forced Python 3 (.6+)
    PYVERSION = "3 "
else:
    # System
    PYVERSION = ""

# Docstring values for PYCART
_fmt = {
    "cmd": CMD,
    "name": NAME,
    "mod": MODULE_RST,
    "modname": MODNAME,
    "pyver": PYVERSION,
    "solver": SOLVER,
    "title": TITLE,
}


# Get template
_template = cli_doc.template

# Create docstring for PYCART; add version info
PYFUN_HELP = _template % _fmt + r"""

:Versions:
    * 2014-10-06 ``@ddalle``: Version 1.0 (of ``pycart``)
    * 2015-10-16 ``@ddalle``: Version 1.0
    * 2020-09-11 ``@ddalle``: Version 1.1
    * 2021-03-04 ``@ddalle``: Version 1.2; use "entry_points"
"""


# Print help if appropriate.
if __name__ == "__main__":
    print(PYFUN_HELP)
