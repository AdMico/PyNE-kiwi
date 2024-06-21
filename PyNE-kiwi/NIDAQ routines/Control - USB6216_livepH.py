"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Adam Micolich

Program to do live running of an ISFET pH meter for testing.
Use the pH Monitor control program instead for traditional sweeps with pHmeter.py
"""

import os
os.chdir('..\\')
from Imports import *
import PID
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import threading as th
import time
import GlobalMeasID as ID

# Setpoints here as some need to be fed to instruments
DLPCA_Gain = 1e4
Vsd = 0.3 #Volts on ao0
Vg = 1.60 #Volts on ao1
IdealDrive = 3e-5 #Amps, current on ai0 to aim for -- NB. Ensure gain is correctly set in Line 19
OffsetThres = 1.0e-3*IdealDrive
# PID settings
P = 1.6*DLPCA_Gain
I = 0.1
D = 0.0
SleepTime = 0.1 # seconds

basePath = r'\\Output\\Testzone'
fileName = r'\\pHtest_'
#[basePath,fileName] = fileDialog() #Use lines above to autodump output to folder (and avoid endless GUI folder calls)

#Definitions up-front

#Key-press escape thread module
keep_going = True
def key_capture_thread():
    global keep_going
    input()
    keep_going = False

#pH monitoring loop module
def pH_mon_loop():
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
    counter = 0
    fig,ax1 = plt.subplots()
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('voltage (V)', color = 'tab:red')
    ax1.tick_params(axis='y', labelcolor = 'tab:red')        
    ax2=ax1.twinx()
    ax2.set_ylabel('current (A)', color = 'tab:blue')
    ax2.tick_params(axis='y', labelcolor = 'tab:blue')
    ax2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2e'))
    while keep_going:
        currGateVolt = daqout_G._getOutputLevel()
        currDriveCurr = daqin_D._getInputLevel()    
        pHtime = time.time() - pHStartTime
        pid.update(currDriveCurr)
        output = pid.output
        newGateVolt = currGateVolt + output
        daqout_G.goTo(newGateVolt,stepsize=0.01,delay=0.001)
#        print()    
#        print('Time: ',pHtime,'Current = ',currDriveCurr,'New Vg = ',newGateVolt,'Old Vg = ',currGateVolt,'PID output = ',output)
        OutputList.append(newGateVolt)
        CurrentList.append(currDriveCurr)
        TimeList.append(pHtime)
        tsv.write(str(pHtime) + "\t" + str(newGateVolt) + "\n")
        if counter%10 == 0:
            tsv.flush()
            os.fsync(tsv.fileno())
        plt.ion()
        ax1.plot(TimeList, OutputList, color = 'tab:red')
        ax2.plot(TimeList, CurrentList, color = 'tab:blue')        
        fig.tight_layout()
        plt.ioff()
        plt.show()
        plt.pause(0.01)
        counter +=1
        time.sleep(SleepTime)

# Main Code Body Follows

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
    "scaleFactor":DLPCA_Gain #Set to gain of your DLPCA-200.
})
    
print('Establish initial set-point') #Optional, but use unless you trust to be zero.
print()

daqout_S.goTo(Vsd,stepsize=0.01,delay=0.1)
daqout_G.goTo(Vg,stepsize=0.01,delay=0.1)
Drive = daqin_D._getInputLevel()

print('Starting Drive = ',Drive, 'Target Drive =',IdealDrive)
print('Running a PID loop to get to starting pH')
print()

pid = PID.PID(P, I, D)
pid.setSetPoint(IdealDrive)

Offset = abs(Drive - IdealDrive)

while Offset >= OffsetThres:
    currDriveCurr = daqin_D._getInputLevel()
    Offset = abs(currDriveCurr - IdealDrive)    
    currGateVolt = daqout_G._getOutputLevel()
    pid.update(currDriveCurr)
    output = pid.output
    newGateVolt = currGateVolt + output
    daqout_G.goTo(newGateVolt,stepsize=0.01,delay=0.001)    
    time.sleep(SleepTime)

print('At set-point, ready to start experiment')
currGateVolt = daqout_G._getOutputLevel()
print('At current pH solution, gate voltage is:',currGateVolt)
print("Press Enter to continue")
input()

stopper = 0
while stopper == 0:
#    counter = 0
    ID.increaseID()
    LoopFileName = fileName + "_" + str(ID.readCurrentSetup()) + str(ID.readCurrentID())
    tsv = open(basePath + LoopFileName + ".tsv","w")
    tsv.write("\n=====================\n")
    tsv.write("time" + "\t" + "pH by Vg (V)" + "\n")
    OutputList = []
    CurrentList = []
    TimeList = []
    print('Start PID routine -- this is an infinite loop, press Enter twice in iPython console to exit')
    pHStartTime = time.time()
    pH_mon_loop()
    keep_going = True
    tsv.flush()
    os.fsync(tsv.fileno())
    tsv.close()
    plt.savefig(basePath + LoopFileName +'.png') #Save Plot as .png as additional feature
    plt.close()
    print("Holding point: Press 1 for another run, 0 to run sensor down and finish, 2 to finish with sensor up.")
    HoldPoint = input()
    if HoldPoint == '0':
        stopper = 1
        SoftStop = 1
        break
    if HoldPoint == '2':
        stopper = 1
        SoftStop = 0
        break
    if HoldPoint == '1':
        stopper = 0
        continue
        
if SoftStop == 1:
    print('Return outputs to zero')
    daqout_G.goTo(0.0,stepsize=0.01,delay=0.1)
    daqout_S.goTo(0.0,stepsize=0.01,delay=0.1)