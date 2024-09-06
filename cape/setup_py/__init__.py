#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Standard library
import os
import sys


# Python version infor
PY_MAJOR_VERSION = sys.version_info.major
PY_MINOR_VERSION = sys.version_info.minor

# This folder
THIS_DIR = os.path.dirname(__file__)
# File with description
DESCRIPTION_FILE = os.path.join(THIS_DIR, "long_description.rst")
# Parse long description
LONG_DESCRIPTION = open(DESCRIPTION_FILE).read()

# Compile and link
SETUP_SETTINGS = dict(
    name="cape",
    version="1.2.1",
    description="CAPE computational aerosciences package",
    long_description=LONG_DESCRIPTION,
    url="https://www.github.com/nasa/cape",
    author="Derek Dalle",
    author_email="derek.j.dalle@nasa.gov",
    license="NASA Open Source Agreement Version 1.3",
    packages=[
        "cape",
        "cape.attdb",
        "cape.dkit.ftypes",
        "cape.cfdx",
        "cape.cfdx.options",
        "cape.filecntl",
        "cape.nmlfile",
        "cape.optdict",
        "cape.pycart",
        "cape.pycart.options",
        "cape.pyfun",
        "cape.pyfun.options",
        "cape.pykes",
        "cape.pykes.options",
        "cape.pyover",
        "cape.pyover.options",
        "cape.tnakit",
        "cape.tnakit.plot_mpl",
        "cape.tnakit.textutils"
    ],
    install_requires=[
        "defusedxml",
        "numpy>=1.4.1",
        "matplotlib>=2",
        "scipy",
        "vendorize",
        "xlrd3",
        "xlsxwriter"
    ],
    package_data={
        "cape": [
            "templates/paraview/*",
            "templates/tecplot/*"
        ],
        "cape.cfdx": ["templates/*"],
        "cape.cfdx.options": ["*.json"],
        "cape.pycart": ["templates/*"],
        "cape.pycart.options": ["*.json"],
        "cape.pyfun": ["templates/*"],
        "cape.pyfun.options": ["*.json"],
        "cape.pyover": ["templates/*"],
        "cape.pyover.options": ["*.json"],
    },
    scripts=[
        "bin/run_flowCart.py",
        "bin/run_fun3d.py",
        "bin/run_kestrel.py",
        "bin/run_overflow.py"
    ],
    entry_points={
        "console_scripts": [
            "pycart=cape.pycart.cli:main",
            "pyfun=cape.pyfun.cli:main",
            "pykes=cape.pykes.cli:main",
            "pyover=cape.pyover.cli:main",
            "dkit=cape.dkit.cli:main",
            "dkit-quickstart=cape.dkit.quickstart:main",
            "dkit-vendorize=cape.dkit.vendorutils:main",
            "dkit-writedb=cape.dkit.writedb:main",
            "cape-writell=cape.writell:main",
            "cape-step2crv=cape.tricli:main_step2crv",
            "cape-steptri2crv=cape.tricli:main_steptri2crv",
            "cape-uh3d2tri=cape.tricli:main_uh3d2tri",
            "cape-tri2uh3d=cape.tricli:main_tri2uh3d",
            "cape-tri2plt=cape.tricli:main_tri2plt",
            "cape-tri2surf=cape.tricli:main_tri2surf",
            "pyfun-plt2triq=cape.pyfun.tricli:main_plt2triq",
        ],
    })
