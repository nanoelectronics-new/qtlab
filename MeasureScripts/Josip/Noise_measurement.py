from numpy import pi, random, arange, size, mod
from time import time,sleep
import UHFLI_lib
from scipy import signal
import matplotlib.pyplot as plt

#####################################################
# this part is to simulate some data, you can skip it
#####################################################




#####################################################
# here is where the actual measurement program starts
#####################################################

reload(UHFLI_lib)
daq, scopeModule = UHFLI_lib.UHF_init_scope_module(device_id = 'dev2148',  mode = 3)  # Initialize UHF LI, set the mode to get the FFT data

UHFLI_lib.UHF_init_scope()  # Initialize UHF LI
gain = 1e9 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

frequency = 5.8e9   # in GHz

qt.mstart()


data = qt.Data(name='IV 651_test')

 
new_mat  = list()   # Creating empty matrix for storing all data 


#data.add_coordinate('Voltage [mV]')
#data.add_value('UHFLI data [arb.u.]')
data.create_file()


#plot2d = qt.Plot2D(data, name='plot101', autoupdate=False)
#plot2d.set_style('lines')

# Set the VSG power units
VSG.set_power_units("dbm") 
# Set the RF power
VSG.set_power(power)
# Turn the RF on
VSG.set_status("on") 
# Set the RF frequency
VSG.set_frequency(freq)


for i in xrange(10):  # Collect the trace 10 times

    result_lockin = UHFLI_lib.get_scope_record(daq = daq, scopeModule = scopeModule)
    result_lockin = result_lockin[0] # *(1e12/gain)**2  # Converting to pA - squared because of the power spectral density
    new_mat.append(result_lockin)   # The trace is saved as a new row 

    np.savetxt(fname = data.get_dir() + "/Power_spectral_density.dat", X = new_mat, fmt = '%1.4e', delimiter = '  ', newline = '\n')


    plt.plot()
    plt.xlabel('frequency [Hz]')
    plt.ylabel('PSD [V**2/Hz]')
    plt.show()
    qt.msleep(0.010)


# after the measurement ends, you need to close the data file.
data.close_file()
# lastly tell the secondary processes (if any) that they are allowed to start again.
qt.mend()
