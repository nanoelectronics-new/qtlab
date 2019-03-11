from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import numpy as np
from Background_correction import Back_corr as bc
import UHFLI_lib
reload(UHFLI_lib)
#####################################################
# this part is to simulate some data, you can skip it
#####################################################




#####################################################
# here is where the actual measurement program starts
#####################################################

daq = UHFLI_lib.UHF_init_demod_multiple(device_id = 'dev2169', demod_c = [3])
#VSG = qt.instruments.create('VSG','RS_SMW200A',address = 'TCPIP::10.21.64.105::hislip0::INSTR')


def f_vs_B(vg = None):
    """Function for running frequency vs magnetic field sweep."""

    global name_counter

    name_counter += 1

    file_name = '8-10 IV %d_Vg9=%.2fmV'%(name_counter, vg)
    
    TC = 50e-3 # Time constant of the UHFLI in seconds
    
    power = -35.0
    theta = 0.0 
    
    ramp_rate_Y = 0.00054 #T/s
    ramp_rate_Z = 0.0005 #T/s
    step_size_BY = 1e-3 
    step_size_BZ = 1e-3
    Bmin = 130e-3  # Min total field in T
    Bmax = 400e-3 # Max total field in T
    Bymin = Bmin*np.cos(np.deg2rad(theta))  # Min By field in T
    Bymax = Bmax*np.cos(np.deg2rad(theta))  # Max By field in T
    Bzmin = Bmin*np.sin(np.deg2rad(theta))  # Min Bz field in T
    Bzmax = Bmax*np.sin(np.deg2rad(theta))  # Max Bz field in T
        
        
    BY_vector = np.linspace(Bymin,Bymax,100) # Defining the By vector in T  
    magnetY.set_rampRate_T_s(ramp_rate_Y)
    BZ_vector = np.linspace(Bzmin,Bzmax,100) # Defining the Bz vector in T  
    magnetZ.set_rampRate_T_s(ramp_rate_Z)
    
    
    freq_vec = arange(3e9,9e9,5e6)  # frequency 
    
    qt.mstart()
    
    
    data = qt.Data(name=file_name)

    
    #saving directly in matrix format for diamond program
    new_mat_amplitude = np.zeros(len(freq_vec)) # Empty vector for storing the data 
    data_temp_amplitude = np.zeros(len(freq_vec))  # Temporary vector for storing the data
    
    
    #saving directly in matrix format for diamond program
    new_mat_phase = np.zeros(len(freq_vec)) # Empty vector for storing the data 
    data_temp_phase = np.zeros(len(freq_vec))  # Temporary vector for storing the data
    
    
    data.add_coordinate('Frequency [Hz]')  #v2
    data.add_coordinate('B [T]')   #v1
    data.add_value('Refl amplitude [V]')
    data.add_value('Refl phase [degrees]')
    
    
    data.create_file()
    
    
    #plot2d_amplitude = qt.Plot2D(data, name=file_name+ ' amplitude1D',autoupdate=False)
    plot3d_amplitude = qt.Plot3D(data, name=file_name+ ' amplitude2D', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
    
    #plot2d_phase = qt.Plot2D(data, name=file_name+' phase1D',autoupdate=False)
    plot3d_phase = qt.Plot3D(data, name=file_name+' phase2D', coorddims=(1,0), valdim=3, style='image') #flipped coordims that it plots correctly
    
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
        for i,v1 in enumerate(BY_vector):  
            
            
            start = time()
        
            
            magnetY.set_field(BY_vector[i])   # Set the By field first
            while math.fabs(BY_vector[i] - magnetY.get_field_get()) > 0.0001:  # Wait until the By field is set
                qt.msleep(0.050)
    
            magnetZ.set_field(BZ_vector[i])   # Set the Bz field second
            while math.fabs(BZ_vector[i] - magnetZ.get_field_get()) > 0.0001:  # Wait until the Bz field is set
                qt.msleep(0.050)
                
            total_field = np.sqrt(BY_vector[i]**2+BZ_vector[i]**2)
    
            
            # After the field is at the set point, we need to check where is the resonant freuqency and set it
            freq, R = UHFLI_lib.run_sweeper(oscilator_num = 0, demod = 3, start = 290e6, stop = 308e6, num_samples = 200, do_plot= False)
            ind_res = np.where(R == R.min())  # On resonance the amplitude has the minimum value -> getting the index of the resonant frequency
            f_res = freq[ind_res] 
            f_res = f_res[0] - 160e3 # Readout fruequency is offset for -130 kHz from the resonant frequency
            # Now set the readout frequency to be the new resonance frequency
            daq.setDouble('/dev2169/oscs/0/freq', f_res)
            # Set the TC back to previous
            daq.setDouble('/dev2169/demods/3/timeconstant', TC)
    
            daq.setInt('/dev2169/sigins/0/autorange', 1)  # Autoset amplification
            qt.msleep(0.10)
    
            temp_freq = freq_vec[0] # Initial temporary frequency is the first value in the frequency sweep
            temp_power = power
    
            for j,freq in enumerate(freq_vec):  
    
                # For the coax line L1 the power drop from 5 to 15 GHz is 10 dB and it looks linear in this units -> 1dB per GHz
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
                qt.msleep(0.010)
    
                # readout
                # readout
                result_refl = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 2)  # Reading the lockin
                result_refl = array(result_refl)
                result_phase = result_refl[0,1]  # Getting phase values 
                result_amp = result_refl[0,0] # Getting amplitude values 
                
                data_temp_amplitude[j] = result_amp
                data_temp_phase[j] = result_phase
                # save the data point to the file, this will automatically trigger
                # the plot windows to update
                data.add_data_point(freq,total_field, result_amp, result_phase)  
    
          
                
    
             
                
            data.new_block()
            stop = time()
            # Converting the reflectometry amplitude data to the matrix format
            new_mat_amplitude = np.column_stack((new_mat_amplitude, data_temp_amplitude))
            if i == 0: #Kicking out the first column filled with zero
                new_mat_amplitude = new_mat_amplitude[:,1:]
            np.savetxt(fname = data.get_dir() + '/' + file_name + "_amplitude_matrix.dat", X = new_mat_amplitude, fmt = '%1.4e', delimiter = '  ', newline = '\n')
    
            # Converting the reflectometry phase data to the matrix format
            new_mat_phase = np.column_stack((new_mat_phase, data_temp_phase))
            if i == 0: #Kicking out the first column filled with zero
                new_mat_phase = new_mat_phase[:,1:]
            np.savetxt(fname = data.get_dir() + '/' + file_name + "_phase_matrix.dat", X = new_mat_phase, fmt = '%1.4e', delimiter = '  ', newline = '\n')
            
            plot3d_amplitude.update()
            plot3d_phase.update()
            #plot2d_amplitude.update()
            #plot2d_phase.update()
    
            vec_count = vec_count + 1
            print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(BY_vector.size - vec_count))))
            
            
    finally:
        print 'Overall duration: %s sec' % (stop - init_start, )
    
    
    
        # Switching off the RF 
        VSG.set_status("off") 
    
        #Stop the AWG sequence 
        #AWG.stop()
        #Turn OFF all necessary AWG channels
        #AWG.set_ch1_output(0)
        #AWG.set_ch2_output(0)
        #AWG.set_ch3_output(0)
        #AWG.set_ch4_output(0)
    
        # after the measurement ends, you need to close the data file.
        data.close_file()
    
        bc(path = data.get_dir(), fname = file_name + "_amplitude_matrix.dat")
        bc(path = data.get_dir(), fname = file_name + "_phase_matrix.dat")
    
        # lastly tell the secondary processes (if any) that they are allowed to start again.
        qt.mend()



V_G9 = np.linspace(-15.60,-14.80,8)

gatediv = 10.0
IVVI.set_dac3(-20.0*gatediv)

for vg in V_G9:  # Do measurement for different DC points
    IVVI.set_dac2(vg*gatediv)
    # Do_measurement
    f_vs_B(vg = vg)


