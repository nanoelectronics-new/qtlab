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


UHFLI_lib.UHF_init_scope()  # Initialize UHF LI
gain = 1e9 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G




qt.mstart()


data = qt.Data(name='IV 628')

new_mat = list() # Creating empty matrix for storing all data 
new_mat_FD  = list()  


#data.add_coordinate('Voltage [mV]')
#data.add_value('UHFLI data [arb.u.]')
data.create_file()


#plot2d = qt.Plot2D(data, name='plot101', autoupdate=False)
#plot2d.set_style('lines')




for i in xrange(10):  # Collect the trace 10 times

    result_lockin = UHFLI_lib.UHF_measure_scope_single_shot(maxtime = 12)
    result_lockin = result_lockin[0]/gain*1e12
    new_mat.append(result_lockin)   # The trace is saved as a new row 
    #data.add_data_point(np.linspace(1, result_lockin.size, result_lockin.size), result_lockin)  # Adding new data point

    np.savetxt(fname = data.get_dir() + "/Time_domain_off_peak.dat", X = new_mat, fmt = '%1.4e', delimiter = '  ', newline = '\n')
    #plot2d.update()

    ## Calculating and ploting the power spectral density
    f, Pxx_den = signal.periodogram(result_lockin, fs = 27.5e3, window = 'hamming', nfft = 274657)
    #plt.semilogy(f, Pxx_den)
    new_mat_FD.append(f)
    new_mat_FD.append(Pxx_den)
    np.savetxt(fname = data.get_dir() + "/Freq_domain_off_peak.dat", X = new_mat_FD, fmt = '%1.4e', delimiter = '  ', newline = '\n')

#plt.xlabel('frequency [Hz]')
#plt.ylabel('PSD [V**2/Hz]')
#plt.show()



qt.msleep(0.003)



   


# after the measurement ends, you need to close the data file.
data.close_file()
# lastly tell the secondary processes (if any) that they are allowed to start again.
qt.mend()
