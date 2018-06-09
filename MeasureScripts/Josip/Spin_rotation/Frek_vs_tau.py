from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import numpy as np
from Background_correction import Back_corr as bc

#####################################################
# this part is to simulate some data, you can skip it
#####################################################




#####################################################
# here is where the actual measurement program starts
#####################################################
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM3', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x0957::0x0607::MY53003401::INSTR')
#dmm.set_NPLC = 1  # Setting PLCs of dmm

file_name = '1_3 IV 621'

gain = 1000e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

raw_input("Warning: - check if the sequence and the measurement script have the same number of steps!\nPress enter to continue...")

t_burst = arange(0.006,0.160,0.002)


B_total = 147e-3 # in T
theta = 30.0 # in degrees
By = B_total*np.cos(np.deg2rad(theta))
Bz = B_total*np.sin(np.deg2rad(theta))





v1_vec = arange(-5e7,5e7,2e6)  #Frequency offset in Hz
f_center = 5.900e9  # Center frequency in Hz
tau_vector_repetitions = 25
power = 0.0


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
data = qt.Data(name=file_name)

# Now you provide the information of what data will be saved in the
# datafile. A distinction is made between 'coordinates', and 'values'.
# Coordinates are the parameters that you sweep, values are the
# parameters that you readout (the result of an experiment). This
# information is used later for plotting purposes.
# Adding coordinate and value info is optional, but recommended.
# If you don't supply it, the data class will guess your data format.
data.add_coordinate('tau burst [ns]')
data.add_coordinate('%.3f GHz + Frequency offset [Hz]'%(f_center*1e-9))
data.add_value('Current [pA]')

# The next command will actually create the dirs and files, based
# on the information provided above. Additionally a settingsfile
# is created containing the current settings of all the instruments.
data.create_file()



#saving directly in matrix format for diamond program
new_mat = np.zeros(len(t_burst)) # Creating empty matrix for storing all data   

# Next two plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.
plot2d = qt.Plot2D(data, name='measure2D',autoupdate=False)
plot3d = qt.Plot3D(data, name='measure3D', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly


# Set the magnet
ramp_rate_Y = 0.0008 #T/s
ramp_rate_Z = 0.0008 #T/s
magnetY.set_rampRate_T_s(ramp_rate_Y)
magnetZ.set_rampRate_T_s(ramp_rate_Z)
magnetY.set_field(By)   # Set the By field first               
while math.fabs(By - magnetY.get_field_get()) > 0.0001:  # Wait until the By field is set
    qt.msleep(0.050)
magnetZ.set_field(Bz)   # Set the Bz field second
while math.fabs(Bz - magnetZ.get_field_get()) > 0.0001:  # Wait until the Bz field is set
    qt.msleep(0.050)


# Set the VSG power units
VSG.set_power_units("dbm") 
# Set the RF power
VSG.set_power(power)
# Turn the RF on
VSG.set_status("on") 
## Run the AWG sequence 
AWG.run()
# Turn ON all necessary AWG channels
AWG.set_ch1_output(1)
AWG.set_ch2_output(1)
AWG.set_ch3_output(1)
AWG.set_ch4_output(1)
#Force the AWG to start from the first element of the sequence
AWG._ins.force_jump(1)



# preparation is done, now start the measurement.
# It is actually a simple loop.

init_start = time()
vec_count = 0

try:
    for i,v1 in enumerate(v1_vec): 
        
        
        start = time()
        #VSG.set_power(v1)
        VSG.set_frequency(f_center + v1)
  
        tau_vector = np.zeros(len(t_burst)) # Empty vector for averaging intermediate tau result vectors

        for k in xrange(tau_vector_repetitions):  #repeat the one tau vector measurement n times
            AWG._ins.force_jump(1)     # Start from the first tau in the sequence
            for j,v2 in enumerate(t_burst):  
    
                # the next function is necessary to keep the gui responsive. It
                # checks for instance if the 'stop' button is pushed. It also checks
                # if the plots need updating.
                qt.msleep(0.010)
    
                # readout
               
               
                tau_vector[j] += dmm.get_readval()/gain*1e12
                
                
                AWG._ins.force_event()
    
               

        # Calculate the average value of the recorded tau vector
        tau_vector = tau_vector/tau_vector_repetitions

        # save the data point to the file    
        v111 = np.linspace(v1,v1,len(t_burst)) # Vector with repeating value of v1 for the length of the tau vector - for add_data_point command
        data.add_data_point(t_burst*1e3,v111,tau_vector)  
        data.new_block()
        stop = time()

        new_mat = np.column_stack((new_mat,tau_vector))   # Gluing new tau_vector to the present matrix
        if i == 0: #Kicking out the first column filled with zero
            new_mat = new_mat[:,1:]

        np.savetxt(fname = data.get_filepath()+ "_matrix", X = new_mat, fmt = '%1.4e', delimiter = '  ', newline = '\n')
        

        plot2d.update()

        plot3d.update()

        vec_count = vec_count + 1
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(v1_vec.size - vec_count))))
        
        

    print 'Overall duration: %s sec' % (stop - init_start, )

finally:

    # Switching off the RF 
    VSG.set_status("off") 

    #Stop the AWG sequence 
    AWG.stop()
    #Turn OFF all necessary AWG channels
    AWG.set_ch1_output(0)
    AWG.set_ch2_output(0)
    AWG.set_ch3_output(0)
    AWG.set_ch4_output(0)


    # Do the background correction
    bc(path = data.get_dir(), fname = data.get_filename()+"_matrix")

    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
