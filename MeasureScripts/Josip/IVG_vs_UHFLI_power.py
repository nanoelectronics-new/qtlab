from numpy import pi, random, arange, size
from time import time,sleep
import UHFLI_lib
reload(UHFLI_lib)
import numpy as np
import datetime
from Background_correction import Back_corr as bc



daq = UHFLI_lib.UHF_init_demod_multiple(device_id = 'dev2169', demod_c = [3])  # Initializing UHFLI



def dBm_to_volts_50ohm(P_dBm):
    '''
    Function for converting the power in dBm to a corresponding voltage on the 50 ohm resistor.
    Since UHFLI wants volts peak-peak through the API
    '''
    P_mW = 10**(P_dBm/10.0)
    P_volts = np.sqrt(0.05*P_mW)*np.sqrt(2)
    return P_volts




def IVG_vs_Power(P1 = -65.0, P2 = -30.0, numpts = 10, freq = 306.5e6):
    """
    This function performs gate voltage sweeps vs UHFLI carrier amplitude and records phase and amplitude response of the lockin.
    The carrier amplitude is swept linearly in linear scale (volts).
    In my case, horizontal or vertical cut of the DQD interdot transition is repeated for each UHFLI power setting. 

    Inputs:
        P1 (float) - starting power in dBm (coverted to volts afterwards)
        P2 (float) - ending power in dBm (coverted to volts afterwards)
        numpts (int) - number of points in a gate voltage sweep
    """

    
    
    Amplitudes = np.linspace(dBm_to_volts_50ohm(P1), dBm_to_volts_50ohm(P2), numpts) # Amplitude of the UHFLI carrier signal in Volts
    
    
    leak_test = False
    
    
    v_vec = arange(-4.5,-6.4,-0.02)   
    V_G_static = -3.85

    divgate = 100.0 # S3b card division factor

    bias = -200.0
    
    
    
    
    
    
    
    
    
    
    #For saving directly in a matrix format 
    new_mat_phase = np.zeros((len(v_vec))) # Creating empty matrix for storing all data
    temp_phase = np.zeros((len(v_vec))) 

    new_mat_amplitude = np.zeros((len(v_vec))) # Creating empty matrix for storing all data
    temp_amplitude = np.zeros((len(v_vec))) 
    
    
    
    
    qt.mstart()
    
    
    data = qt.Data(name=' V_G11_vs_UHFLI_amplitude_freq=%dHz'%(freq*1e6))  # Put one space before name
    data.add_coordinate('V_G 11 [mV]')   # Underline makes the next letter as index
    data.add_coordinate('UHFLI_amplitude [mV]')
    data.add_value(' Phase [deg]')      # Underline makes the next letter as index
    data.add_value(' Amplitude [V]')
    data.create_file()
    
    
    
    plot3d_phase = qt.Plot3D(data, name='IVG_vs_UHFLI_amplitude_phase_3D', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
    plot2d_phase = qt.Plot2D(data, name='IVG_vs_UHFLI_amplitude_phase_2D',autoupdate=False, valdim = 2)

    plot3d_amplitude = qt.Plot3D(data, name='IVG_vs_UHFLI_amplitude_amplitude_3D', coorddims=(1,0), valdim=3, style='image') #flipped coordims that it plots correctly
    plot2d_amplitude = qt.Plot2D(data, name='IVG_vs_UHFLI_amplitude_amplitude_2D',autoupdate=False, valdim = 3)



    
    
    
    
    
    
    
    
    IVVI.set_dac1(bias)  
    IVVI.set_dac2(V_G_static*divgate)

    # Set the UHFLI_frequency
    daq.setDouble('/dev2169/oscs/0/freq', freq)
    sleep(2.0)
    
    # For counting the overall time to finish
    init_start = time()
    vec_count = 0
    
    
    
    
    
    
    try:
        for ampl in Amplitudes:
            start = time() # Get the time stamp
            daq.setDouble('/dev2169/sigouts/0/amplitudes/3',ampl)  # Set the UHFLI carrier signal amplitude
            daq.setInt('/dev2169/sigins/0/autorange', 1)  # Autoset amplification
            sleep(0.5)
            for i,v in enumerate(v_vec):
                # set the voltage
                IVVI.set_dac3(v*divgate)
            
            
                result_refl = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 3)  # Reading the lockin
                result_refl = array(result_refl)
                result_phase = result_refl[0,1]  # Getting phase values
                result_amplitude =  result_refl[0,0] # Getting amplitude values
            
            
            
                # save the data point to the file
                data.add_data_point(v,ampl*1000, result_phase, result_amplitude)  
            
                # Add to the matrix
                temp_phase[i] = result_phase
                temp_amplitude[i] = result_amplitude


            
                qt.msleep(0.003)
            data.new_block()
            stop = time() # Get the time stamp 

            #Gluing new data vector to the data matrix 
            new_mat_phase = np.column_stack((new_mat_phase, temp_phase))
            new_mat_amplitude = np.column_stack((new_mat_amplitude, temp_amplitude))
            # Kicking out the first column  
            if not(i):
                new_mat_phase = new_mat_phase[:,1:] 
                new_mat_amplitude = new_mat_amplitude[:,1:]

            # Saving the matrix to the matrix filedata.get_filepath
            np.savetxt(fname=data.get_dir() + "\\phase_matrix.dat", X=new_mat_phase, fmt='%1.4e', delimiter=' ', newline='\n') 
            np.savetxt(fname=data.get_dir() + "\\amplitude_matrix.dat", X=new_mat_amplitude, fmt='%1.4e', delimiter=' ', newline='\n') 
        
            plot3d_phase.update()
            plot2d_phase.update()
            plot2d_amplitude.update()
            plot3d_amplitude.update()
            
            # Estimating the time until the end of the measurement
            vec_count = vec_count + 1
            print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(Amplitudes.size - vec_count))))
        print 'Overall duration: %s sec' % (stop - init_start, )
    
    
    
    finally:      
        #Saving plot images
        plot3d_phase.save_png(filepath = data.get_dir())
        plot3d_phase.save_eps(filepath = data.get_dir())
        plot3d_amplitude.save_png(filepath = data.get_dir())
        plot3d_amplitude.save_eps(filepath = data.get_dir())

        # Substracting the background
        bc(path = data.get_dir(), fname = "amplitude_matrix.dat")
        # Getting filepath to the data file
        data_path = data.get_dir() 
        # Saving UHFLI setting to the measurement data folder
        # You can load this settings file from UHFLI user interface 
        UHFLI_lib.UHF_save_settings(daq, path = data_path)
        # after the measurement ends, you need to close the data file.
        data.close_file()
        # lastly tell the secondary processes (if any) that they are allowed to start again.
        qt.mend()






#Performing the VG vs Power for different carrier frequencies
Freqs = np.array([305.65, 306.136, 306.604, 307.117, 307.682])*1e6 # Frequencies in MHz

for freq in Freqs:
    IVG_vs_Power(freq=freq)