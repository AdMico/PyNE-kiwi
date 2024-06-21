"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Jakob Seidl
"""

import pyvisa as visa
import Instrument
import numpy as np
import time

@Instrument.enableOptions
class YokogawaGS200(Instrument.Instrument):
    # Default options to set/get when the instrument is passed into the sweeper
    defaultOutput = "sourceLevel"
    defaultInput = "senseLevel"

    def __init__(self, address):
        super(YokogawaGS200, self).__init__()
        self.dev = visa.ResourceManager().open_resource("GPIB0::"+str(address)+"::INSTR")
        print((self.dev.query("*IDN?"))) # Probably should query and check we have the right device        
        #self.dev.write("*RST")
        # self.dev.write("*CLS")
        self.type ="YokogawaGS200"  #We can check each instrument for its type and react accordingly
        self.name = 'myYokogawaGS200'

    @Instrument.addOptionSetter("name")
    def _setName(self,instrumentName):
         self.name = instrumentName
         
    @Instrument.addOptionGetter("name")
    def _getName(self):
        return self.name
    
    @Instrument.addOptionSetter("outputEnable")
    def _setOutputEnable(self, enable):
        self.dev.write(":OUTP " + ("ON" if enable else "OFF"))
        
    @Instrument.addOptionSetter("sourceMode")
    def _setSourceMode(self, mode):
        if mode == "voltage":
            # Source a voltage, sense a current
            self.dev.write("SOUR:FUNC VOLT")            
        elif mode == "current":
            # Source a current, sense a voltage
            self.dev.write("SOUR:FUNC CURR")
        else:
            raise ValueError(
                "\"{}\" is not a valid source mode for the YokogawaGS200.".format(mode) +
                " The mode must either be \"voltage\" or \"current\""
            )

    @Instrument.addOptionGetter("sourceMode")
    def _getSourceMode(self):
        mode = self.dev.query("SOURCE:FUNC?")
        if mode == "VOLT\n":
            return "voltage"
        elif mode == "CURR\n":
            return "current"
        else:
            raise RuntimeError("Unknown source mode {}".format(mode))

    @Instrument.addOptionSetter("sourceRange")
    def _setSourceRange(self,sourceRange):  
        mode = self._getSourceMode()
        if (mode == 'voltage'):
            if float(sourceRange) in (0.01,0.1,1,10,30):
                self.dev.write("SOUR:RANG "+str(sourceRange))  
            else:
                print("Error! Accepted ranges for voltage are: 0.01, 0.1, 1, 10, 30 Volts")
        elif(mode == 'current'):    
            if float(sourceRange) in (0.001,0.01,0.1,0.2):
                self.dev.write("SOUR:RANG "+str(sourceRange))                     
            else:
                print("Error! Accepted ranges for currents are: 0.001, 0.01, 0.1, 0.2 Amperes") 

    @Instrument.addOptionGetter("sourceRange")
    def _getSourceRange(self):
        return float(self.dev.query("SOUR:RANG?"))

    @Instrument.addOptionSetter('sourceLevel')
    def _setSourceLevel(self,sourceLevel):
        Limits = 1.2*self._getSourceRange()  #the yokogawa can put out a voltage/current 20% higher than the actual range, e.g. 12mV at the 10mV range.
        if (Limits > sourceLevel and sourceLevel > -Limits):
                self.dev.write("SOUR:LEVEL "+str(sourceLevel))
        else:
                raise ValueError(
                    "Specified source level output of \"{} V/A \" not possible in the given voltage range.".format(sourceLevel))
                
    @Instrument.addOptionGetter('sourceLevel')
    def _getSourceLevel(self):
        return float(self.dev.query("SOUR:LEVEL?"))
    
    @Instrument.addOptionSetter('compliance')
    def _setCompliance(self,compliance):
        mode = self._getSourceMode()  
        sourceRange = self._getSourceRange()
        if (mode == 'voltage' and sourceRange in (30,10,1)): # when sourcing a voltage we want current compliance
            if 0.001 <= float(compliance) <=0.1:
                self.dev.write("SOUR:PROT:CURR "+str(compliance))
            else:
                raise ValueError(
                    "Specified source protection of \"{} A \" not possible in the given voltage range. Also take into account that the YokogawaGS200 only accepts current protection for the 30,10 and 1 Volt voltage ranges.".format(compliance))
        elif (mode == 'current'): # when sourcing a current we want voltage compliance
             if 1 <= float(compliance) <=30:
                self.dev.write("SOUR:PROT:VOLT "+str(compliance))

    def goTo(self,target,stepsize= 0.002,delay=0.10):
        currentOutput = self.get('sourceLevel')
        sign = 1 if (target>currentOutput) else -1
        sweepArray = np.arange(currentOutput,target+sign*stepsize,sign*stepsize)
        for point in sweepArray:
            self.set('sourceLevel',point)
            time.sleep(delay)
        self.set('sourceLevel',target)
    
    def close(self):
            self.dev.close()