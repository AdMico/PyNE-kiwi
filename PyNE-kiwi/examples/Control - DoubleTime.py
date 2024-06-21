"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Adam Micolich

Sweeps time vs time as a route to running the software without any real instruments.
"""

import os
os.chdir('..\\')
from Imports import *

# 1) Initialize Instruments
#---- Time 1 --------------
time1 = TimeMeas(0.1) #Note! GPIB number serves instead as wait time interval for TimeMeas.py. Do not make this huge or you will wait forever.
time1.setOptions({
    "timeInterval":0
})

# 1) Initialize Instruments
#---- Time 2 --------------
time2 = TimeMeas(0) #Note! GPIB number is wait time, but serves no function on read, so the value used here has no effect.

[basePath,fileName] = fileDialog()

start = 0.0; end = 100.0; step = 1.0 #Length of sweep is 100 times wait time. Program runs for a few seconds if wait time is zero.
Vsd = np.arange(start,end,step)
inputPoints = product(Vsd)

inputHeaders = ["time1"]
inputSetters = [time1]

outputHeaders = ["time2"]
outputReaders = [time2]

print('sweep1')

sweepAndSave(
        basePath+fileName,
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders, saveEnable = True,
        plotParams = ['time1','time2']
)

start = 0.0; end = 100.0; step = 1.0 #Length of sweep is 100 times wait time. Program runs for a few seconds if wait time is zero.
Vsd = np.arange(start,end,step)
inputPoints = product(Vsd)

inputHeaders = ["time1"]
inputSetters = [time1]

outputHeaders = ["time2"]
outputReaders = [time2]

print('sweep2')

sweepAndSave(
        basePath+fileName,
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders, saveEnable = True,
        plotParams = ['time1','time2']
)

start = 0.0; end = 100.0; step = 1.0 #Length of sweep is 100 times wait time. Program runs for a few seconds if wait time is zero.
Vsd = np.arange(start,end,step)
inputPoints = product(Vsd)

inputHeaders = ["time1"]
inputSetters = [time1]

outputHeaders = ["time2"]
outputReaders = [time2]

print('sweep3')

sweepAndSave(
        basePath+fileName,
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders, saveEnable = True,
        plotParams = ['time1','time2']
)

closeInstruments(inputSetters,outputReaders)