"""
Brought to PyNE-wells v1.1.0 on Wed Apr 17 2024 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

Main software for running assays.
"""

from Imports import *
from Pi_control_Gen4 import PiMUX
import GlobalMeasID as ID
from Config import P1Gain, P2Gain, VSource, ItersAR, WaitAR, zeroThres, basePath, SR, SpC
import pandas as pd
import time
from datetime import datetime,date
from tkinter import *
import tkinter as tk
from pandastable import Table, TableModel
import pandastable as pdtb
import threading
import os
import csv

#---- Initialization of data structures
nRows = 26
nDev = 2*nRows
devices = np.zeros(nDev)
DL = pd.DataFrame(np.zeros((nDev,ItersAR),dtype='float'))
DLerr = pd.DataFrame(np.zeros((nDev,ItersAR),dtype='float'))
DR = pd.DataFrame(np.zeros((nDev,ItersAR),dtype='float'))
DRerr = pd.DataFrame(np.zeros((nDev,ItersAR),dtype='float'))
GUIFrameL = pd.DataFrame(np.zeros((nRows,4)),columns=['Device ID','Resistance','Uncertainty','Timestamp'],dtype='object')
GUIFrameR = pd.DataFrame(np.zeros((nRows,4)),columns=['Device ID','Resistance','Uncertainty','Timestamp'],dtype='object')
RD = np.zeros(105)
PBStart = np.zeros(nRows) # For use in determining time taken to obtain measurements from USB6216
PBEnd = np.zeros(nRows) # For use in determining time taken to obtain measurements from USB6216
PBTime = np.zeros(nRows) # For use in determining time taken to obtain measurements from USB6216
PBElapsed = np.zeros(ItersAR) # For use in determining time taken to obtain measurements from USB6216
PBAverage = np.zeros(ItersAR) # For use in determining time taken to obtain measurements from USB6216
GrabStart = np.zeros(ItersAR) # For use in determining time taken to run a grab
GrabEnd = np.zeros(ItersAR) # For use in determining time taken to run a grab
GrabTime = np.zeros(ItersAR) # for use in determining time taken to run a grab
GrabTime[:] = np.nan
#---- Initialization of files for data and control
stopText = """If you want to stop the program, simply replace this text with 'stop' and save it.""" # Resets the code used to end a grab before quitting program
with open('stop.txt', 'w') as fStop: # Initialise stop button
    fStop.write(stopText)
nRun=1
measurementName = str(ID.readCurrentSetup()) + str(ID.readCurrentID())
today = date.today()
t=today.strftime("%y%m%d")
dataPath = basePath + '/'+t+'_'+measurementName
if not os.path.exists(dataPath):
    os.makedirs(dataPath)
with open(dataPath + '/log_'+t+'_'+measurementName+'.txt', 'w') as fLog:
    fLog.write('Start: '+str(datetime.now()) + '\n' +
               'Assay Number: ' + measurementName + '\n' +
               'Pi Box: ' + PiBox + '\n' +
               'Preamp 1 gain: ' + str(P1Gain) + '\n' +
               'Preamp 2 gain: ' + str(P2Gain) + '\n' +
               'Source Voltage: ' + str(VSource) + ' V' + '\n' +
               'NIDAQ Sample Rate: ' + str(SR) + ' Hz' + '\n' +
               'NIDAQ Samples per Channel: ' + str(SpC) + '\n' +
               'Number of Grabs: ' + str(ItersAR) + '\n' +
               'Time between Grabs: ' + str(WaitAR) + ' s' + '\n \n'
               )

#---- Initialization of instruments
print ('Initialise instruments') ## Keep for diagnostics; Off from 17JAN24 APM
# ---- Raspberry Pi --------------
CtrlPi = PiMUX()
#CtrlPi.setRelayToOn() # Switches multiplexer power on -- deactivated to save power 26FEB24 APM
CtrlPi.setMuxToOutput(0)  # Sets multiplexer to state with all outputs off
#---- NIDAQ Output Port for Source --------------
daqout_S = USB6216Out(0)
daqout_S.setOptions({"feedBack":"Int","scaleFactor":1})
#---- NIDAQ Input Port for Drain running PairBurst on USB6216 --------------
daqin_Drain = USB6216InPB()
daqin_Drain.setOptions({"scaleFactor":1})

