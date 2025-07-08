"""
Code to calculate the thermal conductance of a material given
power and temperature data + experimental setup parameters from a csv file



"""

import numpy as np
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
import csv
import sys
sys.path.insert(0, 'C:/Users/nicol/Documents/00Research/PythonCode/ReadoutDesigner/')
from mechanical_design.thermal_properties.core_thermal_equations import  get_dissipated_heat, NbTi, PhosphorBronze, Kapton


from matplotlib import pyplot as plt
from plot_parameters import FONT, FIG_SIZE, LEGEND_SIZE, FONT_SIZE
plt.rcParams["font.family"] = FONT
plt.rcParams.update({'font.size': FONT_SIZE})
plt.rc('legend', fontsize=LEGEND_SIZE)    # legend fontsize


data_dir =  "C:/Users/nicol/Documents/00Research/Data/APEX/Run 65 Thermal Conductance/"
data_file = "kapton_thermal_conductance_summer_2024.csv"
FILE_PATH = data_dir + data_file

def main():
    print("Analysing thermal conductance of a material based on heat deposited and change in temperature")
    
    ### First, read the data and experimental setup numbers from the csv file:
    V_out, T0, T1, width, thickness, length, R_heater, R_heater_sigma, R_series, R_series_sigma, \
        V_sigma, T_sigma, therm_wire_diameter, therm_wire_length, heater_wire_diameter, heater_wire_length, \
        wiring_end_temperature = read_data_from_csv(data_dir+data_file, verbose=True)

    ### Material properties
    area = 2 * thickness * width # 2 arms
    g = area/length
    
    ## Average base temperature
    T0_mean = np.mean(T0)

    ### Get power dissipated by heater
    I_out = V_out / (R_heater+ R_series)
    P_heater = I_out**2 * R_heater
    
    ### Calculate uncertainty in power dissipated by heater
    P_heater_sigma = V_out/R_heater * np.sqrt( 4*V_sigma**2 + R_heater_sigma**2 * V_out/(R_heater**2) )
    P_heater_over_g_sigma = P_heater_sigma/g
    
    #### Simulate power dissipated by wiring ####
    # intialize material
    heater_material = NbTi(cryogenic=True)
    therm_wire_material = PhosphorBronze(cryogenic=True)
    # get cross sectional area based on wiring diamter
    hw_area = 2 * (heater_wire_diameter/2)**2 * np.pi # two wires
    therm_area = 4 * (therm_wire_diameter/2)**2 * np.pi # four wires
    # initialize array to store total power dissipated by wiring
    total_par_powers = np.zeros(len(T1))
    for t, T1_var in enumerate(T1):
        # Calculate parasitic power
        hw_par_power = get_dissipated_heat(T0_mean, T1_var, heater_material, \
            hw_area, heater_wire_length)
        therm_par_power = get_dissipated_heat(T0_mean, T1_var, therm_wire_material, \
            therm_area, therm_wire_length)
        total_par_powers[t] = hw_par_power + therm_par_power
    
    
    # FIT TO THE DATA
    # fitted parameters
    # params, cov = curve_fit(power_model, T1, P_heater/g)
    # a = params[0] ; b = params[1] ; Ppar_fit = params[2] * g
    # beta = b - 1
    # alpha = a * (beta + 1)
    # measured_material = MeasuredMaterialProperties(alpha, beta, 0, 0)
    # # fitted curve
    # P_heater_over_g_fit = power_model(np.sort(T1), params[0], params[1], params[2])
    # P_heater_fit = P_heater_over_g_fit * g


    # FIT WHILE MODELLING PARASITICS
    # params_2, cov_2 = curve_fit(power_model, T1, (P_heater-total_par_powers)/g)
    # a2 = params_2[0] ; b2 = params_2[1] ; Ppar_fit2 = params_2[2] * g
    # beta2 = b2 - 1
    # alpha2 = a2 * (beta2 + 1)
    # measured_material2 = MeasuredMaterialProperties(alpha2, beta2, 0, 0)
    # P_heater_over_g_fit2 = power_model(np.sort(T1), params_2[0], params_2[1], params_2[2])
    # P_heater_fit2 = P_heater_over_g_fit2 * g
    
    # FIT USING PARASITICS IN UNCERTAINTIES
    uncertainty = np.array([ np.sqrt((P_heater_sigma**2+total_par_powers**2)), P_heater_sigma])
    print("u:", uncertainty[0,:])
    sigma= (uncertainty[0,:]+uncertainty[1, :])/2
    params3, pcov3 = curve_fit(power_model, T1, (P_heater)/g, sigma=sigma, absolute_sigma=True)
    a3 = params3[0] ; b3 = params3[1] ; Ppar_fit3 = params3[2] * g
    beta3 = b3 - 1
    alpha3 = a3 * (beta3 + 1)
    measured_material3 = MeasuredMaterialProperties(alpha3, beta3, 0, 0)
    P_heater_over_g_fit3 = power_model(np.sort(T1), params3[0], params3[1], params3[2])
    P_heater_fit3 = P_heater_over_g_fit3 * g
    # uncertainty of fit parameters
    a3_err = np.sqrt(np.diag(pcov3))[0]
    b3_err = np.sqrt(np.diag(pcov3))[1]
    Ppar_fit3_err = np.sqrt(np.diag(pcov3))[2]
    
    # PLOT RESULTS

    # # # # plot with lots of info
    # # # plt.figure(13, figsize=FIG_SIZE)
    # # # # plot datapoints without taking into account wiring parasitics
    # # # plt.scatter(T1, P_heater *1e9 , color='k', s=15)    
    # # # plt.errorbar(T1, (P_heater)*1e9, yerr = P_heater_sigma*1e9,  \
    # # #     fmt='none', color='k', capsize=5)
    # # # # plot fit
    # # # plt.plot(np.sort(T1), P_heater_fit * 1e9, color='k', linewidth=0.5)
    # # # # plot datapoints while taking into account wiring parasitics
    # # # plt.scatter(T1, (P_heater-total_par_powers) *1e9 , color='g', s=15)
    # # # plt.errorbar(T1, (P_heater-total_par_powers)*1e9, yerr = P_heater_sigma*1e9,  \
    # # #     fmt='none', color='g', capsize=5)
    # # # plt.plot(np.sort(T1), P_heater_fit2 * 1e9, color='g', linewidth=0.5)
    # # # # labels, text
    # # # note = "Fit parameters: \nParasitic  Power: {:.2f} | {:.2f} nW  \na: {:.2e} | {:.2e} \nb: {:.2f} | {:.2f}"\
    # # #     .format(Ppar_fit*1e9, Ppar_fit2*1e9, a, a2, b, b2)
    # # # plt.annotate(note, [0.5, 40])
    # # # plt.xlabel("T [K]")
    # # # plt.ylabel("$P_{diss}$ [nW]")
    # # # #plt.title("($P_{heater} + P_{par} )/g = a * (T^b - T_0^b$)")
    # # # plt.grid(True)
    # # # # parasitics
    # # # #plt.scatter(T1, total_par_powers*1e9, label="parasitic")

    # PLOT FOR PAPER
    plt.figure(14, figsize=FIG_SIZE)
    # plot datapoints
    plt.scatter(T1, P_heater *1e9 , color='k', s=20)    
    plt.errorbar(T1, P_heater*1e9, yerr = uncertainty*1e9,  \
        fmt='none', color='k', capsize=5)
    # plot fit
    plt.plot(np.sort(T1), P_heater_fit3 * 1e9, color='k', linewidth=0.5)
    #plt.plot(np.sort(T1), P_heater_fit * 1e9, color='y', linewidth=0.5)
    plt.xlabel("$T_{1}$ [K]")
    plt.ylabel("$P_{heater}-P_{par,w}$ [nW]")
    plt.grid(True)
    
    print("Covariance")
    print(pcov3)
    print("Parameter uncertainty")
    print(np.sqrt(np.diag(pcov3)))
    print("Parameters")
    print(params3)
    
    print("--- SUMMARY --")
    print("a : ", a3 , "+- ", a3_err)
    print("b : ", b3 , "+- ", b3_err)
    print("Ppar,rad : ", Ppar_fit3*1e9 , "+- ", Ppar_fit3_err*1e9)
    print("alpha: ", alpha3)
    print("beta: ", beta3)
    
    # # PLOT WIRING PARASITICS
    # # plt.figure(15)
    # # plt.scatter(T1, total_par_powers/P_heater)
    # # plt.grid(True)
    
    # --- See if we meet our requirements ----
    Tbath = 0.1#0.112 # Temperature of bath (detector stage) [K]
    Tsq = 0.35#0.405 # Temperature of squid stage {K}
    Pmax = 5e-9 # Watts
    P_expected_sq_k = get_dissipated_heat(Tbath, Tsq, measured_material3, area=area, length=length)
    P_expected_sq = g * a3 * (Tsq**b3 - Tbath**b3)
    
    print("\nExpected dissipated power: {:.2f} nW , {:.2f} nW ".format(P_expected_sq_k*1e9, P_expected_sq*1e9))
    
    
    
    
    plt.show()
    print("The end.")

