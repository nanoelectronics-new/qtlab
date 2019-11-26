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
execfile('C:/QTLab/qtlab/MeasureScripts/Josip/helping_functions.py') # Same as import save the plot function




# Initialize the UHFLI scope module
daq, scopeModule = UHFLI_lib.UHF_init_scope_module()





def upload_ramp_to_AWG(ramp_amp = 4, v_stepping_dac = None):

    if v_stepping_dac == None:
        raise Exception

    ### SETTING AWG
    ##
    AWG_clock = 10e6        
                                                
    ramp_div_step = 10.0        # Total division on the path to the stepped gate
    ramp_div_ramp = 200.0
    ramp_amp = ramp_amp    # mV
    # Maximum amplitude is the maximum amplitude that ocurs
    # in the output waveform increased 1.5 times for safety    
    if abs(ramp_amp*ramp_div_ramp) > abs(max(v1_vec))*ramp_div_step: # Take a bigger of the two div factors
        AWGMax_amp = (ramp_amp/1000.0)*ramp_div_ramp*1.5  
    else:
        AWGMax_amp = abs(max(v1_vec))*ramp_div_step*1.5/1000.0     

    t_sync = 0              
    t_wait = 100  
    Automatic_sequence_generation = False
    
    
    
    sync = Wav.Waveform(waveform_name = 'WAV1elem%d'%0, AWG_clock = AWG_clock, TimeUnits = 'ms' , AmpUnits = 'mV') # First element in sequence is synchronization element
    
    
    if not(Automatic_sequence_generation):  
    
        seqCH3 = list() 
        seqCH4 = list()
        seq = list()
        seq_wav = list()
    
    
        step_index = 0
    
        for i, v_step in enumerate(v_stepping_dac):   # Creating waveforms for all sequence elements
            
            p = Wav.Waveform(waveform_name = 'WAV1elem%d'%(i+1), AWG_clock = AWG_clock, TimeUnits = 'ms' , AmpUnits = 'mV', TWAIT = 0)  
            

            ## CH3
            # Creating ramps for the ramping gate                                                                                                  
            p.setValuesCH3([0.5, -ramp_amp*ramp_div_ramp, 0.0], [0.5, 0.0, ramp_amp*ramp_div_ramp])
            if i==0: # Set marker only at the starting element of the sequence
                p.setMarkersCH3([1,0],[1,0])
            else:    
                p.setMarkersCH3([0,0],[0,0])
  


            ## CH4
            # Set the next value of the stepping DAC 
            p.setValuesCH4([0.5, v_step*ramp_div_step], [0.5, v_step*ramp_div_step])
            p.setMarkersCH4([0,0], [0,0])
    
            seqCH3.append(p.CH3)
            seqCH4.append(p.CH4)
            seq_wav.append(p)  # Sequence of complete waveforms. Needed for compatibility reasons.
                               # That the TWAIT flag can be passed on the Waveform and not Pulse hierarchy level. 
    
    
        seq.append(seqCH3)
        seq.append(seqCH4) 
    
        # Function for uploading and setting all sequence waveforms to AWG
        AWG_lib.set_waveform_trigger_all(seq_wav,seq,AWG_clock,AWGMax_amp, t_sync, sync, do_plot = False) 
    
    
        raw_input("Press Enter if uploading to AWG is finished")





