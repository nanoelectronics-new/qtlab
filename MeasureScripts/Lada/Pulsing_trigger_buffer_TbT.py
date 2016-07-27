from numpy import pi, random, arange, size, mod, reshape, mean
from time import time,sleep
import datetime
import UHFLI_lib
import matplotlib.pyplot as plt
import math


#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
AWG = qt.instruments.get("AWG")
#name='pulsing,80uV -35dBm, -+500, +-600, 200us200us three-part-pulse 1000#' 
name = "5-24 By=2T,crazy sequence, W,L,W,R,E 700us"

Scope_sampling_rate =  7030000#Hz
Sequence_duration = 0.5065 #s
Num_of_pulses = 100 # Sequence length - correspond to number of rows in slice matrix

Signal_level = 0.0015 # In Volts. AWG Marker level 

 



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
    plot3d = qt.Plot3D(data, name='crazy_seq1', coorddims=(0,1), valdim=2, style='image', autoupdate = False)
    #plot2d = qt.Plot2D(data, name=name, autoupdate=True)
    #plot2d.set_style('lines')

    #AWG._ins.stop()
    AWG._ins.run()  # Run AWG - Run must be before do_set_output
    AWG._ins.do_set_output(1,1)   # Turn on AWG ch1
    AWG._ins.do_set_output(1,2)   # Turn on AWG ch1



    # readout
    for i in xrange(Num_of_pulses):
        result = UHFLI_lib.UHF_measure_scope(AWG_instance = AWG, maxtime = 2) 
        ch1 = result[0]
        data.add_data_point(np.linspace(i, i, ch1.size), np.linspace(0, ch1.size, ch1.size), ch1)
        sleep(0.1)
        data.new_block()

    plot3d.update()

    

    # Saving UHFLI setting to the measurement data folder
    # You can load this settings file from UHFLI user interface 
    UHFLI_lib.UHF_save_settings(path = data_path)
    

   
        
    
    

    #plt.show()



finally:
    AWG._ins.do_set_output(0,1)   # Turn off AWG ch1
    AWG._ins.do_set_output(0,2)   # Turn off AWG ch1

   
    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
