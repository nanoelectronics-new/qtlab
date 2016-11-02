from numpy import pi, random, arange, size, mod
from time import time,sleep

#####################################################
# this part is to simulate some data, you can skip it
#####################################################




#####################################################
# here is where the actual measurement program starts
#####################################################

#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x0957::0x0607::MY53003401::INSTR')

gain = 1e9 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G


<<<<<<< HEAD
#bias = 1000
=======
bias = 50


>>>>>>> 67e8801... Matrix file direct saving in Diamond_reflectometry_Lada

leak_test = False

# you define two vectors of what you want to sweep. In this case
# a magnetic field (b_vec) and a frequency (f_vec)
<<<<<<< HEAD
v_vec = arange(2460,0,-4)

=======
v_vec = arange(1000,4000,4)
#v_vec = arange(-300,300,0.06)
>>>>>>> 67e8801... Matrix file direct saving in Diamond_reflectometry_Lada


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
<<<<<<< HEAD
data = qt.Data(name='5-24 grounding')
=======
data = qt.Data(name='5-24 B=0,5T dot')
>>>>>>> 67e8801... Matrix file direct saving in Diamond_reflectometry_Lada


# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.
data.add_coordinate('Voltage [mV]')

data.add_value('Current [pA]')

# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.
data.create_file()

# Next two plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.
<<<<<<< HEAD
plot2d = qt.Plot2D(data, name='ivg', autoupdate=False)
=======
plot2d = qt.Plot2D(data, name='plot1', autoupdate=False)
>>>>>>> 67e8801... Matrix file direct saving in Diamond_reflectometry_Lada
plot2d.set_style('lines')


# preparation is done, now start the measurement.

<<<<<<< HEAD
#IVVI.set_dac1(bias)
=======
IVVI.set_dac1(bias)
>>>>>>> 67e8801... Matrix file direct saving in Diamond_reflectometry_Lada

# It is actually a simple loop.
start = time()
for v in v_vec:
    # set the voltage
<<<<<<< HEAD
=======

>>>>>>> 67e8801... Matrix file direct saving in Diamond_reflectometry_Lada
    IVVI.set_dac7(v)
    # readout
    result = dmm.get_readval()/(gain)*1e12 # Remove Lockin gain if you are not measuring with it

  


    # save the data point to the file, this will automatically trigger
    # the plot windows to update
    data.add_data_point(v, result)

    if leak_test:
        plot2d.update()   # If leak_test is True update every point 
    elif not bool(mod(v,20)):    
        plot2d.update()   # Update every 10 points

    

    # the next function is necessary to keep the gui responsive. It
    # checks for instance if the 'stop' button is pushed. It also checks
    # if the plots need updating.
    qt.msleep(0.001)
stop = time()
print 'Duration: %s sec' % (stop - start, )


   


# after the measurement ends, you need to close the data file.
data.close_file()
# lastly tell the secondary processes (if any) that they are allowed to start again.
qt.mend()
