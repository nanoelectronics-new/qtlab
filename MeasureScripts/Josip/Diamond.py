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

file_name = '1_3 IV 433'

gain = 1000e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

# you define two vectors of what you want to sweep. In this case
# a magnetic field (b_vec) and a frequency (f_vec)



v1_vec = arange(-379.0,-384.0,-0.1)   #V_G 4
v2_vec = arange(-268.0,-271.0,-0.1)  #V_G 2


#
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
data.add_coordinate('V_G 2 [mV]')
data.add_coordinate('V_G 4 [mV]')
data.add_value('Current [pA]')

# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.
data.create_file()

data_path = data.get_dir()

#saving directly in matrix format for diamond program
new_mat = np.zeros((len(v2_vec), len(v1_vec))) # Creating empty matrix for storing all data   - ADD THIS LINE FOR MATRIX FILE SAVING, PUT APPROPRIATE VECTOR NAMES

# Next two plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.
plot2d = qt.Plot2D(data, name=file_name+ "_2D",autoupdate=False)
plot3d = qt.Plot3D(data, name=file_name+ "_3D", coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly



# preparation is done, now start the measurement.
# It is actually a simple loop.

init_start = time()
vec_count = 0

try:
    for i,v1 in enumerate(v1_vec):  # CHANGE THIS LINE FOR MATRIX FILE SAVING
        
        
        start = time()
        # set the voltage
        #IVVI.set_dac2(v1)
        #IVVI.set_dac12(v1) 
        #IVVI.set_dac4(v1)
        IVVI.set_dac5(v1)
        #IVVI.set_dac6(v1)
        #IVVI.set_dac2(v1)
        #IVVI.set_dac8(v1)

        
        for j,v2 in enumerate(v2_vec):  # CHANGE THIS LINE FOR MATRIX FILE SAVING

            IVVI.set_dac6(v2)

            # readout
            result = dmm.get_readval()/gain*1e12
        
            # save the data point to the file, this will automatically trigger
            # the plot windows to update
            data.add_data_point(v2,v1, result)  

            # Save to the matrix
            new_mat[j,i] = result   # ADD THIS LINE FOR MATRIX FILE SAVING

            # the next function is necessary to keep the gui responsive. It
            # checks for instance if the 'stop' button is pushed. It also checks
            # if the plots need updating.
            qt.msleep(0.001)
        data.new_block()
        stop = time()
        

        plot2d.update()

        plot3d.update()

        vec_count = vec_count + 1
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(v1_vec.size - vec_count))))
        
        

    print 'Overall duration: %s sec' % (stop - init_start, )

finally:

    # This part kicks out trailing zeros and last IV if it is not fully finished (stopped somwhere in the middle)  # ADD THIS BLOCK FOR MATRIX FILE SAVING
    for i, el in enumerate(new_mat[0]):     
        all_zeros = not np.any(new_mat[:,i])    # Finiding first column with all zeros
        if all_zeros:
            new_mat = new_mat[:,0:i-1]          # Leving all columns until that column, all the other are kicked out
            break

    # Saving the matrix to the matrix filedata.get_filepath
    np.savetxt(fname=data.get_filepath() + "_matrix", X=new_mat, fmt='%1.4e', delimiter=' ', newline='\n')   # ADD THIS LINE FOR MATRIX FILE SAVING

   
    # Converting the output file into matrix format which can be read with Diamond plot tool. It is in the same folder as original file.   
    #cnv.convert_to_matrix_file(fname = file_name, path = data_path)

    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
