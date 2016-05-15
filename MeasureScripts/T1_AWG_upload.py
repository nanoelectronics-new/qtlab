import T1_lib_v2 as T1_lib
reload(T1_lib)
import Waveform_PresetAmp as Wav
import numpy as np
#import qt
import matplotlib.pyplot as plt



### SETTING AWG
##
AWG_clock = 10e6        # Wanted AWG clock. Info https://www.google.at/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&ved=0ahUKEwjI5KCdy_TLAhXFuxQKHamZAHoQFggcMAA&url=http%3A%2F%2Fwww.tek.com%2Fdl%2F76W-19764-1.pdf&usg=AFQjCNGsPEYMv-JCA5vht2I1cSlzCVVVAA&sig2=RFFJuEw5rKO_uGo69H7U2A&cad=rja
											# In pdf on link read section "AWG: Simple Concept, Maximum Flexibility"
											
						# Take care about waveform and sequence length and clock rate  - AWG has limited capability
AWGMax_amp = 4          # Volts.  Maximum needed amplitude on all channels for your particular experiment (noise reduction) - need to be set at the beginning
Seq_length = 10       # Sequence length (number of periods - waveforms)
    
Automatic_sequence_generation = True   # Flag for determining type of sequence generation: Automatic - True,  Manual - False 








        
#### AUTOMATIC sequence generation - sequnce is generated by interpolation between waveforms p1 and p2
p1 = Wav.Waveform(waveform_name = 'WAV5', AWG_clock = AWG_clock, TimeUnits = 'ms' , AmpUnits = 'mV')  # Generating waveform object p1
                                                                                                          # Important is to define TimeUnits and AmpUnits    
p1.setValuesCH2([10,1000], [5, 0], [5, 0]) # Setting waveform shape for waveform object p1 for AWG channel 1 - [Time1,Amp1],[Time2,Amp2]...  Time in TimeUnits and Amp in AmpUnits
p1.setMArkersCH2([0,1,0],[0,1,0]) # Setting markers values (M1 and M2) for waveform object p1 for AWG channel 1  - Markers are repeated every period
#p1.setValuesCH4([10,1000], [5, 500], [5, 0]) 
#p1.setMArkersCH4([1,0,0],[1,0,0])


p2 = Wav.Waveform(waveform_name = 'WAV2', AWG_clock = AWG_clock, TimeUnits = 'ms' , AmpUnits = 'mV')  # Generating waveform object p2
    
p2.setValuesCH2([10,500], [5, 0], [5, 0])  # Setting waveform shape for waveform object p2 for AWG channel 1 - [Time1,Amp1],[Time2,Amp2]...  Time in TimeUnits and Amp in AmpUnits       
p2.setMArkersCH2([0,1,0],[0,1,0]) # Setting markers values (M1 and M2) for waveform object p2 for AWG channel 1 - Markers are repeated every period
#p2.setValuesCH4([10,1000], [5, 500], [5, 0]) 
#p2.setMArkersCH4([1,0,0],[1,0,0])

seq = p1.interpolate_to(Seq_length,p2)   # Creating sequence by interpolation between wavefrom p1 and p2 in Seq_length number of steps

if Automatic_sequence_generation:   # If user wants Automatic sequence generation (Automatic_sequence_generation = True)
	T1_lib.set_waveform(seq,AWG_clock,AWGMax_amp,Seq_length)  # Function for uploading and setting all sequence waveforms to AWG 



#### MANUAL sequence generation - sequnce is generated manually - more flexible
seqCH1 = list() # Initializing list for channel 1 sequence
seqCH2 = list()	# Initializing list for channel 2 sequence
seq = list() # Initializing list that will contain all sequences (all channels)

A = np.array([500,400,300]) # Initial amplitudes


for i in xrange(Seq_length):   # Creating wavefroms for all sequence elements
    p = Wav.Waveform(waveform_name = 'WAV1elem%d'%i, AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV')  # Generating next object wavefrom in sequnce

    p.setValuesCH1([100,0],[1200,A[0]], [1200,A[1]], [1200, A[2]]) # Setting waveform shape for one wavefrom object p in sequence seq for AWG channel 1 - [Time1,Amp1],[Time2,Amp2]...  Time in TimeUnits and Amp in AmpUnits
    A = A - 40 # Defining amplitude change between wavefroms in sequence
    if i == 0:
        M1 = 1
    else:
        M1 = 0
    p.setMArkersCH1([0,0,0,0],[0,0,0,0])  # Setting marker just in the first wavefrom of the sequence (further is zero)
    
    seqCH1.append(p.CH1) # Filing sequence list for channel 1 (seqCH1) with next waveform (period)
    

seq.append(seqCH1) # Putting sequence list for channel 1 in list that contain all sequences (all channels)
seq.append(seqCH2) # Putting sequence list for channel 2 in list that contain all sequences (all channels)

if not(Automatic_sequence_generation):  # If user wants manual sequence generation (Automatic_sequence_generation = False)
    T1_lib.set_waveform(seq,AWG_clock,AWGMax_amp,Seq_length) # Function for uploading and setting all sequence waveforms to AWG 
    
raw_input("Press Enter if uploading to AWG is finished")