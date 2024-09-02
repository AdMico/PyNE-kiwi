"""
Brought to PyNE-kiwi v1.0.0 on Mon Sep 2 2024 by APM

@developers: Adam Micolich

@author: Jakob Seidl

Development code for running a gate sweep in the VUW set-up
"""

from Imports import *
from Init_B1500 import B1500_init

# Instrument Initialisation Process

#B1500 Initialisation -- Ends with four SMUs at 0.0V
B1500_init()

#B2201 Initialisation -- Ends with Even Configuration Hooked up

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