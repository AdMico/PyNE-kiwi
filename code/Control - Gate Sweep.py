"""
Brought to PyNE-kiwi v1.0.0 on Tue Sep 3 2024 by APM

@developers: Adam Micolich

@author: Jakob Seidl

Control program for basic gate voltage sweep on VUW setup
"""

from Imports import *

# 1) Initialize Instruments
#---- Keithley 1 --------------
keithley = Keithley2401(24)
keithley.setOptions({
    "beepEnable": False,
    "sourceMode": "voltage",
    "sourceRange":10,
    "senseRange": 1.05e-6,
    "compliance": 1.0E-8,
    "scaleFactor":1
})

[basePath,fileName] = fileDialog()

start = 0.0; end = 1.5; step = 0.001
Vsd = np.arange(start,end,step)
inputPoints = product(Vsd)

inputHeaders = ["Vsd"]
inputSetters = [keithley]

outputHeaders = ["Isd"]
outputReaders = [keithley]
keithley.set('outputEnable',True)

sweepAndSave(
        basePath+fileName,
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders, saveEnable = True,
        plotParams = ['Vsd','Isd']
)

closeInstruments(inputSetters,outputReaders)