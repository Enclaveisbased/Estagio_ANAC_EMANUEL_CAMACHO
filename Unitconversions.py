import numpy as np
import scipy.constants as sc
from geopy.distance import geodesic
from geopy.point import Point




# Convert force units
def convforce(value, from_unit, to_unit):
    conversion_factors = {
        ('N', 'lbf'): 0.224809,
        ('lbf', 'N'): 4.44822,
        # Add other conversions if needed
    }
    return value * conversion_factors[(from_unit, to_unit)]

# Convert velocity units
def convvel(value, from_unit, to_unit):
    conversion_factors = {
        ('ft/s', 'kts'): 0.592484,
        ('kts', 'ft/s'): 1.68781,
        ('kts', 'm/s'): 0.514444,
        ('ft/s', 'm/s'): 0.3048,
        ('m/s', 'kts'): 1/0.514444,
        # Add other conversions if needed
    }
    return value * conversion_factors[(from_unit, to_unit)]

# Convert density units
def convdensity(value, from_unit, to_unit):
    conversion_factors = {
        ('kg/m^3', 'slug/ft^3'): 0.00194032,
        ('slug/ft^3', 'kg/m^3'): 515.378,
        # Add other conversions if needed
    }
    return value * conversion_factors[(from_unit, to_unit)]

# Convert pressure units
def convpres(value, from_unit, to_unit):
    conversion_factors = {
        ('psf', 'Pa'): 47.8803,
        ('Pa', 'psf'): 0.0209,
        # Add other conversions if needed
    }
    return value * conversion_factors[(from_unit, to_unit)]

# Convert angle units
def convang(value, from_unit, to_unit):
    if from_unit == 'rad' and to_unit == 'deg':
        return np.degrees(value)
    elif from_unit == 'deg' and to_unit == 'rad':
        return np.radians(value)
    else:
        raise ValueError(f"Unsupported angle conversion from {from_unit} to {to_unit}")

# Correct airspeed for compressibility
def correctairspeed(TAS, a, P, TAS_label, CAS_label):
    # CAS calculation from TAS
    return TAS / (1 + (P / 1000) * (1.0 / (2 * a * TAS**2)))**0.5

# Calculate dynamic pressure
def dpressure(TAS, rho):
    return 0.5 * rho * TAS[:, 0]**2



