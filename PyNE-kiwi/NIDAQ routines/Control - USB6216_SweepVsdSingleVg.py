"""
Brought to v4.0.0 on Tue May 23 2023 by APM

@author: Adam Micolich

Example program for using NIDAQ USB-6216 for full control of a transistor characterisation.
DAQ AO0 on source, DAQ AO1 on gate, Drain feeds a Femto, which feeds AI0. 
"""

import os
os.chdir('..\\')
from Imports import *

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

[basePath,fileName] = fileDialog()

print('Ensure Outputs Zero') #Optional, but use unless you trust to be zero.

daqout_G.goTo(0.0,delay=0.001)
daqout_S.goTo(0.0,delay=0.001)

print('Array definition')

#Vsd array
start_sd = 0.0; end_sd = 2.0; step_sd = 0.01 #Create a up and downsweep array
VsdUp = np.arange(start_sd, end_sd, step_sd) #Only the upsweep
VsdDown = np.arange(end_sd, start_sd-step_sd, -step_sd)
VsdUpDown = np.concatenate((VsdUp, VsdDown)) #np.concatenate() fuses two arrays to one

#Vg chosen
Vg = 1.0

print('Sweep sequence')

#-------------- Sweep Id vs Vsd at single Vg
inputHeaders = ["Vsd"]
inputSetters = [daqout_S]
outputHeaders = ["Vg","Id"]
outputReaders = [daqout_G,daqin_D]
daqout_G.goTo(Vg,delay=0.001)
inputPoints = product(VsdUpDown)
sweepAndSave(
        basePath+fileName,
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders,saveEnable = True,
        plotParams = ['Vsd','Id']
)
    
print('Return outputs to zero')
    
daqout_G.goTo(0.0,delay=0.001)
daqout_S.goTo(0.0,delay=0.001)

closeInstruments(inputSetters,outputReaders)