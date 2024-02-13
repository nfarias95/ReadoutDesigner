import numpy as np
import csv
from matplotlib import pyplot as plt


data_folder = "C:/Users/nicol/Documents/00Research/Data/Dunk Probe/starcryo_cable/date_20230920_19mm_2000um/"
data_files = np.array(["WARM01.csv", "WARM02.csv", "COLD03.csv", "COLD04.csv", "COLD05.csv"])
    
def main():
    
    print("Hello. Let's look at the VNA data")
    
    for data_file in data_files:
        
        filepath = data_folder+data_file
        
        # initialize arrays
        freqs = np.array([])
        S11 = np.array([])
        
        # opening the CSV file
        with open(filepath, mode ='r') as file:
            # reading the CSV file
            csvFile = csv.reader(file)
    
            # displaying the contents of the CSV file
            line_counter = 0
            lines_to_skip = 17
            for line in csvFile:
                if line_counter > lines_to_skip: # skip the headers
                    # ignore last file
                    if len(line) >1:
                        freqs = np.append(freqs, float(line[0]) ) # frequency in Hz
                        S11 = np.append(S11, float(line[1]) ) # S11 in dB
                line_counter = line_counter + 1
        
        
        print(freqs[0:10])
        print(S11[0:10])
        plt.figure(1)
        plt.plot(freqs/1e6, S11)
        plt.xlim(0.3, 75)
        plt.xlabel("Frequency [MHz]")
        plt.ylabel("S21 [dB]")
        
    plt.show()
    
    print("The end")
    
    
if __name__ == "__main__":
    main()