def updateGUI(): # Updates the data in the GUI -- last edited APM 19Jan24
    global nGrab
    GUI_tableL.updateModel(TableModel(GUIFrameL))
    GUI_tableR.updateModel(TableModel(GUIFrameR))
    GUI_tableL.redraw()
    GUI_tableR.redraw()
    assay = tk.Label(root, text=('Assay Number: '+t+'_'+measurementName),bg="skyblue")
    assay.grid(row=0,column=0,padx=5,pady=5)
    run = tk.Label(root, text=('Run Number: ' + str(nRun)),bg="skyblue")
    run.grid(row=1,column=0,padx=5,pady=5)
    grabNum = tk.Label(root, text=('Grab Number: '+str(nGrab+1)),bg="skyblue")
    grabNum.grid(row=3,column=0,padx=5,pady=5)
    grabTot = tk.Label(root, text=('of total grabs: '+ str(ItersAR)),bg="skyblue")
    grabTot.grid(row=4,column=0,padx=5,pady=5)
    root.update_idletasks()

def grabStart(): # Operates the Grab Start button in the GUI
    updateThread = threading.Thread(target=measLoop)
    updateThread.daemon = True
    updateThread.start()

def stop(): # Operates mechanism to complete grab before ending program -- last edited APM 17Jan24
    with open('stop.txt', 'w') as fStop:
        fStop.write('stop')

def end(): # Operates mechanism to end the program entirely
    with open(dataPath + '/log_'+t+'_'+measurementName+'.txt', 'a') as fLog:
        fLog.write('End: ' + str(datetime.now()) + '\n')
    ID.increaseID()

def grab(nGrab,zeroThres): # Code to implement a single grab of all the devices on a chip -- last edited APM 17Jan24
    global nRun,RD
    print('Grab: ',nGrab+1)
    with open(dataPath + '/log_'+t+'_'+measurementName+'.txt', 'a') as fLog:
        fLog.write('Grab: '+str(nGrab+1)+' started: '+str(datetime.now())+'\n')
#    print('Start of grab: ',nGrab+1) ## Keep for diagnostics; Off from 18JAN24 APM
#    print('Set NIDAQ Voltage')  ## Keep for diagnostics; Off from 17JAN24 APM
    daqout_S.goTo(VSource, delay=0.0)  # Run the source up to specified voltage
    CtrlPi.setRelayToOn()  # Ensure power relay is on
    time.sleep(0.5) # Give time for MUXes to properly run up.
    RD[0]=nGrab+1
    for i in range(nRows):
        nRow = i+1
#        print('Row = ',nRow) ## Keep for diagnostics; Off from 15JAN24 APM
        nDevL = i+1
        nDevR = 27+i # Updated for Gen4 26FEB24 APM
#        print('Device Left =', nDevL ,'Device Right =', nDevR) ## Keep for diagnostics; Off from 15JAN24 APM
        #---- Set Multiplexer
        CtrlPi.setMuxToOutput(nRow)
        PBStart[i] = time.time()
        #---- Grab row data from NIDAQ
        Drain = daqin_Drain.get('inputLevel')
        if Drain[0] > zeroThres: # Converts to resistance and sets open circuit to zero for left-bank devices
            DL.iloc[i,nGrab] = ((VSource*P1Gain)/Drain[0])
            DLerr.iloc[i,nGrab] = (Drain[1]/Drain[0])*DL.iloc[i,nGrab]
        else:
            DL.iloc[i,nGrab] = 0.0
            DLerr.iloc[i,nGrab] = 0.0
        if Drain[2] > zeroThres: # Converts to resistance and sets open circuit to zero for right-bank devices
            DR.iloc[i,nGrab] = ((VSource*P2Gain)/Drain[2])
            DRerr.iloc[i,nGrab] = (Drain[3]/Drain[2])*DR.iloc[i,nGrab]
        else:
            DR.iloc[i,nGrab] = 0.0
            DRerr.iloc[i,nGrab] = 0.0
