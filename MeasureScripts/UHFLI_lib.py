import matplotlib.pyplot as plt
import os
#import qt
import re
import time
import warnings
import itertools
import numpy as np 

import zhinst.utils as utils
import zhinst.ziPython as ziPython




def UHF_init_scope(device_id = 'dev2148'):
    
    """
    Connecting to the device specified by device_id and setting initial parameters through LabOne GUI
    


    Arguments:
        

      device_id (str): The ID of the device to run the example with. For
        example, 'dev2148'.



    Raises:

      RuntimeError: If the device is not connected to the Data Server.
    """

    global daq  # Creating global variable for accesing the UHFLI from other functions
    global device # Creating global variable for accesing the UHFLI from other functions 

    # Create an instance of the ziDiscovery class.
    d = ziPython.ziDiscovery()

    # Determine the device identifier from it's ID.
    device = d.find(device_id).lower()

    # Get the device's default connectivity properties.
    props = d.get(device)

    # The maximum API level supported by this example.
    apilevel_example = 5
    # The maximum API level supported by the device class, e.g., MF.
    apilevel_device = props['apilevel']
    # Ensure we run the example using a supported API level.
    apilevel = min(apilevel_device, apilevel_example)
    # See the LabOne Programming Manual for an explanation of API levels.

    # Create a connection to a Zurich Instruments Data Server (an API session)
    # using the device's default connectivity properties.
    daq = ziPython.ziDAQServer(props['serveraddress'], props['serverport'], apilevel)

    # Check that the device is visible to the Data Server
    if device not in utils.devices(daq):
        raise RuntimeError("The specified device `%s` is not visible to the Data Server, " % device_id +
                           "please ensure the device is connected by using the LabOne User Interface " +
                           "or ziControl (HF2 Instruments).")

    # find out whether the device is an HF2 or a UHF
    devtype = daq.getByte('/%s/features/devtype' % device)
    options = daq.getByte('/%s/features/options' % device)

    
 

    # Create a base configuration: disable all outputs, demods and scopes
    general_setting = [
        ['/%s/demods/*/rate' % device, 0],
        ['/%s/demods/*/trigger' % device, 0],
        ['/%s/sigouts/*/enables/*' % device, 0]]
    if re.match('HF2', devtype):
        general_setting.append(['/%s/scopes/*/trigchannel' % device, -1])
    else:  # UHFLI
        pass
        #general_setting.append(['/%s/demods/*/enable' % device, 0])
        #general_setting.append(['/%s/scopes/*/enable' % device, 0])
    daq.set(general_setting)
    
    
    raw_input("Set the UHF LI parameters in user interface dialog!  Press enter to continue...")  # Wait for user to set the device parametrs from user interface

    







