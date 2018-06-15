from numpy import pi, random, arange, size
from time import time,sleep
import UHFLI_lib
import numpy as np



#####################################################
# EXAMPLE SCRIPT SHOWING HOW TO SET UP STANDARD 1D (IV) LOCKIN MEASUREMENT
#####################################################
def do_meas():
    """Better to put this into a function, not to mess with already existing varibales with the same name"""



    UHFLI_lib.UHF_init_scope()  # Initialize UHF LI
    gain = 1e9 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    power = -4.0
    bias = -1000
    
    leak_test = True
    
    # you define two vectors of what you want to sweep. In this case
    # a magnetic field (b_vec) and a frequency (f_vec)
    freq_vec = arange(5.3e9,6.3e9,3e6)  # frequency 
    
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
    
    data = qt.Data(name='IV 646')  # Put one space before name
    
    
    # Now you provide the information of what data will be saved in the
    # datafile. A distinction is made between 'coordinates', and 'values'.
    # Coordinates are the parameters that you sweep, values are the
    # parameters that you readout (the result of an experiment). This
    # information is used later for plotting purposes.
    # Adding coordinate and value info is optional, but recommended.
    # If you don't supply it, the data class will guess your data format.
    
    data.add_coordinate('Frequency [Hz]')   # Underline makes the next letter as index
    
    data.add_value(' Current_lockin [pA]')      # Underline makes the next letter as index
    
    data.add_value('Current [pA]')      # Underline makes the next letter as index
    
    # The next command will actually create the dirs and files, based
    # on the information provided above. Additionally a settingsfile
    # is created containing the current settings of all the instruments.
    data.create_file()
    
    # Getting filepath to the data file
    data_path = data.get_dir() 
    
    # Next two plot-objects are created. First argument is the data object
    # that needs to be plotted. To prevent new windows from popping up each
    # measurement a 'name' can be provided so that window can be reused.
    # If the 'name' doesn't already exists, a new window with that name
    # will be created. For 3d plots, a plotting style is set.
    plot2d = qt.Plot2D(data, name='lockin7', autoupdate=False, valdim =1)
    plot2d.set_style('lines')
    
    plot2d_dmm = qt.Plot2D(data, name='dmm7', autoupdate=False, valdim =2)
    plot2d_dmm.set_style('lines')
    
    
    # Set the VSG power units
    VSG.set_power_units("dbm") 
    # Set the RF power
    VSG.set_power(power)
    # Turn the RF on
    VSG.set_status("on") 
    
    
    # preparation is done, now start the measurement.
    
    # It is actually a simple loop.
    start = time()
    for freq in freq_vec:
    
        VSG.set_frequency(freq)
        # the next function is necessary to keep the gui responsive. It
        # checks for instance if the 'stop' button is pushed. It also checks
        # if the plots need updating.
        qt.msleep(0.010)
        # readout form UHFLI
        # argument Num_of_TC represents number of time constants to wait before raeding the value
        # it is important because of the settling time of the low pass filter
        result_lockin = UHFLI_lib.UHF_measure_scope_single_shot(maxtime = 1.0)
        result_lockin = result_lockin[0] 
        result_lockin = np.mean(result_lockin)/gain*1e12
        # readout_dmm
        result_dmm = dmm.get_readval()/gain*1e12
    
        # save the data point to the file
        data.add_data_point(freq, result_lockin, result_dmm)  
    
        plot2d.update()
        plot2d_dmm.update()
    
        
    stop = time()
    print 'Duration: %s sec' % (stop - start, )
    
    # Saving UHFLI setting to the measurement data folder
    # You can load this settings file from UHFLI user interface 
    UHFLI_lib.UHF_save_settings(path = data_path)
    
    
    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
