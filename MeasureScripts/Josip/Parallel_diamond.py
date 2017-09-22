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


file_name1 = ' Diamond_13-10-G08'
file_name2 = ' Diamond_12-11-G23'

gain = 1e8 #Choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G

#bias =0


#gain_Lockin = 1 # Conversion factor for the Lockin


v_gate_13_10 = arange(400.0,1200.0,0.5)    #V_g1   outer loop
v_gate_12_11 = arange(-400.0,400.0,0.5)    #V_g1   outer loop

v_bias_13_10 = arange(-300.0,300.0,1.0)  #V_g2   inner loop 
v_bias_12_11 = arange(-600.0,600.0,2.0)  #V_g2   inner loop 

if (len(v_bias_13_10) != len(v_bias_12_11)) or (len(v_gate_13_10) != len(v_gate_12_11)):
    raise Exception(" biiiip +/@>?[@]{8&%&(^*@)} Corresponding vectors must be the same length! ")

# you indicate that a measurement is about to start and other
# processes should stop (like batterycheckers, or temperature
# monitors)
qt.mstart()


data_13_10 = qt.Data(name=file_name1)
data_12_11 = qt.Data(name=file_name2)



data_temp_13_10 = np.zeros((len(v_bias_13_10)))
new_mat_13_10 = np.zeros((len(v_bias_13_10)))
data_temp_12_11 = np.zeros((len(v_bias_12_11)))
new_mat_12_11 = np.zeros((len(v_bias_12_11)))



data_13_10.add_coordinate('V_{SD} [mV]')  #v_bias_13_10    inner
data_13_10.add_coordinate('V_{G} [mV]')   #v_gate_13_10    outer
data_13_10.add_value('Current [pA]')

data_12_11.add_coordinate('V_{SD} [mV]')  
data_12_11.add_coordinate('V_{G} [mV]')   
data_12_11.add_value('Current [pA]')




data_13_10.create_file()
data_12_11.create_file()


plot2d_13_10 = qt.Plot2D(data_13_10, name='2D_13_10',autoupdate=False)
plot3d_13_10 = qt.Plot3D(data_13_10, name='Diamond_13_10', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly

plot2d_12_11 = qt.Plot2D(data_12_11, name='2D_12_11',autoupdate=False)
plot3d_12_11 = qt.Plot3D(data_12_11, name='Diamond_12_11', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly







init_start = time()
vec_count = 0


try:
    for i,v1 in enumerate(v_gate_13_10):  # CHANGE THIS LINE FOR MATRIX FILE SAVING
        
        
        start = time()
        # set the voltage
        IVVI.set_dac5(v_gate_13_10[i])  # 13_10
        IVVI.set_dac6(v_gate_12_11[i])
        


        for j,v2 in enumerate(v_bias_13_10):  # CHANGE THIS LINE FOR MATRIX FILE SAVING

            IVVI.set_dac1(v_bias_13_10[j])  # 13_10
            IVVI.set_dac2(v_bias_12_11[j])

            # readout
            result_13_10 = dmm2.get_readval()/gain*1e12
            result_12_11 = dmm.get_readval()/gain*1e12


            # Save to the matrix
            data_temp_13_10[j] = result_13_10
            data_temp_12_11[j] = result_12_11

            data_13_10.add_data_point(v_bias_13_10[j], v_gate_13_10[i], result_13_10) 
            data_12_11.add_data_point(v_bias_12_11[j], v_gate_12_11[i], result_12_11) 
            qt.msleep(0.005)
       
        data_13_10.new_block()
        data_12_11.new_block()
        stop = time()

        
        new_mat_13_10 = np.column_stack((new_mat_13_10, data_temp_13_10))
        new_mat_12_11 = np.column_stack((new_mat_12_11, data_temp_12_11))
        if not(i):
            new_mat_13_10 = new_mat_13_10[:,1:]
            new_mat_12_11 = new_mat_12_11[:,1:]

    
        plot2d_13_10.update()
        plot3d_13_10.update()
        plot2d_12_11.update()
        plot3d_12_11.update()
        
        # Saving the matrix to the matrix filedata.get_filepath
        np.savetxt(fname=data_13_10.get_filepath() + "_matrix", X=new_mat_13_10, fmt='%1.4e', delimiter=' ', newline='\n')   # ADD THIS LINE FOR MATRIX FILE SAVING
        np.savetxt(fname=data_12_11.get_filepath() + "_matrix", X=new_mat_12_11, fmt='%1.4e', delimiter=' ', newline='\n')   # ADD THIS LINE FOR MATRIX FILE SAVING

        vec_count = vec_count + 1
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(v_gate_13_10.size - vec_count))))
        
    

    print 'Overall duration: %s sec' % (stop - init_start, )

finally:

    # after the measurement ends, you need to close the data file.
    data_13_10.close_file()
    data_12_11.close_file()
    #data_current.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()