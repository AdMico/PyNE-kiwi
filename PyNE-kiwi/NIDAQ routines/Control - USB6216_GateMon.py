"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Adam Micolich

Program designed to run an electrode voltage with ground return via DLPCA for quasi-SMU operation
"""

import os
os.chdir('..\\')
from Imports import *
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import threading as th
import time
import GlobalMeasID as ID

# Setpoints here as some need to be fed to instruments
DLPCA_Gain = 1e4
SleepTime = 1 #Seconds -- nominal pause between time points in monitor mode

basePath = r'\\Output\\'
fileName = '\pHtest_'
#[basePath,fileName] = fileDialog() #Use lines above to autodump output to folder (and avoid endless GUI folder calls)

#Definitions up-front

#Key-press escape thread module
keep_going = True
def key_capture_thread():
    global keep_going
    input()
    keep_going = False

#current monitoring loop module
def cur_mon_loop():
    th.Thread(target=key_capture_thread, args=(), name='key_capture_thread', daemon=True).start()
    counter = 0
    fig,ax1 = plt.subplots()
    ax1.set_xlabel('time (s)')
    ax1.set_ylabel('current (A)', color = 'tab:red')
    ax1.tick_params(axis='y', labelcolor = 'tab:red')
    ax1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2e'))        
#   Code snippet below enables a second axis to go on the graph, just in case there's another thing you want to monitor during the gate hold -- e.g., a voltage via one of the ai channels.
#    ax2=ax1.twinx()
#    ax2.set_ylabel('other (units)', color = 'tab:blue')
#    ax2.tick_params(axis='y', labelcolor = 'tab:blue')
#    ax2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2e'))
    while keep_going:
        Current = daqin_D._getInputLevel()    
        MonTime = time.time() - MonStartTime
        CurrentList.append(Current)
#        OutputList.append(other) Off for now, but just in case there's a second variable to monitor
        TimeList.append(MonTime)
        tsv.write(str(MonTime) + "\t" + str(Current) + "\n")
        if counter%10 == 0:
            tsv.flush()
            os.fsync(tsv.fileno())
        plt.ion()
        ax1.plot(TimeList, CurrentList, color = 'tab:red')
#        ax2.plot(TimeList, OutputList, color = 'tab:blue') #For plotting other variable       
        fig.tight_layout()
        plt.ioff()
        plt.show()
        plt.pause(0.01)
        counter +=1
        time.sleep(SleepTime)
        
# Main Code Body Follows

# 1) Initialize Instruments

#---- NIDAQ Output Port for Gate --------------
daqout_G = USB6216Out(0)
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
    
while 1:
    print("Holding point: Press 0 to adjust gate voltage, Press 1 for another run, 2 to run gate down and finish, 3 to hold gate voltage and finish.")
    HoldPoint = input()
    if HoldPoint == '0':
        print("Enter new gate voltage")
        gateVoltage = float(input())
        daqout_G.goTo(gateVoltage,stepsize=0.01,delay=0.01)
        continue
    if HoldPoint == '1':            
        ID.increaseID()
        LoopFileName = fileName + "_" + str(ID.readCurrentSetup()) + str(ID.readCurrentID())
        tsv = open(basePath + LoopFileName + ".tsv","w")
        tsv.write("\n=====================\n")
        tsv.write("time" + "\t" + "pH by Vg (V)" + "\n")
        CurrentList = []
#        OutputList = []
        TimeList = []
        print('Start PID routine -- this is an infinite loop, press Enter twice in iPython console to exit')
        MonStartTime = time.time()
        cur_mon_loop()
        keep_going = True
        tsv.flush()
        os.fsync(tsv.fileno())
        tsv.close()
        plt.savefig(basePath + LoopFileName +'.png') #Save Plot as .png as additional feature
        plt.close()
        continue
    if HoldPoint == '2':
        daqout_G.goTo(0.0,stepsize=0.01,delay=0.01)
        break
    if HoldPoint == '3':
        break