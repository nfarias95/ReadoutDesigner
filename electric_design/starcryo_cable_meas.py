import numpy as np
import csv
from matplotlib import pyplot as plt
from scipy.constants import mu_0
from scipy.optimize import curve_fit
pi = np.pi

from plot_parameters import *

#data_folder = "C:/Users/nicol/Documents/00Research/Data/Dunk Probe/starcryo_cable/date_20230920_19mm_2000um/"
#data_files = np.array(["WARM01.csv", "WARM02.csv", "COLD03.csv", "COLD04.csv", "COLD05.csv"])
    
# data_folder = "C:/Users/nicol/Documents/00Research/Data/Dunk Probe/starcryo_cable/date_20240519_calibration_board/"
# data_files = np.array([ "20240519_70_3.csv", "20240519_4_3.csv"])    
data_folder = "C:/Users/nicol/Documents/00Research/Data/Dunk Probe/starcryo_cable/date_29240521_45mm_2000um/"
data_files = np.array([  "20240521_4_1.csv"])    
labels = np.array([ "4 K"])

def main():
    
    print("Hello. Let's look at the VNA data")
    plot_vna_measurement(data_folder, data_files, labels)
    
    #compare_inductance_formulas()
    
    # attempt of model         
    model_inductance()     
    

    plt.show()
    print("The end")
    

def compare_inductance_formulas():
    lengths = np.linspace(15e-3, 50e-3, 3)
    gap = 5e-6
    w = 200e-6
    s = 5e-6 + w
    t = 5e-6
    
    L1 = mu_0/(2*pi) * lengths * ( np.log(s/(w+t)) +3/2)
    
    L2 = mu_0 / np.pi * np.arccosh(s/w) * lengths
    
    print(L1)
    print(L2)
    
    plt.figure(3)
    plt.plot(lengths, L1, label="L1", linestyle="--")
    plt.plot(lengths, L2, label="L2", linestyle="-.")
    plt.legend()
    
def model_inductance():
    """
    Assume an inductance model and take a reference value
    at one of the geometries
    I'll pick the geometry of 19 mm length and 350 um width
    """

    res_freqs = np.array([3.7e6, 2.0e6, 2.3e6, 1.9e6]) # Resonant frequencies  # y data
    res_freq_err = 0.05e6
    labels = np.array(["calibration", "l=19mm w=350um", "l=19 mm w=350um", "l=45 mm w=300um"])
    lengths = np.array([0, 17.1e-3, 17.1e-3, 40.5e-3]) #np.array([0, 19e-3, 19e-3, 45e-3]) # [m]
    widths = np.array([1, 350e-6, 2000e-6, 2000e-6]) # [m]
    gap=5e-6
    L_over_L_ref = get_inductance_factors(lengths, widths, ref_length=17.1e-3, ref_width=350e-6, gap=gap) # x data
    
    
    # Use initial guesses to help curve fit 
    L_ref_guess = 1e-9 # H
    C_guess = 3.1e-6 # F
    L_wb_guess = 1e-9 # H
    initial_guesses = [L_ref_guess, C_guess, L_wb_guess]
    
    # Run fit 
    popt, pcov = curve_fit(model_res_freq, L_over_L_ref, res_freqs, p0=initial_guesses)
    
    perr = np.sqrt(np.diag(pcov))
    print("Parameter values:", popt)
    print("Parameter uncertainties:", perr)
    
    L_ref_fit = popt[0]
    C_fit = popt[1]
    L_wb_fit = popt[2]
    
    # Print things
    print(L_over_L_ref)
    print("Fit results: ")
    print("L_ref: {:.2f} nH".format(L_ref_fit*1e9))
    print("L_wb: {:.2f} [nH]".format(L_wb_fit*1e9))
    print("C: {:.2f} [muF]".format(C_fit*1e6))
    
    # plot fit
    L_to_plot_fit = np.linspace(0, 2.5e-9, 10 )
    fr_fit = model_res_freq(L_to_plot_fit/L_ref_fit, L_ref_fit, C_fit, L_wb_fit)
    
    plt.figure(2, figsize=FIG_SIZE)
    plt.plot(L_to_plot_fit*1e9, fr_fit/1e6, color='k', linestyle="--", label="fit")
    plt.scatter(L_over_L_ref*L_ref_fit*1e9, res_freqs/1e6, label="$x \ L_{ref}$")
    plt.errorbar(L_over_L_ref*L_ref_fit*1e9, res_freqs/1e6, yerr=res_freq_err/1e6, fmt='o', marker="o", capsize=5)
    plt.xlabel("Inductance [nH]")
    plt.ylabel("Resonant frequency [MHz]")
    plt.grid()
    #plt.title("Fit results: L_ref = {:.2f} nH , C={:.2f} muF, L_wb={:.2f} nH".format(L_ref_fit*1e9, C_fit*1e6, L_wb_fit*1e9))
    plt.legend()
    
    print("Inductances: ")
    print(L_over_L_ref*L_ref_fit*1e9)
    
    # Comparison to expected values?
    s_array = gap + widths
    L_array_expected = mu_0 / np.pi * np.arccosh( np.divide(s_array, widths) ) * lengths
    print("Expected: ")
    print(L_array_expected*1e9, "\n\n\n")
    
    # Calculate uncertainty based on how much things were changing at the lab
    C_70K_sigma = np.std([3.1, 3.2, 3.3])*1e-6 # F
    Lwb_70K_sigma = np.std([2.4, 2.3])*1e-9 # nH
    fr_sigma = 0.05e6 # Hz
    
    L_sigma = np.sqrt( \
        ( C_70K_sigma * 1/(C_fit**2* res_freqs**2 * (2*pi)**2 ) )**2 + \
        ( fr_sigma*2/(C_fit*res_freqs**3*(2*pi)**2) )**2 + \
        ( Lwb_70K_sigma)**2 \
    )
    

    print("Inductances: ")
    print("L      :", L_over_L_ref*L_ref_fit*1e9)
    print("L sigma: ", L_sigma*1e9)
    
