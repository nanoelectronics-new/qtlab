from numpy import pi, random, arange, size, mod
from time import time,sleep
import UHFLI_lib

#####################################################
# this part is to simulate some data, you can skip it
#####################################################




#####################################################
# here is where the actual measurement program starts
#####################################################

#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54505177::INSTR') 

gain = 1e7 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

bias = 200.0

leak_test = True


v_vec = arange(-50.0,50.0,1.0)   

divgate = 10.0



qt.mstart()

data = qt.Data(name=' IV_13-16')



data.add_coordinate('Voltage [mV]')

data.add_value('Current [pA]')


data.create_file()


plot2d = qt.Plot2D(data, name='plot_tolp', autoupdate=False)
plot2d.set_style('lines')




#IVVI.set_dac1(bias)

try:
	start = time()
	for v in v_vec:
	
	    #IVVI.set_dac6(v*divgate)
	    IVVI.set_dac1(v*divgate)

	    #if abs(result) > 30:
			#raise Exception("LEAK\n")
	
	    result = dmm._ins.get_readval()/(gain)*1e12 
	   

	
	    data.add_data_point(v, result)
	

	    if leak_test:
	        plot2d.update()   # If leak_test is True update every point 
	    elif not bool(mod(v,10)):    
	        plot2d.update()   # Update every 10 points
	
	
	    qt.msleep(0.005)
	stop = time()
	print 'Duration: %s sec' % (stop - start, )



finally:
	#IVVI.set_dac1(0.0)
	#Saving plot images
	plot2d.save_png(filepath = data.get_dir())
	plot2d.save_eps(filepath = data.get_dir())

	
	
	
	data.close_file()
	qt.mend()
