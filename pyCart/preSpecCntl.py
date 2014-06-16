"""
Module to interface with "input.cntl" files: :mod:`pyCart.inputCntl`
====================================================================

This is a module built off of the :mod:`pyCart.fileCntl` module customized for
manipulating :file:`input.cntl` files.  Such files are split into section by lines of
the format

    ``$__Post_Processing``
    
and this module is designed to recognize such sections.  The main feature of
this module is methods to set specific properties of the :file:`input.cntl` 
file, for example the Mach number or CFL number.
"""

# Import the base file control class.
from fileCntl import FileCntl, _num, _float

# Base this class off of the main file control class.
class PreSpecCntl(FileCntl):
    """
    File control class for :file:`preSpec.c3d.cntl` files
    
    :Call:
        >>> preSpec = pyCart.PreSpecCntl()
        >>> preSpec = pyCart.PreSpecCntl(fname)
        
    :Inputs:
        *fname*: :class:`str`
            Name of CNTL file to read, defaults to ``'preSpec.c3d.cntl'``
            
    This class is derived from the :class:`pyCart.fileCntl.FileCntl` class, so
    all methods applicable to that class can also be used for instances of this
    class.
    """
    
    # Initialization method (not based off of FileCntl)
    def __init__(self, fname="preSpec.c3d.cntl"):
        """Initialization method"""
        # Versions:
        #  2014.06.16 @ddalle  : First version
        
        # Read the file.
        self.Read(fname)
        # Save the file name.
        self.fname = fname
        # Split into sections.
        self.SplitToSections(reg="\$__([\w_]+)")
        return None
        
    # Function to add an additional BBox
    def AddBBox(self, n, xlim):
        """
        Add an additional bounding box to the :file:`cubes` input control file
        
        :Call:
            >>> preSpec.AddBBox(n, xlim)
            
        :Inputs:
            *preSpec*: :class:`pyCart.preSpecCntl.PreSpecCntl`
                Instance of the :file:`preSpec.c3d.cntl` interface
            *n*: :class:`int`
                Number of refinements to use in the box
            *xlim*: :class:`numpy.ndarray` or :class:`list` (:class:`float`)
                List of *xmin*, *xmax*, *ymin*, *ymax*, *zmin*, *zmax*
            
        :Effects:
            Adds a bounding box line to the existing boxes
        """
        # Versions:
        #  2014.06.16 @ddalle  : First version
        
        # Compose the line.
        line = "BBox: %-2i %10.4f %10.4f %10.4f %10.4f %10.4f %10.4f" % (
            n, xlim[0], xlim[1], xlim[2], xlim[3], xlim[4], xlim[5])
        # Add the line.
        self.AppendLineToSection('Prespecified_Adaptation_Regions', line)
        
    # Function to clear all existing bounding boxes.
    def ClearBBoxes(self):
        """
        Delete all existing bounding boxes
        
        :Call:
            >>> preSpec.ClearBBoxes()
            
        :Inputs:
            *preSpec*: :class:`pyCart.preSpecCntl.PreSpecCntl`
                Instance of the :file:`preSpec.c3d.cntl` interface
        """
        # Versions:
        #  2014.06.16 @ddalle  : First version
        
        # Delete the lines.
        self.DeleteLineInSectionStartsWith(
            'Prespecified_Adaptation_Regions', 'BBox')
        
        
        
        
        
        
        
        
        
        
        
        
        
