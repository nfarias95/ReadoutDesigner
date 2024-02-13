# this script is meant to auxiliate the design of magnetic shields for squids (or focal plane modules, but I'm focused on the squids)
# Author: Nicole Farias
# date created: 03/22/2023

import numpy as np
from matplotlib import pyplot as plt

phi_0 = 2.67e-15 # [Wb] flux quanta. Note: one Tesla = 1Wb/m^2

def main():
    
    # some values from Tijmen
    
    B_out = 28e-6 # [T] External magnetic field (estimated from Kazu from cooler) 
    
    sq_eff_area = 2e-12 # [m^2] squid effective area (from Note 48a, I don't know what this is)
    
    # this implies a sensitivity of 0.1/X Phi_0/Gauss -- I don't really understand where this comes from
    
    ref_flux_burden = 1e-6 # [A, rms] for a 24 uA/phi_0 SSAA
    ref_current = 24e-6 # [A]
    
    allow_flux_factor = ref_flux_burden/ref_current # rms. what factor of phi_0 is allowable
    
    print("Allowable flux ratio: ", allow_flux_factor)
    
    # conservatively give 10% of the flux burden to external fields
    contribution = 0.1 # how much of the flux burden would come from external fields (from 0 to 1)
    allow_flux = contribution * allow_flux_factor * phi_0 # allowable magnetic flux, [wB]
    allow_field = allow_flux * sq_eff_area # allowable field, [T]
    
    print("Allowable Flux: ", allow_flux, " Wb,  allowable field: ", allow_field, "  T")
    
    
    # cup geometry as described in Bergen 2016
    r = 13e-3/2 # [m] radius of opening
    l = 3*r # [m] length of cup
    l3 = l-6e-3 # [m] distance from opening to point of interest (say, squid location)
    
    St, SA = cup_shield_factor(r, l, l3)
    print("St: ", St, "  SA: ", SA)
    
    l_array = np.array([r, 1.5*r, 2*r, 2.5*r, 3*r, 3.5*r, 4*r])
    St_array = []
    SA_array = []
    
    for l in l_array:
        l3 = l - 6e-3
        
        St, SA = cup_shield_factor(r, l, l3)
        St_array.append(St)
        SA_array.append(SA)
    
    plt.figure(1)
    plt.plot(l_array*1e3, St_array)
    plt.xlabel("Cup length (mm)")
    plt.ylabel("Transverse Shield Factor")
    plt.title("Assuming squid is located 6 mm from end of cup")
    
    plt.figure(2)
    plt.plot(l_array*1e3, SA_array)
    plt.xlabel("Cup length (mm)")
    plt.ylabel("Axial Shield Factor")
    plt.title("Assuming squid is located 6 mm from end of cup")
        
    
    print("\n-----------\nThe end. \n---------\n\n")
    plt.show()

def cup_shield_factor(r:float, l:float, l3:float):
    """Function to calculate the shield factor of a cylindrical cup. 
    Returns both transverse and axial factors
    Assuming high permeability!
    Args:
        r (float): radius of opening
        l (float): length of cup
        l3 (float): distance from opening to point of interest (say, squid location)
    """
    # from Bergen et al 2016 - there is a factor of two between the results from
    # Mager and Bergen, I *think* because Mager assumes two open sides and Bergen assumes one open side
    
    St = 3.0 * np.exp(3.52 * l3/r) # transverse

    SA = 1 / (1.3 * np.sqrt(l/(2*r))) * np.exp(2.26 * l3/r)
    
    return St, SA

if __name__ == "__main__":
    main()