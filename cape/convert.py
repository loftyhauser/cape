"""
Conversion tools for Cape
=========================

Perform conversions such as (alpha total, phi) to (alpha, beta).
"""

# Need NumPy for trig.
import numpy as np

# Conversions
slug = 14.593903
inch = 0.0254
ft = 12*inch

# Convert (total angle of attack, total roll angle) to (aoa, aos)
def AlphaTPhi2AlphaBeta(alpha_t, phi):
    """
    Convert total angle of attack and total roll angle to angle of attack and
    sideslip angle.
    
    :Call:
        >>> alpha, beta = cape.AlphaTPhi2AlphaBeta(alpha_t, beta)
    :Inputs:
        *alpha_t*: :class:`float` or :class:`numpy.array`
            Total angle of attack
        *phi*: :class:`float` or :class:`numpy.array`
            Total roll angle
    :Outputs:
        *alpha*: :class:`float` or :class:`numpy.array`
            Angle of attack
        *beta*: :class:`float` or :class:`numpy.array`
            Sideslip angle
    :Versions:
        * 2014-06-02 ``@ddalle``: First version
    """
    # Trig functions.
    ca = np.cos(alpha_t*np.pi/180); cp = np.cos(phi*np.pi/180)
    sa = np.sin(alpha_t*np.pi/180); sp = np.sin(phi*np.pi/180)
    # Get the components of the normalized velocity vector.
    u = ca
    v = sa * sp
    w = sa * cp
    # Convert to alpha, beta
    alpha = np.arctan2(w, u) * 180/np.pi
    beta = np.arcsin(v) * 180/np.pi
    # Output
    return alpha, beta
    
    
# Convert (total angle of attack, total roll angle) to (aoa, aos)
def AlphaBeta2AlphaTPhi(alpha, beta):
    """
    Convert total angle of attack and total roll angle to angle of attack and
    sideslip angle.
    
    :Call:
        >>> alpha_t, phi = cape.AlphaBeta2AlphaTPhi(alpha, beta)
    :Inputs:
        *alpha*: :class:`float` or :class:`numpy.array`
            Angle of attack
        *beta*: :class:`float` or :class:`numpy.array`
            Sideslip angle
    :Outputs:
        *alpha_t*: :class:`float` or :class:`numpy.array`
            Total angle of attack
        *phi*: :class:`float` or :class:`numpy.array`
            Total roll angle
    :Versions:
        * 2014-06-02 ``@ddalle``: First version
        * 2014-11-05 ``@ddalle``: Transposed alpha and beta in *w* formula
    """
    # Trig functions.
    ca = np.cos(alpha*np.pi/180); cb = np.cos(beta*np.pi/180)
    sa = np.sin(alpha*np.pi/180); sb = np.sin(beta*np.pi/180)
    # Get the components of the normalized velocity vector.
    u = cb * ca
    v = sb
    w = cb * sa
    # Convert to alpha, beta
    phi = np.arctan2(v, w) * 180/np.pi
    alpha_t = np.arccos(u) * 180/np.pi
    # Output
    return alpha_t, phi
    

# Sutherland's law (FPS)
def SutherlandFPS(T, mu0=None, T0=None, C=None):
    """Calculate viscosity using Sutherland's law using imperial units
    
    This returns
    
        .. math::
        
            \mu = \mu_0 \frac{T_0+C}{T+C}\left(\frac{T}{T_0}\right)^{3/2}
    
    :Call:
        >>> mu = SutherlandFPS(T)
        >>> mu = SutherlandFPS(T, mu0=None, T0=None, C=None)
    :Inputs:
        *T*: :class:`float`
            Static temperature in degrees Rankine
        *mu0*: :class:`float`
            Reference viscosity [slug/ft*s]
        *T0*: :class:`float`
            Reference temperature [R]
        *C*: :class:`float`
            Reference temperature [R]
    :Outputs:
        *mu*: :class:`float`
            Dynamic viscosity [slug/ft*s]
    :Versions:
        * 2016-03-23 ``@ddalle``: First version
    """
    # Reference viscosity
    if mu0 is None: mu0 = 3.58394e-7
    # Reference temperatures
    if T0 is None: T0 = 491.67
    if C  is None: C = 198.6
    # Sutherland's law
    return mu0 * (T0+C)/(T+C) * (T/T0)**1.5
    
# Sutherland's law (MKS)
def SutherlandMKS(T, mu0=None, T0=None, C=None):
    """Calculate viscosity using Sutherland's law using SI units
    
    This returns
    
        .. math::
        
            \mu = \mu_0 \frac{T_0+C}{T+C}\left(\frac{T}{T_0}\right)^{3/2}
    
    :Call:
        >>> mu = SutherlandMKS(T)
        >>> mu = SutherlandMKS(T, mu0=None, T0=None, C=None)
    :Inputs:
        *T*: :class:`float`
            Static temperature in degrees Rankine
        *mu0*: :class:`float`
            Reference viscosity [kg/m*s]
        *T0*: :class:`float`
            Reference temperature [K]
        *C*: :class:`float`
            Reference temperature [K]
    :Outputs:
        *mu*: :class:`float`
            Dynamic viscosity [kg/m*s]
    :Versions:
        * 2016-03-23 ``@ddalle``: First version
    """
    # Reference viscosity
    if mu0 is None: mu0 = 1.716e-5
    # Reference temperatures
    if T0 is None: T0 = 273.15
    if C  is None: C = 110.33333
    # Sutherland's law
    return mu0 * (T0+C)/(T+C) * (T/T0)**1.5
    

