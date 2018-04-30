from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import numpy as np
from Background_correction import Back_corr as bc



# Coeffs of the DC point sweeping line
#a = 0.89448  # Direction coeff
#b = 58.30482 # y axis cut	

#DAC5_values = np.linspace(-358.724, -357.113, 10.0)  
#DAC6_values = a*DAC5_values + b  # Calculating the DAC6 values based on the line formula

# Shifting the DAC6 DC points for the mean value of the pulse 
#horizontal_shift = (200-113.51)*0.008  # 113.5 is the mean value of the pulse and the 0.008 the conversion factor to get an effective voltage
#DAC5_values  = DAC5_values - horizontal_shift

DAC5_values = np.array([-358.547,-358.368,-358.229,-358.015,-357.822,-357.676,-357.538,-357.310,-357.137,-356.978])
mean = 1.2308  #  Effective (on the sample) mean value of the AWG pulse in mV
DAC5_values = DAC5_values - mean
DAC6_values = np.array([-262.703,-262.544,-262.401,-262.250,-262.108,-261.948,-261.806,-261.647,-261.496,-261.353])

name_counter = 500

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
    for z,DAC5 in enumerate(DAC5_values): 
    	IVVI.set_dac5(DAC5_values[z])               # Set the DAC5 voltage
        IVVI.set_dac6(DAC6_values[z])       		# Set the DAC6 volt

        start = time()
        file_name = '1_3 IV %d_DAC5=%.2fmV_DAC6=%.2fmV'%(name_counter,IVVI.get_dac5(),IVVI.get_dac6())
        name_counter += 1 
        
            
            
        ramp_rate_Y = 0.0008 #T/s
        step_size_BY = -2e-3 
        
        
        
        
        BY_vector = arange(155e-3,105e-3+step_size_BY,step_size_BY) #T  #
        
        magnetY.set_rampRate_T_s(ramp_rate_Y)
        
        
        freq_vec = arange(5.3e9,6.3e9,3e6)  # frequency 
        
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
            print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(len(DAC5_values) - vec_count))))
		    
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



