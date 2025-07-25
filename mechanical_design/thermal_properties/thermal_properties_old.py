"""
    This code calculates useful thermal properties
    
    2D case: 
    
    dQ = dT k(T) * Area / Length
    
    translates to:
    Q = k_integrated * area / length
    k_integrated = np.trapz(k_array, x=T_array)
    
"""

import numpy as np
# Simulation type
sim_type = "kapton_film" # can be "kapton_film", "carbon_fiber_strut"

def main():
    T0 = 0.112 # first temperature stage, Kelvin
    T1 = 0.405 # second temperature stage, Kelvin    

    if sim_type == "heat_strap":  
        length = 0.5 # m
        T1 = 0.450 # K
        T0 = 0.405 # K 

    if sim_type == "carbon_fiber_strut":
        # Carbon Struts following Keith's Note 067 version 1.0
        n_rods = 4 # number of rods in assembly
        length =  32e-3   #22.71e-3 # [m] based on CAD
        rod_OD = 0.7e-3 # [m]
        rod_ID = 0.3e-3 # [m]
        area = np.pi * ( (rod_OD/2)**2 - (rod_ID/2)**2 ) * n_rods
            
        # get thermal conductivity at each temperature differential
        alpha = 8.39e-3
        beta = 2.12
        gamma = -1.05
        n = 0.181
    
    elif sim_type == "kapton_film":
        # https://www.sciencedirect.com/science/article/pii/S0011227500000138
        # Kapton Island Sim
        # geometrical properties
        thick =  12.5e-6 #0.00095 * 0.0254#12.5e-6 # m
        length = 25e-3 # m
        width = 2 * 10e-3 # m   -- assuming 2 sides
        area = thick * width
    
        # thermal properties
        alpha = 6.5e-3
        beta = 1.0
        gamma = 0
        n = 0
      
    elif sim_type == "ubilex_film":
        # Ubilex Island Sim
        #https://www.sciencedirect.com/science/article/pii/S0011227500000138
        # geometrical properties
        thick =  0.00095 * 0.0254#12.5e-6 # m
        length = 25e-3 # m
        width = 2 * 10e-3 # m   -- assuming X sides
        area = thick * width
    
        # thermal properties
        alpha = 1.8e-3 # W/m K
        beta = 1.0
        gamma = 0
        n = 0  
    
      
    # get the heat dissipated across conductor
    Q = get_dissipated_heat(T0, T1, alpha, beta, gamma, n,  area, length)
   
    # Print results
    allowable_heat_per_module = 15 # nW
    allowable_heat_per_SQUID = 5 # nW
    print("Allowable heat leakage per module:  %.2f [nW] " %(allowable_heat_per_module))
    print("Allowable heat leakage per SQUID:   %.2f [nW]  " % (allowable_heat_per_SQUID))
    print("Simulated heat leakage:             %.2f [nW]           " %( Q * 1e9))

    print("\n----\nThe end")
    


if __name__ == "__main__":
    main()