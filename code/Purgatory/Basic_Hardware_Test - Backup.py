"""
Brought to PyNE-kiwi v1.0.0 on Mon Jun 24 2024 by APM

@developers: Adam Micolich

@author: Adam Micolich

Backup only, hold during GateSweepDev fork life, deprecate at next major 10SEP24 APM

Code for testing hardware comms is working correctly for B1500, B2200, K2401 and the RPi controlled relays
Code will set K2401 gate source to 1V, read the output current, and then do quick I-V tests using the B1500 for the
open, odd, even and ground configurations of the B2200 and RPi relays. It will finish by clearing the B2200 and
deactivating the K2401. With a 100kohm test chip in place, you should see results consistent (1uA per 0.1V) in the
Odd and Even configuration IVs and no current flowing in the Clear and Ground configurations. 09SEP24 APM
"""

import pyvisa
import time
from qcodes.instrument_drivers.Keysight import KeysightB1500
from qcodes.instrument_drivers.Keysight.keysightb1500 import MessageBuilder, constants
from Pi_control import PiMUX
from K2401 import K2401

def B2201_odd():
    B2201.write(":ROUT:OPEN:CARD 1") # Need to clear before next setting otherwise you get the OR of both settings -- 09SEP24 APM
    B2201.write(":ROUT:CLOS (@10101,11002,10203,11004,10305,11006,10407,11008,10909,10910,10911,10912)")

def B2201_even():
    B2201.write(":ROUT:OPEN:CARD 1") # Need to clear before next setting otherwise you get the OR of both settings -- 09SEP24 APM
    B2201.write(":ROUT:CLOS (@11001,10102,11003,10204,11005,10306,11007,10408,10909,10910,10911,10912)")

def B2201_ground():
    B2201.write(":ROUT:OPEN:CARD 1") # Need to clear before next setting otherwise you get the OR of both settings -- 09SEP24 APM
    B2201.write(":ROUT:CLOS (@11001,11002,11003,11004,11005,11006,11007,11008,10909,10910,10911,10912)")

def B2201_clear():
    B2201.write(":ROUT:OPEN:CARD 1")

def B1500_init():
    B1500.autozero_enabled(False)
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

    B1500.use_nplc_for_high_resolution_adc(n=1)
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

def smu_run():
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

if __name__ == "__main__": # execute only if this script is run, not when it's being
    print("")
    print("Hardware test run for basic comms testing -- V1.0 09SEP24 APM")
    print("")
    ## Establish the VISA Resource List
    rm = pyvisa.ResourceManager()
    ResList = rm.list_resources()
    #print(ResList)

    ## Hook up the B1500 and ask for its ID.
#    B1500_visa = rm.open_resource('USB0::0x0957::0x0001::0001::INSTR')
#    print('B1500 ID: ', B1500_visa.query("*IDN?"))

    ## Initialise B1500
    print("")
    B1500 = KeysightB1500("SPA", address="USB0::0x0957::0x0001::0001::INSTR")
    print("")
    B1500.smu1.enable_outputs()
    B1500.smu2.enable_outputs()
    B1500.smu3.enable_outputs()
    B1500.smu4.enable_outputs()

    ## Hook up the B2201 and ask for its ID.
    B2201 = rm.open_resource('GPIB0::22::INSTR')
    print('B2201 ID: ',B2201.query("*IDN?"))

    ## Initialise B2201
    B2201.write(":ROUT:FUNC NCON")
    B2201.write(":ROUT:CONN:RULE 1,FREE")
    B2201.write(":ROUT:CONN:SEQ 1,BBM")
    B2201.write(":ROUT:OPEN:CARD 1")

    ## Hook up the K2401 and ask for its ID.
    #    K2401_visa = rm.open_resource('GPIB0::24::INSTR')
    #    print('K2401 ID: ',K2401_visa.query("*IDN?"))
    K2401 = K2401(24)
    K2401.setOptions(
        {"beepEnable": True, "sourceMode": "voltage", "sourceRange": 1, "senseRange": 1.05e-6,
         "compliance": 1.0E-8, "scaleFactor": 1})

    ## Initialise Pi Connection
    CtrlPi = PiMUX()

    ## Commence hardware test run.
    K2401._setOutputEnable("enable")
    K2401._setSourceLevel(1.0)
    VG = K2401._getSourceLevel()
    print("K2401 output voltage: ",VG, "volts")
    time.sleep(1)
    IG = K2401._getSenseLevel()
    print("K2401 output current: ", IG, "amps")
    print("")
    B1500_init()
    print("SMU run - Open")
    smu_run()
    print("")
    time.sleep(3)
    B2201_odd()
    CtrlPi.DP_odd()
    print("SMU run - Odd")
    smu_run()
    print("")
    time.sleep(3)
    B2201_even()
    CtrlPi.DP_even()
    print("SMU run - Even")
    smu_run()
    print("")
    time.sleep(3)
    B2201_ground()
    print("SMU run - Ground")
    smu_run()
    print("")
    time.sleep(3)
    B2201_clear()
    K2401._setSourceLevel(0.0)
    K2401._setOutputEnable("")

    err = B1500.error_message()
    print("B1500 error status:",err)

## Store house of old test commands below
#MM = B1500.get_measurement_mode()
#print(MM)
#FMT = B1500.get_response_format_and_mode()
#print(FMT)