"""
Code to simulate different dfmux scenarios and compare them
See Example_SA13.ipunb as the starting point
"""
import numpy as np
from matplotlib import pyplot as plt
from dfmux_calc import DfMux, Bolometer, CarrierChain, DemodChain, NullerChain, SQUID

# global constants
freqs = np.linspace(1.5e6, 5.5e6, 68) # frequency schedule [Hz]
LB_requirement = 6.2e-12 # A/sqrt(Hz) # from litebird_noise.ipynb

def main():
    print("Let's compare different scenarios :) ")
    
    # Baseline (reference) system - using SA13s
    R_tes_0 = 1. # TES resistance
    Tc0 = 0.480 # TES critical temperature
    T_bias0 = 4 # 
    zt0 = 800. # transimpedance
    rdyn0 = 750. # dynamical impedance
    lin0 = 70e-9 # input inductance
    noise_squid_only_0 = 1e-12 # squid noise
    
    dfmux_0 = DfMux(freqs,
              bolo = Bolometer(r=R_tes_0, tc=Tc0),
              carrier = CarrierChain(t_bias=T_bias0),
              demod = DemodChain(),
              nuller = NullerChain(),
              squid = SQUID(zt = zt0, 
                            rdyn = rdyn0,
                            lin = lin0,
                            noise_squid_only = noise_squid_only_0))
    dfmux_0.calc_noise()
    
    # Comparison - using SA13s
    R_tes_1 = 0.5 # TES resistance
    Tc1 = Tc0 # TES critical temperature
    T_bias1 = 4 # 
    zt1 = zt0 # transimpedance
    rdyn1 = rdyn0 # dynamical impedance
    lin1 = lin0 # input inductance
    noise_squid_only_1 = 7e-12 # squid noise
    label=""
    
    dfmux_1 = DfMux(freqs,
              bolo = Bolometer(r=R_tes_1, tc=Tc1),
              carrier = CarrierChain(t_bias=T_bias1),
              demod = DemodChain(),
              nuller = NullerChain(),
              
              squid = SQUID(zt = zt1, 
                            rdyn = rdyn1,
                            lin = lin1,
                            noise_squid_only = noise_squid_only_1))
    dfmux_1.calc_noise()
    
    
    # ------- PLOT STUFF ---------
    # PLOT INDIVIDUALLY
    # plot_readout_noise_contributions(dfmux_0, figcount=1, title="Reference")
    #plot_readout_noise_contributions(dfmux_1, figcount=2, title=label)
    
    # plot comparison between two systems
    # plot_comparison_readout_noise_contributions(dfmux_0, dfmux_1, figcount=3, title=label)
    # plot_total_noise_comparison(dfmux_0, dfmux_1, figcount=3, title="")
    
    plt.plot(freqs/1e6, dfmux_0.total_noise*1e12, label="R_TES=1.0")
    plt.plot(freqs/1e6, dfmux_1.total_noise*1e12, label="R_TES=0.5")
    plt.legend()
    plt.xlabel("Frequency [MHz]")
    plt.ylabel("NEI [pA/sqrt(Hz)]")
    
    # -------- PRINT STUFF ----------
    print("-----------------------")
    print(" Current Median Noise        Expected Median Noise        Ratio       LiteBIRD ~ requirement ")
    print("   [pA/sqrt(Hz)]                 [pA/sqrt(Hz)]                          [pA/sqrt(Hz)]  ")
    print("        %.1f                          %.1f                   %.2f            %.1f     " \
        %(np.median(dfmux_0.total_noise)*1e12, \
        np.median(dfmux_1.total_noise)*1e12, np.median(dfmux_1.total_noise)/np.median(dfmux_0.total_noise),
        LB_requirement*1e12))
    
    
    
    print("The end")
    plt.show()
    return 0

def plot_total_noise_comparison(dfmux0, dfmux1, figcount=4, title=""):
    plt.figure(figcount)
    
    ratio = np.divide(dfmux1.total_noise , dfmux0.total_noise)
    
    plt.plot(freqs/1e6, ratio, label="")
    plt.plot(freqs/1e6, np.ones(len(freqs)), "--")
    plt.ylabel("Ratio of NEI(new)/NEI(ref)")
    plt.xlabel('Frequency [MHz]')
    
def plot_readout_noise_contributions(dfmux, figcount=1, title=""):
    plt.figure(figcount)
    plt.plot(freqs/1e6, dfmux.total_noise*1e12, 'k', label='Total')
    plt.plot(freqs/1e6, dfmux.carrier.total_noise*1e12, label='carrier')
    plt.plot(freqs/1e6, dfmux.nuller.total_noise*1e12, label='nuller')
    plt.plot(freqs/1e6, dfmux.demod.total_noise*1e12, label='demod')
    plt.plot(freqs/1e6, dfmux.squid.total_noise*1e12, label='squid')
    plt.legend()
    plt.ylabel('Readout noise [pA/rtHz]')
    plt.xlabel('Frequency [MHz]')
    #plt.ylim(0, 10)
    plt.title(title)
    
def plot_comparison_readout_noise_contributions(dfmux0, dfmux1, figcount=3, title=""):
    plt.figure(figcount)
    plt.axhline(LB_requirement*1e12, label="goal", linewidth=5, alpha=0.5)
    
    plt.plot(freqs/1e6, dfmux0.total_noise*1e12, 'k', label='Total, now')
    plt.plot(freqs/1e6, dfmux0.carrier.total_noise*1e12, "b" ,label='carrier')
    plt.plot(freqs/1e6, dfmux0.nuller.total_noise*1e12, "r", label='nuller')
    plt.plot(freqs/1e6, dfmux0.demod.total_noise*1e12, "g", label='demod')
    plt.plot(freqs/1e6, dfmux0.squid.total_noise*1e12, "y", label='squid')
    
    plt.plot(freqs/1e6, dfmux1.total_noise*1e12,  "--", color="k", label="modified")
    plt.plot(freqs/1e6, dfmux1.carrier.total_noise*1e12, "--" , color="b")
    plt.plot(freqs/1e6, dfmux1.nuller.total_noise*1e12, "--", color= "r")
    plt.plot(freqs/1e6, dfmux1.demod.total_noise*1e12, "--", color="g")
    plt.plot(freqs/1e6, dfmux1.squid.total_noise*1e12, "--", color="y")
    
    plt.legend()
    plt.ylabel('Readout noise [pA/rtHz]')
    plt.xlabel('Frequency [MHz]')
    #plt.ylim(0, 10)
    plt.title(title)
    
    
    
    return 0

if __name__ == "__main__":
    main()