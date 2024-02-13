import numpy as np
import copy as copy

def parallel(x, y):
    return 1/(1/x + 1/y)

        
class Bolometer:
    
    def __init__(self, r=1.5, tc=0.171, tb=0.1):
        self.r = r
        self.tc = tc
        self.tb = tb
    
    def calc_johnson_noise(self, freqs):
        return np.sqrt(8*1.38e-23*self.tc/self.r) * (freqs/freqs)
    
    def calc_total_noise(self):
        total = []
        for key in self.noise:
            total.append(self.noise[key]**2)
        total = np.sum(total, axis=0)**.5
        return total

    
class CarrierChain:
    
    def __init__(self, l_bias=0., r_bias=30e-3, t_bias=4., r_stiff=180., polyvals=[1.]):
        self.l_bias = l_bias
        self.r_bias = r_bias
        self.t_bias = t_bias
        self.r_stiff = r_stiff
        self.polyvals = polyvals        
          
    def calc_tf(self, freqs):
        # conversion from current at DAC output to voltage across comb
        dc_tf = 200 / self.r_stiff * 30e-3 # following convention in pydfmux
        ac_tf = np.polyval(self.polyvals, freqs)
        return dc_tf * ac_tf
    
    def calc_dac_noise(self, bolo):
        return 50e-12 * np.sqrt(2) * self.tf / bolo.r
    
    def calc_quantization_noise(self, bolo):
        return 14e-12 * np.sqrt(2) * self.tf / bolo.r
    
    def calc_amplifier_noise(self, bolo):
        return 34e-12 * np.sqrt(2) * self.tf / bolo.r
    
    def calc_stiffening_resistor_johnson_noise(self, freqs, bolo):
        jw = 2.j*np.pi*freqs
        return np.sqrt(2)*np.sqrt(4*1.38e-23*270./self.r_stiff) * np.absolute(self.r_bias + jw*self.l_bias) / bolo.r

    def calc_bias_element_johnson_noise(self, bolo):
        return np.full(len(self.tf),
                       np.sqrt(2)*np.sqrt(4*1.38e-23*self.t_bias*self.r_bias)/bolo.r)

    def calc_total_noise(self):
        total = []
        for key in self.noise:
            total.append(self.noise[key]**2)
        total = np.sum(total, axis=0)**.5
        return total

    
class DemodChain:
    
    def __init__(self, r_wh=40., c_wh=40e-12, l_wh=1e-6):
        self.r_wh = r_wh
        self.c_wh = c_wh
        self.l_wh = l_wh
        
    def calc_req(self, freqs, squid):
        jw = 2.j * np.pi * freqs
        return np.absolute(parallel(1/jw/self.c_wh, squid.rdyn) + 2*self.r_wh + 2*jw*self.l_wh)
    
    def calc_rsqcb(self):
        return (1/10.+1/100.+1/150.)**-1 + (1/4.22e3+1/self.req)**-1
    
    def calc_csf(self, freqs, bolo, squid):
        jw = 2.j * np.pi * freqs
        return np.absolute(1 + jw*squid.lin/bolo.r)
    
    def calc_output_filter(self, freqs, squid):
        w = 2 * np.pi * freqs
        return np.absolute( (1/1j/w/self.c_wh) / ((1/1j/w/self.c_wh) + squid.rdyn))
    
    def calc_adc_noise(self, squid):
        return 0.23e-9 * np.sqrt(2) * self.csf / squid.zt / self.output_filter
    
    def calc_second_stage_amplifier_noise(self, squid):
        return 0.14e-9 * np.sqrt(2) * self.csf / squid.zt / self.output_filter
    
    def calc_first_stage_amplifier_current_noise(self, squid):
        return 2.2e-12 * self.rsqcb * np.sqrt(2) * self.csf / squid.zt / self.output_filter
    
    def calc_first_stage_amplifier_voltage_noise(self, squid):
        return 1.1e-9 * np.sqrt(2) * self.csf / squid.zt / self.output_filter
    
    def calc_squid_bias_johnson_noise(self, squid):
        return 8.36e-9 * self.req / (self.req + 4.22e3) * np.sqrt(2) * self.csf / squid.zt / self.output_filter
        
    def calc_total_noise(self):
        total = []
        for key in self.noise:
            total.append(self.noise[key]**2)
        total = np.sum(total, axis=0)**.5
        return total    

    