def model_res_freq(inductance_factor, L_ref, C, L_wb):
    """
    Model of the resonant frequency of a circuit with a capacitor, an inductor 
    and a wirebond

    Args:
        inductance_factor (_type_): a factor which multiplies the reference inductance [unitless]
        L_red (_type_): a reference inductance [H]
        C (_type_): capacitance [F]
        L_wb (_type_): [H] wire bond inductance
    """
    
    fr = 1/(2*pi) * 1/np.sqrt((C*L_wb + C*inductance_factor*L_ref))
    
    return fr

def get_inductance_factors(lengths, widths, ref_length=19e-3, ref_width=350e-6, gap=5e-6):
    """    
    Get the factor on how much the inductance should change
    in comparison to a reference cable

    Args:
        lengths (_type_): numpy array of lengths [m]
        widths (_type_): numpy array of widths [m]
        ref_length (_type_, optional): reference trace length [m]. Defaults to 19e-3.
        ref_width (_type_, optional): Reference trace width [m]. Defaults to 350e-6.
        gap (_type_, optional): Gap between traces [m]. Defaults to 5e-6.
    """
    # Calculate inductance of reference geometry
    s_ref = gap + ref_width
    L_ref =  mu_0 / np.pi * np.arccosh(s_ref/ref_width) * ref_length
    
    # calculate inductance of different geometries
    s_array = gap + widths
    L_array = mu_0 / np.pi * np.arccosh( np.divide(s_array, widths) ) * lengths
    
    L_over_L_ref = L_array/L_ref
    
    return L_over_L_ref
  


def plot_vna_measurement(data_folder, data_files, labels):
    """
    Function to plot the resonant frequency measured with the VNA

    Args:
        data_folder: folder where data is located
        data_files: array with names of files to be open
        labels: description of each file
    """
    
    for df, data_file in enumerate(data_files):
        
        filepath = data_folder+data_file
        
        # initialize arrays
        freqs = np.array([])
        S11 = np.array([])
        
        # opening the CSV file
        with open(filepath, mode ='r') as file:
            # reading the CSV file
            csvFile = csv.reader(file)
    
            # displaying the contents of the CSV file
            line_counter = 0
            lines_to_skip = 17
            for line in csvFile:
                if line_counter > lines_to_skip: # skip the headers
                    # ignore last file
                    if len(line) >1:
                        freqs = np.append(freqs, float(line[0]) ) # frequency in Hz
                        S11 = np.append(S11, float(line[1]) ) # S11 in dB
                line_counter = line_counter + 1

        plt.figure(1, figsize=FIG_SIZE)
        plt.scatter(freqs/1e6, S11, label=labels[df], alpha=0.5)
        plt.xlabel("Frequency [MHz]")
        plt.ylabel("S21 [dB]")
        plt.legend()
        plt.grid(True)

if __name__ == "__main__":
    main()