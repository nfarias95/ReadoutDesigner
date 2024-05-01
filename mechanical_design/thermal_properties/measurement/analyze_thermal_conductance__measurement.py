"""
Code to calculate the thermal conductance of a material given
power and temperature data    

To do: 
check papers, see what's the best way of plotting your fit to the data.
Figure out a way of gettting the parasitic power. I'm thinking: estimate that from the P0 datapoint 
and assume constant for this range of temperatures.
We know T_hot and the material properties, we can then estimate A/L.

"""

import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
import csv

from thermal_properties import get_dissipated_heat

data_dir = "C:/Users/nicol/Documents/00Research/Data/Thermal Conductance/"
data_file = "kapton_island_thermal_conductance_data_spring_2024.csv"
FILE_PATH = data_dir + data_file

def main():
    # Experiment settings -- Double check these resistance!
    Rw = 97.6e3 #98.7e3  # Warm resistance [ohms] 
    Rc = 130#105 # cold resistor serving as heater [ohms]
    Rp = 140-Rc # parasitic resistance [ohms] - can double check
    
    # Expected parasitics
    Twire = 4 #[K] temperature where we clamp the wire
    length_wire = 0.4 #[m] # Very rough!
    # from Woodcraft 2010, NbTi
    alpha_wire = 0.027 ; beta_wire = 2 ; gamma_wire = 0 ; n_wire = 0 ; 
    wire_diameter = np.mean([0.097, 0.088, 0.104])*1e-3 # [m] # measured by Nicole
    area_wire = (wire_diameter ** 2) /4 * np.pi * 4 #(4 wires)
    
    # Material properties  - confirmed.
    thick = 0.00095 * 0.0254 # measured with micrometer. (25.4e-6: from email exchange with the company)
    length = 25e-3 # m
    width = 2 * 10e-3 # m   -- assuming X sides
    area = thick * width
    g = area/length
    print("g: ", g)
    
    # -- -READ THE DATA ---    
    V_out, T0, T1 = read_data_from_csv(path_to_file=FILE_PATH)
    
    # Get power dissipated by heater
    I_out = V_out / (Rw+ Rc+ Rp)
    P_heater = I_out**2 * Rc
    
    # get uncertainty
    sigma_Rw = np.std([97.2e3, 98.9e3, 101.1e3, 111.2e3, 96e3, 100.4e3])
    sigma_I_out = ((V_out ** 2)/(Rw+Rc+Rp)**2)*sigma_Rw
    sigma_P_heater = 2 * I_out * Rc * sigma_I_out
    
    print("Sigmas: ", sigma_Rw, sigma_I_out, sigma_P_heater)
    
    # print("P_heater: [nW]")
    # i=-1
    # for P in P_heater:
    #     print("Vout: {:.2f} , Iout: {:.2e} Pout: {:.2f}".format(V_out[i], I_out[i], P_heater[i]*1e9)) ; i=i+1
    
    # Estimate power from parasitics
    P_par_estimated = np.array([])
    for T in T1:
        P_par_estimated = np.append(P_par_estimated, get_dissipated_heat(T, Twire, alpha_wire, beta_wire, gamma_wire, n_wire, area_wire, length_wire))
    

    # fit data 
    params, cov = curve_fit(power_model, T1, P_heater/g)
    a = params[0] ; b = params[1] ; Ppar_fit = params[2] * g
    beta = b - 1
    alpha = a * (beta + 1)
    P_heater_over_g_fit = power_model(np.sort(T1), params[0], params[1], params[2])
    P_heater_fit = P_heater_over_g_fit * g

    # plt.figure(12)
    # plt.scatter(T1, P_heater/g, marker='x', color='k')
    # plt.plot(T1, P_heater_over_g_fit , color='k', linewidth=0.5)
    # note = "$Parasitic  Power$: {:.2f} nW  \na: {:.2e}   \nb: {:.2f}".format(Ppar_fit*1e9, a, b )
    # plt.annotate(note, [0.004, 4e-9])
    # plt.xlabel("T [K]")
    # plt.ylabel("$P_{heater}/g$ [W/m]")
    # plt.title("($P_{heater} + P_{par} )/g = a * (T^b - T_0^b$)")
    
    plt.figure(13)
    plt.scatter(T1, P_heater *1e9 , color='k')
    plt.errorbar(T1, P_heater*1e9, yerr = sigma_P_heater*1e9, fmt='none', color='k')
    plt.plot(np.sort(T1), P_heater_fit * 1e9, color='k', linewidth=0.5)
    note = "Fit parameters: \nParasitic  Power: {:.2f} nW  \na: {:.2e}   \nb: {:.2f}"\
        .format(Ppar_fit*1e9, a, b)
    plt.annotate(note, [0.71, 65])
    plt.xlabel("T [K]")
    plt.ylabel("$P_{heater}$ [nW]")
    plt.title("($P_{heater} + P_{par} )/g = a * (T^b - T_0^b$)")
    
    
    
    # --- See if we meet our requirements ----
    Tbath = 0.112 # Temperature of bath (detector stage) [K]
    Tsq = 0.405 # Temperature of squid stage {K}
    Pmax = 5e-9 # Watts
    P_expected_sq_k = get_dissipated_heat(Tbath, Tsq, alpha, beta, gamma=0, n=0, area=area, length=length)
    P_expected_sq = g * a * (Tsq**b - Tbath**b)
    
    print("expected dissipated power: {:.2f} nW , {:.2f} nW ".format(P_expected_sq_k*1e9, P_expected_sq*1e9))
    
    # ---- PRINT OUTPUT ----
    print("\n\n")
    print("Power from heater [nW]: " + str( [f"{x:.2f}" for x in P_heater*1e9]) )
    print("Power from parasitics (estimated): [nW] " , np.median(P_par_estimated)*1e9)    
    print("Parameters: \na: {:.2e}, b: {:.2f}, Ppar:{:.2f} nW".format(a, b, Ppar_fit*1e9))
    print("Parameters: \n$\\alpha$: {:.2e}, $\\beta$: {:.2f}".format(alpha, beta))
    print("\n")
    print("Maximum allowable power: {:.2f} nW  \
        \nSimulated power dissipation: 9.5 nW \
        \nExpected power dissipation:  {:.2f}  nW".format(Pmax*1e9, P_expected_sq*1e9))
    
    print("The end. \n\n")
    plt.show()


