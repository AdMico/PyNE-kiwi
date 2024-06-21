"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Adam Micolich

Very simple test for NIDAQ USB-6216. Connect AO0 to AI0 with a BNC cable. 
Program sweeps AO0 from -1 to +1V and plots corresponding output (should be line).
It then sweeps +1 to -1V and then returns to 0V without saving data.
"""

import os
os.chdir('..\\')
from Imports import *

# 1) Initialize Instruments
#---- NIDAQ Output Port --------------
daqout1 = USB6216Out(0)
daqout1.setOptions({
    "feedBack":"Int",
    "extPort":7,   
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

inputHeaders = ["Vout"]
inputSetters = [daqout1]

outputHeaders = ["Vin"]
outputReaders = [daqin1]

print('sweep1')

sweepAndSave(
        basePath+fileName,
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders, saveEnable = True, 
        plotParams = ["Vout","Vin"]
)

start = 1.0; end = -1.0; step = -0.01 #Important note, if you are sweeping backwards, this must be a negative number or the sweep will fail.
V2 = np.arange(start,end,step)
inputPoints = product(V2)

inputHeaders = ["Vout"]
inputSetters = [daqout1]

outputHeaders = ["Vin"]
outputReaders = [daqin1]

print('sweep2')

sweepAndSave(
        basePath+fileName,
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders, saveEnable = True, 
        plotParams = ["Vout","Vin"]
)

daqout1.goTo(0,delay=0.01)

closeInstruments(inputSetters,outputReaders)