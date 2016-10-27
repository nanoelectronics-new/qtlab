from numpy import pi, random, arange, size, mod, reshape, mean
from time import time,sleep
import datetime
import UHFLI_lib
import matplotlib.pyplot as plt
import math
import data



#gen = data.IncrementalGenerator('D:/Measurements/Lada/20160919/File_name_auto_increment/test') #last part is the name of the file
#qt.Data.set_filename_generator(gen)


#IVVI = qt.instruments.create('DAC','IVVI',interface = 'COM4', polarity=['BIP', 'POS', 'POS', 'BIP'], numdacs=16)
AWG = qt.instruments.get("AWG")
#name='pulsing,80uV -35dBm, -+500, +-600, 200us200us three-part-pulse 1000#' 



Num_of_waveforms = 10 # Sequence length - correspond to number of rows in slice matrix
Num_of_repetitions = 50



UHFLI_lib.UHF_init_scope()  # Initialize UHF LI

qt.mstart()
data = qt.Data(name = "T1_meas 10 traces over 50 50kHz By=2T read 1,9mV no compensation")
data.create_file()
data_path = data.get_dir()

try:

    for j in xrange(Num_of_repetitions):
        print j

        


            # Now you provide the information of what data will be saved in the
            # datafile. A distinction is made between 'coordinates', and 'values'.
            # Coordinates are the parameters that you sweep, values are the
            # parameters that you readout (the result of an experiment). This
            # information is used later for plotting purposes.
            # Adding coordinate and value info is optional, but recommended.
            # If you don't supply it, the data class will guess your data format.
            #data.add_coordinate('Line_num')
            #data.add_coordinate('Num of samples')
            #data.add_value('Reflection [Arb. U.]')
            #data.add_value('Pulse Voltage [V]')

            
           

           
                

                # Next two plot-objects are created. First argument is the data object
                # that needs to be plotted. To prevent new windows from popping up each
                # measurement a 'name' can be provided so that window can be reused.
                # If the 'name' doesn't already exists, a new window with that name
                # will be created. For 3d plots, a plotting style is set.

                #

                #plot2d = qt.Plot2D(data, name=name, autoupdate=True)
                #plot2d.set_style('lines')

        AWG._ins.stop()  # Stop AWG to restart the sequencer       
        AWG._ins.run()  # Run AWG - Run must be before do_set_output
        AWG._ins.do_set_output(1,1)   # Turn on AWG ch1
        AWG._ins.do_set_output(1,2)   # Turn on AWG ch1



        # readout
        for i in xrange(Num_of_waveforms):
            #print i 
            qt.msleep(0.05)  # Sleeping for keeping GUI responsive
            try:
                result = UHFLI_lib.UHF_measure_scope(AWG_instance = AWG, maxtime = 0.3)  # Collecting the result from UHFLI buffer
                if i == 0:
                    ch1 = result[0]         # Taking readout from the first channel, first vector
                else:
                    ch1 = np.c_[ch1, result[0]]    # Adding next vectors 
            except:                    
                pass   
            

                
                    
                
        try:                
            #np.savetxt(fname=data_path + "/result_CH1matrix%d"%j, X=ch1, fmt='%1.4e', delimiter=' ', newline='\n')  # Saving matrix file after each repeteition

            if j == 0:
                aver = ch1
            else:       
                aver = aver + ch1  # Summing all the intermediate results for the average
            AWG._ins.stop()  # Stop AWG to restart the sequencer
        except:
            pass
                
            
                
                
                

               
        
        
            

finally:


    # after the measurement ends, you need to close the data file.
    data.close_file()

    aver /=float(Num_of_repetitions)  # Calucalting the average result

    # Saving UHFLI setting to the measurement data folder
    # You can load this settings file from UHFLI user interface 
    
    UHFLI_lib.UHF_save_settings(path = data_path)
    data.add_data_point(aver)
    

    ## Maybe add plot here

    AWG._ins.do_set_output(0,1)   # Turn off AWG ch1
    AWG._ins.do_set_output(0,2)   # Turn off AWG ch1
    # lastly tell the secondary processes (if any) that they are allowed to start again.
    qt.mend()
