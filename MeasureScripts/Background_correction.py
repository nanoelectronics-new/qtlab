from memory_profiler import profile
from os import walk, remove
import numpy as np
import matplotlib.pyplot as plt

#@profile(precision=4)




def Back_corr(path = None, fname = None):

    file_path = path + "/" + fname
    mat = np.loadtxt(file_path)

    #plt.figure("Before  substraction")
    #plt.imshow(mat)



    for col, element in enumerate(mat[0]):
        processed_column = mat[:,col] 
        mat[:,col] = processed_column - np.mean(processed_column)  # Substracting the mean of the column from the column itself

    for row, element in enumerate(mat[:,0]):
        processed_row = mat[row,:] 
        mat[row,:] = processed_row - np.mean(processed_row)  # Substracting the mean of the column from the column itself

    

    #plt.figure("After  substraction")
    #plt.imshow(mat)

    #plt.show()
         
    np.savetxt(fname=path + "/" + "CORR_" + fname, X=mat, fmt='%1.4e', delimiter=' ', newline='\n')  
    return mat
