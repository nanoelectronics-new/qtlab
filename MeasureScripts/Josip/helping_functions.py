import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib
import numpy as np

def save_the_plot(to_plot, title, x, y, x_label, y_label, c_label, dire):
    '''Function plotting and saving the matrix data
        Inputs:
            to_plot: numpy array to plot (matrix)
            title: title of the plot
            x: x axis values
            y: y axis values
            labels are labels of the axes - strings
            dir: path to the save directory
            name: name of the saved figure'''

    fig, ax = plt.subplots()
    im = ax.imshow(np.flipud(to_plot), aspect = 'equal', cmap = "brg", interpolation = 'None', extent=[x[0],x[-1],y[0],y[-1]])
    ax.ticklabel_format(axis = 'both', style = 'sci', scilimits = (-2,3))
    ax.set_xlabel(x_label, size = 24)
    ax.set_ylabel(y_label, size = 24)
    ax.set_title(title, size = 18)
    cbar = fig.colorbar(im, ax = ax)
    cbar.set_label(c_label, size = 24)
    lo = Labeloffset(ax, label=x_label, axis="x")
    lo = Labeloffset(ax, label=y_label, axis="y")
    matplotlib.rcParams.update({'font.size': 18})
    fig.savefig(dire + '\\' + title + '.png', bbox_inches = 'tight')





class Labeloffset():
    '''The following automates setting the scientific exponent next to the axis label, using a class with a callback, 
    such that if the offset changes, it will be updated in the label.'''
    def __init__(self,  ax, label="", axis="y"):
        self.axis = {"y":ax.yaxis, "x":ax.xaxis}[axis]
        self.label=label
        ax.callbacks.connect(axis+'lim_changed', self.update)
        ax.figure.canvas.draw()
        self.update(None)

    def update(self, lim):
        fmt = self.axis.get_major_formatter()
        self.axis.offsetText.set_visible(False)
        self.axis.set_label_text(self.label + " "+ fmt.get_offset() )





def aray_diferente(v1_start, v1_stop, small_spacing = 0.18, big_spacing = 20.0):

    v1_start = v1_start
    v1_stop = v1_stop
    # Checking the direction of the array to be
    if v1_stop - v1_start > 0:
        pos_direction = 1
    else:
        pos_direction = 0
    
    v1_vec = np.array([v1_start])
    # Spacings always positive
    small_spacing = abs(small_spacing)
    big_spacing = abs(big_spacing)
    k = 0
    while True:
        if pos_direction == 1:
            if v1_vec[k] > v1_stop:
                break
            if ((k%3 == 0)&(k>0)):
                v1_vec = np.append(v1_vec, v1_vec[k] + big_spacing)
            else:
                v1_vec = np.append(v1_vec, v1_vec[k] + small_spacing)
        
        elif pos_direction == 0:
            if v1_vec[k] < v1_stop:
                break
            if ((k%3 == 0)&(k>0)):
                v1_vec = np.append(v1_vec, v1_vec[k] - big_spacing)
            else:
                v1_vec = np.append(v1_vec, v1_vec[k] - small_spacing)
        k = k + 1
    return v1_vec[:len(v1_vec)-1]

