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
AWG_clock = 1e9        
											
						
AWGMax_amp = 3         
Seq_length = 20    
t_sync = 0              
t_wait = 100  
Automatic_sequence_generation = False   


sync = Wav.Waveform(waveform_name = 'WAV1elem%d'%0, AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV') # First element in sequence is synchronization element


if not(Automatic_sequence_generation):  

    seqCH1 = list() 
    seqCH2 = list()	
    seq = list() 

    I = np.linspace(0,500*np.sqrt(2),3) # I vector from 0 until the radius of the sphere

    for i in xrange(Seq_length):   # Creating waveforms for all sequence elements
        p = Wav.Waveform(waveform_name = 'WAV1elem%d'%(i+1), AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV')  
                                                                                                                         
            
        #p.setValuesCH1([0.1, I[i]],[0.2, I[i]],[0.1, I[i]]) 
        #p.setMarkersCH1([1,0,0],[1,0,0])  
#
        #Q = np.sqrt((500*np.sqrt(2))**2-(I[i])**2)  # Q vector calculated such that the overall vector is always on the sphere - constant amplitude
        #
        #p.setValuesCH2([0.1, Q],[0.2, Q],[0.1, Q])
        #p.setMarkersCH2([1,0,0],[1,0,0])

        p.setValuesCH1([0.01, 0.0],[0.01, 500*np.sqrt(2)],[0.01, 0]) 
        p.setMarkersCH1([1,0,0],[1,0,0])  

        p.setValuesCH2([0.01, 0.0],[0.01, 500*np.sqrt(2)],[0.01, 0])
        p.setMarkersCH2([0,1,0],[0,1,0])

   
        seqCH1.append(p.CH1) 
        seqCH2.append(p.CH2) 

    seq.append(seqCH1) 
    seq.append(seqCH2) 

    AWG_lib.set_waveform_trigger_all(seq,AWG_clock,AWGMax_amp, t_sync, sync) # Function for uploading and setting all sequence waveforms to AWG 


    raw_input("Press Enter if uploading to AWG is finished")