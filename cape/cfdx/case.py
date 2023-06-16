r"""
:mod:`cape.cfdx.case`: Case Control Module
==========================================
This module contains templates for interacting with and executing
individual cases. Since this is one of the most highly customized
modules of the CAPE system, there are few functions here, and the
functions that are present are mostly templates.

In general, the :mod:`case` module is used for actually running the CFD
solver (and any additional binaries that may be required as part of the
run process), and it contains other capabilities for renaming files and
determining the settings for a particular case. CAPE saves many settings
for the CFD solver and archiving in a file called ``case.json` within
each case folder, which allows for the settings of one case to diverge
from the other cases in the same run matrix.

Actual functionality is left to individual modules listed below.

    * :mod:`cape.pycart.case`
    * :mod:`cape.pyfun.case`
    * :mod:`cape.pyover.case`
"""

# Standard library modules
import functools
import glob
import json
import os
import sys
from datetime import datetime

# System-dependent standard library
if os.name == "nt":
    resource = None
else:
    import resource

# Local imports
from . import queue
from . import bin
from .. import argread
from .. import text as textutils
from .options import RunControlOpts
from ..tri import Tri


# Constants:
# Name of file that marks a case as currently running
RUNNING_FILE = "RUNNING"
# Name of file marking a case as in a failure status
FAIL_FILE = "FAIL"
# Case settings
RC_FILE = "case.json"
# Run matrix conditions
CONDITIONS_FILE = "conditions.json"
# PBS/Slurm job ID file
JOB_ID_FILE = "jobID.dat"

# Return codes
IERR_OK = 0
IERR_NANS = 32
IERR_RUN_PHASE = 128


# Help message for CLI
HELP_RUN_CFDX = r"""
Run solver CFD{X} for one case

This script determines the appropriate phase to run for an individual
case (e.g. if a restart is appropriate, etc.), sets that case up, and
runs it.

:Call:

    .. code-block:: console

        $ python -m cape.cfdx run [OPTIONS]

:Options:

    -h, --help
        Display this help message and quit
"""


# Decorator for moving directories
def run_rootdir(func):
    r"""Decorator to run a function within a specified folder

    :Call:
        >>> func = run_rootdir(func)
    :Wrapper Signature:
        >>> v = runner.func(*a, **kw)
    :Inputs:
        *func*: :class:`func`
            Name of function
        *runner*: :class:`CaseRunner`
            Controller to run one case of solver
        *a*: :class:`tuple`
            Positional args to :func:`cntl.func`
        *kw*: :class:`dict`
            Keyword args to :func:`cntl.func`
    :Versions:
        * 2020-02-25 ``@ddalle``: v1.1 (:mod:`cape.cntl`)
        * 2023-06-16 ``@ddalle``: v1.0
    """
    # Declare wrapper function to change directory
    @functools.wraps(func)
    def wrapper_func(self, *args, **kwargs):
        # Recall current directory
        fpwd = os.getcwd()
        # Go to specified directory
        os.chdir(self.RootDir)
        # Run the function with exception handling
        try:
            # Attempt to run the function
            v = func(self, *args, **kwargs)
        except Exception:
            # Raise the error
            raise
        except KeyboardInterrupt:
            # Raise the error
            raise
        finally:
            # Go back to original folder
            os.chdir(fpwd)
        # Return function values
        return v
    # Apply the wrapper
    return wrapper_func


