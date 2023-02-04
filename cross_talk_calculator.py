"""
    This script contains functions to calculate cross talk based on Joshua Montgomery's thesis
    Author: Nicole Farias
    
"""

import yaml
import numpy as np
from matplotlib import pyplot as plt
from circuits_functions import series, parallel, get_C_from_bias_freq_and_L
from load_data_functions import read_yaml_file

pi = np.pi


def local_main():
    """
    local main to test functionality of cross talk functions
    """
    
    f_bias_spacing = 'logarithmic' #'linear' # spacing between channels. Options: 'linear' , 'logarithmic' (not yet available)
    
    print("\n\n ------ Welcome ------ \nLet's calculate cross talk!")
    
    # LOAD DATA
    # load configuration file    
    d = read_yaml_file('config.yaml')
    R_tes = d['R_tes_normal'] * d['R_frac']
    
    
    print("data: ", d)
    
    # create bias frequency array
    f_bias_array = create_f_bias_array(d['freq_bias_range'], d['mux_factor'], f_bias_spacing)
    print("f_bias_array: ", f_bias_array)
    
    # get array of capacitor values
    C_array = get_C_from_bias_freq_and_L(f_bias_array, d['L_res'])
    #print("C array: ", C_array)
    
    # get V_bias -- what is a good number for it?????
    V_bias_array = np.ones(d['mux_factor'])
    
    # INITIALIZE ARRAYS TO STORE DATA
    LCX_array = np.zeros(d['mux_factor']) # array of leakage current
    ctf_LCX_array = np.zeros(d['mux_factor']) # array of cross talk fraction (leakage current)
    
    
    # CALCULATE THINGS FOR EACH CHANNEL
    for channel in range(0, d['mux_factor']-1):
        # get frequency
        omega = 2*pi*f_bias_array[channel]
        
        # get voltage bias at frequency 'i'
        V_bias = V_bias_array[channel]
            
        # PARASITICS
        Z_com = omega * d['L_stray'] * 1j   
        
        # ON RESONANCE:
        C_i = C_array[channel] # capacitance of on-resonance circuit
        Z_i = R_tes + d['r_s'] + 1j * omega * d['L_res'] + 1/(1j * omega * C_i) + Z_com
        
        
        # GET THE OFF RESONANCE COMPONENTS:
        # get impedance
        C_n = C_array[channel+1]  # capacitance of neighbor (pick the one to the right of it for simplicity, it could be +1  or - 1.
        Z_n = R_tes + d['r_s'] + 1j * omega * d['L_res'] + 1/(1j * omega * C_n) + Z_com

        # Calculate the leakage function
        # LCX_array[channel] = calculate_leakage_function(omega, V_bias, Z_com, R_tes, d['L_res'], C_n, d['r_s'])
                
        # Calculate the leakage current cross talk fraction
        ctf_LCX = calculate_cross_talk_fraction_LCX(Z_i, Z_n, Z_com)
        
        ctf_LCX_array[channel] = abs(ctf_LCX)

    
    # plt.figure(1)
    # plt.plot(f_bias_array[0:-1]/1e6, LCX_array[0:-1])
    # plt.ylabel('Leakage Current (uncalibrated units)')
    # plt.xlabel("Bias frequency [MHz]")
    
    plt.figure(2)
    plt.plot(f_bias_array[0:-1]/1e6, ctf_LCX_array[0:-1] * 100)
    plt.ylabel('Cross talk fraction (leakage current) [%]')
    plt.xlabel('Bias frequency [MHz]')
    
    
    print("The end")
    plt.show()
    return 0

def calculate_cross_talk_fraction_LCX(Z_i:float, Z_n:float, Z_com:float=0.0):
    """
    Function to calculate the approximate cross talk fraction: dI_i,n,LCX/dI_i,signal
    approximation: delta R_tes,n = delta R_tes,i

    Args:
        Z_i (float): impedance of on-resonance TES+resonator 
        Z_n (float): impedance of closest off-resonance neighbor (TES + resonator)
        Z_com (float, optional): impedance common to all channels. Defaults to 0.0.
    """

    cross_talk_fraction = ( ( Z_i + Z_com)/(Z_n + Z_com) ) **2
    
    return cross_talk_fraction

def calculate_leakage_function(omega, V_bias, Z_com, R_tes, L_res:float, C_n:np.ndarray, r_s:float=0 ):
    """
    Function to calculate the leakage function :  [dI_i/dR_tes,n]_LCX
    TES within off-resonance leg fluctuates in resistance -> modulate the amplitude of the leakage current
    Inputs:
        omega: frequency
        V_bias : voltage bias at frequency 'i' [V]
        Z_com : common impedance [ohms]
        R_tes : resistance of TES
        L_res : inductance of resonator
        C_n : capacitance of neighbor resonator
        r_s : stray impedance, set to zero by default
    """
    
    leakage_current = - V_bias / ( ( R_tes + r_s + 1j * omega * L_res + 1/(1j * omega * C_n) + Z_com)**2 )
    
    return leakage_current


def create_f_bias_array(freq_bias_range, mux_factor: int =40, f_bias_spacing: str='linear'):
    """Function to create an array of frequency bias

    Args:
        freq_bias_range (_type_): array with range of bias frequency [start, end]
        mux_factor (int) : number of channels -- set to 40 by default
        f_bias_spacing (str): type of spacing between channels (ex: 'linear', 'logarithmic')
    """
    
    if f_bias_spacing == 'linear':        
        f_bias_array = np.linspace(freq_bias_range[0], freq_bias_range[1], mux_factor)
        #print("f_bias: ", f_bias_array)
    
    elif f_bias_spacing == "logarithmic":
        print("\n\n hey yo")
        #logspace = np.logspace(np.log(freq_bias_range[0]), np.log(freq_bias_range[1]), mux_factor)
        #print("logspace: ", logspace)
        f_bias_array = np.geomspace(freq_bias_range[0], freq_bias_range[1], mux_factor)
    else:
        print("sorry, I don't know how to calculate that yet")
        
    return f_bias_array

if __name__ == "__main__":
    local_main()