

# We use this script for transport measurements, both DC and AC,
# as a function of 1 or 2 other variables. Its well suited to measure 
# with 1 or 2 Keithleys and/or 1 or 2 Lockins in 2 or 4 terminal geometries.
# If you are a first time user, we recommend scrolling down to the 
# 'initialization' part of the script, we put some usefull comments there.
# Comments/improvements are appreciated.

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.



from numpy import pi, random, arange, size, array, sin, cos, linspace, sinc, sqrt
from time import time, sleep
from shutil import copyfile
from os import mkdir
from os.path import exists
from lib.file_support.spyview import SpyView


import qt
import timetrack
import sys
import numpy as np
import data as d
#import traces
import shutil
import os


keithley1 = qt.instruments.get('keithley1')
keithley2 = qt.instruments.get('keithley2')
lockin1 = qt.instruments.get('lockin1')
#lockin2 = qt.instruments.get('lockin2')
#cryocon = qt.instruments.get('cryocon')
#opto = qt.instruments.get('opto')
magnet = qt.instruments.get('magnet')
magnetX = qt.instruments.get('magnetX')
mw = qt.instruments.get('mw')
ivvi = qt.instruments.get('ivvi')


    
class majorana():
    
    def __init__(self): 
        self.filename=filename
        self.generator=d.IncrementalGenerator(qt.config['datadir']+'\\'+self.filename,1);
    
    
    # Function generates data file, spyview file and copies the pyton script.
    def create_data(self,x_vector,x_coordinate,x_parameter,y_vector,y_coordinate,y_parameter,z_vector,z_coordinate,z_parameter):
        qt.Data.set_filename_generator(self.generator)
        data = qt.Data(name=self.filename)
        data.add_coordinate(x_parameter+' ('+x_coordinate+')',
                            size=len(x_vector),
                            start=x_vector[0],
                            end=x_vector[-1]) 
        data.add_coordinate(y_parameter+' ('+y_coordinate+')',
                            size=len(y_vector),
                            start=y_vector[0],
                            end=y_vector[-1]) 
        data.add_coordinate(z_parameter+' ('+z_coordinate+')',
                            size=len(z_vector),
                            start=z_vector[0],
                            end=z_vector[-1])
        data.add_value('lockin 1')                    # from lock-in 1 for dI measurement
        data.add_value('Keithley 1')            	            # Read out of Keithley 1 for I_dc		
        data.add_value('Keithley 2')                    # Read out of Keithley 1 for dV measurement		
        data.add_value('calibrated dI')            	            # processed dIdV
        data.add_value('calibrated dIdV')            	            # processed dIdV	
        data.add_value('calibrated dIdV_X')            	            # processed dIdV		
        data.create_file()                                  # Create data file
        SpyView(data).write_meta_file()                     # Create the spyview meta.txt file
        return data
    
    
    # Function reads out relevant data
    def take_data(self,dacx,x):
        
        ivvi.set(dacx,x)                                                    # Set specified dac to specified value, has to be done here because of delays needed for Lockin measurements
        qt.msleep(Twait) 
        L1 = lockin1.get_R()                                                 # Read out Lockin1--- measure dI	
        L_X = lockin1.get_X()                                                 # Read out Lockin1--- measure dI_X			
        K1 = keithley1.get_readlastval()                                     # Read out Keithley1---measure I    
        K2 = keithley2.get_readlastval()                                     # Read out Keithley2 ---measure dV		
        dI = L1*12.9/(1.0e-3*excitation*amp-L1*RC)                                 # get dI/dV in the units of (2e2/h)             #  for amp=1M, RC~20KOhm; for amp=10M, R_in=22.5KOhm; for amp=100M, R_in=182KOhm;;; R_in=11.9KOhm for output*100mV, amp=1M	
        dIdV = L1*12.9e8/(1.0*K2*amp*sensitivity)                                    # 	
        dIdV_X = L_X*12.9e8/(1.0*K2*amp*sensitivity)                                    # 			
        datavalues = [L1,K1,K2,dI,dIdV,dIdV_X]
        #datavalues = [value1,K1,0,0,0]		

        return datavalues
        qt.msleep(0.1)                                                     # Keep GUI responsive
     
    ################ 1D scans #####################    
    
    # 1D sweep of a single dac
    def _single_dac_sweep(self,xname,dacx,xstart,xend,xsteps):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        y_vector = [0]
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,y_vector,'none','y_parameter',z_vector,'none','z_parameter')                                # create data file, spyview metafile, copy script
        
        for x in x_vector:
            datavalues = self.take_data(dacx,x) 
			# Go to next sweep value and take data                                                                                                          # Read out mixing chamber temperature
            data.add_data_point(x,0,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5])               		       											        # write datapoint into datafile
        
        data.new_block()
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()
    

    def _dac_vs_2magnets(self,xname,dacx,xstart,xend,xsteps,Bstart,Bend,Bsteps,sita):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        B_vector = linspace(Bstart,Bend,Bsteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,B_vector,'B(T)','Vector_magnet',z_vector,'none','z_parameter')                                     # create data file, spyview metafile, copy script
        
        counter = 0
        #magnet.set_heater(1)		
        #magnet.set_units('T')	
        #magnetX.set_heater(1)		
        #magnetX.set_units('T')			
        for i in arange(len(B_vector)):
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            B = B_vector[i]				
            Bz = B_vector[i]*cos(1.0*sita*pi/180.0)
            Bx = B_vector[i]*sin(1.0*sita*pi/180.0)
			
            magnet.set_field(Bz) 					
            magnetX.set_field(Bx) 				
            ivvi.set(dacx,x_vector[0])
            qt.msleep(2)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,B,0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5])                                                                          # write datapoint into datafile
            
            timetrack.remainingtime(starttime,Bsteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()

		
    def _dac_vs_rotatefield(self,xname,dacx,xstart,xend,xsteps,anglestart,angleend,anglesteps,B):
        qt.mstart()
        
        # Create sweep vectors
        x_vector = linspace(xstart,xend,xsteps+1)
        angle_vector = linspace(anglestart,angleend,anglesteps+1)
        z_vector = [0]
        
        data = self.create_data(x_vector,xname,dacx,angle_vector,'angle(deg)','rotate field',z_vector,'none','z_parameter')                                     # create data file, spyview metafile, copy script
        
        counter = 0
        #magnet.set_heater(1)		
        #magnet.set_units('T')	
        #magnetX.set_heater(1)		
        #magnetX.set_units('T')			
        for i in arange(len(angle_vector)):
            [starttime, counter] = timetrack.start(counter)
            tstart = timetrack.time()
            sita = angle_vector[i]				
            Bz = B*cos(sita*pi*1.0/180.0)
            Bx = B*sin(sita*pi*1.0/180.0)
			
            magnet.set_field(Bz) 					
            magnetX.set_field(Bx) 				
            ivvi.set(dacx,x_vector[0])
            qt.msleep(2)                                                                                                                   # use explained at the bottom of the script
            
            for x in x_vector:
                datavalues = self.take_data(dacx,x)                                                                                             # Go to next sweep value and take data
                data.add_data_point(x,angle_vector[i],0,datavalues[0],datavalues[1],datavalues[2],datavalues[3],datavalues[4],datavalues[5])                                                                          # write datapoint into datafile
            
            timetrack.remainingtime(starttime,anglesteps+1,counter)                                                                                 # Calculate and print remaining scantime
            data.new_block()
            
        data._write_settings_file()                                                                                                             # Overwrite the settings file created at the beginning, this ensures updating the sweep variable with the latest value
        data.close_file()
        qt.mend()

		
#################### INITIALIZATION #########################

# DON'T SKIP THIS PART, ITS CRUCIAL FOR PROPER MEASUREMENTS AND DATA PROCESSING!!!
'''
# Gains and ranges
# Please set the gains and ranges before starting measurements. This ensures proper scaling of axis and data in Spyview.
# Make sure that you put the right gain at the right Keithley/Lockin.
GainK1=1                      # Gain for Keitley 1
GainK2=1                     # Gain for Keitley 2
#GainL1=1e7                      # Gain for Lockin 1
#GainL2=1e2                      # Gain for Lockin 2
Vrange=100e-3                     # voltage range in V/V
'''
#####lockin2 setting(to measure dV)  ###

sensitivity = 50.0e-3   # sensitivity from Lockin2, to measure real dV (need to set manually!!!)

############################ lockin1 setting, don't change (to measure dI)
excitation = 5.0e-6                                        # Excitation amplitude in V
source_amp=10.0e-3                                         # amplifer from IVVI source  10mV/V or 100mV/V
lockin1.set_amplitude(excitation*100.0/(1.0*source_amp))            # Calculates true output excitation voltage lockin

lockin1.set_frequency(77.77)
#lockin1.set_phase(0)

#### change the parameters below if necessary ###

lockin1.set_sensitivity(17)                               # 17:1mV  20:10mV
lockin1.set_tau(9)                                        # tau = 9 equals 300 ms, check S830 driver for other integration times
Twait = 0.5
Tback = 0.3

#### IVVI setting #####

amp=10.0e6    # amplification                 # current range in A/V
RC= 36.7  #KOhm                       # @4K R_in=8.3KOhm ////  @Tbase~30mK, for amp=1M, R_in=20.6KOhm@bias=10mV and 42.7KOhm@bias=0;;;for amp=10M, R_in=36.7KOhm@bias=8mV and 56.8KOhm@bias=0



filename='data'

#################### MEASUREMENTS #########################

m = majorana() 







