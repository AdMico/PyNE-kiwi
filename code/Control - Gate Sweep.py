"""
Brought to PyNE-kiwi v1.0.0 on Tue Sep 3 2024 by APM

@developers: Adam Micolich

@author: Jakob Seidl

Control program for basic gate voltage sweep on VUW setup
"""

from Imports import *

## Initialise B1500 -- Semiconductor Parameter Analyser
B1500_init()

## Initialise B2201
B2201_init()

## Initialise K2401
K2401 = Keithley2401(24)
K2401.setOptions({"beepEnable": False,"sourceMode": "voltage","sourceRange":K2401sourceRange,"senseRange": K2401senseRange,"compliance": K2401compl,"scaleFactor":1})

## Initialise Datafile
measurementName = str(ID.readCurrentSetup()) + str(ID.readCurrentID())
today = date.today()
t=today.strftime("%y%m%d")
dataPath = basePath + "/"+t+"_"+measurementName

## Set gate voltage dataset
start = 0.0; end = 0.5; step = 0.001
Vg = np.arange(start,end,step)
inputPoints = product(Vg)

## Set up inputs and outputs
inputHeaders = ["Vg"]
inputSetters = [K2401]
outputHeaders = ["Is_SMU1","Is_SMU2","Is_SMU3","Is_SMU4"]
outputReaders = [B1500_SMU1,B1500_SMU2,B1500_SMU3,B1500_SMU4]
K2401.set("outputEnable",True)

## Run sweep
sweepAndSave(
        basePath+fileName,
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders, saveEnable = True,
        plotParams = ["Vg","Is_SMU1","Is_SMU2","Is_SMU3","Is_SMU4"]
)

## Finalise
closeInstruments(inputSetters,outputReaders)