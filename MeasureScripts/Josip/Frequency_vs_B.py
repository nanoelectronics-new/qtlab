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
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54505188::INSTR')
#dmm.set_NPLC = 1  # Setting PLCs of dmm
#magnetZ = qt.instruments.create('magnetZ', 'AMI430_Bz', address='10.21.64.176')
#magnetY = qt.instruments.create('magnetY', 'AMI430_By', address='10.21.64.184')
#VSG = qt.instruments.create('VSG','RS_SMW200A',address = 'TCPIP::10.21.64.105::hislip0::INSTR')
#dmm_lockin = qt.instruments.create('dmm_lockin','a34410a', address = 'USB0::0x2A8D::0x0101::MY54505188::INSTR')

file_name = '1_3 IV 93'

gain = 1000e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

#magnet
#ramp_rate_Z = 0.001 #T/s
ramp_rate_Y = 0.0008 #T/s


#step_size_BZ = 2e-3 
step_size_BY = 1e-3 
#BZ_vector = arange(425e-3,490e-3+step_size_BZ,step_size_BZ) #T  # Those two vectors need to be the same left
BY_vector = arange(149e-3,250e-3+step_size_BY,step_size_BY) #T  #

#if len(BZ_vector) != len(BY_vector):
#    raise Exception ("B vectors have different length")

#ramp_time = max(abs((float(step_size_BY)/ramp_rate_Y)),abs(float(step_size_BZ)/ramp_rate_Z))
#ramp_time = 1.2*ramp_time

#magnetZ.set_rampRate_T_s(ramp_rate_Z)
magnetY.set_rampRate_T_s(ramp_rate_Y)


freq_vec = arange(6.0e9,7.0e9,3e6)  # frequency 



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

#saving directly in matrix format for diamond program
new_mat = np.zeros((len(freq_vec), len(BY_vector)),dtype=float16) # Creating empty matrix for storing all data   - ADD THIS LINE FOR MATRIX FILE SAVING, PUT APPROPRIATE VECTOR NAMES

# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.
data.add_coordinate('Frequency [Hz]')  #v2
data.add_coordinate('Bfield [T]')   #v1
data.add_value('Current [pA]')

# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.
#data.create_file()

#data_path = data.get_dir()

# Next two plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.
plot2d = qt.Plot2D(data, name='measure2D_2',autoupdate=False)
plot3d = qt.Plot3D(data, name='measure3D_2', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly



# preparation is done, now start the measurement.
# It is actually a simple loop.

#IVVI.set_dac1(bias)

init_start = time()
vec_count = 0


try:
    for i,v1 in enumerate(BY_vector):  # CHANGE THIS LINE FOR MATRIX FILE SAVING
        
        
        start = time()
        # set the voltage
        #IVVI.set_dac5(v1)

        #magnetZ.set_field(BZ_vector[i])
        magnetY.set_field(BY_vector[i])  

        #total_field = np.sqrt(BZ_vector[i]**2 + BY_vector[i]**2)
        #total_field = np.sqrt(BZ_vector[i]**2)
        total_field = BY_vector[i]

        # changed BY to BZ
        while math.fabs(BY_vector[i] - magnetY.get_field_get()) > 0.0001:
            qt.msleep(0.050)






        for j,freq in enumerate(freq_vec):  # CHANGE THIS LINE FOR MATRIX FILE SAVING

            #IVVI.set_dac5(v2)

            VSG.set_frequency(freq)
            # readout
            result = dmm.get_readval()/gain*1e12
        
            # save the data point to the file, this will automatically trigger
            # the plot windows to update
            data.add_data_point(freq,total_field, result)  
        

            # Save to the matrix
            new_mat[j,i] = float16(result)   # ADD THIS LINE FOR MATRIX FILE SAVING

            # the next function is necessary to keep the gui responsive. It
            # checks for instance if the 'stop' button is pushed. It also checks
            # if the plots need updating.
            qt.msleep(0.001)
        data.new_block()
        stop = time()
        

        plot2d.update()

        plot3d.update()

        vec_count = vec_count + 1
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(BY_vector.size - vec_count))))
        
        

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