#        print(f'DL = {DL.iloc[i,nGrab]:.2f} +/- {DLerr.iloc[i,nGrab]:.2f} ohms') ## Keep for diagnostics; Off from 15JAN24 APM
#        print(f'DR = {DR.iloc[i,nGrab]:.2f} +/- {DRerr.iloc[i,nGrab]:.2f} ohms') ## Keep for diagnostics; Off from 15JAN24 APM
        RD[(2*nDevL-1)] = round(DL.iloc[i,nGrab],3)
        RD[(2*nDevL)] = round(DLerr.iloc[i,nGrab],3)
        RD[(2*nDevR-1)] = round(DR.iloc[i,nGrab],3)
        RD[(2*nDevR)] = round(DRerr.iloc[i,nGrab],3)
        #---- send data to file
        with open(runPath+'/'+t+'_'+measurementName+'_R'+str(nRun)+'_Dev'+str(nDevL)+'.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([str(nGrab+1),str(DL.iloc[i,nGrab]),str(DLerr.iloc[i,nGrab]),str(datetime.now().strftime("%H:%M:%S"))])
        with open(runPath+'/'+t+'_'+measurementName+'_R'+str(nRun)+'_Dev'+str(nDevR)+'.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([str(nGrab+1),str(DR.iloc[i,nGrab]),str(DRerr.iloc[i,nGrab]),str(datetime.now().strftime("%H:%M:%S"))])
        #---- Update data for the GUI
        GUIFrameL.iloc[nRow-1] = [nDevL,round(DL.iloc[i,nGrab],2),round(DLerr.iloc[i,nGrab],2),datetime.now().strftime("%H:%M:%S")]
        GUIFrameR.iloc[nRow-1] = [nDevR,round(DR.iloc[i,nGrab],2),round(DRerr.iloc[i,nGrab],2),datetime.now().strftime("%H:%M:%S")] # Updated for Gen4 26FEB24 APM
        updateGUI()
        #---- End of row timing
        PBEnd[i] = time.time()
        PBTime[i] = PBEnd[i]-PBStart[i]
        PBElapsed[nGrab] = PBEnd[nRows-1]-PBStart[0]
        PBAverage[nGrab] = PBTime.mean()
    #---- Drop all device data to megatable at end of grab
    with open(runPath+'/'+t+'_'+measurementName+'_R'+str(nRun)+'.csv','a',newline='') as f:
        writer = csv.writer(f)
        writer.writerow(RD[:])
#    ResData.to_csv(runPath+'/'+t+'_'+measurementName+'_R'+str(nRun)+'.csv', index=False)
    # ---- Run source voltage back to zero
    daqout_S.goTo(0.0, delay=0.0)
    # ---- Switch Multiplexer to off state.
    CtrlPi.setMuxToOutput(0)
    CtrlPi.setRelayToOff()  # Switches multiplexer power off
#    print('End of grab: ', nGrab+1) ## Keep for diagnostics; Off from 18JAN24 APM

    return PBElapsed,PBAverage

def measLoop():
    global measurementName,nRun,runPath,nGrab
    #---- Currently the main program
    with open(dataPath+'/log_'+t+'_'+measurementName+'.txt', 'a') as fLog:
        fLog.write('Measurement '+measurementName+'R'+str(nRun)+' started at: '+str(datetime.now())+'\n')
    runPath = dataPath+'/'+t+'_'+measurementName+'_R'+str(nRun)
    if not os.path.exists(runPath):
        os.makedirs(runPath)
    with open(runPath+'/'+t+'_'+measurementName+'_R'+str(nRun)+'.csv','w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['Grab','R1','dR1','R2','dR2','R3','dR3','R4','dR4','R5','dR5','R6','dR6','R7','dR7','R8','dR8','R9','dR9','R10','dR10',
                         'R11','dR11','R12','dR12','R13','dR13','R14','dR14','R15','dR15','R16','dR16','R17','dR17','R18','dR18','R19','dR19','R20','dR20',
                         'R21','dR21','R22','dR22','R23','dR23','R24','dR24','R25','dR25','R26','dR26','R27','dR27','R28','dR28','R29','dR29','R30','dR30',
                         'R31','dR31','R32','dR32','R33','dR33','R34','dR34','R35','dR35','R36','dR36','R37','dR37','R38','dR38','R39','dR39','R40','dR40',
                         'R41','dR41','R42','dR42','R43','dR43','R44','dR44','R45','dR45','R46','dR46','R47','dR47','R48','dR48','R49','dR49','R50','dR50',
                         'R51','dR51','R52','dR52'])
    for i in range(nDev):
        with open(runPath+'/'+t+'_'+measurementName+'_R'+str(nRun)+'_Dev'+str(i+1)+'.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Grab','Resistance (ohms)','Uncertainty (ohms)','timestamp'])
    for i in range(ItersAR):
        nGrab = i
        GrabStart[i] = time.time()
        grab(nGrab,zeroThres)
        GrabEnd[i] = time.time()
        GrabTime[i] = GrabEnd[i] - GrabStart[i]
        #---- check for grab-stop signal
        with open('stop.txt', 'r') as fStop:
            r = fStop.read()
            if r == 'stop':
                print('Stopped safely after completed grab: ',nGrab+1)
                break
        GT = WaitAR-GrabTime[i]
        #---- wait for the next scheduled grab
        if nGrab+1 < ItersAR:
            time.sleep(GT)
    print()
    print(f'Time elapsed = {(GrabEnd[i] - GrabStart[0]):.2f} s')
    print(f'Average time per grab = {np.nanmean(GrabTime):.2f} s')
    print()
    print('Measurement Daemon Completed Successfully')
    with open(dataPath + '/log_'+t+'_'+measurementName+'.txt', 'a') as fLog:
        fLog.write('Measurement '+measurementName+'R'+str(nRun)+' finished at: '+str(datetime.now())+'\n'+
                   'with '+str(nGrab+1)+' of '+str(ItersAR)+' grabs completed.'+'\n \n'
                   )
    nRun += 1
    print('Finish Set-up')  ## Keep for diagnostics; Off from 17JAN24 APM
    # ---- Run source voltage back to zero
    daqout_S.goTo(0.0, delay=0.0)
    # ---- Switch Multiplexer to off state.
    CtrlPi.setMuxToOutput(0)
    CtrlPi.setRelayToOff()  # Switches multiplexer power off
    #root.quit() ## remove this line for the program to not quit at the end

