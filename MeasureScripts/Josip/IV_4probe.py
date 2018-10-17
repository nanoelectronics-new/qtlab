from numpy import pi, random, arange, size
from time import time,sleep
import qt

#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'NEG', 'BIP', 'BIP'], numdacs=16)  # Initialize IVVI
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54505188::INSTR') # Initialize dmm

#####################################################
# EXAMPLE SCRIPT SHOWING HOW TO SET UP STANDARD 1D (IV) DMM MEASUREMENT
#####################################################


def IV_4probe(name = "Random", gain = 1e3, mV_to_uA = 1e3, IVVI = IVVI, dmm = dmm):
    #IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'NEG', 'BIP', 'BIP'], numdacs=16)  # Initialize IVVI
    #dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54505188::INSTR') # Initialize dmm
    gain = gain # Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    mV_to_uA = mV_to_uA 
    #bias = 500
    
    # Sweeping vector
    v_vec = arange(-1000,1000,10)  #''' !! Take care about step sign '''
    
    
    
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
    
    data = qt.Data(name=name)  # Put one space before name
    
    
    # Now you provide the information of what data will be saved in the
    # datafile. A distinction is made between 'coordinates', and 'values'.
    # Coordinates are the parameters that you sweep, values are the
    # parameters that you readout (the result of an experiment). This
    # information is used later for plotting purposes.
    # Adding coordinate and value info is optional, but recommended.
    # If you don't supply it, the data class will guess your data format.
    
    data.add_coordinate(' Current [uA]')     # Underline makes the next letter as index
    
    data.add_value(' Voltage [V]')          # Underline makes the next letter as index
    
    # The next command will actually create the dirs and files, based
    # on the information provided above. Additionally a settingsfile
    # is created containing the current settings of all the instruments.
    data.create_file()
    
    # Next two plot-objects are created. First argument is the data object
    # that needs to be plotted. To prevent new windows from popping up each
    # measurement a 'name' can be provided so that window can be reused.
    # If the 'name' doesn't already exists, a new window with that name
    # will be created. For 3d plots, a plotting style is set.
    plot2d = qt.Plot2D(data, name='measure2D', autoupdate=False)
    plot2d.set_style('lines')
    
    
    # preparation is done, now start the measurement.
    #IVVI.set_dac1(bias)
    # It is actually a simple loop.
    start = time()
    for v in v_vec:
        # set the voltage
        IVVI.set_dac3(v)
    
        # readout
        result = dmm.get_readval()/gain
    
        # save the data point to the file, this will automatically trigger
        # the plot windows to update
        data.add_data_point(v/mV_to_uA, result)
        plot2d.update()
        # the next function is necessary to keep the gui responsive. It
        # checks for instance if the 'stop' button is pushed. It also checks
        # if the plots need updating.
        qt.msleep(0.05)
    stop = time()
    print 'Duration: %s sec' % (stop - start, )
    
    
       
    
    
    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()