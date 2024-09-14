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
import GlobalMeasID as ID
from Config import basePath,PiBox,B1500ADCSet,B1500NPLC,K2401compl
from Config import VgStart,VgStop,VgStep,Settle
from Config import VS_SMU1,VS_SMU2,VS_SMU3,VS_SMU4
from Config import B1500ICOM1,B1500ICOM2.B1500ICOM3,B1500ICOM4
from Config import B1500Filt1,B1500Filt2,B1500Filt3,B1500Filt4

class GateSweep(): # Setting up as a class for later scripting potential -- 10SEP24 APM
    def __init__(self):
        super(GateSweep, self).__init__()
        self.dev = GateSweep
        self.type = "GateSweep"  # We can check each instrument for its type and react accordingly

    def dataPathInit(self): # Initialise the folder where the data for this run will be stored
        global dataPath,measurementName,t
        measurementName = str(ID.readCurrentSetup()) + str(ID.readCurrentID())
        today = date.today()
        t = today.strftime("%y%m%d")
        dataPath = basePath + "/" + t + "_" + measurementName
        if not os.path.exists(dataPath):
            os.makedirs(dataPath)

    def logFileMaker(self): # Initialise the log file and enter the starting data
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'w') as fLog:
            fLog.write('Start of GateSweeper: ' + str(datetime.now()) + '\n' +
                       'Sweep Number: ' + measurementName + '\n' +
                       'Pi Box: ' + PiBox + '\n' +
                       'B1500 Mode: ' + str(B1500ADCSet) + '\n' +
                       'B1500 NPLC Setting: ' + str(B1500NPLC) + '\n' +
                       'B1500 SMU 1: V_S = ' + str(VS_SMU1) + ' V' + 'Compliance = ' + str(B1500ICOM1) + 'Filter = ' + str(B1500Filt1) + '\n' +
                       'B1500 SMU 2: V_S = ' + str(VS_SMU2) + ' V' + 'Compliance = ' + str(B1500ICOM2) + 'Filter = ' + str(B1500Filt2) + '\n' +
                       'B1500 SMU 3: V_S = ' + str(VS_SMU3) + ' V' + 'Compliance = ' + str(B1500ICOM3) + 'Filter = ' + str(B1500Filt3) + '\n' +
                       'B1500 SMU 4: V_S = ' + str(VS_SMU4) + ' V' + 'Compliance = ' + str(B1500ICOM4) + 'Filter = ' + str(B1500Filt4) + '\n' +
                       'K2401 Compliance: ' + str(K2401compl) + ' A' + '\n \n'
                       )

    def logFileCloser(self): # Initialise the log file and enter the starting data
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'w') as fLog:
            fLog.write('End of GateSweeper: ' + str(datetime.now()) + '\n')

    def stopFileInit(self): # Note for later, do we want a path to Desktop for this? -- 10SEP24 APM
        stopText = """If you want to stop the program, simply replace this text with 'stop' and save it."""  # Resets the code used to end a grab before quitting program
        with open('stop.txt', 'w') as fStop:  # Initialise stop button
            fStop.write(stopText)

    def stop(self): # Operates stop mechanism (may not need until GUI) -- 14SEP24 APM
        with open('stop.txt', 'w') as fStop:
            fStop.write('stop')

    def end(self): # Operates mechanism to end the program entirely -- 14SEP24 APM
        with open(dataPath + '/log_'+t+'_'+measurementName+'.txt', 'a') as fLog:
            fLog.write('End: ' + str(datetime.now()) + '\n')
        ID.increaseID()

    def measStartOdd(self): # File handling to kick off an odd measurement -- 14SEP24 APM
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('Measurement ' + measurementName + ' odd only forward ' + ' started at: ' + str(datetime.now()) + '\n')
        with open(dataPath + '/' + t + '_' + measurementName + '_odd_forward.csv', 'w', newline='') as fOddFor:
            writer = csv.writer(fOddFor)
            writer.writerow(['Vg (V)', 'Is_1 (A)', 'Is_3 (A)', 'Is_5 (A)', 'Is_7 (A)'])
        with open(dataPath + '/' + t + '_' + measurementName + '_odd_backward.csv', 'w', newline='') as fOddBack:
            writer = csv.writer(fOddBack)
            writer.writerow(['Vg (V)', 'Is_1 (A)', 'Is_3 (A)', 'Is_5 (A)', 'Is_7 (A)'])
        return fOddFor,fOddBack

    def measSwitchOdd(self): # File handling to kick off an odd measurement -- 14SEP24 APM
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('Measurement ' + measurementName + ' odd only backward ' + ' started at: ' + str(datetime.now()) + '\n')

    def measEndOdd(self): # File handling to end an odd measurement -- 14SEP24 APM
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('Measurement ' + measurementName + ' odd only ' + ' stopped at: ' + str(datetime.now()) + '\n')

    def measStartEven(self): # File handling to kick off an even measurement -- 14SEP24 APM
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('Measurement ' + measurementName + ' even only ' + ' started at: ' + str(datetime.now()) + '\n')
        with open(dataPath + '/' + t + '_' + measurementName + '_even.csv', 'w', newline='') as fEvenFor:
            writer = csv.writer(fEvenFor)
            writer.writerow(['Vg (V)', 'Is_2 (A)', 'Is_4 (A)', 'Is_6 (A)', 'Is_8 (A)'])
        with open(dataPath + '/' + t + '_' + measurementName + '_even.csv', 'w', newline='') as fEvenBack:
            writer = csv.writer(fEvenBack)
            writer.writerow(['Vg (V)', 'Is_2 (A)', 'Is_4 (A)', 'Is_6 (A)', 'Is_8 (A)'])
        return fEvenFor,fEvenBack

    def measSwitchEven(self): # File handling to kick off an even measurement -- 14SEP24 APM
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('Measurement ' + measurementName + ' odd only backward ' + ' started at: ' + str(datetime.now()) + '\n')

    def measEndEven(self): # File handling to end an even measurement -- 14SEP24 APM
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('Measurement ' + measurementName + ' even only ' + ' stopped at: ' + str(datetime.now()) + '\n')

    def measStartBoth(self): # File handling to kick off a switched odd/even measurement -- 14SEP24 APM
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('Measurement ' + measurementName + ' both ' + ' started at: ' + str(datetime.now()) + '\n')
        with open(dataPath + '/' + t + '_' + measurementName + '_both.csv', 'w', newline='') as fBothFor:
            writer = csv.writer(fBothFor)
            writer.writerow(['Vg (V)', 'Is_1 (A)', 'Is_2 (A)', 'Is_3 (A)', 'Is_4 (A)', 'Is_5 (A)', 'Is_6 (A)', 'Is_7 (A)', 'Is_8 (A)'])
        with open(dataPath + '/' + t + '_' + measurementName + '_both.csv', 'w', newline='') as fBothBack:
            writer = csv.writer(fBothBack)
            writer.writerow(['Vg (V)', 'Is_1 (A)', 'Is_2 (A)', 'Is_3 (A)', 'Is_4 (A)', 'Is_5 (A)', 'Is_6 (A)', 'Is_7 (A)', 'Is_8 (A)'])
        return fBothFor,fBothBack

    def measSwitchBoth(self): # File handling to kick off an odd measurement -- 14SEP24 APM
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('Measurement ' + measurementName + ' both backward ' + ' started at: ' + str(datetime.now()) + '\n')

    def measEndBoth(self): # File handling to end a switched odd/even measurement -- 14SEP24 APM
        with open(dataPath + '/log_' + t + '_' + measurementName + '.txt', 'a') as fLog:
            fLog.write('Measurement ' + measurementName + ' both ' + ' stopped at: ' + str(datetime.now()) + '\n')

    def array(self,start,target,stepsize):
        """Helper function that creates single 1D array from start to stop. Used in targetArray()"""
        sign = 1 if (target>start) else -1
        sweepArray = np.arange(start,np.round(target+sign*stepsize,decimals=5),sign*stepsize) #The rounding makes function more predictable
        return sweepArray

