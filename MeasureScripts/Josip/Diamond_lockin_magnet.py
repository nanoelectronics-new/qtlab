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
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x0957::0x0607::MY53003401::INSTR')
#dmm.set_NPLC = 1  # Setting PLCs of dmm
#magnetZ = qt.instruments.create('magnetZ', 'AMI430_Bz', address='10.21.64.185')
#magnetY = qt.instruments.create('magnetY', 'AMI430_By', address='10.21.64.175')

UHFLI_lib.UHF_init_demod(demod_c = 3)  # Initialize UHF LI

gain = 1e8 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

v2_vec = arange(-50,51,0.5)  #V_sd

div_factor = 100.0

#bias =0

#magnet
#ramp_rate_Z = 0.0002 #T/s
ramp_rate_Y = 0.00005 #T/s


#step_size_BZ = 1e-3 
step_size_BY = 20e-3 
#BZ_vector = arange(0e-3,10e-3+step_size_BZ,step_size_BZ) #T  # Those two vectors need to be the same left
BY_vector = arange(0e-3,2,step_size_BY) #T  #

#if len(BZ_vector) != len(BY_vector):
    #raise Exception ("B vectors have different length")

#ramp_time = max((float(step_size_BY)/ramp_rate_Y),float(step_size_BZ)/ramp_rate_Z)
ramp_time = 1.1*(float(step_size_BY)/ramp_rate_Y)


#magnetZ.set_rampRate_T_s(ramp_rate_Z)
magnetY.set_rampRate_T_s(ramp_rate_Y)




qt.mstart()


data_refl = qt.Data(name='_IV_Bsweep_13-10_G08_LF_lockin') #just renamed

data_dc = qt.Data(name='_IV_Bsweep_13-10_G08_current') #added to have current recored as well

data_path_refl = data_refl.get_dir()
data_path_dc = data_dc.get_dir()

#saving directly in matrix format for diamond program
new_mat_r = np.zeros((len(v2_vec), len(BY_vector))) # Creating empty matrix for storing all data   - ADD THIS LINE FOR MATRIX FILE SAVING, PUT APPROPRIATE VECTOR NAMES
new_mat_dc = np.zeros((len(v2_vec), len(BY_vector))) # Creating empty matrix for storing all data   - ADD THIS LINE FOR MATRIX FILE SAVING, PUT APPROPRIATE VECTOR NAMES



data_dc.add_coordinate('V{SD} [mV]')
data_dc.add_coordinate('Bfield [T]')
data_dc.add_value('Current [pA]')


data_refl.add_coordinate('V{SD} [mV]')
data_refl.add_coordinate('Bfield [T]')
data_refl.add_value('Lockin out [pA]')




data_dc.create_file()
data_refl.create_file()



plot2d_refl = qt.Plot2D(data_refl, name='lockin_Bsweep2D',autoupdate=False)
plot3d_refl = qt.Plot3D(data_refl, name='lockin_Bsweep3D', coorddims=(1,0), valdim=2, style='image')

plot2d_dc = qt.Plot2D(data_dc, name='Current_Bsweep2D',autoupdate=False)
plot3d_dc = qt.Plot3D(data_dc, name='Current_Bsweep3D', coorddims=(1,0), valdim=2, style='image')




init_start = time()
vec_count = 0


try:
    for i,v1 in enumerate(BY_vector):  # CHANGE THIS LINE FOR MATRIX FILE SAVING
        
        
        start = time()

        #magnetZ.set_field(BZ_vector[i])
        magnetY.set_field(BY_vector[i])  

        #total_field = np.sqrt(BZ_vector[i]**2 + BY_vector[i]**2)

        while math.fabs(BY_vector[i] - magnetY.get_field_get()) > 0.0001:
            qt.msleep(0.050)






        for j,v2 in enumerate(v2_vec):  # CHANGE THIS LINE FOR MATRIX FILE SAVING

            IVVI.set_dac1(v2)

            # readout
            result_reflectometry = UHFLI_lib.UHF_measure_demod(Num_of_TC = 3)/gain*1e12  # Reading the lockin and correcting for M1b gain

            new_mat_r[j,i] = result_reflectometry #for saving as matrix
            
            result_dc = dmm.get_readval()/gain*1e12

            new_mat_dc[j,i] = result_dc #for saving as matrix

            data_refl.add_data_point(v2/div_factor, v1, result_reflectometry) 
            data_dc.add_data_point(v2/div_factor, v1, result_dc) 
            
            qt.msleep(0.001)
        data_refl.new_block()
        data_dc.new_block()

        stop = time()
        

        plot2d_refl.update()
        plot3d_refl.update() 

        plot2d_dc.update()
        plot3d_dc.update() 

        vec_count = vec_count + 1
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(BY_vector.size - vec_count))))
        
        

    print 'Overall duration: %s sec' % (stop - init_start, )

   
finally:

    # This part kicks out trailing zeros and last IV if it is not fully finished (stopped somwhere in the middle)  # ADD THIS BLOCK FOR MATRIX FILE SAVING
    for i, el in enumerate(new_mat_r[0]):     
        all_zeros = not np.any(new_mat_r[:,i])    # Finiding first column with all zeros
        if all_zeros:
            new_mat_r = new_mat_r[:,0:i-1]          # Leving all columns until that column, all the other are kicked out
            break

    # Saving the matrix to the matrix filedata.get_filepath
    np.savetxt(fname=data_refl.get_filepath() + "_matrix", X=new_mat_r, fmt='%1.4e', delimiter=' ', newline='\n')   # ADD THIS LINE FOR MATRIX FILE SAVING

    for i, el in enumerate(new_mat_dc[0]):     
        all_zeros = not np.any(new_mat_dc[:,i])    # Finiding first column with all zeros
        if all_zeros:
            new_mat_dc = new_mat_dc[:,0:i-1]          # Leving all columns until that column, all the other are kicked out
            break

    # Saving the matrix to the matrix filedata.get_filepath
    np.savetxt(fname=data_dc.get_filepath() + "_matrix", X=new_mat_dc, fmt='%1.4e', delimiter=' ', newline='\n')   # ADD THIS LINE FOR MATRIX FILE SAVING
       
    #magnetZ.set_field(0.0)  # Sweeping the field back to zero
    magnetY.set_field(0.0)  # Sweeping the field back to zero


    # after the measurement ends, you need to close the data file.
    data_refl.close_file()
    data_dc.close_file()
    #data_current.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()

    # Saving UHFLI setting to the measurement data folder
    # You can load this settings file from UHFLI user interface 3
    UHFLI_lib.UHF_save_settings(path = data_path_refl)