def UHF_measure_scope(device_id = 'dev2148', maxtime = 5, AWG_instance = None):

    """
    Obtaining data from UHF LI using ziDAQServer's blocking (synchronous) poll() command
    Acessing to UHF LI is done by global variable daq and device defined in UHF_init_scope function
    Triggering AWG

   

    Arguments:
        

      device_id (str): The ID of the device to run the example with. For
        example, 'dev2148'.

      maxtime (int): Maximum measurement time in seconds - after this 
        period expires measurement is stopped and data collected until that
        point is returned

    Returns:

      shotCH1,shotCH2 (np.array)  -  vectors of data read out on scope channels CH1 and CH2

    Raises:

      RuntimeError: If the device is not connected to the Data Server.
    """

    data = list()
    
    # Poll data parameters
    poll_length = 0.001  # [s]
    poll_timeout = int(maxtime*1000)  # [ms]
    poll_flags = 0
    poll_return_flat_dict = True
    
    daq.setInt('/dev2148/scopes/0/enable', 1)  # Enable scope
    time.sleep(0.01)  # Wait for everything to be proper initialized
    
    #START MEASURE
    # Subscribe to the scope data
    path =  '/%s/scopes/0/wave' % (device)  # Device node to acquire data from (this one stands for scope)

    
    daq.sync()
    daq.subscribe(path)
    
    time.sleep(maxtime)   # Empirically proven that here we need to wait at least the scope shot length
    
    AWG_instance._ins.force_trigger() # This trigger also triggers lockin aquisition/BNC cable 
    #AWG_instance._ins.run()
    
    start = time.time()  # Starting time counter
    while True:  # Readout data block by block until whole buffer is read out
        data.append(daq.poll(poll_length, poll_timeout, poll_flags, poll_return_flat_dict))  # Readout from subscribed node (scope)
        if bool(data[-1]) == False:  # If the last poll did not returned any data - buffer is empty - transfer is finished
            break
        stop = time.time() # Checking time pass    
        if (stop - start) > maxtime:  # If measurement time is bigger then maxtime - stop it
            break   
    #END OF MEASURE

  
            
    # Unsubscribe from all paths
    daq.unsubscribe('*')
    
    # Disable the scope
    daq.setInt('/dev2148/scopes/0/enable', 0)
    

    if bool(data[0]) == False:  # If no data is returned
        print("NO DATA RETURNED!")
        return (0,0)
        
    
    # HANDLING THE DATA: 
    shots = list() 
    for i in xrange(len(data)):
        if data[i]:  # If specified poll returned something
            shots.append(data[i][path])  # Extracting measured shot or shots from measurement dictionary in data and putting it in "data" as one element in list
            
    shots = list(itertools.chain(*shots)) # Reducing "shots" dimension to 1d
                                          # Shots is list of dictionaries - each dictionary element is one block 
    
    
    shotCH1 = np.array([0])
    shotCH2 = np.array([0])
    
    Amp_scaling_factorCH1 = shots[0]['channelscaling'][0]  # Extracting amplitude scaling factor from read out data dictionary for channel 1 - see output data structure of poll command
    Amp_scaling_factorCH2 = shots[0]['channelscaling'][1]  # Extracting amplitude scaling factor from read out data dictionary for channel 2 - see output data structure of poll command
    
    # If shot is big it is divided in blocks that needs to be connected (concatenated): 
    # For CH1:  
    for block in shots:  # Going trough all blocks in a shot
        shotCH1 = np.concatenate((shotCH1, block['wave'][:,0]))  # Concatenating block to get a shot recorded on device channel 1
    # For CH2:
    CH2_ON = True # Channel 2 on flag - if it is on flag is True
    try:
        dummy = block['wave'][0,1]  # Checking whether this will return error - channel 2 off , or it will not - channel 2 on
    except IndexError: 
        CH2_ON = False     # If Channel 2 is off flag is False
    
    if CH2_ON:
        for block in shots:  # Going trough all blocks in a shot
            shotCH2 = np.concatenate((shotCH2, block['wave'][:,1]))  # Concatenating block to get a shot recorded on device channel 
        
    
    shotCH1 = shotCH1 * Amp_scaling_factorCH1   # Rescaling returned data to get proper values
    shotCH2 = shotCH2 * Amp_scaling_factorCH2
    
    #plt.figure(1)
    #plt.title("Data from CH1")
    #plt.plot(shotCH1) 
    #plt.xlabel('Samples')
    #plt.ylabel('Amplitude (V)')
    #plt.show(block=False)
    
    #if CH2_ON:
        #plt.figure(2)
        #plt.title("Data from CH2")
        #plt.plot(shotCH2) 
        #plt.xlabel('Samples')
        #plt.ylabel('Amplitude (V)')
        #plt.show(block=False)
    
    
    #AWG._visainstrument.close()   # Closing the session towards instrument

    return shotCH1,shotCH2   # Returning data vectors for both channels



