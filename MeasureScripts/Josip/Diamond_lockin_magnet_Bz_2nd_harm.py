from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv

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

UHFLI_lib.UHF_init_demod_multiple(demod_c = [2,3])  # Initialize UHF LI  - 2 is 2nd harmonik and 3 is 1st harmonik

gain = 1e8 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

v2_vec = arange(-60,60.5,0.5)  #V_sd

div_factor = 100.0

#bias =0

#magnet
ramp_rate_Z = 0.0013 #T/s
#ramp_rate_Y = 0.00005 #T/s


step_size_BZ = 60e-3 
#step_size_BY = 20e-3 
BZ_vector = arange(0e-3,7.5+step_size_BZ,step_size_BZ) #T  # Those two vectors need to be the same left
#BY_vector = arange(0e-3,2,step_size_BY) #T  #

#if len(BZ_vector) != len(BY_vector):
    #raise Exception ("B vectors have different length")

#ramp_time = max((float(step_size_BY)/ramp_rate_Y),float(step_size_BZ)/ramp_rate_Z)
ramp_time = 1.1*(float(step_size_BZ)/ramp_rate_Z)


magnetZ.set_rampRate_T_s(ramp_rate_Z)
#magnetY.set_rampRate_T_s(ramp_rate_Y)




qt.mstart()


data_refl = qt.Data(name='IV_BZsweep_D5_638,71mV_13-10_G08_LF_lockin') #just renamed

data_harm2 = qt.Data(name='IV_BZsweep_D5_638,71mV_13-10_G08_2nd_harm')

data_dc = qt.Data(name='IV_BZsweep_D5_638,71mV_13-10_G08_current') #added to have current recored as well

data_path_refl = data_refl.get_dir()
data_path_dc = data_dc.get_dir()

#saving directly in matrix format for diamond program
data_temp_r = np.zeros((len(v2_vec)))
new_mat_r = np.zeros((len(v2_vec))) 

data_temp_harm2 = np.zeros((len(v2_vec)))
new_mat_harm2 = np.zeros((len(v2_vec)))

data_temp_dc = np.zeros((len(v2_vec)))
new_mat_dc = np.zeros((len(v2_vec))) 



data_dc.add_coordinate('V{SD} [mV]')
data_dc.add_coordinate('Bfield [T]')
data_dc.add_value('Current [pA]')


data_refl.add_coordinate('V{SD} [mV]')
data_refl.add_coordinate('Bfield [T]')
data_refl.add_value('Lockin out [pA]')

data_harm2.add_coordinate('V{SD} [mV]')
data_harm2.add_coordinate('Bfield [T]')
data_harm2.add_value('Lockin harmonik 2 [A.U.]')




data_dc.create_file()
data_refl.create_file()
data_harm2.create_file()



plot2d_refl = qt.Plot2D(data_refl, name='lockin_Bsweep2D',autoupdate=False)
plot3d_refl = qt.Plot3D(data_refl, name='lockin_Bsweep3D', coorddims=(1,0), valdim=2, style='image')

plot2d_dc = qt.Plot2D(data_dc, name='Current_Bsweep2D',autoupdate=False)
plot3d_dc = qt.Plot3D(data_dc, name='Current_Bsweep3D', coorddims=(1,0), valdim=2, style='image')

plot2d_harm2 = qt.Plot2D(data_harm2, name='harmonik2_Bsweep2D',autoupdate=False)
plot3d_harm2= qt.Plot3D(data_harm2, name='harmonik2_Bsweep3D', coorddims=(1,0), valdim=2, style='image')




init_start = time()
vec_count = 0


