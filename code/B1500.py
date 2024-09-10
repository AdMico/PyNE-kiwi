"""
Brought to PyNE-kiwi v1.0.0 on Mon Sep 2 2024 by APM

@developers: Adam Micolich

@author: Adam Micolich

Development of SMU setup for Keysight B1500A using K2401.py from PyNE-probe/

NOTE 10SEP24 APM -- Stripped back to bare minimum functions carried over from K2401 for now plus some
of my own new functions. Removed all the Instrument.Instrument baggage as part of longer-term code
clean-up and trimming of excess baggage.
"""

import numpy as np
import time
from qcodes.instrument_drivers.Keysight import KeysightB1500
from qcodes.instrument_drivers.Keysight.keysightb1500 import MessageBuilder, constants
from Config import B1500AutoZero,B1500ADCSet,B1500NPLC
from Config import B1500MM1,B1500MM2,B1500MM3,B1500MM4
from Config import B1500CMM1,B1500CMM2,B1500CMM3,B1500CMM4
from Config import B1500VOR1,B1500VOR2,B1500VOR3,B1500VOR4
from Config import B1500ICOM1,B1500ICOM2,B1500ICOM3,B1500ICOM4
from Config import B1500MCR1,B1500MCR2,B1500MCR3,B1500MCR4
from Config import B1500Filt1,B1500Filt2,B1500Filt3,B1500Filt4
from Config import B1500VMR1,B1500VMR2,B1500VMR3,B1500VMR4
from Config import B1500IMR1,B1500IMR2,B1500IMR3,B1500IMR4

