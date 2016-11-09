import AWG_lib
reload(AWG_lib)
import Waveform_PresetAmp as Wav
reload(Wav)
import numpy as np
#import qt
import matplotlib.pyplot as plt



### SETTING AWG
##
AWG_clock = 10e6        # Wanted AWG clock. Info https://www.google.at/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&ved=0ahUKEwjI5KCdy_TLAhXFuxQKHamZAHoQFggcMAA&url=http%3A%2F%2Fwww.tek.com%2Fdl%2F76W-19764-1.pdf&usg=AFQjCNGsPEYMv-JCA5vht2I1cSlzCVVVAA&sig2=RFFJuEw5rKO_uGo69H7U2A&cad=rja
											# In pdf on link read section "AWG: Simple Concept, Maximum Flexibility"
											
						# Take care about waveform and sequence length and clock rate  - AWG has limited capability
AWGMax_amp = 3          # In Volts!!! Maximum needed amplitude on all channels for your particular experiment (noise reduction) - need to be set at the beginning
Seq_length = 10     # Sequence length (number of periods - waveforms)
t_sync = 5000
Automatic_sequence_generation = False   # Flag for determining type of sequence generation: Automatic - True,  Manual - False 


sync = Wav.Waveform(waveform_name = 'WAV1elem%d'%0, AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV') # First element in sequence is synchronization element


# Here was automatic sequence generation - look for it in previous verisons


#### MANUAL sequence generation - sequnce is generated manually - more flexible
if not(Automatic_sequence_generation):  # If user wants manual sequence generation (Automatic_sequence_generation = False)

    seqCH1 = list() # Initializing list for channel 1 sequence
    seqCH2 = list()	# Initializing list for channel 2 sequence
    seq = list() # Initializing list that will contain all sequences (all channels)


    T = np.array([20,500,500])
    load_time = np.array([20, 100, 300, 500, 900, 1300, 2000, 3000, 4000, 5000]) #different waiting times in us
    #deltaT = deltaT**3*10
    

    A1 = np.array([0.0,-3.0,-1.9,0.0,0.0])*31.25 # Initial amplitudes, 31.25 is factor of attenuation
    A2 = np.array([0.0,3.0,1.9,0.0,0.0])*31.25*0.81 # Initial amplitudes, 31.25 is factor of attenuation, 1.2 is factor for diagonal pulsing
    biasT_correctionCH1 = 0  #A1[1]*(1-exp(-load_time/23000.0)) #tau=RC=18ms correction needed because biasT cuts the signal for long tw
    biasT_correctionCH2 = 0  #A2[1]*(1-exp(-load_time/23000.0)) #tau=RC=18ms correction needed because biasT cuts the signal for long tw

   

    

    for i in xrange(Seq_length):   # Creating waveforms for all sequence elements
        p = Wav.Waveform(waveform_name = 'WAV1elem%d'%(i+1), AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV')  # Generating next object wavefrom in sequnce
                                                                                                                         # Starting from second element (WAV1elem%d'%(i+1)) 
                                                                                                                         # because sync element is first 
        #T[0] = T[0] + deltaT[i]
        T[0] = load_time[i]
        read_levelCH1 = A1[2] #+ biasT_correctionCH1[i]
        read_levelCH2 = A2[2] #+ biasT_correctionCH2[i]

        p.setValuesCH1([100, A1[0]],[T[0], A1[1]], [T[1],read_levelCH1], [T[2],A1[3]],[100,A1[4]]) # Setting waveform shape for one wavefrom object p in sequence seq for AWG channel 1 - [Time1,Amp1],[Time2,Amp2]...  Time in TimeUnits and Amp in AmpUnits
        p.setMarkersCH1([0,0,1,0,0],[0,0,1,0,0])  # Setting marker just in the first wavefrom of the sequence (further is zero)
    
        p.setValuesCH2([100, A2[0]],[T[0], A2[1]], [T[1],read_levelCH2], [T[2],A2[3]],[100,A2[4]]) # Setting waveform shape for one wavefrom object p in sequence seq for AWG channel 1 - [Time1,Amp1],[Time2,Amp2]...  Time in TimeUnits and Amp in AmpUnits
        p.setMarkersCH2([0,0,1,0,0],[0,0,1,0,0])  # Setting marker just in the first wavefrom of the sequence (further is zero)
        
        seqCH1.append(p.CH1) # Filing sequence list for channel 1 (seqCH1) with next waveform (period)
        seqCH2.append(p.CH2) # Filing sequence list for channel 2 (seqCH2) with next waveform (period)
    

    seq.append(seqCH1) # Putting sequence list for channel 1 in list that contain all sequences (all channels)
    seq.append(seqCH2) # Putting sequence list for channel 2 in list that contain all sequences (all channels)



    AWG_lib.set_waveform_trigger_all(seq,AWG_clock,AWGMax_amp, t_sync, sync) # Function for uploading and setting all sequence waveforms to AWG 
    
    raw_input("Press Enter if uploading to AWG is finished")