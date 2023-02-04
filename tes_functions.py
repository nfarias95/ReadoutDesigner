# functions related to tes performance

import numpy as np

def get_loop_gain(Pbias:float, alpha:float, g:float, Tc:float, omega:float, tau0:float):
    """Function to calculate the loop gain of a detector

    Args:
        Pbias (float): bias power
        alpha (float): T/R * dR/DT = dlog(R)/dlog(T)
        g (float): little thermal conductance
        Tc (float): critical temperature of superconductivity
        omega (float): frequency of AC current
        tau0 (float) : time constant of detector without feedback
    """
    
    Lopen = Pbias * alpha / (g * Tc)
    
    L = Lopen / (1 + 1j*omega*tau0)
    
    return L

def get_responsivity(Vbias:float, L:float, omega:float, tau:float, AC:bool=True):
    """Function to calculate responsivity of detector

    Args:
        Vbias (float): Voltage bias
        L (float): Loop gain
        omega (float): frequency of AC current
        tau (float): time constant of detector
        AC (bool, optional): whether or not system has Alternating Current. True by default
    """
    
    if AC:
        Stilda = 1/np.sqrt(2)
    else:
        Stilda = 1
        
    S = -Stilda / Vbias * L/(1+L) * 1/(1+1j*omega*tau)
    
    return S