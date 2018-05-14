from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import numpy as np




file_name = '1_3 IV 544'

gain = 1000e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
tau_vector_repetitions = 5
power = 4.0
f_center = 5.893e9          # Center frequency in Hz
f_offset = 50e6             # Frequencey offset in MHz

taus = arange(0.006,0.120,0.001)


qt.mstart()


data = qt.Data(name=file_name)


data.add_coordinate('tau wait [ns]')
data.add_value('Current [pA]')


data.create_file()

 

plot2d = qt.Plot2D(data, name='measure2D',autoupdate=False)



# Set the VSG power units
VSG.set_power_units("dbm") 
# Set the RF power
VSG.set_power(power)
# Set the RF frequency
VSG.set_frequency((f_center - f_offset))
#Turn the RF on
VSG.set_status("on") 
##Run the AWG sequence 
AWG.run()
#Turn ON all necessary AWG channels
AWG.set_ch1_output(1)
AWG.set_ch2_output(1)
AWG.set_ch3_output(1)
#AWG.set_ch4_output(1)
#Force the AWG to start from the first element of the sequence
AWG._ins.force_jump(1)



# preparation is done, now start the measurement.
# It is actually a simple loop.


  
tau_vector = np.zeros(len(taus)) # Empty vector for averaging intermediate tau result vectors

start = time()
try: 
    for k in xrange(tau_vector_repetitions):  #repeat the one tau vector measurement n times
        AWG._ins.force_jump(1)     # Start from the first tau in the sequence
        for j,v2 in enumerate(taus):  
        
            
        
            # readout
           
           
            tau_vector[j] += dmm.get_readval()/gain*1e12
            
            
            AWG._ins.force_event()
        
            # the next function is necessary to keep the gui responsive. It
            # checks for instance if the 'stop' button is pushed. It also checks
            # if the plots need updating.
            qt.msleep(0.010)
    
    # Calculate the average value of the recorded tau vector
    tau_vector = tau_vector/tau_vector_repetitions
    # save the data point to the file    

    data.add_data_point(taus*1e3,tau_vector)  
    data.new_block()
    stop = time()
    
    plot2d.update()
    
    stop = time()
    print 'Duration: %s sec' % (stop - start, )


finally:

    # Switching off the RF 
    VSG.set_status("off") 

    #Stop the AWG sequence 
    AWG.stop()
    #Turn OFF all necessary AWG channels
    AWG.set_ch1_output(0)
    AWG.set_ch2_output(0)
    AWG.set_ch3_output(0)
    #AWG.set_ch4_output(0)

    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
