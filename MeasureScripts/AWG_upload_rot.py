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
															
AWGMax_amp = 1         
Seq_length = 5     
t_sync = 0              
t_wait = 100  
Automatic_sequence_generation = False   

sync = Wav.Waveform(waveform_name = 'WAV1elem%d'%0, AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV') # First element in sequence is synchronization element

if not(Automatic_sequence_generation):  

    seqCH1 = list() 
    seqCH2 = list()	
    seq = list() 

    for i in xrange(Seq_length):   # Creating waveforms for all sequence elements
        p = Wav.Waveform(waveform_name = 'WAV1elem%d'%(i+1), AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV')                                                                                                                   

        if i == 0:
            I = 500*np.sqrt(2)
            Q = 0.0
        elif i == 1:
            I = -500.0
            Q = 500.0  # 135
        elif i == 2:
            I = 500*np.sqrt(2)  # 0 
            Q = 0.0
        elif i == 3:
            I = -500.0               # -135
            Q = -500.0 
        elif i == 4:
            I = 500*np.sqrt(2)
            Q = 0.0

        p.setValuesCH1([0.005, I],[0.01, I],[0.005, I]) 
        p.setMarkersCH1([1,0,0],[1,0,0])  
        p.setValuesCH2([0.005, Q],[0.01, Q],[0.005, Q])
        p.setMarkersCH2([0,1,0],[0,1,0])
        seqCH1.append(p.CH1) 
        seqCH2.append(p.CH2) 
    seq.append(seqCH1) 
    seq.append(seqCH2) 

    AWG_lib.set_waveform_trigger_all(seq,AWG_clock,AWGMax_amp, t_sync, sync) # Function for uploading and setting all sequence waveforms to AWG 
    raw_input("Press Enter if uploading to AWG is finished")