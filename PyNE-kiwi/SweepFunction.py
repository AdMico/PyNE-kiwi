"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Jakob Seidl
"""

from collections import Iterable
import json
import GlobalMeasID as ID
import Instrument
import numpy as np
import scipy.io as sio
import time
import os
from itertools import product
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick #to enable Line 125 option for forcing y-axis to scientific notation.

#mpl.use('TkAgg') #Deactivated for V3.1 by APM due to conflicts -- 10Oct19
#mpl.rcParams['axes.linewidth'] = 1.5    # Makes boxplot linewidth larger #Deactivated for V3.1 by APM due to conflicts -- 10Oct19
#mpl.rcParams.update({'font.size': 12})  # Increases fontsize #Deactivated for V3.1 by APM due to conflicts -- 10Oct19

import warnings #used to suppress the annoying matplotlib warning about singular axes
warnings.filterwarnings("ignore", category = UserWarning) #used to suppress the annoying matplotlib warning about singular axes. # APM removed module specificity to make this work correctly in Py3.

# For each input point:
# 1. Sets the instruments to the input point by calling the inputSetters with the point
# 2. Calls each outputReaders to get the output point
# 3. Calls outputReceiver with the point
# After all input points have been processed, outputFinisher is called

# TODO: Possibly add configurable delay value here as well?

# Same options as sweep(), except we have some extra ones now:
#  - filename: The "base" filename to save the data to
#  - inputHeaders: What to call each input point in the saved data
#  - outputHeaders: What to call each output point in the saved data
#  - extraInstruments: Any other instruments that you want their config to be
#                      saved automatically that wasn't specified directly in
#                      inputSetters or outputReaders (e.g., you had a lambda as
#                      one of them)

def sweepAndSave(filename, inputHeaders, inputPoints, inputSetters,
                 outputHeaders, outputReaders, outputReceiver = None,
                 extraInstruments = [],
                 saveEnable = True,delay = 0.0,breakCondition = None,
                 plotParams = None,email = None,comments = "No comments provided by user"):
    
    """sweepAndSave is the main function of this module and THE sweepfunction. It is the only function that the user actually calls themselves in a control program 
    - all other functions provided here are called 'under the hood' by sweepAndSave. It can be subdivided into three parts:
    (1): Initialize: Check if user input is valid, create data and log files on disk and set up the plot object. All this is done ONCE ONLY.
    (2): sweep() function which calls receiver() within: LOOP Section: This is the actual sweep,
    i.e., iterative process carried out over every single datapoint in the inputArray. This is: (I) Query all meas instruments,
    (II) append data to files and plots and (III) every N-th iteration (default = 10), force the file to be written on disk.
    (3): Wrap-up: Write the final instrument parameters and data to file, save the plot as .png, close all file connections (good practice!)"""
    
    ######################################################################## Part(1) -- the opening  ########################################################################
    #########################################################################################################################################################
    #Turn input array into itertools.product if it isnt already. Since our sweepArray is usually a 1D array anyway, this is usually not necessary and is more of a relic than a feature:
    if (type(inputPoints) == product):
        pass
    elif (type(inputPoints) == list or type(inputPoints) == np.ndarray):    
        inputPoints = product(inputPoints)
    else:
        pass
    
    #Check if the plotting parameters ('plotParams') exist in inputHeaders and outputHeaders:
    checkPlotHeaders(inputHeaders,outputHeaders,plotParams)   
    
    if(saveEnable):
        ID.increaseID()
        filename = filename + "_"+str(ID.readCurrentSetup()) + str(ID.readCurrentID())        
        startTime = time.time() # Start time
        # Make a copy of the initial configuration of the instruments
        instruments = set([i for i in inputSetters + outputReaders + extraInstruments if issubclass(type(i), Instrument.Instrument)])
        
        config = {}
        for instrument in instruments: #This goes through the list of all instruments and queries all options that have a associated 'get()' method. E.g., 'sourceMode' for the Keithley2401
            config["{}-{}".format(type(instrument).__name__, len(config) + 1)] = instrument.getOptions() #Prev Version
            #config["{}-{}-{}".format(instrument.get('name'),type(instrument).__name__,len(config)+1)] = instrument.getOptions() #The ['key'] for each instrument is its 'name' and its type.
            
        #  write the initial config to the LOG file:
        log = open(filename +"_LOG"+ ".tsv", "w")
        log.write("Measurement log file for measurement >>> "+ str(ID.readCurrentSetup()) + str(ID.readCurrentID())+" <<< \n")
        log.write("Starting time and date: "+time.asctime(time.localtime(time.time()))+"\n")
        log.write("\n")
        log.write("Comments: "+str(comments) +"\n")
        log.write("=====================\n")
        log.write("Delay = "+str(delay)+"s \n")
        log.write("Initial configuration\n")
        log.write("=====================\n")
        log.write(json.dumps(config, indent = 4, sort_keys = True)) #Writes all initial instrument paramters in intended Json format
        log.write("\n=====================\n")
        log.close()
                
        #Write data headers to plain text file :
        tsv = open(filename + ".tsv", "w")
        tsv.write("\n=====================\n")
        tsv.write("\t".join(flatten(inputHeaders))+ "\t")
        tsv.write("\t".join(flatten(outputHeaders)) + "\n")
        
        # Prepare a dict for the data too. This dict will be used to write data to a .mat file which can be conveniently read by Matlab or Python
        pointsDict = {}
        for header in flatten((flatten(inputHeaders), flatten(outputHeaders))):
            pointsDict[header] = []
        
        ##############  Prepare Plotting: ###############
        a = ''.join(filename).rfind("/")  #a is just a helper variable to find the measurement name from the full file path.
        measurementName = filename[a+1:]
        inputHeaders = flatten(inputHeaders);outputHeaders = flatten(outputHeaders); #Make sure we have simple lists, not lists within lists etc..
#        Yindex = [];Xindex = [];
        allHeaders = inputHeaders + outputHeaders
        Xvalues1 = [];Yvalues1 = [];Xvalues2 = [];Yvalues2 = [] #Generate empty lists of X and Y Data. This is used later in the plotting routine.

        ############## Initialize the plot. Actual plotting happens within receiver() within save() ###############
        if plotParams != None and len(plotParams) ==2: 
            allHeaders = inputHeaders + outputHeaders 
            Xindex1 =  allHeaders.index(plotParams[0])
            Yindex1  = allHeaders.index(plotParams[1])
            mainFig = plt.figure(figsize=(8,8))
            ax1 = mainFig.add_subplot(111)
            line1, = ax1.plot(0,0,'r')
            ax1.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2e')) #Added APM 22/10/19 to enable force axes to number format.
            plt.ylabel(str(allHeaders[Yindex1]))
            plt.xlabel(str(allHeaders[Xindex1]))
            plt.title(measurementName)
            plt.show()
            
        if plotParams != None and len(plotParams) ==4:
            Xindex1 = allHeaders.index(plotParams[0])
            Yindex1 = allHeaders.index(plotParams[1])
            Xindex2 = allHeaders.index(plotParams[2])
            Yindex2 = allHeaders.index(plotParams[3])
            mainFig = plt.figure(figsize=(10,8))
            ax1 = mainFig.add_subplot(211)
            plt.ylabel(str(allHeaders[Yindex1]))
            plt.xlabel(str(allHeaders[Xindex1]))
            line1, = ax1.plot(0,0,'r')
            plt.title(measurementName)
            ax2 = mainFig.add_subplot(212)
            plt.ylabel(str(allHeaders[Yindex2]))
            plt.xlabel(str(allHeaders[Xindex2]))
            line2, = ax2.plot(0,0,'b')
            plt.show()
            
        ############### END initialize plot ###############################
        
        ######################################################################## Part(2) --The loop-- ########################################################################
        #########################################################################################################################################################
        
        ########  The receiver() function is a sub-section of the save() function and is called for EACH point in the sweepArray.
        #It does two things: 1) Append the set of measured values (e.g. results from you SRS830 and K2401) to your measurement text file (.tsv) 
        #and appends it to your python dictionary of results (used for export as .mat file in the end). 2) It updates the current plot with the new data. 
        
        ##############  Definition of receiver() ###############################
        def receiver(inputPoint,outputPoint,counter):
            #print "Got input {} and output {}".format(inputPoint, outputPoint)
            checkPointMatchesHeaders(inputPoint,inputHeaders)
            checkPointMatchesHeaders(outputPoint,outputHeaders)
        
            for value, header in zip(flatten(inputPoint), flatten(inputHeaders)):
                pointsDict[header].append(value)
            for value, header in zip(flatten(outputPoint), flatten(outputHeaders)):
                pointsDict[header].append(value)
                
            tsv.write("\t".join(map(str, flatten(inputPoint))) + "\t") #takes the input points, 'flattens' the list (aka gets rid of unecessary lists in lists) turns them into strings and writes them separated by a tab \t in the tsv file.
            tsv.write("\t".join(map(str, flatten(outputPoint))) + "\n")
            
            #these force saving commands should probably only be executed every tenth iteration or so to speed things up.
            if counter%10==0:
                tsv.flush()   #These three commands force the tsv file and .mat file to be saved to disk. Otherwise the data will be lost when killing the program.
                os.fsync(tsv.fileno())
                sio.savemat(filename, pointsDict)
            
            #Do the actual plotting:
            if plotParams != None and len(plotParams) ==2: # If the user specified ONE PAIR of variables they want plotted, update those.
                points = flatten(inputPoint)+flatten(outputPoint)
                Xvalues1.append(points[Xindex1])
                Yvalues1.append(points[Yindex1])
                line1.set_ydata(Yvalues1)
                line1.set_xdata(Xvalues1)                

                mainFig.canvas.draw()
                mainFig.canvas.flush_events()
                try: #Introduced this since sometimes 'NaNs' or other chunk data may impede setting the axis limits properly
                    ax1.set_xlim(min(Xvalues1),max(Xvalues1))
                    ax1.set_ylim(min(Yvalues1),max(Yvalues1))
                except:
                    pass                         
                
            if plotParams != None and len(plotParams) ==4: # If the user specified TWO PAIRS of variables they want plotted, update those.
                points = flatten(inputPoint)+flatten(outputPoint)                
                Xvalues1.append(points[Xindex1])
                Yvalues1.append(points[Yindex1])
                Xvalues2.append(points[Xindex2])
                Yvalues2.append(points[Yindex2])           
                
                line1.set_ydata(Yvalues1)
                line1.set_xdata(Xvalues1)
                line2.set_ydata(Yvalues2)
                line2.set_xdata(Xvalues2)

                try: #Introduced this since sometimes 'NaNs' or other bad data may impede setting the axis limits properly
                    ax1.set_xlim(min(Xvalues1),max(Xvalues1))
                    ax1.set_ylim(min(Yvalues1),max(Yvalues1))
                    ax2.set_xlim(min(Xvalues2),max(Xvalues2))
                    ax2.set_ylim(min(Yvalues2),max(Yvalues2))                   
                except:
                    pass
                mainFig.canvas.draw() #Those two commands force the plot to actually update
                mainFig.canvas.flush_events()
                ############## END Definition of receiver() ###############################
            
            #if outputReceiver: #we dont really use that ever, ignore. This is a potential future interface if the user wants to do more with their data for each iteration
            #    outputReceiver(inputPoint, outputPoint)
            ##############  END Definition of receiver() ###############################   
        
        #sweep() does the actual sweep and calls receiver() defined just above! sweep() is defined just below, outside of the sweepAndSave() definition 
        sweep(inputPoints,inputSetters,outputReaders,receiver,delay,breakCondition) 
        
        ######################################################################## Part(3) -- The closing ########################################################################
        #########################################################################################################################################################
        ###### Wrapping up the measurement: close the data.tsv file, write the final settings of all instruments in .log file,
        #save a final version of the data to .mat format and save the figure created as .png
        tsv.close()
        log = open(filename +"_LOG"+ ".tsv", "a")
        log.write("Ending time and date: "+time.asctime(time.localtime(time.time()))+"\n")
        log.write("Time elapsed: "+str(time.time()-startTime)+" seconds." +"\n")
        log.write("Final configuration: \n")
        log.write("=====================\n")
        log.write(json.dumps(config, indent = 4, sort_keys = True)) #Writes all the instrument parameters in indented json format
        log.write("\n=====================\n")
        log.close()
        sio.savemat(filename, pointsDict)
        
        plt.savefig(filename+'.png') #Save Plot as .png as additional feature
        
        plt.close() #Line added to avoid Figures from hanging in Py3.
    
    elif(not saveEnable): #This elif branch is basically never executed and can be ignored. We just assume that the user wants to save and plot their data anyway.     
        sweepNoSave(inputPoints, inputSetters, outputReaders,delay,breakCondition) #This does the actual sweep (without saving)!
    
    if email != None: #This allows to send an email to the user after completig a measurement. I've defined sendEmail below. Is only called if the user specifies an address.
        sendEmail(email,measurementName) 
######################################################################## END of sweepAndSave() ########################################################################
#######################################################################################################################################################################

def sweep(inputPoints,inputSetters,outputReaders,receiver,delay,breakCondition):
    """sweep() defines the 'actual sweep',i.e.,, we define what is done for each 'inputPoint' of the array we want to sweep over. """
    prevPoint = None
    counter = 0
#    running = True
#    if breakCondition ==None:
#        breakCondition = [outputReaders[0],-float("inf"),float("inf")]
#    print breakCondition

    # Actual loop over all points in inputArray:
    for inputPoint in inputPoints:
#            while(running): #If we wanted something like a break condition, this would be the place to put them. Not yet implemented, though.
                if len(inputPoint) != len(inputSetters):#Usually len(inputPoint) is 1 since it's a single point in a 1D array. One instrument, one value.
                    raise ValueError("Length of input point does not match length of input setters")
                
                #We define the 'previous' state of the sweep so we are able to 
                if prevPoint == None: #For the first point of each sweep, this is the case. The setter.goTo(target) then slowly goes to the first value. This is mainly to catch user errors.
                    prevPoint = [None] * len(inputPoint) #Usually len(inputPoint) is 1 since it's a single point in a 1D array.
                    for value,setter in zip(inputPoint,inputSetters):                        
                        setter.goTo(value)
                #A Set source instrument        
                for value, prevValue, setter in zip(inputPoint, prevPoint, inputSetters):
                    # Avoid setting a value if it is already set to it
                    if value != prevValue: #only change outputs if they are in fact different to the previous once. Saves time.
                        if callable(setter):# In principle one could directly pass a (lambda) function instead of a real instrument. Then this block is carried out.
                            setter(value)
                        else:
                            setter.set(type(setter).defaultOutput, value)

                prevPoint = inputPoint
                #### B Reading out all instruments defined as 'outputReaders'
                time.sleep(delay) #This is the delay specified by the user, typically 0.2s
                outputPoint = []
                for reader in outputReaders:
                    if callable(reader): # In principle one could directly pass a (lambda) function instead of a real instrument. Then this block is carried out.
                        tempRes = reader()
#                        print(tempRes)
                        outputPoint.append(tempRes)
#                        print(running)    
                    else: #However, usually we provide a 'real' instrument object and the appropriate instrument.get('readVariable') is called.
                        tempRes = reader.get(type(reader).defaultInput)
                        outputPoint.append(tempRes)
                    
                # Block below calls the receiver. In the sweepAndSave function, we define a receiver which we then hand over to the save() function called there.
                # So in normal use, this is used to plot and write the data to file. However, in principle you could pass ANY function to it and you could do other stuff with your data.
                receiver(inputPoint,outputPoint,counter) 
                counter = counter + 1

#################################### From here on unimportant and helper functions ################
###################################################################################################
def sweepNoSave(inputPoints, inputSetters, outputReaders,delay,breakCondition): #Since by default the 'saveEnable' option is True, this funciton is barely ever called.
    prevPoint = None
    for inputPoint in inputPoints:
        if len(inputPoint) != len(inputSetters):
            raise ValueError("Length of input point does not match length of input setters")

        #We define the 'previous' state of the sweep so we are able to only change outputs if they are in fact different to the previous once. Saves time.
        if prevPoint == None: #For the first point of each sweep, this is the case.
            prevPoint = [None] * len(inputPoint) #Usually len(inputPoint) is 1 since it's a single point in a 1D array. 

        for value, prevValue, setter in zip(inputPoint, prevPoint, inputSetters):
            # Avoid setting a value if it is already set to it
            if value != prevValue:
                if callable(setter):
                    setter(value)
                else:
                    setter.set(type(setter).defaultOutput, value)
        prevPoint = inputPoint

        # TODO: Possibly add configurable delay value here?
        time.sleep(delay)
        outputPoint = []
        for reader in outputReaders:
            if callable(reader):
                outputPoint.append(reader())
            else:
                outputPoint.append(reader.get(type(reader).defaultInput))

#Helper functions from here on:
    
# Checks if val is iterable, but not a string
def isIterable(val):
    return isinstance(val, Iterable) and not isinstance(val, str)

# Flattens a list: [[1, 2, 3], 4, [5], [6, 7]] => [1, 2, 3, 4, 5, 6, 7]
def flatten(iterable):
    flattenedList = []
    for e1 in iterable:
        if isIterable(e1):
            for e2 in e1:
                flattenedList.append(e2)
        else:
            flattenedList.append(e1)
    return flattenedList

def checkPointMatchesHeaders(point, headers): # I added heaps of flatten() in here in order to prevent weird errors where there shouldnt be any.
    if len(flatten(point)) != len(flatten(headers)): 
        raise ValueError("Point {} does not have same length as header {}".format(flatten(point), flatten(headers))) 

    for value, header in zip(flatten(point), flatten(headers)):
        if isIterable(header) and isIterable(value):
            if len(flatten(header)) != len(flatten(value)):  
                raise ValueError("Point {} does not have same length as header {}".format(flatten(point), flatten(headers)))
        elif not isIterable(header) and not isIterable(value):
            pass
        else:
            raise ValueError("Point {} does not have same length as header {}".format(flatten(point), flatten(headers)))

def checkPlotHeaders(inputHeaders,outputHeaders,plotParams):
    if plotParams == None:
        return
    if (len(plotParams) ==2 and plotParams[0] in (flatten(inputHeaders)+flatten(outputHeaders)) and plotParams[1] in (flatten(inputHeaders)+flatten(outputHeaders))):
        return 1
    elif (len(plotParams) ==4 and plotParams[0] in (flatten(inputHeaders)+flatten(outputHeaders)) and plotParams[1] in (flatten(inputHeaders)+flatten(outputHeaders)) and plotParams[2] in (flatten(inputHeaders)+flatten(outputHeaders)) and plotParams[3] in (flatten(inputHeaders)+flatten(outputHeaders))):
        return 2
    else:
        raise ValueError("{} does either not have the right format (either two or 4 parameters) or one of the given values is not found in input or output Headers".format(plotParams))
        
def sendEmail(targetAddress,measurementName):
    import smtplib
    sent_from = 'Christopher.PyNE@nanoelectronics.physics.unsw.edu.au'
    password = 'p00dles18'
    subject = 'Measurement finished'
    body = 'Eureka, your measurement >>>'+measurementName+'<<< has just finished!'
    email_text = """\  
    From: %s  
    To: %s  
    Subject: %s
    
    %s
    """ % (sent_from, targetAddress, subject, body)
    mail = smtplib.SMTP('smtp.gmail.com:587') #or 587
    mail.ehlo()
    mail.starttls()
    mail.login(sent_from,password)
    mail.sendmail(sent_from,targetAddress,email_text)
    print(('Email sent to: '+targetAddress))
    mail.close()