"""
Brought to v4.0.0 on Tue May 09 2023 by APM

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
    "scaleFactor":1e4 #Set to gain of your DLPCA-200.
})

basePath = '\\Output\\Testzone\\_'
fileName = 'pHtest_'
#[basePath,fileName] = fileDialog()

print('Ensure Outputs Zero') #Optional, but use unless you trust to be zero.

daqout_G.goTo(0.0,stepsize=0.01,delay=0.1)
daqout_S.goTo(0.0,stepsize=0.01,delay=0.1)

print('Array definition')

#Vg array
start_g = 0.0; end_g = 2.0; step_g = 0.01 #Create a up and downsweep array
VgUp = np.arange(start_g, end_g, step_g) #Only the upsweep
VgDown = np.arange(end_g, start_g-step_g, -step_g)
VgUpDown = np.concatenate((VgUp, VgDown)) #np.concatenate() fuses two arrays to one

#Vsd chosen
Vsd = 0.3

print('Sweep sequence')

#-------------- Sweep Id vs Vg at single Vsd
inputHeaders = ["Vg"]
inputSetters = [daqout_G]
outputHeaders = ["Vsd","Id"]
outputReaders = [daqout_S,daqin_D]
daqout_S.goTo(Vsd,stepsize=0.01,delay=0.1)
inputPoints = product(VgUpDown)
sweepAndSave(
        basePath+fileName,
        inputHeaders, inputPoints, inputSetters,
        outputHeaders, outputReaders,saveEnable = True,
        plotParams = ['Vg','Id']
)
    
print('Return outputs to zero')
    
daqout_G.goTo(0.0,stepsize=0.01,delay=0.1)
daqout_S.goTo(0.0,stepsize=0.01,delay=0.1)

closeInstruments(inputSetters,outputReaders)