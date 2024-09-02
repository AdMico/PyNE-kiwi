"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Adam Micolich

Very basic example for doing an I-V sweep with a single K236 with 6517A on read.
"""

import os
os.chdir('..\\')
from Imports import *

# 1) Initialize Instruments
#---- K236 Vsd --------------
keithley = Keithley2401(24)
keithley.setOptions({
    "beepEnable": False,
    "sourceMode": "voltage",
    "sourceRange":10,
    "senseRange": 1.05e-4,
    "compliance": 1.0e-4,
    "scaleFactor":1
})
#---- K6517A Isd
eMeter = Keithley6517A(20)
eMeter.setOptions({
    "autoRange":True,
    "senseRange":2e-3,
    "senseMode":"current",
})

[basePath,fileName] = fileDialog()

start = -1.0; end = 1.0; step = 0.01
Vsd = np.arange(start,end,step)
inputPoints = product(Vsd)

inputHeaders = ["Vsd"]
inputSetters = [keithley]

outputHeaders = ["Id","Is"]
outputReaders = [eMeter,keithley]
keithley.set('outputEnable',True)

print('Sweep 1 start')

sweepAndSave(
        basePath+fileName,
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders, saveEnable = True,
        plotParams = ["Vsd","Id"]
)

print('Sweep 1 finish')

keithley.goTo(0,delay=0.01)

closeInstruments(inputSetters,outputReaders)