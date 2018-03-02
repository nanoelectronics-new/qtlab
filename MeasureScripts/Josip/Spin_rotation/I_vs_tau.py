from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import numpy as np




file_name = '1_3 IV 224'

gain = 1000e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
tau_vector_repetitions = 800
power = 0.0











qt.mstart()


data = qt.Data(name=file_name)


data.add_coordinate('tau [ns]')
data.add_value('Current [pA]')


data.create_file()

 

plot2d = qt.Plot2D(data, name='measure2D',autoupdate=False)




#Turn the RF on
VSG.set_status("on") 
##Run the AWG sequence 
AWG.run()
#Turn ON all necessary AWG channels
AWG.set_ch1_output(1)
AWG.set_ch2_output(1)
AWG.set_ch3_output(1)
#Force the AWG to start from the first element of the sequence
AWG._ins.force_jump(1)



# preparation is done, now start the measurement.
# It is actually a simple loop.
VSG.set_power(power)

  
tau_vector = np.zeros(len(t_burst)) # Empty vector for averaging intermediate tau result vectors

start = time()
try: 
    for k in xrange(tau_vector_repetitions):  #repeat the one tau vector measurement n times
        AWG._ins.force_jump(1)     # Start from the first tau in the sequence
        for j,v2 in enumerate(t_burst):  
        
            
        
            # readout
           
           
            tau_vector[j] += dmm.get_readval()/gain*1e12
            
            
            AWG._ins.force_event()
        
            # the next function is necessary to keep the gui responsive. It
            # checks for instance if the 'stop' button is pushed. It also checks
            # if the plots need updating.
            qt.msleep(0.002)
    
    # Calculate the average value of the recorded tau vector
    tau_vector = tau_vector/tau_vector_repetitions
    # save the data point to the file    

    data.add_data_point(t_burst*1e3,tau_vector)  
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


    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
