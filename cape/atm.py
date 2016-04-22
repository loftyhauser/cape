"""Atmosphere Model"""


# Basic numerics
import numpy as np
# Radius of earth [km]
RE = 6371.

# Unit conversions
inch = 0.0254
ft   = 12*inch
cm   = 0.01
km   = 1000.0
s    = 1.0
lbf  = 4.44822
lbm  = 0.453592
slug = (lbf*s^2/ft)
psf  = lbf / (ft*ft)
Btu  = 1055.0

# Enthalpy lookup table
href_h = np.array([
    0.0000e+00,
    2.5119e+05,
    5.0472e+05,
    7.7684e+05,
    7.9312e+05,
    1.3444e+06,
    1.6374e+06,
    1.9444e+06,
    2.2515e+06,
    2.5841e+06,
    2.9399e+06,
    3.3446e+06,
    3.9679e+06,
    4.6913e+06,
    5.7705e+06,
    6.6846e+06,
    7.7242e+06,
    8.5104e+06,
    8.8546e+06,
    9.6105e+06,
    1.0234e+07,
    1.0955e+07,
    1.1971e+07,
    1.3230e+07,
    1.4967e+07,
    1.7074e+07,
    1.9819e+07,
    2.2701e+07,
    2.5945e+07,
    2.9746e+07,
    3.3183e+07,
    3.6070e+07
])
href_T = np.arange(0, 8000, 250)

# Get atmosphere.
def atm76(h):
    """Return standard atmosphere parameters
    
    :Call:
        >>> S = atm76(h)
    :Inputs:
        *h*: :class:`float`
            Geometric altitude [km]
    :Outputs:
        *S*: :class:`cape.atm.State`
            Atmospheric state
        *S.T*: :class:`float`
            Temperature [K]
        *S.rho*: :class:`float`
            Static density [kg/m^3]
        *S.p*: :class:`float`
            Static pressure [N/m^2]
        *S.M*: :class:`float`
            Mach number
    :Versions:
        * 2015-07-04 ``@ddalle``: First version
    """
    # Geodetic altitude
    H = h / (1+h/RE)
    # Atmospheric constants
    R = 287.0
    c = g0 / R
    # Get scale height and base parameters.
    if H <= 11.0:
        # Troposphere
        T0 = 288.15
        p0 = 101325.0
        H0 = 0.0
        a  = -6.5
    elif H <= 20.0:
        # Tropopause
        T0 = 216.65
        p0 = 22263.064
        H0 = 11.0
        a  = 0.0
    elif H <= 32.0:
        # Lower stratosphere
        T0 = 216.65
        p0 = 5474.889
        H0 = 20.0
        a  = 1.0
    elif H <= 47.0:
        # Upper stratosphere
        T0 = 228.65
        p0 = 868.019
        H0 = 32.0
        a  = 2.8
    elif H <= 51.0:
        # Stratopause
        T0 = 270.65
        p0 = 110.960
        H0 = 47.0
        a  = 0.0
    elif H <= 71.0:
        # Lower mesosphere
        T0 = 270.65
        p0 = 66.9389
        H0 = 51.0
        a  = -2.8
    elif H <= 85.0:
        # Upper mesosphere
        T0 = 214.64
        p0 = 3.95642
        H0 = 71.0
        a  = -4.5
    else:
        # Mesopause
        T0 = 151.65
        p0 = 0.373384
        H0 = 85.0
        a = 0.0
        
    # Calculate state values
    if a == 0.0:
        # Temperature
        T = T0
        # Pressure
        p = p0 * np.exp(-1000*c*(H-H0)/T0)
    else:
        # Temperature
        T = T0 + a*(H-H0)
        # Pressure
        p = p0*(T/T0) ** (-1000.0*c/a)
        
    # Density
    rho = p / (R*T)
    
    # Output
    return State(p=p, rho=rho, T=T)
    
# Enthalpy
def get_h(T):
    """Get air specific enthalpy using a lookup table
    
    :Call:
        >>> h = get_h(T)
    :Inputs:
        *T*: :Class:`float`
            Temperature [K]
    :Outputs:
        *h*: :class:`float`
            Specific enthalpy [J/kg*K]
    :Versions:
        * 2016-03-03 ``@ddalle``: First version
    """
    # Interpolate
    return np.interp(T, href_T, href_h)
    
# Get temperature from enthalpy
def get_T(h):
    """Get temperature from specific enthalpy
    
    :Call:
        >>> T = get_T(h)
    :Inputs:
        *h*: :class:`float`
            Specific enthalpy [J/kg*K]
    :Outputs:
        *T*: :Class:`float`
            Temperature [K]
    :Versions:
        * 2016-03-03 ``@ddalle``: First version
    """
    # Interpolate
    return np.interp(h, href_h, href_T)
    
# Atmospheric state
class State(object):
    """Atmospheric state
    
    :Call:
        >>> S = atm.State(p=None, rho=None, T=None, V=0, gamma=1.4)
    :Inputs:
        *p*: :class:`float`
            Static pressure [Pa] (required)
        *rho*: :class:`float`
            Static density [kg/m^3] (required)
        *T*: :class:`float`
            Static temperature [K] (required)
        *V*: :class:`float`
            Velocity [m/s]
        *gamma*: :class:`float`
            Ratio of specific heats
    :Outputs:
        *S*: :class:`atm.State`
            Atmospheric state
        *S.p*: :class:`float`
            Static pressure [Pa]
        *S.rho*: :class:`float`
            Static density [kg/m^3]
        *S.T*: :class:`float`
            Static temperature [K]
        *S.R*: :class:`float`
            Normalized gas constant [J/kg-K]
        *S.V*: :class:`float`
            Velocity [m/s]
        *S.M*: :class:`float`
            Mach number
        *gamma*: :class:`float`
            Ratio of specific heats
        *a*: :class:`float`
            Sound speed [m/s]
    :Versions:
        * 2015-07-05 ``@ddalle``: First version
    """
    # Initialization method
    def __init__(self, p=None, rho=None, T=None, **kw):
        # Check required values.
        if p is None:
            raise ValueError("Static pressure 'p' is required.")
        if rho is None:
            raise ValueError("Static density 'rho' is required.")
        if T is None:
            raise ValueError("Static temperature 'T' is required.")
        # Check for velocity.
        V = kw.get('V', 0)
        # Ratio of specific heats
        gamma = kw.get('gamma', 1.4)
        # Calculate gas constant.
        R = p / (rho*T)
        # Calculate soundspeed
        a = np.sqrt(gamma*R*T)
        # Mach number
        M = V / a
        # Save quantities.
        self.p = p
        self.rho = rho
        self.T = T
        self.R = R
        self.a = a
        self.V = V
        self.M = M
        self.gamma = gamma
        
    # Convert to FPS
    def ConvertToFPS(self):
        """Convert state quantities to foot-pound-second units
        
        :Call:
            >>> S.ConvertToFPS()
        :Outputs:
            *S.p*: :class:`float`
                Static pressure [lbf/ft^2]
            *S.rho*: :class:`float`
                Static density [slug/ft^3]
            *S.T*: :class:`float`
                Static temperature [R]
            *S.M*: :class:`float`
                Mach number
            *S.a*: :class:`float`
                Sound speed [ft/s]
        :Versions:
            * 2016-04-22 ``@ddalle``: First version
        """
        # Conversions
        self.rho *= (slug/ft^3)
        self.p   *= (psf)
        self.T   *= (1.8)
        self.a   *= (ft/s)
        self.V   *= (ft/s)
# class State