class NullerChain:
    
    def __init__(self, r_stiff=3e3, polyvals=[1.]):
        self.r_stiff = r_stiff
        self.polyvals = polyvals
        
    def calc_tf(self, freqs):
        # conversion from current at DAC output to current at summing node
        dc_tf = 200 * 96.77 / 196.77 / self.r_stiff # following convention in pydfmux
        ac_tf = np.polyval(self.polyvals, freqs)
        return dc_tf * ac_tf
    
    def calc_dac_noise(self):
        return 50e-12 * np.sqrt(2) * self.tf
    
    def calc_quantization_noise(self):
        return 14e-12 * np.sqrt(2) * self.tf
    
    def calc_amplifier_noise(self):
        return 34e-12 * np.sqrt(2) * self.tf
    
    def calc_stiffening_resistor_johnson_noise(self):    
        return np.full(len(self.tf), np.sqrt(8*1.38e-23*300./self.r_stiff))
    
    def calc_flux_bias_johnson_noise(self):
        return np.full(len(self.tf), np.sqrt(8*1.38e-23*300./20e3))
    
    def calc_analog_feedback_johnson_noise(self):
        return np.full(len(self.tf), np.sqrt(8*1.38e-23*300./20e3))
    
    def calc_total_noise(self):
        total = []
        for key in self.noise:
            total.append(self.noise[key]**2)
        total = np.sum(total, axis=0)**.5
        return total


class SQUID:
    
    def __init__(self, zt=700, rdyn=700, noise_squid_only=3e-12, lin=70e-9):
        self.zt = zt
        self.rdyn = rdyn
        self.noise_squid_only = noise_squid_only
        self.lin = lin
    
    def calc_squid_noise(self, demod):
        return self.noise_squid_only * demod.csf * np.sqrt(2)        


class DfMux():
    
    def __init__(self, freqs, bolo=Bolometer(), carrier=CarrierChain(), demod=DemodChain(), nuller=NullerChain(), squid=SQUID()):
        self.freqs = copy.copy(freqs)
        self.bolo = copy.copy(bolo)
        self.carrier = copy.copy(carrier)
        self.demod = copy.copy(demod)
        self.nuller = copy.copy(nuller)
        self.squid = copy.copy(squid)

    def calc_noise(self):
        self.calc_carrier_chain_noise()
        self.calc_nuller_chain_noise()
        self.calc_demod_chain_noise()
        self.calc_bolo_noise()
        self.calc_squid_noise()
        self.calc_total_noise()
        pass
    
    def calc_carrier_chain_noise(self):
        self.carrier.tf = self.carrier.calc_tf(self.freqs)
        self.carrier.noise = {
            'dac' : self.carrier.calc_dac_noise(self.bolo),
            'quantization' : self.carrier.calc_quantization_noise(self.bolo),
            'amplifier' : self.carrier.calc_amplifier_noise(self.bolo),
            'stiffening_resistor_johnson' : self.carrier.calc_stiffening_resistor_johnson_noise(self.freqs, self.bolo),
            'bias_element_johnson' : self.carrier.calc_bias_element_johnson_noise(self.bolo),
        }
        self.carrier.total_noise = self.carrier.calc_total_noise()

    def calc_nuller_chain_noise(self):
        self.nuller.tf = self.nuller.calc_tf(self.freqs)
        self.nuller.noise = {
            'dac' : self.nuller.calc_dac_noise(),
            'quantization' : self.nuller.calc_quantization_noise(),
            'amplifier' : self.nuller.calc_amplifier_noise(),
            'stiffening_resistor_johnson' : self.nuller.calc_stiffening_resistor_johnson_noise(),
            'flux_bias_johnson' : self.nuller.calc_flux_bias_johnson_noise(),
            'analog_feedback_johnson' : self.nuller.calc_analog_feedback_johnson_noise(),
        }
        self.nuller.total_noise = self.nuller.calc_total_noise()

    def calc_demod_chain_noise(self):
        self.demod.req = self.demod.calc_req(self.freqs, self.squid)
        self.demod.rsqcb = self.demod.calc_rsqcb()
        self.demod.csf = self.demod.calc_csf(self.freqs, self.bolo, self.squid)
        self.demod.output_filter = self.demod.calc_output_filter(self.freqs, self.squid)
        self.demod.noise = {
            'adc' : self.demod.calc_adc_noise(self.squid),
            'amplifier_second_stage' : self.demod.calc_second_stage_amplifier_noise(self.squid),
            'amplifier_first_stage_voltage' : self.demod.calc_first_stage_amplifier_voltage_noise(self.squid),
            'amplifier_first_stage_current' : self.demod.calc_first_stage_amplifier_current_noise(self.squid),
            'squid_bias_johnson' : self.demod.calc_squid_bias_johnson_noise(self.squid),
        }
        self.demod.total_noise = self.demod.calc_total_noise()
    
    def calc_squid_noise(self):
        self.squid.total_noise = self.squid.calc_squid_noise(self.demod)
    
    def calc_bolo_noise(self):
        self.bolo.noise = {
            'johnson' : self.bolo.calc_johnson_noise(self.freqs)
        }
        self.bolo.total_noise = self.bolo.calc_total_noise()
        
    def calc_total_noise(self):
        self.total_noise = np.sqrt(self.demod.total_noise**2
                                   + self.nuller.total_noise**2
                                   + self.carrier.total_noise**2
                                   + self.bolo.total_noise**2
                                   + self.squid.total_noise**2)