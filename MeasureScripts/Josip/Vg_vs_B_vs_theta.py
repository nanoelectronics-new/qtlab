from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import numpy as np
from Background_correction import Back_corr as bc
import UHFLI_lib
reload(UHFLI_lib)





"""Script for observing the evolution of the interdot line scan, measured in gate reflectometry phase, vs the magnitude and the angle of an applied magnetic field"""



#magnetZ = qt.instruments.create('magnetZ', 'AMI430_Bz', address='10.21.64.183')
#magnetY = qt.instruments.create('magnetY', 'AMI430_By', address='10.21.64.184')
daq = UHFLI_lib.UHF_init_demod_multiple(device_id = 'dev2169', demod_c = [3])




def do_Vg_vs_B():

    global name_counter
    
    thetas = [90,360.0] # Angle between the By and Bx axis
    
    TC = 10e-3 # Time constant of the UHFLI in seconds
    
    init_start = time()
    vec_count = 0
    
    for z,theta in enumerate(thetas): 

        start = time()
        name_counter += 1
        file_name = '1-3 IV %d_theta=%d'%(name_counter,theta)
         
        
            
            
        ramp_rate_Y = 0.0003 #T/s
        ramp_rate_Z = 0.0005 #T/s
        step_size_BY = -2e-3 
        step_size_BZ = -2e-3

        Bmin = 0.0  # Min total field in T
        Bmax = 2.0 # Max total field in T
        Bymin = Bmin*np.cos(np.deg2rad(theta))  # Min By field in T
        Bymax = Bmax*np.cos(np.deg2rad(theta))  # Max By field in T
        Bzmin = Bmin*np.sin(np.deg2rad(theta))  # Min Bz field in T
        Bzmax = Bmax*np.sin(np.deg2rad(theta))  # Max Bz field in T
        
        
        BY_vector = np.linspace(Bymin,Bymax,300) # Defining the By vector in T  
        magnetY.set_rampRate_T_s(ramp_rate_Y)

        BZ_vector = np.linspace(Bzmin,Bzmax,300) # Defining the Bz vector in T  
        magnetZ.set_rampRate_T_s(ramp_rate_Z)
        
        
        Vg = arange(-486.0,-483.5,0.06)  # gate voltage
        divgate = 1.0
        
        qt.mstart()
        
        
        data = qt.Data(name=file_name)
        
        #saving directly in matrix format for diamond program
        new_mat = np.zeros(len(Vg)) # Empty vector for storing the data 
        data_temp = np.zeros(len(Vg))  # Temporary vector for storing the data
        
        
        data.add_coordinate('Vg 24 [mV]')  #v2
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
                
                magnetY.set_field(BY_vector[i])   # Set the By field first
                while math.fabs(BY_vector[i] - magnetY.get_field_get()) > 0.0001:  # Wait until the By field is set
                    qt.msleep(0.050)
                magnetZ.set_field(BZ_vector[i])   # Set the Bz field second
                while math.fabs(BZ_vector[i] - magnetZ.get_field_get()) > 0.0001:  # Wait until the Bz field is set
                    qt.msleep(0.050)
                
                total_field = np.sqrt(BY_vector[i]**2+BZ_vector[i]**2)
                # After the field is at the set point, we need to check where is the resonant freuqency and set it
                if i==0: # If determining the resonant freq for the first time    
                    # Then scan a bigger area and find the resonant frequency roughly
                    freq, R = UHFLI_lib.run_sweeper(oscilator_num = 0, demod = 3, start = 205e6, stop = 230e6, num_samples = 500, do_plot= False)
                    ind_res = np.where(R == R.min())  # On resonance the amplitude has the minimum value -> getting the index of the resonant frequency
                    f_res = freq[ind_res][0]

                # Finding the resonant frequency with a better resolution
                freq, R = UHFLI_lib.run_sweeper(oscilator_num = 0, demod = 3, start = (f_res-2e6), stop = (f_res+2e6), num_samples = 500, do_plot= False)

                ind_res = np.where(R == R.min())  # On resonance the amplitude has the minimum value -> getting the index of the resonant frequency
                f_res = freq[ind_res]
                f_res -= 500e3 # The readout frequency offset from the resonance
    
                # Now set the readout frequency 
                daq.setDouble('/dev2169/oscs/0/freq', f_res[0])
                # Set the TC back to the previous one
                daq.setDouble('/dev2169/demods/3/timeconstant', TC)
                # Enable data readout
                daq.setInt('/dev2169/demods/3/enable', 1)
        
                daq.setInt('/dev2169/sigins/0/autorange', 1)  # Autoset amplification
                qt.msleep(0.10)
        
                for j,Vg_val in enumerate(Vg):  
                    IVVI.set_dac6(Vg_val*divgate)
                    
        
                    # the next function is necessary to keep the gui responsive. It
                    # checks for instance if the 'stop' button is pushed. It also checks
                    # if the plots need updating.
                    qt.msleep(0.010)
        
                    # readout
                    result_refl = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 1)  # Reading the lockin
                    result_refl = array(result_refl)
                    result_phase = result_refl[0,1]  # Getting phase values 
                    result_amp = result_refl[0,0] # Getting amplitude values 
                    
                    data_temp[j] = result_phase
                    # save the data point to the file, this will automatically trigger
                    # the plot windows to update
                    data.add_data_point(Vg_val,total_field,result_phase, result_amp)  
                
                    
        
                 
                    
                data.new_block()
                
                new_mat = np.column_stack((new_mat, data_temp))
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
    


#Do measurement
do_Vg_vs_B()