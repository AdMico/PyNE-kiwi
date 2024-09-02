"""
Brought to PyNE-kiwi v1.0.0 on Mon Sep 2 2024 by APM

@developers: Adam Micolich

@author: Adam Micolich


Time-sweep program from PyNE. If unused here move to purgatory and deprecate in a future version
"""

import time
import Instrument 

@Instrument.enableOptions        
class TimeMeas(Instrument.Instrument):
    defaultOutput = "timeInterval"
    defaultInput = "timeStamp"
    def __init__(self,timeInterval): #Note! the 'GPIB number' is used to set the timeInterval for waiting here
        super(TimeMeas,self).__init__()
        self.timeInterval = timeInterval
        self.initTime = time.time()
        self.type = 'TimeMeas'
        self.name = 'myTimeMeas'
 
    @Instrument.addOptionSetter("timeInterval")
    def _setTime(self,timeInterval):
        time.sleep(self.timeInterval)
        
    @Instrument.addOptionGetter("timeStamp")
    def _getTime(self):
        return time.time()-self.initTime
    
    @Instrument.addOptionSetter("timeStampReset")
    def _setTimeReset(self):
        self.initTime = time.time()
    
    @Instrument.addOptionSetter("name")
    def _setName(self,instrumentName):
         self.name = instrumentName
         
    @Instrument.addOptionGetter("name")
    def _getName(self):
        return self.name

    def goTo(target = 0,delay = 0,stepsize = 0): #Line for error handling, serves no practical function
        return