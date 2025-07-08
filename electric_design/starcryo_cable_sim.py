import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import mu_0

# code from Tucker

def main():
    print("hi. \n")
    
    T = np.linspace(0.1, 0.5)

    # NbTi conductivity
    A = 270 # uW / cm / K # From Woodcraft
    B = 2
    k_nbti = A * T**B  / 1e6 * 1e2 # W / m / K
    int_kdT_nbti = np.trapz(k_nbti, x=T) / 1e6 * 1e2 # W / m

    # Kapton conductivity
    #k_kapton = 1.8 * T**1.15 * 1e-5 * 100 # W / m / K # Ubilex!
    k_kapton = 6.5 * T**1.00 * 1e-5 * 100 # W / m / K  # Kapton
    int_kdT_kapton = np.trapz(k_kapton, x=T) # W / m

    print("int_kdT_kapton: ", int_kdT_kapton)
    
    # 1 cm cable
    """
    l_cable = 1e-2
    w_nbti = np.linspace(10e-6, 500e-6)

    p_kapton, p_nbti = calc_heat_leak(l_cable, w_nbti, int_kdT_kapton, int_kdT_nbti)
    L_5 = calc_inductance(l_cable, w_nbti, gw=5e-6)
    L_10 = calc_inductance(l_cable, w_nbti, gw=10e-6)

    plt.figure(1)
    plt.plot(w_nbti*1e6, p_nbti, label='NbTi')
    plt.plot(w_nbti*1e6, p_nbti/p_nbti*p_kapton, label='Kapton')
    plt.plot(w_nbti*1e6, p_nbti + p_kapton, label='Total')
    #plt.axhline(20, linestyle='--', color='black', alpha=.7, label='Requirement')
    plt.legend()
    plt.xlabel('Trace width [um]')
    plt.ylabel('100 mK load [nW]')
    plt.title('1 cm long cable')
    #plt.show()

    plt.figure(2)
    plt.plot(w_nbti*1e6, L_5, label='5 um gap')
    plt.plot(w_nbti*1e6, L_10, label='10 um gap')
    plt.legend()
    plt.xlabel('Trace width [um]')
    plt.ylabel('Cable inductance [nH]')
    plt.title('1 cm long cable')
    plt.show()
    """
    
    # 2 cm cable
    
    l_cable = 2e-2
    w_nbti = np.linspace(10e-6, 1000e-6)

    p_kapton, p_nbti = calc_heat_leak(l_cable, w_nbti, int_kdT_kapton, int_kdT_nbti)
    L_5 = calc_inductance(l_cable, w_nbti, gw=5e-6)
    L_10 = calc_inductance(l_cable, w_nbti, gw=10e-6)

    print("Pkapton: ", p_kapton)
    print("Pnbti: ", p_nbti)

    plt.figure(3)
    plt.plot(w_nbti*1e6, p_nbti, label='NbTi')
    plt.plot(w_nbti*1e6, p_nbti/p_nbti*p_kapton, label='Kapton')
    #plt.plot(w_nbti*1e6, p_nbti + p_kapton, label='Total')
    #plt.axhline(20, linestyle='--', color='black', alpha=.7, label='Requirement')
    plt.legend()
    plt.xlabel('Trace width [um]')
    plt.ylabel('100 mK load [nW]')
    plt.title('2 cm long cable')
    #plt.show()

    plt.figure(4)
    plt.plot(w_nbti*1e6, L_5, label='5 um gap')
    plt.plot(w_nbti*1e6, L_10, label='10 um gap')
    plt.legend()
    plt.xlabel('Trace width [um]')
    plt.ylabel('Cable inductance [nH]')
    plt.title('2 cm long cable')
    plt.show()
    
    
    
    
    
    print("\ndone.\n\n")
    




    
def calc_heat_leak(l_cable, w_nbti, int_kdT_kapton, int_kdT_nbti):
    
    # calculate heat leak for 1 cm wide cable
    # with 8 NbTi conductors
    #
    # requirement: P<20 nW

    # set up geometry
    l_stiff = 2e-3 # 2 mm stiffeners

    w_kapton = 1e-2 # 1 cm
    t_kapton = 12e-6
    a_kapton = w_kapton * t_kapton

    l_nbti = l_cable + 2 * l_stiff
    t_nbti = 0.5e-6
    n_nbti = 8
    a_nbti = w_nbti * t_nbti * n_nbti

    p_kapton = a_kapton / l_cable * int_kdT_kapton * 1e9
    p_nbti = a_nbti / l_nbti * int_kdT_nbti * 1e9

    return p_kapton, p_nbti # units are nW


def calc_inductance(l_cable, w_nbti, gw):
    
    # calculate inductance of
    # edge-coupled striplines

    l_nbti = l_cable
    s = gw + w_nbti

    L = mu_0 / np.pi * np.arccosh(s/w_nbti)
    L = L * 1e9 # nH / m
    L = L * l_nbti # nH

    return L # units are nH


if __name__ == "__main__":
    main()