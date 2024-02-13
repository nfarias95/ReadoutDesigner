"""
Circuit relevant functions here
"""

import numpy as np
from matplotlib import pyplot as plt
pi = np.pi

# ---------------------------------------------------------
# Resonant Frequency Stuff
# ---------------------------------------------------------

def find_resonant_freq(Z_array:np.complex, freq_array:np.ndarray, show_plot:bool=False):
    """Function to find the resonant frequency given an array of impedances and corresponding frequencies

    Args:
        Z (np.complex): array of impedances
        freq_array (ndarray):array of frequencies
        show_plot(bool) : show a plot of frequency vs Z
    Returns:
        f_res (float):  the resonant frequency in Hertz
    """

    # resonant frequency occurs at minimum impedance
    index = np.argmin(Z_array)
    f_res = freq_array[index]
    
    if show_plot:
        plt.figure(1)
        plt.plot(freq_array, Z_array)
        plt.xlabel("Frequency [Hz]")
        plt.ylabel("Impedance [Ohm]")
        plt.grid()

    return f_res


def find_LC_resonant_frequency(L:float, C:float):
    """Function to get the resonant frequency of a simple LC circuit

    Args:
        L (float): inductance (Henry)
        C (float): capacitance (Farads)

    Returns:
        f_res(float): resonant frequency
    """
    f_res = 1/(2*pi * np.sqrt(L*C))
    return f_res

def get_C_from_bias_freq_and_L(freq_array:np.ndarray, L:float):
    """Function to calculate desired capacitances of resonators given the bias frequency and the inductance
    
    resonant frequency: f_res = 1/( 2*pi * sqrt(L*C))
    f_res^2 = 1/(4*pi^2 * L*C)
    C = 1/(4*pi^2 *L) * 1/f_res^2
    

    Args:
        freq_array (np.ndarray): bias frequency array
        L (float): inductance of resonator

    Returns:
        C_array(np.ndarray): Capacitance array
    """
    
    C_array = np.array( [ 1/( (2*pi*f)**2 * L) for f in freq_array ] )
    
    return C_array

# ---------------------------------------------------------
# BASIC STUFF
# ---------------------------------------------------------

def get_voltage_divider_factor(Z1:float, Z2:float):
    """Function to calculate the ratio of Vtotal that is going into Z1 when Z1 and Z2 are connected
    in series. Typically I'd think of this as being two resistors but I guess this could be anything
    Meaning: |Vout| = |Vin| * ratio_mag

    Args:
        Z1 (float): impedance 1
        Z2 (float): impedance 2
    """
    
    complex_ratio = Z1 / series(Z1, Z2)
    ratio_mag = np.amp(complex_ratio)
    ratio_phase = get_phase(complex_ratio)
    
    return ratio_mag, ratio_phase

def get_phase(Z:np.complex):
    """This function calculates the phase associated with an impedance

    Args:
        Z (np.complex): The complex impedance
    """
    
    phase:float = np.real(np.arctan(np.imag(Z) / np.real(Z))) 
    return phase

def series(Z1:np.complex, Z2:np.complex):
    """ This function returns the equivalent impedance in series

    Args:
        Z1 (np.complex): _description_
        Z2 (np.complex): _description_
    """
    Z_eq = Z1 + Z2 
    return Z_eq

def parallel(Z1:np.complex, Z2:np.complex):
    """This function returns the equivalent impedance in parallel

    Args:
        Z1 (np.complex): _description_
        Z2 (np.complex): _description_
    """
    Z_eq = 1/Z1 + 1/Z2
    return Z_eq

def ZC(C:float, omega:float):
    """This function returns the impedance of a capacitor of capacitance C at frequency omega

    Args:
        C (float): capacitance
        omega (float): frequency * 2*pi
    """
    Zc = 1/(1j*C*omega)
    return Zc

def ZL(L:float, omega:float):
    """This function returns the impedance of a inductor of inductance L at frequency omega

    Args:
        L (float): impedance
        omega (float): frequency * 2*pi
    """
    Zl = 1j*L*omega
    return Zl