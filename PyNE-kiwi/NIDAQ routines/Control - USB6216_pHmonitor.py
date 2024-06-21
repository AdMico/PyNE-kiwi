"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Adam Micolich

Program for doing sweeps of the pH meter vs time -- could be extended to testing pH vs other instrument variables
"""

import os
os.chdir('..\\')
from Imports import *

#Key parameter needed before instrument definition
TimeInterval = 5.0#Seconds
DLPCA_Gain = 1e4
driveCurrentAim = 3e-5

# 1) Initialize Instruments
#---- pH Meter Virtual Instrument --------------
pHMeter1 = pHMeter()
pHMeter1.setOptions({
    "sourceVoltage":0.3,#Volts
    "gateVoltage":1.60,#Volts -- kickoff value only, the pHMeter routine will reset this to avoid unnecessary ramps.
    "driveCurrentAim":driveCurrentAim,#Amps -- Ensure gain is set correctly in scalefactor
    "scaleFactor":DLPCA_Gain,
    "sleepTime":0.1,#seconds
    "P":1.6*DLPCA_Gain,
    "I":0.1,
    "D":0.0,
    "offsetThreshold":1.0e-3*driveCurrentAim
})

#---- Time Instrument --------------
time1 = TimeMeas(TimeInterval) #Note! GPIB number serves instead as wait time interval for TimeMeas.py. Do not make this huge or you will wait forever.
time1.setOptions({
    "timeInterval":TimeInterval #Set at top
})

basePath = r'\\Output\\Testzone'
fileName = r'\\pHtest_'
#[basePath,fileName] = fileDialog() #Use lines above to autodump output to folder (and avoid endless GUI folder calls)

startTime = 0.0; endTime = 10.0; stepTime = 1.0 
timeArray = np.arange(startTime,endTime,stepTime)
inputPoints = product(timeArray)

inputHeaders = ["TimeSet"]
inputSetters = [time1]

outputHeaders = ["Time","pH"]
outputReaders = [time1, pHMeter1]

print('Sweep 1')

time1._setTimeReset() #Sets time back to zero for trace
sweepAndSave(
        basePath+fileName,
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders, saveEnable = True,
        plotParams = ['Time','pH']
)

closeInstruments(inputSetters,outputReaders)