# Case runner class
class CaseRunner(object):
    r"""Class to handle running of individual CAPE cases

    :Call:
        >>> runner = CaseRunner(fdir=None)
    :Inputs:
        *fdir*: {``None``} | :class:`str`
            Optional case folder (by default ``os.getcwd()``)
    :Outputs:
        *runner*: :class:`CaseRunner`
            Controller to run one case of solver
    """
   # --- Class attributes ---
    # Attributes
    __slots__ = (
        "j",
        "rc",
        "root_dir",
        "tic",
        "xi",
    )

    # Maximum number of starts
    _nstart_max = 100

    # Help message
    _help_msg = HELP_RUN_CFDX

    # Names
    _modname = "cfdx"
    _progname = "cfdx"
    _logprefix = "run"

    # Specific classes
    _rc_cls = RunControlOpts

   # --- __dunder__ ---
    def __init__(self, fdir=None):
        r"""Initialization method

        :Versions:
            * 2023-06-16 ``@ddalle``: v1.0
        """
        # Default root folder
        if fdir is None:
            # Use current directory (usual case)
            fdir = os.getcwd()
        elif not os.path.isabs(fdir):
            # Absolutize relative to PWD
            fdir = os.path.abspath(fdir)
        # Save root folder
        self.root_dir = fdir
        # Initialize slots
        self.j = None
        self.rc = None
        self.tic = None
        self.xi = None

   # --- Main runner methods ---
    # Main loop
    @run_rootdir
    def run(self):
        r"""Setup and run appropriate solver commands

        :Call:
            >>> runner.run()
        :Inputs:
            *runner*: :class:`CaseRunner`
                Controller to run one case of solver
        :Versions:
            * 2014-10-02 ``@ddalle``: v1.0
            * 2021-10-08 ``@ddalle``: v1.1 (``run_overflow``)
        """
        # Parse arguments
        a, kw = argread.readkeys(sys.argv)
        # Check for help argument.
        if kw.get('h') or kw.get('help'):
            # Display help and exit
            print(textutils.markdown(self._help_msg))
            # Stop execution
            return IERR_OK
        # Create RUNNING file and start timer
        # (Also raises Exception if case already running)
        self.tic = init_timer()
        # Read run control settings
        rc = self.read_case_json()
        # Initialize start counter
        nstart = 0
        # Loop until case exits, fails, or reaches start count limit
        while nstart < self._nstart_max:
            # Determine the phase
            j = self.get_phase()
            # Write start time
            ...
            # Prepare environment variables
            prepare_env(rc, j)
            # Run appropriate commands
            try:
                self.run_phase(rc, j)
            except Exception:
                # Failure
                mark_failure("run_phase")
                # Stop running marker
                mark_stopped()
                # Return code
                return IERR_RUN_PHASE
            # Clean up files
            ...
            # Save time usage
            ...
            # Update start counter
            nstart += 1

    # Run a phase
    def run_phase(self, rc, j: int):
        r"""Run one phase using appropriate commands

        :Call:
            >>> runner.run_phase(rc, j)
        :Inputs:
            *runner*: :class:`CaseRunner`
                Controller to run one case of solver
            *rc*: :class:`RunControlOpts`
                Options interface from ``case.json``
            *j*: :class:`int`
                Phase number
        :Versions:
            * 2023-06-05 ``@ddalle``: v1.0 (``pyover``)
            * 2023-06-14 ``@ddalle``: v1.0
        """
        # Run preliminary commands
        self.run_phase_pre(self, rc, j)

    # Preliminary commands
    def run_phase_pre(self, rc, j: int):
        r"""Perform preliminary actions before running phase

        :Call:
            >>> runner.run_phase_pre(rc, j)
        :Inputs:
            *runner*: :class:`CaseRunner`
                Controller to run one case of solver
            *rc*: :class:`RunControlOpts`
                Options interface from ``case.json``
            *j*: :class:`int`
                Phase number
        :Versions:
            * 2023-06-14 ``@ddalle``: v1.0
        """
        pass

   # --- Local info ---
    # Read ``case.json``
    def read_case_json(self, f=False):
        r"""Read ``case.json`` if not already

        :Call:
            >>> rc = runner.read_case_json(f=False)
        :Inputs:
            *runner*: :class:`CaseRunner`
                Controller to run one case of solver
            *f*: ``True`` | {``False``}
                Option to force re-read
        :Outputs:
            *rc*: :class:`RunControlOpts`
                Options interface from ``case.json``
        :Versions:
            * 2023-06-15 ``@ddalle``: v1.0
        """
        # Check if present
        if (not f) and isinstance(self.rc, self._rc_cls):
            # Already read
            return self.rc
        # Absolute path
        fjson = os.path.join(self.root_dir, RC_FILE)
        # Read it and save it
        self.rc = self._rc_cls(fjson)
        # Return it
        return self.rc

    # Read ``conditions.json``
    def read_conditions(self, f=False):
        r"""Read ``conditions.json`` if not already

        :Call:
            >>> xi = runner.read_conditions(f=False)
        :Inputs:
            *runner*: :class:`CaseRunner`
                Controller to run one case of solver
            *f*: ``True`` | {``False``}
                Option to force re-read
        :Outputs:
            *xi*: :class:`dict`
                Run matrix conditions for this case
        :Versions:
            * 2023-06-16 ``@ddalle``: v1.0
        """
        # Check if present
        if (not f) and isinstance(self.xi, dict):
            # Already read
            return self.xi
        # Absolute path
        fconds = os.path.join(self.root_dir, CONDITIONS_FILE)
        # Check if file exists
        if os.path.isfile(fconds):
            # Open file for handling by json
            with open(fconds) as fp:
                # Read it and save
                self.xi = json.load(fp)
        else:
            # No conditions to read
            self.xi = {}
        # Output
        return self.xi

    # Get condition of a single run matrix key
    def read_condition(self, key: str, f=False):
        r"""Read ``conditions.json`` if not already

        :Call:
            >>> v = runner.read_condition(key, f=False)
        :Inputs:
            *runner*: :class:`CaseRunner`
                Controller to run one case of solver
            *key*: :class:`str`
                Name of run matrix key to query
            *f*: ``True`` | {``False``}
                Option to force re-read
        :Outputs:
            *v*: :class:`int` | :class:`float` | :class:`str`
                Value of run matrix key *key*
        :Versions:
            * 2023-06-16 ``@ddalle``: v1.0
        """
        # Read conditions
        xi = self.read_conditions(f)
        # Get single key
        return xi.get(key)

    # Get PBS/Slurm job ID
    @run_rootdir
    def get_job_id(self, j: int) -> str:
        r"""Get PBS/Slurm job ID, if any

        :Call:
            >>> job_id = runner.get_job_id(j)
        :Inputs:
            *runner*: :class:`CaseRunner`
                Controller to run one case of solver
            *j*: :class:`int`
                Phase index
        :Outputs:
            *job_id*: :class:`str`
                Text form of job ID; ``''`` if no job found
        """
        # Initialize job ID
        job_id = ''
        # Unpack options
        rc = self.read_case_json()
        # Check for job ID
        if rc.get_qsub(j) or rc.get_slurm(j):
            # Test if file exists
            if os.path.isfile(JOB_ID_FILE):
                # Read first line
                line = open(JOB_ID_FILE).readline()
                # Get first "word"
                job_id = line.split(maxsplit=1)[0].strip()
        # Output
        return job_id

   # --- Status ---
    # Determine phase number
    @run_rootdir
    def get_phase(self, n: int, f=True) -> int:
        r"""Determine phase number in present case

        :Call:
            >>> j = runner.get_phase(n, f=True)
        :Inputs:
            *runner*: :class:`CaseRunner`
                Controller to run one case of solver
            *n*: :class:`int`
                Iteration number
            *f*: {``True``} | ``False``
                Force recalculation of phase
        :Outputs:
            *j*: :class:`int`
                Phase number for next restart
        :Versions:
            * 2014-10-02 ``@ddalle``: v1.0
            * 2015-10-19 ``@ddalle``: v1.1; FUN3D version
            * 2016-04-14 ``@ddalle``: v1.2; CFDX version
            * 2023-06-16 ``@ddalle``: v2.0; CaseRunner method
        """
        # Check if present
        if not (f or self.j is None):
            # Return precalculated phase
            return self.j
        # Calculate
        j = self._get_phase(n)
        # Save and return
        self.j = j
        return j

    def _get_phase(self, n: int):
        r"""Calculate phase based on present files

        :Call:
            >>> j = runner._get_phase(n)
        :Inputs:
            *runner*: :class:`CaseRunner`
                Controller to run one case of solver
            *n*: :class:`int`
                Iteration number
        :Outputs:
            *j*: :class:`int`
                Phase number for next restart
        :Versions:
            * 2023-06-16 ``@ddalle``: v1.0
        """
        # Get case options
        rc = self.read_case_json()
        # Get prefix
        fpre = self._logprefix
        # Loop through possible input numbers.
        for j in rc.get_PhaseSequence():
            # Check for output files
            if len(glob.glob('%s.%02i.*' % (fpre, j))) == 0:
                # This run has not been completed yet
                return j
            # Check the iteration number
            if n < rc.get_PhaseIters(j):
                # Phase has been run but not reached phase iter target
                return j
        # Case completed; just return the last value.
        return j

   # --- Timing and logs ---
    # Write *tic* to a file
    @run_rootdir
    def write_start_time(self, j: int):
        r"""Write current start time, *runner.tic*, to file

        :Call:
            >>> runner.write_start_time(tic, j)
        :Inputs:
            *runner*: :class:`CaseRunner`
                Controller to run one case of solver
            *j*: :class:`int`
                Phase number
        :Versions:
            * 2015-12-09 ``@ddalle``: v1.0 (pycart)
            * 2015-12-22 ``@ddalle``: v1.0; module function
            * 2023-06-16 ``@ddalle``: v2.0; ``CaseRunner`` method
        """
        # Get class's name options
        pymod = self._modname
        # Form a file name
        fname = f"{pymod}_start.dat"
        # Check if the file exists
        qnew = not os.path.isfile(fname)
        # Open file
        with open(fname, 'a') as fp:
            # Write header if new
            if qnew:
                fp.write("# nProc, program, date, jobID\n")
            # Write remainder of file
            self._write_start_time(fp, j)

    # Write execution time to file
    @run_rootdir
    def write_user_time(self, j: int):
        r"""Write time usage since time *tic* to file

        :Call:
            >>> runner.write_user_time(tic, j)
        :Inputs:
            *runner*: :class:`CaseRunner`
                Controller to run one case of solver
            *j*: :class:`int`
                Phase number
        :Versions:
            * 2015-12-09 ``@ddalle``: v1.0 (pycart)
            * 2015-12-22 ``@ddalle``: v1.0; module function
            * 2023-06-16 ``@ddalle``: v2.0; ``CaseRunner`` method
        """
        # Get class's name options
        pymod = self._modname
        # Form a file name
        fname = f"{pymod}_time.dat"
        # Check if the file exists
        qnew = not os.path.isfile(fname)
        # Open file
        with open(fname, 'a') as fp:
            # Write header if new
            if qnew:
                fp.write("# TotalCPUHours, nProc, program, date, jobID\n")
            # Write remainder of file
            self._write_user_time(fp, j)

    # Write start time
    def _write_start_time(self, fp, j: int):
        # Get options
        rc = self.read_case_json()
        # Initialize job ID
        jobID = self.get_job_id(j)
        # Program name
        prog = self._progname
        # Number of processors
        nProc = rc.get_nProc(j)
        # Format time
        t_text = self.tic.strftime('%Y-%m-%d %H:%M:%S %Z')
        # Write the data
        fp.write('%4i, %-20s, %s, %s\n' % (nProc, prog, t_text, jobID))

    # Write time since
    def _write_user_time(self, fp, j: int):
        # Get options
        rc = self.read_case_json()
        # Initialize job ID
        jobID = self.get_job_id(j)
        # Program name
        prog = self._progname
        # Get the time
        toc = datetime.now()
        # Number of processors
        nProc = rc.get_nProc(j)
        # Time difference
        t = toc - self.tic
        # Calculate CPU hours
        CPU = nProc * (t.days*24 + t.seconds/3600.0)
        # Format time
        t_text = toc.strftime('%Y-%m-%d %H:%M:%S %Z')
        # Write the data
        fp.write(
            '%8.2f, %4i, %-20s, %s, %s\n'
            % (CPU, nProc, prog, t_text, jobID))


