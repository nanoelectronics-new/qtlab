from numpy import pi, random, arange, size, mod, reshape, mean
from time import time,sleep
import datetime
import UHFLI_lib
import matplotlib.pyplot as plt
import math


#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)


name = "5-24 By=2T diagonal dac upper part of peak 4"

stepsize = 0.06

dot_vec = arange(2196.39,2200.21,stepsize*1.65)     
sens_vec = arange(2495.57,2493.35,-stepsize)  

UHFLI_lib.UHF_init_scope()  # Initialize UHF LI
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
data = qt.Data(name=name)


# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.
data.add_coordinate('Line_num')
data.add_coordinate('Num of samples')
data.add_value('Reflection [Arb. U.]')
#data.add_value('Pulse Voltage [V]')

# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.
data.create_file()

try:   
    data_path = data.get_dir()

    # Next two plot-objects are created. First argument is the data object
    # that needs to be plotted. To prevent new windows from popping up each
    # measurement a 'name' can be provided so that window can be reused.
    # If the 'name' doesn't already exists, a new window with that name
    # will be created. For 3d plots, a plotting style is set.
    plot3d = qt.Plot3D(data, name='0109_4', coorddims=(0,1), valdim=2, style='image', autoupdate = False)
    #plot2d = qt.Plot2D(data, name=name, autoupdate=True)
    #plot2d.set_style('lines')

    

    # readout
    for i in xrange(len(dot_vec)):
        print i 
        IVVI.set_dac5(sens_vec[i])
        IVVI.set_dac7(dot_vec[i])
        result = UHFLI_lib.UHF_measure_scope_single_shot(maxtime = 0.5)  # Collecting the result from UHFLI buffer
        ch1 = result[0]         # Taking readout from the first channel
        data.add_data_point(np.linspace(i, i, ch1.size), np.linspace(0, ch1.size, ch1.size), ch1)  # Adding new data point
        qt.msleep(0.05)  # Sleeping for keeping GUI responsive
        data.new_block()  # Need to be here

    

    

    # Saving UHFLI setting to the measurement data folder
    # You can load this settings file from UHFLI user interface 
    UHFLI_lib.UHF_save_settings(path = data_path)  
    

   

finally:
    plot3d.update()  
    

   
    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
