from numpy import pi, random, arange, size
from time import time,sleep



#####################################################
# EXAMPLE SCRIPT SHOWING HOW TO SET UP STANDARD 1D (IV) DMM MEASUREMENT
#####################################################
#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'BIP', 'BIP', 'BIP'], numdacs=16)  # Initialize IVVI
#dmm = qt.instruments.create('dmm','a34410a', address = 'USB0::0x2A8D::0x0101::MY54505188::INSTR')  # Initialize dmm
#dmm.set_NPLC = 0.1  # Setting PLCs of dmm
file_name = 'test'
gain = 1e9 # choose between: 1e6 for 1M, 10e6 for 10M, 100e6 for 100M and 1e9 for 1G




v1_vec = arange(-200,200,50) #V_sd
v2_vec = arange(-50,50,2)   #V_g


qt.mstart()


data = qt.Data(name=file_name)

#saving directly in matrix format for diamond program
new_mat = np.zeros((len(v2_vec), len(v1_vec))) # Creating empty matrix for storing all data   - ADD THIS LINE FOR MATRIX FILE SAVING, PUT APPROPRIATE VECTOR NAMES


data.add_coordinate('V_{G} [mV]')  #v2
data.add_coordinate('V_{SD} [mV]')   #v1
data.add_value('Current [pA]')


data.create_file()

data_path = data.get_dir()


plot2d = qt.Plot2D(data, name='measure2D_2',autoupdate=False)
plot3d = qt.Plot3D(data, name='measure3D_2', coorddims=(1,0), valdim=2, style='image') #flipped coordims that it plots correctly





try:
    step = abs(v2_vec[0]) - abs(v2_vec[1])
    for i,v1 in enumerate(v1_vec):  # CHANGE THIS LINE FOR MATRIX FILE SAVING

        if IVVI.get_dac5() > (v2_vec[0] + step):
            a = IVVI.get_dac5()
            b = v2_vec[0] + step
            c = abs(step)*(-1)
            v_zero = arange(a,b,c)
        
        if IVVI.get_dac5() < (v2_vec[0] - step):
            a = IVVI.get_dac5()
            b = v2_vec[0] - step
            c = abs(step)
            v_zero = arange(a,b,c)
    
        for i in v_zero:         #Sweep to the starting value
            IVVI.set_dac5(i)
            result = dmm.get_readval()/(gain)*1e12
            qt.msleep(0.1)


        

        print ("swept smoothly :-) b b")
        
        
        start = time()
        # set the bias
        IVVI.set_dac1(v1)


        for j,v2 in enumerate(v2_vec):  # CHANGE THIS LINE FOR MATRIX FILE SAVING

            IVVI.set_dac5(v2)

            # readout
            result = dmm.get_readval()/gain*1e12

            # Save to the matrix
            new_mat[j,i] = result   # ADD THIS LINE FOR MATRIX FILE SAVING

            data.add_data_point(v2, v1, result) 
            qt.msleep(0.001)
       
        data.new_block()
        stop = time()
        

        plot2d.update()

        plot3d.update()

        vec_count = vec_count + 1
        print 'Estimated time left: %s hours\n' % str(datetime.timedelta(seconds=int((stop - start)*(v1_vec.size - vec_count))))
        
    

    print 'Overall duration: %s sec' % (stop - init_start, )

finally:

    # This part kicks out trailing zeros and last IV if it is not fully finished (stopped somwhere in the middle)  # ADD THIS BLOCK FOR MATRIX FILE SAVING
    for i, el in enumerate(new_mat[0]):     
        all_zeros = not np.any(new_mat[:,i])    # Finiding first column with all zeros
        if all_zeros:
            new_mat = new_mat[:,0:i-1]          # Leving all columns until that column, all the other are kicked out
            break

    # Saving the matrix to the matrix filedata.get_filepath
    np.savetxt(fname=data.get_filepath() + "_matrix", X=new_mat, fmt='%1.4e', delimiter=' ', newline='\n')   # ADD THIS LINE FOR MATRIX FILE SAVING


    


    # after the measurement ends, you need to close the data file.
    data.close_file()
    #data_current.close_file()
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()