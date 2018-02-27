import AWG_lib
reload(AWG_lib)
import Waveform_PresetAmp as Wav
reload(Wav)
import numpy as np
#import qt
import matplotlib.pyplot as plt
from Waveform_PresetAmp import Pulse as pul
import datetime
from Background_correction import Back_corr as bc


## GENERAL SETTINGS

tau_vector =  arange(0.005,0.050,0.002)# period pulse in us
ch3_amp = 200.0



## SETTING AWG
#
AWG_clock = 1.0e9        
                                            
                        
AWGMax_amp = 0.5         
Seq_length = 3   
t_sync = 0              
t_wait = 100  
Automatic_sequence_generation = False   


sync = Wav.Waveform(waveform_name = 'WAV1elem%d'%0, AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV') # First element in sequence is synchronization element



name_counter = 174

## UPLOADING TO THE AWG
   
for tau_index,tau in enumerate(tau_vector):


    seqCH1 = list() 
    seqCH2 = list() 
    seqCH3 = list() 
    seq = list() 


    period = 0.130
    
    init = 0.015
    manipulate = 0.100
    read = 0.015 
    delay = 0.023 

    for i in xrange(Seq_length):   # Creating waveforms for all sequence elements
        p = Wav.Waveform(waveform_name = 'WAV1elem%d'%(i+1), AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV')  
                                                                                                                         
            

        a = (manipulate - tau)/2.0 - delay  # First part of the IQ pulse, with the delay compensation
        b = (manipulate - tau)/2.0   # Last (third) part of the IQ pulse, with the delay compensation
        p.setValuesCH1([init,0.0],[a,0.0],[tau,500.0],[b,0.0],[delay,0.0],[read, 0.0])   # I
        p.setMarkersCH1([0,1,0,0,0,0],[0,1,0,0,0,0])  
        p.setValuesCH2([init,0.0],[a,0.0],[tau,500.0],[b,0.0],[delay,0.0],[read, 0.0])    # Q
        p.setMarkersCH2([0,1,0,0,0,0],[0,1,0,0,0,0])
        p.setValuesCH3([init,ch3_amp],[a,0.0],[tau,0.0],[b,0.0],[delay,0.0],[read, ch3_amp])  # Gate
        p.setMarkersCH3([0,1,0,0,0,0],[0,1,0,0,0,0])



        seqCH1.append(p.CH1) 
        seqCH2.append(p.CH2) 
        seqCH3.append(p.CH3) 

    seq.append(seqCH1) 
    seq.append(seqCH2) 
    seq.append(seqCH3) 

    AWG_lib.set_waveform_trigger_all(seq,AWG_clock,AWGMax_amp, t_sync, sync) # Function for uploading and setting all sequence waveforms to AWG 


    #raw_input("Press Enter if uploading to AWG is finished")
    print("Waiting to upload the sequence to the AWG")
    sleep(10.0)
    print("Waiting finished")
            

## Turn on AWG channels and run it
    AWG.run()
    AWG.set_ch1_output(1)
    AWG.set_ch2_output(1)
    AWG.set_ch3_output(1)





    file_name = '1_3 IV %d'%(name_counter)
    
    name_counter += 1 
    gain = 1000e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    
    
    ramp_rate_Y = 0.25e-3 #T/s
    
    
    
    step_size_BY = -0.5e-3 
    
    BY_vector = arange(129e-3,120e-3+step_size_BY,step_size_BY) #T  #
    
    magnetY.set_rampRate_T_s(ramp_rate_Y)
    
    
    freq_vec = arange(5.75e9,6.00e9,3e6)  # frequency 
    
    qt.mstart()
    
    
    data = qt.Data(name=file_name)
    
    #saving directly in matrix format for diamond program
    new_mat = np.zeros(len(freq_vec)) # Empty vector for storing the data 
    data_temp = np.zeros(len(freq_vec))  # Temporary vector for storing the data
    
    
    data.add_coordinate('Frequency [Hz]')  #v2
    data.add_coordinate('Bfield [T]')   #v1
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
                # readout
                result = dmm.get_readval()/gain*1e12
                
                data_temp[j] = result
                # save the data point to the file, this will automatically trigger
                # the plot windows to update
                data.add_data_point(freq,total_field, result)  
            
                
    
                # the next function is necessary to keep the gui responsive. It
                # checks for instance if the 'stop' button is pushed. It also checks
                # if the plots need updating.
                qt.msleep(0.001)
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
    
    
    