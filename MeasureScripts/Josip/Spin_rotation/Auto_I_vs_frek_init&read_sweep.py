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


## GENERAL SETTINGS

init_read = array([0.070])#arange(70.0,400.0,10.0)# period pulse in us
ch3_amp = 200.0

name_counter = 247

### SETTING AWG
##
AWG_clock = 1.2e9                                                                     
AWGMax_amp = 0.5         
t_sync = 0              
t_wait = 100  



sync = Wav.Waveform(waveform_name = 'WAV1elem%d'%0, AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV') # First element in sequence is synchronization element


for index,in_rd in enumerate(init_read):

    ### SETTING AWG
    ##
    AWG_clock = 1.0e9    # AWG sampling rate     
                                                
                            
    AWGMax_amp = 0.5       
       
    t_sync = 0          # Some things for the compatibility with AWG_lib scripts 
                        #they mean nothing for this case    
    t_wait = 100   
    
    
    
    sync = Wav.Waveform(waveform_name = 'WAV1elem%d'%0, AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV') # Creating the waveform object
    
    seqCH1 = list()   # Empty lists as containers for the sequence elements
    seqCH2 = list() 
    seqCH3 = list()
    seqCH4 = list() 
    seq = list() 
    
    
    
      
    init_read = in_rd                            # First part of the pulse
    manipulate = 0.130                      # Second part of the pulse
                                            # Third part of the pulse
    period = init_read + manipulate        # Total pulse period
                           
    
    
    
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
    
        a = init_read + gate_to_IQ - delay                                   # Time from the start of the period, until the start of the IQ pulse 
        rest_of_IQ = period - a - IQ_duration                           # The duration after the second IQ pulse until the end of the period
    
        p.setValuesCH1([a, 0.0],[IQ_duration, 500.0],[rest_of_IQ, 0.0])  # I analog wavefrom
        p.setMarkersCH1([0,0,0],[0,0,0])                                                       # I markers
        p.setValuesCH2([a, 0.0],[IQ_duration, 500.0],[rest_of_IQ, 0.0])   # Q analog wavefrom
        p.setMarkersCH2([0,0,0],[0,0,0])                                                       # Q markers
    
    
    
        p.setValuesCH3([init_read, 200.0],[manipulate, 0.0])  # Gate pulse analog wavefrom
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

    ## adopt the DC point to take the new average value into account
    #dac5_ref = -358.92
    #dac5_new = (avg_ch3 - 46)*0.008 - 358.92
    #IVVI.set_dac5(dac5_new)
#
#
#
#
    #for bzvz in xrange(3):
    #    file_name = '1_3 IV %d'%(name_counter)
    #
    #    name_counter += 1 
    #
    #    gain = 1000e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    #    tau_vector_repetitions = 5
    #    power = 0.0
    #
    #
    #
    #
    #    qt.mstart()
    #
    #
    #    data = qt.Data(name=file_name)
    #
    #
    #    data.add_coordinate('tau [ns]')
    #    data.add_value('Current [pA]')
    #
    #
    #    data.create_file()
    #
    # 
    #
    #    plot2d = qt.Plot2D(data, name=file_name,autoupdate=False)
    #
    #
    #
    #
    #    #Turn the RF on
    #    #VSG.set_status("on") 
    #    ###Run the AWG sequence 
    #    #AWG.run()
    #    ##Turn ON all necessary AWG channels
    #    #AWG.set_ch1_output(1)
    #    #AWG.set_ch2_output(1)
    #    #AWG.set_ch3_output(1)
    #    #Force the AWG to start from the first element of the sequence
    #    AWG._ins.force_jump(1)
    #
    #
    #
    #    # preparation is done, now start the measurement.
    #    # It is actually a simple loop.
    #    VSG.set_power(power)
    #
    #  
    #    tau_vector = np.zeros(len(t_burst)) # Empty vector for averaging intermediate tau result vectors
    #
    #    start = time()
    #    try: 
    #        for k in xrange(tau_vector_repetitions):  #repeat the one tau vector measurement n times
    #            AWG._ins.force_jump(1)     # Start from the first tau in the sequence
    #            for j,v2 in enumerate(t_burst):  
    #        
    #            
    #        
    #                # readout
    #           
    #           
    #                tau_vector[j] += dmm.get_readval()/gain*1e12
    #            
    #            
    #                AWG._ins.force_event()
    #        
    #                # the next function is necessary to keep the gui responsive. It
    #                # checks for instance if the 'stop' button is pushed. It also checks
    #                # if the plots need updating.
    #                qt.msleep(0.002)
    #    
    #        # Calculate the average value of the recorded tau vector
    #        tau_vector = tau_vector/tau_vector_repetitions
    #        # save the data point to the file    
    #
    #        data.add_data_point(t_burst*1e3,tau_vector)  
    #        data.new_block()
    #        stop = time()
    #    
    #        plot2d.update()
    #    
    #        stop = time()
    #        print 'Duration: %s sec' % (stop - start, )
    #
    #
    #    finally:
    #    
    #
    #        # Switching off the RF 
    #        #VSG.set_status("off") 
    #
    #        #Stop the AWG sequence 
    #        #AWG.stop()
    #        #Turn OFF all necessary AWG channels
    #        #AWG.set_ch1_output(0)
    #        #AWG.set_ch2_output(0)
    #        #AWG.set_ch3_output(0)
    #
    #
    #        # after the measurement ends, you need to close the data file.
    #        data.close_file()
    #        # lastly tell the secondary processes (if any) that they are allowed to start again.
    #        qt.mend()
#
    
    