# Function to intersect geometry if appropriate
def CaseIntersect(rc, j, proj='Components', n=0, fpre='run'):
    r"""Run ``intersect`` to combine geometries if appropriate

    This is a multistep process in order to preserve all the component
    IDs of the input triangulations. Normally ``intersect`` requires
    each intersecting component to have a single component ID, and each
    component must be a water-tight surface.

    Cape utilizes two input files, ``Components.c.tri``, which is the
    original triangulation file with intersections and the original
    component IDs, and ``Components.tri``, which maps each individual
    original ``tri`` file to a single component. The files involved are
    tabulated below.

    * ``Components.tri``: Intersecting components, each with own compID
    * ``Components.c.tri``: Intersecting triangulation, original compIDs
    * ``Components.o.tri``: Output of ``intersect``, only a few compIDs
    * ``Components.i.tri``: Original compIDs mapped to intersected tris

    More specifically, these files are ``"%s.i.tri" % proj``, etc.; the
    default project name is ``"Components"``.  This function also calls
    the Chimera Grid Tools program ``triged`` to remove unused nodes from
    the intersected triangulation and optionally remove small triangles.

    :Call:
        >>> CaseIntersect(rc, proj='Components', n=0, fpre='run')
    :Inputs:
        *rc*: :class:`RunControlOpts`
            Case options interface from ``case.json``
        *proj*: {``'Components'``} | :class:`str`
            Project root name
        *n*: :class:`int`
            Iteration number
        *fpre*: {``'run'``} | :class:`str`
            Standard output file name prefix
    :See also:
        * :class:`cape.tri.Tri`
        * :func:`cape.bin.intersect`
    :Versions:
        * 2015-09-07 ``@ddalle``: Split from :func:`run_flowCart`
        * 2016-04-05 ``@ddalle``: Generalized to :mod:`cape`
    """
    # Exit if not phase zero
    if j > 0:
        return
    # Check for intersect status.
    if not rc.get_intersect():
        return
    # Check for initial run
    if n:
        return
    # Triangulation file names
    ftri  = "%s.tri" % proj
    fftri = "%s.f.tri" % proj
    fotri = "%s.o.tri" % proj
    fctri = "%s.c.tri" % proj
    fatri = "%s.a.tri" % proj
    futri = "%s.u.tri" % proj
    fitri = "%s.i.tri" % proj
    # Check for triangulation file.
    if os.path.isfile(fitri):
        # Note this.
        print("File '%s' already exists; aborting intersect." % fitri)
        return
    # Set file names
    rc.set_intersect_i(ftri)
    rc.set_intersect_o(fotri)
    # Run intersect
    if not os.path.isfile(fotri):
        bin.intersect(opts=rc)
    # Read the original triangulation.
    tric = Tri(fctri)
    # Read the intersected triangulation.
    trii = Tri(fotri)
    # Read the pre-intersection triangulation.
    tri0 = Tri(ftri)
    # Map the Component IDs
    if os.path.isfile(fatri):
        # Just read the mapped file
        trii = Tri(fatri)
    elif os.path.isfile(futri):
        # Just read the mapped file w/o unused nodes
        trii = Tri(futri)
    else:
        # Perform the mapping
        trii.MapCompID(tric, tri0)
        # Add in far-field, sources, non-intersect comps
        if os.path.isfile(fftri):
            # Read the tri file
            trif = Tri(fftri)
            # Add it to the mapped triangulation
            trii.AddRawCompID(trif)
    # Intersect post-process options
    o_rm = rc.get_intersect_rm()
    o_triged = rc.get_intersect_triged()
    o_smalltri = rc.get_intersect_smalltri()
    # Check if we can use ``triged`` to remove unused triangles
    if o_triged:
        # Write the triangulation.
        trii.Write(fatri)
        # Remove unused nodes
        infix = "RemoveUnusedNodes"
        fi = open('triged.%s.i' % infix, 'w')
        # Write inputs to the file
        fi.write('%s\n' % fatri)
        fi.write('10\n')
        fi.write('%s\n' % futri)
        fi.write('1\n')
        fi.close()
        # Run triged to remove unused nodes
        print(" > triged < triged.%s.i > triged.%s.o" % (infix, infix))
        os.system("triged < triged.%s.i > triged.%s.o" % (infix, infix))
    else:
        # Trim unused trianlges (internal)
        trii.RemoveUnusedNodes(v=True)
        # Write trimmed triangulation
        trii.Write(futri)
    # Check if we should remove small triangles
    if o_rm and o_triged:
        # Input file to remove small tris
        infix = "RemoveSmallTris"
        fi = open('triged.%s.i' % infix, 'w')
        # Write inputs to file
        fi.write('%s\n' % futri)
        fi.write('19\n')
        fi.write('%f\n' % rc.get("SmallArea", o_smalltri))
        fi.write('%s\n' % fitri)
        fi.write('1\n')
        fi.close()
        # Run triged to remove small tris
        print(" > triged < triged.%s.i > triged.%s.o" % (infix, infix))
        os.system("triged < triged.%s.i > triged.%s.o" % (infix, infix))
    elif o_rm:
        # Remove small triangles (internally)
        trii.RemoveSmallTris(o_smalltri, v=True)
        # Write final triangulation file
        trii.Write(fitri)
    else:
        # Rename file
        os.rename(futri, fitri)


