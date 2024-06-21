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

mpl.rcParams['axes.linewidth'] = 1.5    # Makes boxplot linewidth larger
mpl.rcParams.update({'font.size': 12})  # Increases fontsize

import warnings #used to suppress the annoying matplotlib warning about singular axes
warnings.filterwarnings("ignore", category = UserWarning) #used to suppress the annoying matplotlib warning about singular axes. # APM removed module specificity to make this work correctly in Py3.

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

# For each input point:
# 1. Sets the instruments to the input point by calling the inputSetters with the point
# 2. Calls each outputReaders to get the output point
# 3. Calls outputReceiver with the point
# After all input points have been processed, outputFinisher is called
def sweep(inputPoints, inputSetters, outputReaders, outputReceiver,delay,breakCondition):
    APSIndex= 0
    for setters in flatten([outputReaders]):
        if setters.type == 'APS100':
            sweepDirection = setters.get('sweepDirection')
            sweepLimits = setters.get('limits')
            break
        else:
            APSIndex = APSIndex+1
        
    print(('APS Index: '+str(APSIndex)))
    print(('Performing an '+sweepDirection+' sweep'))
    print(('sweep Limits are: '+str(sweepLimits[0])+ ' and '+str(sweepLimits[1])))
    epsilon = 0.0005
    prevPoint = None
    counter = 0
#    running = True
#    if breakCondition ==None:
#        breakCondition = [outputReaders[0],-float("inf"),float("inf")]
#    print breakCondition

    for inputPoint in inputPoints:
#            while(running):
                if len(inputPoint) != len(inputSetters):
                    raise ValueError("Length of input point does not match length of input setters")
                if prevPoint == None:
                    prevPoint = [None] * len(inputPoint)
                    for value,setter in zip(inputPoint,inputSetters):                        
                        setter.goTo(value)
                for value, prevValue, setter in zip(inputPoint, prevPoint, inputSetters):
                    # Avoid setting a value if it is already set to it
                    if value != prevValue:
                        if callable(setter):
                            setter(value)
                        else:
                            setter.set(type(setter).defaultOutput, value)

                prevPoint = inputPoint
        
                time.sleep(delay)
                outputPoint = []
                for reader in outputReaders:
                    if callable(reader):
                        tempRes = reader()
#                        print(tempRes)
                        outputPoint.append(tempRes)
#                        print(running)
    
                    else:
                        tempRes = reader.get(type(reader).defaultInput)
                        outputPoint.append(tempRes)
#                        print(tempRes)
#                        if (reader == breakCondition[0] and (breakCondition[2] < tempRes[0] or breakCondition[1] > tempRes[0])):
#                            running = False
#                            print(reader)
#                            print(breakCondition[0])
#                            print("we just hit the condition")
#                            break
#                        print(running)
#                print(flatten(inputPoint))
#                print(flatten(outputPoint))
#                print("\n")
                outputReceiver(inputPoint, outputPoint,counter)
#               print(flatten(outputPoint))
                if(sweepDirection =='up' and abs(flatten(outputPoint)[APSIndex]-sweepLimits[1]*0.1)<=epsilon):
#                   print('We hit the condition for an upsweep')
                    outputReceiver(inputPoint, outputPoint,counter=20)
                    break
                elif(sweepDirection =='down' and abs(flatten(outputPoint)[APSIndex]-sweepLimits[0]*0.1)<=epsilon):
#                   print('hit the down condition')
                    outputReceiver(inputPoint, outputPoint,counter=20)
                    break
                else:
                    outputReceiver(inputPoint, outputPoint,counter)
                    
                counter = counter+1
def sweepNoSave(inputPoints, inputSetters, outputReaders,delay,breakCondition):
    prevPoint = None
    for inputPoint in inputPoints:
        if len(inputPoint) != len(inputSetters):
            raise ValueError("Length of input point does not match length of input setters")

        if prevPoint == None:
            prevPoint = [None] * len(inputPoint)

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

        # TODO: Possibly add configurable delay value here as well?