def read_data_from_csv(path_to_file:str, verbose=False):
    """function to read the voltage and temperature from a csv file.

    Args:
        path_to_file (str): _description_
        verbose (bool): whether or not to print useful things
    """
    V_out = np.array([])
    T1 = np.array([])
    T0 = np.array([])
    
    with open(path_to_file, mode='r') as file:
        csv_reader = csv.reader(file)
        row_count = -1
    
        for row in csv_reader:
            row_count +=1
            #print(row)
            
            # get material properties
            if row_count == 3:
                width = float(row[0])
                thickness = float(row[1])
                length = float(row[2])
            elif row_count == 5:
                R_heater = float(row[0])
                R_heater_sigma = float(row[1])
            elif row_count == 7:
                R_series = float(row[0])
                R_series_sigma = float(row[1])
            elif row_count == 9:
                V_sigma = float(row[0])
            elif row_count == 11:
                T_sigma = float(row[0])
            elif row_count == 13:
                therm_wire_length = float(row[0])
                therm_wire_diameter = float(row[1])
                heater_wire_length = float(row[2])
                heater_wire_diameter = float(row[3])
                wiring_end_temperature = float(row[4])
            elif row_count >= 15:                
                V_out = np.append(V_out, float(row[2]))
                T0 = np.append(T0, float(row[3]))
                T1 = np.append(T1, float(row[4]))
            
    if verbose:
        print("Width[mm]: ", width*1e3, " , thickness [um]: ", thickness*1e6, " , length [mm]: ", length*1e3)
        print("R_heater [Ohms]", R_heater, " +- ", R_heater_sigma)
        print("R_series [Ohms]: ", R_series, " +- ", R_series_sigma)
        print("Voltage uncertainty [V]: ", V_sigma)
        print("Temperature uncertainty [K]: ", T_sigma)
        print("Thermometer length [m], diameter [um] ", therm_wire_length, therm_wire_diameter*1e6)
        print("Heater wire length[m] and diameter [um]: ", heater_wire_length, heater_wire_diameter*1e6)
        print("Wiring end temperature: ", wiring_end_temperature)
    
    return V_out, T0, T1, width, thickness, length, R_heater, R_heater_sigma, R_series, R_series_sigma, \
        V_sigma, T_sigma, therm_wire_diameter, therm_wire_length, heater_wire_diameter, heater_wire_length, \
        wiring_end_temperature
    
    
class MeasuredMaterialProperties():
    def __init__(self, alpha, beta, gamma, n):
        self.alpha=alpha
        self.beta=beta
        self.gamma=gamma
        self.n=n


def power_model(T1, a, b, Ppar_over_g):
    """Function that models the power dissipation P/g of a material 
    such that (P+Par)/g = a(T1^b - T0^b)
    Args:
        T1 (_type_): _description_
        a (_type_): _description_
        b (_type_): _description_
        Ppar (_type_): _description_
    """
    T0 = 0.243
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
