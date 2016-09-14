from memory_profiler import profile
import numpy as np

@profile(precision=4)

def convert_to_matrix_file(fname = None, path = None):
    
    if fname is None or path is None:
        raise Exception("File name and path must be passed!")

    file_name = fname
    
    file_path = path 

    full_name = file_path + "/" + file_name


    first_col = np.loadtxt(fname = full_name, usecols= (0,), dtype =np.int16)  # Reading the first column 
    trc_num = first_col[-1] # Last element of the first column is number of traces
    del first_col # Freeing up memory
 
    third_col = np.loadtxt(fname = full_name, usecols= (2,), dtype =np.float16)  # Reading the third column - scope channel 1 
    fourth_exists = False
    try: # It can happen that there is no fourth column which will give an error - try finally combination skips this error
        fourth_col = np.loadtxt(fname = full_name, usecols= (2,), dtype =np.float16)  # Reading the fourth column - scope channel 2 
        fourth_exists = True # Flag indicating that fourth column exists
    finally:
   
        row_num = len(third_col)/trc_num  # Calculating rows number - to lower
        third_col = third_col[:row_num*trc_num] # Rounding number of elements to row_num*trc_num for the reshape function to work
        third_col.reshape((row_num,trc_num),order = 'F')
    
        if fourth_exists:
            row_num = len(fourth_col)/trc_num  # Calculating rows number - to lower
            fourth_col = fourth_col[:row_num*trc_num] # Rounding number of elements to row_num*trc_num for the reshape function to work
            fourth_col.reshape((row_num,trc_num),order = 'F')
            
    
   
   
    
        #Saving readout data from channel 1
        np.savetxt(fname=full_name + "_CH1matrix", X=third_col, fmt='%1.4e', delimiter=' ', newline='\n')  
    
    
        #Saving readout data from channel 2
        np.savetxt(fname=full_name + "_CH2matrix", X=fourth_col, fmt='%1.4e', delimiter=' ', newline='\n')  
    
    
    
    
    
    
    
                
            