def UHF_measure_scope_single_shot(device_id = 'dev2148', maxtime = 5, AWG_instance = None):

    """
    Obtaining data from UHF LI using ziDAQServer's blocking (synchronous) poll() command
    Acessing to UHF LI is done by global variable daq and device defined in UHF_init_scope function
    Without AWG triggering

   

    Arguments:
        

      device_id (str): The ID of the device to run the example with. For
        example, 'dev2148'.

      maxtime (int): Maximum measurement time in seconds - after this 
        period expires measurement is stopped and data collected until that
        point is returned

    Returns:

      shotCH1,shotCH2 (np.array)  -  vectors of data read out on scope channels CH1 and CH2

    Raises:

      RuntimeError: If the device is not connected to the Data Server.
    """

    data = list()
    
    # Poll data parameters
    poll_length = 0.001  # [s]
    poll_timeout = int(2*maxtime*1000)  # [ms]
    poll_flags = 0
    poll_return_flat_dict = True
    
    
    daq.setInt('/dev2148/scopes/0/enable', 1)  # Enable scope
    time.sleep(0.01)  # Wait for everything to be proper initialized
    
    #START MEASURE
    # Subscribe to the scope data
    path =  '/%s/scopes/0/wave' % (device)  # Device node to acquire data from (this one stands for scope)

    
    daq.sync()
    daq.subscribe(path)
    daq.flush()
    
 
    #time.sleep(maxtime)   # Empirically proven that here we need to wait at least the scope shot length
    daq.setInt('/dev2148/scopes/0/trigforce', 1) # Force trigger UHFLI scope
    #time.sleep(maxtime)   # Empirically proven that here we need to wait at least the scope shot length
    
   
 
    
    start = time.time()  # Starting time counter
    while True:  # Readout data block by block until whole buffer is read out
        data.append(daq.poll(poll_length, poll_timeout, poll_flags, poll_return_flat_dict))  # Readout from subscribed node (scope)
        if bool(data[-1]) == False:  # If the last poll did not returned any data - buffer is empty - transfer is finished
            break
        stop = time.time() # Checking time pass    
        if (stop - start) > maxtime:  # If measurement time is bigger then maxtime - stop it
            break   
    #END OF MEASURE

  
            
    # Unsubscribe from all paths
    daq.unsubscribe('*')
    
    # Disable the scope
    daq.setInt('/dev2148/scopes/0/enable', 0)
    

    if bool(data[0]) == False:  # If no data is returned
        print("NO DATA RETURNED!")
        return (0,0)
        
    
    # HANDLING THE DATA: 
    shots = list() 
    for i in xrange(len(data)):
        if data[i]:  # If specified poll returned something
            shots.append(data[i][path])  # Extracting measured shot or shots from measurement dictionary in data and putting it in "data" as one element in list
            
    shots = list(itertools.chain(*shots)) # Reducing "shots" dimension to 1d
                                          # Shots is list of dictionaries - each dictionary element is one block 
    
    
    shotCH1 = np.array([0])
    shotCH2 = np.array([0])
    
    Amp_scaling_factorCH1 = shots[0]['channelscaling'][0]  # Extracting amplitude scaling factor from read out data dictionary for channel 1 - see output data structure of poll command
    Amp_scaling_factorCH2 = shots[0]['channelscaling'][1]  # Extracting amplitude scaling factor from read out data dictionary for channel 2 - see output data structure of poll command
    
    # If shot is big it is divided in blocks that needs to be connected (concatenated): 
    # For CH1:  
    for block in shots:  # Going trough all blocks in a shot
        shotCH1 = np.concatenate((shotCH1, block['wave'][:,0]))  # Concatenating block to get a shot recorded on device channel 1
    # For CH2:
    CH2_ON = True # Channel 2 on flag - if it is on flag is True
    try:
        dummy = block['wave'][0,1]  # Checking whether this will return error - channel 2 off , or it will not - channel 2 on
    except IndexError: 
        CH2_ON = False     # If Channel 2 is off flag is False
    
    if CH2_ON:
        for block in shots:  # Going trough all blocks in a shot
            shotCH2 = np.concatenate((shotCH2, block['wave'][:,1]))  # Concatenating block to get a shot recorded on device channel 
        
    
    shotCH1 = shotCH1 * Amp_scaling_factorCH1   # Rescaling returned data to get proper values
    shotCH2 = shotCH2 * Amp_scaling_factorCH2
    
    #plt.figure(1)
    #plt.title("Data from CH1")
    #plt.plot(shotCH1) 
    #plt.xlabel('Samples')
    #plt.ylabel('Amplitude (V)')
    #plt.show(block=False)
    
    #if CH2_ON:
        #plt.figure(2)
        #plt.title("Data from CH2")
        #plt.plot(shotCH2) 
        #plt.xlabel('Samples')
        #plt.ylabel('Amplitude (V)')
        #plt.show(block=False)
    
    
    #AWG._visainstrument.close()   # Closing the session towards instrument

    return shotCH1,shotCH2   # Returning data vectors for both channels



