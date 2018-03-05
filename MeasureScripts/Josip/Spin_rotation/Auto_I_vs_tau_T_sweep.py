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

T_mult_factor =  arange(1.1,1.6,0.1)# period pulse in us
ch3_amp = 200.0

name_counter = 240

### SETTING AWG
##
AWG_clock = 1.0e9                                                                     
AWGMax_amp = 0.5         
t_sync = 0              
t_wait = 100  



sync = Wav.Waveform(waveform_name = 'WAV1elem%d'%0, AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV') # First element in sequence is synchronization element


for Tmf_index,Tmf in enumerate(T_mult_factor):

    seqCH1 = list() 
    seqCH2 = list() 
    seqCH3 = list() 
    seq = list() 
    #I = np.linspace(0,500*np.sqrt(2),3) # I vector from 0 until the radius of the sphere
    
    period = 0.200*Tmf
      
    init = 0.030*Tmf
    manipulate = 0.200*Tmf
    read = 0.030*Tmf
    delay = 0.023 
    
    t_burst = arange(0.005,manipulate - 0.020,0.001)
    
    delay = 0.023
    
    for i,t in enumerate(t_burst):   # Creating waveforms for all sequence elements
        p = Wav.Waveform(waveform_name = 'WAV1elem%d'%(i+1), AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV')  
              
        x = (manipulate - t)/2
        b = delay - x
    
    
        if b >= 0.001000:
            a = init - b
            c = t - b
            d = delay + x
            e = read
            p.setValuesCH1([a, 0.0],[b, 500.0],[c,500.0],[d,0.0],[e,0.0])   # I
            p.setMarkersCH1([0,1,0,0,0],[0,1,0,0,0])  
            p.setValuesCH2([a, 0.0],[b, 500.0],[c,500.0],[d,0.0],[e,0.0])    # Q
            p.setMarkersCH2([0,1,0,0,0],[0,1,0,0,0])
            p.setValuesCH3([a, 200.0],[b, 200.0],[c,0.0],[d,0.0],[e,200.0])  # Gate
            p.setMarkersCH3([0,1,0,0,0],[0,1,0,0,0])
    
        elif abs(b) < 0.001000:    
            a = init - b
            c = t - b
            d = delay + x
            e = read
            p.setValuesCH1([a, 0.0],[c,500.0],[d,0.0],[e,0.0])   # I
            p.setMarkersCH1([0,1,0,0],[0,1,0,0])  
            p.setValuesCH2([a, 0.0],[c,500.0],[d,0.0],[e,0.0])    # Q
            p.setMarkersCH2([0,1,0,0],[0,1,0,0])
            p.setValuesCH3([a, 200.0],[c,0.0],[d,0.0],[e,200.0])  # Gate
            p.setMarkersCH3([0,1,0,0],[0,1,0,0])
    
        elif b <= 0.001000:
            b = abs(b)
            a = init 
            c = t 
            d = delay + x
            e = read
            p.setValuesCH1([a, 0.0],[b, 0.0],[c,500.0],[d,0.0],[e,0.0])   # I
            p.setMarkersCH1([0,1,0,0,0],[0,1,0,0,0])  
            p.setValuesCH2([a, 0.0],[b, 0.0],[c,500.0],[d,0.0],[e,0.0])    # Q
            p.setMarkersCH2([0,1,0,0,0],[0,1,0,0,0])
            p.setValuesCH3([a, 200.0],[b, 0.0],[c,0.0],[d,0.0],[e,200.0])  # Gate
            p.setMarkersCH3([0,1,0,0,0],[0,1,0,0,0])
    
        seqCH1.append(p.CH1) 
        seqCH2.append(p.CH2) 
        seqCH3.append(p.CH3) 
    seq.append(seqCH1) 
    seq.append(seqCH2) 
    seq.append(seqCH3) 
    AWG_lib.set_waveform_trigger_all_wait_mean(seq,AWG_clock,AWGMax_amp, t_sync, sync) # Function for uploading and setting all sequence waveforms to AWG 

    print("Waiting to upload the sequence to the AWG")
    sleep(10.0)
    print("Waiting finished")
            

# Turn on AWG channels and run it
    AWG.run()
    AWG.set_ch1_output(1)
    AWG.set_ch2_output(1)
    AWG.set_ch3_output(1)





    file_name = '1_3 IV %d_%dns'%(name_counter, period*1000)
    
    name_counter += 1 
    
    gain = 1000e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    tau_vector_repetitions = 15
    power = 0.0
    
    
    
    
    qt.mstart()
    
    
    data = qt.Data(name=file_name)
    
    
    data.add_coordinate('tau [ns]')
    data.add_value('Current [pA]')
    
    
    data.create_file()
    
     
    
    plot2d = qt.Plot2D(data, name='measure2D',autoupdate=False)
    
    
    
    
    #Turn the RF on
    #VSG.set_status("on") 
    ###Run the AWG sequence 
    #AWG.run()
    ##Turn ON all necessary AWG channels
    #AWG.set_ch1_output(1)
    #AWG.set_ch2_output(1)
    #AWG.set_ch3_output(1)
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
        #AWG.stop()
        #Turn OFF all necessary AWG channels
        #AWG.set_ch1_output(0)
        #AWG.set_ch2_output(0)
        #AWG.set_ch3_output(0)
    
    
        # after the measurement ends, you need to close the data file.
        data.close_file()
        # lastly tell the secondary processes (if any) that they are allowed to start again.
        qt.mend()

    
    