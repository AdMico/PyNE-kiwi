"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Adam Micolich

Example program for using NIDAQ USB-6216 for full control of a transistor characterisation 2SK940 with 10kohm in series with channel.
DAQ AO0 on the source, DAQ AO1 on the gate, Drain feeds a Femto at 10^4 gain, which feeds AI0. Program should give classic MOSFET saturation curve 
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
start = 0.0; end = 2.0; step = 0.01 #Create a up and downsweep array
VsdUp = np.arange(start, end, step) #Only the upsweep
VsdDown = np.arange(end, start-step, -step)
VsdUpDown = np.concatenate((VsdUp, VsdDown)) #np.concatenate() fuses two arrays to one
#print(VsdUpDown) -- debug

#Vg array
start = 2.0; end = 3.0; step = 0.2 #Create a up and downsweep array
count = int((end-start)/step) + 1 
Vg = np.linspace(start, end, count, endpoint=True) #I like linspace a bit more than arange
#print(Vg) -- debug

print('Sweep sequence')

#-------------- Sweep Id vs Vsd at various Vg
inputHeaders = ["Vsd"]
inputSetters = [daqout_S]
outputHeaders = ["Vg","Id"]
outputReaders = [daqout_G,daqin_D]
for i in range(count):
    print("sweep",i,"of",count,"with gate voltage",Vg[i])
    daqout_G.goTo(Vg[i],delay=0.001)
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