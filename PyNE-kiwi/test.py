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

## Hook up the B1500A and call it
# explicitly define r/w terminations; set sufficiently large timeout in milliseconds or None.
B1500A = AgilentB1500("GPIB0::17::INSTR", read_termination='\r\n', write_termination='\r\n', timeout=600000)
B1500A.initialize_all_smus()
print(B1500A.id())