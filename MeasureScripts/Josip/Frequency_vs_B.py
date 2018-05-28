from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import numpy as np

#####################################################
# this part is to simulate some data, you can skip it
#####################################################




#####################################################
# here is where the actual measurement program starts
#####################################################

#UHFLI_lib.UHF_init_demod(demod_c = 2)  # Initialize UHF LI


file_name = '1_3 IV 590'


gain = 1000e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
power = -4.0
theta = 30.0 

ramp_rate_Y = 0.0008 #T/s
ramp_rate_Z = 0.0008 #T/s
step_size_BY = -2e-3 
step_size_BZ = -2e-3
Bmin = 80e-3  # Min total field in T
Bmax = 150e-3 # Max total field in T
Bymin = Bmin*np.cos(np.deg2rad(theta))  # Min By field in T
Bymax = Bmax*np.cos(np.deg2rad(theta))  # Max By field in T
Bzmin = Bmin*np.sin(np.deg2rad(theta))  # Min Bz field in T
Bzmax = Bmax*np.sin(np.deg2rad(theta))  # Max Bz field in T
    
    
BY_vector = np.linspace(Bymax,Bymin,45) # Defining the By vector in T  
magnetY.set_rampRate_T_s(ramp_rate_Y)
BZ_vector = np.linspace(Bzmax,Bzmin,45) # Defining the Bz vector in T  
magnetZ.set_rampRate_T_s(ramp_rate_Z)


freq_vec = arange(3e9,5e9,3e6)  # frequency 

qt.mstart()


data = qt.Data(name=file_name)
#data_lockin = qt.Data(name=file_name + '_lockin')

#saving directly in matrix format for diamond program
new_mat = np.zeros(len(freq_vec)) # Empty vector for storing the data 
data_temp = np.zeros(len(freq_vec))  # Temporary vector for storing the data


#saving directly in matrix format for diamond program
#new_mat_lockin = np.zeros(len(freq_vec)) # Empty vector for storing the data 
#data_temp_lockin = np.zeros(len(freq_vec))  # Temporary vector for storing the data


data.add_coordinate('Frequency [Hz]')  #v2
data.add_coordinate('B [T]')   #v1
data.add_value('Current [pA]')


#data_lockin.add_coordinate('Frequency [Hz)')
#data_lockin.add_coordinate('B [T]')   #
#data_lockin.add_value('Demod current [pA]')

data.create_file()
#data_lockin.create_file()


plot2d = qt.Plot2D(data, name=file_name+' 2D',autoupdate=False)
plot3d = qt.Plot3D(data, name=file_name+' 3D', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly

#plot2d_lockin = qt.Plot2D(data_lockin, name=file_name+' 2D_lockin',autoupdate=False)
#plot3d_lockin = qt.Plot3D(data_lockin, name=file_name+' 3D_lockin', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly

# Set the VSG power units
VSG.set_power_units("dbm") 
# Set the RF power
VSG.set_power(power)
# Turn the RF on
VSG.set_status("on") 
## Run the AWG sequence 
AWG.run()
## Turn ON all necessary AWG channels
AWG.set_ch1_output(1)
AWG.set_ch2_output(1)
AWG.set_ch3_output(1)
#AWG.set_ch4_output(1)

init_start = time()
vec_count = 0


try:
    for i,v1 in enumerate(BY_vector):  
        
        
        start = time()
    
        
        magnetY.set_field(BY_vector[i])   # Set the By field first
        while math.fabs(BY_vector[i] - magnetY.get_field_get()) > 0.0001:  # Wait until the By field is set
            qt.msleep(0.050)

        magnetZ.set_field(BZ_vector[i])   # Set the Bz field second
        while math.fabs(BZ_vector[i] - magnetZ.get_field_get()) > 0.0001:  # Wait until the Bz field is set
            qt.msleep(0.050)
            
        total_field = np.sqrt(BY_vector[i]**2+BZ_vector[i]**2)





        for j,freq in enumerate(freq_vec):  

            #IVVI.set_dac5(v2)

            VSG.set_frequency(freq)

            # the next function is necessary to keep the gui responsive. It
            # checks for instance if the 'stop' button is pushed. It also checks
            # if the plots need updating.
            qt.msleep(0.010)

            # readout
            result = dmm.get_readval()*1e12/gain
            #result_lockin = UHFLI_lib.UHF_measure_demod(Num_of_TC = 3)*1e12/gain  # Reading the lockin and correcting for M1b gain
            
            data_temp[j] = result
            #data_temp_lockin[j] = result_lockin
            # save the data point to the file, this will automatically trigger
            # the plot windows to update
            data.add_data_point(freq,total_field, result)  
            #data_lockin.add_data_point(freq,total_field, result_lockin)
      
            

         
            
        data.new_block()
        #data_lockin.new_block()
        stop = time()
        # Converting the DC current data to the matrix format
        new_mat = np.column_stack((new_mat, data_temp))
        if i == 0: #Kicking out the first column filled with zero
            new_mat = new_mat[:,1:]
        np.savetxt(fname = data.get_filepath()+ "_matrix", X = new_mat, fmt = '%1.4e', delimiter = '  ', newline = '\n')

        # Converting the lockin data to the matrix format
        #new_mat_lockin = np.column_stack((new_mat_lockin, data_temp_lockin))
        #if i == 0: #Kicking out the first column filled with zero
        #    new_mat_lockin = new_mat_lockin[:,1:]
        #np.savetxt(fname = data_lockin.get_filepath()+ "_matrix", X = new_mat_lockin, fmt = '%1.4e', delimiter = '  ', newline = '\n')
        

        plot2d.update()
        plot3d.update()
        #plot2d_lockin.update()
        #plot3d_lockin.update()

        vec_count = vec_count + 1
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(BY_vector.size - vec_count))))
        
        

    print 'Overall duration: %s sec' % (stop - init_start, )

finally:

    # Switching off the RF 
    VSG.set_status("off") 

    #Stop the AWG sequence 
    AWG.stop()
    #Turn OFF all necessary AWG channels
    AWG.set_ch1_output(0)
    AWG.set_ch2_output(0)
    AWG.set_ch3_output(0)
    #AWG.set_ch4_output(0)

    # after the measurement ends, you need to close the data file.
    data.close_file()
    #data_lockin.close_file()

    bc(path = data.get_dir(), fname = data.get_filename()+"_matrix")
    #bc(path = data_lockin.get_dir(), fname = data_lockin.get_filename()+"_matrix")

    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()

