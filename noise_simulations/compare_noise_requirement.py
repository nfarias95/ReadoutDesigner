import sys
import os
sys.path.append('C:/Users/nicol/Documents/00Research/PythonCode/ReadoutDesigner/')


import numpy as np
from matplotlib import pyplot as plt
#from plot_parameters import FONT_SIZE, LEGEND_SIZE, FONT,  figsize
from noise_simulations.noise_sims_from_Tucker.noise_formulas import NEP_g, NEP_ph, S_I

figsize=(10,8)
#%run ../utils/python_utils.py
from plot_parameters import *

np.set_printoptions(precision=2)

def main():
    print("hello")
    
    P_opt = 0.5e-12 # [W] optical power in detector
    R = 0.7 #[ohms] operating resistance
    
    # get readout NEP using Tijmen's way
    NEP_read_tij = get_requirement_Tijmen_way()
    
    # get readout NEP using Nicole's/Tucker's way
    P_sat = P_opt*2.5
    nep_read = NEP_read_tij #np.sqrt((nep_g**2 + nep_ph**2)*(1.1**2-1))
    rtes = R
    loopgain = 10
    si_0 = S_I(rtes, P_sat-P_opt, loopgain)
    print(si_0)
    
    P_el = P_sat - P_opt
    V = np.sqrt(P_el*R)
    si_1 = np.sqrt(2)/V * 1.0
    print(si_1)
    
    nei_read = nep_read*si_1
    print(nei_read)
    
    print("NEI [pA/sqrt(Hz)]: {:.2f}".format( nei_read *1e12 ))
    
    print("done.")
    
    
def get_requirement_Tijmen_way(P_opt = 0.5e-12, R = 0.7):
    """
    Inputs:
    P_opt: optical power in Watts
    R: operating resistance in Ohms
    
    
    NEP_read = np.sqrt(21)/11 * NEP_total
    
    P_el = 1.5 P_opt = V^2/R -> V = sqrt(P_opt * 1.5 * R)
    
    NEP = NEI /S_I = NEI * V / (excess responsivity * sqrt(2))
    
    where does excess responsivity comes from?
    
    NEP = np.sqrt(1.5 * P_opt * R) * NEI / (np.sqrt(2) * excess_S_I)
    """
    # Assume a readout NEI 
    NEI = 8.2e-12 # A/sqrt(Hz)
    excess_S_I = 1.2
    
    NEP = np.sqrt(1.5 * P_opt * R) * NEI / (np.sqrt(2) * excess_S_I)
    
    print("NEP [aW]: {:.2f}".format( NEP *1e18 ))
    
    return NEP
    
if __name__ == "__main__":
    main()