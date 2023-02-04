# This program is meant for calculating inductances and capacitances in microstrip lines - for example, in a PCB!
# Equations are based off:
# https://resources.altium.com/p/pcb-trace-inductance-and-width-how-wide-too-wide

from matplotlib import pyplot as plt
import numpy as np
pi = np.pi
e = np.e


def main():
    print("\n\n\nLet's calculate some impedances!\n\n")
    
    # Note: board thickness is 1.6 mm but we have 8 layers
    # material: Tg150 FR-4
    # Typical dielectric constant values found in dielectric materials commonly used in PCBs 
    # are between 3.5 and 5.5, but this value is strictly dependent on the signal frequency and 
    # decreases as it increases. For FR4, varies from 3.8 to 4.8. Let's take 4.3
    
    # 1 oz -> 1.2 mils
    # bias trace length is 10 mm
    # bias pad in SA13/StarCRYO footprint is 1x1 mm
    
    # PCB PARAMETERS
    h = 1.6 / 7 /1000 # [meters] height of dielectric (distance between trace/microstrip and ground). 
                # we have 8 layers and the board thickness is 1.6 mm, so the ground plane is a distance of 1.6/7 mm
    t = 1.2/1000 * 2.54/100 # [meters] thickness of copper layer
    epsilon_r = 4.3 #  [unitless] relative permittivity 
    
    # Checking that the inductance of the bias trace is correct:
    w = 0.127/1000 # [meters] width of trace
    d = 10e-3 # [meters] -- 10 mm

    L_bias, C_bias = calculate_pad_L_and_C(d, w, h, t, epsilon_r)
    print("L_bias: ", L_bias * 1e9 , " nH ")
    
    # NOW LET'S SEE WHAT HAPPENS TO THE PADS AS WE INCREASE THEIR SIDE
    d = 1e-3 # 1 mm
    w = 1e-3 # 1 mm
    L0, C0 = calculate_pad_L_and_C(d, w, h, t, epsilon_r)
    
    print(" 1x1 mm pad:")
    print("L0: ", L0*1e9 , " nH ")
    print("C0: ", C0*1e12, " pF")
    
    # Now let's see what happens as we expand the pads
    d_array = np.linspace(0.5, 2.0, 4) * 1e-3 # [meters]
    w_array = np.linspace(1, 5, 10) * 1e-3 #[meters]
    
    L_matrix = np.zeros((4, 10)) 
    C_matrix = np.zeros((4,10)) 
    
    d_c = -1 # d counter
    
    for d in d_array:
        d_c = d_c + 1
        w_c = -1 # w counter
        for w in w_array:
            w_c = w_c + 1 
            L, C = calculate_pad_L_and_C(d, w, h, t, epsilon_r)
            L_matrix[d_c, w_c] = L
            C_matrix[d_c, w_c] = C
            
        plt.figure(1)
        plt.plot(w_array*1e3, L_matrix[d_c, :]*1e9, label='pad length [mm]:' + str(d*1e3))
        plt.xlabel("Pad width [mm]")
        plt.ylabel("Inductance [nH]")
        plt.legend()    
        
        plt.figure(2)
        plt.plot(w_array*1e3, C_matrix[d_c, :]*1e12, label='pad length [mm]:' + str(d*1e3))
        plt.xlabel("Pad width [mm]")
        plt.ylabel("Capacitance [pF]")
        plt.legend()   
    
    
    ################
    plt.show()
    print("---\nThe end. \n\n\n")

def calculate_pad_L_and_C(d:float, w:float, h:float, t:float, epsilon_r:float):
    """Calculate the inductance and capacitance of a pad in a PCB

    Args:
        d (float): length of pad [m]
        w (float): width of pad  [m]
        h (float): height of dielectric (distance betwen pad and ground plane) [m]
        t (float): thickness of copper layer [m]
        epsilon_r (float): dielectric constant / relative permittivity
    """
    # calculate w_prime:
    w_prime = calculate_w_prime(w, epsilon_r, t, h)
    
    # calculate impedance Z0:
    Z0 = calculate_Z0(epsilon_r, w_prime, h)
    
    # calculate effective epsilon:
    epsilon_eff = calculate_epsilon_eff(epsilon_r, h, w)
    
    # calculate L and C
    
    L_per_meter = calculate_L_per_meter(Z0, epsilon_eff)
    
    C_per_meter = calculate_C_per_meter(L_per_meter, Z0)
    
    # print("w: ", w)
    # print("w': ", w_prime)
    # print("Z0: ", Z0)
    # print("epsilon eff: ", epsilon_eff)
    # print("L: ", L_per_meter)
    # print("C: ", C_per_meter)
    
    L = d * L_per_meter
    C = d * C_per_meter
    
    return L, C
    
def calculate_Z0(epsilon_r, w_prime, h):
    """Function to calculate impedance

    Args:
        epsilon_r (_type_): _description_
        omega_prime (_type_): _description_
        h (_type_): _description_
    """
    
    Z0 = 60 / ( (2*epsilon_r + 2)**0.5 ) * np.log(1 + 4*h/w_prime * ( (14+8/epsilon_r)/11 * (4*h/w_prime) + \
        np.sqrt( ((14+8/epsilon_r)/11)**2 * (4*h/w_prime)**2 + pi**2  * (1+1/epsilon_r)/2 )) )
    
    return Z0

def calculate_w_prime(w : float, epsilon_r:float, t:float, h:float):
    """Function to calculate w_prime, which I think is an effective width of the microstrip

    Args:
        w (float): _description_
    """
    
    w_prime = w + (1+1/epsilon_r)/2 * (t/pi) * np.log( 4*e / ( (t/h)**2 + ( (1/pi) / (w/t + 1.1)**2 )))
    
    return w_prime

def calculate_epsilon_eff(epsilon_r:float, h:float, w:float):
    """function to calculate effective dielectric constant

    Args:
        epsilon_r (float): _description_
        h (float): _description_
        w (float): _description_
    """

    if w < h:
        epsilon_eff = (epsilon_r+ 1 )/2 + (epsilon_r - 1)/2 * (( 1 + 12*h/w)**(-0.5) + 0.004 * (1-w/h)**2 )
        
    else:
        epsilon_eff = (epsilon_r+ 1 )/2 + (epsilon_r - 1)/2 * (1 + 12*h/w)**(-0.5)
        
    return epsilon_eff


def calculate_L_per_meter(Z0:float, epsilon_eff:float, c_vac=3.0e8):
    """function to calculate the inductance per unit length of trace
    
    L = Z0/c_vac * np.sqrt(epsilon_eff)
    
    checking units: 
    [Z0] = ohms
    [c_vac] = m/s
    [epsilon_eff] = unitless
    
    so the units are ohms*sec/meters
    
    impedance of inductor is: Z = i omega L , so [L] = [Z]/[omega] = [ohms]/([1/s]) = [omhs][s]
    so to get the actual inductance just multiply L here by distance in METERS.
    
    Args:
        Z0 (float): _description_
        epsilon_eff (float): _description_
    """
    
    L_per_meter = Z0/c_vac * np.sqrt(epsilon_eff)
    
    return L_per_meter
    
def calculate_C_per_meter(L_per_meter:float, Z0:float):
    """function to calculate capacitance of trace

    Args:
        L (float): inductance per meter of trace
        Z0 (float): _description_
    """
    
    C_per_meter = L_per_meter/(Z0**2)
    
    return C_per_meter

if __name__ == "__main__":
    main()