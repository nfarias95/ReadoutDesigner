kb = 1.380649e-23 #boltzmann constant
h = 6.62607015e-34 # planck constant

def NEP_g(psat, n, tb, tc):
    return (
        (4*kb*psat*tb) * (n+1)**2 * ((tc/tb)**(2*n+3)-1)
        / (2*n+3) / ((tc/tb)**(n+1)-1)**2
    )**.5
    
def NEP_ph(popt, v, dv):
    #return (2*popt*h*v + popt**2/dv)**.5
    return 2**.5*(popt*h*v + popt**2/dv)**.5


def S_I(rtes, pelec, loopgain, ac=True):
    prefactor = 1.
    if ac: 
        prefactor = 2. # will go inside square root below
    return (prefactor/rtes/pelec)**.5 * loopgain / (loopgain + 1)