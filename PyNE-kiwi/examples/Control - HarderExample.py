"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Jakob Seidl

More complex example for doing a multi-instrument sweep with two K2401s and a K6517A; corresponds to second example in documentation.
"""

import os
os.chdir('..\\')
from Imports import *

#----Keithley Vsd --------------
Ksd = Keithley2401(24)
Ksd.setOptions({
    "beepEnable": False,
    "sourceMode": "voltage",
    "sourceRange":1,
    "senseRange": 1.05e-5,
    "compliance": 1.0E-5,
    "scaleFactor":1
})

#---Keithley Vg -----------
KVg = Keithley2401(25)
KVg.setOptions({
    "beepEnable": False,
    "sourceMode": "voltage",
    "sourceRange":1,
    "senseRange": 1.05e-6,
    "compliance": 1.0E-7,
    "scaleFactor":1
})

#Electrometer
eMeter = Keithley6517A(20)
eMeter.setOptions({
    "autoRange":True,
    "senseRange":2E-6,
    "senseMode":"current",
})

[basePath,fileName] = fileDialog()

#Vsd array
start = -0.05; end = 0.05; step = 0.001 #Create a up and downsweep array
VsdUp = np.arange(start, end, step) #Only the upsweep
VsdDown = np.arange(end, start-step, -step)
VsdUpDown = np.concatenate((VsdUp, VsdDown)) #np.concatenate() fuses two arrays to one

#Gatesweep array, Vg
start = 0.0; end = 1.4; step = 0.010 #Create a up and downsweep array
Vg = np.concatenate(( #np.concatenate() fuses two arrays to one
        np.arange(start, end, step),
        np.arange(end, start-step, -step)
))

#--------------Headers and setters for IV curves
inputHeaders = ["Vsd"]
inputSetters = [Ksd]
outputHeaders = ["Id","Idrough"]
outputReaders = [eMeter,Ksd]
Ksd.set('outputEnable',True)
for i in range(3): # 3 Vsd sweeps from -0.05 -> 0.05 V
    inputPoints = product(VsdUpDown)
    sweepAndSave(
            basePath+fileName,
            inputHeaders, inputPoints, inputSetters,
            outputHeaders, outputReaders,saveEnable = True,
            plotParams = ['Vsd','Id']
    )
Ksd.goTo(0.05,delay=0.001) # since we stop the sweep at -0.05 V we go to 0.05 V manually

#--------------Headers and setters for Vg curves
inputHeaders = ["Vg"]
inputSetters = [KVg]
outputHeaders = ["Id","Ileak","Idrough"]
outputReaders = [eMeter,KVg,Ksd]
for i in range(5): # do 5 full gatesweeps from 0 to 1.4 V
    inputPoints = product(Vg)
    sweepAndSave(
            basePath+fileName,
            inputHeaders, inputPoints, inputSetters,
            outputHeaders, outputReaders,saveEnable = True,
            plotParams = ['Vg','Id','Vg','Ileak']
    )

Ksd.goTo(0.00,delay=0.001)

closeInstruments(inputSetters,outputReaders)