# Same options as sweep(), except we have some extra ones now:
#  - filename: The "base" filename to save the data to
#  - inputHeaders: What to call each input point in the saved data
#  - outputHeaders: What to call each output point in the saved data
#  - extraInstruments: Any other instruments that you want their config to be
#                      saved automatically that wasn't specified directly in
#                      inputSetters or outputReaders (e.g., you had a lambda as
#                      one of them)
def sweepMagnet(filename, inputHeaders, inputPoints, inputSetters,
                 outputHeaders, outputReaders, outputReceiver = None,
                 extraInstruments = [],saveEnable = True,delay = 0.0,breakCondition = None,plotParams = None,email = None,comments = ""):
    
    Xvalues1 = [];Yvalues1 = [];Xvalues2 = [];Yvalues2 = []
    
    #Turn input array into itertools.product if it isnt already:
    if (type(inputPoints) == product):
        print('I')
        pass
    elif (type(inputPoints) == list or type(inputPoints) == np.ndarray):
        
        print('II')
        inputPoints = product(inputPoints)
    else:
        pass
    
    #Check if the plotting parameters exist in in and outputHEaders:
    checkPlotHeaders(inputHeaders,outputHeaders,plotParams)   
    
    if(saveEnable):
        ID.increaseID()
        filename = filename + "_"+str(ID.readCurrentSetup()) + str(ID.readCurrentID())        
        startTime = time.time()
        # Make a copy of the initial configuration of the instruments
        instruments = set([i for i in inputSetters + outputReaders + extraInstruments if issubclass(type(i), Instrument.Instrument)])
        config = {}
        for instrument in instruments:
            config["{}-{}".format(type(instrument).__name__, len(config) + 1)] = instrument.getOptions()
    
        #  write the initial config:
        
        log = open(filename +"_LOG"+ ".tsv", "w")
        log.write("Measurement Log file for measurement >>> "+ str(ID.readCurrentSetup()) + str(ID.readCurrentID())+" <<< \n")
        log.write("Starting time and date: "+time.asctime(time.localtime(time.time()))+"\n")
        log.write("\n")
        log.write("Comments: "+str(comments) +"\n")
        log.write("=====================\n")
        log.write("Delay = "+str(delay)+"s \n")
        log.write("Initial configuration\n")
        log.write("=====================\n")
        log.write(json.dumps(config, indent = 4, sort_keys = True))
        log.write("\n=====================\n")
        log.close()
                
        #Write data file:
        tsv = open(filename + ".tsv", "w")
        tsv.write("\n=====================\n")
        tsv.write("\t".join(flatten(inputHeaders))+ "\t")
        tsv.write("\t".join(flatten(outputHeaders)) + "\n")
        
        # Prepare a dict for the data too
        pointsDict = {}
        for header in flatten((flatten(inputHeaders), flatten(outputHeaders))):
            pointsDict[header] = []
        
        #Prepare Plotting:
        a = ''.join(filename).rfind("/")  #a is just a helper variable to find the mesurement name from the full file path.
        measurementName = filename[a+1:]
        inputHeaders = flatten(inputHeaders);outputHeaders = flatten(outputHeaders);
#        Yindex = [];Xindex = [];
        allHeaders = inputHeaders + outputHeaders
        if plotParams != None and len(plotParams) ==2: 
            allHeaders = inputHeaders + outputHeaders 
            Xindex1 =  allHeaders.index(plotParams[0])
            Yindex1  = allHeaders.index(plotParams[1])
            
