# SCRIPT WITH SOME CORE EQUATIONS

import numpy as np

def calculate_responsivity(V_bias, loop_gain, tau=None, omega=None, ac=True, R_TES=1, R_s=0):
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
        prefactor = np.sqrt(2)    
    else:
        prefactor = 1
    
    V_TES = V_bias * R_TES / (R_TES + R_s) # =V_bias if there are no stray impedances
    
    # Derived in Tucker's thesis section 5.1 and re-arranged in Josh's thesis
    # I NEED TO CHECK HOW THE LAST TERM WHICH DEPENDS ON TAU GETS AFFECTED
    # I DON'T TRUST TUCKER'S DERIVATION JUST YET
    S_I = prefactor/V_TES * \
        (loop_gain * (R_TES) /( loop_gain*(R_TES - R_s) + (R_TES + R_s))) * (1/(1 + omega*tau))
        
    return S_I