"""Script for calculating an optimal attenuator configuration, based on inputs.

    INPUTS:
        wanted_overall_attenuation: int
        attenuator_set: list of attenuattors on disposal
        Tin: float, noise temperature on the input of the first attenuator
        Ta: list, ambient temperatures of all the attenuators
        Pinput: Input power in mW
        max_P_4K: Maximum allowed dissipation on the 4K plate in mW
        max_P_MC: Maximum allowed dissipation on the MC plate in mW
        
    OUTPUTS:
        Currently_minium_noise_of_combination - minimum calculated overall noise
        Currently_noise_minimizing_combination - attenuator combination that minimizes the overall noise
"""
        
wanted_overall_attenuation = 50         # In dB
attenuator_set = [0,3,6,9,10,12,20,30]     # In dB
Tin = 290.0                             # In Kelvins
Ta = [50.0,4.0,1.0,0.1,0.02]            # In Kelvins

Pinput = 1.0                            # Input power in mW
max_P_4K = 5.0                         # Maximum allowed dissipation on the 4K plate in mW
max_P_MC = 2e-4                         # Maximum allowed dissipation on the MC plate in mW






def L(dB):
    """
    Function for converting dB to ratio
    
     Input: attenuator value in dB
     Output: attenuator value in ratio
    """ 
    return 10**(dB/10.0)

       
                     
def Tout(Tin, L, Ta):
    """
    Function for calculating the ouptut noise temperature of the attenuator.
    
    Input: Tin - noise temperature of the noise at the attenuator input
           L   - attenuator value in ratio
           Ta  - ambient temerature of the attenuator
    Output: Noise temperature of the noise on the attenuator output
    """
    return (float(Tin)/L + (float(L-1)/L)*Ta)
   
     
def Powers(Pin, L):
    """
    Function for calculating dissipated and transmitted power of an attenuator.
    
    Input: Pin - power on the attenuator input
           L   - attenuator value in ratio
    Output: list - first element is a dissipated power, second element is a transmitted power
    """
    return [Pin*(1-1.0/L),float(Pin)/L]
    



possible_atten_combination = []  # Container for all the possible attenuator configurations

for a1 in attenuator_set:        # Going through all the attenuators we have on our disposal  
    for a2 in attenuator_set:    # Through all the fridge stages
        for a3 in attenuator_set:
            for a4 in attenuator_set:
                for a5 in attenuator_set:
                    if a1+a2+a3+a4+a5 == wanted_overall_attenuation:          # Here we create a list off all the possible attenuator configurations.   
                        possible_atten_combination.append([a1,a2,a3,a4,a5])   # The configuration is allowed to go into the list if attenuators sum is equal 
                                                                              # to the wanted overall attenuation. 
                        
if len(possible_atten_combination) == 0:  # For some values of wanted attenuations, it is not possible to find the configuration, which is detected here
    raise Exception("Given overall attenuation cannot be achieved with the given attenuator set")


print "\n\nALL THE POSSIBLE COMBINATIONS:" 
print possible_atten_combination       # Printing all the possible attenuator configurations 

# Eliminating the combinations with a too big power on 4K and MC stages
combinations_to_remove = []
for index,combination in enumerate(possible_atten_combination):  # Going through all the possible combinations
    for i,element in enumerate(combination):   # Going through attenuators on all the fridge plates 
        if i==0:                               # If it is an attenuator on the 50 K plate
            P = Powers(Pinput,L(element))      # Then its input is Pin   
        else:                                  # Otherwise 
            P = Powers(P[1],L(element))        # its input is an output from the previous stage
        if (i==1 and (P[0] > max_P_4K)) or (i==4 and (P[0] > max_P_MC)): # If an attenuator is on the 4K stage and dissipation there is higher then max_P_4K
                                                                          # Or if the attenuator is on the MC stage and dissipation there is higher then max_P_MC
            combinations_to_remove.append(combination) # Then add this combination into the removal list
            break

for combination in combinations_to_remove:      
    possible_atten_combination.remove(combination)     # Removing the over dissipative combinations from the list

print('\n\n\n\n\n\n')
print "COMBINATIONS THAT SATISFY THE DISSIPATION CRITERIA:"
print possible_atten_combination        # Printing the attenuator configurations which satisfied the dissipation criteria



if len(possible_atten_combination) == 0:    # If there is no attenuator configuration which satisfied the dissipation criteria, then stop the execution of the script
    raise Exception("No attenuator configuration can satisfy the given criteria!")



Currently_minium_noise = 10e15                          # Setting the initial noise value to somethign super high (infinite)
Currently_noise_minimizing_combination = []             # Container list for attenuator configurations giving local minimum of the ouput noise 
                                                        # durig the search for the global minimum
for combination in possible_atten_combination:          # Going through all the possible combinations which satisfied the dissipation criteria
    for i,element in enumerate(combination):            # Going through attenuators on all the fridge plates 
        if i==0:                                        # If it is an attenuator on the 50 K plate
            Tin_next = Tout(Tin,L(element),Ta[i])       # Then its input is Tin (noise from the room temperature)
            
        else:                                           # Otherwise
            Tin_next = Tout(Tin_next,L(element),Ta[i])  # its input is an output from the previous stage
            
    if Currently_minium_noise > Tin_next:               # If the currenlty minimum noise is bigger then the noise ouput of the examined combination
        Currently_minium_noise = Tin_next               # Then set this output noise as a new currently minimum noise
        Currently_noise_minimizing_combination = combination   # And set this combination as the currently noise minimizing combiantion
                                                        # After the loop is finished, currently minimum noise will be a global minimum
                                                        # And currenlty noise minimizing combination will be the one which gives the minimum noise
        
        
     

print "\n\n\n\n" 
print  "Noise minimizing attenuator configuration:"
print str(Currently_noise_minimizing_combination) + "\n"        # Printing the noise minimizing combination
print  "Temperature of the noise on the output of the MC plate attenuator %.3f K"%Currently_minium_noise   # And the output noise of this combination

#print  "Noise minimizing attenuator configuration 50K: {0}dB 4K: {1}dB still: {2}dB 50mK: {3}dB MC: {4}dB".format(*Currently_noise_minimizing_combination)   
       
# Calculating the dissipation on all the stages of the noise minimizing combination 
Dissipation_of_stages = [] # Here the dissipation on the individual stages will be stored             
for i,element in enumerate(Currently_noise_minimizing_combination):     # Going through attenuators on all the fridge plates 
        if i==0:                                                        # If it is an attenuator on the 50 K plate
            P = Powers(Pinput,L(element))                               # Then its input is Pin   
            Dissipation_of_stages.append(P[0])                          # Adding the dissipation of the attenuator on the 50 K stage to the list
        else:                                                           # If it is not on 50 K stage
            P = Powers(P[1],L(element))                                 # its input is an output from the previous stage
            Dissipation_of_stages.append(P[0])                          # Adding the dissipation of the attenuator on all the other stages to the list
                
print "Power dissipation at the 50K: {0}mW  4K: {1}mW  still: {2}mW  50mK: {3}mW  MC: {4}mW".format(*Dissipation_of_stages)    # Printing the dissipations on 4K and MC plates
 
