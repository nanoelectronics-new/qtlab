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

period = 0.390
  
init = 0.045
manipulate = 0.300
read = 0.045
delay = 0.023 

t_burst = arange(0.005,0.280,0.001)

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

raw_input("Press Enter if uploading to AWG is finished")