# Function to verify if requested
def CaseVerify(rc, j, proj='Components', n=0, fpre='run'):
    r"""Run ``verify`` to check triangulation if appropriate

    This function checks the validity of triangulation in file
    ``"%s.i.tri" % proj``.  It calls :func:`cape.bin.verify`.

    :Call:
        >>> CaseVerify(rc, proj='Components', n=0, fpre='run')
    :Inputs:
        *rc*: :class:`RunControlOpts`
            Case options interface from ``case.json``
        *proj*: {``'Components'``} | :class:`str`
            Project root name
        *n*: :class:`int`
            Iteration number
        *fpre*: {``'run'``} | :class:`str`
            Standard output file name prefix
    :Versions:
        * 2015-09-07 ``@ddalle``: v1.0; from :func:`run_flowCart`
        * 2016-04-05 ``@ddalle``: v1.1; generalize to :mod:`cape`
    """
    # Exit if not phase zero
    if j > 0:
        return
    # Check for verify
    if not rc.get_verify():
        return
    # Check for initial run
    if n:
        return
    # Set file name
    rc.set_verify_i('%s.i.tri' % proj)
    # Run it.
    bin.verify(opts=rc)


# Mesh generation
def run_aflr3(opts, j, proj='Components', fmt='lb8.ugrid', n=0):
    r"""Create volume mesh using ``aflr3``

    This function looks for several files to determine the most
    appropriate actions to take, replacing ``Components`` with the value
    from *proj* for each file name and ``lb8.ugrid`` with the value from
    *fmt*:

        * ``Components.i.tri``: Triangulation file
        * ``Components.surf``: AFLR3 surface file
        * ``Components.aflr3bc``: AFLR3 boundary conditions
        * ``Components.xml``: Surface component ID mapping file
        * ``Components.lb8.ugrid``: Output volume mesh
        * ``Components.FAIL.surf``: AFLR3 surface indicating failure

    If the volume grid file already exists, this function takes no
    action. If the ``surf`` file does not exist, the function attempts
    to create it by reading the ``tri``, ``xml``, and ``aflr3bc`` files
    using :class:`cape.tri.Tri`.  The function then calls
    :func:`cape.bin.aflr3` and finally checks for the ``FAIL`` file.

    :Call:
        >>> run_aflr3(opts, proj="Components", fmt='lb8.ugrid', n=0)
    :Inputs:
        *opts*: :class:`RunControlOpts`
            Options instance from ``case.json``
        *proj*: {``"Components"``} | :class:`str`
            Project root name
        *fmt*: {``"b8.ugrid"``} | :class:`str`
            AFLR3 volume mesh format
        *n*: :class:`int`
            Iteration number
    :Versions:
        * 2016-04-05 ``@ddalle``: v1.0 (``CaseAFLR3()``)
        * 2023-06-02 ``@ddalle``: v1.1; Clean and use ``run_aflr3_run)``
    """
    # Check for initial run
    if (n is not None) or j:
        # Don't run AFLR3 if >0 iterations already complete
        return
    # Check for option to run AFLR3
    if not opts.get_aflr3_run(j=0):
        # AFLR3 not requested for this run
        return
    # File names
    ftri = '%s.i.tri' % proj
    fsurf = '%s.surf' % proj
    fbc = '%s.aflr3bc' % proj
    fxml = '%s.xml' % proj
    fvol = '%s.%s' % (proj, fmt)
    ffail = "%s.FAIL.surf" % proj
    # Exit if volume exists
    if os.path.isfile(fvol):
        return
    # Check for file availability
    if not os.path.isfile(fsurf):
        # Check for the triangulation to provide a nice error message if app.
        if not os.path.isfile(ftri):
            raise ValueError(
                "User has requested AFLR3 volume mesh.\n" +
                ("But found neither Cart3D tri file '%s' " % ftri) +
                ("nor AFLR3 surf file '%s'" % fsurf))
        # Read the triangulation
        if os.path.isfile(fxml):
            # Read with configuration
            tri = Tri(ftri, c=fxml)
        else:
            # Read without config
            tri = Tri(ftri)
        # Check for boundary condition flags
        if os.path.isfile(fbc):
            tri.ReadBCs_AFLR3(fbc)
        # Write the surface file
        tri.WriteSurf(fsurf)
    # Set file names
    opts.set_aflr3_i(fsurf)
    opts.set_aflr3_o(fvol)
    # Run AFLR3
    bin.aflr3(opts=opts)
    # Check for failure; aflr3 returns 0 status even on failure
    if os.path.isfile(ffail):
        # Remove RUNNING file
        mark_stopped()
        # Create failure file
        mark_failure("aflr3")
        # Error message
        raise RuntimeError(
            "Failure during AFLR3 run:\n" +
            ("File '%s' exists." % ffail))


