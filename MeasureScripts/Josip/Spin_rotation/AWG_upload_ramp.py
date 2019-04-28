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
AWG_clock = 10e6        
											
						
AWGMax_amp = 2.0         
Seq_length = 6   
t_sync = 0              
t_wait = 100  
Automatic_sequence_generation = False
ramp_amp = 4.0 # mV
ramp_div = 200.0 # The line 3 attenuators attenuation


sync = Wav.Waveform(waveform_name = 'WAV1elem%d'%0, AWG_clock = AWG_clock, TimeUnits = 'ms' , AmpUnits = 'mV') # First element in sequence is synchronization element


if not(Automatic_sequence_generation):  

    seqCH1 = list() 
    seq = list()
    seq_wav = list()


    

    for i in xrange(Seq_length):   # Creating waveforms for all sequence elements
        
        p = Wav.Waveform(waveform_name = 'WAV1elem%d'%(i+1), AWG_clock = AWG_clock, TimeUnits = 'ms' , AmpUnits = 'mV', TWAIT = 0)  
                                                                                                             
        p.setValuesCH1([3.0, -ramp_amp*ramp_div, ramp_amp*ramp_div], [3.0, -ramp_amp*ramp_div, ramp_amp*ramp_div])
        p.setMarkersCH1([1,0], [1,0])

        seqCH1.append(p.CH1)
        seq_wav.append(p)  # Sequence of complete waveforms. Needed for compatibility reasons.
                           # That the TWAIT flag can be passed on the Waveform and not Pulse hierarchy level. 


    seq.append(seqCH1) 

    # Function for uploading and setting all sequence waveforms to AWG
    AWG_lib.set_waveform_trigger_all(seq_wav,seq,AWG_clock,AWGMax_amp, t_sync, sync, do_plot = False) 


    raw_input("Press Enter if uploading to AWG is finished")