from numpy import pi, random, arange, size
from time import time,sleep
import UHFLI_lib



#####################################################
# EXAMPLE SCRIPT SHOWING HOW TO SET UP STANDARD 1D (IV) LOCKIN MEASUREMENT
#####################################################
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM3', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54502777::INSTR')
daq = UHFLI_lib.UHF_init_demod_multiple(demod_c = [6])  # Initialize UHF LI

gain = 1e9 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

bias = 100

leak_test = False

gain_Lockin = 1 # Conversion factor for the Lockin

# Sweeping vector
v_vec = arange(0,700,1)  ##''' !! Take care about step sign '''


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

data_refl_mag = qt.Data(name='IVG_13-03_G06&12_refl_mag')  # Put one space before name
data_refl_ph = qt.Data(name='IVG_13-03_G06&12_refl_ph')  # Put one space before name
data_current = qt.Data(name='IVG_13-03_G06&12_current')  # Put one space before name


# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.

data_refl_mag.add_coordinate(' Voltage [mV]')   # Underline makes the next letter as index

data_refl_mag.add_value(' Voltage [V]')      # Underline makes the next letter as index

data_refl_ph.add_coordinate(' Voltage [mV]')   # Underline makes the next letter as index

data_refl_ph.add_value(' Angle [deg]')      # Underline makes the next letter as index

data_current.add_coordinate(' Voltage [mV]')   # Underline makes the next letter as index

data_current.add_value(' Current [pA]')      # Underline makes the next letter as index

# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.
data_refl_mag.create_file()
data_refl_ph.create_file()
data_current.create_file()

# Getting filepath to the data file
data_path = data_refl_mag.get_dir() 

# Next two plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.
next = 0 
next = next + 1 
plot2d_refl_mag = qt.Plot2D(data_refl_mag, name='refl_mag_%d'%next, autoupdate=False)
plot2d_refl_mag.set_style('lines')

plot2d_refl_ph = qt.Plot2D(data_refl_ph, name='refl_ph_%d'%next, autoupdate=False)
plot2d_refl_ph.set_style('lines')

plot2d_current = qt.Plot2D(data_current, name='current_%d'%next, autoupdate=False)
plot2d_current.set_style('lines')



# preparation is done, now start the measurement.
IVVI.set_dac1(bias)
# It is actually a simple loop.
start = time()
for v in v_vec:
    # set the voltage
    IVVI.set_dac5(v)
    IVVI.set_dac6(v)

    # readout form UHFLI
    # argument Num_of_TC represents number of time constants to wait before raeding the value
    # it is important because of the settling time of the low pass filter
    result_current = dmm.get_readval()/gain*1e12
    result_refl = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 3)  # Reading the lockin
    result_refl = array(result_refl)
    result_ph = sum(result_refl[:,1])  # Getting phase values from all three demodulators and summing them
    result_mag = sum(result_refl[:,0]) # Getting amolitude values from all three demodulators and summing them
 
    # save the data point to the file
    data_refl_mag.add_data_point(v, result_mag) 
    data_refl_ph.add_data_point(v, result_ph)
    data_current.add_data_point(v, result_current) 

    if leak_test:
        plot2d_current.update()
        plot2d_refl_mag.update()   # If leak_test is True update every point 
        plot2d_refl_ph.update()   # If leak_test is True update every point 
    elif not bool(mod(v,50)):  
        plot2d_current.update()  
        plot2d_refl_mag.update()   # Update every 10 points
        plot2d_refl_ph.update()   # If leak_test is True update every point
    # the next function is necessary to keep the gui responsive. It
    # checks for instance if the 'stop' button is pushed. It also checks
    # if the plots need updating.
    qt.msleep(0.001)
stop = time()
print 'Duration: %s sec' % (stop - start, )

# Saving UHFLI setting to the measurement data folder
# You can load this settings file from UHFLI user interface 
UHFLI_lib.UHF_save_settings(path = data_path)


# after the measurement ends, you need to close the data file.
data_refl_mag.close_file()
data_refl_ph.close_file()
data_current.close_file()
# lastly tell the secondary processes (if any) that they are allowed to start again.
qt.mend()
