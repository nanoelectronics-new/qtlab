from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv



#####################################################
# EXAMPLE SCRIPT SHOWING HOW TO SET UP STANDARD DIAMOND MEASUREMENT WITH DMM
#####################################################
IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4')
dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x0957::0x0607::MY53003401::INSTR')
dmm.set_NPLC = 0.1  # Setting PLCs of dmm
file_name = ' testmeasurement'

gain = 10e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

# you define two vectors of what you want to sweep. In this case
# a gate voltage (v1_vec) and a bias voltage (v2_vec)

v1_vec = arange(0,10,2) ##''' !! Take care about step sign '''
v2_vec = arange(-50,50,20)  ##''' !! Take care about step sign '''



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

data = qt.Data(name=file_name)  # Put one space before name

# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.

data.add_coordinate('V_S_D [mV]')  # Underline makes the next letter as index
data.add_coordinate('V_G [mV]')    # Underline makes the next letter as index
data.add_value('Current [pA]')     # Underline makes the next letter as index

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
plot2d = qt.Plot2D(data, name='measure2D',autoupdate=False)
plot3d = qt.Plot3D(data, name='measure3D', coorddims=(1,0), valdim=2, style='image')



# preparation is done, now start the measurement.
# It is actually a simple loop.

init_start = time()
vec_count = 0
for v1 in v1_vec:
    
    start = time()
    # set the voltage
    IVVI.set_dac3(v1)

    for v2 in v2_vec:

        IVVI.set_dac1(v2)

        # readout
        result = dmm.get_readval()/gain*1e12
    
        # save the data point to the file, this will automatically trigger
        # the plot windows to update
        data.add_data_point(v2,v1, result)
        # the next function is necessary to keep the gui responsive. It
        # checks for instance if the 'stop' button is pushed. It also checks
        # if the plots need updating.
        qt.msleep(0.001)
    data.new_block()
    stop = time()
    

    plot2d.update()  # Updating 2d plot every iteration trough inner loop
    plot3d.update()  # Updating 3d plot every iteration trough inner loop


    vec_count = vec_count + 1
    print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(v1_vec.size - vec_count))))
    
    

print 'Overall duration: %s sec' % (stop - init_start, )

# Converting the output file into matrix format which can be read with Diamond plot tool. It is in the same folder as originla file.   
cnv.convert_to_matrix_file(fname = file_name, path = data_path)

# after the measurement ends, you need to close the data file.
data.close_file()
# lastly tell the secondary processes (if any) that they are allowed to start again.
qt.mend()
