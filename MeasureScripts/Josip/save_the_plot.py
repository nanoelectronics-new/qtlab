import matplotlib.pyplot as plt
import matplotlib
import numpy as np

def save_the_plot(to_plot, title, x, y, x_label, y_label, c_label, dire):
    '''Function the plot and save the matrix data
        Inputs:
            to_plot: numpy array to plot (matrix)
            title: title of the plot
            x: x axis values
            y: y axis values
            labels are labels of the axes - strings
            dir: path to the save directory
            name: name of the saved figure'''

    fig, ax = plt.subplots()
    im = ax.imshow(np.flipud(to_plot), aspect = "auto", cmap = "bwr_r", extent=[x[0],x[-1],y[0],y[-1]])
    ax.set_xlabel(x_label, size = 24)
    ax.set_ylabel(y_label, size = 24)
    ax.set_title(title, size = 24)
    cbar = fig.colorbar(im, ax = ax)
    cbar.set_label(c_label, size = 24)
    matplotlib.rcParams.update({'font.size': 18})
    fig.savefig(dire + '\\' + title + '.png', bbox_inches = 'tight')