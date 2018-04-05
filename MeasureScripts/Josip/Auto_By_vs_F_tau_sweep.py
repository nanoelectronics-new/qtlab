import AWG_lib
reload(AWG_lib)
from time import time
import Waveform_PresetAmp as Wav
reload(Wav)
import numpy as np
#import qt
import matplotlib.pyplot as plt
from Waveform_PresetAmp import Pulse as pul
import datetime
from Background_correction import Back_corr as bc


## GENERAL SETTINGS

tau_vector =  arange(0.020,0.100,0.010)  # burst duration in us
name_counter = 373

power = -4.0


### SETTING AWG
###
     

AWG_clock = 1.0e9    # AWG sampling rate                                                                         
AWGMax_amp = 0.5        
t_sync = 0          # Some things for the compatibility with AWG_lib scripts 
                               #they mean nothing for this case    

t_wait = 100  

# First element in sequence is synchronization element
sync = Wav.Waveform(waveform_name = 'WAV1elem%d'%0, AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV') # Creating the waveform objec


## UPLOADING TO THE AWG
   
for tau_index,tau in enumerate(tau_vector):


    seqCH1 = list()   # Empty lists as containers for the sequence elements
    seqCH2 = list() 
    seqCH3 = list()
    seqCH4 = list() 
    seq = list() 
            
            
            
              
    init_and_read = 0.210                       # First part of the pulse
    manipulate = 0.160                      # Second part of the pulse
                                                
    period = init_and_read + manipulate        # Total pulse period
                                   
            
            
            
    delay = 0.023                           # Delay of the IQ in ns
            
    gate_to_IQ = 0.010                      # Intentional pause between the onset of the C.B. part of the gate pulse (CH3) and the IQ pulse in ns
            
    delay_IQ_to_PM = 0.040                  # Additional delay between the IQ and PM in ns  
                                                    # Reason is that PM delays after IQ in the instrument and therefore need to be sent earlier to compensate
            
    PM_before_IQ = 0.010                    # Since the rise time of the PM is slower (approx 10 ns)
                                                    # The start of the PM pulse is 10 ns before and the end is 10 ns after the IQ pulse
                                                    # In other words - PM pulse is a window around IQ pulse, 20 ns wider
            
    overall_delay_IQ_to_PM = delay_IQ_to_PM + PM_before_IQ   #  Self descriptive
            
            
    IQ_duration = tau                         # Duration of the IQ pulse in ns
    PM_duration = IQ_duration + 2*PM_before_IQ  # Duration of the pm pulse in ns - window around IQ pulses
            
    for i in xrange(3):          # Creating waveforms for all sequence elements
        p = Wav.Waveform(waveform_name = 'WAV1elem%d'%(i+1), AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV')   # New waveform object for the new
                                                                                                                                  # sequence element
            
        a = init_and_read + gate_to_IQ - delay                                   # Time from the start of the period, until the start of the IQ pulse 
        rest_of_IQ = period - a - IQ_duration                           # The duration after the second IQ pulse until the end of the period
            
        p.setValuesCH1([a, 0.0],[IQ_duration, 500.0],[rest_of_IQ, 0.0])  # I analog wavefrom
        p.setMarkersCH1([0,0,0],[0,0,0])                                                       # I markers
        p.setValuesCH2([a, 0.0],[IQ_duration, 500.0],[rest_of_IQ, 0.0])   # Q analog wavefrom
        p.setMarkersCH2([0,0,0],[0,0,0])                                                       # Q markers
            
            
            
        p.setValuesCH3([init_and_read, 200.0],[manipulate, 0.0])  # Gate pulse analog wavefrom
        p.setMarkersCH3([0,0],[0,0])                              # Gate pulse markers
            
            
        b = a - overall_delay_IQ_to_PM
        rest_PM = period - b - PM_duration                     # The duration after the PM pulse until the end of the period
        p.setValuesCH4([b, 0.0],[PM_duration, 0.0],[rest_PM, 0.0])
        p.setMarkersCH4([0,1,0],[0,0,0])
            
               
            
            
        seqCH1.append(p.CH1) 
        seqCH2.append(p.CH2) 
        seqCH3.append(p.CH3) 
        seqCH4.append(p.CH4)
            
    seq.append(seqCH1) 
    seq.append(seqCH2) 
    seq.append(seqCH3) 
    seq.append(seqCH4)
    AWG_lib.set_waveform_trigger_all_wait_mean(seq,AWG_clock,AWGMax_amp, t_sync, sync) # Function for uploading and setting all sequence waveforms to AWG 


    #raw_input("Press Enter if uploading to AWG is finished")
    print("Waiting to upload the sequence to the AWG")
    sleep(10.0)
    print("Waiting finished")
            

    # Set the VSG power units
    VSG.set_power_units("dbm") 
    # Set the RF power
    VSG.set_power(power)
    # Turn the RF on
    VSG.set_status("on") 
    ## Run the AWG sequence 
    AWG.run()
    ## Turn ON all necessary AWG channels
    AWG.set_ch1_output(1)
    AWG.set_ch2_output(1)
    AWG.set_ch3_output(1)
    AWG.set_ch4_output(1)





    file_name = '1_3 IV %d_%dns'%(name_counter, tau*1000)
    
    name_counter += 1 
    gain = 1000e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    
    
    ramp_rate_Y = 0.25e-3 #T/s
    
    
    
    step_size_BY = -1.0e-3 
    
    BY_vector = arange(145e-3,115e-3+step_size_BY,step_size_BY) #T  #
    
    magnetY.set_rampRate_T_s(ramp_rate_Y)
    
    
    freq_vec = arange(5.5e9,6.5e9,3e6)  # frequency 
    
    qt.mstart()
    
    
    data = qt.Data(name=file_name)
    
    #saving directly in matrix format for diamond program
    new_mat = np.zeros(len(freq_vec)) # Empty vector for storing the data 
    data_temp = np.zeros(len(freq_vec))  # Temporary vector for storing the data
    
    
    data.add_coordinate('Frequency [Hz]')  #v2
    data.add_coordinate('By [T]')   #v1
    data.add_value('Current [pA]')
    
    plot2d = qt.Plot2D(data, name=file_name+' 2D_2',autoupdate=False)
    plot3d = qt.Plot3D(data, name=file_name+' 3D_2', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
    
    
    
    init_start = time()
    vec_count = 0
    
    
    try:
        for i,v1 in enumerate(BY_vector):  
            
            
            start = time()
            
            
            magnetY.set_field(BY_vector[i])  
    
        
            total_field = BY_vector[i]
    
            while math.fabs(BY_vector[i] - magnetY.get_field_get()) > 0.0001:
                qt.msleep(0.050)
    
    
    
    
    
    
            for j,freq in enumerate(freq_vec):  
    
                #IVVI.set_dac5(v2)
    
                VSG.set_frequency(freq)

                # the next function is necessary to keep the gui responsive. It
                # checks for instance if the 'stop' button is pushed. It also checks
                # if the plots need updating.
                qt.msleep(0.010)

                # readout
                result = dmm.get_readval()/gain*1e12
                
                data_temp[j] = result
                # save the data point to the file, this will automatically trigger
                # the plot windows to update
                data.add_data_point(freq,total_field, result)  
            
                
    
               
                
            data.new_block()
            stop = time()
            new_mat = np.column_stack((new_mat, data_temp))
            if i == 0: #Kicking out the first column filled with zero
                new_mat = new_mat[:,1:]
            np.savetxt(fname = data.get_filepath()+ "_matrix", X = new_mat, fmt = '%1.4e', delimiter = '  ', newline = '\n')
            
    
            plot2d.update()
    
            plot3d.update()
    
            vec_count = vec_count + 1
            print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(BY_vector.size - vec_count))))
            
            
    
        print 'Overall duration: %s sec' % (stop - init_start, )
    
    finally:
    
        bc(path = data.get_dir(), fname = data.get_filename()+"_matrix")
        # after the measurement ends, you need to close the data file.
        data.close_file()
        # lastly tell the secondary processes (if any) that they are allowed to start again.
        qt.mend()
    
    
    