"""
Brought to v1.0.0 on Mon Jun 24 2024 by APM

Test code for establishing initial communication with B1500 and B2201 and testing basic functions

@author: Adam Micolich
"""

import pyvisa
import time
from pymeasure.instruments.agilent import AgilentB1500

## Establish the VISA Resource List
rm = pyvisa.ResourceManager()
ResList = rm.list_resources()
print(ResList)

## Hook up the B2201 and ask for its ID.
B2201 = rm.open_resource('GPIB0::22::INSTR')
print('B2201 ID: ',B2201A.query("*IDN?"))

## Hook up the B1500 and ask for its ID.
B1500 = rm.open_resource('USB0::0x0957::0x0001::0001::INSTR')
print('B1500 ID: ',B1500.query("*IDN?"))

## Hook up the B1500 to PyMeasure and use it to set a voltage
B1500 = AgilentB1500('USB0::0x0957::0x0001::0001::INSTR', read_termination='\r\n', write_termination='\r\n', timeout=60000)
#B1500 = AgilentB1500('USB0::0x0957::0x0001::0001::INSTR', timeout = 60000)
B1500.initialize_all_smus()
B1500.smu1.force('Voltage','Auto Ranging',1.0)
time.sleep(5)

## Get the B2201 to set up a switch set.
B2201.write(":ROUT:FUNC NCON")
B2201.write(":ROUT:CONN:RULE 1,FREE")
B2201.write(":ROUT:CONN:SEQ 1,BBM")
B2201.write(":ROUT:CLOS (@10101,10202,10303,10404,11005,11006,11007,11008,10909,11010,11011,11012)")
time.sleep(5)
B2201.write(":ROUT:CLOS (@11001,11002,11003,11004,10105,10206,10307,10408,10909,11010,11011,11012)")
time.sleep(5)
B2201.write(":ROUT:OPEN:CARD 1")
time.sleep(5)

B1500.smu1.force('Voltage','Auto Ranging',0.0)