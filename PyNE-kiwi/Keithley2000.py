"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Jakob Seidl
"""

import pyvisa as visa
import Instrument
import numpy as np
import time

@Instrument.enableOptions
class Keithley2000(Instrument.Instrument):
    # Default options to set/get when the instrument is passed into the sweeper
    defaultOutput = "sourceLevel"
    defaultInput = "senseLevel"

    def __init__(self, address):
        super(Keithley2000, self).__init__()
        self.dev = visa.ResourceManager().open_resource("GPIB0::"+str(address)+"::INSTR")
        print((self.dev.query("*IDN?"))) # Probably should query and check we have the right device
        
        #self.dev.write("*RST")
        # self.dev.write("*CLS")
        self.type ="Keithley2000"  #We cna check each instrument for its type and react accordingly
        self.name = 'myKeithley2000'
        self.scaleFactor = 1.0
#    @Instrument.addOptionSetter("beepEnable")
#    def _setBeepEnable(self, enable):
#        self.dev.write(":SYST:BEEP:STAT " + ("ON" if enable else "OFF"))

    @Instrument.addOptionSetter("name")
    def _setName(self,instrumentName):
         self.name = instrumentName
         
    @Instrument.addOptionGetter("name")
    def _getName(self):
        return self.name
    
    @Instrument.addOptionSetter("senseMode")
    def _setSenseMode(self,senseMode):
        if senseMode == 'voltage':
            self.dev.write('CONF:VOLT')
        elif senseMode == 'current':
            self.dev.write('CONF:CURR')
    
    @Instrument.addOptionGetter("senseMode")
    def _getSenseMode(self):
        senseMode = str(self.dev.query('FUNC?'))[1:-5]
        if senseMode == 'VOLT':
            return 'voltage'
        elif senseMode == 'CURR':
            return 'current'
    
    @Instrument.addOptionSetter("senseRange")   #Voltage sense ranges: 100mV, 1V, 10V,100V, 1000V
    def _setSenseRange(self, senseRange):
        mode = self.get("senseMode", forceCached = False)
        if (mode == "voltage"): # when sourcing a voltage we usually sense current aka set its range
            if float(senseRange) in (100E-3,1,10,100,1000):   
                self.dev.write("SENS:VOLT:RANG "+str(senseRange))
            else:
                raise ValueError(
                    "\"{}\" is not a valid voltage measurement range for the Keithley200.".format(senseRange) +
                    " Valid voltage sensing ranges are: 100E-3,1,10,100,1000 Volts and equivalent representations."
                )
        elif (mode == "current"): # when sourcing a current we sense voltage 
            if float(senseRange) in (10E-3,100E-3,1,3):   
                self.dev.write("SENS:CURR:RANG "+str(senseRange))
            else:
                raise ValueError(
                    "\"{}\" is not a valid current measurement range for the Keithley200.".format(senseRange) +
                    " Valid current sensing ranges are: 10E-3,100E-3,1,3 Amps and equivalent representations."
                )
#
    @Instrument.addOptionGetter("senseLevel")
    def _getSenseLevel(self):
        tempData = self.dev.query_ascii_values(":READ?")
        if abs(tempData[0])> 1E10:
            res = float('nan')
        else: res = float(tempData[0])/self.scaleFactor 
        return res
        
#    @Instrument.addOptionSetter("compliance")
#    def _setCompliance(self,compliance,currOrVolt=None): #currOrVolt is an optional paramter. you can use it to specify whether you want to set the current or voltage protection. If not give, the function will change the current compliance when in voltage sourcing mode and vice versa.
#        mode = currOrVolt
#        if mode == None:
#            mode = self.get("sourceMode", forceCached = True)
#            
#        if (mode == "voltage" and 0.001E-6 <= float(compliance) <= 1.05): # when sourcing a voltage we want current compliance
#            self.dev.write("SENS:CURR:PROT "+str(compliance))
#
#
#        elif (mode == "current" and 0.2E-3 <= compliance <= 21): # when sourcing a current we want voltage compliance
#            self.dev.write("SENS:VOLT:PROT "+str(compliance))
#
#
#        else:
#            raise ValueError(
#                "\"{}\" is not a valid current/voltage protection value (compliance) for the Keithley2401.".format(compliance) +
#                " Current compliance must be between 1.05 Amps - 0.001E-6 Amps (including bounds). /n Voltage protection values must be between 21 V and 0.2mV."
#            )
            
    @Instrument.addOptionGetter("scaleFactor")
    def _getScaleFactor(self):
        return self.scaleFactor
    
    @Instrument.addOptionSetter("scaleFactor")
    def _setScaleFactor(self,scaleFactor):
        self.scaleFactor = scaleFactor
       
    def close(self):
        self.dev.close()
        
    def goTo(self,target,stepsize= 0.001,delay=0.2):
        return    #This set the unit to the final value, even if the target value does not fit together with the stepsize.