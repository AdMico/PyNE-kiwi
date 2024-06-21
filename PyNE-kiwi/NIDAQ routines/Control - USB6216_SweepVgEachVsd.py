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
    "scaleFactor":1
})

[basePath,fileName] = fileDialog()

print('Ensure Outputs Zero') #Optional, but use unless you trust to be zero.

daqout_G.goTo(0.0,delay=0.001)
daqout_S.goTo(0.0,delay=0.001)

print('Array definition')

#Vg array
start_g = 0.0; end_g = 2.0; step_g = 0.01 #Create a up and downsweep array
VgUp = np.arange(start_g, end_g, step_g) #Only the upsweep
VgDown = np.arange(end_g, start_g-step_g, -step_g)
VgUpDown = np.concatenate((VgUp, VgDown)) #np.concatenate() fuses two arrays to one

#Vsd array
start_sd = 2.0; end_sd = 3.0; step_sd = 0.2 #Create a up and downsweep array
count_sd = int((end_sd-start_sd)/step_sd) + 1 
Vsd = np.linspace(start_sd, end_sd, count_sd, endpoint=True) #I like linspace a bit more than arange

print('Sweep sequence')

#-------------- Sweep Id vs Vg at various Vsd
inputHeaders = ["Vg"]
inputSetters = [daqout_G]
outputHeaders = ["Vsd","Id"]
outputReaders = [daqout_S,daqin_D]
for i in range(count_sd):
    print("sweep",i,"of",count_sd,"with source-drain voltage",Vsd[i])
    daqout_S.goTo(Vsd[i],delay=0.001)
    inputPoints = product(VgUpDown)
    sweepAndSave(
            basePath+fileName,
            inputHeaders, inputPoints, inputSetters,
            outputHeaders, outputReaders,saveEnable = True,
            plotParams = ['Vg','Id']
    )
    
print('Return outputs to zero')
    
daqout_G.goTo(0.0,delay=0.001)
daqout_S.goTo(0.0,delay=0.001)

closeInstruments(inputSetters,outputReaders)