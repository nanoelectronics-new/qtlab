import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import sympy as sym
import os

def calc_widths(fname = None, path = None, trace_duration = 50, trace_num = 5, treshold = -0.00002):
    
    if fname is None or path is None:
        raise Exception("File name and path must be passed!")

    import numpy as np

    def isfloat(value):
        try:
            float(value)
            return True
        except:
            return False


    file_name = fname
    
    file_path = path 

    full_name = file_path + "/" + file_name
    
    mat = []

    f = open(full_name,"r") # Open file
    lines = f.readlines()  # Read file
    
    iv_count = [0]
    iv_num = 0
    
        
    tmp = open(file_path + "/" +'tmp.txt','w')  #  Open temp file
    
    for i,line in enumerate(lines[:len(lines)-1]):  # Skip the last ugly row
        if isfloat(line[:3]):
            tmp.write(line)  # Fill the buffer file skipping unneccesarry lines
            iv_count[iv_num] += 1 
        elif i > 30 and line == "\n":  # Splitting separate IV traces
            iv_count.append(0)
            iv_num += 1 
            
    
    del lines            
    tmp.close()
    
    
    mat = np.loadtxt(file_path + "/" +'tmp.txt')
    os.remove(file_path + '/' + 'tmp.txt')  # Removing the tmp file
    
    #Collecting readout data from channel 1
    new_mat = np.zeros((iv_count[0], len(iv_count)))
        
    left_of = 0
    
    for col,iv in enumerate(iv_count[:(len(iv_count)-1)]):
        new_mat[:,col] = mat[left_of:iv+left_of,2]    # Taking just third column of the data file - ch1 readout
 
        left_of += iv
         
           
    going_up = 0
    vec = new_mat[:,trace_num]
    tresh = treshold
    widths_up = list()
    widths_down = list()
    index_up = list()
    index_down = list()
    
    for i,el in enumerate(vec[1:]):
        if el>tresh and going_up ==0 and vec[i-1]<tresh and vec[i+1]>tresh:
            widths_up.append(el)
            index_up.append(i)
            going_up =1
        if el<tresh and going_up ==1 and vec[i-1]>tresh and vec[i+1]<tresh:
            widths_down.append(el)
            index_down.append(i)
            going_up =0
            
            
    t = np.linspace(0, trace_duration, len(vec) )
    index_up = np.array(index_up)*(float(trace_duration)/len(vec))
    index_down = np.array(index_down)*(float(trace_duration)/len(vec))
    plt.plot(t,vec)
    plt.plot(index_up,widths_up,"ro")
    plt.plot(index_down,widths_down,"go")
    plt.xlabel("time [ms]")
    plt.ylabel("amplitude [a.u.]")
    plt.title("tunnel jumps vs time")
    
    plt.show()
    
    #widths_up = widths_up[0:len(widths_down)-1]  # making widths_up and widths_down the same in length
    widths = np.array(index_down) - np.array(index_up) 
    
    plt.figure(2)
    # Making histogram
    hist = np.histogram(widths, 10)
    bins = (hist[1][1:]+hist[1][0:-1])/2 # Calculating histogram bins - x values
    bins = np.array(bins, dtype=float)  # Converting to float for the fitting function to work
    hist = hist[0] # Histogram values - y values
    hist = np.array(hist, dtype=float)  # Converting to float for the fitting function to work
    plt.plot(bins, hist, "o")
    plt.xlabel("time [ms]")
    plt.ylabel("num of occurrences")
    plt.title("histogram")
    
    
    # Fitting histogram for tunneling time extraction 
    def func(x, a, b, c):  # Fitting function 
        return a * np.exp(-b * x) + c
    """
    make the curve_fit
    """
    
    popt, pcov = curve_fit(func, bins, hist)
 
    a = popt[0]
    b = popt[1]
    c = popt[2]
    
    plt.plot(bins, func(bins,a,b,c), "g")
    
    plt.show()
    
    Tout = 1.0/b
    print "Tunnel out time is: %f ms"%Tout
        
    return Tout
    
    

