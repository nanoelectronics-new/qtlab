import numpy as np
from time import sleep

''' Function to sweep DACs to zero quasi simultaneously.'''

def sweep_to_zero():
	dac5 = IVVI.get_dac5()
	dac6 = IVVI.get_dac6()
	dac7 = IVVI.get_dac7()
	v_step = 10 # Voltage step in mV
	stepdelay = 0.2 # Delay between steps in s
	
	# Checking if the current value is pos or neg and creating the corresponding sweeping vector 
	if dac5 > 0:  # If it is positive
		v_array = np.arange(dac5, 0.0, -v_step)
	elif dac5 < 0: # If it is negative
		v_array = np.arange(dac5, 0.0, v_step)
	else:
		raise Excpetion("Already at zero")
	

	if dac5 == dac6 == dac7:
		for v in v_array:
			IVVI.set_dac5(v)
			IVVI.set_dac6(v)
			IVVI.set_dac7(v)
			sleep(stepdelay)
	else:
		raise Exception("DACs are not at the same voltage value")

#Run the function
sweep_to_zero()



def sweep_to_zero_single():

	dac5 = IVVI.get_dac2()
	v_step = 10 # Voltage step in mV
	stepdelay = 0.2 # Delay between steps in s
	
	# Checking if the current value is pos or neg and creating the corresponding sweeping vector 
	if dac5 > 0:  # If it is positive
		v_array = np.arange(dac5, 0.0, -v_step)
	elif dac5 < 0: # If it is negative
		v_array = np.arange(dac5, 0.0, v_step)
	else:
		raise Exception("Already at zero")
	
	for v in v_array:
		IVVI.set_dac2(v)
		sleep(stepdelay)

#sweep_to_zero_single()



