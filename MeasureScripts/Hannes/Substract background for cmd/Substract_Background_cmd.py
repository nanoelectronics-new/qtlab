# open matrix file and remove background (linetrace as reference)


import numpy as np
import numpy.matlib 
import matplotlib.pyplot as plt

M = np.loadtxt("C:/QTLab/qtlab/MeasureScripts/Hannes/Substract background for cmd/190815_15_17 IV 454.dat", unpack=True)

m,n = M.shape

#if M1.shape != M2.shape:
#    raise Exception ("Files are of different size")

M_corr = np.zeros(shape=(m,n))

linetr = M[2,:]

for i in range(m):
    for j in range(n):
         M_corr[i,j] = M[i,j] - M[2,j]
        
    #M_corr[i,:] = M[i,:] - M[0,:]



#for i in range(m):
#    for j in range (n):
#        M_av[i,j]=(M1[i,j]+M2[i,j]+M3[i,j])/2

np.savetxt('C:/QTLab/qtlab/MeasureScripts/Hannes/Substract background for cmd/Background_Corrected_IV 454.dat',M_corr.T)