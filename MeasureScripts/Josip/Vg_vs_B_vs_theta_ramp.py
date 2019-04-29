from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import numpy as np
from Background_correction import Back_corr as bc
from AWG_upload_ramp import upload_ramp_to_AWG as u2AWG
import UHFLI_lib
reload(UHFLI_lib)





"""Script for observing the evolution of the interdot line scan, measured in gate reflectometry 
   vs the magnitude and the angle of an applied magnetic field"""



#magnetZ = qt.instruments.create('magnetZ', 'AMI430_Bz', address='10.21.64.183')
#magnetY = qt.instruments.create('magnetY', 'AMI430_By', address='10.21.64.184')

ramp_amp = 1.0  # Amplitude of the ramp in mV
u2AWG(ramp_amp = ramp_amp) # Call the function to upload ramp with a given amplitude to the AWG

# Initialize the UHFLI scope module
daq, scopeModule = UHFLI_lib.UHF_init_scope_module()





def do_Vg_vs_B(Vg_ramped = None, Vg_static = None, num_aver_pts = None, daq = daq):

    if (Vg_ramped == None) or (Vg_static == None) or (num_aver_pts == None): 
        raise Exception('Define gate voltages and num_aver_pts first')

    global name_counter
    
    thetas = [0.0,90.0,180.0,270.0] # Angle between the By and Bx axis
    TC = 5e-6 # Time constant of the UHFLI in seconds

    scope_segment_length = daq.getDouble('/dev2169/scopes/0/length')
    scope_num_segments = daq.getDouble('/dev2169/scopes/0/segments/count')
    # Number of adjacent points to average in the read data
    num_aver_pts = num_aver_pts  
    Vg_ramped = Vg_ramped  # DC gate voltage point in mV - ramp is added on top of it
    Vg_static = Vg_static  # Other main gate voltage. The static one.
    divgate = 1.0










    num_points_vertical = scope_segment_length//num_aver_pts 
    ramp = np.linspace(-ramp_amp, ramp_amp, num_points_vertical)  # Defining the ramp segment

    # Set the ramping and the static gates
    IVVI.set_dac3(Vg_ramped*divgate)
    IVVI.set_dac4(Vg_static*divgate)


    #Run the AWG sequence - ramp
    AWG.run()
    #Turn ON necessary AWG channels
    AWG.set_ch1_output(1)
    
    init_start = time()
    vec_count = 0


    
    for z,theta in enumerate(thetas): 

        start = time()
        name_counter += 1
        file_name = '2_20 IV %d_theta=%d'%(name_counter,theta)
         
        
            
        Bmin = 0.0  # Min total field in T
        Bmax = 2.0 # Max total field in T   
        ramp_rate_Y = 0.0003 #T/s
        ramp_rate_Z = 0.0005 #T/s
        step_size_BY = -2e-3 
        step_size_BZ = -2e-3
        Bymin = Bmin*np.cos(np.deg2rad(theta))  # Min By field in T
        Bymax = Bmax*np.cos(np.deg2rad(theta))  # Max By field in T
        Bzmin = Bmin*np.sin(np.deg2rad(theta))  # Min Bz field in T
        Bzmax = Bmax*np.sin(np.deg2rad(theta))  # Max Bz field in T
        
        
        BY_vector = np.linspace(Bymin,Bymax,300) # Defining the By vector in T  
        magnetY.set_rampRate_T_s(ramp_rate_Y)

        BZ_vector = np.linspace(Bzmin,Bzmax,300) # Defining the Bz vector in T  
        magnetZ.set_rampRate_T_s(ramp_rate_Z)
        
    
        
        qt.mstart()
        
        
        data = qt.Data(name=file_name)
        
        #saving directly in matrix format for diamond program
        new_mat = np.zeros(num_points_vertical) # Empty vector for storing the data 
        data_temp = np.zeros(num_points_vertical)  # Temporary vector for storing the data
        
        
        data.add_coordinate('Vg 4 [mV]')  #v2
        data.add_coordinate('B [T]')   #v1
        data.add_value('Refl_phase [deg]')
        data.add_value('Refl_amplitude [arb.u.]')

        data.create_file()
        
        plot2d_phase = qt.Plot2D(data, name=file_name+' 2D',autoupdate=False)
        plot3d_phase = qt.Plot3D(data, name=file_name+' 3D_phase_%d'%theta, coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
        plot3d_amp = qt.Plot3D(data, name=file_name+' 3D_amplitude_%d'%theta, coorddims=(1,0), valdim=3, style='image')
        
        
        
        Vg_traces_counter = 0    # Counter of the frequency traces used for the remaining measurement time estimation

        try:
        
            for i,v1 in enumerate(BY_vector):  
                
                start_Vg_trace = time()  # Remebering the time when the ongoing freq trace started
                
                #magnetY.set_field(BY_vector[i])   # Set the By field first
                #while math.fabs(BY_vector[i] - magnetY.get_field_get()) > 0.0001:  # Wait until the By field is set
                    #qt.msleep(0.050)
                #magnetZ.set_field(BZ_vector[i])   # Set the Bz field second
                #while math.fabs(BZ_vector[i] - magnetZ.get_field_get()) > 0.0001:  # Wait until the Bz field is set
                    #qt.msleep(0.050)
                
                total_field = np.sqrt(BY_vector[i]**2+BZ_vector[i]**2)
                # After the field is at the set point, we need to check where is the resonant frequency and set it
                freq, R = UHFLI_lib.run_sweeper(oscilator_num = 0, demod = 3, start = 135e6, stop = 170e6, num_samples = 500, do_plot= False)

                ind_res = np.where(R == R.min())  # On resonance the amplitude has the minimum value -> getting the index of the resonant frequency
                f_res = freq[ind_res]
                f_res += 0e3 # The readout frequency offset from the resonance
    
                # Now set the readout frequency 
                daq.setDouble('/dev2169/oscs/0/freq', f_res[0])
                # Set the TC back to the previous one
                daq.setDouble('/dev2169/demods/3/timeconstant', TC)
        

                daq.setInt('/dev2169/sigins/0/autorange', 1)  # Autoset amplification
                qt.msleep(0.10)

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
                data.add_data_point(Vg_ramped + ramp, np.linspace(total_field,total_field, num_points_vertical),refl_phase, refl_mag)
    
                 
                    
                data.new_block()
                
                new_mat = np.column_stack((new_mat, refl_phase))
                if i == 0: #Kicking out the first column filled with zeros
                    new_mat = new_mat[:,1:]
                np.savetxt(fname = data.get_dir() + '/' + file_name + "_phase_matrix.dat", X = new_mat, fmt = '%1.4e', delimiter = '  ', newline = '\n')
                
                plot2d_phase.update()
                plot3d_phase.update()
                plot3d_amp.update()

                stop = time()
                print 'Estimated remaining time of the ongoing measurement: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start_Vg_trace)*(len(BY_vector) - Vg_traces_counter))))
                Vg_traces_counter += 1

            
    
        
        finally:
            stop = time()
            vec_count = vec_count + 1
            print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(len(thetas) - vec_count))))
            #Saving plot images
            plot3d_phase.save_png(filepath = data.get_dir())
            plot3d_phase.save_eps(filepath = data.get_dir())
            plot3d_amp.save_png(filepath = data.get_dir())
            plot3d_amp.save_eps(filepath = data.get_dir())
            # Substracting the background
            #bc(path = data.get_dir(), fname = data.get_filename()+"_matrix")
    	        
    	    # after the measurement ends, you need to close the data file.
            data.close_file()
    	    # lastly tell the secondary processes (if any) that they are allowed to start again.
            qt.mend()

    	    print 'Overall duration: %s sec' % (stop - init_start, )

        # Save the UHFLI settings
        settings_path = data.get_dir()
        UHFLI_lib.UHF_save_settings(daq, path = settings_path)
    
        #Turn OFF the AWG 
        AWG.stop()
        AWG.set_ch1_output(0)

# Do measurement
do_Vg_vs_B(Vg_ramped = -550.048, Vg_static = -650.126, num_aver_pts = 40)

