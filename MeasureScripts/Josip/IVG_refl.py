from numpy import pi, random, arange, size, mod
from time import time,sleep
import UHFLI_lib

#####################################################
# this part is to simulate some data, you can skip it
#####################################################


def run_IVG():
    ''' 
    Just to run the code below in the separate function
    not to polute common memory space'''

    #####################################################
    # here is where the actual measurement program starts
    #####################################################
    
    #IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)
    #dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54505177::INSTR') 
    daq = UHFLI_lib.UHF_init_demod_multiple(device_id = 'dev2169', demod_c = [3])
    
    
    bias = 100.0
    
    leak_test = True
    gate2div = 1.0
    
    v_vec = arange(100.0,-200.0,-0.2)   
    
    
    
    
    
    qt.mstart()
    
    data = qt.Data(name=' 1-3 IV 8')
    
    
    
    data.add_coordinate('Voltage [mV]')
    
    data.add_value('Refl phase [deg]')
    
    
    data.create_file()
    
    
    plot2d = qt.Plot2D(data, name='plot_phas', autoupdate=False)
    plot2d.set_style('lines')
    
    
    
    
    IVVI.set_dac1(bias)
    
    
    start = time()
    daq.setInt('/dev2169/sigins/0/autorange', 1)  # Autoset amplification
    try:
        for v in v_vec:
        
            IVVI.set_dac5(v*gate2div)
            IVVI.set_dac6(v*gate2div)
        
            result = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 3)  # Reading the lockin
            result_refl = array(result)
            result_phase = result_refl[0,1]  # Getting phase values 
           
        
        
            data.add_data_point(v, result_phase)
        
            if leak_test:
                plot2d.update()   # If leak_test is True update every point 
            elif not bool(mod(v,2)):    
                plot2d.update()   # Update every 10 points
        
        
            qt.msleep(0.005)
        stop = time()
        print 'Duration: %s sec' % (stop - start, )
    
    finally:
        settings_path = data.get_dir()
        UHFLI_lib.UHF_save_settings(daq, path = settings_path)
        #Saving plot images
        plot2d.save_png(filepath = data.get_dir())
        plot2d.save_eps(filepath = data.get_dir())
        
        data.close_file()
        qt.mend()


# Run the above function
run_IVG()