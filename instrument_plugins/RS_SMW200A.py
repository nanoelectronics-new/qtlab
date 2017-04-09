# RS_SMF100A class, to perform the communication between the Wrapper and the device
# Sandesh Kalantre <kalantresandesh@gmail.com>
# Josip Kukucka <josip.kukucka@ist.ac.at>
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
import pyvisa
import types
import logging

class RS_SMW200A(Instrument):
    '''
    This is the python driver for the Rohde & Schwarz RS_SMW200A
    vector signal generator

    Usage:
    Initialize with
    <name> = instruments.create('name', 'RS_SMW200A', address='<GPIB address>',
        reset=<bool>)
    '''

    def __init__(self, name, address, reset=False):
        '''
        Initializes the RS_SMW200A, and communicates with the wrapper.

        Input:
            name (string)    : name of the instrument
            address (string) : GPIB address / IP address
            reset (bool)     : resets to default values, default=false

        Output:
            None
        '''
        logging.info(__name__ + ' : Initializing instrument')
        Instrument.__init__(self, name, tags=['physical'])



        self._address = address
        #self._visainstrument = visa.instrument(self._address)

        self._visainstruments = pyvisa.ResourceManager()
        if self._address is not None:
            self._visainstrument = self._visainstruments.open_resource(self._address)

        self.add_parameter('frequency', type=types.FloatType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET,
            minval=100e3, maxval=20e9,
            units='Hz', format='%.04e',
            tags=['sweep'])
        self.add_parameter('power', type=types.FloatType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET,
            minval=-30, maxval=30, units='dBm',
            tags=['sweep'])
        self.add_parameter('status', type=types.StringType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)
        self.add_parameter('IQ_status', type=types.StringType,
            flags=Instrument.FLAG_GETSET | Instrument.FLAG_GET_AFTER_SET)

        self.add_function('reset')
        self.add_function('get_all')
        self.add_function('adjust_IQ_mod_frek')

        if reset:
            self.reset()
        else:
            self.get_all()

    # Functions
    def reset(self):
        '''
        Resets the instrument to default values

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : Resetting instrument')
        self._visainstrument.write('*RST')
        self.get_all()

    def get_all(self):
        '''
        Reads all implemented parameters from the instrument,
        and updates the wrapper.

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : reading all settings from instrument')
        self.get_frequency()
        self.get_power()
        self.get_status()

    def adjust_IQ_mod_frek(self):
        '''
        Starts adjustment of the I/Q modulator for the currently set frequency and baseband gain

        Input:
            None

        Output:
            None
        '''

        logging.info(__name__ + ' : adjusting IQ modulator frequency')
        return float(self._visainstrument.ask('CAL:IQM:LOC?'))

    # communication with machine

    def do_get_frequency(self):
        '''
        Get frequency from device

        Input:
            None

        Output:
            frequency (float) : frequency in Hz
        '''
        logging.debug(__name__ + ' : reading frequency from instrument')
        return float(self._visainstrument.ask('SOUR:FREQ?'))

    def do_set_frequency(self, frequency):
        '''
        Set frequency of device

        Input:
            frequency (float) : frequency in Hz

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting frequency to %s GHz' % frequency)
        self._visainstrument.write('SOUR:FREQ %e' % frequency)

    def do_get_power(self):
        '''
        Get output power from device

        Input:
            None

        Output:
            power (float) : output power in dBm
        '''
        logging.debug(__name__ + ' : reading power from instrument')
        return float(self._visainstrument.ask('SOUR:POW?'))

    def do_set_power(self,power):
        '''
        Set output power of device

        Input:
            power (float) : output power in dBm

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting power to %s dBm' % power)
        self._visainstrument.write('SOUR:POW %e' % power)

    def do_get_status(self):
        '''
        Get status from instrument

        Input:
            None

        Output:
            status (string) : 'on or 'off'
        '''
        logging.debug(__name__ + ' : reading status from instrument')
        stat = str(int(self._visainstrument.ask('OUTP?')))

        if stat == '1':
            return 'on'
        elif stat == '0':
            return 'off'
        else:
            raise ValueError('Output status not specified : %s' % stat)

    def do_set_status(self,status):
        '''
        Set status of instrument

        Input:
            status (string) : 'on or 'off'

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting status to "%s"' % status)
        if status.upper() in ('ON', 'OFF'):
            status = status.upper()
        else:
            raise ValueError('set_status(): can only set on or off')
        self._visainstrument.write(':OUTP:STAT %s' % status)

    # shortcuts
    def off(self):
        '''
        Set status to 'off'

        Input:
            None

        Output:
            None
        '''
        self.set_status('off')

    def on(self):
        '''
        Set status to 'on'

        Input:
            None

        Output:
            None
        '''
        self.set_status('on')



    def do_get_IQ_status(self):
        '''
        Get IQ status from instrument

        Input:
            None

        Output:
            status (string) : 'on or 'off'
        '''
        logging.debug(__name__ + ' : reading status from instrument')
        stat = str(int(self._visainstrument.ask('IQ:STAT?')))

        if stat == '1':
            return 'on'
        elif stat == '0':
            return 'off'
        else:
            raise ValueError('Output status not specified : %s' % stat)

    def do_set_IQ_status(self,status):
        '''
        Set status of instrument

        Input:
            status (string) : 'on or 'off'

        Output:
            None
        '''
        logging.debug(__name__ + ' : setting status to "%s"' % status)
        if status.upper() in ('ON', 'OFF'):
            status = status.upper()
        else:
            raise ValueError('set_status(): can only set on or off')
        self._visainstrument.write('IQ:STAT %s' % status)

    # shortcuts
    def IQ_off(self):
        '''
        Set status to 'off'

        Input:
            None

        Output:
            None
        '''
        self.set_IQ_status('off')

    def IQ_on(self):
        '''
        Set status to 'on'

        Input:
            None

        Output:
            None
        '''
        self.set_IQ_status('on')
