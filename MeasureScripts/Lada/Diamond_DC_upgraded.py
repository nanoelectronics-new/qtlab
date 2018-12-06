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
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM5', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54505177::INSTR')
#dmm.set_NPLC = 1  # Setting PLCs of dmm


file_name = ' zoomin diamond 13-14 30mK'

gain = 1e9 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

#bias =0


#gain_Lockin = 1 # Conversion factor for the Lockin


v1_vec = arange(-650.0,-400.0,1.0)     #V_g
v2_vec = arange(-600.0,600.5,0.5)  #V_sd 



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


plot2d = qt.Plot2D(data, name='ivs',autoupdate=False)
plot3d = qt.Plot3D(data, name='dia3', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly




#IVVI.set_dac1(bias)

init_start = time()
vec_count = 0


try:
    for i,v1 in enumerate(v1_vec):  # CHANGE THIS LINE FOR MATRIX FILE SAVING
        
        
        start = time()
        # set the voltage
        IVVI.set_dac4(v1)
        


        for j,v2 in enumerate(v2_vec):  # CHANGE THIS LINE FOR MATRIX FILE SAVING

            IVVI.set_dac2(v2)

            # readout
            result = dmm.get_readval()/gain*1e12


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