# Function for the most recent available restart iteration
def GetRestartIter():
    r"""Get the restart iteration

    This is a placeholder function and is only called in error.

    :Call:
        >>> cape.case.GetRestartIter()
    :Raises:
        *RuntimeError*: :class:`Exception`
            Error regarding where this was called
    :Versions:
        * 2016-04-14 ``@ddalle``: v1.0
    """
    raise IOError("Called cape.case.GetRestartIter()")


# Function to call script or submit.
def StartCase():
    r"""Empty template for starting a case

    The function is empty but does not raise an error

    :Call:
        >>> cape.case.StartCase()
    :See also:
        * :func:`cape.pycart.case.StartCase`
        * :func:`cape.pyfun.case.StartCase`
        * :func:`cape.pyover.case.StartCase`
    :Versions:
        * 2015-09-27 ``@ddalle``: v1.0
        * 2023-06-02 ``@ddalle``: v2.0; empty
    """
    pass


# Function to delete job and remove running file.
def StopCase():
    r"""Stop a case by deleting PBS job and removing ``RUNNING`` file

    :Call:
        >>> case.StopCase()
    :Versions:
        * 2014-12-27 ``@ddalle``: v1.0
    """
    # Get the config.
    fc = ReadCaseJSON()
    # Get the job number.
    jobID = queue.pqjob()
    # Try to delete it.
    if fc.get_slurm(0):
        # Delete Slurm job
        queue.scancel(jobID)
    else:
        # Delete PBS job
        queue.qdel(jobID)
    # Delete RUNNING file if appropriate
    mark_stopped()


