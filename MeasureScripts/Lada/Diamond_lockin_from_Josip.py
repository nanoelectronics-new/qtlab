from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import UHFLI_lib
reload(UHFLI_lib)
#####################################################
# added automatic conversion to matrix file
#####################################################




#####################################################
# here is where the actual measurement program starts
#####################################################
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM1', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54505188::INSTR')

#magnetZ = qt.instruments.create('magnetZ', 'AMI430_Bz', address='10.21.64.109')
#magnetY = qt.instruments.create('magnetY', 'AMI430_By', address='10.21.64.175')

UHFLI_lib.UHF_init_demod(device_id = 'dev2169', demod_c = 3)  # Initialize UHF LI

gain = 100e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

v1_vec = arange(-650.0,-400.0,1.0)  #V_g 
v2_vec = arange(-500.0,505.0,5.0)  #V_sd

div_factor = 100.0

#bias =0






qt.mstart()


data_refl = qt.Data(name=' Diamond lockin 13-14') #just renamed

data_dc = qt.Data(name=' Diamond current 13-14') #added to have current recored as well

data_path_refl = data_refl.get_dir()
data_path_dc = data_dc.get_dir()

#saving directly in matrix format for diamond program
data_temp_r = np.zeros((len(v2_vec)))
new_mat_r = np.zeros((len(v2_vec))) 
data_temp_dc = np.zeros((len(v2_vec)))
new_mat_dc = np.zeros((len(v2_vec))) 



data_dc.add_coordinate('V{SD} [mV]')
data_dc.add_coordinate('V_G [mT]')
data_dc.add_value('Current [pA]')


data_refl.add_coordinate('V{SD} [mV]')
data_refl.add_coordinate('V_G [mT]')
data_refl.add_value('Lockin out [pA]')




data_dc.create_file()
data_refl.create_file()



plot2d_refl = qt.Plot2D(data_refl, name='lockin_2D 6',autoupdate=False)
plot3d_refl = qt.Plot3D(data_refl, name='lockin_3D 6', coorddims=(1,0), valdim=2, style='image')

plot2d_dc = qt.Plot2D(data_dc, name='Current_2D 6',autoupdate=False)
plot3d_dc = qt.Plot3D(data_dc, name='Current_3D 6', coorddims=(1,0), valdim=2, style='image')




init_start = time()
vec_count = 0


try:
    for i,v1 in enumerate(v1_vec):  # CHANGE THIS LINE FOR MATRIX FILE SAVING
        
        
        start = time()


        IVVI.set_dac4(v1)




        for j,v2 in enumerate(v2_vec):  # CHANGE THIS LINE FOR MATRIX FILE SAVING

            IVVI.set_dac2(v2)

            # readout
            result_reflectometry = UHFLI_lib.UHF_measure_demod(Num_of_TC = 3)/gain*1e12  # Reading the lockin and correcting for M1b gain

            data_temp_r[j] = result_reflectometry

            
            result_dc = dmm.get_readval()/gain*1e12

            data_temp_dc[j] = result_dc #for saving as matrix

            data_refl.add_data_point(v2/div_factor, v1, result_reflectometry) 
            data_dc.add_data_point(v2/div_factor, v1, result_dc) 
            
            qt.msleep(0.001)
        data_refl.new_block()
        data_dc.new_block()

        stop = time()
       
        new_mat_r = np.column_stack((new_mat_r, data_temp_r))
        new_mat_dc = np.column_stack((new_mat_dc, data_temp_dc))
        if not(i): # Kicking out the first column filled with zeros
            new_mat_r = new_mat_r[:,1:]
            new_mat_dc = new_mat_dc[:,1:]

        

        plot2d_refl.update()
        plot3d_refl.update() 

        plot2d_dc.update()
        plot3d_dc.update() 

        # Saving the matrix to the matrix filedata.get_filepath
        np.savetxt(fname=data_refl.get_filepath() + "_matrix", X=new_mat_r, fmt='%1.4e', delimiter=' ', newline='\n')   # ADD THIS LINE FOR MATRIX FILE SAVING
    
        # Saving the matrix to the matrix filedata.get_filepath
        np.savetxt(fname=data_dc.get_filepath() + "_matrix", X=new_mat_dc, fmt='%1.4e', delimiter=' ', newline='\n')   # ADD THIS LINE FOR MATRIX FILE SAVING

 

        vec_count = vec_count + 1
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(v1_vec.size - vec_count))))
        
        

    print 'Overall duration: %s sec' % (stop - init_start, )

   
finally:

  



    # after the measurement ends, you need to close the data file.
    data_refl.close_file()
    data_dc.close_file()
    #data_current.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()


    # Saving UHFLI setting to the measurement data folder
    # You can load this settings file from UHFLI user interface 3
    #UHFLI_lib.UHF_save_settings(path = data_path_refl)