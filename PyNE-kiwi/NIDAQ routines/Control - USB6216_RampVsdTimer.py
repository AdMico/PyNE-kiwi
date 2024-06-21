"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Adam Micolich

Program for using NIDAQ USB-6216 for full control of a transistor characterisation.
DAQ AO0 on source, DAQ AO1 on gate, Drain feeds a Femto, which feeds AI0.
This program runs Vg and Vsd to specified values, then does a time sweep for a given length
of time, then ramps Vg and Vsd back. 
"""

import os
os.chdir('..\\')
from Imports import *

# Setpoints here as some need to be fed to instruments
Vsd = 0.3 #Volts
Vg = 0.0 #Volts
Timestep = 0.1 #Seconds
TimeStop = 180 #Seconds

# 1) Initialize Instruments
#---- NIDAQ Output Port for Source --------------
daqout_S = USB6216Out(0)
daqout_S.setOptions({
    "feedBack":"Int",
    "extPort":6, # Can be any number 0-7 if in 'Int'  
    "scaleFactor":1
})

#---- NIDAQ Output Port for Gate --------------
daqout_G = USB6216Out(1)
daqout_G.setOptions({
    "feedBack":"Int",
    "extPort":7, # Can be any number 0-7 if in 'Int'  
    "scaleFactor":1
})

#---- NIDAQ Input Port for Drain --------------
daqin_D = USB6216In(0)
daqin_D.setOptions({
#    "inputRange":10,
    "scaleFactor":1
})

#---- Time Step Instrument --------------
time1 = TimeMeas(0.1) #Note! GPIB number serves instead as wait time interval for TimeMeas.py. Do not make this huge or you will wait forever.
time1.setOptions({
    "timeInterval":0
})

[basePath,fileName] = fileDialog()

print('Ensure Outputs Zero') #Optional, but use unless you trust to be zero.

daqout_G.goTo(0.0,delay=0.001)
daqout_S.goTo(0.0,delay=0.001)

print('Array definition')

#time array
tset = np.arange(0.0,Timestop,Timestep)
inputPoints = product(tset)

print('Sweep sequence')

print('Set outputs')

daqout_S.goTo(Vsd,delay=0.001)
daqout_G.goTo(Vg,delay=0.001)

#-------------- Sweep Id vs Vsd at single Vg
inputHeaders = ["Time"]
inputSetters = [time1]
outputHeaders = ["Id"]
outputReaders = [daqin_D]
sweepAndSave(
        basePath+fileName,
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders,saveEnable = True,
        plotParams = ["Time","Id"]
)
    
print('Return outputs to zero')
    
daqout_G.goTo(0.0,delay=0.001)
daqout_S.goTo(0.0,delay=0.001)

closeInstruments(inputSetters,outputReaders)