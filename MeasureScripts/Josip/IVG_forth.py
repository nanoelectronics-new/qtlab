from numpy import pi, random, arange, size
from time import time,sleep



#####################################################
# EXAMPLE SCRIPT SHOWING HOW TO SET UP STANDARD 1D (IV) DMM MEASUREMENT
#####################################################
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)  # Initialize IVVI
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54505188::INSTR')  # Initialize dmm
#dmm.set_NPLC = 0.1  # Setting PLCs of dmm

gain = 1e8 # choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

bias = 36.7

# Sweeping vector
start = IVVI.get_dac5()
stop = 413.95
step = 0.06
v_vec = arange(start,stop,step)  #''' !! Take care about step sign '''

#mult_factor = 5



qt.mstart()


name = " IVG_13-10_G08_367uV_after_B_sweep"


data = qt.Data(name=name)  # Put one space before name


data.add_coordinate(' Voltage [mV]')     # Underline makes the next letter as index

data.add_value(' Current [pA]')          # Underline makes the next letter as index


data.create_file()


plot2d = qt.Plot2D(data, name=name, autoupdate=False)
plot2d.set_style('lines')





#if IVVI.get_dac5() > (v_vec[0] + step):
    #a = IVVI.get_dac5()
    #b = v_vec[0] + step
    #c = abs(step)*(-1)
    #v_zero = arange(a,b,c)

#if IVVI.get_dac5() < (v_vec[0] - step):
#    a = IVVI.get_dac5()
#    b = v_vec[0] - step
#    c = abs(step)
#    v_zero = arange(a,b,c)
#
#for i in v_zero:         #Sweep to the starting value
#    IVVI.set_dac5(i)
#    result = dmm.get_readval()/(gain)*1e12
#    qt.msleep(0.1)
#  
#
#print ("swept smoothly :-) b b")




IVVI.set_dac1(bias)

start = time()
try:
    for v in v_vec:
        # set the voltage
        IVVI.set_dac5(v)
        #IVVI.set_dac6(v)
        #IVVI.set_dac7(v)

        # readout
        result = dmm.get_readval()/(gain)*1e12

        #if result > 50:
            #raise Exception("Leak treshold reached") 

        # save the data point to the file, this will automatically trigger
        # the plot windows to update
        data.add_data_point(v, result)
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