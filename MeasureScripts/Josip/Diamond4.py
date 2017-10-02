from numpy import pi, random, arange, size, linspace
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import UHFLI_lib

#####################################################
# this part is to simulate some data, you can skip it
#####################################################



daq = UHFLI_lib.UHF_init_demod_multiple(demod_c = [3])

    
#####################################################
# here is where the actual measurement program starts
#####################################################
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54502777::INSTR')
#dmm.set_NPLC = 1  # Setting PLCs of dmm


file_name = '11_18 IV 27'

gain = 1000e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G


bias = 80


v1_vec = arange(-100,100.5,0.5)   #V_sd
v2_vec = arange(80,140.4,0.4)  #V_g




qt.mstart()



data = qt.Data(name=file_name + 'current')
data_refl = qt.Data(name=file_name + 'reflection')
data_phase = qt.Data(name=file_name + 'refl_phase')


data.add_coordinate('V_{SD} [mV]')
data.add_coordinate('V_{G} [mV]')
data.add_value('Current [pA]')

data_refl.add_coordinate('V_{SD [mV]')
data_refl.add_coordinate('V_{G} [mV]')
data_refl.add_value('Reflection [V]')

data_phase.add_coordinate('V_{SD [mV]')
data_phase.add_coordinate('V_{G} [mV]')
data_phase.add_value('Refl_phase [deg]')



data.create_file()
data_refl.create_file()
data_phase.create_file()

#data_path = data.get_dir()

#saving directly in matrix format for diamond program
new_mat_cur = np.zeros((len(v2_vec), len(v1_vec))) # Creating empty matrix for storing all data  
new_mat_refl = np.zeros((len(v2_vec), len(v1_vec))) # Creating empty matrix for storing all data 
new_mat_phase = np.zeros((len(v2_vec), len(v1_vec))) # Creating empty matrix for storing all data  

# Next two plot-objects are created. First argument is the data object
# that needs to be plotted. To prevent new windows from popping up each
# measurement a 'name' can be provided so that window can be reused.
# If the 'name' doesn't already exists, a new window with that name
# will be created. For 3d plots, a plotting style is set.
plot2d = qt.Plot2D(data, name='measure2D_current3',autoupdate=False)
plot3d = qt.Plot3D(data, name='measure3D_current3', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
plot2d_refl = qt.Plot2D(data_refl, name='measure2D_reflection3',autoupdate=False)
plot3d_refl = qt.Plot3D(data_refl, name='measure3D_reflection3', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
plot2d_phase = qt.Plot2D(data_phase, name='measure2D_phase4',autoupdate=False)
plot3d_phase = qt.Plot3D(data_phase, name='measure3D_phase4', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly


# preparation is done, now start the measurement.
# It is actually a simple loop.
IVVI.set_dac1(bias)

init_start = time()
vec_count = 0

 

try:
    #daq.setInt('/dev2148/sigins/0/autorange', 1)  # Autoset amplification
    
    for i,v1 in enumerate(v1_vec):
        
        
        start = time()
        # set the voltage
   
        IVVI.set_dac6(v1)


        

        for j,v2 in enumerate(v2_vec):

            IVVI.set_dac4(v2)
            

            # readout
            result = dmm.get_readval()/gain*1e12
            result_refl = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 3)  # Reading the lockin
            result_refl = array(result_refl)
            result_phase = sum(result_refl[:,1])  # Getting phase values from all three demodulators and summing them
            result_reflection = sum(result_refl[:,0]) # Getting amplitude values from all three demodulators and summing them
        
            # save the data point to the file, this will automatically trigger
            # the plot windows to update
            data.add_data_point(v2,v1, result)  
            data_refl.add_data_point(v2,v1, result_reflection)
            data_phase.add_data_point(v2,v1, result_phase)

            # Save to the matrix
            new_mat_cur[j,i] = result
            new_mat_refl[j,i] = result_reflection  
            new_mat_phase[j,i] = result_phase 

            # the next function is necessary to keep the gui responsive. It
            # checks for instance if the 'stop' button is pushed. It also checks
            # if the plots need updating.
            qt.msleep(0.001)
        data.new_block()
        data_refl.new_block()
        data_phase.new_block()
        stop = time()
        

        plot2d.update()
        plot3d.update()
        plot2d_refl.update()
        plot3d_refl.update()
        plot2d_phase.update()
        plot3d_phase.update()

        vec_count = vec_count + 1
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(v1_vec.size - vec_count))))
        
        

    print 'Overall duration: %s sec' % (stop - init_start, )

finally:
   
    # This part kicks out trailing zeros and last IV if it is not fully finished (stopped somwhere in the middle)  
    for i, el in enumerate(new_mat_cur[0]):     
        all_zeros = not np.any(new_mat_cur[:,i])    # Finiding first column with all zeros
        if all_zeros:
            new_mat_cur = new_mat_cur[:,0:i-1]          # Leving all columns until that column, all the other are kicked out
            break

   # This part kicks out trailing zeros and last IV if it is not fully finished (stopped somwhere in the middle) 
    for i, el in enumerate(new_mat_refl[0]):     
        all_zeros = not np.any(new_mat_refl[:,i])    # Finiding first column with all zeros
        if all_zeros:
            new_mat_refl = new_mat_refl[:,0:i-1]          # Leving all columns until that column, all the other are kicked out
            break

    # This part kicks out trailing zeros and last IV if it is not fully finished (stopped somwhere in the middle) 
    for i, el in enumerate(new_mat_phase[0]):     
        all_zeros = not np.any(new_mat_phase[:,i])    # Finiding first column with all zeros
        if all_zeros:
            new_mat_phase = new_mat_phase[:,0:i-1]          # Leving all columns until that column, all the other are kicked out
            break


    # Saving the matrix to the matrix filedata.get_filepath
    np.savetxt(fname=data.get_filepath() + "_matrix", X=new_mat_cur, fmt='%1.4e', delimiter=' ', newline='\n')  

    # Saving the matrix to the matrix filedata.get_filepath
    np.savetxt(fname=data_refl.get_filepath() + "_matrix", X=new_mat_refl, fmt='%1.4e', delimiter=' ', newline='\n')  

    # Saving the matrix to the matrix filedata.get_filepath
    np.savetxt(fname=data_phase.get_filepath() + "_matrix", X=new_mat_phase, fmt='%1.4e', delimiter=' ', newline='\n')  

    # after the measurement ends, you need to close the data files.
    data.close_file()
    data_refl.close_file()
    data_phase.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
