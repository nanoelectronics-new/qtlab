from numpy import pi, random, arange, size
from time import time,sleep
import AWG_lib




#####################################################
# EXAMPLE SCRIPT SHOWING HOW TO DO MEASUREMENT WITH UHF LOCKIN AMPLIFIER SCOPE
#####################################################
T1_lib.UHF_init()  # Initialize UHF LI

# Sweeping vector
v_vec = arange(0,600,200)



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

data = qt.Data(name=' testmeasurement')  # Put one space before name

# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.
data.add_coordinate('Samples')

data.add_value('Readout')

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
plot2d = qt.Plot2D(data, name='measure2D')
plot2d.set_style('lines')


# preparation is done, now start the measurement.
# It is actually a simple loop.
start = time()
for v in v_vec:
   

    # readout
    shotCH1,shotCH2 = T1_lib.UHF_measure(maxtime = 1)  # Reading out UHF LI scope shot. Channel one data in shotCH1, channel two data in shotCH2
                                                       # maxtime is maximum measurement time in seconds


    # save the data point to the file, this will automatically trigger
    # the plot windows to update
    data.add_data_point(v, sum(shotCH1)/len(shotCH1))
    plot2d.update()
    # the next function is necessary to keep the gui responsive. It
    # checks for instance if the 'stop' button is pushed. It also checks
    # if the plots need updating.
    qt.msleep(0.001)
stop = time()
print 'Duration: %s sec' % (stop - start, )
print 'Overal duration prediction: %s sec' % (stop - start, )*len(v)


# Saving UHFLI setting to the measurement data folder
# You can load this settings file from UHFLI user interface 
UHFLI_lib.UHF_save_settings(path = data_path)  


# after the measurement ends, you need to close the data file.
data.close_file()
# lastly tell the secondary processes (if any) that they are allowed to start again.
qt.mend()
