from numpy import pi, random, arange, size
from time import time,sleep



#####################################################
# EXAMPLE SCRIPT SHOWING HOW TO SET UP STANDARD 1D (IV) DMM MEASUREMENT
#####################################################
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)  # Initialize IVVI
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54505188::INSTR')  # Initialize dmm
#dmm.set_NPLC = 0.1  # Setting PLCs of dmm

gain = 1e9 # hoose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

div_factor = 0.2

bias = 500

# Sweeping vector
v_vec = arange(-263.00,0.0,1.0)  #''' !! Take care about step sign '''


qt.mstart()


name = " leak_check_21-23_back"


data = qt.Data(name=name)  # Put one space before name






data.add_coordinate(' Voltage [mV]')     # Underline makes the next letter as index

data.add_value(' Current [pA]')          # Underline makes the next letter as index


data.create_file()


plot2d = qt.Plot2D(data, name=name, autoupdate=False)
plot2d.set_style('lines')



#IVVI.set_dac1(bias)

start = time()
try:
    for v in v_vec:
        # set the voltage
        IVVI.set_dac5(v)
        #IVVI.set_dac6(v)
        #IVVI.set_dac7(v)

        # readout
        result = dmm.get_readval()/(gain)*1e12

        #if abs(result) > 50:
            #raise Exception("Leak treshold reached") 

        # save the data point to the file, this will automatically trigger
        # the plot windows to update
        data.add_data_point(v/div_factor, result)
        plot2d.update()
        # the next function is necessary to keep the gui responsive. It
        # checks for instance if the 'stop' button is pushed. It also checks
        # if the plots need updating.
        qt.msleep(0.005)

finally:
    stop = time()
    print 'Duration: %s sec' % (stop - start, )


       


    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
