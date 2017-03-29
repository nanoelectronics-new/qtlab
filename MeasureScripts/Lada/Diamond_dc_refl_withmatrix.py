from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import UHFLI_lib



#####################################################
#This script runs reflectometry and dc diamond measurement in parallel and saves both as a matrix file. Not tested yet with a real diamond plot, but it saves what it should I thinl
#####################################################

#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x0957::0x0607::MY53003401::INSTR')   # Initialize dmm
UHFLI_lib.UHF_init_demod(demod_c = 3)  # Initialize UHF LI


#file_name = '5-24 gate vs gate, sensor jumping, bias=300uV reflectometry only, -40dB'

gain = 1e9 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

#bias = 300


gain_Lockin = 1 # Conversion factor for the Lockin


v1_vec = arange(0,-100,-1)     #V_g
v2_vec = arange(-500,500,100)  #V_sd 


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

data_refl = qt.Data(name='24-21 refl test script') #just renamed

data_dc = qt.Data(name='24-21 dc test script') #added to have current recored as well

data_path_refl = data_refl.get_dir()
data_path_dc = data_dc.get_dir()

#saving directly in matrix format for diamond program
new_mat_r = np.zeros((len(v2_vec), len(v1_vec))) # Creating empty matrix for storing all data   - ADD THIS LINE FOR MATRIX FILE SAVING, PUT APPROPRIATE VECTOR NAMES
new_mat_dc = np.zeros((len(v2_vec), len(v1_vec))) # Creating empty matrix for storing all data   - ADD THIS LINE FOR MATRIX FILE SAVING, PUT APPROPRIATE VECTOR NAMES

# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.

data_dc.add_coordinate('V_G (sensor) [mV]')
data_dc.add_coordinate('V_G (dot) [mV]')
data_dc.add_value('Current [pA]')


data_refl.add_coordinate('V_G (sensor) [mV]')
data_refl.add_coordinate('V_G (dot) [mV]')
data_refl.add_value('Reflection [Arb. U.]')


# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.

data_dc.create_file()
data_refl.create_file()


# Next two plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.

plot2d_refl = qt.Plot2D(data_refl, name='refl',autoupdate=False)
plot3d_refl = qt.Plot3D(data_refl, name='refl3D', coorddims=(1,0), valdim=2, style='image')

plot2d_dc = qt.Plot2D(data_dc, name='measure2D',autoupdate=False)
plot3d_dc = qt.Plot3D(data_dc, name='measure3D', coorddims=(1,0), valdim=2, style='image')



# preparation is done, now start the measurement.
# It is actually a simple loop.

init_start = time()
vec_count = 0

try:
    for i, v1 in enumerate(v1_vec):
        
        
        start = time()
        # set the voltage
        IVVI.set_dac5(v1)


        for j,v2 in enumerate(v2_vec):

            IVVI.set_dac1(v2)

            # readout
            result_reflectometry = UHFLI_lib.UHF_measure_demod(Num_of_TC = 3)  # Reading the lockin and correcting for M1b gain

            new_mat_r[j,i] = result_reflectometry #for saving as matrix
            
            result_dc = dmm.get_readval()/gain*1e12

            new_mat_dc[j,i] = result_dc #for saving as matrix

            data_refl.add_data_point(v2, v1, result_reflectometry) 
            data_dc.add_data_point(v2, v1, result_dc) 
        
            # save the data point to the file, this will automatically trigger
            # the plot windows to update
           
            # the next function is necessary to keep the gui responsive. It
            # checks for instance if the 'stop' button is pushed. It also checks
            # if the plots need updating.
            qt.msleep(0.001)
        data_refl.new_block()
        data_dc.new_block()

        stop = time()
        

        plot2d_refl.update()
        plot3d_refl.update() 

        plot2d_dc.update()
        plot3d_dc.update() 

        vec_count = vec_count + 1
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(v1_vec.size - vec_count))))
        
        

    print 'Overall duration: %s sec' % (stop - init_start, )

   
finally:

    # This part kicks out trailing zeros and last IV if it is not fully finished (stopped somwhere in the middle)  # ADD THIS BLOCK FOR MATRIX FILE SAVING
    for i, el in enumerate(new_mat_r[0]):     
        all_zeros = not np.any(new_mat_r[:,i])    # Finiding first column with all zeros
        if all_zeros:
            new_mat_r = new_mat_r[:,0:i-1]          # Leving all columns until that column, all the other are kicked out
            break

    # Saving the matrix to the matrix filedata.get_filepath
    np.savetxt(fname=data_refl.get_filepath() + "_matrix", X=new_mat_r, fmt='%1.4e', delimiter=' ', newline='\n')   # ADD THIS LINE FOR MATRIX FILE SAVING

    for i, el in enumerate(new_mat_dc[0]):     
        all_zeros = not np.any(new_mat_dc[:,i])    # Finiding first column with all zeros
        if all_zeros:
            new_mat_dc = new_mat_dc[:,0:i-1]          # Leving all columns until that column, all the other are kicked out
            break

    # Saving the matrix to the matrix filedata.get_filepath
    np.savetxt(fname=data_dc.get_filepath() + "_matrix", X=new_mat_dc, fmt='%1.4e', delimiter=' ', newline='\n')   # ADD THIS LINE FOR MATRIX FILE SAVING
       
    # Saving UHFLI setting to the measurement data folder
    # You can load this settings file from UHFLI user interface 3
    UHFLI_lib.UHF_save_settings(path = data_path_refl)


    # after the measurement ends, you need to close the data file.
    data_refl.close_file()
    data_dc.close_file()
    #data_current.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()