def UHF_init_demod(device_id = 'dev2210', demod_c = 3, out_c = 0):
    
    """
    Connecting to the device specified by device_id and setting initial parameters through LabOne GUI
    


    Arguments:
        

      device_id (str): The ID of the device to run the example with. For
					   example, 'dev2148'.
      demod_c (int): One of {0 - 7} demodulators of UHF LI 
      out_c (int): One of {0,1} output channels of UHF LI


    Raises:

      RuntimeError: If the device is not connected to the Data Server.
    """

    global daq  # Creating global variable for accesing the UHFLI from other functions
    global device # Creating global variable for accesing the UHFLI from other functions 

    # Create an instance of the ziDiscovery class.
    d = ziPython.ziDiscovery()

    # Determine the device identifier from it's ID.
    device = d.find(device_id).lower()

    # Get the device's default connectivity properties.
    props = d.get(device)

    # The maximum API level supported by this example.
    apilevel_example = 5
    # The maximum API level supported by the device class, e.g., MF.
    apilevel_device = props['apilevel']
    # Ensure we run the example using a supported API level.
    apilevel = min(apilevel_device, apilevel_example)
    # See the LabOne Programming Manual for an explanation of API levels.

    # Create a connection to a Zurich Instruments Data Server (an API session)
    # using the device's default connectivity properties.
    daq = ziPython.ziDAQServer(props['serveraddress'], props['serverport'], apilevel)

    # Check that the device is visible to the Data Server
    if device not in utils.devices(daq):
        raise RuntimeError("The specified device `%s` is not visible to the Data Server, " % device_id +
                           "please ensure the device is connected by using the LabOne User Interface " +
                           "or ziControl (HF2 Instruments).")

    # find out whether the device is an HF2 or a UHF
    devtype = daq.getByte('/%s/features/devtype' % device)
    options = daq.getByte('/%s/features/options' % device)

    
 

    # Create a base configuration: disable all outputs, demods and scopes
    general_setting = [
        ['/%s/demods/*/rate' % device, 0],
        ['/%s/demods/*/trigger' % device, 0],
        ['/%s/sigouts/*/enables/*' % device, 0]]
    if re.match('HF2', devtype):
        general_setting.append(['/%s/scopes/*/trigchannel' % device, -1])
    else:  # UHFLI
        pass
        #general_setting.append(['/%s/demods/*/enable' % device, 0])
        #general_setting.append(['/%s/scopes/*/enable' % device, 0])
    daq.set(general_setting)
    
    
    raw_input("Set the UHF LI parameters in user interface dialog!  Press enter to continue...")  # Wait for user to set the device parametrs from user interface

   
    daq.setInt('/%s/demods/%s/enable' % (device, demod_c) , 1)  # Enable demodulator 

    daq.setInt('/%s/demods/%s/rate' % (device, demod_c), 100000) # Set the demodulator sampling rate



    
    
    
    # Unsubscribe any streaming data
    daq.unsubscribe('*')



    # Path to UHF LI readout node made globally for using in other functions
    global path_demod
    path_demod = '/%s/demods/%d/sample' % (device, demod_c)

    global path_demod_enable
    path_demod_enable = '/%s/demods/%d/enable' % (device, demod_c) 

    # Path to UHF LI demodulator trigger node made globally for using in other functions
    global path_demod_trig
    path_demod_trig = '/%s/demods/%d/trigger' % (device, demod_c) 


    # Perform a global synchronisation between the device and the data server:
    # Ensure that 1. the settings have taken effect on the device before issuing
    # the poll() command and 2. clear the API's data buffers. Note: the sync()
    # must be issued after waiting for the demodulator filter to settle above.
    daq.sync()

    # Subscribe to the demodulator's sample
    path = path_demod
    daq.subscribe(path)

    # Get output amplitude 
    # made globally for using in other functions
    global out_ampl 
    out_ampl = daq.getDouble('/%s/sigouts/%s/amplitudes/3' % (device, out_c))/np.sqrt(2)

    # Get sampling rate
    # made globally for using in other functions
    global sampling_rate
    sampling_rate = daq.getDouble('/%s/demods/%s/rate' % (device, demod_c))

    # Get time constant in seconds 
    # made globally for using in other functions
    global TC
    TC = daq.getDouble('/%s/demods/%s/timeconstant' % (device, demod_c))

    return daq
    

    
            


