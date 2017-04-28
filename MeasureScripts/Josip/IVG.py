from numpy import pi, random, arange, size, mod
from time import time,sleep

#####################################################
# this part is to simulate some data, you can skip it
#####################################################




#####################################################
# here is where the actual measurement program starts
#####################################################

#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM3', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54502777::INSTR')
#stop = 0
#while True:
    
    #while True:  # Wait five minutes
        #count_time = time()
        #if abs(count_time - stop) > 300:
            #break


gain = 1e8 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

bias = -200

gate = 1000

leak_test = True

          
v_vec = arange(0,2000,0.4)

name = ' IVG_23-03_G24(dac6)'

          
qt.mstart()

          
data = qt.Data(name=name)
#data = qt.Data(name='test')


          
data.add_coordinate('Voltage [mV]')

data.add_value('Current [pA]')

          
data.create_file()

      
plot2d = qt.Plot2D(data, name=name, autoupdate=False)
plot2d.set_style('lines')




IVVI.set_dac1(bias)
sleep(1)


start = time()
for v in v_vec:

    
    #IVVI.set_dac5(v)
    IVVI.set_dac6(v)
    #IVVI.set_dac7(v)
    # readout
    result = dmm._ins.get_readval()/(gain)*1e12 
 
    if v < 0 and result < -200:  # leak protection
        print "break 1"
        break

    if v > 0 and result > 200:   # leak protection
        print "break 2"
        break
    
    data.add_data_point(v, result)

    if leak_test:
        plot2d.update()   # If leak_test is True update every point 
    elif not bool(mod(v,20)):    
        plot2d.update()   # Update every 10 points

    

  
    qt.msleep(0.001) 
stop = time()
print 'Duration: %s sec' % (stop - start, )




# after the measurement ends, you need to close the data file.
data.close_file()
# lastly tell the secondary processes (if any) that they are allowed to start again.
qt.mend()
