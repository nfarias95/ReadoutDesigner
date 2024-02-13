import yaml

output_file = "config.yaml"

params = {} # a dictionary to store relevant parameters

params['Rtes_normal'] = 1 # [ohm] : normal resistance of TES
params['Rfrac'] = 0.7 # fraction of normal resistancecd 

with open(output_file, 'w') as file:
    yaml.dump( params, file)
    
print("Created config file: ", output_file)