if __name__ == "__main__":
    # GUI Code
    nGrab=0
    root = tk.Tk()
    root.title("Live Measurement GUI")
    root.geometry('1100x650')
#    root.maxsize(1200,800)
    root.config(bg="skyblue")
    left_table = Frame(root)
    left_table.grid(row=0,column=1,rowspan=7,padx=5,pady=5)
    right_table = Frame(root)
    right_table.grid(row=0,column=2,rowspan=7,padx=5,pady=5)
    GUI_tableL = Table(left_table,showtoolbar=False,showstatusbar=False,width=365,height=590)
    GUI_optionsL = {'align':'w','cellwidth':85,'floatprecision':2,'font':'Arial','fontsize':12,'linewidth':1,'rowheight':22}
    pdtb.config.apply_options(GUI_optionsL,GUI_tableL)
    GUI_tableR = Table(right_table,showtoolbar=False,showstatusbar=False,width=365,height=590)
    GUI_optionsR = {'align':'w','cellwidth':85,'floatprecision':2,'font':'Arial','fontsize':12,'linewidth':1,'rowheight':22}
    pdtb.config.apply_options(GUI_optionsR,GUI_tableR)
    GUI_tableL.show()
    GUI_tableR.show()
    GUI_tableL.updateModel(TableModel(GUIFrameL))
    GUI_tableR.updateModel(TableModel(GUIFrameR))
    assay = tk.Label(root,text=('Assay Number: '+t+'_'+measurementName),bg="skyblue")
    assay.grid(row=0,column=0,padx=5,pady=5)
    run = tk.Label(root, text=('Run Number: '+str(nRun)),bg="skyblue")
    run.grid(row=1, column=0, padx=5, pady=5)
    start_button = tk.Button(root, text='Start Run',command=lambda:grabStart())
    start_button.grid(row=2,column=0,padx=5,pady=5)
    grabNum = tk.Label(root, text=('Grab Number: '+str(nGrab+1)),bg="skyblue")
    grabNum.grid(row=3, column=0, padx=5, pady=5)
    grabTot = tk.Label(root, text=('of total grabs: '+str(ItersAR)),bg="skyblue")
    grabTot.grid(row=4, column=0, padx=5, pady=5)
    stop_button = tk.Button(root,text='Last Grab',command=lambda:stop())
    stop_button.grid(row=5,column=0,padx=5,pady=5)
    exit_button = tk.Button(root,text='End Program',command=lambda:[end(),root.quit()])
    exit_button.grid(row=6,column=0,padx=5,pady=5)
    root.mainloop()