def read_data_from_csv(path_to_file:str):
    """function to read the voltage and temperature from a csv file.

    Args:
        path_to_file (str): _description_
    """
    V_out = np.array([])
    T1 = np.array([])
    T0 = np.array([])
    
    with open(path_to_file, mode='r') as file:
        csv_reader = csv.reader(file)
        # skip three header lines
        next(csv_reader)
        next(csv_reader)
        next(csv_reader)
    
        for row in csv_reader:
            V_out = np.append(V_out, float(row[3]))
            T0 = np.append(T0, float(row[4]))
            T1 = np.append(T1, float(row[5]))
            
    return V_out, T0, T1


def power_model(T1, a, b, Ppar_over_g):
    """Function that models the power dissipation P/g of a material 
    such that (P+Par)/g = a(T1^b - T0^b)
    Args:
        T1 (_type_): _description_
        a (_type_): _description_
        b (_type_): _description_
        Ppar (_type_): _description_
    """
    T0 = 0.242
    P_over_g = a * (T1**b - T0**b) - Ppar_over_g
    return P_over_g

def plot_power_vs_temperature(P, T0, T1):
    plt.figure(1)
    plt.scatter(P*1e9, T1)
    plt.xlabel("Power dissipated [nW]")
    plt.ylabel("$T_{hot}$ [K]")
    
    plt.figure(2)
    plt.scatter(P*1e9, T1-T0)
    plt.xlabel("Power dissipated [nW]")
    plt.ylabel("$T_{hot}-T_{cold}$ [K]")

def get_k_with_temp_dependency(P, A, L, T0, T1, Ppar=None):
    """Function to find k of the form
    k = alpha * T**(beta)

    Args:
        P (_type_): _description_
        A (_type_): _description_
        L (_type_): _description_
        T0 (_type_): _description_
        T1 (_type_): _description_
        Ppar : Parasitic power
    """
    
    plot_power_vs_temperature(P, T1, T0)


def get_k_no_temp_dependency(P, A, L, T0, T1):
    """Function to get the thermal conductance assuming no temperature dependency
        k = alpha 
    Args:
        P (_type_): Power dissipated
        A (_type_): Area
        L (_type_): Length
        T0 (_type_): Low temperature
        T1 (_type_): High temperature
    """
    alpha = L/A * np.divide(P , (T1-T0))
    beta = 1
    gamma = 0
    n = 0
    
    return np.mean(alpha), beta, gamma, n
    

def power_from_voltage(V, R):
    """Function to get the power dissipation given a voltage and resistance

    P = I*V = V/R = V**2/R
    Args:
        V (_type_): _description_
        R (_type_): _description_
    """
    
    P = V**2/R
    
    return P

if __name__ == "__main__":
    main()
