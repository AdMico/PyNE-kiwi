"""
Brought to PyNE-kiwi v1.0.0 on Mon Sep 2 2024 by APM

@developers: Adam Micolich

@author: Adam Micolich

Development of SMU2 setup for Keysight B1500A using K2401_SMU.py from PyNE-probe/

NOTE 08SEP24 APM -- Stripped back to bare minimum functions and will add things in as some K2401 features are unimplementable in B1500.
Will just comment out these functions for now, deprecate properly in a future version.
"""

import Instrument
import numpy as np
import time
from Config import Diags
from qcodes.instrument_drivers.Keysight import KeysightB1500
from qcodes.instrument_drivers.Keysight.keysightb1500 import constants, MessageBuilder

@Instrument.enableOptions
class B1500_SMU2(Instrument.Instrument):
    # Default options to set/get when the instrument is passed into the sweeper
    defaultOutput = "sourceLevel"
    defaultInput = "senseLevel"

    def __init__(self):
        super(B1500_SMU2, self).__init__()
        self.dev = B1500.smu2
        self.type ="B1500_SMU2"  #We can check each instrument for its type and react accordingly
        self.scaleFactor = 1.0
        self.currentSourceSetpoint = float('nan')
        self.hitCompliance = []
#        self.sourceMode = self._getSourceMode() ## Line dysfunctional presently to fix later -- 03SEP24 APM
        self.sourceMode = "voltage"
        self.SMUnum = 2
        self.sourceLimits = 2 #Dummy number to be replaced by setSourceRange function, 2V used currently re: Config.py -- 08SEP24 APM

    @Instrument.addOptionSetter("outputEnable")
    def _setOutputEnable(self, enable):
        if enable:
            self.dev.enable_outputs()
        else:
            self.dev.disable_outputs()

    @Instrument.addOptionGetter("sourceLevel")
    def _getSourceLevel(self):
        mode = self.sourceMode
        if (mode == "voltage"):
           return(float(self.dev.voltage()))
        elif (mode == "current"):
            return(float(self.dev.current()))

    @Instrument.addOptionSetter("sourceLevel") 
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

    @Instrument.addOptionGetter("senseLevel")
    def _getSenseLevel(self):
        tempData = self.dev.current()
        measInput = float(tempData) / self.scaleFactor
#        measOutput = float(tempData[0])  # Just having this one off for now, need to understand CMM better -- 08SEP24 APM
        return measInput  # ,measOutput

    @Instrument.addOptionGetter("scaleFactor")
    def _getScaleFactor(self):
        return self.scaleFactor

    @Instrument.addOptionSetter("scaleFactor")
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

## Commenting this function as I don't know how to sensibly implement in the Keysight B1500, possible future deprecate -- 03SEP24 APM
#    @Instrument.addOptionSetter("sourceMode")
#    def _setSourceMode(self, mode):
#        if mode == "voltage":
#            # Source a voltage, sense a current
#            self.dev.write("SOUR:FUNC VOLT")
#            self.dev.write("SENS:FUNC 'CURR'")
#            self.sourceMode = 'voltage'
#        elif mode == "current":
#            # Source a current, sense a voltage
#            self.dev.write("SOUR:FUNC CURR")
#            self.dev.write("SENS:FUNC 'VOLT'")
#            self.sourceMode = 'current'
#        else:
#            raise ValueError(
#                "\"{}\" is not a valid source mode for the Keithley2401.".format(mode) +
#                " The mode must either be \"voltage\" or \"current\""
#            )

## Commenting this as a problem for later, this is doable but not urgent -- 03SEP24
#    @Instrument.addOptionGetter("sourceMode")
#    def _getSourceMode(self):
#        mode = self.dev.query("SOUR:FUNC:MODE?")
#        if mode == "VOLT\n":
#            return "voltage"
#        elif mode == "CURR\n":
#            return "current"
#        else:
#            raise RuntimeError("Unknown source mode {}".format(mode))