try:
    for i,v1 in enumerate(BZ_vector):  # CHANGE THIS LINE FOR MATRIX FILE SAVING
        
        
        start = time()

        magnetZ.set_field(BZ_vector[i])
        #magnetY.set_field(BY_vector[i])  

        #total_field = np.sqrt(BZ_vector[i]**2 + BY_vector[i]**2)

        #while math.fabs(BY_vector[i] - magnetY.get_field_get()) > 0.0001:
            #qt.msleep(0.050)

        while math.fabs(BZ_vector[i] - magnetZ.get_field_get()) > 0.0001:
            qt.msleep(0.050)






        for j,v2 in enumerate(v2_vec):  # CHANGE THIS LINE FOR MATRIX FILE SAVING

            IVVI.set_dac1(v2)

            # readout

            result_refl = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 3)  # Reading the lockin
            result_refl = array(result_refl)

            result_harm2 = result_refl[0][0]/gain*1e12  # Getting amplitude value from the first of two demods (2. harmonik)
              
        
            result_harm1 = result_refl[1][0]/gain*1e12  # Getting amplitude values from the other of two demods (1. harmonik)
              


            data_temp_r[j] = result_harm1

            data_temp_harm2[j] = result_harm2

            
            result_dc = dmm.get_readval()/gain*1e12

            data_temp_dc[j] = result_dc #for saving as matrix

            data_refl.add_data_point(v2/div_factor, v1, result_harm1) 
            data_dc.add_data_point(v2/div_factor, v1, result_dc) 
            data_harm2.add_data_point(v2/div_factor, v1, result_harm2) 
            
            qt.msleep(0.001)
        data_refl.new_block()
        data_dc.new_block()
        data_harm2.new_block()

        stop = time()

        new_mat_r = np.column_stack((new_mat_r, data_temp_r))
        new_mat_dc = np.column_stack((new_mat_dc, data_temp_dc))
        new_mat_harm2 = np.column_stack((new_mat_harm2, data_temp_harm2))
        if not(i): # Kicking out the first column filled with zeros
            new_mat_r = new_mat_r[:,1:]
            new_mat_dc = new_mat_dc[:,1:]
            new_mat_harm2 = new_mat_harm2[:,1:]

        

        plot2d_refl.update()
        plot3d_refl.update() 

        plot2d_dc.update()
        plot3d_dc.update() 

        plot2d_harm2.update()
        plot3d_harm2.update()

        # Saving the matrix to the matrix filedata.get_filepath
        np.savetxt(fname=data_refl.get_filepath() + "_matrix", X=new_mat_r, fmt='%1.4e', delimiter=' ', newline='\n')   # ADD THIS LINE FOR MATRIX FILE SAVING
    
        # Saving the matrix to the matrix filedata.get_filepath
        np.savetxt(fname=data_dc.get_filepath() + "_matrix", X=new_mat_dc, fmt='%1.4e', delimiter=' ', newline='\n')   # ADD THIS LINE FOR MATRIX FILE SAVING

        # Saving the matrix to the matrix filedata.get_filepath
        np.savetxt(fname=data_harm2.get_filepath() + "_matrix", X=new_mat_harm2, fmt='%1.4e', delimiter=' ', newline='\n')   # ADD THIS LINE FOR MATRIX FILE SAVING        

        vec_count = vec_count + 1
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(BZ_vector.size - vec_count))))
        
        

    print 'Overall duration: %s sec' % (stop - init_start, )

   
finally:

  



    # after the measurement ends, you need to close the data file.
    data_refl.close_file()
    data_dc.close_file()
    data_harm2.close_file()
    #data_current.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()

    magnetZ.set_field(0.0)  # Sweeping the field back to zero
    #magnetY.set_field(0.0)  # Sweeping the field back to zero

    while math.fabs(0.0 - magnetZ.get_field_get()) > 0.0001:   #Wait until field drops to zero
        qt.msleep(0.050)

    execfile('C:\QTLab\qtlab\MeasureScripts\Josip\IVG_forth.py')       # Taking the IVGs to determine if it shifted
    execfile('C:\QTLab\qtlab\MeasureScripts\Josip\IVG_back.py')

 

    # Saving UHFLI setting to the measurement data folder
    # You can load this settings file from UHFLI user interface 3
    UHFLI_lib.UHF_save_settings(path = data_path_dc)