class B1500():
    def __init__(self):
        super(B1500, self).__init__()
        self.dev = KeysightB1500("SPA", address="USB0::0x0957::0x0001::0001::INSTR")
        self.type ="B1500"  #We can check each instrument for its type and react accordingly
        self.scaleFactor = 1.0
        self.currentSourceSetpoint = float('nan')
        self.hitCompliance = []
        self.sourceMode = "voltage"
        self.sourceLimits = 2 #Dummy number to be replaced by setSourceRange function, 2V used currently re: Config.py -- 08SEP24 APM

    def B1500_init(self):
        # B1500 AutoZero
        self.dev.autozero_enabled(B1500AutoZero)
        # B1500 Measurement Mode
        self.dev.smu1.measurement_mode(B1500MM1)
        self.dev.smu2.measurement_mode(B1500MM2)
        self.dev.smu3.measurement_mode(B1500MM3)
        self.dev.smu4.measurement_mode(B1500MM4)
        # B1500 Source Configuration
        self.dev.smu1.source_config(output_range=B1500VOR1, compliance=B1500ICOM1, compl_polarity=None,
                                    min_compliance_range=B1500MCR1)
        self.dev.smu2.source_config(output_range=B1500VOR2, compliance=B1500ICOM2, compl_polarity=None,
                                    min_compliance_range=B1500MCR2)
        self.dev.smu3.source_config(output_range=B1500VOR3, compliance=B1500ICOM3, compl_polarity=None,
                                    min_compliance_range=B1500MCR3)
        self.dev.smu4.source_config(output_range=B1500VOR4, compliance=B1500ICOM4, compl_polarity=None,
                                    min_compliance_range=B1500MCR4)
        # B1500 Analog-Digital Converter Settings
        if B1500ADCSet == "HighSpeed":
            self.dev.use_nplc_for_high_speed_adc(n=B1500NPLC)
            self.dev.smu1.use_high_speed_adc()
            self.dev.smu2.use_high_speed_adc()
            self.dev.smu3.use_high_speed_adc()
            self.dev.smu4.use_high_speed_adc()
        elif B1500ADCSet == "HighRes":
            self.dev.use_nplc_for_high_resolution_adc(n=B1500NPLC)
            self.dev.smu1.use_high_resolution_adc()
            self.dev.smu2.use_high_resolution_adc()
            self.dev.smu3.use_high_resolution_adc()
            self.dev.smu4.use_high_resolution_adc()
        # B1500 Filter Settings
        self.dev.smu1.enable_filter(B1500Filt1)
        self.dev.smu2.enable_filter(B1500Filt2)
        self.dev.smu3.enable_filter(B1500Filt3)
        self.dev.smu4.enable_filter(B1500Filt4)
        # B1500 Compliance Measure Mode
        self.dev.smu1.measurement_operation_mode(B1500CMM1)
        self.dev.smu2.measurement_operation_mode(B1500CMM2)
        self.dev.smu3.measurement_operation_mode(B1500CMM3)
        self.dev.smu4.measurement_operation_mode(B1500CMM4)
        # B1500 Voltage Measure Range Setting
        self.dev.smu1.v_measure_range_config(v_measure_range=B1500VMR1)
        self.dev.smu2.v_measure_range_config(v_measure_range=B1500VMR2)
        self.dev.smu3.v_measure_range_config(v_measure_range=B1500VMR3)
        self.dev.smu4.v_measure_range_config(v_measure_range=B1500VMR4)
        # B1500 Current Measure Range Setting
        self.dev.smu1.i_measure_range_config(i_measure_range=B1500IMR1)
        self.dev.smu2.i_measure_range_config(i_measure_range=B1500IMR2)
        self.dev.smu3.i_measure_range_config(i_measure_range=B1500IMR3)
        self.dev.smu4.i_measure_range_config(i_measure_range=B1500IMR4)
        # Enable all four SMUs -- Moved to before settings of zero due to gate sweep software error 10SEP24 APM
        self.dev.smu1.enable_outputs()
        self.dev.smu2.enable_outputs()
        self.dev.smu3.enable_outputs()
        self.dev.smu4.enable_outputs()
        # Ensure all four SMUs are zeroed
        self.dev.smu1.voltage(0.0)
        self.dev.smu2.voltage(0.0)
        self.dev.smu3.voltage(0.0)
        self.dev.smu4.voltage(0.0)

    def B1500_setV1(self,value):
        self.dev.smu1.voltage(value)

    def B1500_setV2(self,value):
        self.dev.smu2.voltage(value)

    def B1500_setV3(self,value):
        self.dev.smu3.voltage(value)

    def B1500_setV4(self,value):
        self.dev.smu4.voltage(value)

    def B1500_setVall(self,value): # Currently write only might revise later -- 10SEP24 APM
        self.dev.smu1.voltage(value)
        self.dev.smu2.voltage(value)
        self.dev.smu3.voltage(value)
        self.dev.smu4.voltage(value)

    def B1500_getV1(self):
        return self.dev.smu1.voltage()

    def B1500_getV2(self):
        return self.dev.smu2.voltage()

    def B1500_getV3(self):
        return self.dev.smu3.voltage()

    def B1500_getV4(self):
        return self.dev.smu4.voltage()

    def B1500_getI1(self):
        return self.dev.smu1.current()

    def B1500_getI2(self):
        return self.dev.smu2.current()

    def B1500_getI3(self):
        return self.dev.smu3.current()

    def B1500_getI4(self):
        return self.dev.smu4.current()

    def B1500_err(self):
        err = self.dev.error_message()
        return err

    def _setOutputEnable(self, enable):
        if enable:
            self.dev.enable_outputs()
        else:
            self.dev.disable_outputs()

    def _setSourceLevel(self, sourceLevel):
        mode = self.sourceMode
        if (mode == "voltage"): # when sourcing a voltage we want to set the voltage level =)   
            if (self.sourceLimits > sourceLevel and sourceLevel > -self.sourceLimits):
                self.dev.voltage(float(sourceLevel))
                self.currentSourceSetpoint = float(sourceLevel)
            else:
                raise ValueError(
                    "Specified voltage output of \"{} V\" not possible in the given voltage range.".format(sourceLevel)
                )

    def _getSenseLevel(self):
        tempData = self.dev.current()
        measInput = float(tempData) / self.scaleFactor
#        measOutput = float(tempData[0])  # Just having this one off for now, need to understand CMM better -- 08SEP24 APM
        return measInput  # ,measOutput

    def _getScaleFactor(self):
        return self.scaleFactor

    def _setScaleFactor(self, scaleFactor):
        self.scaleFactor = scaleFactor

    def goTo(self, target, stepsize=0.01, delay=0.02):
        currentOutput = self.get('sourceLevel')
        sign = 1 if (target > currentOutput) else -1
        sweepArray = np.arange(currentOutput, target + sign * stepsize, sign * stepsize)
        for point in sweepArray:
            self.set('sourceLevel', point)
            time.sleep(delay)
            self.set('sourceLevel', target)  # This set the unit to the final value, even if the target value does not fit together with the stepsize.