# Celete running file if approrpate
def mark_stopped():
    r"""Delete the ``RUNNING`` file if it exists

    :Call:
        >>> mark_stopped()
    :Versions:
        * 2023-06-02 ``@ddalle``: v1.0
    """
    # Check if file exists
    if os.path.isfile(RUNNING_FILE):
        # Delete it
        os.remove(RUNNING_FILE)


# Check if case is already running
def check_running():
    r"""Check if a case is already running, raise exception if so

    :Call:
        >>> check_running()
    :Versions:
        * 2023-06-02 ``@ddalle``: v1.0
    """
    # Check for RUNNING file
    if os.path.isfile(RUNNING_FILE):
        # Case already running
        raise IOError('Case already running!')


# Mark a cases as running
def mark_running():
    r"""Check if cases already running and create ``RUNNING`` otherwise

    :Call:
        >>> mark_running()
    :Versions:
        * 2023-06-02 ``@ddalle``: v1.0
    """
    # Check for RUNNING file
    check_running()
    # Create RUNNING file
    open(RUNNING_FILE, "w").close()


# General function to mark failures
def mark_failure(msg="no details"):
    r"""Mark the current folder in failure status using ``FAIL`` file

    :Call:
        >>> mark_failure(msg="no details")
    :Inputs:
        *msg*: ``{"no details"}`` | :class:`str`
            Error message for output file
    :Versions:
        * 2023-06-02 ``@ddalle``: v1.0
    """
    # Ensure new line
    txt = msg.rstrip("\n") + "\n"
    # Append message to failure file
    open(FAIL_FILE, "a+").write(txt)


