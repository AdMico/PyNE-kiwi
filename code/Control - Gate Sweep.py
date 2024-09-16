"""
Brought to PyNE-kiwi v1.0.0 on Tue Sep 3 2024 by APM

@developers: Adam Micolich

@author: Adam Micolich

Control program for basic gate voltage sweep on VUW setup
"""

from Imports import *
import time
from datetime import datetime,date
import os
import csv
import pandas as pd
import GlobalMeasID as ID
import tkinter as tk
import threading
from Config import basePath,PiBox,B1500ADCSet,B1500NPLC,K2401compl,Diags
from Config import VgStart,VgStop,VgStep,Settle
from Config import VS_SMU1,VS_SMU2,VS_SMU3,VS_SMU4
from Config import B1500ICOM1,B1500ICOM2,B1500ICOM3,B1500ICOM4
from Config import B1500Filt1,B1500Filt2,B1500Filt3,B1500Filt4
global nRun

class GateSweep(): # Setting up as a class for later scripting potential -- 10SEP24 APM
    def __init__(self):
        super(GateSweep, self).__init__()
        self.dev = GateSweep
        self.type = "GateSweep"  # We can check each instrument for its type and react accordingly

    def initialise(self): # Routine to start everything up in the code
        global CtrlPi,B1500,B2201,K2401
        global dataPath,measurementName,t
        global VgForward,VgBackward,I_1,I_2,I_3,I_4,I_5,I_6,I_7,I_8,I_g
        if Diags == "Verbose":
            print("Initialising Instruments")
        # Initialise instruments
        CtrlPi = PiMUX()
        B1500 = B1500()
        B1500.init()
        B2201 = B2201()
        B2201.init()
        K2401 = K2401(24)
        K2401.setOptions({"beepEnable": False,"sourceMode": "voltage","sourceRange":K2401sourceRange,"senseRange": K2401senseRange,"compliance": K2401compl,"scaleFactor":1})
        ## Initialise datapath and files
        if Diags == "Verbose":
            print("Setup data files")
        dataPath,measurementName,t = GateSweeper.dataPathInit()
        GateSweeper.logFileMaker()
        GateSweeper.stopFileInit()
        ## Build arrays of gate voltage values for forward and backward sweeps
        if Diags == "Verbose":
            print("Build Gate Voltage and Source Current Arrays")
        VgForward = GateSweeper.array(VgStart,VgStop,VgStep)
        VgBackward = GateSweeper.array(VgStop,VgStart,VgStep)
        nVg = len(VgForward)
        I_1 = pd.DataFrame(np.zeros((nVg,1),dtype='float'))
        I_2 = pd.DataFrame(np.zeros((nVg,1),dtype='float'))
        I_3 = pd.DataFrame(np.zeros((nVg,1),dtype='float'))
        I_4 = pd.DataFrame(np.zeros((nVg,1),dtype='float'))
        I_5 = pd.DataFrame(np.zeros((nVg,1),dtype='float'))
        I_6 = pd.DataFrame(np.zeros((nVg,1),dtype='float'))
        I_7 = pd.DataFrame(np.zeros((nVg,1),dtype='float'))
        I_8 = pd.DataFrame(np.zeros((nVg,1),dtype='float'))
        I_g = pd.DataFrame(np.zeros((nVg,1),dtype='float'))
        ## Set B1500 source values
        if Diags == "Verbose":
            print("Set B1500 SMUs")
        B1500.setV1(VS_SMU1)
        B1500.setV2(VS_SMU2)
        B1500.setV3(VS_SMU3)
        B1500.setV4(VS_SMU4)
        ## Set K2401 starting gate voltage
        if Diags == "Verbose":
            print("Set K2401 SMU")
        K2401._setOutputEnable("enable")
        K2401._setSourceLevel(VgStart)

    def dataPathInit(self): # Initialise the folder where the data for this run will be stored
        measurementName = str(ID.readCurrentSetup()) + str(ID.readCurrentID())
        today = date.today()
        t = today.strftime("%y%m%d")
        dataPath = basePath + "/" + t + "_" + measurementName
        if not os.path.exists(dataPath):
            os.makedirs(dataPath)
        return dataPath,measurementName,t

    def logFileMaker(self): # Initialise the log file and enter the starting data
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'w') as fLog:
            fLog.write('Start of GateSweeper: ' + str(datetime.now()) + '\n' +
                       'Measurement Number: ' + measurementName + '\n' +
                       'Pi Box: ' + PiBox + '\n' +
                       'B1500 Mode: ' + str(B1500ADCSet) + '\n' +
                       'B1500 NPLC Setting: ' + str(B1500NPLC) + '\n' +
                       'B1500 SMU 1: V_S = ' + str(VS_SMU1) + 'V, ' + 'Compliance = ' + str(B1500ICOM1) + 'A, Filter = ' + str(B1500Filt1) + '\n' +
                       'B1500 SMU 2: V_S = ' + str(VS_SMU2) + 'V, ' + 'Compliance = ' + str(B1500ICOM2) + 'A, Filter = ' + str(B1500Filt2) + '\n' +
                       'B1500 SMU 3: V_S = ' + str(VS_SMU3) + 'V, ' + 'Compliance = ' + str(B1500ICOM3) + 'A, Filter = ' + str(B1500Filt3) + '\n' +
                       'B1500 SMU 4: V_S = ' + str(VS_SMU4) + 'V, ' + 'Compliance = ' + str(B1500ICOM4) + 'A, Filter = ' + str(B1500Filt4) + '\n' +
                       'K2401 Compliance: ' + str(K2401compl) + ' A' + '\n \n'
                       )

    def stopFileInit(self): # Note for later, do we want a path to Desktop for this? -- 10SEP24 APM
        stopText = """If you want to stop the program, simply replace this text with 'stop' and save it."""  # Resets the code used to end a grab before quitting program
        with open('stop.txt', 'w') as fStop:  # Initialise stop button
            fStop.write(stopText)

    def stop(self): # Operates stop mechanism (may not need until GUI) -- 14SEP24 APM
        with open('stop.txt', 'w') as fStop:
            fStop.write('stop')

    def array(self,start,target,stepsize):
        """Helper function that creates single 1D array from start to stop. Used in targetArray()"""
        sign = 1 if (target>start) else -1
        sweepArray = np.arange(start,np.round(target+sign*stepsize,decimals=5),sign*stepsize) #The rounding makes function more predictable
        return sweepArray

    def updateGUI(self):  # Updates the data in the GUI -- last edited APM 19Jan24
        global nRun
        assay = tk.Label(root, text=('Assay Number: ' + t + '_' + measurementName), bg="purple")
        assay.grid(row=0, column=0, padx=5, pady=5)
        run = tk.Label(root, text=('Sweep Number: ' + str(nRun)), bg="purple")
        run.grid(row=1, column=0, padx=5, pady=5)
        root.update_idletasks()

    def oddStart(self):  # Operates the Grab Start button in the GUI
        updateThread = threading.Thread(target=GateSweeper.gateSweepOdd)
        updateThread.daemon = True
        updateThread.start()

    def evenStart(self):  # Operates the Grab Start button in the GUI
        updateThread = threading.Thread(target=GateSweeper.gateSweepEven)
        updateThread.daemon = True
        updateThread.start()

    def bothStart(self):  # Operates the Grab Start button in the GUI
        updateThread = threading.Thread(target=GateSweeper.gateSweepBoth)
        updateThread.daemon = True
        updateThread.start()

    def switchedStart(self):  # Operates the Grab Start button in the GUI
        updateThread = threading.Thread(target=GateSweeper.gateSweepSwitched)
        updateThread.daemon = True
        updateThread.start()

    def end(self):
        if Diags == "Verbose":
            print("Finalising Software")
        ## Finalise by returning the system to a stable state between measurements
        B1500.setV1(0.0)
        B1500.setV2(0.0)
        B1500.setV3(0.0)
        B1500.setV4(0.0)
        K2401._setSourceLevel(0.0)
        K2401._setOutputEnable("")
        B2201.clear()
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('End of GateSweeper: ' + str(datetime.now()) + '\n')
        ID.increaseID()

    def gateSweepOdd(self): #Just sweep the odd device pins
        global VgForward,VgBackward,I_1,I_2,I_3,I_4,I_5,I_6,I_7,I_8,I_g,nRun
        if Diags == "Verbose":
            print("Starting odd sweep: ",nRun)
        ## Set Odd Configuration
        CtrlPi.odd()
        B2201.odd()
        ## Initialise File Handling for odd sweep
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('Measurement ' + measurementName + ' Sweep ' + str(nRun) + ' odd_forward' + ' started at: ' + str(datetime.now()) + '\n')
        with open(dataPath + '/' + t + '_' + measurementName + '_' + str(nRun) + '_odd_forward.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Vg (V)', 'Is_1 (A)', 'Is_3 (A)', 'Is_5 (A)', 'Is_7 (A)', 'Ig (A)'])
        ##  Start the odd sweep algorithm -- Turn into a proper function later 14SEP24 APM
        for i in range(len(VgForward)):
            if Diags == "Verbose":
                print("Forward-trace Iteration: ",i+1)
            K2401._setSourceLevel(VgForward[i])
            time.sleep(Settle)
            I_1[i] = B1500.getI1()
            I_3[i] = B1500.getI2()
            I_5[i] = B1500.getI3()
            I_7[i] = B1500.getI4()
            I_g[i] = K2401._getSenseLevel()
            # send data to file -- Might need to test file name stays open in this setup 14SEP24 APM
            with open(dataPath + '/' + t + '_' + measurementName + '_' + str(nRun) + '_odd_forward.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([str(VgForward[i]), str(I_1.iloc[i,0]), str(I_3.iloc[i,0]),str(I_5.iloc[i,0]), str(I_7.iloc[i,0]), str(I_g.iloc[i,0])])
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('Measurement ' + measurementName + ' Sweep ' + str(nRun) +  ' odd_backward' + ' started at: ' + str(
                datetime.now()) + '\n')
        with open(dataPath + '/' + t + '_' + measurementName + '_' + str(nRun) + '_odd_backward.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Vg (V)', 'Is_1 (A)', 'Is_3 (A)', 'Is_5 (A)', 'Is_7 (A)', 'Ig (A)'])
        for i in range(len(VgBackward)):
            if Diags == "Verbose":
                print("Back-trace Iteration: ",i+1)
            K2401._setSourceLevel(VgBackward[i])
            time.sleep(Settle)
            I_1[i] = B1500.getI1()
            I_3[i] = B1500.getI2()
            I_5[i] = B1500.getI3()
            I_7[i] = B1500.getI4()
            I_g[i] = K2401._getSenseLevel()
            # send data to file -- Might need to test file name stays open in this setup 14SEP24 APM
            with open(dataPath + '/' + t + '_' + measurementName + '_' + str(nRun) +  '_odd_backward.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([str(VgBackward[i]), str(I_1.iloc[i,0]), str(I_3.iloc[i,0]),str(I_5.iloc[i,0]), str(I_7.iloc[i,0]), str(I_g.iloc[i,0])])
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('Measurement ' + measurementName + ' Sweep ' + str(nRun) + ' odd' + ' finished at: ' + str(datetime.now()) + '\n')
        print("End sweep: ", nRun)
        nRun += 1
        GateSweeper.updateGUI()

    def gateSweepEven(self): #Just sweep the even device pins
        global VgForward,VgBackward,I_1,I_2,I_3,I_4,I_5,I_6,I_7,I_8,I_g,nRun
        if Diags == "Verbose":
            print("Starting even sweep: ",nRun)
        ## Set Even Configuration
        CtrlPi.even()
        B2201.even()
        ## Initialise File Handling for even sweep
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('Measurement ' + measurementName + ' Sweep ' + str(nRun) + ' even-forward' + ' started at: ' + str(
                datetime.now()) + '\n')
        with open(dataPath + '/' + t + '_' + measurementName + '_' + str(nRun) + '_even_forward.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Vg (V)', 'Is_2 (A)', 'Is_4 (A)', 'Is_6 (A)', 'Is_8 (A)', 'Ig (A)'])
        ##  Start the even sweep algorithm -- Turn into a proper function later 14SEP24 APM
        for i in range(len(VgForward)):
            if Diags == "Verbose":
                print("Forward-trace Iteration: ",i+1)
            K2401._setSourceLevel(VgForward[i])
            time.sleep(Settle)
            I_2[i] = B1500.getI1()
            I_4[i] = B1500.getI2()
            I_6[i] = B1500.getI3()
            I_8[i] = B1500.getI4()
            I_g[i] = K2401._getSenseLevel()
            # send data to file -- Might need to test file name stays open in this setup 14SEP24 APM
            with open(dataPath + '/' + t + '_' + measurementName + '_' + str(nRun) + '_even_forward.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([str(VgForward[i]), str(I_2.iloc[i,0]), str(I_4.iloc[i,0]), str(I_6.iloc[i,0]), str(I_8.iloc[i,0]), str(I_g.iloc[i,0])])
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('Measurement ' + measurementName + ' Sweep ' + str(nRun) + ' even-backward' + ' started at: ' + str(
                datetime.now()) + '\n')
        with open(dataPath + '/' + t + '_' + measurementName + '_' + str(nRun) + '_even_backward.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Vg (V)', 'Is_2 (A)', 'Is_4 (A)', 'Is_6 (A)', 'Is_8 (A)', 'Ig (A)'])
        for i in range(len(VgBackward)):
            if Diags == "Verbose":
                print("Back-trace Iteration: ",i+1)
            K2401._setSourceLevel(VgBackward[i])
            time.sleep(Settle)
            I_2[i] = B1500.getI1()
            I_4[i] = B1500.getI2()
            I_6[i] = B1500.getI3()
            I_8[i] = B1500.getI4()
            I_g[i] = K2401._getSenseLevel()
            # send data to file -- Might need to test file name stays open in this setup 14SEP24 APM
            with open(dataPath + '/' + t + '_' + measurementName + '_' + str(nRun) + '_even_backward.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([str(VgBackward[i]), str(I_2.iloc[i,0]), str(I_4.iloc[i,0]), str(I_6.iloc[i,0]), str(I_8.iloc[i,0]), str(I_g.iloc[i,0])])
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('Measurement ' + measurementName + ' Sweep ' + str(nRun) + ' even' + ' finished at: ' + str(datetime.now()) + '\n')
        print("End sweep: ", nRun)
        nRun += 1
        GateSweeper.updateGUI()

    def gateSweepBoth(self): #Sweep the odd device pins first then the even device pins
        global VgForward,VgBackward,I_1,I_2,I_3,I_4,I_5,I_6,I_7,I_8,I_g,nRun
        GateSweeper.gateSweepOdd()
        GateSweeper.gateSweepEven()

    def gateSweepSwitched(self): #Sweep with switching from odd to even each gate point
        global VgForward,VgBackward,I_1,I_2,I_3,I_4,I_5,I_6,I_7,I_8,I_g,nRun
        if Diags == "Verbose":
            print("Starting switched sweep: ",nRun)
        ## Set to odd for start of switched Configuration
        CtrlPi.odd()
        B2201.odd()
        ## Initialise File Handling for even sweep
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write(
                'Measurement ' + measurementName + ' Sweep ' + str(nRun) + ' switched-forward' + ' started at: ' + str(datetime.now()) + '\n')
        with open(dataPath + '/' + t + '_' + measurementName + '_' + str(nRun) + '_both_forward.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(
                ['Vg (V)', 'Is_1 (A)', 'Is_2 (A)', 'Is_3 (A)', 'Is_4 (A)', 'Is_5 (A)', 'Is_6 (A)', 'Is_7 (A)',
                 'Is_8 (A)', 'Ig (A)'])
        ##  Start the switched sweep algorithm -- Turn into a proper function later 14SEP24 APM
        for i in range(len(VgForward)):
            if Diags == "Verbose":
                print("Forward-trace Iteration: ",i+1)
            K2401._setSourceLevel(VgForward[i])
            time.sleep(Settle)
            I_1[i] = B1500.getI1()
            I_3[i] = B1500.getI2()
            I_5[i] = B1500.getI3()
            I_7[i] = B1500.getI4()
            CtrlPi.even()
            B2201.even()
            time.sleep(Settle)
            I_2[i] = B1500.getI1()
            I_4[i] = B1500.getI2()
            I_6[i] = B1500.getI3()
            I_8[i] = B1500.getI4()
            I_g[i] = K2401._getSenseLevel()
            CtrlPi.odd()
            B2201.odd()
            # send data to file -- Might need to test file name stays open in this setup 14SEP24 APM
            with open(dataPath + '/' + t + '_' + measurementName + '_' + str(nRun) + '_both_forward.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([str(VgForward[i]),str(I_1.iloc[i,0]),str(I_2.iloc[i,0]),str(I_3.iloc[i,0]),str(I_4.iloc[i,0]),str(I_5.iloc[i,0]),str(I_6.iloc[i,0]),str(I_7.iloc[i,0]),str(I_8.iloc[i,0]),str(I_g.iloc[i,0])])
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write(
                'Measurement ' + measurementName + ' Sweep ' + str(nRun) + ' both-backward' + ' started at: ' + str(datetime.now()) + '\n')
        with open(dataPath + '/' + t + '_' + measurementName + '_' + str(nRun) + '_both_backward.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(
                ['Vg (V)', 'Is_1 (A)', 'Is_2 (A)', 'Is_3 (A)', 'Is_4 (A)', 'Is_5 (A)', 'Is_6 (A)', 'Is_7 (A)',
                 'Is_8 (A)', 'Ig (A)'])
        for i in range(len(VgBackward)):
            if Diags == "Verbose":
                print("Back-trace Iteration: ",i+1)
            K2401._setSourceLevel(VgBackward[i])
            time.sleep(Settle)
            I_1[i] = B1500.getI1()
            I_3[i] = B1500.getI2()
            I_5[i] = B1500.getI3()
            I_7[i] = B1500.getI4()
            CtrlPi.even()
            B2201.even()
            time.sleep(Settle)
            I_2[i] = B1500.getI1()
            I_4[i] = B1500.getI2()
            I_6[i] = B1500.getI3()
            I_8[i] = B1500.getI4()
            I_g[i] = K2401._getSenseLevel()
            CtrlPi.odd()
            B2201.odd()
            # send data to file -- Might need to test file name stays open in this setup 14SEP24 APM
            with open(dataPath + '/' + t + '_' + measurementName + '_' + str(nRun) + '_both_backward.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([str(VgBackward[i]),str(I_1.iloc[i,0]),str(I_2.iloc[i,0]),str(I_3.iloc[i,0]),str(I_4.iloc[i,0]),str(I_5.iloc[i,0]),str(I_6.iloc[i,0]),str(I_7.iloc[i,0]),str(I_8.iloc[i,0]),str(I_g.iloc[i,0])])
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('Measurement ' + measurementName + ' Sweep ' + str(nRun) + ' both' + ' finished at: ' + str(datetime.now()) + '\n')
        print("End sweep: ",nRun)
        nRun += 1
        GateSweeper.updateGUI()

if __name__ == "__main__":
    # GUI Code
    nRun=1
    GateSweeper = GateSweep()
    GateSweeper.initialise()
    root = tk.Tk()
    root.title("Gate Sweeper GUI")
    root.geometry('200x250')
    root.config(bg="purple")
    assay = tk.Label(root,text=('Assay Number: '+t+'_'+measurementName),bg="purple")
    assay.grid(row=0,column=0,padx=5,pady=5)
    run = tk.Label(root,text=('Sweep Number: '+str(nRun)),bg="purple")
    run.grid(row=1, column=0, padx=5, pady=5)
    odd_button = tk.Button(root,text='Start odd sweep',command=lambda:GateSweeper.oddStart())
    odd_button.grid(row=2, column=0, padx=5, pady=5)
    even_button = tk.Button(root,text='Start even sweep',command=lambda:GateSweeper.evenStart())
    even_button.grid(row=3, column=0, padx=5, pady=5)
    both_button = tk.Button(root,text='Start odd+even sweep',command=lambda:GateSweeper.bothStart())
    both_button.grid(row=4, column=0, padx=5, pady=5)
    switched_button = tk.Button(root,text='Start switched sweep',command=lambda:GateSweeper.switchedStart())
    switched_button.grid(row=5, column=0, padx=5, pady=5)
    exit_button = tk.Button(root,text='End GateSweeper',command=lambda:[GateSweeper.end(),root.quit()])
    exit_button.grid(row=6,column=0,padx=5,pady=5)
    root.mainloop()