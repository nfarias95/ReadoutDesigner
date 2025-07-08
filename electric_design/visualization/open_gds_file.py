""" 
    This code is a simple gds file viewer
    For basic operations, see: https://gdspy.readthedocs.io/en/stable/gettingstarted.html?highlight=viewer#first-gdsii
"""

import gdspy



print("\nHello!")

# Load a GDSII file into a new library
folder = 'C:/Users/nicol/Documents/00Research/GDS Files/'
filename = 'flex_cable_wafer_v4.gds'
gdsii = gdspy.GdsLibrary(infile=folder+filename)

#print(gdsii)

gdspy.LayoutViewer(gdsii)

print("\n\nDone.\n--------\n\n")