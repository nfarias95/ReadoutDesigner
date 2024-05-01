import numpy as np

def get_dissipated_heat(T0, T1, material,  area, length):
    """Calculate dissipated heat given thermal conductance k=alpha*T^(beta+gamma*(T^n))

    Args:
        T_0 (_type_): cold temperature
        T_1 : warm temperature
        material: a class that contains the thermal properties of a material
        area (_type_): area of cross section of conductor
        length (_type_): length of conductor
    """
    # divide temperature into array
    T_array = np.linspace(T0, T1, 100) # array of temperature used to integrate G   
    
    # Get conductance    
    k_array = np.zeros(len(T_array))
    for tc, T in enumerate(T_array):
        k_array[tc] = material.alpha * T **(material.beta  + material.gamma * (T **(material.n)))
    # integrate conductance and calculate heat transfer
    k_integrated = np.trapz(k_array, x=T_array)
    Q = k_integrated * area / length 
    
    return Q
  

class PhosphorBronze:
    """
    Material used in Lakeshore thermometers.
    Sources: 
    alpha from: https://www.lakeshore.com/products/categories/specification/temperature-products/cryogenic-accessories/cryogenic-wire
    beta from: https://ntrs.nasa.gov/api/citations/20090032058/downloads/20090032058.pdf (looks linear)
    From Keith: k(set_Tlow) = PB_data(1,2)*(T(set_Tlow)/1.0).^1.5;   # alpha=1
                # power law 1.5 just a guess based on extrap.
    """
    def __init__(self, cryogenic=True):
        if cryogenic:
            # Thermal conductance properties
            self.alpha = 0.22# [W/m K] at 1K. No information at sub-K
            self.beta = 1.5
            self.gamma = 0
            self.n = 0



class Kapton:
    # Source: https://www.sciencedirect.com/science/article/pii/S0011227500000138
    def __init__(self, cryogenic=True):
        if cryogenic:
            # Thermal conductance properties
            self.alpha = 6.5e-3 # W/m K
            self.beta = 1.0
            self.gamma = 0
            self.n = 0
            
class NbTi:
    # Source:  Woodcraft 2010
    def __init__(self, cryogenic=True):
        if cryogenic:
            # Thermal conductance properties
            self.alpha = 0.027 # W/m K
            self.beta = 2.0
            self.gamma = 0
            self.n = 0
            
class Ubilex:
    # Source: https://www.sciencedirect.com/science/article/pii/S0011227500000138
    def __init__(self, cryogenic=True):
        if cryogenic:
            # Thermal conductance properties
            self.alpha = 1.8e-3 # W/m K
            self.beta = 1.0
            self.gamma = 0
            self.n = 0

class CarbonStrut:
    # From Keith's note 67    
    def __init__(self, cryogenic=True):
        if cryogenic:
            self.alpha = 8.39e-3
            self.beta = 2.12
            self.gamma = -1.05
            self.n = 0.181