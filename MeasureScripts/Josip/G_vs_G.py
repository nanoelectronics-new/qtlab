from numpy import pi, random, arange, size, linspace
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import UHFLI_lib





    

#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54502777::INSTR')

name_counter +=1

def do_meas_current(bias = 500.0, v2start = 100, v2stop = 100):

    file_name = '2-20_GvsG_%d'%name_counter
    
    gain = 1e8 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    
    
    bias = bias
    
    gatediv = 1.0
    
    
    v1_vec = arange(0.0,-1000.0,-1.0)      #outer
    v2_vec = arange(v2start,v2stop,-1.0)       #inner
    
    
    qt.mstart()
    
    
    
    data = qt.Data(name=file_name)
    
    
    
    
    ##CURRENT
    data.add_coordinate('V_G 17 [mV]')    # inner
    data.add_coordinate('V_G 4 [mV]')      #  outer
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
       
            IVVI.set_dac3(v1*gatediv)
    
    
            
    
            for j,v2 in enumerate(v2_vec):
    
                IVVI.set_dac4(v2*gatediv)
                
    
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
                qt.msleep(0.001)
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


#for bias in [-1000,-500]:
    #do_meas_current(bias)

#Do measurement
do_meas_current(v2start = -600, v2stop = -700)
do_meas_current(v2start = -700, v2stop = -800)