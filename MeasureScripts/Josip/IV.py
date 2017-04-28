from numpy import pi, random, arange, size
from time import time,sleep




#####################################################
# EXAMPLE SCRIPT SHOWING HOW TO SET UP STANDARD 1D (IV) DMM MEASUREMENT
#####################################################
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)  # Initialize IVVI
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x0957::0x0607::MY53003401::INSTR')  # Initialize dmm
#dmm.set_NPLC = 0.1  # Setting PLCs of dmm

gain = 10e6 # hoose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

#bias = 500

# Sweeping vector
v_vec = arange(-1000,1000,20)  #''' !! Take care about step sign '''

name = ' IV_08-10'

qt.mstart()



data = qt.Data(name=name)  # Put one space before name




data.add_coordinate(' Voltage [mV]')     # Underline makes the next letter as index

data.add_value(' Current [pA]')          # Underline makes the next letter as index


data.create_file()


plot2d = qt.Plot2D(data, name=name, autoupdate=False)
plot2d.set_style('lines')



start = time()
for v in v_vec:
    
    IVVI.set_dac1(v)

    # readout
    result = dmm._ins.get_readval()/(gain)*1e12

 
    data.add_data_point(v, result)
    plot2d.update()
   
    qt.msleep(0.001)
stop = time()
print 'Duration: %s sec' % (stop - start, )



# after the measurement ends, you need to close the data file.
data.close_file()
# lastly tell the secondary processes (if any) that they are allowed to start again.
qt.mend()
