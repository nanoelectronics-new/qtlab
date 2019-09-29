import AWG_lib
reload(AWG_lib)
import Waveform_PresetAmp as Wav
reload(Wav)
import numpy as np
#import qt
import matplotlib.pyplot as plt
from Waveform_PresetAmp import Pulse as pul


num_aver_ramps = 5 # Number of averaged ramps
v_stepping_dac = np.arange(-400.0,-350.0,5.0)  # Values of the stepping DAC
v_stepping_dac_mean = np.mean(v_stepping_dac)
v_stepping_dac_ramp = v_stepping_dac - v_stepping_dac_mean
print v_stepping_dac_mean, v_stepping_dac_ramp[0], v_stepping_dac_ramp[-1]


def upload_ramp_to_AWG(ramp_amp = 4, num_aver_ramps = 1):
    ### SETTING AWG
    ##
    AWG_clock = 10e6        
                                                
    ramp_div = 200.0 # The line 3 attenuators attenuation     
    ramp_amp = ramp_amp # mV                 
    AWGMax_amp = (ramp_amp/1000.0)*ramp_div*1.5 # Maximum amplitude is the maximum amplitude that ocurs
                                                # in the output waveform increased 1.5 time for safety         
    Seq_length = num_aver_ramps*len(v_stepping_dac_ramp) # Sequence length is the multiplication of the number of averaged ramps and number of stepped axis steps
    t_sync = 0              
    t_wait = 100  
    Automatic_sequence_generation = False
    
    
    
    sync = Wav.Waveform(waveform_name = 'WAV1elem%d'%0, AWG_clock = AWG_clock, TimeUnits = 'ms' , AmpUnits = 'mV') # First element in sequence is synchronization element
    
    
    if not(Automatic_sequence_generation):  
    
        seqCH1 = list() 
        seqCH2 = list()
        seq = list()
        seq_wav = list()
    
    
        step_index = 0
    
        for i in xrange(Seq_length):   # Creating waveforms for all sequence elements
            
            p = Wav.Waveform(waveform_name = 'WAV1elem%d'%(i+1), AWG_clock = AWG_clock, TimeUnits = 'ms' , AmpUnits = 'mV', TWAIT = 0)  
            

            ## CH1                                                                                                  
            p.setValuesCH1([3.0, -ramp_amp*ramp_div, ramp_amp*ramp_div], [3.0, -ramp_amp*ramp_div, ramp_amp*ramp_div])
            p.setMarkersCH1([1,0], [1,0])
  


            ## CH2
            # Set the next value of the stepping DAC after the averaging for the previous value has finished 
            # Did by the integer division of the total index with the num_aver_ramps
            p.setValuesCH2([3.0, v_stepping_dac_ramp[i//num_aver_ramps]], [3.0, v_stepping_dac_ramp[i//num_aver_ramps]])
            p.setMarkersCH2([0,0],[0,0])
    
            seqCH1.append(p.CH1)
            seqCH2.append(p.CH2)
            seq_wav.append(p)  # Sequence of complete waveforms. Needed for compatibility reasons.
                               # That the TWAIT flag can be passed on the Waveform and not Pulse hierarchy level. 
    
    
        seq.append(seqCH1)
        seq.append(seqCH2) 
    
        # Function for uploading and setting all sequence waveforms to AWG
        AWG_lib.set_waveform_trigger_all(seq_wav,seq,AWG_clock,AWGMax_amp, t_sync, sync, do_plot = False) 
    
    
        raw_input("Press Enter if uploading to AWG is finished")



upload_ramp_to_AWG(ramp_amp = 2, num_aver_ramps = num_aver_ramps)