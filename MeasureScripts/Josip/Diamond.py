from numpy import pi, random, arange, size, linspace
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv
import UHFLI_lib

#####################################################
# this part is to simulate some data, you can skip it
#####################################################



daq = UHFLI_lib.UHF_init_demod_multiple(demod_c = [3])
#var_list = [0,-1000,-1250,-1500,-1750,-2000]#,167.24+0.0526,185.34-0.26316,185.34+0.26316]
#frek_list = [271.83,273.37,281.87,286.79,290.40,292.91,150.31]
var_list = [-1000,-2000,-1500]
frek_list = [273.37,292.91,286.79]



index = 0
for index,frek in enumerate(var_list):
    #frek = frek*1000000
    #frek = int(frek)
    #daq.setInt('/dev2210/oscs/3/freq', frek)

    


    #####################################################
    # here is where the actual measurement program starts
    #####################################################
    #IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
    #dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54502777::INSTR')
    #dmm.set_NPLC = 1  # Setting PLCs of dmm
    init_dict = {'Address': 'TCPIP::10.21.41.103::hislip0::INSTR',
                         'Meas_param':'S21',
                         'Cont_off/on':'OFF',
                         'Num_of_sweep_points' : 201,  
                         'Num_of_sweeps' : 1, 
                         'Averaging' : 'OFF', 
                         'BW' : 5, 
                         'Source_power' : -20, 
                         'Data_format' : 'MLOG', 
                         'VNA_mode' : 'MLOG',
                         'Start_freq': 75.38,
                         'Stop_freq': 75.38,
                         'Center_freq' : 200 
                        }
    #VNA = qt.instruments.create('VNA','RS_ZNB20',address = 'TCPIP::10.21.41.148::hislip0::INSTR', init_dict_update = init_dict)

    file_name = ' Diamond_GS_40mK_06-07_G08_LFfridge_IronWoman_L_220nH_var05_%smV_'%(frek*5) #SAMPLE10_01-17_G24&18_foffset_sweep_on_freq_%sMHz_'%(frek*1e-6)

    gain = 1e8 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

    # you define two vectors of what you want to sweep. In this case
    # a magnetic field (b_vec) and a frequency (f_vec)

    bias = -200



    #PdBm = arange(-15,-31,-1)   # Power vector in dBm
    #Pvolt = 10**((PdBm-10)/20.0)  # Power vector converterd to Volts

    #foffset = linspace(1000000,-1000000, 20)

    #v1_vec = Pvolt     #Power vector
    #v1_vec = foffset  # Readout frequency offset vector
    #v2_vec = arange(-250,-300,-0.1)  #V_g 

    v2_vec = arange(-300,300,1)   #V_sd
    v1_vec = arange(-430,-460,-0.06)  #V_g



    # you indicate that a measurement is about to start and other
    # processes should stop (like batterycheckers, or temperature
    # monitors)
    qt.mstart()

    # Next a new data object is made.
    # The file will be placed in the folder:
    # <datadir>/<datestamp>/<timestamp>_testmeasurement/
    # and will be called:
    # <timestamp>_testmeasurement.dat
    # to find out what 'datadir' is set to, type: qt.config.get('datadir')

    data = qt.Data(name=file_name + 'current')
    data_refl = qt.Data(name=file_name + 'reflection')
    data_phase = qt.Data(name=file_name + 'refl_phase')

    # Now you provide the information of what data will be saved in the
    # datafile. A distinction is made between 'coordinates', and 'values'.
    # Coordinates are the parameters that you sweep, values are the
    # parameters that you readout (the result of an experiment). This
    # information is used later for plotting purposes.
    # Adding coordinate and value info is optional, but recommended.
    # If you don't supply it, the data class will guess your data format.
    data.add_coordinate('V_{SD} [mV]')
    data.add_coordinate('V_{G} [mV]')
    data.add_value('Current [pA]')

    data_refl.add_coordinate('V_{SD [mV]')
    data_refl.add_coordinate('V_{G} [mV]')
    data_refl.add_value('Reflection [V]')

    data_phase.add_coordinate('V_{SD [mV]')
    data_phase.add_coordinate('V_{G} [mV]')
    data_phase.add_value('Refl_phase [deg]')


    # The next command will actually create the dirs and files, based
    # on the information provided above. Additionally a settingsfile
    # is created containing the current settings of all the instruments.
    data.create_file()
    data_refl.create_file()
    data_phase.create_file()

    #data_path = data.get_dir()

    #saving directly in matrix format for diamond program
    new_mat_cur = np.zeros((len(v2_vec), len(v1_vec))) # Creating empty matrix for storing all data  
    new_mat_refl = np.zeros((len(v2_vec), len(v1_vec))) # Creating empty matrix for storing all data 
    new_mat_phase = np.zeros((len(v2_vec), len(v1_vec))) # Creating empty matrix for storing all data  

    # Next two plot-objects are created. First argument is the data object
    # that needs to be plotted. To prevent new windows from popping up each
    # measurement a 'name' can be provided so that window can be reused.
    # If the 'name' doesn't already exists, a new window with that name
    # will be created. For 3d plots, a plotting style is set.
    plot2d = qt.Plot2D(data, name='measure2D_current3',autoupdate=False)
    plot3d = qt.Plot3D(data, name='measure3D_current3', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
    plot2d_refl = qt.Plot2D(data_refl, name='measure2D_reflection3',autoupdate=False)
    plot3d_refl = qt.Plot3D(data_refl, name='measure3D_reflection3', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly
    plot2d_phase = qt.Plot2D(data_phase, name='measure2D_phase4',autoupdate=False)
    plot3d_phase = qt.Plot3D(data_phase, name='measure3D_phase4', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly


    # preparation is done, now start the measurement.
    # It is actually a simple loop.

    init_start = time()
    vec_count = 0



    try:
        IVVI.set_dac6(0)   # First discharge varactor
        sleep(10)
        IVVI.set_dac6(frek)   # Setting varactor 5 voltage
        daq.setDouble('/dev2148/oscs/0/freq',frek_list[index]*1e6)  # Setting the readout frequency on resonance
        sleep(10)  # Waiting for varactor response
        daq.setInt('/dev2148/sigins/0/autorange', 1)  # Autoset amplification
        
        for i,v1 in enumerate(v1_vec):
            
            
            start = time()
            # set the voltage
            #IVVI.set_dac5(v1)
            #daq.setDouble('/dev2210/sigouts/0/amplitudes/3', v1) 
            #daq.setDouble('/dev2210/oscs/3/freq', frek+v1)
            IVVI.set_dac5(v1)

            #sleep(0.2)  # Waiting for the stable amplitude
            #daq.setInt('/dev2210/sigins/0/autorange', 1)  # Autoset amplification
            

            for j,v2 in enumerate(v2_vec):

                IVVI.set_dac1(v2)
                

                # readout
                result = dmm.get_readval()/gain*1e12
                result_refl = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 3)  # Reading the lockin
                result_refl = array(result_refl)
                result_phase = sum(result_refl[:,1])  # Getting phase values from all three demodulators and summing them
                result_reflection = sum(result_refl[:,0]) # Getting amplitude values from all three demodulators and summing them
            
                # save the data point to the file, this will automatically trigger
                # the plot windows to update
                data.add_data_point(v2,v1, result)  
                data_refl.add_data_point(v2,v1, result_reflection)
                data_phase.add_data_point(v2,v1, result_phase)

                # Save to the matrix
                new_mat_cur[j,i] = result
                new_mat_refl[j,i] = result_reflection  
                new_mat_phase[j,i] = result_phase 

                # the next function is necessary to keep the gui responsive. It
                # checks for instance if the 'stop' button is pushed. It also checks
                # if the plots need updating.
                qt.msleep(0.001)
            data.new_block()
            data_refl.new_block()
            data_phase.new_block()
            stop = time()
            

            plot2d.update()
            plot3d.update()
            plot2d_refl.update()
            plot3d_refl.update()
            plot2d_phase.update()
            plot3d_phase.update()

            vec_count = vec_count + 1
            print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(v1_vec.size - vec_count))))
            
            

        print 'Overall duration: %s sec' % (stop - init_start, )

    finally:
       
        # This part kicks out trailing zeros and last IV if it is not fully finished (stopped somwhere in the middle)  
        for i, el in enumerate(new_mat_cur[0]):     
            all_zeros = not np.any(new_mat_cur[:,i])    # Finiding first column with all zeros
            if all_zeros:
                new_mat_cur = new_mat_cur[:,0:i-1]          # Leving all columns until that column, all the other are kicked out
                break

       # This part kicks out trailing zeros and last IV if it is not fully finished (stopped somwhere in the middle) 
        for i, el in enumerate(new_mat_refl[0]):     
            all_zeros = not np.any(new_mat_refl[:,i])    # Finiding first column with all zeros
            if all_zeros:
                new_mat_refl = new_mat_refl[:,0:i-1]          # Leving all columns until that column, all the other are kicked out
                break

        # This part kicks out trailing zeros and last IV if it is not fully finished (stopped somwhere in the middle) 
        for i, el in enumerate(new_mat_phase[0]):     
            all_zeros = not np.any(new_mat_phase[:,i])    # Finiding first column with all zeros
            if all_zeros:
                new_mat_phase = new_mat_phase[:,0:i-1]          # Leving all columns until that column, all the other are kicked out
                break


        # Saving the matrix to the matrix filedata.get_filepath
        np.savetxt(fname=data.get_filepath() + "_matrix", X=new_mat_cur, fmt='%1.4e', delimiter=' ', newline='\n')  

        # Saving the matrix to the matrix filedata.get_filepath
        np.savetxt(fname=data_refl.get_filepath() + "_matrix", X=new_mat_refl, fmt='%1.4e', delimiter=' ', newline='\n')  

        # Saving the matrix to the matrix filedata.get_filepath
        np.savetxt(fname=data_phase.get_filepath() + "_matrix", X=new_mat_phase, fmt='%1.4e', delimiter=' ', newline='\n')  

        # after the measurement ends, you need to close the data files.
        data.close_file()
        data_refl.close_file()
        data_phase.close_file()
        # lastly tell the secondary processes (if any) that they are allowed to start again.
        qt.mend()
