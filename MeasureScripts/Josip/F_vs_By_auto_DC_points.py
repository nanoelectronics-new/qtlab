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

def do_auto_EDSR():

    gate2div = 100.0
    gate24div = 10.0

    DAC2_values = np.array([-0.15, 0.0, 0.16])*gate2div # Multiplied with corresponding S3b division
    #mean = 0.0  #  Effective (on the sample) mean value of the AWG pulse in mV
    #DAC5_values = DAC5_values - mean
    DAC4_values = np.array([88.3,88.44,88.5])*gate24div # Multiplied with corresponding S3b division


    
    name_counter = 10
    
    gain = 1e8 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    power = -10.0 # in dBm
    
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
    
 
    for z,DAC2 in enumerate(DAC2_values): 
    	IVVI.set_dac2(DAC2_values[z])               # Set the DAC2 voltage
        IVVI.set_dac4(DAC4_values[z])       		# Set the DAC4 volt

        start = time()
        file_name = '1_3 IV %d_V_G2=%.2fmV_V_G24=%.2fmV'%(name_counter,IVVI.get_dac2()/gate2div,IVVI.get_dac4()/gate24div)
        name_counter += 1 
        
            
            
        ramp_rate_Y = 0.0005 #T/s
        step_size_BY = 2e-3 
        
        
        
        
        BY_vector = np.arange(50e-3,150e-3+step_size_BY,step_size_BY) #T  #
        
        magnetY.set_rampRate_T_s(ramp_rate_Y)
        
        
        freq_vec = arange(3e9,6e9,3e6)  # frequency 
        
        qt.mstart()
        
        
        data = qt.Data(name=file_name)
        
        #saving directly in matrix format for diamond program
        new_mat = np.zeros(len(freq_vec)) # Empty vector for storing the data 
        data_temp = np.zeros(len(freq_vec))  # Temporary vector for storing the data
        
        
        data.add_coordinate('Frequency [Hz]')  #v2
        data.add_coordinate('By [T]')   #v1
        data.add_value('Current [pA]')

        data.create_file()
        
        plot2d = qt.Plot2D(data, name=file_name+' 2D_2',autoupdate=False)
        plot3d = qt.Plot3D(data, name=file_name+' 3D_2', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly


        for i,v1 in enumerate(BY_vector):  
            
          			
            
            
            magnetY.set_field(BY_vector[i])  
    
        
            total_field = BY_vector[i]
    
            while math.fabs(BY_vector[i] - magnetY.get_field_get()) > 0.0001:
                qt.msleep(0.050)
    
    
    
    
    
    
            for j,freq in enumerate(freq_vec):  
    
    
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
        
                
                
                
        
            
        
        stop = time()
        vec_count = vec_count + 1
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(len(DAC2_values) - vec_count))))
    	   
        bc(path = data.get_dir(), fname = data.get_filename()+"_matrix")
    	   # after the measurement ends, you need to close the data file.
        #Saving plot images
        plot3d.save_png(filepath = data.get_dir())
        plot3d.save_eps(filepath = data.get_dir())
        data.close_file()
    	   # lastly tell the secondary processes (if any) that they are allowed to start again.
        qt.mend()


    	
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



