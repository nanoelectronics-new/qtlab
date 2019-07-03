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
reload(Wav)
#import qt
import matplotlib.pyplot as plt
from Waveform_PresetAmp import Pulse as pul



def upload_ramp_to_AWG(ramp_amp = 4):
    ### SETTING AWG
    ##
    AWG_clock = 10e6        
                                                
    ramp_div = 200.0 # The line 3 attenuators attenuation     
    ramp_amp = ramp_amp # mV                 
    AWGMax_amp = (ramp_amp/1000.0)*ramp_div*1.5 # Maximum amplitude is the maximum amplitude that ocurs
                                                # in the output waveform increased 1.5 time for safety         
    Seq_length = 6   
    t_sync = 0              
    t_wait = 100  
    Automatic_sequence_generation = False
    
    
    
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





ramp_amp = 1.0  # Amplitude of the ramp in mV
upload_ramp_to_AWG(ramp_amp = ramp_amp) # Call the function to upload ramp with a given amplitude to the AWG

# Initialize the UHFLI scope module
daq, scopeModule = UHFLI_lib.UHF_init_scope_module()





def do_meas_refl(bias = None, v2 = None, v1_start = None, v1_stop = None, v_middle = None, num_aver_pts = 20):

    if (bias == None) or (v2 == None) or (v1_start == None) or (v1_stop == None) or (v_middle == None): 
        raise Exception('Define the values first: bias, v2...')

    global name_counter
    name_counter += 1

    file_name = '13-17 IV %d GvsG_V_middle=%.2fmV'%(name_counter, v_middle)

    
    gate1div = 10.0
    gate2div = 1.0
    v_middle_factor = 1.0 
    
    bias = bias
    


    v2 = v2       #inner - the middle DC point of the ramp

    v1_vec = arange(v1_start,v1_stop,-0.02)      # Outer
    v1_vec_for_graph = v1_vec                   # Defining the v1_vec which is going to be used for the graph axis
    v1_mean = (v1_start + v1_stop)/2.0          # The value of non-divided DAC which is superimposed to the gate via an S3b card
    v1_vec = v1_vec - v1_mean

 

    scope_segment_length = daq.getDouble('/dev2169/scopes/0/length')
    scope_num_segments = daq.getDouble('/dev2169/scopes/0/segments/count')

    # Number of adjacent points to average in the read data
    num_aver_pts = num_aver_pts 

    num_points_vertical = scope_segment_length//num_aver_pts 
    ramp = np.linspace(-ramp_amp, ramp_amp, num_points_vertical)  # Defining the ramp segment
    
    qt.mstart()
    
    # Set the bias and static gates
    IVVI.set_dac1(bias)
    IVVI.set_dac7(v_middle/v_middle_factor)  
    IVVI.set_dac5(v2*gate2div)
    IVVI.set_dac6(v1_mean)

    #Run the AWG sequence - ramp
    AWG.run()
    #Turn ON necessary AWG channels
    AWG.set_ch1_output(1)
    
    
    # Create data files
    data = qt.Data(name=file_name)

    
    
    data.add_coordinate('V_G 16 [mV]')       # inner
    data.add_coordinate('V_G 18 [mV]')      # outer
    data.add_value('Refl_mag [V]')
    data.add_value('Refl_phase [deg]')
    
    
    
    
    
    
    data.create_file()

    
    
    #saving directly in matrix format 
    new_mat_mag = np.zeros(num_points_vertical) # Creating empty matrix for storing all data 
    new_mat_phase = np.zeros(num_points_vertical) # Creating empty matrix for storing all data 
    
    
    
    plot3d_mag = qt.Plot3D(data, name=file_name + "_2D_amplitude", coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
    #plot2d_mag = qt.Plot2D(data_mag, name=file_name + "_1D_amplitude",autoupdate=False)
    plot3d_phase = qt.Plot3D(data, name=file_name + "_2D_phase", coorddims=(1,0), valdim=3, style='image') #flipped coordims that it plots correctly
    #plot2d_phase = qt.Plot2D(data_phase, name=file_name + "_1D_phase",autoupdate=False)
    
    
    
    # preparation is done, now start the measurement.
    
   
    init_start = time()
    vec_count = 0
    
     
    
   
    daq.setInt('/dev2169/sigins/0/autorange', 1)  # Autoset amplification
    daq.setInt('/dev2169/sigouts/0/enables/3', 1) # Turn on the UHFLI out 1
    try:
        for i,v1 in enumerate(v1_vec):
            
        
            # set the voltage
        
            IVVI.set_dac4(v1*gate1div)
    
    
            
    
    
    
            # readout
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
            # the next function is necessary to keep the gui responsive. It
            # checks for instance if the 'stop' button is pushed. It also checks
            # if the plots need updating.
            qt.msleep(0.003)
    
            # save the data to the file
            v1_real = v1_vec_for_graph[i]
            data.add_data_point(v2 + ramp, np.linspace(v1_real,v1_real, num_points_vertical), refl_mag, refl_phase)
    
    
            data.new_block()
            stop = time()
    
            new_mat_mag = np.column_stack((new_mat_mag, refl_mag))
            new_mat_phase = np.column_stack((new_mat_phase, refl_phase))
    
            # Kicking out the first column with zeros
            if not(i):
                new_mat_mag = new_mat_mag[:,1:]
                new_mat_phase = new_mat_phase[:,1:]
    
    
            #plot2d_mag.update()
            #plot3d_mag.update()
            #plot2d_phase.update()
            #plot3d_phase.update()
    
            # Saving the matrix to the matrix filedata.get_filepath
            np.savetxt(fname = data.get_dir() + '/' + file_name + "_amp_matrix.dat", X=new_mat_mag, fmt='%1.4e', delimiter=' ', newline='\n')  
            np.savetxt(fname = data.get_dir() + '/' + file_name + "_phase_matrix.dat", X=new_mat_phase, fmt='%1.4e', delimiter=' ', newline='\n')  
    


    finally:
        print 'Overall duration: %s sec' % (stop - init_start, )
    
        plot3d_mag.update()
        plot3d_phase.update()

    
        #Saving plot images
        plot3d_phase.save_png(filepath = data.get_dir())
        plot3d_phase.save_eps(filepath = data.get_dir())
    
        plot3d_mag.save_png(filepath = data.get_dir())
        plot3d_mag.save_eps(filepath = data.get_dir())
    
        # after the measurement ends, you need to close the data files.
        data.close_file()
    
    
        settings_path = data.get_dir()
    
        UHFLI_lib.UHF_save_settings(daq, path = settings_path)
    
        #Turn OFF the AWG 
        AWG.stop()
        AWG.set_ch1_output(0)
        daq.setInt('/dev2169/sigouts/0/enables/3', 0) # Turn OFF the UHFLI out 1
        # lastly tell the secondary processes (if any) that they are allowed to start again.
        qt.mend()

#v2s = np.arange(-600.0,-400.0,20.0)

#for v2 in v2s:
do_meas_refl(bias = 0.0, v2 = -112.0, v1_start = -310.2, v1_stop = -311.6, v_middle = 0.0, num_aver_pts = 40)






    
