FONT = "Times New Roman"
FONT_SIZE = 20
LEGEND_SIZE = 17
FIG_SIZE = (10, 8) # size of figure
markersize=12

from matplotlib import pyplot as plt
plt.rcParams["font.family"] = FONT
plt.rcParams.update({'font.size': FONT_SIZE})
plt.rc('legend', fontsize=LEGEND_SIZE)    # legend fontsize

import matplotlib as mpl
mpl.rcParams['figure.facecolor'] = 'white'# necessary in jupyter notebook in visual studio code


def remove_ticks():
    plt.tick_params(axis='both',          # Changes apply to both x and y axis
                    which='both',         # Apply changes to both major and minor ticks
                    bottom=False,         # Remove ticks along the bottom edge
                    top=False,            # Remove ticks along the top edge
                    left=False,           # Remove ticks along the left edge
                    right=False,          # Remove ticks along the right edge
                    labelbottom=False,    # Remove labels along the bottom edge
                    labeltop=False,       # Remove labels along the top edge
                    labelleft=False,      # Remove labels along the left edge
                    labelright=False)     # Remove labels along the right edge