def UHF_measure_demod(Num_of_TC = 3):


    """
    Obtaining data from UHF LI demodulator using ziDAQServer's blocking (synchronous) poll() command
    Acessing to UHF LI is done by global variable daq and device defined in UHF_init_demod function

   

    Arguments:
	  Num_of_TC(int) - Number of time constant to wait before the measurement
      

    Returns:

      sample_mean (float): Mean value of recorded samples (default 1000) as R (amplitude) value of input  

    Raises:

      RuntimeError: If the device is not connected to the Data Server.
    """

    
    
    path = path_demod

    # Poll data parameters
    poll_length = 1/sampling_rate * 1000  # [s]   # Data aquisition time for recording 1000 samples
    poll_timeout = 500  # [ms]
    poll_flags = 0
    poll_return_flat_dict = True 
    

    #START MEASURE

    # Wait for the demodulator filter to settle
    time.sleep(Num_of_TC*TC)

    daq.sync()  # Getting rid of previous read data in the buffer

    data = daq.poll(poll_length, poll_timeout, poll_flags, poll_return_flat_dict)  # Readout from subscribed node (demodulator)

    #END OF MEASURE

    # Check the dictionary returned is non-empty
    assert data, "poll() returned an empty data dictionary, did you subscribe to any paths?"
    # Note, the data could be empty if no data arrived, e.g., if the demods were
    # disabled or had demodulator rate 0
    assert path in data, "data dictionary has no key '%s'" % path
    # The data returned is a dictionary of dictionaries that reflects the node's path


    # The data returned is a dictionary of dictionaries that reflects the node's path
    sample = data[path]
    sample_x = np.array(sample['x'])    # Converting samples to numpy arrays for faster calculation
    sample_y = np.array(sample['y'])    # Converting samples to numpy arrays for faster calculation
    sample_r = np.sqrt(sample_x**2 + sample_y**2)   # Calculating R value from X and y values
    sample_fi = np.arctan2(sample_y,sample_x) * 180 / np.pi  # Calculating the angle value in degrees
    
    #print (len(sample_r))
    
    sample_mean_r = np.mean(sample_r)  # Mean value of recorded data vector
    sample_mean_fi = np.mean(sample_fi) 
    #measured_ac_conductance = sample_mean/out_ampl
  
    return sample_mean_r, sample_mean_fi





