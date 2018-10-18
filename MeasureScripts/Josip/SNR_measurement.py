from numpy import pi, random, arange, size
from time import time,sleep
import UHFLI_lib
reload(UHFLI_lib)
import numpy as np
import datetime


"""
Script for extracting the SNR according to the protocol from 
"Gate-based single-shot readout of spins in silicon", A.West,...,Dzurak, Figure 2c
"""


Nsamples = 1000 # Number of integrated samples to record

daq = UHFLI_lib.UHF_init_demod_multiple(device_id = 'dev2169', demod_c = [3])
daq.setInt('/dev2169/sigouts/0/enables/3', 1) # Turn on the UHFLI Out 1



raw_input("\nSet the bias point then press Enter to continue...\n")





I_buffer = np.zeros(Nsamples) # Buffer for I values
Q_buffer = np.zeros(Nsamples) # Buffer for Q values





qt.mstart()

# Creating folders and defining coordinates and values
data_I = qt.Data(name=' SNR_measurement_ON_I') 
data_Q = qt.Data(name=' SNR_measurement_ON_Q') 
data_I.add_coordinate(' Number of samples') 
data_Q.add_coordinate(' Number of samples') 
data_I.add_value(' I [V]')
data_Q.add_value(' Q [V]')    
data_I.create_file()
data_Q.create_file()














init_start = time()


daq.setInt('/dev2169/sigins/0/autorange', 1)  # Autoset UHFLI demod amplification

try:

    for i in xrange(Nsamples):
    
    
        result_refl = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 3, Integration_time = 0.01, Measure = "Quadratures")  # Reading the UHFLI
        result_refl = array(result_refl)
        result_I = result_refl[0,0]  # Getting I value integrated for the integration time
        result_Q = result_refl[0,1]  # Getting Q value integrated for the integration time

    
        # save the data point to the file
        data_I.add_data_point(i,result_I) 
        data_Q.add_data_point(i,result_Q) 
    
    
        qt.msleep(0.003)

    
    
    stop = time() # Get the time stamp 
    print 'Overall duration: %s sec' % (stop - init_start, )



finally:      
    
    # Getting filepath to the data file
    data_path = data_I.get_dir() 
    # Saving UHFLI setting to the measurement data folder
    # You can load this settings file from UHFLI user interface 
    UHFLI_lib.UHF_save_settings(daq, path = data_path)
    # after the measurement ends, you need to close the data file.
    data_I.close_file()
    data_Q.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()