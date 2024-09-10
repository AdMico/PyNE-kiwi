"""
Brought to PyNE-kiwi v1.0.0 on Tue Sep 3 2024 by APM

@developers: Adam Micolich

@author: Jakob Seidl

Control program for basic gate voltage sweep on VUW setup
"""

from Imports import *

## Initialise Pi Connection
CtrlPi = PiMUX()

## Initialise B1500 -- Semiconductor Parameter Analyser
B1500_init()

## Initialise B2201
B2201 = B2201()
B2201.B2201_init()

## Initialise K2401
K2401 = K2401(24)
K2401.setOptions({"beepEnable": False,"sourceMode": "voltage","sourceRange":K2401sourceRange,"senseRange": K2401senseRange,"compliance": K2401compl,"scaleFactor":1})

## Initialise Datafile
measurementName = str(ID.readCurrentSetup()) + str(ID.readCurrentID())
today = date.today()
t=today.strftime("%y%m%d")
dataPath = basePath + "/"+t+"_"+measurementName

## Set gate voltage dataset
start = 0.0; end = 0.5; step = 0.01
Vg = np.arange(start,end,step)
inputPoints = product(Vg)

print("Do the first odd gate sweep")
B2201.B2201_odd()
CtrlPi.DP_odd()

## Set up inputs and outputs
inputHeaders = ["Vg"]
inputSetters = [K2401]
outputHeaders = ["Is_SMU1","Is_SMU3","Is_SMU5","Is_SMU7"]
outputReaders = [B1500_SMU1,B1500_SMU2,B1500_SMU3,B1500_SMU4]
K2401.set("outputEnable",True)

#Set odd fileName
fileName = t+"_"+measurementName+"_odd"

## Run sweep
sweepAndSave(
        dataPath+fileName,
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders, saveEnable = True,
        plotParams = ["Vg","Is_SMU1"]
)

print("Do the second even gate sweep")
B2201.B2201_even()
CtrlPi.DP_even()

## Set up inputs and outputs
inputHeaders = ["Vg"]
inputSetters = [K2401]
outputHeaders = ["Is_SMU2","Is_SMU4","Is_SMU6","Is_SMU8"]
outputReaders = [B1500_SMU1,B1500_SMU2,B1500_SMU3,B1500_SMU4]
K2401.set("outputEnable",True)

#Set even fileName
fileName = t+"_"+measurementName+"_even"

## Run sweep
sweepAndSave(
        dataPath+fileName,
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders, saveEnable = True,
        plotParams = ["Vg","Is_SMU2","Is_SMU4","Is_SMU6","Is_SMU8"]
)

## Finalise software
B2201.B2201_clear()
closeInstruments(inputSetters,outputReaders)