def UHF_init_demod_multiple(device_id = 'dev2148', demod_c = [0], out_c = 0):
    
    """
    Connecting to the device specified by device_id and setting initial parameters through LabOne GUI
    


    Arguments:
        

      device_id (str): The ID of the device to run the example with. For
                       example, 'dev2148'.
      demod_c (list): Elements of the list are integers {0 - 7} that represents demodulators of UHF LI 
      out_c (int): One of {0,1} output channels of UHF LI


    Raises:

      RuntimeError: If the device is not connected to the Data Server.
    """

    global daq  # Creating global variable for accesing the UHFLI from other functions
    global device # Creating global variable for accesing the UHFLI from other functions 

    # Create an instance of the ziDiscovery class.
    d = ziPython.ziDiscovery()

    # Determine the device identifier from it's ID.
    device = d.find(device_id).lower()

    # Get the device's default connectivity properties.
    props = d.get(device)

    # The maximum API level supported by this example.
    apilevel_example = 5
    # The maximum API level supported by the device class, e.g., MF.
    apilevel_device = props['apilevel']
    # Ensure we run the example using a supported API level.
    apilevel = min(apilevel_device, apilevel_example)
    # See the LabOne Programming Manual for an explanation of API levels.

    # Create a connection to a Zurich Instruments Data Server (an API session)
    # using the device's default connectivity properties.
    daq = ziPython.ziDAQServer(props['serveraddress'], props['serverport'], apilevel)

    # Check that the device is visible to the Data Server
    if device not in utils.devices(daq):
        raise RuntimeError("The specified device `%s` is not visible to the Data Server, " % device_id +
                           "please ensure the device is connected by using the LabOne User Interface " +
                           "or ziControl (HF2 Instruments).")

    # find out whether the device is an HF2 or a UHF
    devtype = daq.getByte('/%s/features/devtype' % device)
    options = daq.getByte('/%s/features/options' % device)

    
 

    # Create a base configuration: disable all outputs, demods and scopes
    general_setting = [
        ['/%s/demods/*/rate' % device, 0],
        ['/%s/demods/*/trigger' % device, 0],
        ['/%s/sigouts/*/enables/*' % device, 0]]
    if re.match('HF2', devtype):
        general_setting.append(['/%s/scopes/*/trigchannel' % device, -1])
    else:  # UHFLI
        pass
        #general_setting.append(['/%s/demods/*/enable' % device, 0])
        #general_setting.append(['/%s/scopes/*/enable' % device, 0])
    daq.set(general_setting)
    
    
    raw_input("Set the UHF LI parameters in user interface dialog!  Press enter to continue...")  # Wait for user to set the device parametrs from user interface

    daq.setInt('/%s/demods/*/rate' % device, 100000)  # Set all demodulators rate to 100k

    for dem in demod_c:
        daq.setInt('/%s/demods/%s/enable' % (device, dem) , 1)  # Enable all demodulators listed in the list demod_c
    
    
    # Unsubscribe any streaming data
    daq.unsubscribe('*')
    
   

    # Path to UHF LI readout node made globally for using in other functions
    
    global path_demod 
    path_demod = []
    for dem in demod_c:
        path_demod.append('/%s/demods/%d/sample' % (device, dem))
        

    
    global path_demod_enable
    path_demod_enable = [] 
    for dem in demod_c:
        path_demod_enable.append('/%s/demods/%d/enable' % (device, dem))
        


    # Path to UHF LI demodulator trigger node made globally for using in other functions
    global path_demod_trig
    path_demod_trig = []
    for dem in demod_c:
        path_demod_trig.append('/%s/demods/%d/enable' % (device, dem))

    # Perform a global synchronisation between the device and the data server:
    # Ensure that 1. the settings have taken effect on the device before issuing
    # the poll() command and 2. clear the API's data buffers. Note: the sync()
    # must be issued after waiting for the demodulator filter to settle above.
    daq.sync()

    # Subscribe to demodulator's samples from the list demod_c 
    for path in path_demod:
        daq.subscribe(path)

    # Get output amplitude 
    # made globally for using in other functions
    #global out_ampl 
    #out_ampl = daq.getDouble('/%s/sigouts/%s/amplitudes/3' % (device, out_c))/np.sqrt(2)

    # Get sampling rate
    # made globally for using in other functions
    global sampling_rate
    sampling_rate = daq.getDouble('/%s/demods/%s/rate' % (device, demod_c[0]))

    # Get time constant in seconds 
    # made globally for using in other functions
    global TC
    TC = daq.getDouble('/%s/demods/%s/timeconstant' % (device, demod_c[0]))

    return daq


def UHF_measure_demod_multiple(Num_of_TC = 3):


    """
    Obtaining data from UHF LI demodulator using ziDAQServer's blocking (synchronous) poll() command
    Acessing to UHF LI is done by global variable daq and device defined in UHF_init_demod function

   

    Arguments:
      Num_of_TC(int) - Number of time constant to wait before the measurement
      

    Returns:

      result (list of lists of floats): each entry of the list corresponds to the radout of one deomodulator (0 - demod1, 1 - demod2,...)
                                        this entry itself is a list with the first element (index 0) equal to R and second to phase

    Raises:

      RuntimeError: If the device is not connected to the Data Server.
    """

    
    
    path = path_demod

    # Poll data parameters
    poll_length = 1/sampling_rate * 2000  # [s]   # Data aquisition time for recording 1000 samples
    poll_timeout = 500  # [ms]
    poll_flags = 0
    poll_return_flat_dict = True 
    

    #START MEASURE

    # Wait for the demodulator filter to settle
    time.sleep(Num_of_TC*TC)

    daq.sync()  # Getting rid of previous read data in the buffer

    data = daq.poll(poll_length, poll_timeout, poll_flags, poll_return_flat_dict)  # Readout from subscribed node (demodulator)

    #END OF MEASURE

    # Check the dictionary returned is non-empty
    assert data, "poll() returned an empty data dictionary, did you subscribe to any paths?"
    # Note, the data could be empty if no data arrived, e.g., if the demods were
    # disabled or had demodulator rate 0
    
    
    
    #assert path in data, "data dictionary has no key '%s'" % path
    # The data returned is a dictionary of dictionaries that reflects the node's path
    result = []
    for dem in path:
    # The data returned is a dictionary of dictionaries that reflects the node's path
    # Since we have a list of paths, corresponding to read demodulators, we need to extract the data from each of them 
        sample = data[dem]
        sample_x = np.array(sample['x'])    # Converting samples to numpy arrays for faster calculation
        sample_y = np.array(sample['y'])    # Converting samples to numpy arrays for faster calculation
        mean_x = np.mean(sample_x)
        mean_y = np.mean(sample_y)
        mean_r = np.sqrt(mean_x**2 + mean_y**2)   # Calculating R value from X and y values
        mean_fi = np.arctan2(mean_y,mean_x) * 180 / np.pi  # Calculating the angle value in degrees
        result.append([mean_r,mean_fi])
        
      # Mean value of recorded data vector
    #measured_ac_conductance = sample_mean/out_ampl
  
    return result


