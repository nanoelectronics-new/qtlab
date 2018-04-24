from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import numpy as np
from Background_correction import Back_corr as bc



thetas = arange(70,95,5) # Angle between the By and x axis

name_counter = 478

gain = 1000e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
power = -4.0

# Set the VSG power units
VSG.set_power_units("dbm") 
# Set the RF power
VSG.set_power(power)
# Turn the RF on
VSG.set_status("on") 
## Run the AWG sequence 
#AWG.run()
## Turn ON all necessary AWG channels
#AWG.set_ch1_output(1)
#AWG.set_ch2_output(1)
#AWG.set_ch3_output(1)
#AWG.set_ch4_output(1)

init_start = time()
vec_count = 0

try:  
    for z,theta in enumerate(thetas): 

        start = time()
        
        file_name = '1_3 IV %d_theta=%d'%(name_counter,180-theta)
        name_counter += 1 
        
            
            
        ramp_rate_Y = 0.0008 #T/s
        ramp_rate_Z = 0.0008 #T/s
        step_size_BY = -2e-3 
        step_size_BZ = -2e-3

        Bmin = 140e-3  # Min total field in T
        Bmax = 190e-3 # Max total field in T
        Bymin = Bmin*np.cos(np.deg2rad(theta))  # Min By field in T
        Bymax = Bmax*np.cos(np.deg2rad(theta))  # Max By field in T
        Bzmin = Bmin*np.sin(np.deg2rad(theta))  # Min Bz field in T
        Bzmax = Bmax*np.sin(np.deg2rad(theta))  # Max Bz field in T
        
        
        BY_vector = np.linspace(-Bymax,-Bymin,45) # Defining the By vector in T  
        magnetY.set_rampRate_T_s(ramp_rate_Y)

        BZ_vector = np.linspace(Bzmax,Bzmin,45) # Defining the Bz vector in T  
        magnetZ.set_rampRate_T_s(ramp_rate_Z)
        
        
        freq_vec = arange(2.5e9,4e9,3e6)  # frequency 
        
        qt.mstart()
        
        
        data = qt.Data(name=file_name)
        
        #saving directly in matrix format for diamond program
        new_mat = np.zeros(len(freq_vec)) # Empty vector for storing the data 
        data_temp = np.zeros(len(freq_vec))  # Temporary vector for storing the data
        
        
        data.add_coordinate('Frequency [Hz]')  #v2
        data.add_coordinate('B [T]')   #v1
        data.add_value('Current [pA]')
        
        plot2d = qt.Plot2D(data, name=file_name+' 2D_2',autoupdate=False)
        plot3d = qt.Plot3D(data, name=file_name+' 3D_2', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
        
        
        try:
            for i,v1 in enumerate(BY_vector):  
                
              			
            
                
                magnetY.set_field(BY_vector[i])   # Set the By field
                magnetZ.set_field(BZ_vector[i])   # Set the Bz field
        
                

        
                while math.fabs(BY_vector[i] - magnetY.get_field_get()) > 0.0001:  # Wait until the By field is set
                    qt.msleep(0.050)

                while math.fabs(BZ_vector[i] - magnetZ.get_field_get()) > 0.0001:  # Wait until the Bz field is set
                    qt.msleep(0.050)
                
                total_field = np.sqrt(BY_vector[i]**2+BZ_vector[i]**2)
        
        
        
        
        
                for j,freq in enumerate(freq_vec):  
        
                    #IVVI.set_dac5(v2)
        
                    VSG.set_frequency(freq)
        
                    # the next function is necessary to keep the gui responsive. It
                    # checks for instance if the 'stop' button is pushed. It also checks
                    # if the plots need updating.
                    qt.msleep(0.005)
        
                    # readout
                    result = dmm.get_readval()/gain*1e12
                    
                    data_temp[j] = result
                    # save the data point to the file, this will automatically trigger
                    # the plot windows to update
                    data.add_data_point(freq,total_field, result)  
                
                    
        
                 
                    
                data.new_block()
                
                new_mat = np.column_stack((new_mat, data_temp))
                if i == 0: #Kicking out the first column filled with zero
                    new_mat = new_mat[:,1:]
                np.savetxt(fname = data.get_filepath()+ "_matrix", X = new_mat, fmt = '%1.4e', delimiter = '  ', newline = '\n')
                
        
                plot2d.update()
        
                plot3d.update()
        
                
                
                
        
            
        finally:
            stop = time()
            vec_count = vec_count + 1
            print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(len(thetas) - vec_count))))
		    
            bc(path = data.get_dir(), fname = data.get_filename()+"_matrix")
		    # after the measurement ends, you need to close the data file.
            data.close_file()
		    # lastly tell the secondary processes (if any) that they are allowed to start again.
            qt.mend()

finally:
	
	# Switching off the RF 
	VSG.set_status("off")
	#Stop the AWG sequence 
	#AWG.stop()
	#Turn OFF all necessary AWG channels
	#AWG.set_ch1_output(0)
	#AWG.set_ch2_output(0)
	#AWG.set_ch3_output(0)
	#AWG.set_ch4_output(0)
	print 'Overall duration: %s sec' % (stop - init_start, )



