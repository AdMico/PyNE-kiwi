"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Jan Gluschke
"""

import pyvisa as visa
import time
import Instrument
import math

@Instrument.enableOptions
class Keithley6517A(Instrument.Instrument):
    # Default options to set/get when the instrument is passed into the sweeper
    #defaultOutput = "sourceLevel"
    defaultInput = "senseLevel"
    
    def __init__(self, address):
        super(Keithley6517A, self).__init__()
        self.dev = visa.ResourceManager().open_resource("GPIB0::"+str(address)+"::INSTR")
        print((self.dev.query("*IDN?"))) # Probably should query and check we have the right device
        self.type ="Keithley6517A" 
        self.name = 'myElectrometer'
        self.senseMode = 'current'
        self.zeroCheckEnable = True
        
        self.autoRange = False       
        self.possibleCurrRanges = [20E-12,200E-12,2E-9,20E-9,200E-9,2E-6,20E-6,200E-6,2E-3,20E-3]
        #self.possibleCurrAutoRanges = [200E-12,200E-9,2E-6,200E-6,2E-3,20E-3] #default for all ranges
        self.possibleCurrAutoRanges = [2E-9,200E-9,2E-6,20E-6,2E-3,20E-3] #A subset of 'self.possibleCurrRanges'!!
        self.possibleVoltRanges = [2,20,200]
        self.rangeIndex =  self.possibleCurrRanges.index(self._getSenseRange())          
        self.rangeDic = {  #we shift the lower intervals 30% (-> 0.7*number) downwards so they dont overlap with the bounds when we shift up.
            0:[15E-18,1.8E-9],
            1:[1*1E-9,180*1E-9],
            2:[130E-9,1.8*1E-6],
            3:[0.7*1E-6,17E-6],
            4:[15*1E-6,1.7E-3],
            5:[1.5*1E-3,20E-3],
            }
    
    @Instrument.addOptionSetter("name")
    def _setName(self,instrumentName):
         self.name = instrumentName
         
    @Instrument.addOptionGetter("name")
    def _getName(self):
        return self.name
    
    @Instrument.addOptionSetter("zeroCheck")    
    def _setZeroCheckEnable(self,enable):
        self.dev.write("SYST:ZCH "+("1" if enable else "0"))
        self.zeroCheckEnable = enable
        time.sleep(1)
        
    @Instrument.addOptionGetter("zeroCheck")    
    def _getZeroCheckEnable(self):
        zeroCheck = self.dev.query("SYST:ZCH?")
        if zeroCheck == '1\n': 
            return True
        elif zeroCheck == '0\n': 
            return False
        else:
            raise RuntimeError("Unknown zeroCheck mode.".format(zeroCheck))
    
    @Instrument.addOptionSetter("senseMode")
    def _setSenseMode(self,mode):     
        if mode == "voltage": 
            self.dev.write("SENS:FUNC 'VOLT'")
            self.senseMode = "voltage"
        elif mode == "current": 
            self.dev.write("SENS:FUNC 'CURR'")
            self.senseMode = "current"
        else:
            raise RuntimeError("\"{}\" is not a valid current/voltage measurement mode. Choose between 'voltage' or 'current'".format(mode))
    
    @Instrument.addOptionGetter("senseMode")
    def _getSenseMode(self):
        mode = self.dev.query("CONF?")
        if mode == '"VOLT:DC"\n': 
            self.senseMode = 'voltage'
            return "voltage"
        elif mode == '"CURR:DC"\n': 
            self.senseMode = 'current'
            return "current"
        else:
            raise RuntimeError("Unknown senseMode".format(mode))  

    @Instrument.addOptionGetter("senseLevel")
    def _getSenseLevel(self):
        if self.zeroCheckEnable:
            self.set('zeroCheck',False)
        
        #tempData = self.dev.query("READ?")
        tempData = self.dev.query(':FETCh?')
        divideIndex = tempData.find(",")
        result = float(tempData[0:divideIndex-4])
        if abs(result)> 1E10:
            result = float('nan')
        if self.autoRange:
            self._autoSensitivity(result)
        
        return result
    
    @Instrument.addOptionSetter("autoRange")
    def _setAutoRange(self,enable):
        if enable in (True,False):
            self.autoRange = enable
            if self._getSenseRange() in self.possibleCurrAutoRanges:
                self.rangeIndex =  self.possibleCurrAutoRanges.index(self._getSenseRange())
                self._setSenseRange(self.possibleCurrAutoRanges[self.rangeIndex]) #Not sure
                time.sleep(0.5)#Not sure
            else:
                self._setSenseRange(self.possibleCurrAutoRanges[-1])
                self.rangeIndex = self.possibleCurrAutoRanges.index(self._getSenseRange())
                self._setSenseRange(self.possibleCurrAutoRanges[self.rangeIndex]) #Not sure
                time.sleep(0.5)#Not sure
        else:
            raise RuntimeError("Unknown autoRange mode".format(enable))  
    
    @Instrument.addOptionGetter("autoRange")
    def _getAutoRange(self):
        return self.autoRange
    
    @Instrument.addOptionGetter("senseRange")
    def _getSenseRange(self):
        if self.senseMode == 'voltage':
            return float(self.dev.query(":VOLT:RANG?"))
        elif self.senseMode =='current':
            return float(self.dev.query(":CURR:RANG?"))  
        
    @Instrument.addOptionSetter("senseRange")
    def _setSenseRange(self,senseRange):

        if self.senseMode == 'current':
            if senseRange in self.possibleCurrRanges:
                self.dev.write(":CURR:RANG "+str(senseRange))
            else:
                raise RuntimeError("\"{}\" is not a valid current measurement range for the Keithley6517A electrometer".format(senseRange)+
                 "Possible values are \"{}\"".format(self.possibleCurrRanges))
        
        elif (self.senseMode =='voltage' and senseRange in self.possibleVoltRanges):
             self.dev.write(":VOLT:RANG "+str(senseRange))
             
    def _autoSensitivity(self,givenValue):
            R = abs(givenValue)
#            print('#############\n')
#            print('current value is'+str(R)+'\n')
#            print('current range index is: '+str(self.rangeIndex)+'\n')
#            print('the boundaries here are: '+str(self.rangeDic[self.rangeIndex][0]) +'and' + str(self.rangeDic[self.rangeIndex][1])+'\n')
#            print('#############\n')
            if (self.rangeDic[self.rangeIndex][0] >= R): #If current is below the current lower bound: Move one range down!  #and not math.isnan(R)
                a = self.rangeIndex -1
                if a in range(len(self.rangeDic)):
                    self.rangeIndex = a
                    #print(a)
                    self._setSenseRange(self.possibleCurrAutoRanges[self.rangeIndex])
                    time.sleep(0.5)
            elif (R > self.rangeDic[self.rangeIndex][1]): #If current is above the current higher bound: Move one range up!  
                a = self.rangeIndex +1
                if a in range(len(self.rangeDic)):
                    self.rangeIndex = a
                    #print(a)
                    self._setSenseRange(self.possibleCurrAutoRanges[self.rangeIndex])
                    time.sleep(0.5)
            else:
                if math.isnan(R): #when we measure a nan, better increase the range! This de=escalates the autorange when values change too quickly for the electrometer                   
                    a = self.rangeIndex +1
                    if a in range(len(self.rangeDic)):
                        self.rangeIndex = a
                        #print(a)
                        self._setSenseRange(self.possibleCurrAutoRanges[self.rangeIndex])
                        time.sleep(0.5)    

    @Instrument.addOptionSetter("NPLC")
    def _setNPLC(self,NPLCs):
        if (NPLCs >= 0.01 and NPLCs <= 10):
            if self._getSenseMode() == "current":
                self.dev.write('CURR:NPLC '+str(NPLCs))
            elif self._getSenseMode() == 'voltage':
                self.dev.write('VOLT:NPLC '+str(NPLCs))
        else:
            raise RuntimeError("\"{}\" is not a valid NPLC input for the Keithley6517A electrometer".format(NPLCs)+
                 "Choose a value between 0.01 and 10.")

    @Instrument.addOptionGetter("NPLC")
    def _getNPLC(self):
        if self._getSenseMode() == 'current':
            NPLCs = self.dev.query('CURR:NPLC?')
            return float(NPLCs)
        else:
            NPLCs = self.dev.query('VOLT:NPLC?')
            return float(NPLCs)
    def close(self):
        self.set('zeroCheck',True)
        self.dev.close()
        
#[:SENSe[1]]:VOLTage[:DC]:RANG:AUTO
# [:SENSe[1]]:FUNC 'VOLT'  #Maybe this is the real measure mode not the one defined above...