from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import numpy as np





name_counter = 168

DC_points = [(-357.70,-261.7),(-358.04,-261.97),(-358.49,-262.324),(-358.88,-262.63),(-358.82,-262.90),(-358.50,-262.67),(-358.188,-262.434),(-357.873,-262.127),(-357.625,-261.935)]  # List of DC point tuples


for DC_point in DC_points:

	#Setting the DC point 
	IVVI.set_dac5(DC_point[0])  
	IVVI.set_dac6(DC_point[1])





	# Doing the f vs By measurement
	file_name = '1_3 IV %d'%(name_counter)
	name_counter += 1 

	gain = 1000e6 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G   
	    
	ramp_rate_Y = 0.0008 #T/s
	
	step_size_BY = -1e-3 
	
	BY_vector = arange(155e-3,105e-3+step_size_BY,step_size_BY) #T  #
	
	magnetY.set_rampRate_T_s(ramp_rate_Y)
	
	
	freq_vec = arange(5.3e9,6.3e9,3e6)  # frequency 
	
	qt.mstart()
	
	
	data = qt.Data(name=file_name)
	
	#saving directly in matrix format for diamond program
	new_mat = np.zeros(len(freq_vec)) # Empty vector for storing the data 
	data_temp = np.zeros(len(freq_vec))  # Temporary vector for storing the data
	
	
	data.add_coordinate('Frequency [Hz]')  #v2
	data.add_coordinate('Bfield [T]')   #v1
	data.add_value('Current [pA]')
	
	plot2d = qt.Plot2D(data, name=file_name+' 2D_2',autoupdate=False)
	plot3d = qt.Plot3D(data, name=file_name+' 3D_2', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
	
	
	
	init_start = time()
	vec_count = 0
	
	
	try:
	    for i,v1 in enumerate(BY_vector):  
	        
	        
	        start = time()
	    
	        
	        magnetY.set_field(BY_vector[i])  
	
	    
	        total_field = BY_vector[i]
	
	        while math.fabs(BY_vector[i] - magnetY.get_field_get()) > 0.0001:
	            qt.msleep(0.050)
	
	
	
	
	
	
	        for j,freq in enumerate(freq_vec):  
	
	            #IVVI.set_dac5(v2)
	
	            VSG.set_frequency(freq)
	            # readout
	            result = dmm.get_readval()/gain*1e12
	           
	            data_temp[j] = result
	            # save the data point to the file, this will automatically trigger
	            # the plot windows to update
	            data.add_data_point(freq,total_field, result)  
	        
	            
	
	            # the next function is necessary to keep the gui responsive. It
	            # checks for instance if the 'stop' button is pushed. It also checks
	            # if the plots need updating.
	            qt.msleep(0.001)
	        data.new_block()
	        stop = time()
	        new_mat = np.column_stack((new_mat, data_temp))
	        if i == 0: #Kicking out the first column filled with zero
	            new_mat = new_mat[:,1:]
	        np.savetxt(fname = data.get_filepath()+ "_matrix", X = new_mat, fmt = '%1.4e', delimiter = '  ', newline = '\n')
	        
	
	        plot2d.update()
	
	        plot3d.update()
	
	        vec_count = vec_count + 1
	        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(BY_vector.size - vec_count))))
	        
	        
	
	    print 'Overall duration: %s sec' % (stop - init_start, )
	
	finally:
	
	    bc(path = data.get_dir(), fname = data.get_filename()+"_matrix")
	    # after the measurement ends, you need to close the data file.
	    data.close_file()
	    # lastly tell the secondary processes (if any) that they are allowed to start again.
	    qt.mend()
