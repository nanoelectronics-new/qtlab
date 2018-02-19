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
AWG_clock = 1.2e9        
											
						
AWGMax_amp = 0.5         
   
t_sync = 0              
t_wait = 100  



sync = Wav.Waveform(waveform_name = 'WAV1elem%d'%0, AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV') # First element in sequence is synchronization element


 

seqCH1 = list() 
seqCH2 = list()	
seqCH3 = list() 
seq = list() 
#I = np.linspace(0,500*np.sqrt(2),3) # I vector from 0 until the radius of the sphere

period = 0.400

init = 0.100
manipulate = 0.200
read = 0.100  

t_burst = arange(0.005,0.150,0.005)

delay = 0.023

for i,t in enumerate(t_burst):   # Creating waveforms for all sequence elements
    p = Wav.Waveform(waveform_name = 'WAV1elem%d'%(i+1), AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV')  
          
    t1 = (period - t)/2.0 - delay  # First part of the IQ pulse, with the delay compensation
    t3 = (period - t)/2.0 + delay  # Last (third) part of the IQ pulse, with the delay compensation
    p.setValuesCH1([t1, 0.0],[t, 500.0],[t3, 0.0])   # I
    p.setMarkersCH1([0,1,0],[0,1,0])  
    p.setValuesCH2([t1, 0.0],[t, 500.0],[t3, 0.0])    # Q
    p.setMarkersCH2([0,0,0],[0,0,0])
    p.setValuesCH3([init, 100.0],[manipulate, 0.0],[read, 100.0])  # Gate
    p.setMarkersCH3([0,0,1],[0,0,1])

    seqCH1.append(p.CH1) 
    seqCH2.append(p.CH2) 
    seqCH3.append(p.CH3) 
seq.append(seqCH1) 
seq.append(seqCH2) 
seq.append(seqCH3) 
AWG_lib.set_waveform_trigger_all_wait_mean(seq,AWG_clock,AWGMax_amp, t_sync, sync) # Function for uploading and setting all sequence waveforms to AWG 

raw_input("Press Enter if uploading to AWG is finished")