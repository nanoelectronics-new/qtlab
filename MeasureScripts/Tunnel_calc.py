import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.lines as mlines


def Tunnel_calc(fname = None, path = None, sampling_rate = 7.03e6, load_time = 4000e-6, read_time = 500e-6):
    '''
    Function for calculating the tunneling time.
    
    
    Input:
            fname (string) : matrix file name
            path (string) : path to the folder containing data
            sampling_rate (float) : Scope sampling rate in Samples/second
            load_time (float) : Duration of load time in seconds
            read_time (float) : Duration of read time in seconds
                      
            
    Output:
            Tunnel time in us
            Plots mean value of all traces in passed matrix file
            Plots exponential fit to experimental values
            
    Returns:
        None
    '''
    
    
    if fname is None or path is None:
        raise Exception("File name and path must be passed!")
   
  
    
    mat = np.loadtxt(path + '/' + fname)    # Loading the data from matrix file
    
    
    nums = int(sampling_rate * load_time)    
    numend = int(nums + sampling_rate * read_time) 
    
    new_mat = mat[nums:numend, :]
    
    mean_trace = new_mat.mean(1)
    
    
    
    x = np.linspace(0, len(mean_trace), len(mean_trace))
    t = np.linspace(0, read_time, len(mean_trace))
    
    
    
    
    # Fitting histogram for tunneling time extraction 
    def func(x, a, b, c):  # Fitting function 
        return a * np.exp(-b * x) + c
    
    """
    make the curve_fit
    """
    
    popt, pcov = curve_fit(func,x,mean_trace)
    
    a = popt[0]
    b = popt[1]
    c = popt[2]
    
    
    
    Ttunnel = (1.0/b)*1e6*read_time/len(mean_trace)
    print "Tunnel out time is: %f us"%Ttunnel 
    
    
    
    plt.plot(t, func(x,a,b,c), "r")
    plt.plot(t,mean_trace, "g")
    plt.xlabel("time [s]")
    plt.ylabel("amplitude [a.u.]")
    plt.title("read interval vs time")
    plt.legend("green - experimental")
    
    blue_line = mlines.Line2D([], [], color='green',
        markersize=15, label='Experimental')
    green_line = mlines.Line2D([], [], color='red',
        markersize=15, label='Exp fit')
    plt.legend(handles=[blue_line, green_line])
    plt.show()