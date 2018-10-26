from numpy import pi, random, arange, size, linspace
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import UHFLI_lib





    

#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54502777::INSTR')


def do_meas_current():
    file_name = 'G_vs_G_1-3_G2&24'
    
    gain = 1e8 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    
    
    bias = 100.0
    
    
    gate2div = 100.0
    gate24div = 10.0
    
    
    v1_vec = arange(80.0,100.0,0.05)      #outer
    v2_vec = arange(0.0,7.0,0.05)      #inner
    
    
    
    qt.mstart()
    
    
    
    data = qt.Data(name=file_name)
    
    
    
    
    ##CURRENT
    data.add_coordinate('V_G 2 [mV]')
    data.add_coordinate('V_G 24 [mV]')
    data.add_value('Current [pA]')
    
    
    
    
    
    
    data.create_file()
    
    
    #saving directly in matrix format 
    new_mat_cur = np.zeros((len(v2_vec))) # Creating empty matrix for storing all data
    temp_cur = np.zeros((len(v2_vec))) 
    
    
    
    plot3d = qt.Plot3D(data, name='measure3D_current', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
    plot2d = qt.Plot2D(data, name='measure2D_current',autoupdate=False)
    
    
    
    
    # preparation is done, now start the measurement.
    
    IVVI.set_dac1(bias)  
    
    init_start = time()
    vec_count = 0
    
     
    
    try:
        
        for i,v1 in enumerate(v1_vec):
            
            
            start = time()
            # set the voltage
       
            IVVI.set_dac4(v1*gate24div)
    
    
            
    
            for j,v2 in enumerate(v2_vec):
    
                IVVI.set_dac2(v2*gate2div)
                
    
                # readout
                result = dmm.get_readval()/gain*1e12
    
            
                # save the data point to the file, this will automatically trigger
                # the plot windows to update
                data.add_data_point(v2,v1, result)  
    
                # Save to the matrix
                temp_cur[j] = result
    
    
                # the next function is necessary to keep the gui responsive. It
                # checks for instance if the 'stop' button is pushed. It also checks
                # if the plots need updating.
                qt.msleep(0.003)
            data.new_block()
    
            stop = time()
    
            new_mat_cur = np.column_stack((new_mat_cur, temp_cur))
    
    
            if not(i):
                new_mat_cur = new_mat_cur[:,1:]
    
    
            plot2d.update()
            plot3d.update()
    
            # Saving the matrix to the matrix filedata.get_filepath
            np.savetxt(fname=data.get_filepath() + "_matrix", X=new_mat_cur, fmt='%1.4e', delimiter=' ', newline='\n')  
    
    
            vec_count = vec_count + 1
            print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(v1_vec.size - vec_count))))
    
        print 'Overall duration: %s sec' % (stop - init_start, )
    
    finally:

        #Saving plot images
        plot3d.save_png(filepath = data.get_dir())
        plot3d.save_eps(filepath = data.get_dir())
    
        # after the measurement ends, you need to close the data files.
        data.close_file()
    
        # lastly tell the secondary processes (if any) that they are allowed to start again.
        qt.mend()