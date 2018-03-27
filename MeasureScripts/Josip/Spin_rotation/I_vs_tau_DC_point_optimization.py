from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import numpy as np


## Script for running I vs tau measurement versus DAC voltages
## Used for the optimization of the visibility of the oscillations in respect to the DC point position

file_name = '1_3 IV 353'


gain = 1000e6               # Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
tau_vector_repetitions = 5  # Number of whole traces averages
f_center = 5.96555e9        # Center frequency in Hz
power = 5.0                 # RF power in dBm

raw_input("Warning: - check if the sequence and the measurement script have the same number of steps!\nPress enter to continue...")
taus = arange(0.006,0.141,0.001)    # Should be same like in the used AWG upload script

DAC5_center = -357.89       #  DAC5 center voltage in mV
DAC6_center = -261.20       #  DAC6 center voltage in mV
DAC5_offsets = np.linspace(-0.15,0.15,5) # DAC5 offsets from the center (to be swept through) voltage 
DAC6_offsets = np.linspace(-0.15,0.15,5) # DAC6 offsets from the center (to be swept through) voltage 


#saving directly in matrix format for diamond program
new_mat = np.zeros(len(taus)) # Creating empty matrix for storing all data  


qt.mstart()


data = qt.Data(name=file_name)


data.add_coordinate('tau [ns]')
data.add_coordinate('DAC6_offset_voltage [mV]')
data.add_coordinate('DAC5_offset_voltage [mV]')
data.add_value('Current [pA]')



data.create_file()

 

plot2d = qt.Plot2D(data, name='measure2D',autoupdate=False)
plot3d = qt.Plot3D(data, name='measure3D', coorddims=(1,0), valdim=3, style='image') 



# Turn the RF on
VSG.set_status("on")
# Set the VSG power units
VSG.set_power_units("dbm") 
# Set the RF power
VSG.set_power(power)
# Set the RF frequency
VSG.set_frequency(f_center)
##Run the AWG sequence 
AWG.run()
#Turn ON all necessary AWG channels
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
    for DAC5_off in DAC5_offsets:
        IVVI.set_dac5(DAC5_center + DAC5_off)               # Set the DAC5 voltage

        for DAC6_off in DAC6_offsets: 
            IVVI.set_dac6(DAC6_center + DAC6_off)           # Set the DAC6 voltage

            tau_vector = np.zeros(len(taus))                # Empty vector for averaging intermediate tau result vectors

            for k in xrange(tau_vector_repetitions):    # Repeat the one tau vector measurement n times
                AWG._ins.force_jump(1)                  # Start from the first tau in the sequence
                for j,v2 in enumerate(taus):            # Going thorugh taus
                    
                    # the next function is necessary to keep the gui responsive. It
                    # checks for instance if the 'stop' button is pushed. It also checks
                    # if the plots need updating.
                    qt.msleep(0.010)
                    # Readout
                    tau_vector[j] += dmm.get_readval()/gain*1e12
                    
                    
                    AWG._ins.force_event()
                          
            # Calculate the average value of the recorded tau vector
            tau_vector = tau_vector/tau_vector_repetitions
            # save the data point to the file    
            data.add_data_point(taus*1e3,DAC6_off+DAC6_center,DAC5_off+DAC5_center,tau_vector)  
            data.new_block()
            stop = time()
            new_mat = np.column_stack((new_mat,tau_vector))   # Gluing new tau_vector to the present matrix
            if i == 0:                                        # Kicking out the first column, filled with zeros, from the matrix 
                new_mat = new_mat[:,1:]
    
            np.savetxt(fname = data.get_filepath()+ "_matrix", X = new_mat, fmt = '%1.4e', delimiter = '  ', newline = '\n')
            
            plot2d.update()
            plot3d.update()
            
            stop = time()              # Some things for being able to calculate the remaining time of the measurement
            vec_count = vec_count + 1
            # Calculating and showing the remaining measurement time
            print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(DAC5_offsets.size*DAC6_offsets.size - vec_count))))
    # Calculating and showing the overall measurement time
    print 'Overall duration: %s sec' % (stop - init_start, )

finally:

    # Switching off the RF 
    VSG.set_status("off") 

    #Stop the AWG sequence 
    AWG.stop()
    #Turn OFF AWG channels
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
