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
from .fileCntl import FileCntl

# Base this class off of the main file control class.
class Namelist(FileCntl):
    """
    File control class for :file:`fun3d.nml`
    ========================================
            
    This class is derived from the :class:`pyCart.fileCntl.FileCntl` class, so
    all methods applicable to that class can also be used for instances of this
    class.
    
    :Call:
        >>> nml = cape.Namelist()
        >>> nml = cape.Namelist(fname)
    :Inputs:
        *fname*: :class:`str`
            Name of namelist file to read, defaults to ``'fun3d.nml'``
    :Version:
        * 2015-10-15 ``@ddalle``: Started
    """
    
    # Initialization method (not based off of FileCntl)
    def __init__(self, fname="fun3d.nml"):
        """Initialization method"""
        # Read the file.
        self.Read(fname)
        # Save the file name.
        self.fname = fname
        # Split into sections.
        self.SplitToSections(reg="\&([\w_]+)")
        
    # Copy the file
    def Copy(self, fname):
        """Copy a file interface
        
        :Call:
            >>> nml2 = nml.Copy()
        :Inputs:
            *nml*: :class:`cape.namelist.Namelist`
                File control instance for :file:`fun3d.nml`
        :Outputs:
            *nml2*: :class:`cape.namelist.Namelist`
                Duplicate file control instance for :file:`fun3d.nml`
        :Versions:
            * 2015-06-12 ``@ddalle``: First version
        """
        # Create empty instance.
        nml = Namelist(fname=None)
        # Copy the file name.
        nml.fname = self.fname
        nml.lines = self.lines
        # Copy the sections
        nml.Section = self.Section
        nml.SectionNames = self.SectionNames
        # Update flags.
        nml._updated_sections = self._updated_sections
        nml._updated_lines = self._updated_lines
        # Output
        return nml
        
    # Function to set generic values, since they have the same format.
    def SetVar(self, sec, name, val, k=None):
        """Set generic :file:`fun3d.nml` variable value
        
        :Call:
            >>> nml.SetVar(sec, name, val)
            >>> nml.SetVar(sec, name, val, k)
        :Inputs:
            *nml*: :class:`cape.namelist.Namelist`
                File control instance for :file:`fun3d.nml`
            *sec*: :class:`str`
                Name of section in which to set variable
            *name*: :class:`str`
                Name of variable as identified in 'aero.csh'
            *val*: any
                Value to which variable is set in final script
            *k*: :class:`int`
                Namelist index
        :Versions:
            * 2014-06-10 ``@ddalle``: First version
            * 2015-10-20 ``@ddalle``: Added Fortran index
        """
        # Check sections
        if sec not in self.SectionNames:
            raise KeyError("Section '%s' not found." % sec)
        # Check format
        if k is None:
            # Format: '   component = "something"'
            # Line regular expression: "XXXX=" but with white spaces
            reg = '^\s*%s\s*[=\n]' % name
            # Form the output line.
            line = '    %s = %s\n' % (name, self.ConvertToText(val))
        else:
            # Format: '   component(1) = "something"'
            # Line regular expression: "XXXX([0-9]+)=" but with white spaces
            reg = '^\s*%s\(%i\)\s*[=\n]' % (name, k)
            # Form the output line.
            line = '    %s(%i) = %s\n' % (name, k, self.ConvertToText(val))
        # Replace the line; prepend it if missing
        self.ReplaceOrAddLineToSectionSearch(sec, reg, line, 1)
        
    # Function to get the value of a variable
    def GetVar(self, sec, name, k=None):
        """Get value of a variable
        
        :Call:
            >>> val = nml.GetVar(sec, name)
            >>> val = nml.GetVar(sec, name, k)
        :Inputs:
            *nml*: :class:`cape.namelist.Namelist`
                File control instance for :file:`fun3d.nml`
            *sec*: :class:`str`
                Name of section in which to set variable
            *name*: :class:`str`
                Name of variable as identified in 'aero.csh'
            *k*: :class:`int`
                Namelist index
        :Outputs:
            *val*: any
                Value to which variable is set in final script
        :Versions:
            * 2015-10-15 ``@ddalle``: First version
            * 2015-10-20 ``@ddalle``: Added Fortran index
        """
        # Check sections
        if sec not in self.SectionNames:
            raise KeyError("Section '%s' not found." % sec)
        # Check for index
        if k is None:
            # Line regular expression: "XXXX=" but with white spaces
            reg = '^\s*%s\s*[=\n]' % name
        else:
            # Index: "XXXX(k)=" but with white spaces
            reg = '^\s*%s\(%i\)\s*[=\n]' % (name, k)
        # Find the line.
        lines = self.GetLineInSectionSearch(sec, reg, 1)
        # Exit if no match
        if len(lines) == 0: return None
        # Split on the equal sign
        vals = lines[0].split('=')
        # Check for a match
        if len(vals) < 1: return None
        # Convert to Python value
        return self.ConvertToVal(vals[1])
    
    
    # Return a dictionary
    def ReturnDict(self):
        """Return a dictionary of options that mirrors the namelist
        
        :Call:
            >>> opts = nml.ReturnDict()
        :Inputs:
            *nml*: :class:`cape.namelist.Namelist`
                File control instance for :file:`fun3d.nml`
        :Outputs:
            *opts*: :class:`dict`
                Dictionary of namelist options
        :Versions:
            * 2015-10-16 ``@ddalle``: First version
        """
        # Initialize dictionary
        opts = {}
        # Loop through sections
        for sec in self.SectionNames[1:]:
            # Initialize the section dictionary
            o = {}
            # Loop through the lines
            for line in self.Section[sec]:
                # Split the line to values
                vals = line.split('=')
                # Check for a parameter.
                if len(vals) < 2: continue
                # Get the name.
                key = vals[0].strip()
                val = vals[1].strip()
                # Set the value.
                o[key] = self.ConvertToVal(val)
            # Set the section dictionary
            opts[sec] = o
        # Output
        return opts
        
    # Apply a whole bunch of options
    def ApplyDict(self, opts):
        """Apply a whole dictionary of settings to the namelist
        
        :Call:
            >>> nml.ApplyDict(opts)
        :Inputs:
            *nml*: :class:`cape.namelist.Namelist`
                File control instance for :file:`fun3d.nml`
            *opts*: :class:`dict`
                Dictionary of namelist options
        :Versions:
            * 2015-10-16 ``@ddalle``: First version
        """
        # Loop through major keys.
        for sec in opts.keys():
            # Check it it's a section
            if sec not in self.SectionNames:
                # Initialize the section.
                self.SectionNames.append(sec)
                # Add the lines
                self.Section[sec] = [
                    ' &%s\n' % sec,
                    ' /\n', '\n'
                ]
            # Loop through the keys in this subnamelist/section
            for k in opts[sec].keys():
                # Set the value.
                self.SetVar(sec, k, opts[sec][k])
    
    
    # Conversion
    def ConvertToVal(self, val):
        """Convert a text file value to Python based on a series of rules
        
        :Call:
            >>> v = nml.ConvertToVal(val)
        :Inputs:
            *nml*: :class:`cape.namelist.Namelist`
                File control instance for :file:`fun3d.nml`
            *val*: :class:`str` | :class:`unicode`
                Text of the value from file
        :Outputs:
            *v*: :class:`str` | :class:`int` | :class:`float` | :class:`list`
                Evaluated value of the text
        :Versions:
            * 2015-10-16 ``@ddalle``: First version
            * 2016-01-29 ``@ddalle``: Added boolean shortcuts, ``.T.``
        """
        # Check inputs.
        if type(val).__name__ not in ['str', 'unicode']:
            # Not a string; return as is.
            return val
        # Split to parts
        V = val.split()
        # Check the value.
        try:
            # Check the value.
            if ('"' in val) or ("'" in val):
                # It's a string.  Remove the quotes.
                return eval(val)
            elif val.lower() in [".false.", ".f."]:
                # Boolean
                return False
            elif val.lower() in [".true.", ".t."]:
                # Boolean
                return True
            elif len(V) == 0:
                # Nothing here.
                return None
            elif lev(V) == 1:
                # Convert to float/integer
                return eval(val)
            else:
                # List
                return [eval(v) for v in V]
        except Exception:
            # Give it back, whatever it was.
            return val
            
    # Conversion to text
    def ConvertToText(self, v):
        """Convert a value to text to write in the namelist file
        
        :Call:
            >>> val = nml.ConvertToText(v)
        :Inputs:
            *nml*: :class:`cape.namelist.Namelist`
                File control instance for :file:`fun3d.nml`
            *v*: :class:`str` | :class:`int` | :class:`float` | :class:`list`
                Evaluated value of the text
        :Outputs:
            *val*: :class:`str` | :class:`unicode`
                Text of the value from file
        :Versions:
            * 2015-10-16 ``@ddalle``: First version
        """
        # Get the type
        t = type(v).__name__
        # Form the output line.
        if t in ['str', 'unicode']:
            # Force quotes
            return '"%s"' % v
        elif t in ['bool'] and v:
            # Boolean
            return ".true."
        elif t in ['bool']:
            # Boolean
            return ".false."
        elif type(v).__name__ in ['list', 'ndarray']:
            # List (convert to string first)
            V = [str(vi) for vi in v]
            return " ".join(V)
        else:
            # Use the built-in string converter
            return str(v)
        
        
# class Namelist

        
