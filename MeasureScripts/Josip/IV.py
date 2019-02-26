from numpy import pi, random, arange, size
from time import time,sleep


#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54505177::INSTR') 

name_counter +=1

def run_IV():
    ''' 
    Just to run the code below in the separate function
    not to polute common memory space'''

    gain = 1e9 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    
    
    v_vec = arange(0.0,-2000.0,-1.0)   
    
    div = 1.0
    
    
    
    qt.mstart()
    name = ' 8-10 IV %d_leak_check_11_to_9'%name_counter
    data = qt.Data(name=name)
    
    
    
    data.add_coordinate('Voltage [mV]')
    
    data.add_value('Current [pA]')
    
    
    data.create_file()
    
    
    plot2d = qt.Plot2D(data, name=name, autoupdate=False)
    plot2d.set_style('lines')
    
    
    

    
    try:
        start = time()
        for v in v_vec:
    
    
            IVVI.set_dac5(v*div)

    
            result = dmm._ins.get_readval()/(gain)*1e12 
        
            data.add_data_point(v, result)
        

            plot2d.update()  
        
        
            qt.msleep(0.003)
        stop = time()
        print 'Duration: %s sec' % (stop - start, )
    
    
    
    finally:
        IVVI.set_dac5(0.0)
        #Saving plot images
        plot2d.save_png(filepath = data.get_dir())
        plot2d.save_eps(filepath = data.get_dir())
    
        
        
        
        data.close_file()
        qt.mend()


#Run the measurement
run_IV()
    