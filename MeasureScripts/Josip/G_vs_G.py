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


file_name1 = ' GvsG_22-03-G04_G21'
file_name2 = ' GvsG_23-24-G21_G04'

gain = 1e9 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

#bias = 0


#gain_Lockin = 1 # Conversion factor for the Lockin


v1_vec = arange(0.0,1000.0,1)    #V_g1   outer loop  23-24
v2_vec = arange(-200.0,200.0,1)  #V_g2   inner loop  22-03



# you indicate that a measurement is about to start and other
# processes should stop (like batterycheckers, or temperature
# monitors)
qt.mstart()


data1 = qt.Data(name=file_name1)
data2 = qt.Data(name=file_name2)



data_temp1 = np.zeros((len(v2_vec)))
new_mat1 = np.zeros((len(v2_vec)))
data_temp2 = np.zeros((len(v2_vec)))
new_mat2 = np.zeros((len(v2_vec)))



data1.add_coordinate('V_{G2} [mV]')  #y inner
data1.add_coordinate('V_{G1} [mV]')   #x outer
data1.add_value('Current [pA]')

data2.add_coordinate('V_{G2} [mV]')  #y inner
data2.add_coordinate('V_{G1} [mV]')   #x outer
data2.add_value('Current [pA]')




data1.create_file()
data2.create_file()


plot2d1 = qt.Plot2D(data1, name='2D_22-03',autoupdate=False)
plot3d1 = qt.Plot3D(data1, name='GvsG_22-03', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly

plot2d2 = qt.Plot2D(data2, name='2D_23-24',autoupdate=False)
plot3d2 = qt.Plot3D(data2, name='GvsG_23-24', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly




#IVVI.set_dac1(bias)

raw_input("Set bias voltages and press Enter to continue...")

init_start = time()
vec_count = 0


try:
    for i,v1 in enumerate(v1_vec):  # CHANGE THIS LINE FOR MATRIX FILE SAVING
        
        
        start = time()
        # set the voltage
        IVVI.set_dac5(v1)
        


        for j,v2 in enumerate(v2_vec):  # CHANGE THIS LINE FOR MATRIX FILE SAVING

            IVVI.set_dac6(v2)

            # readout
            result1 = dmm03.get_readval()/gain*1e12
            result2 = dmm24.get_readval()/gain*1e12


            # Save to the matrix
            data_temp1[j] = result1
            data_temp2[j] = result2

            data1.add_data_point(v2, v1, result1) 
            data2.add_data_point(v2, v1, result2) 
            qt.msleep(0.005)
       
        data1.new_block()
        data2.new_block()
        stop = time()

        
        new_mat1 = np.column_stack((new_mat1, data_temp1))
        new_mat2 = np.column_stack((new_mat2, data_temp2))
        if not(i):
            new_mat1 = new_mat1[:,1:]
            new_mat2 = new_mat2[:,1:]

    
        plot2d1.update()
        plot3d1.update()
        plot2d2.update()
        plot3d2.update()
        
        # Saving the matrix to the matrix filedata.get_filepath
        np.savetxt(fname=data1.get_filepath() + "_matrix", X=new_mat1, fmt='%1.4e', delimiter=' ', newline='\n')   # ADD THIS LINE FOR MATRIX FILE SAVING
        np.savetxt(fname=data2.get_filepath() + "_matrix", X=new_mat2, fmt='%1.4e', delimiter=' ', newline='\n')   # ADD THIS LINE FOR MATRIX FILE SAVING

        vec_count = vec_count + 1
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(v1_vec.size - vec_count))))
        
    

    print 'Overall duration: %s sec' % (stop - init_start, )

finally:

    # after the measurement ends, you need to close the data file.
    data1.close_file()
    data2.close_file()
    #data_current.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()