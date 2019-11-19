from numpy import pi, random, arange, size
import numpy as np
from time import time,sleep
import matplotlib.pyplot as plt


#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54505177::INSTR') 



def run_IV():
    ''' 
    Just to run the code below in the separate function
    not to polute common memory space'''

    global name_counter
    name_counter +=1
    gain = 1e9 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    
    
    v_vec = arange(0.0,-2000.0,-5.0)   
    

    div = 1.0
    
    
    qt.mstart()
    name = 'Leak_check_2to21_%d'%name_counter
    data = qt.Data(name=name)
    
    
    data.add_coordinate('Voltage [mV]')
    data.add_value('Current [pA]')
    
    
    data.create_file()
    
    
    plot2d = qt.Plot2D(data, name=name, autoupdate=False)
    plot2d.set_style('lines')
    
    
    
    
    
    try:
        start = time()
        for v in v_vec:
    
        
            IVVI.set_dac7(v/div)

    
            result = dmm._ins.get_readval()/(gain)*1e12 
            #if abs(result) > 100.0:
                #raise Exception("LEAK")
        
            data.add_data_point(v, result)
        

            plot2d.update()  

        
            qt.msleep(0.003)
        stop = time()
        print 'Duration: %s sec' % (stop - start, )
    
    
    
    finally:
        #IVVI.set_dac5(0.0)
        #Saving plot images
        plot2d.save_png(filepath = data.get_dir())
        plot2d.save_eps(filepath = data.get_dir())
    
        
        
        
        data.close_file()
        qt.mend()


#Run the measurement
run_IV()



def run_line_scan():
    ''' 
    Just to run the code below in the separate function
    not to polute common memory space'''

    gain = 1e9 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
    
    
    v_vec = arange(-495.0,-488.0,0.06)   

    div = 1.0
    
    result = np.array([])
    qt.mstart()
    
 
    
    for v in v_vec:  
        IVVI.set_dac1(v/div)
        res = dmm._ins.get_readval()/(gain)*1e12
        result = np.append(result, res) 
        qt.msleep(0.003)

    qt.mend()
    #plt.plot(v_vec, result)
    #plt.xlabel('Gate 6 [mV]')
    #plt.ylabel('Current [pA]')
    #plt.show()
    return result, v_vec

   