from numpy import pi, random, arange, size, linspace
import numpy as np
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import UHFLI_lib
reload(UHFLI_lib)
import AWG_lib
reload(AWG_lib)
import Waveform_PresetAmp as Wav
#reload(Wav)
#import qt
import matplotlib.pyplot as plt
from Waveform_PresetAmp import Pulse as pul




def upload_ramp_to_AWG(ramp_amp = 4):
    ### SETTING AWG
    ##
    AWG_clock = 10e6        
                                                
    ramp_div = 200.0 # The line 4 attenuators attenuation     
    ramp_amp = ramp_amp # mV                 
    AWGMax_amp = (ramp_amp/1000.0)*ramp_div*1.5 # Maximum amplitude is the maximum amplitude that ocurs
                                                # in the output waveform increased 1.5 time for safety         
    Seq_length = 6   
    t_sync = 0              
    t_wait = 100  
    Automatic_sequence_generation = False
    
    
    
    sync = Wav.Waveform(waveform_name = 'WAV1elem%d'%0, AWG_clock = AWG_clock, TimeUnits = 'ms' , AmpUnits = 'mV') # First element in sequence is synchronization element
    
    
    if not(Automatic_sequence_generation):  
    
        seqCH3 = list() 
        seq = list()
        seq_wav = list()
    
    
        
    
        for i in xrange(Seq_length):   # Creating waveforms for all sequence elements
            
            p = Wav.Waveform(waveform_name = 'WAV1elem%d'%(i+1), AWG_clock = AWG_clock, TimeUnits = 'ms' , AmpUnits = 'mV', TWAIT = 0)  
                                                                                                                 
            p.setValuesCH3([1.0, -ramp_amp*ramp_div, ramp_amp*ramp_div], [1.0, -ramp_amp*ramp_div, ramp_amp*ramp_div])
            p.setMarkersCH3([1,0], [1,0])
    
            seqCH3.append(p.CH3)
            seq_wav.append(p)  # Sequence of complete waveforms. Needed for compatibility reasons.
                               # That the TWAIT flag can be passed on the Waveform and not Pulse hierarchy level. 
    
    
        seq.append(seqCH3) 
    
        # Function for uploading and setting all sequence waveforms to AWG
        AWG_lib.set_waveform_trigger_all(seq_wav,seq,AWG_clock,AWGMax_amp, t_sync, sync, do_plot = False) 
    
    
        raw_input("Press Enter if uploading to AWG is finished")





ramp_amp = 0.8  # Amplitude of the ramp in mV
upload_ramp_to_AWG(ramp_amp = ramp_amp) # Call the function to upload ramp with a given amplitude to the AWG

# Initialize the UHFLI scope module
daq, scopeModule = UHFLI_lib.UHF_init_scope_module()





def do_line_scan_ramp(v2 = None, v1, num_aver_pts = 20, num_ramps = 2):
     

    # Initialize the UHFLI scope module
    daq, scopeModule = UHFLI_lib.UHF_init_scope_module()
    
    gate1div = 1.0
    gate2div = 1.0


    


    v2 = v2       #inner - the middle DC point of the ramp
    v1 = v1
    v2_initial = v2 - (num_ramps-1)*ramp_amp    # Complete vertical sweep ic segmented into n_ramps so v2 needs to be positioned properly for each segment
                                                # Initial one is given by this formula

 

    scope_segment_length = daq.getDouble('/dev2169/scopes/0/length')
    scope_num_segments = daq.getDouble('/dev2169/scopes/0/segments/count')

    # Number of adjacent points to average in the read data
    num_aver_pts = num_aver_pts 

    num_points_vertical = scope_segment_length//num_aver_pts
    ramp = np.linspace(-num_ramps*ramp_amp, num_ramps*ramp_amp, num_ramps*num_points_vertical)  # Defining the ramp segment
    
    #qt.mstart()
    

    #Run the AWG sequence - ramp
    AWG.run()
    #Turn ON necessary AWG channels
    AWG.set_ch3_output(1)
    
    


    
    
   
    daq.setInt('/dev2169/sigins/0/autorange', 1)  # Autoset amplification
    daq.setInt('/dev2169/sigouts/0/enables/3', 1) # Turn on the UHFLI out 1


    try:

            
        
        # set the voltage
    
        IVVI.set_dac1(v1*gate1div)

        # UHFLI data containers
        refl_mag_full = np.array([])
        refl_phase_full = np.array([])
        
        for n in xrange(num_ramps):
            
            IVVI.set_dac2(v2_initial + (n*2*ramp_amp)) # Setting the v2 properly in the middle of each vertical segment
            # the next function is necessary to keep the gui responsive. It
            # checks for instance if the 'stop' button is pushed. It also checks
            # if the plots need updating.
            qt.msleep(0.05)
            # readout - getting the recording corresponding to one ramp
            num_samples, wave = UHFLI_lib.get_scope_record(daq = daq, scopeModule= scopeModule)           
            
            
            # Organizing each scope shot into individual rows 
            refl_mag = wave[0].reshape(-1, scope_segment_length)   
            refl_phase = wave[1].reshape(-1, scope_segment_length) 
            # Average the read scope segments (rows) to one segment (one row)
            refl_mag = np.mean(refl_mag, axis = 0)
            refl_phase = np.mean(refl_phase, axis = 0)
            # Reduce the number of samples - average amongst adjacent samples
            refl_mag = np.mean(refl_mag[:num_points_vertical*num_aver_pts].reshape(-1,num_aver_pts), axis=1)
            refl_phase = np.mean(refl_phase[:num_points_vertical*num_aver_pts].reshape(-1,num_aver_pts), axis=1)
            refl_mag_full = np.concatenate((refl_mag_full, refl_mag))
            refl_phase_full = np.concatenate((refl_phase_full, refl_phase))
                
    
    

    

    
    finally:

        #Turn OFF the AWG 
        AWG.stop()
        AWG.set_ch3_output(0)
        #aq.setInt('/dev2169/sigouts/0/enables/3', 0) # Turn OFF the UHFLI out 1
        # lastly tell the secondary processes (if any) that they are allowed to start again.
        #qt.mend()
        #plt.plot(v_vec, result)
        #plt.xlabel('Gate 6 [mV]')
        #plt.ylabel('Current [pA]')
        #plt.show()

    return refl_mag_full, refl_phase_full



#Vms = [2000.0, 2300.0, 2600.0, 2900.0, 3200.0]
#
#
#for Vm in Vms:
#do_line_scan_ramp(v2 = -352.5, v1= -420.58, num_aver_pts = 20, num_ramps = 1)





















    
