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
        # old: k_kapton_array = 1.8e-3 * T_array**1.15  # W / m / K  -- This is what Tucker used

        # Kapton Island Sim
        # geometrical properties
        thick =  0.00095 * 0.0254#12.5e-6 # m
        length = 25e-3 # m
        width = 2 * 10e-3 # m   -- assuming X sides
        area = thick * width
    
        # thermal properties
        alpha = 6.5e-3
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
    
def get_dissipated_heat(T0, T1, alpha, beta, gamma, n,  area, length):
    """Calculate dissipated heat given thermal conductance k=alpha*T^(beta+gamma*(T^n))

    Args:
        T_0 (_type_): cold temperature
        T_1 : warm temperature
        alpha (_type_): 
        beta (_type_): 
        gamma (_type_): 
        area (_type_): area of cross section of conductor
        length (_type_): length of conductor
    """
    # divide temperature into array
    T_array = np.linspace(T0, T1, 100) # array of temperature used to integrate G   
    
    # Get conductance    
    k_array = np.zeros(len(T_array))
    for tc, T in enumerate(T_array):
        k_array[tc] = alpha * T **(beta  + gamma * (T **(n)))
    
    # integrate conductance and calculate heat transfer
    k_integrated = np.trapz(k_array, x=T_array)
    Q = k_integrated * area / length 
    
    return Q

def get_kapton_thermal_conductivity(T:float):
    """
    FUNCTION IS BROKEN, FIX BEFORE USING
    Function to calculate the thermal conductivity of Kapton for a specific temperature
        
    based on: https://trc.nist.gov/cryogenics/materials/Polyimide%20Kapton/PolyimideKapton_rev.htm
    data range: 4-300 K

    Args:
        T (float): temperature
    """
    
    # units: W/(m*K)
    a = 5.73101	
    b= -39.5199	
    c = 9.9313	
    d = -83.8572
    e = 50.9157	
    f = -17.9835
    g = 3.42413
    h = -0.27133
    i = 0
    
    kappa = 10**(a + b*(np.log10(T)) + c*np.log10(T)**2 + d*np.log10(T)**3 + e*np.log10(T)**4 + f*np.log10(T)**5 +\
        g**np.log10(T)**6 + h*np.log10(T)**7 + i*np.log10(T)**8)
    
    
    return kappa


if __name__ == "__main__":
    main()