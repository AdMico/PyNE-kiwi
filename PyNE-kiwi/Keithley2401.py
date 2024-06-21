"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Jakob Seidl
"""

import pyvisa as visa
import Instrument
import numpy as np
import time

@Instrument.enableOptions
class Keithley2401(Instrument.Instrument):
    # Default options to set/get when the instrument is passed into the sweeper
    defaultOutput = "sourceLevel"
    defaultInput = "senseLevel"

    def __init__(self, address):
        super(Keithley2401, self).__init__()
        self.dev = visa.ResourceManager().open_resource("GPIB0::"+str(address)+"::INSTR")
        print((self.dev.query("*IDN?"))) # Probably should query and check we have the right device        
        #self.dev.write("*RST")
        # self.dev.write("*CLS")
        self.type ="Keithley2401"  #We can check each instrument for its type and react accordingly
        self.scaleFactor = 1.0
        self.currentSourceSetpoint = float('nan')
        self.hitCompliance = []
        self.sourceMode = self._getSourceMode()
        self.sourceLimits = 100 #Dummy number to be replaced by setSourceRange function

    @Instrument.addOptionSetter("beepEnable")
    def _setBeepEnable(self, enable):
        self.dev.write(":SYST:BEEP:STAT " + ("ON" if enable else "OFF"))

    @Instrument.addOptionSetter("outputEnable")
    def _setOutputEnable(self, enable):
        self.dev.write(":OUTP " + ("ON" if enable else "OFF"))
    
    @Instrument.addOptionSetter("sourceMode")
    def _setSourceMode(self, mode):
        if mode == "voltage":
            # Source a voltage, sense a current
            self.dev.write("SOUR:FUNC VOLT")
            self.dev.write("SENS:FUNC 'CURR'")
            self.sourceMode = 'voltage'
        elif mode == "current":
            # Source a current, sense a voltage
            self.dev.write("SOUR:FUNC CURR")
            self.dev.write("SENS:FUNC 'VOLT'")
            self.sourceMode = 'current'
        else:
            raise ValueError(
                "\"{}\" is not a valid source mode for the Keithley2401.".format(mode) +
                " The mode must either be \"voltage\" or \"current\""
            )

    @Instrument.addOptionGetter("sourceMode")
    def _getSourceMode(self):
        mode = self.dev.query("SOUR:FUNC:MODE?")
        if mode == "VOLT\n":
            return "voltage"
        elif mode == "CURR\n":
            return "current"
        else:
            raise RuntimeError("Unknown source mode {}".format(mode))

    @Instrument.addOptionSetter("sourceRange")
    def _setSourceRange(self, sourceRange):  
        mode = self.get("sourceMode", forceCached = False)

        if (mode == "voltage"): 
            if float(sourceRange) in (20,10,1,0.1,0.01,0.001):
                self.dev.write("SOUR:VOLT:RANG "+str(sourceRange))
                self.sourceLimits = 1.3*float(sourceRange)
            else:
                raise ValueError(
                    "\"{}\" is not a valid voltage source range for the Keithley2401.".format(sourceRange) +
                    " Valid voltage ranges are: 20, 10, 1, 0.1, 0.01 and 0.001 Volts and equivalent exponential representations."
                )
        elif (mode == "current"):   
            if float(sourceRange) in (1,0.1,0.01,0.001,1E-4,1E-5,1E-6):
                self.dev.write("SOUR:CURR:RANG "+str(sourceRange))   #Dummy function. Have to ignore false inputs and accept 1E-2 as well as 1e-2 etc.
                self.sourceLimits = 1.3*float(sourceRange)
            else:
                raise ValueError(
                    "\"{}\" is not a valid current source range for the Keithley2401.".format(sourceRange) +
                    " Valid voltage ranges are: 1, 0.1, 0.01, 0.001, 1E-5 and 1E-6 Amps and equivalent exponential representations."
                )

    @Instrument.addOptionGetter("sourceLevel")
    def _getSourceLevel(self):
       # mode = self.get("sourceMode", deprecated
        mode = self.sourceMode
        if (mode == "voltage"): #    
           return(float(self.dev.query("SOUR:VOLT?")))               
        elif (mode == "current"):  
            return(float(self.dev.query("SOUR:CURR?")))
           
    @Instrument.addOptionSetter("sourceLevel") 
    def _setSourceLevel(self, sourceLevel):
        #mode = self.get("sourceMode", deprecated
        mode = self.sourceMode
        if (mode == "voltage"): # when sourcing a voltage we want to set the voltage level =)   
            #Limits = float(self.dev.query("SOUR:VOLT:RANG?")) #Get the set range and thus deduce the limits we can put out. Deprecated
            if (self.sourceLimits > sourceLevel and sourceLevel > -self.sourceLimits):
                self.dev.write("SOUR:VOLT "+str(sourceLevel))
                self.currentSourceSetpoint = float(sourceLevel)
            else:
                raise ValueError(
                    "Specified voltage output of \"{} V\" not possible in the given voltage range.".format(sourceLevel)
                )               
        elif (mode == "current"): # when sourcing a current we want to set the current output level
            #Limits = float(self.dev.query("SOUR:CURR:RANG?")) #Get the set range and thus deduce the limits we can put out. Deprecated
            if (self.sourceLimits > sourceLevel and sourceLevel > -self.sourceLimits):
                self.dev.write("SOUR:CURR "+str(sourceLevel))
                self.currentSourceSetpoint = float(sourceLevel)
            else:
                raise ValueError(
                    "Specified current output of \"{} A\" not possible in the given current range.".format(sourceLevel)
                )

    @Instrument.addOptionSetter("senseRange")
    def _setSenseRange(self, senseRange):
        mode = self.get("sourceMode", forceCached = False)
        if (mode == "voltage"): # when sourcing a voltage we usually sense current aka set its range
            if float(senseRange) in (1.05E-4,1.05E-5,1.05E-6):   
                self.dev.write("SENS:CURR:RANG "+str(senseRange))
            else:
                raise ValueError(
                    "\"{}\" is not a valid current measurement range for the Keithley2401.".format(senseRange) +
                    " Valid current sensing ranges are: 1.05E-4, 1.05E-5 and 1.05E-6 Amps and equivalent representations."
                )
        elif (mode == "current"): # when sourcing a current we sense voltage 
            if float(senseRange) in (21.00,2.10,0.21):   
                self.dev.write("SENS:VOLT:RANG "+str(senseRange))
            else:
                raise ValueError(
                    "\"{}\" is not a valid voltage measurement range for the Keithley2401.".format(senseRange) +
                    " Valid voltage sensing ranges are: 21.00, 2.10 and 0.21 Volts and equivalent representations."
                )

    @Instrument.addOptionGetter("senseLevel")
    def _getSenseLevel(self):
        tempData = self.dev.query_ascii_values(":READ?")
        measInput = float(tempData[1])/self.scaleFactor 
        measOutput = float(tempData[0])        
        return measInput#,measOutput]
        
    @Instrument.addOptionSetter("compliance")
    def _setCompliance(self,compliance,currOrVolt=None): #currOrVolt is an optional paramter. you can use it to specify whether you want to set the current or voltage protection. If not give, the function will change the current compliance when in voltage sourcing mode and vice versa.
        mode = currOrVolt
        if mode == None:
            mode = self.get("sourceMode", forceCached = False)            
        if (mode == "voltage" and 0.001E-6 <= float(compliance) <= 1.05): # when sourcing a voltage we want current compliance
            self.dev.write("SENS:CURR:PROT "+str(compliance))
        elif (mode == "current" and 0.2E-3 <= compliance <= 21): # when sourcing a current we want voltage compliance
            self.dev.write("SENS:VOLT:PROT "+str(compliance))
        else:
            raise ValueError(
                "\"{}\" is not a valid current/voltage protection value (compliance) for the Keithley2401.".format(compliance) +
                " Current compliance must be between 1.05 Amps - 0.001E-6 Amps (including bounds). /n Voltage protection values must be between 21 V and 0.2mV."
            )
            
    @Instrument.addOptionGetter("scaleFactor")
    def _getScaleFactor(self):
        return self.scaleFactor
    
    @Instrument.addOptionSetter("scaleFactor")
    def _setScaleFactor(self,scaleFactor):
        self.scaleFactor = scaleFactor

    def goTo(self,target,stepsize= 0.01,delay=0.02):
        currentOutput = self.get('sourceLevel')
        sign = 1 if (target>currentOutput) else -1
        sweepArray = np.arange(currentOutput,target+sign*stepsize,sign*stepsize)
        for point in sweepArray:
            self.set('sourceLevel',point)
            time.sleep(delay)
        self.set('sourceLevel',target)     #This set the unit to the final value, even if the target value does not fit together with the stepsize.
       
    def close(self):
        self.dev.close()