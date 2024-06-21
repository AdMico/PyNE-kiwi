"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Adam Micolich

This is a virtual instrument for running ISFETs for pH sensing using the NI-USB6216
It maintains specified source-drain bias and aims to hold specified source-drain current
by adjusting gate voltage using a PID controller circuit, which we are using in software.
Implicit assumption that source is ao0, gate is ao1, drain is ai0.
Current return is the PID-stable gate voltage value
"""

import Instrument
import time
import PID

@Instrument.enableOptions
class pHMeter(Instrument.Instrument):
    # Default options to set/get when the instrument is passed into the sweeper
    defaultInput = "pHLevel"
    defaultOutput = "pHLevel"

    def __init__(self):
        super(pHMeter, self).__init__()
        self.type ="pHMeter"  #We can check each instrument for its type and react accordingly
        self.name = "pHMeter"
        self.scaleFactor = 1.0 #Default to define variable
        self.sleepTime = 0.1 #Default to define variable
        self.gain = 1e4 #Default to define variable
        self.driveCurrentAim = 3e-5 #Default to define variable
        
        # 1) Initialize Real Instruments inside this Virtual Instrument
        #---- NIDAQ Output Port for Source --------------
        self.pHDaqOut_S = USB6216Out(0)
        self.pHDaqOut_S.setOptions({
                "feedBack":"Int",
                "extPort":6, # Can be any number 0-7 if in 'Int'  
                "scaleFactor":self.scaleFactor
                })

        #---- NIDAQ Output Port for Gate --------------
        self.pHDaqOut_G = USB6216Out(1)
        self.pHDaqOut_G.setOptions({
                "feedBack":"Int",
                "extPort":7, # Can be any number 0-7 if in 'Int'  
                "scaleFactor":self.scaleFactor
                })

        #---- NIDAQ Input Port for Drain --------------
        self.pHDaqIn_D = USB6216In(0)
        self.pHDaqIn_D.setOptions({
                "scaleFactor":self.gain
                })
        
    @Instrument.addOptionSetter("name")
    def _setName(self,instrumentName):
         self.name = instrumentName
         
    @Instrument.addOptionGetter("name")
    def _getName(self):
        return self.name

    @Instrument.addOptionSetter("sourceVoltage")
    def _setSourceVoltage(self,sourceVoltage):
        currSourVolt = self.pHDaqOut_S._getOutputLevel()
        if (currSourVolt == sourceVoltage):
            pass
        else:
            self.pHDaqOut_S.goTo(sourceVoltage,delay=0.001)
            
    @Instrument.addOptionGetter("sourceVoltage")
    def _getSourceVoltage(self):
        currSourVolt = self.pHDaqOut_S._getOutputLevel()
        return currSourVolt
    
    @Instrument.addOptionSetter("gateVoltage")
    def _setGateVoltage(self,gateVoltage):
        currGateVolt = self.pHDaqOut_G._getOutputLevel()
        if (currGateVolt == gateVoltage):
            pass
        else:
            self.pHDaqOut_G.goTo(gateVoltage,delay=0.001)
            
    @Instrument.addOptionGetter("gateVoltage")
    def _getGateVoltage(self):
        currGateVolt = self.pHDaqOut_G._getOutputLevel()
        return currGateVolt
            
    @Instrument.addOptionSetter("driveCurrentAim")
    def _setDriveCurrentAim(self,driveCurrentAim):
        self.driveCurrentAim = driveCurrentAim

    @Instrument.addOptionGetter("driveCurrentAim")
    def _getDriveCurrentAim(self):
        return self.driveCurrentAim
    
    @Instrument.addOptionGetter("driveCurrentActual")
    def _getDriveCurrentActual(self):
        currDriveCurr = self.pHDaqIn_D._getInputLevel()
        return currDriveCurr

    @Instrument.addOptionGetter("pHLevel")
    def _getPHLevel(self):
        pid = PID.PID(self.P, self.I, self.D)
        pid.setSetPoint(self.driveCurrentAim)
        currGateVolt = self.pHDaqOut_G._getOutputLevel()
        currDriveCurr = self.pHDaqIn_D._getInputLevel()
        pid.update(currDriveCurr)
        output = pid.output
        newGateVolt = currGateVolt + output
        self.pHDaqOut_G.goTo(newGateVolt,delay=0.001)
        time.sleep(self.sleepTime)
        currDriveCurr = self.pHDaqIn_D._getInputLevel()
        offset = abs(currDriveCurr - self.driveCurrentAim)
        while offset >= self.offsetThreshold:
            currGateVolt = self.pHDaqOut_G._getOutputLevel()
            pid.update(currDriveCurr)
            output = pid.output
            newGateVolt = currGateVolt + output
            self.pHDaqOut_G.goTo(newGateVolt,delay=0.001)    
            time.sleep(self.sleepTime)
            currDriveCurr = self.pHDaqIn_D._getInputLevel()
            offset = abs(currDriveCurr - self.driveCurrentAim)
        return newGateVolt
        
    @Instrument.addOptionGetter("scaleFactor")
    def _getScaleFactor(self):
        return self.scaleFactor
    
    @Instrument.addOptionSetter("scaleFactor")
    def _setScaleFactor(self,scaleFactor):
        self.scaleFactor = scaleFactor
        
    @Instrument.addOptionGetter("sleepTime")
    def _getSleepTime(self):
        return self.sleepTime
    
    @Instrument.addOptionSetter("sleepTime")
    def _setSleepTime(self,sleepTime):
        self.sleepTime = sleepTime
        
    @Instrument.addOptionGetter("P")
    def _getP(self):
        return self.P
    
    @Instrument.addOptionSetter("P")
    def _setP(self,P):
        self.P = P
        
    @Instrument.addOptionGetter("I")
    def _getI(self):
        return self.I
    
    @Instrument.addOptionSetter("I")
    def _setI(self,I):
        self.I = I
        
    @Instrument.addOptionGetter("D")
    def _getD(self):
        return self.D
    
    @Instrument.addOptionSetter("D")
    def _setD(self,D):
        self.D = D
            
    @Instrument.addOptionGetter("offsetThreshold")
    def _getOffsetThreshold(self):
        return self.offsetThreshold
    
    @Instrument.addOptionSetter("offsetThreshold")
    def _setOffsetThreshold(self,offsetThreshold):
        self.offsetThreshold = offsetThreshold    
        
    def close(self):
#        print('Return outputs to zero')
        self.pHDaqOut_G.goTo(0.0,delay=0.001)
        self.pHDaqOut_S.goTo(0.0,delay=0.001)