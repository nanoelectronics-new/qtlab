from numpy import pi, random, arange, size, linspace
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import UHFLI_lib
reload(UHFLI_lib)




# Initialize the UHFLI scope module
daq, scopeModule = UHFLI_lib.UHF_init_scope_module()





def do_meas_refl(bias = None, v2 = None, v1_start = None, v1_stop = None, v_middle = None, num_aver_pts = 20):

    if (bias == None) or (v2 == None) or (v1_start == None) or (v1_stop == None) or (v_middle == None): 
        raise Exception('Define the values first: bias, v2...')

    global name_counter
    name_counter += 1

    file_name = '2-20 IV %d GvsG_V_middle=%.2fmV_'%(name_counter, v_middle)
    file_name = 'test'

    
    gate1div = 1.0
    gate2div = 1.0
    v_middle_factor = 1.0 
    
    bias = bias
    
    ramp_start = -71.0  # Starting value of the ramp in mV
    ramp_stop = 71.0    # Ending value of the ramp in mV


    v1_vec = arange(v1_start,v1_stop,-0.06)      #outer
    v2 = v2       #inner - the middle DC point of the ramp
 

    scope_segment_length = daq.getDouble('/dev2169/scopes/0/length')
    scope_num_segments = daq.getDouble('/dev2169/scopes/0/segments/count')

    # Number of adjacent points to average in the read data
    num_aver_pts = num_aver_pts 

    num_points_vertical = scope_segment_length//num_aver_pts 
    ramp = np.linspace(ramp_start, ramp_stop, num_points_vertical)  # Defining the ramp segment
    
    qt.mstart()
    
    # Set the bias and static gates
    #IVVI.set_dac1(bias)
    #IVVI.set_dac6(v_middle/v_middle_factor)  
    #IVVI.set_dac3(v2*gate2div)

    #Run the AWG sequence - ramp
    AWG.run()
    #Turn ON necessary AWG channels
    AWG.set_ch1_output(1)
    
    
    # Create data files
    data = qt.Data(name=file_name)

    
    
    data.add_coordinate('V_G 4 [mV]')       # inner
    data.add_coordinate('V_G 17 [mV]')      # outer
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
    
    for i,v1 in enumerate(v1_vec):
        
    
        # set the voltage
    
        #IVVI.set_dac4(v1*gate1div)


        



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
        data.add_data_point(v2 + ramp, np.linspace(v1,v1, num_points_vertical), refl_mag, refl_phase)


        data.new_block()
        stop = time()

        new_mat_mag = np.column_stack((new_mat_mag, refl_mag))
        new_mat_phase = np.column_stack((new_mat_phase, refl_phase))

        # Kicking out the first column with zeros
        if not(i):
            new_mat_mag = new_mat_mag[:,1:]
            new_mat_phase = new_mat_phase[:,1:]


        #plot2d_mag.update()
        plot3d_mag.update()
        #plot2d_phase.update()
        plot3d_phase.update()

        # Saving the matrix to the matrix filedata.get_filepath
        np.savetxt(fname = data.get_dir() + '/' + file_name + "_amp_matrix.dat", X=new_mat_mag, fmt='%1.4e', delimiter=' ', newline='\n')  
        np.savetxt(fname = data.get_dir() + '/' + file_name + "_phase_matrix.dat", X=new_mat_phase, fmt='%1.4e', delimiter=' ', newline='\n')  


    print 'Overall duration: %s sec' % (stop - init_start, )



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
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()






# Run the measurement
#v_middle_sweep = np.arange(10.0,25.0,5.0)

#for ve in v_middle_sweep: 
do_meas_refl(bias = 0.0, v2 = -500.0,  v1_start = -545.5, v1_stop = -548.0, v_middle = 20.0, num_aver_pts = 20)

