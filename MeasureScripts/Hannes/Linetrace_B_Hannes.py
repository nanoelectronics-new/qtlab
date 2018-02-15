from numpy import pi, random, arange, size, mod
from time import time,sleep

#####################################################
# this part is to simulate some data, you can skip it
#####################################################




#####################################################
# here is where the actual measurement program starts
#####################################################

#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54506631::INSTR')


gain = 1000e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

#magnet
ramp_rate_Z = 0.001 #T/s
ramp_rate_Y = 0.0008 #T/s


step_size_BZ = -1e-3 
step_size_BY = -1e-3 
BZ_vector = arange(350e-3,0e-3+step_size_BZ,step_size_BZ) #T  # Those two vectors need to be the same left
BY_vector = arange(350e-3,0e-3+step_size_BY,step_size_BY) #T  #

if len(BZ_vector) != len(BY_vector):
    raise Exception ("B vectors have different length")

ramp_time = max(abs((float(step_size_BY)/ramp_rate_Y)),abs(float(step_size_BZ)/ramp_rate_Z))
ramp_time = 1.2*ramp_time

magnetZ.set_rampRate_T_s(ramp_rate_Z)
magnetY.set_rampRate_T_s(ramp_rate_Y)


leak_test = True

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
data = qt.Data(name='1_3 IV 251')


# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.
data.add_coordinate('B[T]')

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
plot2d = qt.Plot2D(data, name='noname', autoupdate=False)
plot2d.set_style('lines')


# preparation is done, now start the measurement.


# It is actually a simple loop.
start = time()

for i,v1 in enumerate(BY_vector):  # CHANGE THIS LINE FOR MATRIX FILE SAVING
        
        
        start = time()
        # set the voltage
        #IVVI.set_dac5(v1)

        magnetZ.set_field(BZ_vector[i])
        magnetY.set_field(BY_vector[i])  

        total_field = np.sqrt(BZ_vector[i]**2 + BY_vector[i]**2)
        #total_field = np.sqrt(BY_vector[i]**2)

        # changed BY to BZ
        while math.fabs(BY_vector[i] - magnetY.get_field_get()) > 0.0001:
            qt.msleep(0.050)

        # readout
        result = dmm._ins.get_readval()/(gain)*1e12 # Remove Lockin gain if you are not measuring with it

        # save the data point to the file, this will automatically trigger
        # the plot windows to update
        data.add_data_point(total_field, result)

        if leak_test:
            plot2d.update()   # If leak_test is True update every point 
        elif not bool(mod(total_field,10)):    
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
