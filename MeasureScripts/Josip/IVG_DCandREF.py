from numpy import pi, random, arange, size
from time import time,sleep
import UHFLI_lib




#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM3', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54502777::INSTR')
daq = UHFLI_lib.UHF_init_demod_multiple(demod_c = [1])  # Initialize UHF LI

gain = 1e9 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

bias = -200

leak_test = False

f1 = '277.70 MHz'
f2 = '340.40 MHz'

# Sweeping vector
v_vec = arange(152.80,0,-0.4)  ##''' !! Take care about step sign '''



qt.mstart()



data = qt.Data(name=' IVG_11-13_G18')  # Put one space before name





data.add_coordinate(' Voltage [mV]')   # Underline makes the next letter as index

data.add_value(' Current_[pA]')      # Underline makes the next letter as index


data.add_value(' Refl_voltage_%s [V]'%f1)
data.add_value(' Angle_%s [deg]'%f1)

data.add_value(' Refl_voltage_%s [V]'%f2)
data.add_value(' Angle_%s [deg]'%f2)



data.create_file()


data_path = data.get_dir() 



plot2d_current = qt.Plot2D(data, name=' current', coordim = 0, valdim = 1, autoupdate=False)

plot2d_refl_mag_f1 = qt.Plot2D(data, name=' Refl_voltage_%s [V]'%f1, coordim = 0, valdim = 2, autoupdate=False)
plot2d_refl_ph_f1 = qt.Plot2D(data, name=' Angle_%s [deg]'%f1, coordim = 0, valdim = 3, autoupdate=False)

plot2d_refl_mag_f2 = qt.Plot2D(data, name=' Refl_voltage_%s [V]'%f2, coordim = 0, valdim = 4, autoupdate=False)
plot2d_refl_ph_f2 = qt.Plot2D(data, name=' Angle_%s [deg]'%f2, coordim = 0, valdim = 5, autoupdate=False)



#plot2d_current.set_style('lines')




IVVI.set_dac1(bias)
daq.setInt('/dev2210/sigins/0/autorange', 1)  # Autoset amplification
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

        result_mag_f1 = result_refl[0,0] # Getting amplitude values from all three demodulators and summing them
        result_ph_f1 = result_refl[0,1]  # Getting phase values from all three demodulators and summing them
        
        result_mag_f2 = result_refl[1,0] # Getting amplitude values from all three demodulators and summing them
        result_ph_f2 = result_refl[1,1]  # Getting phase values from all three demodulators and summing them
       





     
        # save the data point to the file
        data.add_data_point(v,result_current, result_mag_f1, result_ph_f1, result_mag_f2, result_ph_f2)
   

        if leak_test: # If leak_test is True update every point
            plot2d_current.update()
            plot2d_refl_mag_f1.update()
            plot2d_refl_ph_f1.update()
            plot2d_refl_mag_f2.update()
            plot2d_refl_ph_f2.update() 
            # If leak_test is True update every point 
             # If leak_test is True update every point 
        elif not bool(mod(int(v),20)):  
            plot2d_current.update()
            plot2d_refl_mag_f1.update()
            plot2d_refl_ph_f1.update()
            plot2d_refl_mag_f2.update()
            plot2d_refl_ph_f2.update()  
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
    data.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
