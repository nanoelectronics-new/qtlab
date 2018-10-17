from numpy import pi, random, arange, size
from time import time,sleep
import UHFLI_lib
reload(UHFLI_lib)
import numpy as np
import datetime


"""
This script is used for tuning the sensitivity of the gate reflectometry phase response.
Horizontal or vertical cut of the interdot transition is repeated for each UHFLI frequency setting.
"""

daq = UHFLI_lib.UHF_init_demod_multiple(device_id = 'dev2169', demod_c = [3])
gain = 1e8 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

frequencies = np.linspace(219.00e6, 224.00e6, 50) #Hz

leak_test = False


v_vec = arange(15.00,16.75,0.06)   #V_G 24
V_G_static = 3.30  
bias = 0






#For saving directly in a matrix format 
new_mat = np.zeros((len(v_vec))) # Creating empty matrix for storing all data
temp = np.zeros((len(v_vec))) 





qt.mstart()


data = qt.Data(name=' V_G24_vs_UHFLI_frequency')  # Put one space before name
data.add_coordinate('V_G 24 [mV]')   # Underline makes the next letter as index
data.add_coordinate('Frequency [Hz]')
data.add_value(' Phase [deg]')      # Underline makes the next letter as index
data.create_file()



plot3d_phase = qt.Plot3D(data, name='IVG_vs_UHFLI_frequency_phase_3D', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
plot2d_phase = qt.Plot2D(data, name='IVG_vs_UHFLI_frequency_phase_2D',autoupdate=False)








IVVI.set_dac1(bias)  
IVVI.set_dac5(V_G_static)

# For counting the overall time to finish
init_start = time()
vec_count = 0




daq.setInt('/dev2169/sigins/0/autorange', 1)  # Autoset amplification

try:
    for freq in frequencies:
        start = time() # Get the time stamp
        daq.setDouble('/dev2169/oscs/0/freq', freq)  # Set the UHFLI oscillator frequency
        for i,v in enumerate(v_vec):
            # set the voltage
            IVVI.set_dac6(v)
        
        
            result_refl = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 0.5)  # Reading the lockin
            result_refl = array(result_refl)
            result_phase = result_refl[0,1]  # Getting phase values 
        
        
        
            # save the data point to the file
            data.add_data_point(v,freq, result_phase)  
        
            # Add to the matrix
            temp[i] = result_phase
        
            qt.msleep(0.003)
        data.new_block()
        stop = time() # Get the time stamp 
        #Gluing new data vector to the data matrix 
        new_mat = np.column_stack((new_mat, temp))
        # Kicking out the first column  
        if not(i):
            new_mat = new_mat[:,1:] 
        # Saving the matrix to the matrix filedata.get_filepath
        np.savetxt(fname=data.get_filepath() + "_matrix", X=new_mat, fmt='%1.4e', delimiter=' ', newline='\n')  
    
        plot3d_phase.update()
        plot2d_phase.update()
        
        # Estimating the time until the end of the measurement
        vec_count = vec_count + 1
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(frequencies.size - vec_count))))
    print 'Overall duration: %s sec' % (stop - init_start, )



finally:      
    #Saving plot images
    plot3d_phase.save_png(filepath = data.get_dir())
    plot3d_phase.save_eps(filepath = data.get_dir())
    
    # Getting filepath to the data file
    data_path = data.get_dir() 
    # Saving UHFLI setting to the measurement data folder
    # You can load this settings file from UHFLI user interface 
    UHFLI_lib.UHF_save_settings(daq, path = data_path)
    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()