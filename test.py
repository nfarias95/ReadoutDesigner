"""
script to test stuff
"""
    
import numpy as np
from matplotlib import pyplot as plt

from circuits_functions import ZL, ZC, find_LC_resonant_frequency, series, find_resonant_freq, get_phase

pi = np.pi

def main():
    print("\nWelcome! This program calculates various readout properties!")

    # config file
    # what would it have?
    # Rtes, L, Cs?
    
    # calculate resonances or capacitances? given resonance freqs calculate capacitances and vice versa?
    
    
    print("type: ", type(np.array([0, 1])))
    
    C = 20e-9 # farad
    R = 2 # 1 ohm
    L = 60e-9 # henry
    
    omegas = np.linspace(4e6*2*pi, 6e6*2*pi, 1000) # Hertz
    Z_mag_tot = np.empty(len(omegas), dtype=complex)
    Z_phase_tot = np.empty(len(omegas), dtype=float)
    
    i=0
    for omega in omegas:
        Zl = ZL(L, omega)
        Zc = ZC(C, omega)
        Z_mag_tot[i] = np.abs( series(R, series(Zl, Zc) ) )
        Z_phase_tot[i] = get_phase( series(R, series(Zl, Zc) ) )
        
        i=i+1
    
    
    print("Phase: ")
    print(Z_phase_tot * 180/pi)
    
    f_res = find_resonant_freq(Z_mag_tot, freq_array=omegas/(2*pi), show_plot=True)
    
    print("Resonant frequency: ", f_res/1e6)
    
    
    # calculate cross talk based on Josh's paper
    
    # -----------------------------------
    print("the end. have a nice day. \n")
    plt.show()
    return 0


if __name__ == "__main__":
    main()