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
AWG_clock = 1.0e9        
											
						
AWGMax_amp = 0.5         
   
t_sync = 0              
t_wait = 100  



sync = Wav.Waveform(waveform_name = 'WAV1elem%d'%0, AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV') # First element in sequence is synchronization element


 

seqCH1 = list() 
seqCH2 = list()	
seqCH3 = list() 
seq = list() 
#I = np.linspace(0,500*np.sqrt(2),3) # I vector from 0 until the radius of the sphere

period = 0.340
  
init = 0.105
manipulate_half = 0.065
read = 0.105
delay = 0.023 

t_burst_half = arange(0.003,0.041,0.001)

pi_half = 0.007  # Duration of the burst for the pi/2 rotation

delay = 0.023

for i,t in enumerate(t_burst_half):   # Creating waveforms for all sequence elements
    p = Wav.Waveform(waveform_name = 'WAV1elem%d'%(i+1), AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV')  

    a = init - delay + (manipulate_half - t - pi_half)
    b = pi_half 
    c = t*2
    d = pi_half
    e = period - a-b-c-d

    p.setValuesCH1([a, 0.0],[b, 500.0],[c,0.0],[d,500.0],[e,0.0])   # I
    p.setMarkersCH1([0,0,0,0,0],[0,0,0,0,0])  
    p.setValuesCH2([a, 0.0],[b, 500.0],[c,0.0],[d,500.0],[e,0.0])    # Q
    p.setMarkersCH2([0,0,0,0,0],[0,0,0,0,0])
    p.setValuesCH3([init, 200.0],[manipulate_half*2, 0.0],[read,200.0])  # Gate
    p.setMarkersCH3([0,0,0],[0,0,0])


    seqCH1.append(p.CH1) 
    seqCH2.append(p.CH2) 
    seqCH3.append(p.CH3) 
seq.append(seqCH1) 
seq.append(seqCH2) 
seq.append(seqCH3) 
AWG_lib.set_waveform_trigger_all_wait_mean(seq,AWG_clock,AWGMax_amp, t_sync, sync) # Function for uploading and setting all sequence waveforms to AWG 

raw_input("Press Enter if uploading to AWG is finished")