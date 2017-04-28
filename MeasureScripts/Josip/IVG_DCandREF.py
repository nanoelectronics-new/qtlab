from numpy import pi, random, arange, size
from time import time,sleep
import UHFLI_lib




#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM3', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54502777::INSTR')
daq = UHFLI_lib.UHF_init_demod_multiple(demod_c = [3])  # Initialize UHF LI

gain = 1e8 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

bias = -200

leak_test = True



# Sweeping vector
v_vec = arange(57.60,300,0.4)  ##''' !! Take care about step sign '''



qt.mstart()



data_refl_mag = qt.Data(name=' IVG_23-03_G24_refl_mag')  # Put one space before name
data_refl_ph = qt.Data(name=' IVG_23-03_G24_refl_ph')  # Put one space before name
data_current = qt.Data(name=' IVG_23-03_G24_current')  # Put one space before name




data_refl_mag.add_coordinate(' Voltage [mV]')   # Underline makes the next letter as index

data_refl_mag.add_value(' Voltage [V]')      # Underline makes the next letter as index

data_refl_ph.add_coordinate(' Voltage [mV]')   # Underline makes the next letter as index

data_refl_ph.add_value(' Angle [deg]')      # Underline makes the next letter as index

data_current.add_coordinate(' Voltage [mV]')   # Underline makes the next letter as index

data_current.add_value(' Current [pA]')      # Underline makes the next letter as index


data_refl_ph.create_file()
data_current.create_file()

data_path = data_refl_mag.get_dir() 


next = 0 
next = next + 1 
plot2d_refl_mag = qt.Plot2D(data_refl_mag, name='refl_mag_%d'%next, autoupdate=False)
plot2d_refl_mag.set_style('lines')

plot2d_refl_ph = qt.Plot2D(data_refl_ph, name='refl_ph_%d'%next, autoupdate=False)
plot2d_refl_ph.set_style('lines')

plot2d_current = qt.Plot2D(data_current, name='current_%d'%next, autoupdate=False)
plot2d_current.set_style('lines')




IVVI.set_dac1(bias)
sleep(1)

start = time()
try:
    for v in v_vec:
        # set the voltage
        #IVVI.set_dac5(v)
        IVVI.set_dac6(v)

        result_current = dmm.get_readval()/gain*1e12
        if v < 0 and result < -200:  # leak protection
            print "break 1"
            break

        if v > 0 and result > 200:   # leak protection
            print "break 2"
            break

        result_refl = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 3)  # Reading the lockin
        result_refl = array(result_refl)

        #result_ph = sum(result_refl[:,1])  # Getting phase values from all three demodulators and summing them
        #result_mag = sum(result_refl[:,0]) # Getting amolitude values from all three demodulators and summing them
        result_ph = sum(result_refl[:,1])  # Getting phase values from all three demodulators and summing them
        result_mag = sum(result_refl[:,0]) # Getting amolitude values from all three demodulators and summing them
     
        # save the data point to the file
        data_refl_mag.add_data_point(v, result_mag) 
        data_refl_ph.add_data_point(v, result_ph)
        data_current.add_data_point(v, result_current) 

        if leak_test:
            plot2d_current.update()
            plot2d_refl_mag.update()   # If leak_test is True update every point 
            plot2d_refl_ph.update()   # If leak_test is True update every point 
        elif not bool(mod(v,50)):  
            plot2d_current.update()  
            plot2d_refl_mag.update()   # Update every 10 points
            plot2d_refl_ph.update()   # If leak_test is True update every point
        # the next function is necessary to keep the gui responsive. It
        # checks for instance if the 'stop' button is pushed. It also checks
        # if the plots need updating.
        qt.msleep(0.001)

finally:
    stop = time()
    print 'Duration: %s sec' % (stop - start, )

    # Saving UHFLI setting to the measurement data folder
    # You can load this settings file from UHFLI user interface 
    UHFLI_lib.UHF_save_settings(path = data_path)


    # after the measurement ends, you need to close the data file.
    data_refl_mag.close_file()
    data_refl_ph.close_file()
    data_current.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
