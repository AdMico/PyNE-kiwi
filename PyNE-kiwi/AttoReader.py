"""
Brought to v4.0.0 on Tue May 09 2023 by APM

Rarely used, may be retired in a future version.

@author: Jan Gluschke
"""

import Instrument

@Instrument.enableOptions        
class AttoReader(Instrument.Instrument):
    defaultOutput = "sourceLevel"
    defaultInput = "temperature"
    
    def __init__(self,logFilePath):
        super(AttoReader,self).__init__()
        self.logFilePath = logFilePath
        self.type = 'AttoReader'
        self.name = 'myAttoReader'
    
    @Instrument.addOptionSetter("sourceLevel")
    def _dummySourceFunction(self,dummyVariable):
        return
    
    @Instrument.addOptionSetter("name")
    def _setName(self,instrumentName):
         self.name = instrumentName
    @Instrument.addOptionGetter("name")
    def _getName(self):
        return self.name
    
    @Instrument.addOptionGetter("temperature")
    def _getTemp(self):
        with open('..\\..\\Desktop\\'+self.logFilePath, 'r') as f:
            lines = f.read().splitlines()
            last_line = lines[-1]
            listNumbs = last_line.split()
            print(float(listNumbs[10]))
        return float(listNumbs[10])
    
    def goTo(target = 0.1,delay = 0.2,stepsize = 0.2):
        return