def UHF_measure_demod_trig(Num_of_TC = 3, trigger = 3, AWG_instr = None, record_time = 5):


    """
    Obtaining data from UHF LI demodulator using ziDAQServer's blocking (synchronous) poll() command
    Data aqusition controlled with trigger 3 or 4 - trggering on trigger HIGH level
    Acessing to UHF LI is done by global variable daq and device defined in UHF_init_demod function

   

    Arguments:
      Num_of_TC(int) - Number of time constant to wait before the measurement
      Trigger(int) - 3 or 4 - indicates used trigger input on the UHFLI
                              It will complain if not 3 or 4 is selected

      AWG_instr(Tektronix_AWG5014 class) - Instance of AWG instrument
      record_time(float) - Recording time in seconds

    Returns:

      sample_mean (float): Mean value of recorded samples (default 1000) as R (amplitude) value of input  

    Raises:

      RuntimeError: If the device is not connected to the Data Server.
    """

    
    if AWG_instr is None:
        raise Exception("AWG_instr is not passed :-P")

    path = path_demod

    # Poll data parameters
    poll_length = 0.001  # [s]
    poll_timeout = 500  # [ms]
    poll_flags = 0
    poll_return_flat_dict = True 

    if trigger not in [3,4]:
        raise Exception("Trigger must be either 3 or 4!")


    

    # Unsubscribe from all paths (nodes) - needed that buffer is not continuously filling
    daq.unsubscribe('*')

    daq.setInt(path_demod_trig, 32)

    #START MEASURE

    # Subscribe to the demodulator's sample using global parameter "path demod" from "UHF_init_demod" function
    daq.subscribe(path_demod) 

    daq.setInt(path_demod_enable, 1)  # Enable demodulator 

    daq.sync()  # Getting rid of previous read data in the buffer

    # Wait for the demodulator filter to settle
    time.sleep(Num_of_TC*TC) 

    AWG_instr._ins.run()  # Forcing AWG to start output      


    data = daq.poll(record_time, poll_timeout, poll_flags, poll_return_flat_dict)  # Readout from subscribed node (demodulator)  # Waiting until whole desired data is in buffer (record time)

    daq.setInt(path_demod_enable, 0)  # Disable demodulator

    #END OF MEASURE

    # Check the dictionary returned is non-empty
    assert data, "poll() returned an empty data dictionary, did you subscribe to any paths?"
    # Note, the data could be empty if no data arrived, e.g., if the demods were
    # disabled or had demodulator rate 0
    assert path in data, "data dictionary has no key '%s'" % path
    # The data returned is a dictionary of dictionaries that reflects the node's path


    # The data returned is a dictionary of dictionaries that reflects the node's path
    sample = data[path]
    sample_x = np.array(sample['x'])    # Converting samples to numpy arrays for faster calculation
    sample_y = np.array(sample['y'])    # Converting samples to numpy arrays for faster calculation
    sample_r = np.sqrt(sample_x**2 + sample_y**2)   # Calculating R value from X and y values
    

  
    return sample_r





def UHF_save_settings(path = None, filename = 'UHFLI_settings_file.xml'):
    """
    Saving UHF Lockin settings file to a location defined by path in a file defined
    by filename.

    Arguments:

      daq (ziDAQServer): Instance of UHFLI device
      path (str): Location on disk where settings file is going to be saved
      filename (str): File name of saved settings file

    """
    dev = utils.autoDetect(daq)  # Get a device string - needed for save_settings function
    utils.save_settings(daq, dev, path + os.sep + filename)  # saving setting file



