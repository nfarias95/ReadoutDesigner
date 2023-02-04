"""
this file contains functions useful for loading data
Nicole Farias Spring 2022
"""

import numpy as np
import yaml


def read_yaml_file(filename:str):
    """This function reads the content of a yaml file and returns it in the form  of a dictionary

    Args:
        filename (str): name of yaml file
    """
    
    with open(filename, 'r') as file: 
        data = yaml.safe_load(file)
        
    return data


def local_main():
    # for testing
    read_yaml_file('config.yaml')
    print("hey it worked")

if __name__ == "__main__":
    local_main()

