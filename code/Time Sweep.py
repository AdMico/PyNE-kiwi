"""
Brought to PyNE-kiwi v1.0.0 on Tue Sep 3 2024 by APM

@developers: Adam Micolich

@author: Adam Micolich

Control program for basic time sweep on VUW setup
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
import math
import matplotlib.pyplot as plt

from Config import basePath,PiBox,B1500ADCSet,B1500NPLC,K2401compl,Diags
from Config import Vg,SampleWait,MaxDuration,Settle
from Config import VS_SMU1,VS_SMU2,VS_SMU3,VS_SMU4
from Config import B1500ICOM1,B1500ICOM2,B1500ICOM3,B1500ICOM4
from Config import B1500Filt1,B1500Filt2,B1500Filt3,B1500Filt4
global nRun

class TimeSweep(): # Setting up as a class for later scripting potential -- 10SEP24 APM
    def __init__(self):
        super(TimeSweep, self).__init__()
        self.dev = TimeSweep
        self.type = "TimeSweep"  # We can check each instrument for its type and react accordingly

    def initialise(self): # Routine to start everything up in the code
        global CtrlPi,B1500,B2201,K2401
        global dataPath,measurementName,t,nTime
        global elapsed,I_1,I_2,I_3,I_4,I_5,I_6,I_7,I_8,I_g
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
        dataPath,measurementName,t = TimeSweeper.dataPathInit()
        TimeSweeper.logFileMaker()
        TimeSweeper.stopFileInit()
        nTime = math.ceil(MaxDuration/SampleWait) + 3 ## Is 3 and not 1 to avoid array overrun during stop -- 16SEP24 APM
        elapsed = pd.DataFrame(np.zeros((nTime,1),dtype='float'))
        I_1 = pd.DataFrame(np.zeros((nTime,1),dtype='float'))
        I_2 = pd.DataFrame(np.zeros((nTime,1),dtype='float'))
        I_3 = pd.DataFrame(np.zeros((nTime,1),dtype='float'))
        I_4 = pd.DataFrame(np.zeros((nTime,1),dtype='float'))
        I_5 = pd.DataFrame(np.zeros((nTime,1),dtype='float'))
        I_6 = pd.DataFrame(np.zeros((nTime,1),dtype='float'))
        I_7 = pd.DataFrame(np.zeros((nTime,1),dtype='float'))
        I_8 = pd.DataFrame(np.zeros((nTime,1),dtype='float'))
        I_g = pd.DataFrame(np.zeros((nTime,1),dtype='float'))
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
        K2401._setSourceLevel(Vg)

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
            fLog.write('Start of TimeSweeper: ' + str(datetime.now()) + '\n' +
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

    def updateGUI(self):  # Updates the data in the GUI -- last edited APM 19Jan24
        global nRun
        assay = tk.Label(root, text=('Assay Number: ' + t + '_' + measurementName), bg="purple")
        assay.grid(row=0, column=0, padx=5, pady=5)
        run = tk.Label(root, text=('Sweep Number: ' + str(nRun)), bg="purple")
        run.grid(row=1, column=0, padx=5, pady=5)
        root.update_idletasks()

    def timeStart(self):  # Operates the Time Start button in the GUI
        global timex, plotI1, plotI2,plotI3,plotI4,plotI5,plotI6,plotI7,plotI8,plotIg
        TimeSweeper.stopFileInit()
        updateThread = threading.Thread(target=TimeSweeper.timeSweep)
        updateThread.daemon = True
        updateThread.start()
        #Initialise Live Plotting
        timex = []
        plotI1 = []
        plotI2 = []
        plotI3 = []
        plotI4 = []
        plotI5 = []
        plotI6 = []
        plotI7 = []
        plotI8 = []
        plotIg = []
        plot_ys = [plotI1, plotI2,plotI3,plotI4,plotI5,plotI6,plotI7,plotI8,plotIg]
        plt.figure()
        ax1 = plt.axes(xlim=(0, 500), ylim=(0, 5e-6))
        lines = []
        for index in range(len(plot_ys)):
            string_current = 'I_{}'.format(index + 1)
            lnobj = ax1.plot([], [], label=string_current)[0]
            lines.append(lnobj)
        plt.xlabel('Time (s)')
        plt.ylabel('Current (A)')
        plt.legend()
        plt.ion()
        plt.show()
        while updateThread.is_alive():
            plt.pause(1)
            for num, line in enumerate(lines):
                line.set_data(timex, plot_ys[num])
            plt.draw()

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
            fLog.write('End of TimeSweeper: ' + str(datetime.now()) + '\n')
        ID.increaseID()

    def timeSweep(self): #Sweep with switching from odd to even each gate point
        global elapsed,I_1,I_2,I_3,I_4,I_5,I_6,I_7,I_8,I_g,nRun,nTime
        if Diags == "Verbose":
            print("Starting time sweep: ",nRun)
        ## Set to odd for start of switched Configuration
        CtrlPi.odd()
        B2201.odd()
        time.sleep(Settle)
        ## Initialise File Handling for time sweep
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write(
                'Measurement ' + measurementName + ' Sweep ' + str(nRun) + ' time' + ' started at: ' + str(datetime.now()) + '\n')
        with open(dataPath + '/' + t + '_' + measurementName + '_' + str(nRun) + '_time.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(
                ['t (s)', 'Is_1 (A)', 'Is_2 (A)', 'Is_3 (A)', 'Is_4 (A)', 'Is_5 (A)', 'Is_6 (A)', 'Is_7 (A)',
                 'Is_8 (A)', 'Ig (A)'])
        ##  Start the time sweep algorithm -- Turn into a proper function later 14SEP24 APM
        sweepStart = time.time()
        for i in range(nTime):
            if Diags == "Verbose":
                print("Time Iteration: ",i+1," Time: ",time.time())
            iterStart = time.time()
            elapsed.iat[i,0] = time.time()-sweepStart
            I_1.iat[i,0] = B1500.getI1()
            I_3.iat[i,0] = B1500.getI2()
            I_5.iat[i,0] = B1500.getI3()
            I_7.iat[i,0] = B1500.getI4()
            CtrlPi.even()
            B2201.even()
            time.sleep(Settle)
            I_2.iat[i,0] = B1500.getI1()
            I_4.iat[i,0] = B1500.getI2()
            I_6.iat[i,0] = B1500.getI3()
            I_8.iat[i,0] = B1500.getI4()
            I_g.iat[i,0] = K2401._getSenseLevel()
            CtrlPi.odd()
            B2201.odd()
            # Check for Stop signal
            with open('stop.txt', 'r') as fStop:
                r = fStop.read()
                if r == 'stop':
                    print('Stop button activated at iteration: ',i+1)
                    break
            # send data to file -- Might need to test file name stays open in this setup 14SEP24 APM
            with open(dataPath + '/' + t + '_' + measurementName + '_' + str(nRun) + '_time.csv', 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([str(elapsed.iat[i,0]),str(I_1.iat[i,0]),str(I_2.iat[i,0]),str(I_3.iat[i,0]),str(I_4.iat[i,0]),str(I_5.iat[i,0]),str(I_6.iat[i,0]),str(I_7.iat[i,0]),str(I_8.iat[i,0]),str(I_g.iat[i,0])])
            #Append readings for live graphing
            timex.append(elapsed.iat[i,0])
            plotI1.append(I_1.iat[i,0])
            plotI2.append(I_2.iat[i,0])
            plotI3.append(I_3.iat[i,0])
            plotI4.append(I_4.iat[i,0])
            plotI5.append(I_5.iat[i,0])
            plotI6.append(I_6.iat[i,0])
            plotI7.append(I_7.iat[i,0])
            plotI8.append(I_8.iat[i,0])
            plotIg.append(I_g.iat[i,0])
            time.sleep(SampleWait - (time.time() - iterStart))
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('Measurement ' + measurementName + ' Sweep ' + str(nRun) + ' time' + ' finished at: ' + str(datetime.now()) + '\n')
        print("End sweep: ",nRun)
        nRun += 1
        TimeSweeper.updateGUI()

if __name__ == "__main__":
    # GUI Code
    nRun=1
    TimeSweeper = TimeSweep()
    TimeSweeper.initialise()
    root = tk.Tk()
    root.title("Time Sweeper GUI")
    root.geometry('200x250')
    root.config(bg="purple")
    assay = tk.Label(root,text=('Assay Number: '+t+'_'+measurementName),bg="purple")
    assay.grid(row=0,column=0,padx=5,pady=5)
    run = tk.Label(root,text=('Sweep Number: '+str(nRun)),bg="purple")
    run.grid(row=1, column=0, padx=5, pady=5)
    time_button = tk.Button(root,text='Start time sweep',command=lambda:TimeSweeper.timeStart())
    time_button.grid(row=2, column=0, padx=5, pady=5)
    stop_button = tk.Button(root,text='Stop time sweep',command=lambda:TimeSweeper.stop())
    stop_button.grid(row=3, column=0, padx=5, pady=5)
    exit_button = tk.Button(root,text='End GateSweeper',command=lambda:[TimeSweeper.end(),root.quit()])
    exit_button.grid(row=6,column=0,padx=5,pady=5)
    root.mainloop()