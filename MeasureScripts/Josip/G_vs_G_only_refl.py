from numpy import pi, random, arange, size, linspace
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import UHFLI_lib
reload(UHFLI_lib)





daq = UHFLI_lib.UHF_init_demod_multiple(device_id = 'dev2169', demod_c = [3])

#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54502777::INSTR')




def do_meas_refl(bias = 0.0, fmw = None, v2_start = 200, v2_stop = 300, v1_start = None, v1_stop = None,v_middle = 0.0):

    def V_G1(V_G2):
        '''In order to record paralelogram instead of the rectangle, in the gate space,
           a functional dependance of y-axis gate vales is needed. This function returns the 
           y-axis values for given x-axis value''' 
        return 1.344*V_G2 - 0.791


    global name_counter
    name_counter += 1

    file_name = '2-20 IV %d GvsG_V_middle=%.2fmV_'%(name_counter, v_middle)

    
    gate1div = 1.0
    gate2div = 1.0
    v_middle_factor = 1.0 
    
    bias = bias
    

    v1_vec = arange(v1_start,v1_stop,-0.06)      #outer
    v2_vec = arange(v2_start,v2_stop,-0.06)       #inner

    #v2_vec = arange(V_G1(v1_vec[0]),V_G1(v1_vec[0])+2.0,0.05) # only to get the v2_vec length




    
    qt.mstart()
    
    IVVI.set_dac1(bias)
    IVVI.set_dac6(v_middle/v_middle_factor)  
    
    
    
    data_mag = qt.Data(name=file_name + 'refl_mag')
    data_phase = qt.Data(name=file_name + 'refl_phase')
    
    
    
    
    

    data_mag.add_coordinate('V_G 17 [mV]')       # inner
    data_mag.add_coordinate('V_G 4 [mV]')      # outer
    data_mag.add_value('Refl_mag [V]')
    
    data_phase.add_coordinate('V_G 17 [mV]')
    data_phase.add_coordinate('V_G 4 [mV]')
    data_phase.add_value('Refl_phase [deg]')
    
    
    
    
    
    
    data_mag.create_file()
    data_phase.create_file()
    
    
    #saving directly in matrix format 
    new_mat_mag = np.zeros((len(v2_vec))) # Creating empty matrix for storing all data 
    temp_mag = np.zeros((len(v2_vec)))
    new_mat_phase = np.zeros((len(v2_vec))) # Creating empty matrix for storing all data 
    temp_phase = np.zeros((len(v2_vec))) 
    
    
    
    plot3d_mag = qt.Plot3D(data_mag, name=file_name + "_2D_amplitude", coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
    #plot2d_mag = qt.Plot2D(data_mag, name=file_name + "_1D_amplitude",autoupdate=False)
    plot3d_phase = qt.Plot3D(data_phase, name=file_name + "_2D_phase", coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
    #plot2d_phase = qt.Plot2D(data_phase, name=file_name + "_1D_phase",autoupdate=False)
    
    
    
    # preparation is done, now start the measurement.
    
   
    init_start = time()
    vec_count = 0
    
     
    
   
    daq.setInt('/dev2169/sigins/0/autorange', 1)  # Autoset amplification
    
    for i,v1 in enumerate(v1_vec):
        #v2_vec = arange(V_G1(v1),V_G1(v1)+2.0,0.05)      #Inner, scanning only a diagonal stripe 2 mV in width
        
        
        start = time()
        # set the voltage
    
        IVVI.set_dac3(v1*gate1div)


        

        for j,v2 in enumerate(v2_vec):

            IVVI.set_dac4(v2*gate2div)
            

            # readout

            result_refl = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 2, Integration_time = 0.002)  # Reading the lockin
            result_refl = array(result_refl)
            result_phase = result_refl[0,1]  # Getting phase values 
            result_mag = result_refl[0,0] # Getting amplitude values 
        
            # save the data point to the file, this will automatically trigger
            # the plot windows to update
            data_mag.add_data_point(v2,v1, result_mag)
            data_phase.add_data_point(v2,v1, result_phase)

            # Save to the matrix
            temp_mag[j] = result_mag 
            temp_phase[j] = result_phase 

            # the next function is necessary to keep the gui responsive. It
            # checks for instance if the 'stop' button is pushed. It also checks
            # if the plots need updating.
            qt.msleep(0.003)
        data_mag.new_block()
        data_phase.new_block()
        stop = time()

        new_mat_mag = np.column_stack((new_mat_mag, temp_mag))
        new_mat_phase = np.column_stack((new_mat_phase, temp_phase))

        if not(i):
            new_mat_mag = new_mat_mag[:,1:]
            new_mat_phase = new_mat_phase[:,1:]


        #plot2d_mag.update()
        plot3d_mag.update()
        #plot2d_phase.update()
        plot3d_phase.update()

        # Saving the matrix to the matrix filedata.get_filepath
        np.savetxt(fname=data_mag.get_filepath() + "_matrix", X=new_mat_mag, fmt='%1.4e', delimiter=' ', newline='\n')  
        np.savetxt(fname=data_phase.get_filepath() + "_matrix", X=new_mat_phase, fmt='%1.4e', delimiter=' ', newline='\n')  

        vec_count = vec_count + 1
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(v1_vec.size - vec_count))))

    print 'Overall duration: %s sec' % (stop - init_start, )



    #Saving plot images
    plot3d_phase.save_png(filepath = data_phase.get_dir())
    plot3d_phase.save_eps(filepath = data_phase.get_dir())

    plot3d_mag.save_png(filepath = data_mag.get_dir())
    plot3d_mag.save_eps(filepath = data_mag.get_dir())

    # after the measurement ends, you need to close the data files.
    data_mag.close_file()
    data_phase.close_file()

    settings_path = data_mag.get_dir()

    UHFLI_lib.UHF_save_settings(daq, path = settings_path)
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()






# Run the measurement
#v_middle_sweep = np.arange(10.0,25.0,5.0)

#for ve in v_middle_sweep: 
do_meas_refl(bias = 0.0, v1_start = -545.5, v1_stop = -548.0, v2_start = -642.0, v2_stop = -650.0, v_middle = 20.0)
# Do measurement for different biases:
#biases = np.linspace(-300,300,13) # Bias voltages in mV *10

#for Vsd in biases:
    #do_meas_refl(bias = Vsd)

# Turn the RF on
#VSG.set_status("on") 

#power = -35 # dBm
#freq_vec = np.arange(1.5e9,6.5e9,100e6) # in Hz
#temp_freq = freq_vec[0]

#for j,freq in enumerate(freq_vec): 
    # Set frequency
    #VSG.set_frequency(freq)

    #if freq >= (temp_freq + 1e9):
        #temp_freq = freq
        #power = power + 1
        # Set the VSG power units
        #VSG.set_power_units("dbm") 
        # Set the RF power
        #VSG.set_power(power)



    # Do measurement
    #do_meas_refl(fmw = freq)


# Turn the RF on
#VSG.set_status("off") 
