from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import numpy as np

#####################################################
# this part is to simulate some data, you can skip it
#####################################################




#####################################################
# here is where the actual measurement program starts
#####################################################
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM3', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x0957::0x0607::MY53003401::INSTR')
#dmm.set_NPLC = 1  # Setting PLCs of dmm

file_name = 'test_matrix_saving'

gain = 1000e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

# you define two vectors of what you want to sweep. In this case
# a magnetic field (b_vec) and a frequency (f_vec)




v1_vec = arange(5.0,-15,-0.2)  #Power
tau_vector_repetitions = 200


# you indicate that a measurement is about to start and other
# processes should stop (like batterycheckers, or temperature
# monitors)
qt.mstart()

# Next a new data object is made.
# The file will be placed in the folder:
# <datadir>/<datestamp>/<timestamp>_testmeasurement/
# and will be called:
# <timestamp>_testmeasurement.dat
# to find out what 'datadir' is set to, type: qt.config.get('datadir')
data = qt.Data(name=file_name)

# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.
data.add_coordinate('t_burst [ns]')
data.add_coordinate('Power [dBm]')
data.add_value('Current [pA]')

# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.
data.create_file()

data_path = data.get_dir()

#saving directly in matrix format for diamond program
new_mat = np.zeros(len(t_burst)) # Creating empty matrix for storing all data   

# Next two plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.
plot2d = qt.Plot2D(data, name='measure2D',autoupdate=False)
plot3d = qt.Plot3D(data, name='measure3D', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly

tau_vector = np.zeros(len(t_burst)) # Empty vector for averaging intermediate tau result vectors
VSG.set_status("on") # Turn the RF on 
# preparation is done, now start the measurement.
# It is actually a simple loop.

init_start = time()
vec_count = 0

try:
    for i,v1 in enumerate(v1_vec): 
        
        
        start = time()
        VSG.set_power(v1)
  

        for i in xrange(tau_vector_repetitions):  #repeat the one tau vector measurement n times
            for j,v2 in enumerate(t_burst):  
    
                AWG._ins.force_event()
    
                # readout
               
               
                tau_vector[j] += dmm.get_readval()/gain*1e12
                
                
                
                
    
                # Save to the matrix
                
    
                # the next function is necessary to keep the gui responsive. It
                # checks for instance if the 'stop' button is pushed. It also checks
                # if the plots need updating.
                qt.msleep(0.002)

        # Calculate the average value of the recorded tau vector
        tau_vector = tau_vector/tau_vector_repetitions
        # save the data point to the file    
        v111 = np.linspace(v1,v1,len(t_burst))  # Vector with repeating value of v1 for length of tau vector - for saving
        data.add_data_point(t_burst*1e3,v111,tau_vector)  
        data.new_block()
        stop = time()

        new_mat = np.column_stack((new_mat,tau_vector))   # Gluing new tau_vector to the present matrix
        if not(i): #Kicking out the first column filled with zero
            new_mat = new_mat[:,1:]

        np.savetxt(fname = data.get_filepath()+ "_matrix", X = new_mat, fmt = '%1.4e', delimiter = '', newline = '\n')
        

        plot2d.update()

        plot3d.update()

        vec_count = vec_count + 1
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(v1_vec.size - vec_count))))
        
        

    print 'Overall duration: %s sec' % (stop - init_start, )

finally:

    ## This part kicks out trailing zeros and last IV if it is not fully finished (stopped somwhere in the middle)  # ADD THIS BLOCK FOR MATRIX FILE SAVING
    #for i, el in enumerate(new_mat[0]):     
    #    all_zeros = not np.any(new_mat[:,i])    # Finiding first column with all zeros
    #    if all_zeros:
    #        new_mat = new_mat[:,0:i-1]          # Leving all columns until that column, all the other are kicked out
    #        break
#
    # Saving the matrix to the matrix filedata.get_filepath
    #np.savetxt(fname=data.get_filepath() + "_matrix", X=new_mat, fmt='%1.4e', delimiter=' ', newline='\n')   # ADD THIS LINE FOR MATRIX FILE SAVING

    VSG.set_status("off") # Switching off the RF 
    # Converting the output file into matrix format which can be read with Diamond plot tool. It is in the same folder as original file.   
    #cnv.convert_to_matrix_file(fname = file_name, path = data_path)

    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
