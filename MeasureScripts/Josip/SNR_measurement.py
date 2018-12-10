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


ON_voltage = -90.0 # DAC3 voltage to be on the interdot transition
OFF_voltage = -20.0 # DAC3 voltage to be OFF the interdot transition


integration_times = np.array([0.010, 0.020, 0.050, 0.100])  # In seconds

qt.mstart()

# Creating folders and defining coordinates and values
data_SNR = qt.Data(name=' SNR')
data_SNR.add_coordinate(' Integration time [s]') 
data_SNR.add_value(' SNR')


plot2d = qt.Plot2D(data_SNR, name='SNR_vs_integration_time', autoupdate=False)
plot2d.set_style('lines')


for integ in integration_times:
    # Creating folders and defining coordinates and values
    data = qt.Data(name=' SNR_measurement_%d_ms'%(integ*1e3)) # Single SNR measurement, qith a given integration time
    data.add_coordinate(' Number of samples') 
    data.add_value(' I_ON [V]')
    data.add_value(' Q_ON [V]')  
    data.add_value(' I_OFF [V]')
    data.add_value(' Q_OFF [V]')  
    
    
    
      
    data.create_file()
    
    
    result_I_ON = np.zeros(Nsamples)
    result_I_OFF = np.zeros(Nsamples)
    result_Q_ON = np.zeros(Nsamples)
    result_Q_OFF = np.zeros(Nsamples)
    
    
    
    init_start = time()
    
    
    daq.setInt('/dev2169/sigins/0/autorange', 1)  # Autoset UHFLI demod amplification
    
    
        
    # Setting the DC point ON the interdot transition
    IVVI.set_dac3(ON_voltage)
    # Gathering the sampled I and Q data ON the interdot transition
    for i in xrange(Nsamples):
    
        result_refl = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 3, Integration_time = integ, Measure = "Quadratures")  # Reading the UHFLI
        result_refl = array(result_refl)
        result_I_ON[i] = result_refl[0,0]  # Getting I value integrated for the integration time
        result_Q_ON[i] = result_refl[0,1]  # Getting Q value integrated for the integration time

    
    
        qt.msleep(0.003)



    # Setting the DC point OFF the interdot transition
    IVVI.set_dac3(OFF_voltage)
    # Gathering the sampled I and Q data OFF the interdot transition
    for i in xrange(Nsamples):
    
        result_refl = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 3, Integration_time = integ, Measure = "Quadratures")  # Reading the UHFLI
        result_refl = array(result_refl)
        result_I_OFF[i] = result_refl[0,0]  # Getting I value integrated for the integration time
        result_Q_OFF[i] = result_refl[0,1]  # Getting Q value integrated for the integration time
     
    
    
        qt.msleep(0.003)

    
    # save the data to the file
    data.add_data_point(np.linspace(1,Nsamples,Nsamples),result_I_ON, result_Q_ON, result_I_OFF, result_Q_OFF) 
    data.close_file() 
    
    stop = time() # Get the time stamp FI_b
    print 'Overall duration: %s sec' % (stop - init_start, )

    # Calculating SNR
    S = np.square(np.mean(result_I_ON - result_I_OFF)) + np.square(np.mean(result_Q_ON - result_Q_OFF))
    N = np.std(np.square(result_I_ON - result_I_OFF) + np.square(result_Q_ON - result_Q_OFF))

    SNR = S/N
    print ("SNR is %.2f"%SNR)
    # Save SNR value to the file
    data_SNR.add_data_point(integ, SNR)

    plot2d.update()
    
        
    
       
# Getting filepath to the data file
data_path = data_SNR.get_dir() 
# Saving UHFLI setting to the measurement data folder
# You can load this settings file from UHFLI user interface 
UHFLI_lib.UHF_save_settings(daq, path = data_path)
# after the measurement ends, you need to close the data file.
data_SNR.close_file()   
# lastly tell the secondary processes (if any) that they are allowed to start again.
qt.mend()