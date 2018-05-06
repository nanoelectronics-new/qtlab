import AWG_lib
reload(AWG_lib)
import Waveform_PresetAmp as Wav
reload(Wav)
import numpy as np
#import qt
import matplotlib.pyplot as plt
from Waveform_PresetAmp import Pulse as pul


### SETTING AWG
###
     

AWG_clock = 1.0e8    # AWG sampling rate                                                                         
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
        
        
        
          
IQ_on = 10.0                    # Part during which the RF burst is on, in us
IQ_off = 10.0                      # Part during which the RF burst is off, in us
                                            

                               
        
        
        

        
for i in xrange(2):          # Creating waveforms for all sequence elements
    p = Wav.Waveform(waveform_name = 'WAV1elem%d'%(i+1), AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV', repeat = 50000)   # New waveform object for the new
                                                                                                                              # sequence element
              
    if i == 0:     # Creating the high level element   
        p.setValuesCH1([IQ_on, 500.0],[IQ_off, 500.0])                  # I analog wavefrom
        p.setMarkersCH1([1,1],[0,0])                                # I markers
        p.setValuesCH2([IQ_on, 500.0],[IQ_off, 500.0])   # Q analog wavefrom
        p.setMarkersCH2([0,0],[0,0])                                # Q markers
        p.setValuesCH3([IQ_on, 500.0],[IQ_off, 500.0])   # Q analog wavefrom
        p.setMarkersCH3([0,0],[0,0])                                # Q markers

    elif i == 1:     # Creating the low level element  

        p.setValuesCH1([IQ_on, 00.0],[IQ_off, 0.0])                  # I analog wavefrom
        p.setMarkersCH1([0,0],[0,0])                                # I markers
        p.setValuesCH2([IQ_on, 00.0],[IQ_off, 0.0])   # Q analog wavefrom
        p.setMarkersCH2([0,0],[0,0])                                # Q markers
        p.setValuesCH3([IQ_on, 00.0],[IQ_off, 0.0])   # Q analog wavefrom
        p.setMarkersCH3([0,0],[0,0])                                # Q markers



        
        
    seqCH1.append(p.CH1) 
    seqCH2.append(p.CH2) 
    seqCH3.append(p.CH3)

seq.append(seqCH1) 
seq.append(seqCH2) 
seq.append(seqCH3) 
AWG_lib.set_waveform_trigger_all_wait_mean(seq,AWG_clock,AWGMax_amp, t_sync, sync) # Function for uploading and setting all sequence waveforms to AWG 
    