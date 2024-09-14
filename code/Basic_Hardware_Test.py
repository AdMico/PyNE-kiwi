"""
Brought to PyNE-kiwi v1.0.0 on Mon Jun 24 2024 by APM

@developers: Adam Micolich

@author: Adam Micolich

Major update 10SEP24 APM

Code for testing hardware comms is working correctly for B1500, B2200, K2401 and the RPi controlled relays
Code will set K2401 gate source to 1V, read the output current, and then do quick I-V tests using the B1500 for the
open, odd, even and ground configurations of the B2200 and RPi relays. It will finish by clearing the B2200 and
deactivating the K2401. With a 100kohm test chip in place, you should see results consistent (1uA per 0.1V) in the
Odd and Even configuration IVs and no current flowing in the Clear and Ground configurations. 09SEP24 APM
"""

import time
from Pi_control import PiMUX
from K2401 import K2401
from B1500 import B1500
from B2201 import B2201

def smu_run():
    B1500.setV1(0.0)
    B1500.setV2(0.0)
    B1500.setV3(0.0)
    B1500.setV4(0.0)
    vol1 = B1500.getV1()
    cur1 = B1500.getI1()
    vol2 = B1500.getV2()
    cur2 = B1500.getI2()
    vol3 = B1500.getV3()
    cur3 = B1500.getI3()
    vol4 = B1500.getV4()
    cur4 = B1500.getI4()
    print("SMU1 I=",cur1,"SMU1 V=",vol1,"SMU2 I=",cur2,"SMU2 V=",vol2,"SMU3 I=",cur3,"SMU3 V=",vol3,"SMU4 I=",cur4,"SMU4 V=",vol4)

    B1500.setV1(0.1)
    B1500.setV2(0.1)
    B1500.setV3(0.1)
    B1500.setV4(0.1)
    vol1 = B1500.getV1()
    cur1 = B1500.getI1()
    vol2 = B1500.getV2()
    cur2 = B1500.getI2()
    vol3 = B1500.getV3()
    cur3 = B1500.getI3()
    vol4 = B1500.getV4()
    cur4 = B1500.getI4()
    print("SMU1 I=",cur1,"SMU1 V=",vol1,"SMU2 I=",cur2,"SMU2 V=",vol2,"SMU3 I=",cur3,"SMU3 V=",vol3,"SMU4 I=",cur4,"SMU4 V=",vol4)

    B1500.setV1(0.2)
    B1500.setV2(0.2)
    B1500.setV3(0.2)
    B1500.setV4(0.2)
    vol1 = B1500.getV1()
    cur1 = B1500.getI1()
    vol2 = B1500.getV2()
    cur2 = B1500.getI2()
    vol3 = B1500.getV3()
    cur3 = B1500.getI3()
    vol4 = B1500.getV4()
    cur4 = B1500.getI4()
    print("SMU1 I=",cur1,"SMU1 V=",vol1,"SMU2 I=",cur2,"SMU2 V=",vol2,"SMU3 I=",cur3,"SMU3 V=",vol3,"SMU4 I=",cur4,"SMU4 V=",vol4)

    B1500.setV1(0.3)
    B1500.setV2(0.3)
    B1500.setV3(0.3)
    B1500.setV4(0.3)
    vol1 = B1500.getV1()
    cur1 = B1500.getI1()
    vol2 = B1500.getV2()
    cur2 = B1500.getI2()
    vol3 = B1500.getV3()
    cur3 = B1500.getI3()
    vol4 = B1500.getV4()
    cur4 = B1500.getI4()
    print("SMU1 I=",cur1,"SMU1 V=",vol1,"SMU2 I=",cur2,"SMU2 V=",vol2,"SMU3 I=",cur3,"SMU3 V=",vol3,"SMU4 I=",cur4,"SMU4 V=",vol4)

    B1500.setV1(0.0)
    B1500.setV2(0.0)
    B1500.setV3(0.0)
    B1500.setV4(0.0)

if __name__ == "__main__": # execute only if this script is run, not when it's being
    print("")
    print("Hardware test run for basic comms testing -- V1.1 10SEP24 APM")
    print("")

    ## Initialise B1500
    B1500 = B1500()
    B1500.init()

    ## Initialise B2201
    B2201 = B2201()
    B2201.init()

    ## Initialise K2401
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
    print("SMU run - Open")
    smu_run()
    print("")
    time.sleep(3)
    B2201.odd()
    CtrlPi.odd()
    print("SMU run - Odd")
    smu_run()
    print("")
    time.sleep(3)
    B2201.even()
    CtrlPi.even()
    print("SMU run - Even")
    smu_run()
    print("")
    time.sleep(3)
    B2201.ground()
    print("SMU run - Ground")
    smu_run()
    print("")
    time.sleep(3)
    B2201.clear()
    K2401._setSourceLevel(0.0)
    K2401._setOutputEnable("")

    err = B1500.err()
    print("B1500 error status:",err)

## Store house of old test commands below
#MM = B1500.get_measurement_mode()
#print(MM)
#FMT = B1500.get_response_format_and_mode()
#print(FMT)