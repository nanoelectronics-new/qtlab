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
daq = UHFLI_lib.UHF_init_demod_multiple(device_id = 'dev2169', demod_c = [3])


bias = 0.0

leak_test = False
gate2div = 100.0

v_vec = arange(3.0,4.0,0.005)   





qt.mstart()

data = qt.Data(name=' IVG_1-3_V_G24=16,1mV_VG2_swept')



data.add_coordinate('Voltage [mV]')

data.add_value('Refl phase [deg]')


data.create_file()


plot2d = qt.Plot2D(data, name='plot_phas', autoupdate=False)
plot2d.set_style('lines')




IVVI.set_dac1(bias)


start = time()
daq.setInt('/dev2169/sigins/0/autorange', 1)  # Autoset amplification
for v in v_vec:

    IVVI.set_dac2(v*gate2div)

    result = UHFLI_lib.UHF_measure_demod_multiple(Num_of_TC = 3)  # Reading the lockin
    result_refl = array(result_refl)
    result_phase = result_refl[0,1]  # Getting phase values 
   


    data.add_data_point(v, result)

    if leak_test:
        plot2d.update()   # If leak_test is True update every point 
    elif not bool(mod(v,2)):    
        plot2d.update()   # Update every 10 points


    qt.msleep(0.005)
stop = time()
print 'Duration: %s sec' % (stop - start, )


settings_path = data_mag.get_dir()
UHFLI_lib.UHF_save_settings(daq, path = settings_path)

data.close_file()
qt.mend()
