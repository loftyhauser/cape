#!/usr/bin/env python
"""
Convert Triangulation to Tecplot PLT Format: :file:`pc_Tri2Plt.py`
==================================================================

Convert a Cart3D triangulation ``.tri`` or ``.triq`` file to a Tecplot PLT
file.  Each component of the triangulation is written as a separate zone.

:Call:

    .. code-block:: console
    
        $ pc_Tri2UH3D.py -i $tri -c $cfg -o $uh3d
        $ pc_Tri2UH3D.py $tri
        $ pc_Tri2UH3D.py -i $tri
        $ pc_Tri2UH3D.py $tri $uh3d
        $ pc_Tri2UH3D.py -h

:Inputs:
    * *tri*: Name of output '.tri' file
    * *uh3d*: Name of input '.uh3d' file
    
:Options:
    -h, --help
        Display this help message and exit
        
    -i TRI
        Use *TRI* as name of created output file
        
    -c CFG
        Use *CFG* as configuration file (defaults to :file:`Config.xml`)
        
    -o UH3D
        Use *UH3D* as input file
    
If the name of the output file is not specified, the script will just add
``.uh3d`` as the extension to the input (deleting ``.tri`` if possible).

:Versions:
    * 2015-04-17 ``@ddalle``: First version
"""

# Get the geometry file format modules
import cape.tri
import cape.plt
# Module to handle inputs and os interface
import sys, os.path
# Command-line input parser
import cape.argread

# Main function
def Tri2Plt(*a, **kw):
    """
    Convert a UH3D triangulation file to Cart3D tri format
    
    :Call:
        >>> Tri2Plt(tri, c, plt=None, dat=None, h=False)
        >>> Tri2Plt(tri=None, c='Config.xml', plt=None, dat=None, h=False)
    :Inputs:
        *tri*: :class:`str`
            Name of input file; can be any readable TRI or TRIQ format
        *plt*: {``None``} | :class:`str`
            Name of PLT file to create; defaults to name of TRI file with the
            ``.tri`` replaced by ``.plt``
        *dat*: {``None``} | :class:`str`
            If not ``None``, write this file as Tecplot ASCII; suppresses PLT
        *c*: :class:`str`
            Name of configuration file (XML, JSON, or MIXSUR format)
        *h*, *help*: ``True`` | {``False``}
            Display help and exit if ``True``
        *v*: ``True`` | {``False``}
            Verbose output while creating PLT interface
    :Versions:
        * 2016-04-05 ``@ddalle``: First version
    """
    # Get the file pyCart settings file name.
    if len(a) == 0:
        # Defaults
        ftri = None
    else:
        # Use the first general input.
        ftri = a[0]
    # Prioritize a "-i" input.
    ftri = kw.get('tri', ftri)
    # Must have a file name.
    if ftri is None:
        # Required input.
        print __doc__
        raise IOError("At least one input required.")
    
    # Get the file pyCart settings file name.
    if len(a) <= 2:
        # Defaults
        fcfg = "Config.xml"
    else:
        # Use the first general input.
        fcfg = a[1]
    # Prioritize a "-i" input.
    fcfg = kw.get('c', fcfg)
        
    # Read in the triangulation
    if os.path.isfile(fcfg):
        # Read the file
        tri = cape.tri.Tri(ftri, c=fcfg)
    else:
        # Read TRI file without configuration
        tri = cape.tri.Tri(ftri)
    
    # Determine default output
    if ftri.endswith("tri"):
        # Strip "tri" and replace with "plt"
        fplt = ftri[:-3] + "plt"
    else:
        # Otherwise add .plt
        fplt = ftri + ".plt"
    # Process output file names
    fplt = kw.get("plt", fplt)
    fdat = kw.get("dat")
    
    # Create PLT interface
    plt = cape.plt.Plt(triq=tri, **kw)
    
    # Output
    if fdat is None:
        # Write PLT file
        plt.Write(fplt)
    else:
        # Write ASCII Tecplot DAT file
        plt.WriteDat(fdat)
        

# Only process inputs if called as a script!
if __name__ == "__main__":
    # Process the command-line interface inputs.
    (a, kw) = cape.argread.readkeys(sys.argv)
    # Check for a help option.
    if kw.get('h',False) or kw.get('help',False):
        print __doc__
        sys.exit()
    # Run the main function.
    Tri2Plt(*a, **kw)
    
