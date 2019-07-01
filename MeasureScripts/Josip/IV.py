from numpy import pi, random, arange, size
from time import time,sleep


#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54505177::INSTR') 



def run_IV():
    ''' 
    Just to run the code below in the separate function
    not to polute common memory space'''

    global name_counter
    name_counter +=1
    gain = 1e7 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    
    
    v_vec = arange(-10.0,10.0,0.2)   
    

    div = 100.0
    
    
    qt.mstart()
    name = 'Leak_test_13_to_10_%d'%name_counter
    data = qt.Data(name=name)
    
    
    data.add_coordinate('Voltage [mV]')
    data.add_value('Current [pA]')
    
    
    data.create_file()
    
    
    plot2d = qt.Plot2D(data, name=name, autoupdate=False)
    plot2d.set_style('lines')
    
    
    
    
    
    try:
        start = time()
        for v in v_vec:
    
        
            IVVI.set_dac1(v*div)

    
            result = dmm._ins.get_readval()/(gain)*1e12 
            #if abs(result) > 50.0:
             #   raise Exception("LEAK")
        
            data.add_data_point(v, result)
        

            plot2d.update()  

        
            qt.msleep(0.003)
        stop = time()
        print 'Duration: %s sec' % (stop - start, )
    
    
    
    finally:
        IVVI.set_dac1(0.0)
        #Saving plot images
        plot2d.save_png(filepath = data.get_dir())
        plot2d.save_eps(filepath = data.get_dir())
    
        
        
        
        data.close_file()
        qt.mend()


#Run the measurement
run_IV()
    