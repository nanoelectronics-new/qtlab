from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import UHFLI_lib



#####################################################
#This script runs reflectometry and dc diamond measurement in parallel
#Added: leak test T/F and saving both refl and dc
#####################################################

#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x0957::0x0607::MY53003401::INSTR')   # Initialize dmm
UHFLI_lib.UHF_init_demod(demod_c = 3)  # Initialize UHF LI


#file_name = '5-24 gate vs gate, sensor jumping, bias=300uV reflectometry only, -40dB'

gain = 1e8 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

#bias = 300


#gain_Lockin = 1 # Conversion factor for the Lockin

leak_test = False

v_vec = arange(-50,50,0.5)

div_factor = 100

bias = 100


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

data_refl1 = qt.Data(name=' IV_13-10_G08_lockin_exc=2,5uV') #value give in Vrms

data_dc = qt.Data(name=' IV_13-10_G08') #added to have current recored as well

data_path_refl1 = data_refl1.get_dir()
data_path_dc = data_dc.get_dir()

# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.

data_dc.add_coordinate('V_G [mV]')

data_dc.add_value('Current [pA]')


data_refl1.add_coordinate('V_G [mV]')

data_refl1.add_value('Locin out [pA]')


# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.

data_dc.create_file()
data_refl1.create_file()


# Next two plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.

plot2d_refl1 = qt.Plot2D(data_refl1, name='lockin',autoupdate=False)

plot2d_dc = qt.Plot2D(data_dc, name='dc',autoupdate=False)




# preparation is done, now start the measurement.
# It is actually a simple loop.

#IVVI.set_dac1(bias)
    
    
start = time()
for v in v_vec:

    IVVI.set_dac1(v)

    # readout
    result_reflectometry = UHFLI_lib.UHF_measure_demod(Num_of_TC = 3)/gain*1e12  # Reading the lockin and correcting for M1b gain

    result_dc = dmm.get_readval()/gain*1e12

    data_refl1.add_data_point(v/div_factor, result_reflectometry) 
    data_dc.add_data_point(v/div_factor, result_dc) 

    if leak_test:
        plot2d_refl1.update()
        plot2d_dc.update()   # If leak_test is True update every point 
    elif not bool(mod(v,10)):    
        plot2d_refl1.update()
        plot2d_dc.update()   # Update every 10 points
    
       

    # the next function is necessary to keep the gui responsive. It
    # checks for instance if the 'stop' button is pushed. It also checks
    # if the plots need updating.
    qt.msleep(0.001)



stop = time()
    

    

print 'Overall duration: %s sec' % (stop - init_start, )

   
# Saving UHFLI setting to the measurement data folder
# You can load this settings file from UHFLI user interface 
UHFLI_lib.UHF_save_settings(path = data_path_refl1)


# after the measurement ends, you need to close the data file.
data_refl1.close_file()
data_dc.close_file()
#data_current.close_file()
# lastly tell the secondary processes (if any) that they are allowed to start again.
qt.mend()