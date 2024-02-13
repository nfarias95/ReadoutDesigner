"""
Script to calculate loads on parts

"""

def main():
    print("Hello. Let's calculate some loads")
    
    # Load on kapton island 
    
    #########  Inputs #############
    
    # film dimensions
    film_width = 10e-3 # m
    film_height = 25e-6 # m
    film_length = 65e-3 # m
    # squid properties
    sq_density = 2330 # kg/m3 (Silicon)
    sq_volume = 6e-3 * 6e-3 * 2e-3 # m^3 (roughly)
    sq_mass = sq_density * sq_volume
    
    ############ Calculations ##########
    
    # Force (quasi-static)
    F_qs = sq_mass * 30 * 9.8 # 30 g of force (m/s^2)
    
    
    # Calculate maximum shear
    tau_max = max_shear_rectangle(F_qs , film_width , film_height) /2
    
    # Calculate maximum bending stress
    M = F_qs * 1/2 * film_length
    sigma_max = max_bending_stress_rectangle(M, film_width, film_height)
    
    ############# Outputs ##################
    print("Film properties: ")
    print("Length: %.1f mm  | Height: %.1f um  | Width: %.1f mm " \
        %(film_length*1e3, film_height*1e6, film_width*1e3))
    print("Squid mass: %.1f g " %(sq_mass*1e3) )
    
    print("\nMaximum shear stress: %.2f MPa " % ( tau_max/1e6 ) )
    print("Maximum bending stress: %.2f MPa " % ( sigma_max/1e6 ) )
    
    

def max_shear_rectangle(F, w, h):
    """This function calculates the maximum shear force 
    in a rectangular cross section

    Args:
        F (_type_): Force (N)
        w (_type_): width of cross section (m)
        h (_type_): height of cross section (m)
    """
    
    area = w*h
    
    tau_max = 3 * F / (2 * area)
    
    return tau_max


def max_bending_stress_rectangle(M:float, width:float, height:float):
    """Function to calculate the bending stress in a rectangular beam
    
    sigma_max = M * y / I
    
    I = 1/12 b * h^3
    
    sigma_max = 12 * M/ (b*h^2)

    Args:
        M (float): _description_
        width (float): _description_
        height (float): _description_
    """

    sigma_max = 6 * M / (width * height**2 )

    return sigma_max


if __name__ == "__main__":
    main()