# Function to set the environment
def prepare_env(rc, i=0):
    r"""Set environment variables, alter resource limits (``ulimit``)

    This function relies on the system module :mod:`resource`.

    :Call:
        >>> case.prepare_env(rc, i=0)
    :Inputs:
        *rc*: :class:`RunControlOpts`
            Options interface for run control and command-line inputs
        *i*: :class:`int`
            Phase number
    :See also:
        * :func:`SetResourceLimit`
    :Versions:
        * 2015-11-10 ``@ddalle``: v1.0 (``PrepareEnvironment()``)
        * 2023-06-02 ``@ddalle``: v1.1; fix logic for appending
            - E.g. ``"PATH": "+$HOME/bin"``
            - This is designed to append to path
    """
    # Loop through environment variables
    for key in rc.get('Environ', {}):
        # Get the environment variable
        val = rc.get_Environ(key, i)
        # Check if it stars with "+"
        if val.startswith("+"):
            # Remove preceding '+' signes
            val = val.lstrip('+')
            # Check if it's present
            if key in os.environ:
                # Append to path
                os.environ[key] += (os.path.pathsep + val.lstrip('+'))
                continue
        # Set the environment variable from scratch
        os.environ[key] = val
    # Get ulimit parameters
    ulim = rc['ulimit']
    # Block size
    block = resource.getpagesize()
    # Set the stack size
    SetResourceLimit(resource.RLIMIT_STACK,   ulim, 's', i, 1024)
    SetResourceLimit(resource.RLIMIT_CORE,    ulim, 'c', i, block)
    SetResourceLimit(resource.RLIMIT_DATA,    ulim, 'd', i, 1024)
    SetResourceLimit(resource.RLIMIT_FSIZE,   ulim, 'f', i, block)
    SetResourceLimit(resource.RLIMIT_MEMLOCK, ulim, 'l', i, 1024)
    SetResourceLimit(resource.RLIMIT_NOFILE,  ulim, 'n', i, 1)
    SetResourceLimit(resource.RLIMIT_CPU,     ulim, 't', i, 1)
    SetResourceLimit(resource.RLIMIT_NPROC,   ulim, 'u', i, 1)


# Set resource limit
def SetResourceLimit(r, ulim, u, i=0, unit=1024):
    r"""Set resource limit for one variable

    :Call:
        >>> SetResourceLimit(r, ulim, u, i=0, unit=1024)
    :Inputs:
        *r*: :class:`int`
            Integer code of particular limit, from :mod:`resource`
        *ulim*: :class:`cape.options.ulimit.ulimit`
            System resource options interface
        *u*: :class:`str`
            Name of limit to set
        *i*: :class:`int`
            Phase number
        *unit*: :class:`int`
            Multiplier, usually for a kbyte
    :See also:
        * :mod:`cape.options.ulimit`
    :Versions:
        * 2016-03-13 ``@ddalle``: v1.0
        * 2021-10-21 ``@ddalle``: v1.1; check if Windows
    """
    # Check if the limit has been set
    if u not in ulim:
        return
    elif resource is None:
        # Running on Windows
        return
    # Get the value of the limit
    l = ulim.get_ulimit(u, i)
    # Check the type
    if isinstance(l, (int, float)) and (l > 0):
        # Set the value numerically
        try:
            resource.setrlimit(r, (unit*l, unit*l))
        except ValueError:
            pass
    else:
        # Set unlimited
        resource.setrlimit(r, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))


# Resubmit a case, if appropriate
def resubmit_case(rc, fpbs: str, j0: int, j1: int):
    r"""Resubmit a case as a new job if appropriate

    :Call:
        >>> q = resubmit_case(rc, j0)
    :Inputs:
        *rc*: :class:`RunControl`
            Options interface from ``case.json``
        *j0*: :class:`int`
            Index of phase most recently run prior
            (may differ from current phase)
        *j1*: :class:`int`
            Current phase
    :Outputs:
        *q*: ``True`` | ``False``
            Whether or not a new job was submitted to queue
    :Versions:
        * 2022-01-20 ``@ddalle``: v1.0 (:mod:`cape.pykes.case`)
        * 2023-06-02 ``@ddalle``: v1.0
    """
    # Job submission options
    qsub0 = rc.get_qsub(j0) or rc.get_slurm(j0)
    qsub1 = rc.get_qsub(j1) or rc.get_slurm(j1)
    # Trivial case if phase *j* is not submitted
    if not qsub1:
        return False
    # Check if *j1* is submitted and not *j0*
    if not qsub0:
        # Submit new phase
        _submit_job(rc, fpbs, j1)
        return True
    # If rerunning same phase, check the *Continue* option
    if j0 == j1:
        if rc.get_Continue(j0):
            # Don't submit new job (continue current one)
            return False
        else:
            # Rerun same phase as new job
            _submit_job(rc, fpbs, j1)
            return True
    # Now we know we're going to new phase; check the *Resubmit* opt
    if rc.get_Resubmit(j0):
        # Submit phase *j1* as new job
        _submit_job(rc, fpbs, j1)
        return True
    else:
        # Continue to next phase in same job
        return False


