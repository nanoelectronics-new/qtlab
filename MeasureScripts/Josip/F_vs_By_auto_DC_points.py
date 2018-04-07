from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import numpy as np



DAC5_center = -357.95       #  DAC5 center voltage in mV
DAC6_center = -261.33       #  DAC6 center voltage in mV
DAC5_offsets = np.linspace(-0.30,0.30,5) # DAC5 offsets from the center (to be swept through) voltage 
DAC6_offsets = np.linspace(-0.12,0.12,2) # DAC6 offsets from the center (to be swept through) voltage 


name_counter = 386

gain = 1000e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
power = -4.0

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
    for DAC5_off in DAC5_offsets:
        IVVI.set_dac5(DAC5_center + DAC5_off)               # Set the DAC5 voltage

        for DAC6_off in DAC6_offsets: 
            IVVI.set_dac6(DAC6_center + DAC6_off)           # Set the DAC6 voltage


            start = time()
            file_name = '1_3 IV %d_DAC5=%.2fmV_DAC6=%.2fmV'%(name_counter,IVVI.get_dac5(),IVVI.get_dac6())
            name_counter += 1 
            
                
                
            ramp_rate_Y = 0.0008 #T/s
            step_size_BY = -1e-3 
            
            
            
            
            BY_vector = arange(145e-3,115e-3+step_size_BY,step_size_BY) #T  #
            
            magnetY.set_rampRate_T_s(ramp_rate_Y)
            
            
            freq_vec = arange(5.5e9,6.5e9,3e6)  # frequency 
            
            qt.mstart()
            
            
            data = qt.Data(name=file_name)
            
            #saving directly in matrix format for diamond program
            new_mat = np.zeros(len(freq_vec)) # Empty vector for storing the data 
            data_temp = np.zeros(len(freq_vec))  # Temporary vector for storing the data
            
            
            data.add_coordinate('Frequency [Hz]')  #v2
            data.add_coordinate('By [T]')   #v1
            data.add_value('Current [pA]')
            
            plot2d = qt.Plot2D(data, name=file_name+' 2D_2',autoupdate=False)
            plot3d = qt.Plot3D(data, name=file_name+' 3D_2', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
            
            
            try:
                for i,v1 in enumerate(BY_vector):  
                    
                  			
                
                    
                    magnetY.set_field(BY_vector[i])  
            
                
                    total_field = BY_vector[i]
            
                    while math.fabs(BY_vector[i] - magnetY.get_field_get()) > 0.0001:
                        qt.msleep(0.050)
            
            
            
            
            
            
                    for j,freq in enumerate(freq_vec):  
            
                        #IVVI.set_dac5(v2)
            
                        VSG.set_frequency(freq)
            
                        # the next function is necessary to keep the gui responsive. It
                        # checks for instance if the 'stop' button is pushed. It also checks
                        # if the plots need updating.
                        qt.msleep(0.010)
            
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
                print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(DAC5_offsets.size*DAC6_offsets.size .size - vec_count))))
                
                bc(path = data.get_dir(), fname = data.get_filename()+"_matrix")
                # after the measurement ends, you need to close the data file.
                data.close_file()
                # lastly tell the secondary processes (if any) that they are allowed to start again.
                qt.mend()

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
	print 'Overall duration: %s sec' % (stop - init_start, )



