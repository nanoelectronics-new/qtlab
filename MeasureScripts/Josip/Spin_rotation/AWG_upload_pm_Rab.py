import AWG_lib
reload(AWG_lib)
import Waveform_PresetAmp as Wav
reload(Wav)
import numpy as np
#import qt
import matplotlib.pyplot as plt
from Waveform_PresetAmp import Pulse as pul


### SETTING AWG
##
AWG_clock = 1.0e9    # AWG sampling rate     
                                            
                        
AWGMax_amp = 0.5       
   
t_sync = 0          # Some things for the compatibility with AWG_lib scripts 
                    # they mean nothing for this case    
t_wait = 100   



sync = Wav.Waveform(waveform_name = 'WAV1elem%d'%0, AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV') # Creating the waveform object

seqCH1 = list()   # Empty lists as containers for the sequence elements
seqCH2 = list() 
seqCH3 = list()
seqCH4 = list() 
seq = list() 



  
init = 20                             # First part of the pulse in num of points
manipulate = 140                    # Second part of the pulse in num of points
read = 20                             # Third part of the pulse in num of points
period = init + manipulate + read     # Total pulse period in num of points
                       

t_burst = arange(6,10,1)     # Array of increasing durations between the pulses (in the Ramsey experiment case)

delay = 23                           # Delay of the IQ in ns

gate_to_IQ = 10                      # Intentional pause between the onset of the C.B. part of the gate pulse (CH3) and the IQ pulse in ns

delay_IQ_to_PM = 40                  # Additional delay between the IQ and PM in ns  
                                        # Reason is that PM delays after IQ in the instrument and therefore need to be sent earlier to compensate

PM_before_IQ = 10                    # Since the rise time of the PM is slower (approx 10 ns)
                                        # The start of the PM pulse is 10 ns before and the end is 10 ns after the IQ pulse
                                        # In other words - PM pulse is a window around IQ pulse, 20 ns wider

overall_delay_IQ_to_PM = delay_IQ_to_PM + PM_before_IQ   #  Self descriptive







for i,t in enumerate(t_burst):          # Creating waveforms for all sequence elements
    p = Wav.Waveform(waveform_name = 'WAV1elem%d'%(i+1), AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV')   # New waveform object for the new
                                                                                                                      # sequence element

    a = init + read + gate_to_IQ - delay                   # Time from the start of the period, until the start of the IQ pulse 
    IQ_duration = t                                 # The burst duration
    rest_of_IQ = period - a - IQ_duration           # The duration after the IQ pulse until the end of the period

    p.setValuesCH1([a, 0.0],[IQ_duration, 500.0],[rest_of_IQ, 0.0])                         # I analog wavefrom
    p.setMarkersCH1([0,0,0],[0,0,0])                                                        # I markers
    p.setValuesCH2([a, 0.0],[IQ_duration, 500.0],[rest_of_IQ, 0.0])                         # Q analog wavefrom
    p.setMarkersCH2([0,0,0],[0,0,0])                                                        # Q markers

    #print round(a*AWG_clock)/1000000 + round(IQ_duration*AWG_clock)/1000000 + round(rest_of_IQ*AWG_clock)/1000000
       
   


    p.setValuesCH3([init, 200.0],[read,200.0],[manipulate, 0.0])    # Gate pulse analog wavefrom
    p.setMarkersCH3([0,0,0],[0,0,0])                                # Gate pulse markers

    #print round(init*AWG_clock)/1000000 + round(read*AWG_clock)/1000000 + round(manipulate*AWG_clock)/1000000

    
    PM_duration = IQ_duration + 2*PM_before_IQ  # Duration of the pm pulse in ns - window around IQ pulses
    b = a - overall_delay_IQ_to_PM
    
    if b > 0:   # if b is positive then there is no reason for splitting the PM pulse into two parts   
        
        rest_PM = period - b - PM_duration                     # The duration after the PM pulse until the end of the period
        p.setValuesCH4([b, 0.0],[PM_duration, 0.0],[rest_PM, 0.0])
        p.setMarkersCH4([0,1,0],[0,0,0])
        
    elif b <= 0: # if b is negative then split the PM pulse into two - part of it at the start and part of it at the end of the CH4 pulse

        b = abs(b)
        rest_PM = period - PM_duration                     # The duration after the PM pulse until the end of the period
        PM_first_part = PM_duration - b
        p.setValuesCH4([PM_first_part, 0.0],[rest_PM, 0.0],[b, 0.0])
        p.setMarkersCH4([1,0,1],[0,0,0])
#
    

    print len(p.CH1.waveform)
    print len(p.CH2.waveform)
    print len(p.CH3.waveform)

    seqCH1.append(p.CH1) 
    seqCH2.append(p.CH2) 
    seqCH3.append(p.CH3) 
    seqCH4.append(p.CH4)

seq.append(seqCH1) 
seq.append(seqCH2) 
seq.append(seqCH3) 
seq.append(seqCH4) 
AWG_lib.set_waveform_trigger_all_wait_mean(seq,AWG_clock,AWGMax_amp, t_sync, sync) # Function for uploading and setting all sequence waveforms to AWG 

raw_input("Press Enter if uploading to AWG is finished")