# Get Reynolds number
def ReynoldsPerFoot(p, T, M, R=None, gam=None, mu0=None, T0=None, C=None):
    """Calculate Reynolds number per foot using Sutherland's Law
    
    :Call:
        >>> Re = ReynoldsPerFoot(p, T, M)
        >>> Re = ReynoldsPerFoot(p, T, M, gam=None, R=None, T0=None, C=None)
    :Inputs:
        *p*: :class:`float`
            Static pressure [psf]
        *T*: :class:`float`
            Static temperature [R]
        *M*: :class:`float`
            Mach number
        *R*: :class:`float`
            Gas constant [ft^2/s^2*R]
        *gam*: :class:`float`
            Ratio of specific heats
        *mu0*: :class:`float`
            Reference viscosity [slug/ft*s]
        *T0*: :class:`float`
            Reference temperature [R]
        *C*: :class:`float`
            Reference temperature [R]
    :Outputs:
        *Re*: :class:`float`
            Reynolds number per foot
    :Versions:
        * 2016-03-23 ``@ddalle``: First version
    """
    # Gas constant
    if R is None: R = 1716.0
    # Ratio of specific heats
    if gam is None: gam = 1.4
    # Calculate density
    rho = p / (R*T)
    # Sound speed
    a = np.sqrt(gam*R*T)
    # Velocity
    U = M*a
    # Calculate viscosity
    mu = SutherlandFPS(T, mu0=mu0, T0=T0, C=C)
    # Reynolds number per foot
    return rho*U/mu
    
# Get Reynolds number
def ReynoldsPerMeter(p, T, M, R=None, gam=None, mu0=None, T0=None, C=None):
    """Calculate Reynolds number per meter using Sutherland's Law
    
    :Call:
        >>> Re = ReynoldsPerFoot(p, T, M)
        >>> Re = ReynoldsPerFoot(p, T, M, gam=None, R=None, T0=None, C=None)
    :Inputs:
        *p*: :class:`float`
            Static pressure [Pa]
        *T*: :class:`float`
            Static temperature [K]
        *M*: :class:`float`
            Mach number
        *R*: :class:`float`
            Gas constant [m^2/s^2*R]
        *gam*: :class:`float`
            Ratio of specific heats
        *mu0*: :class:`float`
            Reference viscosity [kg/m*s]
        *T0*: :class:`float`
            Reference temperature [K]
        *C*: :class:`float`
            Reference temperature [K]
    :Outputs:
        *Re*: :class:`float`
            Reynolds number per foot
    :Versions:
        * 2016-03-24 ``@ddalle``: First version
    """
    # Gas constant
    if R is None: R = 287.0
    # Ratio of specific heats
    if gam is None: gam = 1.4
    # Calculate density
    rho = p / (R*T)
    # Sound speed
    a = np.sqrt(gam*R*T)
    # Velocity
    U = M*a
    # Calculate viscosity
    mu = SutherlandMKS(T, mu0=mu0, T0=T0, C=C)
    # Reynolds number per foot
    return rho*U/mu

# Calculate pressure from Reynolds number
def PressureFPSFromRe(Re, T, M, R=None, gam=None, mu0=None, T0=None, C=None):
    """Calculate pressure from Reynolds number
    
    :Call:
        >>> p = PressureFPSFromRe(Re, T, M)
        >>> p = PressureFPSFromRe(Re, T, M, R=None, gam=None, **kw)
    
    :Inputs:
        *Re*: :class:`float`
            Reynolds number per foot
        *T*: :class:`float`
            Static temperature [R]
        *M*: :class:`float`
            Mach number
        *R*: :class:`float`
            Gas constant [ft^2/s^2*R]
        *gam*: :class:`float`
            Ratio of specific heats
        *mu0*: :class:`float`
            Reference viscosity [slug/ft*s]
        *T0*: :class:`float`
            Reference temperature [K]
        *C*: :class:`float`
            Reference temperature [K]
    :Outputs:
        *p*: :class:`float`
            Static pressure [psf]
    :Versions:
        * 2016-03-24 ``@ddalle``: First version
    """
    # Gas constant
    if R is None: R = 1716.0
    # Ratio of specific heats
    if gam is None: gam = 1.4
    # Sound speed
    a = np.sqrt(gam*R*T)
    # Velocity
    U = M*a
    # Viscosity
    mu = SutherlandFPS(T, mu0=mu0, T0=T0, C=C)
    # Pressure
    return Re*mu*R*T/U

# Calculate pressure from Reynolds number
def PressureMKSFromRe(Re, T, M, R=None, gam=None, mu0=None, T0=None, C=None):
    """Calculate pressure from Reynolds number
    
    :Call:
        >>> p = PressureMKSFromRe(Re, T, M)
        >>> p = PressureMKSFromRe(Re, T, M, R=None, gam=None, **kw)
    
    :Inputs:
        *Re*: :class:`float`
            Reynolds number per foot
        *T*: :class:`float`
            Static temperature [K]
        *M*: :class:`float`
            Mach number
        *R*: :class:`float`
            Gas constant [m^2/s^2*R]
        *gam*: :class:`float`
            Ratio of specific heats
        *mu0*: :class:`float`
            Reference viscosity [kg/m*s]
        *T0*: :class:`float`
            Reference temperature [K]
        *C*: :class:`float`
            Reference temperature [K]
    :Outputs:
        *p*: :class:`float`
            Static pressure [Pa]
    :Versions:
        * 2016-03-24 ``@ddalle``: First version
    """
    # Gas constant
    if R is None: R = 287.0
    # Ratio of specific heats
    if gam is None: gam = 1.4
    # Sound speed
    a = np.sqrt(gam*R*T)
    # Velocity
    U = M*a
    # Viscosity
    mu = SutherlandMKS(T, mu0=mu0, T0=T0, C=C)
    # Pressure
    return Re*mu*R*T/U
# def Pressure MKSFromRe

