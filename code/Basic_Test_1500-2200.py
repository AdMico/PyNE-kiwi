"""
Brought to PyNE-kiwi v1.0.0 on Mon Jun 24 2024 by APM

@developers: Adam Micolich

@author: Adam Micolich

Test code for establishing initial communication with B1500 and B2201 and testing basic functions
"""

import pyvisa
import time
from qcodes.instrument_drivers.Keysight import KeysightB1500
from qcodes.instrument_drivers.Keysight.keysightb1500 import MessageBuilder, constants

## Establish the VISA Resource List
rm = pyvisa.ResourceManager()
ResList = rm.list_resources()
#print(ResList)

## Hook up the B2201 and ask for its ID.
B2201 = rm.open_resource('GPIB0::22::INSTR')
#print('B2201 ID: ',B2201.query("*IDN?"))

## Hook up the K2401 and ask for its ID.
K2401 = rm.open_resource('GPIB0::24::INSTR')
#print('K2401 ID: ',K2401.query("*IDN?"))

## Hook up the B1500 and ask for its ID.
B1500_visa = rm.open_resource('USB0::0x0957::0x0001::0001::INSTR')
#print('B1500 ID: ',B1500_visa.query("*IDN?"))

## Initialise B1500
#B1500 = KeysightB1500('USB0::0x0957::0x0001::0001::INSTR', read_termination='\r\n', write_termination='\r\n', timeout=60000)
B1500 = KeysightB1500("SPA", address="USB0::0x0957::0x0001::0001::INSTR")
#B1500.initialize_all_smus()
B1500.smu1.enable_outputs()
B1500.smu2.enable_outputs()
B1500.smu3.enable_outputs()
B1500.smu4.enable_outputs()
#B1500.smu1.force('Voltage','Auto Ranging',0.0)
time.sleep(0.2)

## Initialise B2201
B2201.write(":ROUT:FUNC NCON")
B2201.write(":ROUT:CONN:RULE 1,FREE")
B2201.write(":ROUT:CONN:SEQ 1,BBM")
# Odd config below
#B2201.write(":ROUT:OPEN:CARD 1")
#B2201.write(":ROUT:CLOS (@10101,11002,10203,11004,10305,11006,10407,11008,10909,10910,10911,10912)")
# Even config below
#B2201.write(":ROUT:OPEN:CARD 1")
#B2201.write(":ROUT:CLOS (@11001,10102,11003,10204,11005,10306,11007,10408,10909,10910,10911,10912)")
# Nothing connected config below
B2201.write(":ROUT:OPEN:CARD 1")
time.sleep(0.2)

# Command Testing -- PyMeasure B1500
#B1500.smu1.force('Voltage','Auto Ranging',0.0)
#B1500.data_format(21, mode=1)
#B1500.adc_averaging = 1
#B1500.adc_auto_zero = True
#B1500.adc_setup('HRADC','AUTO',6)
#B1500.meas_mode('Spot', *B1500.smu_references)
#B1500.check_errors()
#B1500.clear_buffer()
#B1500.clear_timer()
#B1500.send_trigger()
#B1500.check_idle()
#data = B1500.smu_names()
#data = B1500.read_data(3)
#data = B1500.read_channels(1)
#print(data)

# Command Testing -- Qcodes B1500
B1500.autozero_enabled(True)
#B1500.self_calibration()
B1500.smu1.measurement_mode(constants.MM.Mode.SPOT)
B1500.smu2.measurement_mode(constants.MM.Mode.SPOT)
B1500.smu3.measurement_mode(constants.MM.Mode.SPOT)
B1500.smu4.measurement_mode(constants.MM.Mode.SPOT)

B1500.smu1.source_config(output_range=constants.VOutputRange.AUTO,compliance=1e-3,compl_polarity=None,min_compliance_range=constants.IOutputRange.AUTO)
B1500.smu2.source_config(output_range=constants.VOutputRange.AUTO,compliance=1e-3,compl_polarity=None,min_compliance_range=constants.IOutputRange.AUTO)
B1500.smu3.source_config(output_range=constants.VOutputRange.AUTO,compliance=1e-3,compl_polarity=None,min_compliance_range=constants.IOutputRange.AUTO)
B1500.smu4.source_config(output_range=constants.VOutputRange.AUTO,compliance=1e-3,compl_polarity=None,min_compliance_range=constants.IOutputRange.AUTO)

#B1500.use_nplc_for_high_speed_adc(n=1)
#B1500.smu1.use_high_speed_adc()
#B1500.smu2.use_high_speed_adc()
#B1500.smu3.use_high_speed_adc()
#B1500.smu4.use_high_speed_adc()

B1500.use_nplc_for_high_resolution_adc(n=2)
B1500.smu1.use_high_resolution_adc()
B1500.smu2.use_high_resolution_adc()
B1500.smu3.use_high_resolution_adc()
B1500.smu4.use_high_resolution_adc()

