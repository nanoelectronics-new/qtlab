from numpy import pi, random, arange, size, linspace
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import UHFLI_lib





daq = UHFLI_lib.UHF_init_demod_multiple(device_id = 'dev2169', demod_c = [3])

    

#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54502777::INSTR')


def do_meas_both():
    file_name = 'GvsG_8-10_G9&12_'
    
    gain = 1e8 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    
    bias = 0.0
    
   
    gatediv = 100
    
    
    
    v1_vec = arange(-2.2,3.0,0.05)      #outer
    v2_vec = arange(-2.6,4.0,0.05)      #inner
    
    
    
    qt.mstart()
    
    
    
    data = qt.Data(name=file_name + 'current')
    data_mag = qt.Data(name=file_name + 'refl_mag')
    data_phase = qt.Data(name=file_name + 'refl_phase')
    
    
    
    ##CURRENT
    data.add_coordinate('V_G 12 [mV]')   # inner
    data.add_coordinate('V_G 9 [mV]')  #  outer
    data.add_value('Current [pA]')
    
    ##REFL f1
    data_mag.add_coordinate('V_G 12 [mV]')
    data_mag.add_coordinate('V_G 9 [mV]')
    data_mag.add_value('Refl_mag [V]')
    
    data_phase.add_coordinate('V_G 12 [mV]')
    data_phase.add_coordinate('V_G 9 [mV]')
    data_phase.add_value('Refl_phase [deg]')
    
    
    
    
    
    data.create_file()
    data_mag.create_file()
    data_phase.create_file()
    
    
    #saving directly in matrix format 
    new_mat_cur = np.zeros((len(v2_vec))) # Creating empty matrix for storing all data
    temp_cur = np.zeros((len(v2_vec))) 
    new_mat_mag = np.zeros((len(v2_vec))) # Creating empty matrix for storing all data 
    temp_mag = np.zeros((len(v2_vec)))
    new_mat_phase = np.zeros((len(v2_vec))) # Creating empty matrix for storing all data 
    temp_phase = np.zeros((len(v2_vec))) 
    
    
    
    plot3d = qt.Plot3D(data, name='measure3D_current', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
    plot2d = qt.Plot2D(data, name='measure2D_current',autoupdate=False)
    plot3d_mag = qt.Plot3D(data_mag, name='measure3D_magnitude', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
    plot2d_mag = qt.Plot2D(data_mag, name='measure2D_magnitude',autoupdate=False)
    plot3d_phase = qt.Plot3D(data_phase, name='measure3D_phase', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
    plot2d_phase = qt.Plot2D(data_phase, name='measure2D_phase',autoupdate=False)
    
    
    
    # preparation is done, now start the measurement
    
    IVVI.set_dac1(bias)  
    
    init_start = time()
    vec_count = 0
    
     
    
    try:
        daq.setInt('/dev2169/sigins/0/autorange', 1)  # Autoset amplification
        
        for i,v1 in enumerate(v1_vec):
            
            
            start = time()
            # set the voltage
       
            IVVI.set_dac2(v1*gatediv)
    
    
            
    
            for j,v2 in enumerate(v2_vec):
    
                IVVI.set_dac3(v2*gatediv)
                
    
                # readout
                result = dmm.get_readval()/gain*1e12
                result_refl = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 1)  # Reading the lockin
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
    
    
            plot2d.update()
            plot3d.update()
            plot2d_mag.update()
            plot3d_mag.update()
            plot2d_phase.update()
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
        plot3d_phase.save_png(filepath = data_phase.get_dir())
        plot3d_phase.save_eps(filepath = data_phase.get_dir())
    
        plot3d_mag.save_png(filepath = data_mag.get_dir())
        plot3d_mag.save_eps(filepath = data_mag.get_dir())
    
        plot3d.save_png(filepath = data.get_dir())
        plot3d.save_eps(filepath = data.get_dir())
        # after the measurement ends, you need to close the data files.
        data.close_file()
        data_mag.close_file()
        data_phase.close_file()
    
        settings_path = data_mag.get_dir()
    
        UHFLI_lib.UHF_save_settings(daq, path = settings_path)
        # lastly tell the secondary processes (if any) that they are allowed to start again.
        qt.mend()   