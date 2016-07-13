# QTlab driver for American Magnetics 430 magnet power supply.
# This version controls a single solenoid.

#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from instrument import Instrument
import types
import socket
import logging
import time
from math import *
from numpy import *

class AMI430(Instrument):
    
    #Global parameters
    #Important:
    #Set these values in accordance with the limits of each system
    #otherwise magnet quench or damage of equipment might occur
    MARGIN = 0.0001
    
    #ratio between current and magnetic field
    COILCONSTANT = 0.1084       #T/A              #0.0510 for Bx            #0.09279 for the center fridge
    
    #Rated operating current in A, from spec sheet. A margin of 0.03A is added so that the rated fields fit in.
    #If the magnet quenches regularly, reduce these values!!!!
    CURRENTRATING = 80      #A            # 78 for Bx
    
    #Rated magnetic field based on the two previous values
    FIELDRATING = COILCONSTANT*CURRENTRATING    #mT
    
    #Maximum ramp limits from datasheet
    CURRENTRAMPLIMIT = 0.038     #A/s    0.0025 for Bx
    FIELDRAMPLIMIT=COILCONSTANT*CURRENTRAMPLIMIT   #T/s
    
    #Persistent switch rated currents. 
    #These values are based on the autodetect function of the supply unit
    #typical values are ~50mA for wet systems and ~30mA for dry systems
    PSCURRENT=35         #mA
    
    #Heat and cooldown time for persistent switch
    PSHEATTIME=20       #s
    PSCOOLTIME=20       #s
    
    #buffersize for socket
    BUFSIZE=1024    
    
    def __init__(self, name, address='10.21.64.152', port=7180):
        Instrument.__init__(self, name, tags=['measure'])
        
        #self.add_parameter('pSwitch', type=types.BooleanType,
        #        flags=Instrument.FLAG_GETSET,
        #        format_map={False:'off',True:'on'})
                
        self.add_parameter('current', type=types.FloatType,
                flags=Instrument.FLAG_SET,
                units='A',
                minval=-self.CURRENTRATING, maxval=self.CURRENTRATING,
                format='%.4f')
        self.add_parameter('current_get', type=types.FloatType,
                flags=Instrument.FLAG_GET,
                units='A',
                format='%.4f')
                
        self.add_parameter('field', type=types.FloatType,
                flags=Instrument.FLAG_SET,
                units='T',
                minval=-self.FIELDRATING, maxval=self.FIELDRATING,
                format='%.5f')
        self.add_parameter('field_get', type=types.FloatType,
                flags=Instrument.FLAG_GET,
                units='T',
                format='%.5f')

        self.add_parameter('units', type=types.FloatType,
                flags=Instrument.FLAG_GETSET,
                format_map={0:'kG',1:'T'})          


                
        self.add_parameter('setPoint', type=types.FloatType,
                flags=Instrument.FLAG_GET,
                units='T',
                format='%.6f')
        
        self.add_parameter('rampRate_T_s', type=types.FloatType,
                flags=Instrument.FLAG_SET,
                units='T/s',
                minval=0.0, maxval=self.FIELDRAMPLIMIT, format='%.5f')
        self.add_parameter('rampRate_get_T_s', type=types.FloatType,
                flags=Instrument.FLAG_GET,
                units='T/s',
                format='%.5f')
        
        self.add_parameter('rampState', type=types.IntType,
                flags=Instrument.FLAG_GET,
                format_map={1:'Ramping', 2:'Holding', 3:'Paused', 4:'Manual up',
                5:'Manual down', 6:'Ramping to zero', 7:'Quench detected', 
                8:'At zero', 9:'Heating switch', 10:'Cooling switch'})
        
        #self.add_parameter('persistent', type=types.BooleanType,
        #        flags=Instrument.FLAG_GETSET,
        #        format_map={False:'driven mode',True:'persistent mode'})
        
        self.add_parameter('quench', type=types.BooleanType,
                flags=Instrument.FLAG_GET,
                format_map={False:'off',True:'on'})
        
        self.add_parameter('error', type=types.StringType,
                           flags=Instrument.FLAG_GET)
        
        #self.add_function('reset')
        #self.add_function('rampTo')
        self.add_function('resetQuench')
        self.add_function('setPause')
        
        #init connection via ethernet link
        self._host = address
        self._port = port
        
        self._connect()
        
        #quick and dirty solution to flush startup message from buffer
        print self._receive()
        
        self.get_all()
        
    def reset(self):                                                          ###TODO
        pass
    
    def get_all(self):                                                   ### Run this command after interupted the measurements.
        self.get_field_get()
        self.get_current_get()      
        self.get_rampState()
        #self.get_pSwitch()
        self.get_rampRate_get_T_s()
        #self.get_persistent()
        self.get_quench()
        self.get_setPoint()
        self.get_units()        
        
    #Low level functions to handle communication
    #should not be used directly
    
    def _connect(self):                                                 ### Initialize the socket
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.settimeout(0.6)           
        self._socket.connect((self._host, self._port))
        
    def _closeconnection(self):                                                        ###Close all the connections
        self._socket.close()
        
    def _send(self, data):                                              ###TODO: check for timeout and throw exception
        self._socket.sendall(data)
        time.sleep(0.3)                                                 ###Temporary solution for too fast computers
        
    def _receive(self):
        return self._socket.recv(self.BUFSIZE) 
    
    def _ask(self, data):                     
        self._send(data)
        return self._receive()
    
    ### This function tests the magnet status before we start to ramp
    ### used by set_field and rampTo, should not be used directly
    
    def _set_magnet_for_ramping(self):
        if self.get_quench():
            logging.error(__name__ +': Magnet quench')
            return False
        elif self.get_persistent():
            logging.error(__name__ +': Magnet set to persistent mode')
            return False
        else:
            temp=self.get_rampState()
            if temp == 4 or temp == 5:
                logging.error(__name__ +': Magnet set to manual ramp')
                return False
            elif temp == 6:
                logging.error(__name__ +': Magnet is ramping to zero')
                return False
            elif temp == 9 or temp == 10:
                logging.error(__name__ +': Persistent switch being heated or cooled')
                return False
            elif temp == 7:     #this should not happen, but better handle it
                logging.error(__name__ +': Magnet quench')
                return False                
            elif temp == 1:         #if ramping
                if self.get_pSwitch():          #if switch heater is ON, then proceed, otherwise return with error
                    return True
                else:
                    logging.error(__name__ +': Already ramping with switch heater off (persistent mode?)')
                    return False   
            elif temp == 2 or temp == 3 or temp == 8:         #if holding or paused, or zero, we can proceed
                return True
            else:
                logging.error(__name__ +': Invalid status received')
                return False
        return False        

    #### RAMP state commands #####
    #### Don't use them directly unless you know what you are doing

    ##issue RAMP state
    ##magnet will start to ramp to setpoint   
    
    def setRamp(self):
        self._send('RAMP\n')
        self.get_rampState()
    
    ##issue PAUSE state
    ##magnet will stop ramping immediately  
      
    def setPause(self):
        self._send('PAUSE\n')
        self.get_rampState()
    
    ##issue ZERO state
    ##magnet will ramp to zero (regardless of earlier PAUSE)
    
    def setZero(self):
        self._send('ZERO\n')
        self.get_rampState()
        
    
    #### Persistent switch on-off commands #####
    #### WARNING: THERE IS NO BUILT-IN CHECK TO AVOID MAGNET QUENCH (TODO) ######
        
    def do_get_pSwitch(self):
        return (int(self._ask('PS?\n')) == 1)
         
    def do_set_pSwitch(self,value):
        if value:
            self._send('PS 1\n')
            time.sleep(0.5)
            while (self.get_rampState() == 9):           #Polling for finished heating/cooling
                time.sleep(0.3)
            return
        else:
            self._send('PS 0\n')
            time.sleep(0.5)
            while (self.get_rampState() == 10):
                time.sleep(0.3)
            return
    
    #### Rampstate query commands ####
    
    def do_get_rampState(self):
        return int(self._ask('STATE?\n'))
    
    ### Ramprate set and query ###
    ### Note: we only use a single segment that spawns over the entire field range ###


    def do_get_rampRate_get_T_s(self):
        return float(self._ask('RAMP:RATE:FIELD:1?\n').split(',',1)[0])     ##Max. current is also returned and has to be removed
    
    def do_set_rampRate_T_s(self, value):
        #self._send('CONF:RAMP:RATE:FIELD 1,%0.5f,self.FIELDRATING;'%value)        ##Note: max field has to be added to command
        self._send('CONF:RAMP:RATE:FIELD 1,'+str(value)+','+str(self.FIELDRATING)+'\n')        ##Note: max field has to be added to command    
    #### Field setting and readout #######
    ### Note: get_field always returns actual field, for reading setpoint, see get_setPoint
    def do_get_field_get(self):                              
        self.get_rampState()                             ### update rampstate as well
        return float(self._ask('FIELD:MAG?\n'))    

    def do_set_field(self,value,wait=True):                              ### Set field
        self.setPause()
        self._send('CONF:FIELD:TARG %0.5f ;'%value)  ### the unit
        self.setRamp() 
        if wait:
            while math.fabs(value - self.get_field()) > self.MARGIN:
                time.sleep(0.050)

        return True     

    def do_get_current_get(self):                              
        self.get_rampState()                             ### update rampstate as well
        return float(self._ask('CURR:MAG?\n'))          
        
    def do_set_current(self,value):                              ### Set current %0.5f
        self.setPause()
        self._send('CONF:CURR:TARG %0.5f ;'%value)
        self.setRamp() 
    
    ### Note: get_field always returns actual field, for reading setpoint, see get_setPoint

    def do_set_units(self,value):
            self._send('CONF:FIELD:UNITS %d\n'%value)   

    def do_get_units(self):
            self._send(self._ask('FIELD:UNITS?\n'))         
    
    def rampTo(self,value):
        if self._set_magnet_for_ramping() and value <= self.get_parameter_options('field')['maxval'] and value >= self.get_parameter_options('field')['minval']:
            self.setPause()
            self._send('CONF:FIELD:TARG '+str(value)+'\n')
            if not self.get_pSwitch():
                self.set_pSwitch(True)
            self.setRamp()
            self.get_setPoint()
            return True 
        else:
            logging.error(__name__+': rampTo '+ str(value) + 'failed')
            return False

    ###query setpoint
    ###for reading actual field, see get_field
    
    def do_get_setPoint(self):
        self.get_rampState()                        #also updates rampState
        return float(self._ask('FIELD:TARG?\n'))

    #### Quench query command
    #### Note that quench reset command differs for safety reasons. See below!

    def do_get_quench(self):
        return (int(self._ask('QU?\n')) == 1)
    
    #### Quench reset command. Only use if you know what you are doing!

    def resetQuench(self):
        return self._send('QU 0\n')
    
    #### Persistent mode set and query

    def do_get_persistent(self):
        return (int(self._ask('PERS?\n')) == 1)
    
    def do_set_persistent(self, value):
        if value:
            if self.get_persistent():           #already in persistent mode, nothing to do
                return True
            else:
                temp = self.get_rampState()
                if not ( temp == 2 or temp == 3 ):  #persistent mode only accepted if magnet is idle (holding or paused)
                    logging.error(__name__ + ': setting persistent mode failed, because of magnet status' + str(temp))
                    return False
                else:
                    self.set_pSwitch(False)
                    self.setZero()
                    time.sleep(0.5)
                    while(self.get_rampState() == 6):    #waiting for zeroing to finish
                        time.sleep(0.3)
                    time.sleep(2.0)
                    if self.get_persistent() and self.get_rampState == 8:   #check for successful setting
                        return True
                    else:
                        logging.error(__name__ + ': Setting persistent mode failed, magnet status is ' + str(self.get_rampState()))
                        return False
        else:
            if not self.get_persistent():       #already in driven mode, nothing to do
                return True
            else:
                temp = self.get_rampState()
                if not ( temp == 2 or temp == 3 or temp == 8 ):  #persistent mode only accepted if magnet is idle (holding or paused or at zero)
                    logging.error(__name__ + ': setting driven mode failed, because of magnet status ' + str(temp))
                    return False
                else:
                    if self.set_field(self.get_field()):           #not a typo! this ramps to the value where the magnet was set to persistent mode
                        self.set_pSwitch(True)
                        return True
                    else:
                        logging.error(__name__ + ': setting driven mode failed, magnet cannot ramp to specified value')
                        return False
                    
                    
    def do_get_error(self):
        return self._ask('SYST:ERR?\n').rstrip() 
       