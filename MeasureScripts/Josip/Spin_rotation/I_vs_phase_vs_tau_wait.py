from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import numpy as np
import AWG_lib
reload(AWG_lib)
import Waveform_PresetAmp as Wav
reload(Wav)
import matplotlib.pyplot as plt
from Waveform_PresetAmp import Pulse as pul
from Background_correction import Back_corr as bc


def  I_vs_phase_vs_tau_wait(fname = "Random", f = 5.887e9):   
    
    file_name = fname
    
    
    gain = 1000e6               # Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    tau_vector_repetitions = 5  # Number of whole traces averages
    f_center = f          # Frequency in Hz
    
    power = 4.0                 # RF power in dBm
    
    tau_wait = arange(0.006,0.120,0.004)    # Array of increasing durations between the pulses 
    thetas = np.linspace(0.0,360.0,100)         # Angle of the rotation axis associated with the second pi/2 pulse, in respect 
                                            # to the angle of the rotation axis of the first pi/2 puls
    
    
    #saving directly in matrix format for diamond program
    new_mat = np.zeros(len(thetas)) # Creating empty matrix for storing all data  
    
    
    qt.mstart()
    
    
    data = qt.Data(name=file_name)
    
    
    data.add_coordinate('delta phi [deg]')
    data.add_coordinate('tau wait [ns]')
    data.add_value('Current [pA]')
    
    
    
    data.create_file()
    
     
    
    plot2d = qt.Plot2D(data, name=file_name +'2D',autoupdate=False)
    plot3d = qt.Plot3D(data, name=file_name +'3D', coorddims=(1,0), valdim=3, style='image') 
      
    
    Update_AWG = True  # Flag for indication weather to upload or not a sequence to the AWG 
    
    
      
    
                           
    
    
    
    
    
    ### SETTING AWG
    ##
    AWG_clock = 1.2e9    # AWG sampling rate     
                                                                     
    AWGMax_amp = 1.0       
       
    t_sync = 0          # Some things for the compatibility with AWG_lib scripts 
                        #they mean nothing for this case    
    t_wait = 100 
    
    init = 0.030                          # First part of the pulse
    manipulate = 0.160                      # Second part of the pulse
    read = 0.030                          # Third part of the pulse
    period = init + manipulate + read       # Total pulse period
    
    delay = 0.023                           # Delay of the IQ in ns
    
    gate_to_IQ = 0.010                      # Intentional pause between the onset of the C.B. part of the gate pulse (CH3) and the IQ pulse in ns
    
    IQ_duration = 0.009                      # Duration of the IQ pulse in ns
    
    I_amp = 707.11  # mV
    Q_amp = 707.11  # mV
    
    vec_count = 0
    
    
    for i,t in enumerate(tau_wait):          # Creating waveforms for all sequence elements
        start = time()                               # Getting the timestamp for the calculation of the remaining measurement time
        if Update_AWG:      # Check weather the AWG sequence needs to be updated or not
        
            a = init + gate_to_IQ - delay                   # Time from the start of the period, until the start of the IQ pulse 
            rest_of_IQ = period - a - 2*IQ_duration - t     # The duration after the second IQ pulse until the end of the period
        
            sync = Wav.Waveform(waveform_name = 'WAV1elem%d'%0, AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV') # Creating the waveform object
            seqCH1 = list()   # Empty lists as containers for the sequence elements
            seqCH2 = list() 
            seqCH3 = list()
        
            seq = list() 
        
            for m,theta in enumerate(thetas):
                p = Wav.Waveform(waveform_name = 'WAV1elem%d'%(m+1), AWG_clock = AWG_clock, TimeUnits = 'us' , AmpUnits = 'mV')   # New waveform object for the new
                                                                                                                              # sequence element
                I = I_amp * np.cos(np.deg2rad(theta))         
                Q = Q_amp * np.sin(np.deg2rad(theta))   
        
                p.setValuesCH1([a, 0.0],[IQ_duration, I_amp],[t,0.0],[IQ_duration, I],[rest_of_IQ, 0.0])   # I analog wavefrom
                p.setMarkersCH1([0,0,0,0,0],[0,0,0,0,0])                                                       # I markers
                p.setValuesCH2([a, 0.0],[IQ_duration, 0.0],[t,0.0],[IQ_duration, Q],[rest_of_IQ, 0.0])   # Q analog wavefrom
                p.setMarkersCH2([0,0,0,0,0],[0,0,0,0,0])                                                       # Q markers
            
            
            
                p.setValuesCH3([init, 200.0],[manipulate, 0.0],[read,200.0])  # Gate pulse analog wavefrom
                p.setMarkersCH3([0,0,0],[0,0,0])                              # Gate pulse markers
            
            
            
            
            
                seqCH1.append(p.CH1) 
                seqCH2.append(p.CH2) 
                seqCH3.append(p.CH3) 
        
        
            seq.append(seqCH1) 
            seq.append(seqCH2) 
            seq.append(seqCH3) 
            
            AWG_lib.set_waveform_trigger_all_wait_mean(seq,AWG_clock,AWGMax_amp, t_sync, sync) # Function for uploading and setting all sequence waveforms to AWG 
            
            print("Waiting to upload the sequence to the AWG")
            sleep(90.0)
            print("Waiting finished")
    
    
    
    
    
    
        # Turn the RF on
        VSG.set_status("on")
        # Set the VSG power units
        VSG.set_power_units("dbm") 
        # Set the RF power
        VSG.set_power(power)
        # Set the RF frequency
        VSG.set_frequency(f_center)
        ##Run the AWG sequence 
        AWG.run()
        #Turn ON all necessary AWG channels
        AWG.set_ch1_output(1)
        AWG.set_ch2_output(1)
        AWG.set_ch3_output(1)
        #AWG.set_ch4_output(1)
        #Force the AWG to start from the first element of the sequence
        AWG._ins.force_jump(1)
        
        
        
        # preparation is done, now start the measurement.
        # It is actually a simple loop.
        
        tau_vector = np.zeros(len(thetas))   # Data vector for recording and averaging determined number of line traces
        
        init_start = time()
              
       
        for k in xrange(tau_vector_repetitions):    # Repeat the one trace measurement n times
            AWG._ins.force_jump(1)                  # Start from the first tau in the sequence
            for j,v2 in enumerate(thetas):            # Going thorugh thetas
                
                # the next function is necessary to keep the gui responsive. It
                # checks for instance if the 'stop' button is pushed. It also checks
                # if the plots need updating.
                qt.msleep(0.010)
                # Readout
                tau_vector[j] += dmm.get_readval()/gain*1e12
                
                
                AWG._ins.force_event()
                      
        # Calculate the average value of the recorded tau vector
        tau_vector = tau_vector/tau_vector_repetitions
        # save the data point to the file    
      
        tau_wait_vector = np.linspace(t,t,len(thetas))
        data.add_data_point(thetas,tau_wait_vector,tau_vector)  
        data.new_block()

        new_mat = np.column_stack((new_mat,tau_vector))   # Gluing new tau_vector to the present matrix
        if i == 0:                                        # Kicking out the first column, filled with zeros, from the matrix 
            new_mat = new_mat[:,1:]
        np.savetxt(fname = data.get_filepath()+ "_matrix", X = new_mat, fmt = '%1.4e', delimiter = '  ', newline = '\n')
        
        plot2d.update()
        plot3d.update()
        
        stop = time()              # Some things for being able to calculate the remaining measurement time
        vec_count = vec_count + 1
        # Calculating and showing the remaining measurement time
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(len(tau_wait) - vec_count))))
    
    
    # Calculating and showing the overall measurement time
    print 'Overall duration: %s sec' % (stop - init_start, )
    
    
    # Switching off the RF 
    VSG.set_status("off") 
    #Stop the AWG sequence 
    AWG.stop()
    #Turn OFF AWG channels
    AWG.set_ch1_output(0)
    AWG.set_ch2_output(0)
    AWG.set_ch3_output(0)
    # after the measurement ends, you need to close the data file.
    data.close_file()
    
    # Do the background correction
    bc(path = data.get_dir(), fname = data.get_filename()+"_matrix")
    
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
    





num_meas = 568
f_center =  5.887e9  # Center frequency in Hz
f_offsets = np.linspace(-20e6,20e6,5e6) # Frequency offset in Hz

for i,f in enumerate(f_offsets):
    I_vs_phase_vs_tau_wait(fname = "1_3 IV %d_offset=%.2f MHz"%(num_meas,f/1e6), f = (f_center + f))
    num_meas += 1

