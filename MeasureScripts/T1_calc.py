import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import sympy as sym
from os import walk, remove

def convert_to_matrix_file(fname = None, path = None):
    
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
    remove(file_path + '/' + 'tmp.txt')  # Removing the tmp file
    
    #Collecting readout data from channel 1
    new_mat = np.zeros((iv_count[0], len(iv_count)))
        
    left_of = 0
    
    for col,iv in enumerate(iv_count[:(len(iv_count)-1)]):
        new_mat[:,col] = mat[left_of:iv+left_of,2]    # Taking just third column of the data file - ch1 readout
 
        left_of += iv
        
    
    np.savetxt(fname=full_name + "_CH1matrix", X=new_mat, fmt='%1.4e', delimiter=' ', newline='\n')  
       
    return new_mat 
    
    



def T1_calc_with_conversion(fname = None, path = None, treshold = -0.0002, sampling_rate = 7.03e6, read_time = 500e-6):

    
    mypath = path
    f = []
    for (dirpath, dirnames, filenames) in walk(mypath):  # Getting all the file names from the data folder
        f.extend(filenames)
        break

    print "File names: ", f
    wait_time = []
    for i in f:
        wait_time.append(float(raw_input("Input wait time - order need to match the file order! :  ")))   # User input of wait_time


    
    dictionary = dict(zip(wait_time, f))  # Creating the dict: wait_time - keys and file names - values
    wait_time.sort()   # Sorting the wait_time (dictionary keys) 

    data_list = []
    for p in f:     # Going through all data files in the folder and converting to matrix and storing this matrixes in data_list
        data_list.append(convert_to_matrix_file(fname = p, path = mypath))

    count = [] # Event counting list - every element is number of events per one wait time
    for i, w_time in enumerate(wait_time):   # Going throug all wait_times

        new_mat = data_list[i]   # Dataset for current wait_time
        nums = sampling_rate * w_time    # Starting index of the read interval
        numend = nums + sampling_rate * read_time # Ending index of the read interval
        r_mat = new_mat[nums:numend, :]     # Matrix reduced just to read interval

    

        #if i == 0:      # Treshold input just for the first dataset - first wait_time
        vec = np.reshape(r_mat,(len(r_mat[0])*len(r_mat[:, 1])),order="F")  # Reshaping r_mat to vector for ploting read intervals adjacent to each other for easier determination of the treshold
  
        

        count_tmp = 0     # Counter for each wait_time

        for read_trace in r_mat.T:
            for el in read_trace:
                if el > treshold:
                    count_tmp +=1
                    break

        print count
        count.append(count_tmp)   

    plt.figure(1)
    # Making histogram
    plt.plot(wait_time, count, "o")
    plt.xlabel("time [s]")
    plt.ylabel("num of events")
    plt.title("histogram for T1")
    
    
    # Fitting histogram for tunneling time extraction 
    def func(x, a, b, c):  # Fitting function 
        return a * np.exp(-b * x) + c
    """
    make the curve_fit
    """
    
    popt, pcov = curve_fit(func, np.array(wait_time), np.array(count))
 
    a = popt[0]
    b = popt[1]
    c = popt[2]
  
    plt.plot(np.array(wait_time), func(np.array(wait_time),a,b,c), "g")
    
    plt.show()
    
    T1 = 1.0/b
    print "T1 is: %f s"%T1

    return count
    
    

    
def T1_calc(fname = None, path = None, treshold = -0.0002, sampling_rate = 7.03e6, read_time = 500e-6):

    mypath = path
    f = []
    for (dirpath, dirnames, filenames) in walk(mypath):  # Getting all the file names from the data folder
        f.extend(filenames)
        break

    print "File names: ", f
    wait_time = []
    for i in f:
        wait_time.append(float(raw_input("Input wait time - order need to match the file order! :  ")))   # User input of wait_time


    
    dictionary = dict(zip(wait_time, f))  # Creating the dict: wait_time - keys and file names - values
    wait_time.sort()   # Sorting the wait_time (dictionary keys) 

    data_list = []
    for key in wait_time:     # Going through all data files in the folder and loading them in data_list in a sorted manner (from smaller to bigger waiting time)
        data_list.append(np.loadtxt(mypath + '/' + dictionary[key]))



    count = [] # Event counting list - every element is number of events per one wait time
    for i, w_time in enumerate(wait_time):   # Going throug all wait_times

        new_mat = data_list[i]   # Dataset for current wait_time
        nums = sampling_rate * w_time    # Starting index of the read interval
        numend = nums + sampling_rate * read_time # Ending index of the read interval
        r_mat = new_mat[nums:numend, :]     # Matrix reduced just to read interval

    

        #if i == 0:      # Treshold input just for the first dataset - first wait_time
        #vec = np.reshape(r_mat,(len(r_mat[0])*len(r_mat[:, 1])),order="F")  # Reshaping r_mat to vector for ploting read intervals adjacent to each other for easier determination of the treshold
        #plt.plot(vec)
        #plt.show(block=False)
        

        count_tmp = 0     # Counter for each wait_time

        for read_trace in r_mat.T:
            for el in read_trace:
                if el > treshold:
                    count_tmp +=1
                    break

        print count
        count.append(count_tmp) 

    plt.figure(1)
    # Making histogram
    plt.plot(wait_time, count, "o")
    plt.xlabel("time [s]")
    plt.ylabel("num of events")
    plt.title("histogram for T1")
    
    
    # Fitting histogram for tunneling time extraction 
    def func(x, a, b, c):  # Fitting function 
        return a * np.exp(-b * x) + c
    """
    make the curve_fit
    """
    
    popt, pcov = curve_fit(func, np.array(wait_time), np.array(count))
 
    a = popt[0]
    b = popt[1]
    c = popt[2]
      
    plt.plot(np.array(wait_time), func(np.array(wait_time),a,b,c), "g")
    
    plt.show()
    
    T1 = 1.0/b
    print "T1 is: %f s"%T1

    return count


def plot_single(fname = None, path = None, sampling_rate = 7.03e6, read_time = 500e-6):

    mypath = path
    f = []        
    for (dirpath, dirnames, filenames) in walk(mypath):  # Getting all the file names from the data folder
        f.extend(filenames)
        break

    print "File names: ", f

    index = int(raw_input("Input the index of the file you want to plot (starting from 0):  ")) # User need to input the index of the matrix file to plot
    w_time = float(raw_input("Input wait time in sec:  ")) # User need to put in the wait time

    new_mat = np.loadtxt(mypath + '/' + f[index])  # Reading the wanted matrix file

    nums = sampling_rate * w_time    # Starting index of the read interval
    numend = nums + sampling_rate * read_time # Ending index of the read interval
    r_mat = new_mat[nums:numend, :]     # Matrix reduced just to read interval

    vec = np.reshape(r_mat,(len(r_mat[0])*len(r_mat[:, 1])),order="F")  # Reshaping r_mat to vector for ploting read intervals adjacent to each other for easier determination of the treshold
    plt.plot(vec)
    plt.show()

