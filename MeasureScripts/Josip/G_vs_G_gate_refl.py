from numpy import pi, random, arange, size, linspace
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import UHFLI_lib
reload(UHFLI_lib)
execfile('C:/QTLab/qtlab/MeasureScripts/Josip/save_the_plot.py') # Same as import save the plot function




daq = UHFLI_lib.UHF_init_demod_multiple(device_id = 'dev2169', demod_c = [3])

    
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54502777::INSTR')




def do_meas_both(bias = 1000.0, v2_start = 200, v2_stop = 300, v1_start = None, v1_stop = None, static_gate1 = 0.0, static_gate2 = 0.0, v_middle = 0.0, v_middle_init = 0.0):

    global name_counter 
    name_counter += 1
    file_name = '3-5 IV %d GvsG_V_middle=%.2fmV_bias=%.2fmV'%(name_counter, v_middle, (bias/100.0))
    
    gain = 1e9 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    
    bias = bias
    
    # These are the values of the voltages which are superimposed to gates via S3b cards
    static_gate1 = static_gate1
    static_gate2 = static_gate2

    gatediv = 1.0
    v_middle_factor = 5.0 
    
    #mg_horizontal_shift = -0.093
    #mg_vertical_shift = -0.074

    

    v1_vec = arange(v1_start, v1_stop,0.06)       #outer
    v2_vec = arange(v2_start,v2_stop,0.06)        #inner

    # Substracting the value of the static gate voltages to get the voltages to be swept through
    #v1_vec = v1_vec - static_gate1
    #v2_vec = v2_vec - static_gate2

    #v1_vec = v1_vec + mg_horizontal_shift*(v_middle - v_middle_init)
    #v2_vec = v2_vec + mg_vertical_shift*(v_middle - v_middle_init)
    
    
    qt.mstart()
    
    
    
    data = qt.Data(name=file_name + 'current')
    data_mag = qt.Data(name=file_name + 'refl_mag')
    data_phase = qt.Data(name=file_name + 'refl_phase')
    
    
    
    ##CURRENT
    data.add_coordinate('V_G 9 [mV]')   # inner
    data.add_coordinate('V_G 6 [mV]')  #  outer
    data.add_value('Current [pA]')
    
    ##REFL f1
    data_mag.add_coordinate('V_G 9 [mV]')
    data_mag.add_coordinate('V_G 6 [mV]')
    data_mag.add_value('Refl_mag [V]')
    
    data_phase.add_coordinate('V_G 9 [mV]')
    data_phase.add_coordinate('V_G 6 [mV]')
    data_phase.add_value('Refl_phase [deg]')
    
    
    
    
    
    data.create_file()
    data_mag.create_file()
    data_phase.create_file()
    
    
    #Saving directly in the matrix format 
    new_mat_cur = np.zeros((len(v2_vec))) # Creating empty matrix for storing all data
    temp_cur = np.zeros((len(v2_vec))) 
    new_mat_mag = np.zeros((len(v2_vec))) # Creating empty matrix for storing all data 
    temp_mag = np.zeros((len(v2_vec)))
    new_mat_phase = np.zeros((len(v2_vec))) # Creating empty matrix for storing all data 
    temp_phase = np.zeros((len(v2_vec))) 
    
    
    
    plot3d = qt.Plot3D(data, name=file_name + "_current", coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
    #plot2d = qt.Plot2D(data, name='measure2D_current',autoupdate=False)
    plot3d_mag = qt.Plot3D(data_mag, name=file_name + "_amp", coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
    #plot2d_mag = qt.Plot2D(data_mag, name='measure2D_magnitude',autoupdate=False)
    plot3d_phase = qt.Plot3D(data_phase, name=file_name + "_phase", coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
    #plot2d_phase = qt.Plot2D(data_phase, name='measure2D_phase',autoupdate=False)
    
    
    
    # preparation is done, now start the measurement
    # Set bias
    IVVI.set_dac3(bias)  

    # Set gates
    IVVI.set_dac5(v_middle/v_middle_factor)
    #IVVI.set_dac5(static_gate1)
    #IVVI.set_dac6(static_gate2)

    init_start = time()
    vec_count = 0
    
     
    
    
    #daq.setInt('/dev2169/sigins/0/autorange', 1)  # Autoset amplification
    try:
        for i,v1 in enumerate(v1_vec):
            
            
            start = time()
            # set the voltage
        
            IVVI.set_dac1(v1*gatediv)
    
    
            
    
            for j,v2 in enumerate(v2_vec):
    
                IVVI.set_dac2(v2*gatediv)
                
    
                # readout
                result = dmm.get_readval()/gain*1e12
                result_refl = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 0.5, Integration_time = 0.005)  # Reading the lockin
                result_refl = array(result_refl)
                result_phase = result_refl[0,1]  # Getting phase values 
                result_mag = result_refl[0,0] # Getting amplitude values 
            
                # save the data point to the file, this will automatically trigger
                # the plot windows to update
                data.add_data_point(v2,v1, result)  
                data_mag.add_data_point(v2,v1, result_mag)
                data_phase.add_data_point(v2,v1, result_phase)
    
                # Save to the matrix
                temp_cur[j] = result
                temp_mag[j] = result_mag 
                temp_phase[j] = result_phase 
    
                # the next function is necessary to keep the gui responsive. It
                # checks for instance if the 'stop' button is pushed. It also checks
                # if the plots need updating.
                qt.msleep(0.003)
            data.new_block()
            data_mag.new_block()
            data_phase.new_block()
            stop = time()
    
            new_mat_cur = np.column_stack((new_mat_cur, temp_cur))
            new_mat_mag = np.column_stack((new_mat_mag, temp_mag))
            new_mat_phase = np.column_stack((new_mat_phase, temp_phase))
    
            if not(i):
                new_mat_cur = new_mat_cur[:,1:]
                new_mat_mag = new_mat_mag[:,1:]
                new_mat_phase = new_mat_phase[:,1:]
    
    
            #plot2d.update()
            plot3d.update()
            #plot2d_mag.update()
            plot3d_mag.update()
            #plot2d_phase.update()
            plot3d_phase.update()
    
            # Saving the matrix to the matrix filedata.get_filepath
            np.savetxt(fname=data.get_filepath() + "_matrix", X=new_mat_cur, fmt='%1.4e', delimiter=' ', newline='\n')  
            np.savetxt(fname=data_mag.get_filepath() + "_matrix", X=new_mat_mag, fmt='%1.4e', delimiter=' ', newline='\n')  
            np.savetxt(fname=data_phase.get_filepath() + "_matrix", X=new_mat_phase, fmt='%1.4e', delimiter=' ', newline='\n')  
    
            vec_count = vec_count + 1
            print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(v1_vec.size - vec_count))))
    
        print 'Overall duration: %s sec' % (stop - init_start, )
    

    
    finally:
        #Saving plot images
        
        #plot3d_phase.save_png(filepath = data_phase.get_dir())
        #plot3d_phase.save_eps(filepath = data_phase.get_dir())
        save_the_plot(to_plot = new_mat_mag, title = file_name + '_amplitude', x = v1_vec, y = v2_vec, y_label = data_mag.get_coordinates()[0]['name'], x_label = data_mag.get_coordinates()[1]['name'], c_label = data_mag.get_values()[0]['name'], dire = data_mag.get_dir())
        #plot3d_mag.save_png(filepath = data_mag.get_dir())
        #plot3d_mag.save_eps(filepath = data_mag.get_dir())

        save_the_plot(to_plot = new_mat_phase, title = file_name + '_phase', x = v1_vec, y = v2_vec, y_label = data_phase.get_coordinates()[0]['name'], x_label = data_phase.get_coordinates()[1]['name'], c_label = data_phase.get_values()[0]['name'], dire = data_phase.get_dir())
        #plot3d.save_png(filepath = data.get_dir())
        #plot3d.save_eps(filepath = data.get_dir())
        save_the_plot(to_plot = new_mat_cur, title = file_name + '_current', x = v1_vec, y = v2_vec, y_label = data.get_coordinates()[0]['name'], x_label = data.get_coordinates()[1]['name'], c_label = data.get_values()[0]['name'], dire = data.get_dir())
        # after the measurement ends, you need to close the data files.
        data.close_file()
        data_mag.close_file()
        data_phase.close_file()
    
        settings_path = data_mag.get_dir()
    
        #UHFLI_lib.UHF_save_settings(daq, path = settings_path)
        # lastly tell the secondary processes (if any) that they are allowed to start again.
        qt.mend()   




#g6_vs_m = 0.065
#g9_vs_m = 0.14
#initial_Vm = 3000.0
#
#Vms = np.arange(3000.0,2800.0,-20.0)
#



#for Vm in Vms:
    #g6_shift = (Vm - initial_Vm)*g6_vs_m
    #g9_shift = (Vm - initial_Vm)*g9_vs_m
do_meas_both(bias = 0.0,  v1_start = -416.0, v1_stop = -412.5, v2_start = -385.0, v2_stop = -381.0, v_middle = 2820.0)


 
