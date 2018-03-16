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


  
init = 0.105
manipulate = 0.100
read = 0.105
period = init + manipulate + read
delay = 0.023 

t_burst = arange(0.005,0.080,0.001)



delay = 0.023  # ns
delay_IQ_to_PM = 0.040  # ns
PM_before_IQ = 0.010  #ns
overall_delay_IQ_to_PM = delay_IQ_to_PM + PM_before_IQ


for i,t in enumerate(t_burst):   # Creating waveforms for all sequence elements
    p = Wav.Waveform(waveform_name = 'WAV1elem%d'%(i+1), AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV')  

    Tpm = t + 2*PM_before_IQ  # PM pulse starts for PM_before_IQ and for PM_before_IQ after the IQ pulse
    start = init + 0.010 - overall_delay_IQ_to_PM - delay   # Time until the PM pulse starts

    if Tpm < overall_delay_IQ_to_PM:  # If a PM pulse does not overlap with an IQ pulse 

        gap = overall_delay_IQ_to_PM - Tpm  # A gap between the finishing of the PM pulse and starting of the IQ pulse
        rest = period - start - Tpm - gap - t  # Leftover of the period
        p.setValuesCH1([start, 0.0],[Tpm, 0.0],[gap,0.0],[t,500.0],[rest,0.0])   # I
        p.setMarkersCH1([0,1,0,0,0],[0,0,0,0,0])  
        p.setValuesCH2([start, 0.0],[Tpm, 0.0],[gap,0.0],[t,500.0],[rest,0.0])    # Q
        p.setMarkersCH2([0,1,0,0,0],[0,0,0,0,0])
      
    elif abs(Tpm - overall_delay_IQ_to_PM) < 0.001:  # If the PM pulse finishes exaclty when the IQ pulse starts

        rest = period - start - Tpm - t  # Leftover of the period

        p.setValuesCH1([start, 0.0],[Tpm, 0.0],[t,500.0],[rest,0.0])   # I
        p.setMarkersCH1([0,1,0,0],[0,0,0,0])  
        p.setValuesCH2([start, 0.0],[Tpm, 0.0],[t,500.0],[rest,0.0])    # Q
        p.setMarkersCH2([0,0,0,0],[0,0,0,0])

    elif  Tpm > overall_delay_IQ_to_PM:  # If the PM pulse overlaps with the IQ pulse 

        overlap = Tpm - overall_delay_IQ_to_PM
        rest = period - start - overall_delay_IQ_to_PM - t  # Leftover of the period


        p.setValuesCH1([start, 0.0],[overall_delay_IQ_to_PM, 0.0],[overlap,500.0],[t-overlap,500.0],[rest,0.0])   # I
        p.setMarkersCH1([0,1,1,0,0],[0,0,0,0,0])  
        p.setValuesCH2([start, 0.0],[overall_delay_IQ_to_PM, 0.0],[overlap,500.0],[t-overlap,500.0],[rest,0.0])    # Q
        p.setMarkersCH2([0,0,0,0,0],[0,0,0,0,0])


    p.setValuesCH3([init, 200.0],[manipulate, 0.0],[read,200.0])  # Gate
    p.setMarkersCH3([0,0,0],[0,0,0])


    seqCH1.append(p.CH1) 
    seqCH2.append(p.CH2) 
    seqCH3.append(p.CH3) 
seq.append(seqCH1) 
seq.append(seqCH2) 
seq.append(seqCH3) 
AWG_lib.set_waveform_trigger_all_wait_mean(seq,AWG_clock,AWGMax_amp, t_sync, sync) # Function for uploading and setting all sequence waveforms to AWG 

raw_input("Press Enter if uploading to AWG is finished")