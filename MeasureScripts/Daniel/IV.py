from numpy import pi, random, arange, size
from time import time,sleep



#####################################################
# EXAMPLE SCRIPT SHOWING HOW TO SET UP STANDARD 1D (IV) DMM MEASUREMENT
#####################################################
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)  # Initialize IVVI
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54505177::INSTR')  # Initialize dmm
#dmm.set_NPLC = 0.1  # Setting PLCs of dmm

gain = 1e6 # hoose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

bias = 100

# Sweeping vector
v_vec = arange(1000,0,-5)  #''' !! Take care about step sign '''
#v_vec = arange(0,1000,5)

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

data = qt.Data(name=' QW4_Ohmic3_4GND_otheropen_1')  # Put one space before name
#data = qt.Data(name=' test_08-23') 



# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.

data.add_coordinate(' Voltage [mV]')     # Underline makes the next letter as index
#data.add_coordinate(' Current [microA]')

data.add_value(' Current [pA]')          # Underline makes the next letter as index
#data.add_value(' Voltage [mV]')
# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.
data.create_file()

# Next two plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.
plot2d = qt.Plot2D(data, name='meas_12', autoupdate=False)
plot2d.set_style('lines')


# preparation is done, now start the measurement.
#IVVI.set_dac1(bias)
# It is actually a simple loop.
start = time()
try:
    for v in v_vec:
        # set the voltage
        IVVI.set_dac1(v)
        #IVVI.set_dac5(v)
        #IVVI.set_dac6(v)
        #IVVI.set_dac7(v)

        # readout
        result = dmm.get_readval()/(gain)*1e12

        #if abs(result) > 50:
            #raise Exception("Leak treshold reached") 

        # save the data point to the file, this will automatically trigger
        # the plot windows to update
        #a = v*1e-5*1e-3*1e6 #when sweeping the current you want microamp
        #data.add_data_point(v, result)
        data.add_data_point(v, result)
        plot2d.update()
        # the next function is necessary to keep the gui responsive. It
        # checks for instance if the 'stop' button is pushed. It also checks
        # if the plots need updating.
        qt.msleep(0.001)

finally:
    stop = time()
    print 'Duration: %s sec' % (stop - start, )


       


    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()