#            if Yindex1 >= len(flatten(inputHeaders)):
#                Yindex.append(1);
#                Yindex.append(Yindex1-len(inputHeaders))
#            else:
#                Yindex.append(0);
#                Yindex.append(Yindex1)
#                
#            if Xindex1 >= len(flatten(inputHeaders)):
#                Xindex.append(1);
#                Xindex.append(Xindex1-len(inputHeaders))
#            else:
#                Xindex.append(0);
#                Xindex.append(Xindex1)
#            print(Xindex)
#            print(Yindex)
#            Xindex1 = flatten(inputHeaders).index(plotParams[0]) #old
#            Yindex1 = flatten(outputHeaders).index(plotParams[1]) #old
            
            mainFig = plt.figure(figsize=(8,8))
            ax1 = mainFig.add_subplot(111)
            line1, = ax1.plot(0,0,'r')
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
        
        def receiver(inputPoint, outputPoint,counter):
            #print "Got input {} and output {}".format(inputPoint, outputPoint)
            checkPointMatchesHeaders(inputPoint, inputHeaders)
            checkPointMatchesHeaders(outputPoint, outputHeaders)
        
            for value, header in zip(flatten(inputPoint), flatten(inputHeaders)):
                pointsDict[header].append(value)
            for value, header in zip(flatten(outputPoint), flatten(outputHeaders)):
                pointsDict[header].append(value)
                
            tsv.write("\t".join(map(str, flatten(inputPoint))) + "\t") #takes the input points, 'flattens' the list (aka gets rid of unecessary lists in lists) turns them into strings and writes them separated by a tab \t in the tsv file.
            tsv.write("\t".join(map(str, flatten(outputPoint))) + "\n")
            
            #these force saving commands should probably only be executed every tenth iteration or so to speed things up.
            if counter%20==0:
                tsv.flush()   #These three commands force the tsv file and .mat file to be saved to disk. Otherwise the file will be lost when killing the program
                os.fsync(tsv.fileno())
                sio.savemat(filename, pointsDict)
                       
            #Do the actual Plotting:
            if plotParams != None and len(plotParams) ==2:
                points = flatten(inputPoint)+flatten(outputPoint)
                Xvalues1.append(points[Xindex1])
                Yvalues1.append(points[Yindex1])
                line1.set_ydata(Yvalues1)
                line1.set_xdata(Xvalues1)
                mainFig.canvas.draw()
                mainFig.canvas.flush_events()
#                if counter%3 ==0:
                try: #Introduced this since sometimes 'NaNs' or other chunk data may impede setting the axis limits properly
                    ax1.set_xlim(min(Xvalues1),max(Xvalues1))
                    ax1.set_ylim(min(Yvalues1),max(Yvalues1))
                except:
                    pass
                                       
            if plotParams != None and len(plotParams) ==4:
                points = flatten(inputPoint)+flatten(outputPoint)                
                Xvalues1.append(points[Xindex1])
                Yvalues1.append(points[Yindex1])
                Xvalues2.append(points[Xindex2])
                Yvalues2.append(points[Yindex2])
                line1.set_ydata(Yvalues1)
                line1.set_xdata(Xvalues1)
                line2.set_ydata(Yvalues2)
                line2.set_xdata(Xvalues2)

                #for counter%==3:
                try: #Introduced this since sometimes 'NaNs' or other chunk data may impede setting the axis limits properly
                    ax1.set_xlim(min(Xvalues1),max(Xvalues1))
                    ax1.set_ylim(min(Yvalues1),max(Yvalues1))
                    ax2.set_xlim(min(Xvalues2),max(Xvalues2))
                    ax2.set_ylim(min(Yvalues2),max(Yvalues2))                   
                except:
                    pass
                mainFig.canvas.draw()
                mainFig.canvas.flush_events()
                        
            if outputReceiver: #we dont really use that ever
                outputReceiver(inputPoint, outputPoint)
                       
        sweep(inputPoints, inputSetters, outputReaders, receiver,delay,breakCondition) #This does the actual sweep !
                
        tsv.close()
        log = open(filename +"_LOG"+ ".tsv", "a")
        log.write("Ending time and date: "+time.asctime(time.localtime(time.time()))+"\n")
        log.write("Time elapsed: "+str(time.time()-startTime)+" seconds." +"\n")
        log.write("Final configuration: \n")
        log.write("=====================\n")
        log.write(json.dumps(config, indent = 4, sort_keys = True))
        log.write("\n=====================\n")
        log.close()
        sio.savemat(filename, pointsDict)
        
    elif(not saveEnable):       
        sweepNoSave(inputPoints, inputSetters, outputReaders,delay,breakCondition) #This does the actual sweep (without saving)!
    if email != None:
        sendEmail(email,measurementName) 
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