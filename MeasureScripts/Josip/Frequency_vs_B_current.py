from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import numpy as np
execfile('C:/QTLab/qtlab/MeasureScripts/Background_correction.py')
import UHFLI_lib
reload(UHFLI_lib)
execfile('C:/QTLab/qtlab/MeasureScripts/Josip/save_the_plot.py') # Same as import save the plot function
#####################################################
# this part is to simulate some data, you can skip it
#####################################################




#####################################################
# here is where the actual measurement program starts
#####################################################

## Upload the chirp signal to the AWG
#execfile('C:/QTLab/qtlab/MeasureScripts/AWG_upload_chirp.py')

#daq = UHFLI_lib.UHF_init_demod_multiple(device_id = 'dev2169', demod_c = [3])
#VSG = qt.instruments.create('VSG','RS_SMW200A',address = 'TCPIP::10.21.64.105::hislip0::INSTR')


def f_vs_B(vg = None, Bmin = None, Bmax = None, power = -10):
    """Function for running frequency vs magnetic field sweep."""

    if (Bmin == None) or (Bmax==None):
        raise Exception("Define B field borders")

    global name_counter

    name_counter += 1

    file_name = '5-3 IV %d_Vg9=%.2fmV_Vg6=%.2fmV_power=%ddBm'%(name_counter, vg[0], vg[1], power)

    
    gain = 1e9
    
    power = power
    theta = 0.0 
    
    ramp_rate_Y = 0.0003 #T/s
    ramp_rate_Z = 0.0005 #T/s
    step_size_BY = 1e-3 
    step_size_BZ = 1e-3
    Bmin = Bmin  # Min total field in T
    Bmax = Bmax # Max total field in T
    Bymin = Bmin*np.cos(np.deg2rad(theta))  # Min By field in T
    Bymax = Bmax*np.cos(np.deg2rad(theta))  # Max By field in T
    Bzmin = Bmin*np.sin(np.deg2rad(theta))  # Min Bz field in T
    Bzmax = Bmax*np.sin(np.deg2rad(theta))  # Max Bz field in T
    
        
    BY_vector = np.linspace(Bymin,Bymax,25.0) # Defining the By vector in T  
    magnetY.set_rampRate_T_s(ramp_rate_Y)
    BZ_vector = np.linspace(Bzmin,Bzmax,25.0) # Defining the Bz vector in T  
    magnetZ.set_rampRate_T_s(ramp_rate_Z)
    
    
    freq_vec = arange(3.0e9,6.5e9,7e6)  # Frequency 
    
    qt.mstart()
    
    
    data = qt.Data(name=file_name)

    
    #saving directly in matrix format for diamond program
    new_mat_current = np.zeros(len(freq_vec)) # Empty vector for storing the data 
    data_temp_current = np.zeros(len(freq_vec))  # Temporary vector for storing the data
    
    
  
    
    
    data.add_coordinate('Frequency [Hz]')  #v2
    data.add_coordinate('B [T]')   #v1
    data.add_value('Current [pA]')

    
    
    data.create_file()
    
    
    plot2d_current = qt.Plot2D(data, name=file_name+ ' Current1D',autoupdate=False, valdim = 2)
    plot3d_current = qt.Plot3D(data, name=file_name+ ' Current2D', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
    

    
    # Set the VSG power units
    VSG.set_power_units("dbm") 
    # Set the RF power
    VSG.set_power(power)
    # Turn the RF on
    VSG.set_status("on") 

    
    init_start = time()
    vec_count = 0
    
    
    try:
        for i,v1 in enumerate(BY_vector):  
            
            start = time()
            ## SEting the B field 
            magnetY.set_field(BY_vector[i])   # Set the By field first
            while math.fabs(BY_vector[i] - magnetY.get_field_get()) > 0.0001:  # Wait until the By field is set
                qt.msleep(0.050)
    
            magnetZ.set_field(BZ_vector[i])   # Set the Bz field second
            while math.fabs(BZ_vector[i] - magnetZ.get_field_get()) > 0.0001:  # Wait until the Bz field is set
                qt.msleep(0.050)
                
            total_field = np.sqrt(BY_vector[i]**2+BZ_vector[i]**2)
    
    
    
    
            for j,freq in enumerate(freq_vec):  
                if j == 0:
                    temp_freq = freq_vec[0] # Initial temporary frequency is the first value in the frequency sweep
                    temp_power = power
                    VSG.set_power(temp_power)
    
    
                # For the coax line 3 the power drop, above 5 GHz, is 1dB per 1GHz
                # Therefore, each time the frequency increases for 1 GHz we are increasing the power for 1 dB
                if freq >= (temp_freq + 1e9):
                    temp_freq = freq
                    temp_power += 1
                    # Set the VSG power units
                    VSG.set_power_units("dbm") 
                    # Set the RF power
                    VSG.set_power(temp_power)
    
                VSG.set_frequency(freq)
    
                # the next function is necessary to keep the gui responsive. It
                # checks for instance if the 'stop' button is pushed. It also checks
                # if the plots need updating.
                qt.msleep(0.005)
    
                # readout
                result_current = dmm.get_readval()/gain*1e12  # Getting current values 
            
                data_temp_current[j] = result_current
                # save the data point to the file, this will automatically trigger
                # the plot windows to update
                data.add_data_point(freq,total_field, result_current)  
    
            ## Do the triangle scan at the beginning, in the middle and at the end of every EDSR scan
            if (i==0) or (i==(len(BY_vector)/2)) or (i == (len(BY_vector)-1)):
                ## Remeber the current DC point and the dmm PLC(aperture) before the triangle scan
                dmm_APER = dmm.get_APER()
                dac2_volt = IVVI.get_dac2()
                dac1_volt = IVVI.get_dac1()
                # Set the PLC to 0.2 for the fast triangle scan
                dmm.set_NPLC(0.2)
                do_meas_current(bias = 200.0,  v1_start = -495.5, v1_stop = -489.0, v2_start = -491.5, v2_stop = -484.0, v_middle = 3700.0, B_field = BY_vector[i])
                ## Set the DC point and the dmm PLC (aperture) back
                dmm.set_APER(dmm_APER)
                IVVI.set_dac2(dac2_volt)
                IVVI.set_dac1(dac1_volt)
    
            # Do the vertical line scan and correct the DC point
            #dmm_APER = dmm.get_APER()   # Remember the previous apreture
            #dmm.set_NPLC(1.0)           # Set the averaging for the line scan
            #line_scan, gate_voltages = run_line_scan()      # Get the line scan and corresponding gate voltages as numpy arrays
            #index_max_current = line_scan.argmax()    # Find the index of the maximum current
            #corr_volt = gate_voltages[index_max_current]    # Find the gate voltage that corresponds to the maximum current
            #IVVI.set_dac1(corr_volt - 0.4)  # Do the voltage correction
            #dmm.set_APER(dmm_APER)          # Set back to the previous aperture
    
    
            
                
    
             
                
            data.new_block()
            stop = time()
            # Converting the reflectometry amplitude data to the matrix format
            new_mat_current = np.column_stack((new_mat_current, data_temp_current))
            if i == 0: #Kicking out the first column filled with zero
                new_mat_current = new_mat_current[:,1:]
            np.savetxt(fname = data.get_dir() + '/' + file_name + "_matrix.dat", X = new_mat_current, fmt = '%1.4e', delimiter = '  ', newline = '\n')
    
        
            
            plot3d_current.update()
            plot2d_current.update()
    
    
            vec_count = vec_count + 1
            print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(BY_vector.size - vec_count))))
                
            
    finally:
        stop = time()
        print 'Overall duration: %s sec' % (stop - init_start, )
    
    
    
        # Switching off the RF 
        #VSG.set_status("off") 
    
    
        # after the measurement ends, you need to close the data file.
        data.close_file()
    
        corrected_data_matrix = bc(path = data.get_dir(), fname = file_name + "_matrix.dat")
        #bc(path = data.get_dir(), fname = file_name + "_lockin_matrix.dat")
        if BY_vector[0] > BY_vector[-1]:
        ## Checking if the x axis needs to be flipped or not. It depends on the scanning direction.
            save_the_plot(to_plot = corrected_data_matrix, title = file_name + '_current_CORR', x = BY_vector[::-1], y = freq_vec, y_label = data.get_coordinates()[0]['name'], x_label = data.get_coordinates()[1]['name'], c_label = data.get_values()[0]['name'], dire = data.get_dir())
        else:
            save_the_plot(to_plot = corrected_data_matrix, title = file_name + '_current_CORR', x = BY_vector, y = freq_vec, y_label = data.get_coordinates()[0]['name'], x_label = data.get_coordinates()[1]['name'], c_label = data.get_values()[0]['name'], dire = data.get_dir())

        # lastly tell the secondary processes (if any) that they are allowed to start again.
        qt.mend()


V_G9 = [-488.80,-487.24]
V_G6 = [-493.34,-491.69]

gatediv = 1.0
dmm.set_APER(0.1) # Set the dmm aperture time to 100 ms

# Run the G_vs_G once to have the function do_meas_current available and updated
execfile('C:/QTLab/qtlab/MeasureScripts/Josip/G_vs_G.py')

for nj,vg in enumerate(V_G9):     # Do measurement for different DC points
    
    IVVI.set_dac2(gatediv*V_G9[nj])
    IVVI.set_dac1(gatediv*V_G6[nj])
    # Do_measurement
    f_vs_B(vg = [V_G9[nj], V_G6[nj]], Bmin = 0.180, Bmax = 0.130, power = -10.0)