def do_meas_refl_whole(bias = None, v2 = None, v1_start = None, v1_stop = None, v1_step = 0.12, v_middle = None, num_aver_pts = 20, ramp_amp = 5, averages = 8):
    '''Function for running gate vs gate scans. Gate 1 (ramps) and Gate 2 (steps) volages are supplied from the AWG around the mean voltage value 
        provided by IVVI DACs. 
        A whole 2D scan is recorded in one go and read from the UHFLI scope, then it is transformed in corresponding matrices in which rows are
        averaged for num_aver_pts. Finally, "averages" number of this 2D scans are measured and averaged.
    ''' 

    if (bias == None) or (v2 == None) or (v1_start == None) or (v1_stop == None) or (v_middle == None): 
        raise Exception('Define the values first: bias, v2...')

    global name_counter
    name_counter += 1

  

    file_name = '7-11 IV %d GvsG_V_middle=%.2fmV'%(name_counter, v_middle)

    
    gate1div = 1.0
    gate2div = 1.0
    v_middle_factor = 1.0 
    
    bias = bias
    num_ramps = 1 # This is not used here, but it is kept for the compatibility reasons and set to 1




    v2 = v2       # Inner - the middle DC point of the ramp
    v2_initial = v2 - (num_ramps-1)*ramp_amp    # Complete vertical sweep ic segmented into n_ramps so v2 needs to be positioned properly for each segment
                                                # Initial one is given by this formula
    v1_vec = arange(v1_start,v1_stop,v1_step)      # Outer
    v1_vec_for_graph = v1_vec                   # Defining the v1_vec which is going to be used for the graph axis (without the mean substraction)
    v1_mean = (v1_start + v1_stop)/2.0          # The value of non-divided DAC which is superimposed to the gate via an S3b card
    v1_vec = v1_vec - v1_mean                   # Stepping dac values which should be generated by the AWG

    #upload_ramp_to_AWG(ramp_amp = ramp_amp, v_stepping_dac = v1_vec) # Call the function to upload ramp with a given amplitude to the AWG


    scope_sampling_rate = 7.03e6    # In Hz
    ramp_duration = 1e-3            # In seconds
    scope_segment_length = scope_sampling_rate*ramp_duration*len(v1_vec)
    daq.setDouble('/dev2169/scopes/0/length',scope_segment_length)  # Set number of samples to record in the scope that coresponds to one 2D map
    daq.setDouble('/dev2169/scopes/0/trigdelay', (scope_segment_length/2.0)/scope_sampling_rate)
    #scope_segment_length = daq.getDouble('/dev2169/scopes/0/length')
    #scope_num_segments = daq.getDouble('/dev2169/scopes/0/segments/count')




    # Number of adjacent points to average in the read data
    num_aver_pts = num_aver_pts 

    num_points_vertical = (scope_sampling_rate*ramp_duration)//num_aver_pts
    ramp = np.linspace(-num_ramps*ramp_amp, num_ramps*ramp_amp, num_ramps*num_points_vertical)  # Defining the ramp segment
    
    #qt.mstart()
    
    # Set the bias and static gates
    IVVI.set_dac3(bias)
    IVVI.set_dac7(v_middle/v_middle_factor)  
    #IVVI.set_dac5(v2*gate2div)
    IVVI.set_dac6(v1_mean)

    #Run the AWG sequence - ramp
    AWG.run()
    #Turn ON necessary AWG channels
    AWG.set_ch3_output(1)
    
    
    # Create data files
    data = qt.Data(name=file_name)

    
    
    data.add_coordinate('V_G 4 [mV]')       # inner
    data.add_coordinate('V_G 6 [mV]')      # outer
    data.add_value('Refl_mag [V]')
    data.add_value('Refl_phase [deg]')
    
    
    
    
    
    
    data.create_file()

    
    


    
    
    
    #plot3d_mag = qt.Plot3D(data, name=file_name + "_2D_amplitude", coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
    #plot2d_mag = qt.Plot2D(data_mag, name=file_name + "_1D_amplitude",autoupdate=False)
    #plot3d_phase = qt.Plot3D(data, name=file_name + "_2D_phase", coorddims=(1,0), valdim=3, style='image') #flipped coordims that it plots correctly
    #plot2d_phase = qt.Plot2D(data_phase, name=file_name + "_1D_phase",autoupdate=False)
    
    
    
    # preparation is done, now start the measurement.
    
   
    init_start = time()
    vec_count = 0
    
     
    
   
    daq.setInt('/dev2169/sigins/0/autorange', 1)  # Autoset amplification
    daq.setInt('/dev2169/sigouts/0/enables/3', 1) # Turn on the UHFLI out 1


        
    
    # set the voltage

    # IVVI.set_dac6(v1*gate1div)
    # UHFLI data containers
    refl_mag_averaged = np.array([])
    refl_phase_averaged = np.array([])
        
    for n in xrange(num_ramps):
        
        for avgs in xrange(averages):
            IVVI.set_dac5(v2_initial + (n*2*ramp_amp)) # Setting the v2 properly in the middle of each vertical segment
            # the next function is necessary to keep the gui responsive. It
            # checks for instance if the 'stop' button is pushed. It also checks
            # if the plots need updating.
            qt.msleep(0.01)
            # readout - getting the recording corresponding to one ramp
            num_samples, wave = UHFLI_lib.get_scope_record(daq = daq, scopeModule= scopeModule)           
            
            # Organizing the scope shot into a matrix corresponding to 2D map where columns correspond to responses to ramps
            refl_mag = wave[0].reshape(-1, scope_sampling_rate*ramp_duration).T
            refl_phase = wave[1].reshape(-1, scope_sampling_rate*ramp_duration).T

            # Kick out the last elements from each measurement, which do not fit in num_points_vertical*num_aver_pts
            refl_mag = refl_mag[:num_points_vertical*num_aver_pts,:]
            refl_phase = refl_phase[:num_points_vertical*num_aver_pts,:]
            # Reduce the number of samples - average amongst adjacent samples of each ramp 
            # Average every num_aver_pts point of each column in the matrix
            # General formula for taking the average of r rows for a 2D array a with c columns:
            # a.transpose().reshape(-1,r).mean(1).reshape(c,-1).transpose()
            refl_mag = refl_mag.transpose().reshape(-1,num_aver_pts).mean(1).reshape(-1,num_points_vertical).transpose()
            refl_phase = refl_phase.transpose().reshape(-1,num_aver_pts).mean(1).reshape(-1,num_points_vertical).transpose()
            # Averaging amongst adjacent 2D measurements
            if avgs == 0: #If getting the data for the first time, the average matrix does not exist still, so do not use it
                refl_mag_averaged = refl_mag
                refl_phase_averaged = refl_phase
            else:
                refl_mag_averaged = (refl_mag + refl_mag_averaged)/2.0
                refl_phase_averaged = (refl_phase + refl_phase_averaged)/2.0
            
        
    # save the data to the file
    #v1_real = v1_vec_for_graph[i]
    #data.add_data_point(v2 + ramp, np.linspace(v1_real,v1_real,num_ramps*num_points_vertical), refl_mag_averaged, refl_phase_averaged)
    #data.new_block()
    stop = time()

    #plot2d_mag.update()
    #plot3d_mag.update()
    #plot2d_phase.update()
    #plot3d_phase.update()
    # Saving the matrix to the matrix filedata.get_filepath
    np.savetxt(fname = data.get_dir() + '/' + file_name + "_amp_matrix.dat", X=refl_mag_averaged, fmt='%1.4e', delimiter=' ', newline='\n')  
    np.savetxt(fname = data.get_dir() + '/' + file_name + "_phase_matrix.dat", X=refl_phase_averaged, fmt='%1.4e', delimiter=' ', newline='\n')  
    
   
    print 'Overall duration: %s sec' % (stop - init_start, )

    #plot3d_mag.update()
    #plot3d_phase.update()

    #Saving plot images
    #plot3d_phase.save_png(filepath = data.get_dir())
    #plot3d_phase.save_eps(filepath = data.get_dir())
    #plot3d_mag.save_png(filepath = data.get_dir())
    #plot3d_mag.save_eps(filepath = data.get_dir())
    save_the_plot(to_plot = refl_mag_averaged, title = file_name + '_amplitude', x = v1_vec_for_graph, y = v2 + ramp, y_label = data.get_coordinates()[0]['name'], x_label = data.get_coordinates()[1]['name'], c_label = data.get_values()[0]['name'], dire = data.get_dir())
    save_the_plot(to_plot = refl_phase_averaged, title = file_name + '_phase', x = v1_vec_for_graph, y = v2 + ramp, y_label = data.get_coordinates()[0]['name'], x_label = data.get_coordinates()[1]['name'], c_label = data.get_values()[1]['name'], dire = data.get_dir())


    # after the measurement ends, you need to close the data files.
    data.close_file()


    settings_path = data.get_dir()

    UHFLI_lib.UHF_save_settings(daq, path = settings_path)

    #Turn OFF the AWG 
    AWG.stop()
    AWG.set_ch3_output(0)
    daq.setInt('/dev2169/sigouts/0/enables/3', 0) # Turn OFF the UHFLI out 1
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    #qt.mend()



#Vms = [100.0, 300.0, 500.0]
#
#
#for Vm in Vms:
do_meas_refl_whole(bias = 0.0, v2 = -643.0, v1_start = -395.0, v1_stop = -365.0, v1_step = 0.12, v_middle = 600.0, num_aver_pts = 20, ramp_amp = 5, averages = 8)

