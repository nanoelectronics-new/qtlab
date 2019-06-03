from numpy import pi, random, arange, size
from time import time,sleep
import UHFLI_lib
reload(UHFLI_lib)
import numpy as np



#####################################################
# EXAMPLE SCRIPT SHOWING HOW TO SET UP STANDARD 1D (IV) LOCKIN MEASUREMENT
#####################################################
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)  # Initialize IVVI
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x0957::0x0607::MY53003401::INSTR')   # Initialize dmm
UHFLI_lib.UHF_init_demod_multiple(device_id = 'dev2169', demod_c = [3])  # Initialize UHF LI


name_counter += 1

def run_IVG_both():
    gain = 1e8 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    
    bias = 200.0
    

    v_vec = arange(0.0,-1500.0,-0.1)   #V_G 4
    

    qt.mstart()

    
    name = ' 17-3 IVG %d'%name_counter
    data = qt.Data(name=name)  # Put one space before name
    
    
    
    data.add_coordinate('Voltage [mV]')   # Underline makes the next letter as index
    
    data.add_value(' Phase [deg]')      # Underline makes the next letter as index
    
    data.add_value('Current [pA]')      # Underline makes the next letter as index
    
    data.create_file()
    
    # Getting filepath to the data file
    data_path = data.get_dir() 
    
    plot2d = qt.Plot2D(data, name=name + '_phase', autoupdate=False, valdim =1)
    plot2d.set_style('lines')
    
    plot2d_dmm = qt.Plot2D(data, name=name + '_current', autoupdate=False, valdim =2)
    plot2d_dmm.set_style('lines')
    
    
    
    # Preparation is done, now start the measurement.
    IVVI.set_dac1(bias)
    IVVI.set_dac7(-600.0)
    IVVI.set_dac6(-600.0)
    # It is actually a simple loop.
    start = time()
    for v in v_vec:
        # set the voltage
        
        IVVI.set_dac5(v)

    
        # readout_dmm
        result_dmm = dmm.get_readval()/gain*1e12
        # readout form UHFLI
        # argument Num_of_TC represents number of time constants to wait before raeding the value
        # it is important because of the settling time of the low pass filter
        result_lockin = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 0.5, Integration_time = 0.002)  # Reading the lockin
        result_refl = array(result_lockin)
        result_phase = result_refl[0,1]  # Getting phase values 
    
        # save the data point to the file
        data.add_data_point(v, result_phase, result_dmm)  

        if (v%5 == 0):
            plot2d.update()
            plot2d_dmm.update()
    

        qt.msleep(0.003)
    stop = time()


    print 'Duration: %s sec' % (stop - start, )
    
    
    #Saving plot images
    plot2d.save_png(filepath = data.get_dir())
    plot2d.save_eps(filepath = data.get_dir())
    
    plot2d_dmm.save_png(filepath = data.get_dir())
    plot2d_dmm.save_eps(filepath = data.get_dir())
    
    # Saving UHFLI setting to the measurement data folder
    # You can load this settings file from UHFLI user interface 
    UHFLI_lib.UHF_save_settings(path = data_path)
    
    
    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()


# Run the measurement
run_IVG_both()
