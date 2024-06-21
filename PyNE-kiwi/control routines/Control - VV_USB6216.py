"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Jakob Seidl
"""

import os
os.chdir('..\\')
from Imports import *

# 1) Initialize Instruments
#---- NIDAQ Output Port --------------
daqout1 = USB6216Out(0)
daqout1.setOptions({
    "scaleFactor":1
})

#---- NIDAQ Input Port --------------
daqin1 = USB6216In(0)
daqin1.setOptions({
#    "inputRange":10,
    "scaleFactor":1
})

[basePath,fileName] = fileDialog()

start = -1.0; end = 1.0; step = 0.01
V1 = np.arange(start,end,step)
inputPoints = product(V1)

inputHeaders = ["V"]
inputSetters = [daqout1]

outputHeaders = ["V"]
outputReaders = [daqin1]

print('Sweep 1 start')

sweepAndSave(
        basePath+fileName,
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders, saveEnable = True, 
        plotParams = ["V","V"]
)

print('Sweep 1 finish')

start = 1.0; end = -1.0; step = -0.01 #Important note, if you are sweeping backwards, this must be a negative number or the sweep will fail.
V2 = np.arange(start,end,step)
inputPoints = product(V2)

inputHeaders = ["V"]
inputSetters = [daqout1]

outputHeaders = ["V"]
outputReaders = [daqin1]

print('Sweep 2 start')

sweepAndSave(
        basePath+fileName,
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders, saveEnable = True, 
        plotParams = ["V","V"]
)

print('Sweep 2 finish')

daqout1.goTo(0,delay=0.01)

closeInstruments(inputSetters,outputReaders)