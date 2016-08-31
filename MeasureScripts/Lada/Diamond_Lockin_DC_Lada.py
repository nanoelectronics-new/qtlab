from numpy import pi, random, arange, size
from time import time,sleep
#import UHFLI_lib
import datetime
import convert_for_diamond_plot as cnv



#####################################################
# here is where the actual measurement program starts
#####################################################
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'BIP', 'BIP'], numdacs=16) # Initialize IVVI
UHFLI_lib.UHF_init_demod(demod_c = 7)  # Initialize UHF LI
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x0957::0x0607::MY53003401::INSTR')


gain = 100e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

# you define two vectors of what you want to sweep


v1_vec = arange(2500,2200,-2)     #V_g
v2_vec = arange(-200,200,0.2)  #V_sd 



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

#fname_ac = '5-24 lockin'
#fname_dc = '5-24 dc'

data_ac = qt.Data(name='5-24 lockin By 1T') #just renamed

data_dc = qt.Data(name='5-24 dc By 1T') #added to have current recored as well

data_path_ac = data_ac.get_dir()
data_path_dc = data_dc.get_dir()

# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.
data_ac.add_coordinate('V_{SD} [mV]')
data_ac.add_coordinate('V_G[mV]')
data_ac.add_value('AC_Conductance ')

data_dc.add_coordinate('V_{SD} [mV]')
data_dc.add_coordinate('V_G [mV]')
data_dc.add_value('Current [pA]')

# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.
data_ac.create_file()
data_dc.create_file()

# Next two plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.
plot2d_ac = qt.Plot2D(data_ac, name='measure2D',autoupdate=False)
plot3d_ac = qt.Plot3D(data_ac, name='measure3D', coorddims=(1,0), valdim=2, style='image')

#plot2d_dc = qt.Plot2D(data_dc, name='measure2D',autoupdate=False)
#plot3d_dc = qt.Plot3D(data_dc, name='measure3D', coorddims=(1,0), valdim=2, style='image')



# preparation is done, now start the measurement.
# It is actually a simple loop.

init_start = time()
vec_count = 0
for v1 in v1_vec:
    
    start = time()
    # set the voltage 
    IVVI.set_dac5(v1)

    for v2 in v2_vec:
        
        # set the voltage
        IVVI.set_dac1(v2)

        # readout
        result_ac = UHFLI_lib.UHF_measure_demod(Num_of_TC = 1)/gain  # Reading the lockin and correcting for M1b gain
        result_dc = dmm.get_readval()/gain*1e12

        #print result_ac, result_dc

    
        # save the data point to the file, this will automatically trigger
        # the plot windows to update
        data_ac.add_data_point(v2,v1, result_ac)  
        data_dc.add_data_point(v2,v1, result_dc)


        # the next function is necessary to keep the gui responsive. It
        # checks for instance if the 'stop' button is pushed. It also checks
        # if the plots need updating.
        qt.msleep(0.001)
    data_ac.new_block()
    data_dc.new_block()
    stop = time()
    

    plot2d_ac.update()
    plot3d_ac.update() #added

    #plot2d_dc.update()
    #plot3d_dc.update() #added

    vec_count = vec_count + 1
    print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(v1_vec.size - vec_count))))
    
    

print 'Overall duration: %s sec' % (stop - init_start, )

   
#cnv.convert_to_matrix_file(fname = fname_ac, path = data_path_ac)
#cnv.convert_to_matrix_file(fname = fname_dc, path = data_path_dc)

# after the measurement ends, you need to close the data file.
data_ac.close_file()
data_dc.close_file()
# lastly tell the secondary processes (if any) that they are allowed to start again.
qt.mend()
