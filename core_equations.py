# SCRIPT WITH SOME CORE EQUATIONS

import numpy as np

def calculate_responsivity(V_bias, loop_gain, tau=None, omega=None, ac=True):
    """
    Function to calculate the responsivity of a bolometer

    Args:
        V_bias (_type_): _description_
        loop_gain (_type_): _description_
        tau (_type_): _description_
        omega (_type_): _description_
        ac (bool, optional): _description_. Defaults to True.
    """
    
    if (omega is None) or (tau is None):
        # just assume a very fast detector
        omega = 1
        tau = omega/100
    
    if ac:
        S_I = np.sqrt(2)/V_bias * (loop_gain/(loop_gain + 1)) * (1/(1 + omega*tau))
    
    else:
        S_I = 1/V_bias * (loop_gain/(loop_gain + 1)) * (1/(1 + omega*tau))
        
    return S_I