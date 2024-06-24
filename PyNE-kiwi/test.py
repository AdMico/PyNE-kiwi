"""
Brought to v1.0.0 on Mon Jun 24 2024 by APM

@author: Adam Micolich
"""

import pyvisa
from pymeasure.instruments.agilent import AgilentB1500

## Establish Resource List
rm = pyvisa.ResourceManager()
ResList = rm.list_resources()
print(ResList)

## Hook up the B2201A and call it
B2201A = rm.open_resource('GPIB0::22::INSTR')
print(B2201A.query("*IDN?"))

## Hook up the GPIB Interface and call it
Inter = rm.open_resource('USB0::0x0957::0x0001::0001::INSTR')
print(Inter.query("*IDN?"))

## Hook up the B1500 and call it
# explicitly define r/w terminations; set sufficiently large timeout in milliseconds or None.
B1500 = AgilentB1500('USB0::0x0957::0x0001::0001::INSTR', read_termination='\r\n', write_termination='\r\n', timeout=60000)
#B1500 = AgilentB1500('USB0::0x0957::0x0001::0001::INSTR', timeout = 60000)
B1500.initialize_all_smus()
B1500.smu1.force('Voltage','Auto Ranging',0.0)