# Submit a job using PBS, Slurm, (something else,) or nothing
def _submit_job(rc, fpbs: str, j: int):
    # Check submission type
    if rc.get_qsub(j):
        # Submit PBS job
        return queue.pqsub(fpbs)
    elif rc.get_qsbatch(j):
        # Submit slurm job
        return queue.pqsbatch(fpbs)


# Function to get most recent L1 residual
def GetCurrentIter():
    r"""Template function to report the most recent iteration

    :Call:
        >>> n = cape.case.GetCurrentIter()
    :Outputs:
        *n*: ``0``
            Most recent index, customized for each solver
    :Versions:
        * 2015-09-27 ``@ddalle``: v1.0
    """
    return 0


# Read most recent start time from file
def ReadStartTimeProg(fname):
    """Read the most recent start time to file

    :Call:
        >>> nProc, tic = ReadStartTimeProg(fname)
    :Inputs:
        *fname*: :class:`str`
            Name of file containing CPU usage history
    :Outputs:
        *nProc*: :class:`int`
            Number of cores
        *tic*: :class:`datetime.datetime`
            Time at which most recent run was started
    :Versions:
        * 2016-08-30 ``@ddalle``: v1.0
    """
    # Check for the file
    if not os.path.isfile(fname):
        # No time of start
        return None, None
    # Avoid failures
    try:
        # Read the last line and split on commas
        V = bin.tail(fname).split(',')
        # Get the number of processors
        nProc = int(V[0])
        # Split date and time
        dtxt, ttxt = V[2].strip().split()
        # Get year, month, day
        year, month, day = [int(v) for v in dtxt.split('-')]
        # Get hour, minute, second
        hour, minute, sec = [int(v) for v in ttxt.split(':')]
        # Construct date
        tic = datetime(year, month, day, hour, minute, sec)
        # Output
        return nProc, tic
    except Exception:
        # Fail softly
        return None, None


# Function to determine newest triangulation file
def GetTriqFile(proj='Components'):
    r"""Get most recent ``triq`` file and its associated iterations

    This is a template version with specific implementations for each
    solver. The :mod:`cape.cfdx` version simply returns the most recent
    ``triq`` file in the  folder with no iteration information.

    :Call:
        >>> ftriq, n, i0, i1 = GetTriqFile(proj='Components')
    :Inputs:
        *proj*: {``"Components"``} | :class:`str`
            File root name
    :Outputs:
        *ftriq*: :class:`str`
            Name of most recently modified ``triq`` file
        *n*: {``None``}
            Number of iterations included
        *i0*: {``None``}
            First iteration in the averaging
        *i1*: {``None``}
            Last iteration in the averaging
    :Versions:
        * 2016-12-19 ``@ddalle``: v1.0
    """
    # Get the glob of numbered files.
    fglob = glob.glob('*.triq')
    # Check it.
    if len(fglob) > 0:
        # Get modification times
        t = [os.path.getmtime(f) for f in fglob]
        # Extract file with maximum index
        ftriq = fglob[t.index(max(t))]
        # Output
        return ftriq, None, None, None
    else:
        # No TRIQ files
        return None, None, None, None


# Initialize running case
def init_timer():
    r"""Mark a case as ``RUNNING`` and initialize a timer

    :Call:
        >>> tic = init_timer()
    :Outputs:
        *tic*: :class:`datetime.datetime`
            Time at which case was started
    :Versions:
        * 2021-10-21 ``@ddalle``: v1.0; from :func:`run_fun3d`
    """
    # Touch (create) the running file, exception if already exists
    mark_running()
    # Start timer
    tic = datetime.now()
    # Output
    return tic


# Function to read the local settings file
def read_case_json(cls=RunControlOpts):
    r"""Read *RunControl* settings from ``case.json``

    :Call:
        >>> rc = read_case_json()
        >>> rc = read_case_json(cls)
    :Inputs:
        *cls*: {:mod:`RunControlOpts`} | :class:`type`
            Class to use for output file
    :Outputs:
        *rc*: *cls*
            Case run control settings
    :Versions:
        * 2021-10-21 ``@ddalle``: v1.0
    """
    # Check for file
    if not os.path.isfile("case.json"):
        # Use defaults
        return cls()
    # Read the file, fail if not present
    with open("case.json") as fp:
        # Read the settings.
        opts = json.load(fp)
    # Convert to a flowCart object.
    rc = cls(**opts)
    # Output
    return rc