## Main Routine Below

if __name__ == "__main__":
        ## Initialise this class for use
        GateSweeper = GateSweep()
        ## Initialise Pi Connection
        CtrlPi = PiMUX()
        ## Initialise B1500 -- Semiconductor Parameter Analyser
        B1500 = B1500()
        B1500.init()
        ## Initialise B2201
        B2201 = B2201()
        B2201.init()
        ## Initialise K2401
        K2401 = K2401(24)
        K2401.setOptions({"beepEnable": False,"sourceMode": "voltage","sourceRange":K2401sourceRange,"senseRange": K2401senseRange,"compliance": K2401compl,"scaleFactor":1})
        ## Build arrays of gate voltage values for forward and backward sweeps
        VgForward = GateSweeper.array(VgStart,VgStop,VgStep)
        VgBackward = GateSweeper.array(VgStop,VgStart,VgStep)
        ## Set B1500 source values
        B1500.smu1.voltage(VS_SMU1)
        B1500.smu2.voltage(VS_SMU2)
        B1500.smu3.voltage(VS_SMU3)
        B1500.smu4.voltage(VS_SMU4)
        ## Set K2401 starting gate voltage
        K2401._setSourceLevel(VgStart)

        ## Set Odd Configuration
        CtrlPi.odd()
        B2201.odd()
        ## Initialise File Handling for odd sweep
        fOddFor,fOddBack = GateSweeper.measStartOdd()
        ##  Start the odd sweep algorithm -- Turn into a proper function later 14SEP24 APM
        for i in range(VgForward):
            K2401._setSourceLevel(VgForward[i])
            time.sleep(Settle)
            I_1[i] = B1500.smu1.current()
            I_3[i] = B1500.smu2.current()
            I_5[i] = B1500.smu3.current()
            I_7[i] = B1500.smu4.current()
            # send data to file -- Might need to test file name stays open in this setup 14SEP24 APM
            writer = csv.writer(fOddFor)
            writer.writerow([str(VgForward[i]), str(I_1[i]), str(I_3[i]),str(I_5[i]), str(I_7[i])])
        GateSweeper.measSwitchOdd()
        for i in range(VgBackward):
            K2401._setSourceLevel(VgBackward[i])
            time.sleep(Settle)
            I_1[i] = B1500.smu1.current()
            I_3[i] = B1500.smu2.current()
            I_5[i] = B1500.smu3.current()
            I_7[i] = B1500.smu4.current()
            # send data to file -- Might need to test file name stays open in this setup 14SEP24 APM
            writer = csv.writer(fOddBack)
            writer.writerow([str(VgBackward[i]), str(I_1[i]), str(I_3[i]),str(I_5[i]), str(I_7[i])])
        GateSweeper.measEndOdd()

        ## Set Even Configuration
        CtrlPi.even()
        B2201.even()
        ## Initialise File Handling for even sweep
        fEvenFor, fEvenBack = GateSweeper.measStartEven()
        ##  Start the even sweep algorithm -- Turn into a proper function later 14SEP24 APM
        for i in range(VgForward):
            K2401._setSourceLevel(VgForward[i])
            time.sleep(Settle)
            I_2[i] = B1500.smu1.current()
            I_4[i] = B1500.smu2.current()
            I_6[i] = B1500.smu3.current()
            I_8[i] = B1500.smu4.current()
            # send data to file -- Might need to test file name stays open in this setup 14SEP24 APM
            writer = csv.writer(fEvenFor)
            writer.writerow([str(VgForward[i]), str(I_2[i]), str(I_4[i]), str(I_6[i]), str(I_8[i])])
        GateSweeper.measSwitchEven()
        for i in range(VgBackward):
            K2401._setSourceLevel(VgBackward[i])
            time.sleep(Settle)
            I_2[i] = B1500.smu1.current()
            I_4[i] = B1500.smu2.current()
            I_6[i] = B1500.smu3.current()
            I_8[i] = B1500.smu4.current()
            # send data to file -- Might need to test file name stays open in this setup 14SEP24 APM
            writer = csv.writer(fEvenBack)
            writer.writerow([str(VgBackward[i]), str(I_2[i]), str(I_4[i]), str(I_6[i]), str(I_8[i])])
        GateSweeper.measEndEven()

        ## Set to odd for start of switched Configuration
        CtrlPi.odd()
        B2201.odd()
        ## Initialise File Handling for even sweep
        fBothFor, fBothBack = GateSweeper.measStartBoth()
        ##  Start the switched sweep algorithm -- Turn into a proper function later 14SEP24 APM
        for i in range(VgForward):
            K2401._setSourceLevel(VgForward[i])
            time.sleep(Settle)
            I_1[i] = B1500.smu1.current()
            I_3[i] = B1500.smu2.current()
            I_5[i] = B1500.smu3.current()
            I_7[i] = B1500.smu4.current()
            CtrlPi.even()
            B2201.even()
            time.sleep(Settle)
            I_2[i] = B1500.smu1.current()
            I_4[i] = B1500.smu2.current()
            I_6[i] = B1500.smu3.current()
            I_8[i] = B1500.smu4.current()
            CtrlPi.odd()
            B2201.odd()
            # send data to file -- Might need to test file name stays open in this setup 14SEP24 APM
            writer = csv.writer(fBothFor)
            writer.writerow([str(VgForward[i]),str(I_1[i]),str(I_2[i]),str(I_3[i]),str(I_4[i]),str(I_5[i]),str(I_6[i]),str(I_7[i]),str(I_8[i])])
        GateSweeper.measSwitchBoth()
        for i in range(VgBackward):
            K2401._setSourceLevel(VgBackward[i])
            time.sleep(Settle)
            I_1[i] = B1500.smu1.current()
            I_3[i] = B1500.smu2.current()
            I_5[i] = B1500.smu3.current()
            I_7[i] = B1500.smu4.current()
            CtrlPi.even()
            B2201.even()
            time.sleep(Settle)
            I_2[i] = B1500.smu1.current()
            I_4[i] = B1500.smu2.current()
            I_6[i] = B1500.smu3.current()
            I_8[i] = B1500.smu4.current()
            CtrlPi.odd()
            B2201.odd()
            # send data to file -- Might need to test file name stays open in this setup 14SEP24 APM
            writer = csv.writer(fBothBack)
            writer.writerow([str(VgBackward[i]),str(I_1[i]),str(I_2[i]),str(I_3[i]),str(I_4[i]),str(I_5[i]),str(I_6[i]),str(I_7[i]),str(I_8[i])])
        GateSweeper.measEndBoth()

        ## Finalise by returning the system to a stable state between measurements
        B1500.smu1.voltage(0.0)
        B1500.smu2.voltage(0.0)
        B1500.smu3.voltage(0.0)
        B1500.smu4.voltage(0.0)
        K2401._setSourceLevel(0.0)
        B2201.clear()
        GateSweeper.logFileCloser()