## Commenting this as a problem for later, this is doable but not urgent, but do we need it -- 03SEP24
#    @Instrument.addOptionSetter("sourceRange")
#    def _setSourceRange(self, sourceRange): ## Set to fixed range and auto only -- 08SEP24 APM
#        mode = self.get("sourceMode", forceCached = False)
#        if (mode == "voltage"):
#            if float(sourceRange) in (100,40,20,5,2,0.5): ## Set to Limited Autorange
#                if sourceRange == 100:
#                    self.dev.source_config(output_range=constants.VOutputRange.MIN_100V,compliance=B1500ICOM1,compl_polarity=None,min_compliance_range=B1500MCR1)
#                elif sourceRange == 40:
#                    self.dev.source_config(output_range=constants.VOutputRange.MIN_40V,compliance=B1500ICOM1,compl_polarity=None,min_compliance_range=B1500MCR1)
#                elif sourceRange == 20:
#                    self.dev.source_config(output_range=constants.VOutputRange.MIN_20V,compliance=B1500ICOM1,compl_polarity=None,min_compliance_range=B1500MCR1)
#                elif sourceRange == 5:
#                    self.dev.source_config(output_range=constants.VOutputRange.MIN_5V,compliance=B1500ICOM1,compl_polarity=None,min_compliance_range=B1500MCR1)
#                elif sourceRange == 2:
#                    self.dev.source_config(output_range=constants.VOutputRange.MIN_2V,compliance=B1500ICOM1,compl_polarity=None,min_compliance_range=B1500MCR1)
#                elif sourceRange == 0.5:
#                    self.dev.source_config(output_range=constants.VOutputRange.MIN_0V5,compliance=B1500ICOM1,compl_polarity=None,min_compliance_range=B1500MCR1)
#                self.sourceLimits = 1.3*float(sourceRange)
#            elif sourceRange == "AUTO"
#                self.dev.source_config(output_range=constants.VOutputRange.AUTO,compliance=B1500ICOM1,compl_polarity=None,min_compliance_range=B1500MCR1)
#            else:
#                raise ValueError(
#                    "\"{}\" is not a valid voltage source range for the Keysight B1500.".format(sourceRange) +
#                    " Valid voltage ranges are: 100, 40, 20, 5, 2 and 0.5 Volts and equivalent exponential representations."
#                )
#        elif (mode == "current"): # I need to sort this trainwreck out.
#            if float(sourceRange) in (0.1,0.01,1E-3,1E-4,1E-5,1E-6,1E-7,1E-8,1E-9,1E-10,1E-11,1E-12):
#                if sourceRange == 0.1:
#                    self.dev.write("RI " + str(self.SMUnum) + ",19")
#                elif sourceRange == 0.01:
#                    self.dev.write("RI " + str(self.SMUnum) + ",18")
#                elif sourceRange == 1E-3:
#                    self.dev.write("RI " + str(self.SMUnum) + ",17")
#                elif sourceRange == 1E-4:
#                    self.dev.write("RI " + str(self.SMUnum) + ",16")
#                elif sourceRange == 1E-5:
#                    self.dev.write("RI " + str(self.SMUnum) + ",15")
#                elif sourceRange == 1E-6:
#                    self.dev.write("RI " + str(self.SMUnum) + ",14")
#                elif sourceRange == 1E-7:
#                    self.dev.write("RI " + str(self.SMUnum) + ",13")
#                elif sourceRange == 1E-8:
#                    self.dev.write("RI " + str(self.SMUnum) + ",12")
#                elif sourceRange == 1E-9:
#                    self.dev.write("RI " + str(self.SMUnum) + ",11")
#                elif sourceRange == 1E-10:
#                    self.dev.write("RI " + str(self.SMUnum) + ",10")
#                elif sourceRange == 1E-11:
#                    self.dev.write("RI " + str(self.SMUnum) + ",9")
#                elif sourceRange == 1E-12:
#                    self.dev.write("RI " + str(self.SMUnum) + ",8")
#                self.sourceLimits = 1.3*float(sourceRange)
#            else:
#                raise ValueError(
#                    "\"{}\" is not a valid current source range for the Keysight B1500.".format(sourceRange) +
#                    " Valid voltage ranges are: 0.1 to 1E-12 Amps in decades and equivalent exponential representations."
#                )

## Going to deal with current mode later on when I have things working for voltage properly -- 08SEP24 APM
#        elif (mode == "current"): # when sourcing a current we want to set the current output level
#            if (self.sourceLimits > sourceLevel and sourceLevel > -self.sourceLimits):
#                self.dev.write("SOUR:CURR "+str(sourceLevel))
#                self.currentSourceSetpoint = float(sourceLevel)
#            else:
#                raise ValueError(
#                    "Specified current output of \"{} A\" not possible in the given current range.".format(sourceLevel)
#                )

## Going to leave this one for later, I think we can deprecate this one for simplicity -- 08SEP24 APM
#    @Instrument.addOptionSetter("senseRange")
#    def _setSenseRange(self, senseRange):
#        mode = self.get("sourceMode", forceCached = False)
#        if (mode == "voltage"): # when sourcing a voltage we usually sense current aka set its range
#            if float(senseRange) in (1.05E-4,1.05E-5,1.05E-6):
#                self.dev.write("SENS:CURR:RANG "+str(senseRange))
#            else:
#                raise ValueError(
#                    "\"{}\" is not a valid current measurement range for the Keithley2401.".format(senseRange) +
#                    " Valid current sensing ranges are: 1.05E-4, 1.05E-5 and 1.05E-6 Amps and equivalent representations."
#                )
#        elif (mode == "current"): # when sourcing a current we sense voltage
#            if float(senseRange) in (21.00,2.10,0.21):
#                self.dev.write("SENS:VOLT:RANG "+str(senseRange))
#            else:
#                raise ValueError(
#                    "\"{}\" is not a valid voltage measurement range for the Keithley2401.".format(senseRange) +
#                    " Valid voltage sensing ranges are: 21.00, 2.10 and 0.21 Volts and equivalent representations."
#                )

## Leaving for later, we can really simplify this one a lot -- 08SEP24 APM
#    @Instrument.addOptionSetter("compliance")
#    def _setCompliance(self,compliance,currOrVolt=None): #currOrVolt is an optional paramter. you can use it to specify whether you want to set the current or voltage protection. If not give, the function will change the current compliance when in voltage sourcing mode and vice versa.
#        mode = currOrVolt
#        if mode == None:
#            mode = self.get("sourceMode", forceCached = False)
#        if (mode == "voltage" and 0.001E-6 <= float(compliance) <= 1.05): # when sourcing a voltage we want current compliance
#            self.dev.write("SENS:CURR:PROT "+str(compliance))
#        elif (mode == "current" and 0.2E-3 <= compliance <= 21): # when sourcing a current we want voltage compliance
#            self.dev.write("SENS:VOLT:PROT "+str(compliance))
#        else:
#            raise ValueError(
#                "\"{}\" is not a valid current/voltage protection value (compliance) for the Keithley2401.".format(compliance) +
#                " Current compliance must be between 1.05 Amps - 0.001E-6 Amps (including bounds). /n Voltage protection values must be between 21 V and 0.2mV."
#            )

## Do we even need this -- 08SEP24 APM
#    def close(self):
#        self.dev.close()