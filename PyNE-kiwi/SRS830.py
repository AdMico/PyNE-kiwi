"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Jakob Seidl
"""

import pyvisa as visa
import time
import math
import numpy as np
import Instrument

@Instrument.enableOptions        
class SRS830(Instrument.Instrument):
    defaultOutput = "sourceLevel"
    defaultInput = "senseLevel"
    def __init__(self, address):
        super(SRS830,self).__init__()
        self.dev = visa.ResourceManager().open_resource("GPIB0::"+str(address)+"::INSTR")
        print((self.dev.query("*IDN?"))) # Probably should query and check we have the right device       
        self.outputMode = "amplitude" # or "frequency"
        self.sweepDelay = 0.5
        self.type ="SRS830"
        self.name = 'mySRS830'
        self.scaleFactor = 1.0
        self.input = self._getInput()            
        self.autoSensitivityEnable = False
        self.possibleCurrRanges = [9,12,15,18,21,24,26]
        self.rangeIndex =  6 #random
        self.rangeDic = {  #we shift the lower intervals 30% (-> 0.7*number) downwards so they dont overlap with the bounds when we shift up.
            0:[15E-18,1.5E-12],
            1:[0.7*1.5E-12,15E-12],
            2:[0.7*15E-12,150E-12],
            3:[0.7*150E-12,1.5E-9],
            4:[0.7*1.5E-9,15E-9],
            5:[0.7*15E-9,150E-9],
            6:[0.7*150E-9,1.5E-6], 
            }
    @Instrument.addOptionSetter("name")
    def _setName(self,instrumentName):
         self.name = instrumentName

    @Instrument.addOptionGetter("name")
    def _getName(self):
        return self.name
    
    @Instrument.addOptionSetter("frequency")
    def _setFrequency(self,frequency):
        self.dev.write("FREQ  "+str(frequency))

    @Instrument.addOptionGetter("frequency")
    def _getFrequency(self):
        return float(self.dev.query("FREQ?"))
    
    @Instrument.addOptionSetter("amplitude")
    def _setAmplitude(self,amplitude):
        self.dev.write("SLVL  "+str(amplitude))

    @Instrument.addOptionGetter("amplitude")
    def _getAmplitude(self):
        return float(self.dev.query("SLVL?"))

    @Instrument.addOptionGetter("senseLevel")
    def readXY(self): # This function is a bit more ellaborate since snap return a string comprised of both X and Y values. The function then separates this string, i.e. looks for the separation coma and both exponents... 
        XY = self.dev.query("SNAP?1,2") # ONE could also use OUTP? i (i=1,2,3,4 X,Y,R theta)
        divideIndex = XY.find(",")
        X = XY[0:divideIndex]
        #print(X)
        Y = XY[divideIndex+1:-1]
        #print(Y)
        #Voltage measurements:
        if self.input == 'A' or self.input =='A-B': #
            XexpIndex = X.find("e-")
            YexpIndex = Y.find("e-")
            if (XexpIndex == -1 or YexpIndex == -1):
                return [float(X)*(1/self.scaleFactor),float(Y)*(1/self.scaleFactor)]
            else:
                XList =list(X)
                if XList[XexpIndex+2] =="0":
                    XList[XexpIndex+2] =""
                Xfinal = float("".join(XList))
                YList =list(Y)
                if YList[YexpIndex+2] =="0":
                    YList[YexpIndex+2] =""
                Yfinal = float("".join(YList))
                return [(1/self.scaleFactor)*Xfinal,(1/self.scaleFactor)*Yfinal]
        #Current measurements          
        XexpIndex = X.find("e-")
        if XexpIndex != -1:
            # print("Xexp index is "+str(XexpIndex))
           XList =list(X)
           if XList[XexpIndex+2] =="0":
              XList[XexpIndex+2] =""
           Xfinal = float("".join(XList))
        else:
            Xfinal = 0 # we need to do something like htis because if the result is already zero or some odd/weird number, the exponent finding process above breaks down        
        YexpIndex = Y.find("e-")    
        if YexpIndex != -1:
            #  print("Yexp index is "+str(YexpIndex))
           YList =list(Y)
           if YList[YexpIndex+2] =="0":
              YList[YexpIndex+2] =""
           Yfinal = float("".join(YList))
        else:
           Yfinal = 0
           
        if self.autoSensitivityEnable:
            self._autoSensitivity([Xfinal,Yfinal])
        return [(1/self.scaleFactor)*Xfinal,(1/self.scaleFactor)*Yfinal]
    
    def _autoSensitivity(self,givenValue):
            R = math.sqrt(givenValue[0]**2+givenValue[1]**2)
#            print('#############\n')
#            print('current value is'+str(R)+'\n')
#            print('current range index is: '+str(self.rangeIndex)+'\n')
#            print('the boundaries here are: '+str(self.rangeDic[self.rangeIndex][0]) +'and' + str(self.rangeDic[self.rangeIndex][1])+'\n')
#            print('#############\n')
            if (self.rangeDic[self.rangeIndex][0] >= R): #and not math.isnan(R)
                a = self.rangeIndex -1
                if a in range(7):
                    self.rangeIndex = a
                   # print(self.rangeIndex)
                    self.dev.write("SENS "+str(self.possibleCurrRanges[self.rangeIndex]))
                    time.sleep(2)
            elif (R > self.rangeDic[self.rangeIndex][1]):
                a = self.rangeIndex +1
                if a in range(7):
                    self.rangeIndex = a
                    #print(self.rangeIndex)
                    self.dev.write("SENS "+str(self.possibleCurrRanges[self.rangeIndex]))
                    time.sleep(2)
            else:
                pass

    @Instrument.addOptionSetter("sourceLevel")
    def _setSourceLevel(self,sourceLevel):
        self.dev.write(("SLVL " if self.outputMode == "amplitude" else "FREQ ") +str(sourceLevel))
        time.sleep(self.sweepDelay) 
    @Instrument.addOptionGetter("sourceLevel")
    def _getSourceLevel(self):
         return float(self.dev.query(("SLVL?" if self.outputMode == "amplitude" else "FREQ?")))

    @Instrument.addOptionSetter("timeConst")    
    def _setTimeConst(self,timeConst): #Index can be between 0 (10 microsec to 19 30ksec)
        possibleConstants = [10E-6,30E-6,100E-6,300E-6,1E-3,3E-3,10E-3,30E-3,100E-3,300E-3,1,3,10,30,100,300]
        if float(timeConst) in possibleConstants: #Not including the highest kilosecond integration times since not never used.
            self.dev.write("OFLT "+str(possibleConstants.index(timeConst)))
        else:
            raise ValueError(
                            "\"{}\" is not a valid time Constant for the SRS830.".format(timeConst) +
                            " Valid time constants are: (10,30,100,300)X 1E-6, (1,3,10,30,100,300)X 1E-3 and (1,3,10,30,100,300)X 1E-0 seconds."
                            )
    
    @Instrument.addOptionSetter("senseRange")        
    def _setSenseRange(self,senseRange):
        possibleSenseRanges = [1E-9,2E-9,5E-9,10E-9,20E-9,50E-9,100E-9,200E-9,500E-9,1E-6,2E-6,5E-6,10E-6,20E-6,50E-6,100E-6,200E-6,500E-6,1E-3,2E-3,5E-3,10E-3,20E-3,50E-3,100E-3,200E-3,500E-3,1] #For voltages !!
        if senseRange in possibleSenseRanges:
            sensIndex = possibleSenseRanges.index(senseRange)-1
            if self.rangeIndex != sensIndex: #Only change rhe range if it is different than before. This will be helpfull with the auoRange function True
                self.dev.write("SENS "+str(sensIndex))
                time.sleep(0.4)
                #self.rangeIndex = sensIndex
            else:
                pass
        else:
            raise ValueError(
                            "\"{}\" is not a valid senseRange for the SRS830.".format(senseRange) +
                            " Valid sensitivities are:\"{}\"  Volts or microAmps respectively.".format(possibleSenseRanges)
                            )

    @Instrument.addOptionGetter("senseRange")
    def _getSenseRange(self):
        possibleSenseRanges = [1E-9,2E-9,5E-9,10E-9,20E-9,50E-9,100E-9,200E-9,500E-9,1E-6,2E-6,5E-6,10E-6,20E-6,50E-6,100E-6,200E-6,500E-6,1E-3,2E-3,5E-3,10E-3,20E-3,50E-3,100E-3,200E-3,500E-3,1] #For voltages !!
        tempRes = int(self.dev.query('SENS?'))
        return(possibleSenseRanges[tempRes])
     
    @Instrument.addOptionSetter("input")
    def _setInput(self,inputSetting):  #I1 = I(1E6) and I2 = I(1E8)
        possibleSettings = ["A","A-B","I1","I2"]
        if str(inputSetting) in possibleSettings:
            self.dev.write("ISRC "+str(possibleSettings.index(inputSetting)))
            self.input = str(inputSetting)
    
    @Instrument.addOptionGetter("input")
    def _getInput(self):
        possibleSettings = ["A","A-B","I1","I2"]
        modeIndex = int(self.dev.query("ISRC?"))
        return possibleSettings[modeIndex]
    
    @Instrument.addOptionGetter("scaleFactor")
    def _getScaleFactor(self):
        return self.scaleFactor
    
    @Instrument.addOptionSetter("scaleFactor")
    def _setScaleFactor(self,scaleFactor):
        self.scaleFactor = scaleFactor
    
    @Instrument.addOptionSetter("sweepParameter")
    def _setSweepParameter(self,sweepParameter):
        if sweepParameter in ("frequency","amplitude"): 
            self.outputMode = str(sweepParameter)
        else:
            raise ValueError(
                            "\"{}\" is not a valid sweepParameter for the SRS830.".format(sweepParameter) +
                            " You can either sweep the reference 'frequency' or the sine output 'amplitude'."
                            )    
    def _getSenseIndex(self):
        return int(self.dev.query("SENS?"))
    
    @Instrument.addOptionGetter("sweepParameter")
    def _getSweepParameter(self):
        return self.outputMode
    
    @Instrument.addOptionSetter('sweepDelay')
    def _setSweepDelay(self,delay):
        self.sweepDelay = delay
        
    @Instrument.addOptionGetter('sweepDelay')
    def _getSweepDelay(self):
        return self.sweepDelay
    
    @Instrument.addOptionSetter("autoSensitivity")
    def _setAutoSensitivity(self,enable):
        self.autoSensitivityEnable = True if enable else False

    @Instrument.addOptionGetter("autoSensitivity")
    def _getAutoSensitivity(self):
        return self.autoSensitivityEnable
    def autoPhase(self):
        self.dev.write("APHS")
        time.sleep(3)
        
    @Instrument.addOptionSetter("phase")
    def _setPhase(self,phase):
        self.dev.write("PHAS "+str(phase))
        
    @Instrument.addOptionGetter("phase")
    def _getPhase(self):
        return float(self.dev.query("PHAS?"))   
    def close(self):
        self.dev.close()    
    def goTo(self,target,stepsize= 0.01,delay=0.2):
        currentOutput = self.get('sourceLevel')
        sign = 1 if (target>currentOutput) else -1
        sweepArray = np.arange(currentOutput,target+sign*stepsize,sign*stepsize)
        for point in sweepArray:
            self.set('sourceLevel',point)
            time.sleep(delay)
        self.set('sourceLevel',target)