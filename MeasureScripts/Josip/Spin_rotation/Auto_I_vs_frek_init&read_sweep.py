import AWG_lib
reload(AWG_lib)
from time import time
import Waveform_PresetAmp as Wav
reload(Wav)
import numpy as np
#import qt
import matplotlib.pyplot as plt
from Waveform_PresetAmp import Pulse as pul
import datetime
from Background_correction import Back_corr as bc




file_name = '1_3 IV 342'
    
gain = 1000e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

init_read = arange(0.030,0.300,0.010) # Init + read duration in us
freq_vec = arange(5.70e9,6.30e9,3e6)  # Frequency vector 

qt.mstart()


data = qt.Data(name=file_name)

#saving directly in matrix format for diamond program
new_mat = np.zeros(len(freq_vec)) # Empty vector for storing the data 
data_temp = np.zeros(len(freq_vec))  # Temporary vector for storing the data


data.add_coordinate('Frequency [Hz]')  #v2
data.add_coordinate('Init&read_duration [ns]')   #v1
data.add_value('Current [pA]')

plot2d = qt.Plot2D(data, name=file_name+' 2D_2',autoupdate=False)
plot3d = qt.Plot3D(data, name=file_name+' 3D_2', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
        
        
VSG.set_power_units("dbm")  # Setting the power units of the VSG to "dBm"
VSG.set_power(0.0)          # Setting the power of the VSG to 0 dBm   
VSG.set_status('on')        # Turning on the VSG output         
        
vec_count = 0

init_start = time()         # Starting time of the measurement








try:
    for index,in_rd in enumerate(init_read):
        start = time()   # Starting time of the current trace
    
        ### SETTING AWG
        ##
     

        AWG_clock = 1.2e9    # AWG sampling rate                                                                         
        AWGMax_amp = 0.5        
        t_sync = 0          # Some things for the compatibility with AWG_lib scripts 
                               #they mean nothing for this case    
        t_wait = 100   
        
        
        # First element in sequence is synchronization element
        sync = Wav.Waveform(waveform_name = 'WAV1elem%d'%0, AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV') # Creating the waveform object
        
        seqCH1 = list()   # Empty lists as containers for the sequence elements
        seqCH2 = list() 
        seqCH3 = list()
        seqCH4 = list() 
        seq = list() 
        
        
        
          
        init_and_read = in_rd                       # First part of the pulse
        manipulate = 0.120                      # Second part of the pulse
                                            
        period = init_and_read + manipulate        # Total pulse period
                               
        
        
        
        delay = 0.023                           # Delay of the IQ in ns
        
        gate_to_IQ = 0.010                      # Intentional pause between the onset of the C.B. part of the gate pulse (CH3) and the IQ pulse in ns
        
        delay_IQ_to_PM = 0.040                  # Additional delay between the IQ and PM in ns  
                                                # Reason is that PM delays after IQ in the instrument and therefore need to be sent earlier to compensate
        
        PM_before_IQ = 0.010                    # Since the rise time of the PM is slower (approx 10 ns)
                                                # The start of the PM pulse is 10 ns before and the end is 10 ns after the IQ pulse
                                                # In other words - PM pulse is a window around IQ pulse, 20 ns wider
        
        overall_delay_IQ_to_PM = delay_IQ_to_PM + PM_before_IQ   #  Self descriptive
        
        
        IQ_duration = 0.080                         # Duration of the IQ pulse in ns
        PM_duration = IQ_duration + 2*PM_before_IQ  # Duration of the pm pulse in ns - window around IQ pulses
        
        for i in xrange(3):          # Creating waveforms for all sequence elements
            p = Wav.Waveform(waveform_name = 'WAV1elem%d'%(i+1), AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV')   # New waveform object for the new
                                                                                                                              # sequence element
        
            a = init_and_read + gate_to_IQ - delay                                   # Time from the start of the period, until the start of the IQ pulse 
            rest_of_IQ = period - a - IQ_duration                           # The duration after the second IQ pulse until the end of the period
        
            p.setValuesCH1([a, 0.0],[IQ_duration, 500.0],[rest_of_IQ, 0.0])  # I analog wavefrom
            p.setMarkersCH1([0,0,0],[0,0,0])                                                       # I markers
            p.setValuesCH2([a, 0.0],[IQ_duration, 500.0],[rest_of_IQ, 0.0])   # Q analog wavefrom
            p.setMarkersCH2([0,0,0],[0,0,0])                                                       # Q markers
        
        
        
            p.setValuesCH3([init_and_read, 200.0],[manipulate, 0.0])  # Gate pulse analog wavefrom
            p.setMarkersCH3([0,0],[0,0])                              # Gate pulse markers
        
        
            b = a - overall_delay_IQ_to_PM
            rest_PM = period - b - PM_duration                     # The duration after the PM pulse until the end of the period
            p.setValuesCH4([b, 0.0],[PM_duration, 0.0],[rest_PM, 0.0])
            p.setMarkersCH4([0,1,0],[0,0,0])
        
           
        
        
            seqCH1.append(p.CH1) 
            seqCH2.append(p.CH2) 
            seqCH3.append(p.CH3) 
            seqCH4.append(p.CH4)
        
        seq.append(seqCH1) 
        seq.append(seqCH2) 
        seq.append(seqCH3) 
        seq.append(seqCH4)
        avg_ch3 = AWG_lib.set_waveform_trigger_all_wait_mean(seq,AWG_clock,AWGMax_amp, t_sync, sync) # Function for uploading and setting all sequence waveforms to AWG 
    
        print("Waiting to upload the sequence to the AWG")
        sleep(10.0)
        print("Waiting finished")
                
     
        # Turn on AWG channels and run it
        AWG.run()
        AWG.set_ch1_output(1)
        AWG.set_ch2_output(1)
        AWG.set_ch3_output(1)
        AWG.set_ch4_output(1)
    
        # adopt the DC point to take the new average value into account
        dac5_ref = -358.19  # Referent dac5 voltage
        dac5_new = (avg_ch3 - 135.48)*0.008 + dac5_ref  # Calculating the new dac5 voltage based on the reference and the mean
                                                        # value of the reference pulse and the new pulse
        IVVI.set_dac5(dac5_new)
    
    
    
    
    
    
    #############  I vs FREK vs INIT+READ DURATION:
    ###############################################
          
        try:
            for j,freq in enumerate(freq_vec):  
    
    
                VSG.set_frequency(freq)
                # the next function is necessary to keep the gui responsive. It
                # checks for instance if the 'stop' button is pushed. It also checks
                # if the plots need updating.
                # Also it is important for the VSG ouput to settle down after the freq has been changed 
                qt.msleep(0.010)
                # readout
                result = dmm.get_readval()/gain*1e12
                
                data_temp[j] = result
                # save the data point to the file, this will automatically trigger
                # the plot windows to update
                data.add_data_point(freq,in_rd*1000, result)   # The second argunment is the init+read duration multiplied by 1000
                                                               # to get nanoseconds
            
                
    
                
        finally:
    
            data.new_block()
            stop = time()
            new_mat = np.column_stack((new_mat, data_temp))
            if i == 0: #Kicking out the first column filled with zero
                new_mat = new_mat[:,1:]
            np.savetxt(fname = data.get_filepath()+ "_matrix", X = new_mat, fmt = '%1.4e', delimiter = '  ', newline = '\n')
            
    
            plot2d.update()
    
            plot3d.update()
    
            vec_count = vec_count + 1
            stop = time()  # Finishing time of the current trace
            print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(init_read.size - vec_count))))
            
finally:
    print 'Overall duration: %s sec' % (stop - init_start, )
            
    bc(path = data.get_dir(), fname = data.get_filename()+"_matrix")
    # after the measurement ends, you need to close the data file.
    data.close_file()
    

    # Switching off the RF 
    VSG.set_status("off") 

    #Stop the AWG sequence 
    AWG.stop()
    #Turn OFF all necessary AWG channels
    AWG.set_ch1_output(0)
    AWG.set_ch2_output(0)
    AWG.set_ch3_output(0)
    AWG.set_ch4_output(0)

    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
    
    