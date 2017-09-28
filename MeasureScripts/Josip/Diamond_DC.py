from numpy import pi, random, arange, size
from time import time,sleep
import datetime
import convert_for_diamond_plot as cnv

#####################################################
# added automatic conversion to matrix file
#####################################################




#####################################################
# here is where the actual measurement program starts
#####################################################
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x0957::0x0607::MY53003401::INSTR')
#dmm.set_NPLC = 1  # Setting PLCs of dmm


file_name = 'Diamond_07-08_G09_2'

gain = 1e9 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

#bias =0


#gain_Lockin = 1 # Conversion factor for the Lockin


v1_vec = arange(0.0,-1000,-0.5)     #V_g
v2_vec = arange(-500.0,500.0,2.0)  #V_sd 



# you indicate that a measurement is about to start and other
# processes should stop (like batterycheckers, or temperature
# monitors)
qt.mstart()


data = qt.Data(name=file_name)


data_temp = np.zeros((len(v2_vec)))
new_mat = np.zeros((len(v2_vec)))


data.add_coordinate('V_{SD} [mV]')  #v2
data.add_coordinate('V_{G} [mV]')   #v1
data.add_value('Current [pA]')


data.create_file()

data_path = data.get_dir()


plot2d = qt.Plot2D(data, name='measure2D',autoupdate=False)
plot3d = qt.Plot3D(data, name='measure3D', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly




#IVVI.set_dac1(bias)

init_start = time()
vec_count = 0


try:
    for i,v1 in enumerate(v1_vec):  # CHANGE THIS LINE FOR MATRIX FILE SAVING
        
        
        start = time()
        # set the voltage
        IVVI.set_dac5(v1)
        


        for j,v2 in enumerate(v2_vec):  # CHANGE THIS LINE FOR MATRIX FILE SAVING

            IVVI.set_dac1(v2)

            # readout
            result = dmm03.get_readval()/gain*1e12


            # Save to the matrix
            data_temp[j] = result

            data.add_data_point(v2, v1, result) 
            qt.msleep(0.005)
       
        data.new_block()
        stop = time()

        
        new_mat = np.column_stack((new_mat, data_temp))
        if not(i):
            new_mat = new_mat[:,1:]
        


        plot2d.update()

        plot3d.update()

        # Saving the matrix to the matrix filedata.get_filepath
        np.savetxt(fname=data.get_filepath() + "_matrix", X=new_mat, fmt='%1.4e', delimiter=' ', newline='\n')   # ADD THIS LINE FOR MATRIX FILE SAVING

        vec_count = vec_count + 1
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(v1_vec.size - vec_count))))
        
    

    print 'Overall duration: %s sec' % (stop - init_start, )

finally:

    # after the measurement ends, you need to close the data file.
    data.close_file()
    #data_current.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()