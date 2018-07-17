from numpy import pi, random, arange, size
from time import time,sleep

# ANDREA


#####################################################
# EXAMPLE SCRIPT SHOWING HOW TO SET UP STANDARD 1D (IV) DMM MEASUREMENT
#####################################################
# IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'NEG', 'BIP', 'BIP'], numdacs=16)  # Initialize IVVI
# dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54505188::INSTR')  # Initialize dmm
# dmm.set_NPLC = 0.1  # Setting PLCs of dmm
# name = "001_Initialize"

# gain = 100e6 # choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G
gain = 100e6
# gain2 = 100e6 # choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

# div_sweep = 0.01 # 0.01 for 10mV / V ; 0.1 for 100mV / V
div_sweep = 1.0 # 5.0 for amplification 5x

# Sweeping vector
v_start = 0/div_sweep
v_stop = -4000/div_sweep
v_step = -2/div_sweep

v_sweep = arange(v_start, v_stop+v_step, v_step)  #''' !! Take care about step sign '''

# stepping voltage
div_bias = 0.01 # 0.01 for 10mV / V
# div_bias = 1.0 # 5 for 5V / V
v_bias = 0.05/div_bias

div_gate = 1.0
v_gate = 0/div_gate

qt.mstart()

name = "005_sweep21_set20_meas19_open-rest"
# name = "test_2values"

data = qt.Data(name=name)  # Put one space before name
data2 = qt.Data(name="current")  # Put one space before name

data.add_coordinate(' Voltage [mV]')     # Underline makes the next letter as index
# data.add_coordinate(' Time [Step]')

data.add_value(' Current [pA]')          # Underline makes the next letter as index

data.create_file()

plot2d = qt.Plot2D(data, name=name, autoupdate=False, style='lines')

IVVI.set_dac1(v_bias)
# IVVI.set_dac2(v_gate)

start = time()
try:
    for v in v_sweep:
        # set the voltage
        IVVI.set_dac5(v)

        # result = dmm.get_readval()/(gain)*1e6+22.5 # voltage in uV; gain is amplification 
        result = dmm.get_readval()/(gain)*1e12 # current in pA; gain feedback resistance

        #if result < -50:
            #raise Exception("Leak treshold reached") 

        # save the data point to the file, this will automatically trigger
        # the plot windows to update
        data.add_data_point(v*div_sweep,result)
        plot2d.update()

        # the next function is necessary to keep the gui responsive. It
        # checks for instance if the 'stop' button is pushed. It also checks
        # if the plots need updating.
        qt.msleep(0.0001)

finally:
    stop = time()
    print 'Duration: %s sec' % (stop - start, )
    #IVVI.set_dac1(0.0)


       


    # after the measurement ends, you need to close the data file.
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
