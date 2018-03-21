from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import numpy as np




file_name = '1_3 IV 341'

gain = 1000e6                   # Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
start_power = -5.0                # Starting power value in dBm
stop_power = 10.0                 # FInishing power value in dBm
num_of_steps = 80               # Number of steps 
averaging_repetitions = 25      # Defines the number of averaged traces
f_center = 5.96555e9            # Center frequency in Hz


def dBm_to_volts_50ohm(P_dBm):
    '''
    Function for converting the power in dBm to a corresponding voltage on the 50 ohm resistor
    '''
    P_mW = 10**(P_dBm/10.0)
    P_volts = np.sqrt(0.05*P_mW)
    return P_volts


volt_array = np.linspace(dBm_to_volts_50ohm(start_power),dBm_to_volts_50ohm(stop_power),num_of_steps)   # Voltage vector inferred 
                                                                                                        # from the given power values
VSG.set_power_units("V")  # Setting the power units of the SMW200A to volts

qt.mstart()
data = qt.Data(name=file_name)


data.add_coordinate('RF amplitude [V]')
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
AWG.set_ch4_output(1)
#Force the AWG to start from the first element of the sequence
AWG._ins.force_jump(1)
# Set the VSG to the necessary frequency
VSG.set_frequency(f_center)   



# preparation is done, now start the measurement.
# It is actually a simple loop.


  
averaging_vector = np.zeros(len(volt_array))         # Empty vector for averaging intermediate result 

start = time()
try: 
    for k in xrange(averaging_repetitions):     # Repeat the one trace n times for averaging
        
        for j,v2 in enumerate(volt_array):  
        
            
        
            
           
            VSG.set_power(v2)   # Set the power point (x axis point it this measurement)

            qt.msleep(0.010)    # Waiting for the power of the VSG to settle
                                # Also it is necessary to keep the gui responsive. It
                                # checks for instance if the 'stop' button is pushed. It also checks
                                # if the plots need updating.

            # readout
            averaging_vector[j] += dmm.get_readval()/gain*1e12
            
            

        

            
    
    # Calculate the average value of the recorded tau vector
    averaging_vector = averaging_vector/averaging_repetitions
    # save the data point to the file    

    data.add_data_point(volt_array,averaging_vector)  
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
    AWG.set_ch4_output(0)


    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
