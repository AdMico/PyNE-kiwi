"""
Brought to v1.0.0 on Tue June 25 2024 by APM

Development space for B1500 Hardware Commands --- to be deleted for initial release version

@author: Adam  Micolich
"""

import pyvisa
import Instrument
import numpy as np
import time
from pymeasure.instruments.agilent import AgilentB1500

# Hook up instrument connection
B1500 = AgilentB1500('USB0::0x0957::0x0001::0001::INSTR', read_termination='\r\n', write_termination='\r\n', timeout=6000)

# Pull ID back.
print(B1500.id) #Documentation has incorrect usage, there should be no brackets after the id.
rm = pyvisa.ResourceManager()
B1500A = rm.open_resource('USB0::0x0957::0x0001::0001::INSTR')
ID = B1500A.query('*IDN?')
print('Machine ID: ',ID)

# SMU initialization is required to be able to address single SMUs
B1500.initialize_all_smus()
#B1500.data_format(21,mode=1) #call after SMUs are initialized to get names for the channels

# Test enabling a SMU
B1500.smu1.enable()

# Test setting a SMU voltage
B1500.smu1.force('Voltage','Auto Ranging',1.0)

# Test setting a measurement mode

B1500.smu1.adc_type = 'HSADC' #set ADC to high-speed ADC
B1500.smu1.meas_range_current = '1 nA'
B1500.smu1.meas_op_mode = 'Voltage' # other choices: Current, Voltage, FORCE_SIDE, COMPLIANCE_AND_FORCE_SIDE, COMPLIANCE_SIDE

B1500.smu1.sampling_source('VOLTAGE','Auto Ranging',0,1,0.001) #MV/MI: type, range, base, bias, compliance

#print(B1500.query_learn(1))
#print(B1500.query_modules())

#B1500.meas_mode('Spot',1,2,3,4)
# Test reading a SMU voltage
#B1500.check_errors()
#B1500.clear_buffer()
#B1500.clear_timer()
#B1500.send_trigger()

# read measurement data all at once
#B1500.check_idle() #wait until measurement is finished
#data = B1500.read_data(1)
#print(data)

B1500.smu1.force('Voltage','Auto Ranging',0.0)

## I hate to say this, but the PyMeasure route to this is looking to be extremely shit. Some cursory attempts at a more direct approach.

B1500A.write("DV 1,0,1") # Set SMU 1 to 1V with autoranging
B1500A.write("MM 1,1") # Set SMU to measurement mode 1 (spot measurement)
B1500A.write("RV 1,0") # Set SMU 1 to autorange
B1500A.write("XE") # Trigger measurement
data = B1500A.read_raw()
print(data)
time.sleep(2)

B1500A.write("DV 1,0,2") # Set SMU 1 to 2V with autoranging
B1500A.write("MM 1,1") # Set SMU to measurement mode 1 (spot measurement)
B1500A.write("RV 1,0") # Set SMU 1 to autorange
B1500A.write("XE") # Trigger measurement
data = B1500A.read_raw()
print(data)
time.sleep(2)

B1500A.write("DV 1,0,3") # Set SMU 1 to 3V with autoranging
B1500A.write("MM 1,1") # Set SMU to measurement mode 1 (spot measurement)
B1500A.write("RV 1,0") # Set SMU 1 to autorange
B1500A.write("XE") # Trigger measurement
data = B1500A.read_raw()
print(data)
time.sleep(2)

B1500A.write("DV 1,0,0") # Set SMU 1 to 0V with autoranging