B1500.smu1.enable_filter(False)
B1500.smu2.enable_filter(False)
B1500.smu3.enable_filter(False)
B1500.smu4.enable_filter(False)

B1500.smu1.measurement_operation_mode(constants.CMM.Mode.COMPLIANCE_SIDE)
B1500.smu2.measurement_operation_mode(constants.CMM.Mode.COMPLIANCE_SIDE)
B1500.smu3.measurement_operation_mode(constants.CMM.Mode.COMPLIANCE_SIDE)
B1500.smu4.measurement_operation_mode(constants.CMM.Mode.COMPLIANCE_SIDE)

B1500.smu1.i_measure_range_config(i_measure_range=constants.IMeasRange.MIN_100mA)
B1500.smu2.i_measure_range_config(i_measure_range=constants.IMeasRange.MIN_100mA)
B1500.smu3.i_measure_range_config(i_measure_range=constants.IMeasRange.MIN_100mA)
B1500.smu4.i_measure_range_config(i_measure_range=constants.IMeasRange.MIN_100mA)

B1500.smu1.v_measure_range_config(v_measure_range=constants.VMeasRange.FIX_2V)
B1500.smu2.v_measure_range_config(v_measure_range=constants.VMeasRange.FIX_2V)
B1500.smu3.v_measure_range_config(v_measure_range=constants.VMeasRange.FIX_2V)
B1500.smu4.v_measure_range_config(v_measure_range=constants.VMeasRange.FIX_2V)

B1500.smu1.voltage(0.0)
B1500.smu2.voltage(0.0)
B1500.smu3.voltage(0.0)
B1500.smu4.voltage(0.0)
vol1 = B1500.smu1.voltage()
cur1 = B1500.smu1.current()
vol2 = B1500.smu2.voltage()
cur2 = B1500.smu2.current()
vol3 = B1500.smu3.voltage()
cur3 = B1500.smu3.current()
vol4 = B1500.smu4.voltage()
cur4 = B1500.smu4.current()
print("SMU1 I=",cur1,"SMU1 V=",vol1,"SMU2 I=",cur2,"SMU2 V=",vol2,"SMU3 I=",cur3,"SMU3 V=",vol3,"SMU4 I=",cur4,"SMU4 V=",vol4)

B1500.smu1.voltage(0.1)
B1500.smu2.voltage(0.1)
B1500.smu3.voltage(0.1)
B1500.smu4.voltage(0.1)
vol1 = B1500.smu1.voltage()
cur1 = B1500.smu1.current()
vol2 = B1500.smu2.voltage()
cur2 = B1500.smu2.current()
vol3 = B1500.smu3.voltage()
cur3 = B1500.smu3.current()
vol4 = B1500.smu4.voltage()
cur4 = B1500.smu4.current()
print("SMU1 I=",cur1,"SMU1 V=",vol1,"SMU2 I=",cur2,"SMU2 V=",vol2,"SMU3 I=",cur3,"SMU3 V=",vol3,"SMU4 I=",cur4,"SMU4 V=",vol4)

B1500.smu1.voltage(0.2)
B1500.smu2.voltage(0.2)
B1500.smu3.voltage(0.2)
B1500.smu4.voltage(0.2)
vol1 = B1500.smu1.voltage()
cur1 = B1500.smu1.current()
vol2 = B1500.smu2.voltage()
cur2 = B1500.smu2.current()
vol3 = B1500.smu3.voltage()
cur3 = B1500.smu3.current()
vol4 = B1500.smu4.voltage()
cur4 = B1500.smu4.current()
print("SMU1 I=",cur1,"SMU1 V=",vol1,"SMU2 I=",cur2,"SMU2 V=",vol2,"SMU3 I=",cur3,"SMU3 V=",vol3,"SMU4 I=",cur4,"SMU4 V=",vol4)

B1500.smu1.voltage(0.3)
B1500.smu2.voltage(0.3)
B1500.smu3.voltage(0.3)
B1500.smu4.voltage(0.3)
vol1 = B1500.smu1.voltage()
cur1 = B1500.smu1.current()
vol2 = B1500.smu2.voltage()
cur2 = B1500.smu2.current()
vol3 = B1500.smu3.voltage()
cur3 = B1500.smu3.current()
vol4 = B1500.smu4.voltage()
cur4 = B1500.smu4.current()
print("SMU1 I=",cur1,"SMU1 V=",vol1,"SMU2 I=",cur2,"SMU2 V=",vol2,"SMU3 I=",cur3,"SMU3 V=",vol3,"SMU4 I=",cur4,"SMU4 V=",vol4)

B1500.smu1.voltage(0.0)
B1500.smu2.voltage(0.0)
B1500.smu3.voltage(0.0)
B1500.smu4.voltage(0.0)

err = B1500.error_message()
print(err)
MM = B1500.get_measurement_mode()
print(MM)
FMT = B1500.get_response_format_and_mode()
print(FMT)
