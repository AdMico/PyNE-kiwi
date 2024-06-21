"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Jakob Seidl
"""

import tkinter as tk
from tkinter.filedialog import asksaveasfilename, askdirectory
import json
import numpy as np
import matplotlib

#matplotlib.use('TkAgg') #Deactivated for V3.1 by APM due to conflicts -- 10Oct19
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #Deactivated for V3.1 by APM due to conflicts -- 10Oct19
from matplotlib.figure import Figure

def array(start,target,stepsize,upDown = False):
    
    sign = 1 if (target>start) else -1
    sweepArray = np.arange(start,target+sign*stepsize,sign*stepsize)
    if upDown:
        sweepArrayBack = np.arange(target,start+-sign*stepsize,-sign*stepsize)
        sweepArray = np.concatenate((sweepArray,sweepArrayBack))
    return sweepArray

def fileDialog(initAd = "\\Output"):
    root = tk.Tk()
    #root.lift()
    root.attributes('-topmost','true')   
    root.withdraw()
    fullPath = asksaveasfilename(initialdir = initAd)
    a = ''.join(fullPath).rfind("/")
    basePath = fullPath[0:a+1]
    fileName = fullPath[a+1:]
    return [basePath,fileName]

    ######################### Main INIT FUNCTION ###########################
def initialize(testVarList):
    
    instrumentTuple = [item.get('name') for item in testVarList]
    gui = tk.Tk()
    gui.title("pyNE Instrument Control")
    gui.configure(background = 'White')
    #gui.geometry("100x500") #Can change the size of the window
   
    """1) if a tempOptions.json file is available in the current version folder, read it into a dic. Otherwise we create a dict of presets
    We will then later assign all the variables to those so the user doesnt have to type in the val every time."""
    
    try:
        initialDict = readOptions('tempOptions.json')
    except:
        initialDict = {'filePath':'',"sample":'SampleName',"sweepArray":[float('nan'),float('nan')],"sourceVarName":['sourceVariable'],'notes':'enterNotes',
                     'startValue':0,'targetValue1':0.5,'step1':0.1,'targetValue2':float('nan'),'targetValue3':float('nan'),'step2':float('nan'),'step3':float('nan')}
    
    
    #---------------------------------Main HEADER ---------------------
    tk.Label(gui,text="pyNE Instrument Control",background='White',  font=(None, 12), height=5, width=20).grid(row=0,column=0)
    
    #fr = tk.Frame(gui,width=120,height=60,relief ='raised',borderwidth='2').grid(row=0,column=2,columnspan=2)
    #IDText ="Measurement ID: None" #+str(ID.readCurrentID())
    #tk.Label(fr,text=IDText).grid(row=0,column=2)
    
    folderPath =tk.StringVar()
    folderPath.set(initialDict['filePath'])
    tk.Entry(textvariable = folderPath,width=50).grid(row=0,column=1,columnspan=2)
    browseButton = tk.Button(text="Browse",width=20,command = lambda: browseFile(initialDict['filePath'],initialDict,folderPath))
    browseButton.grid(row=0,column=3,padx=20,pady=20)
    #---------------------------------END Main HEADER ---------------------
    
    
    #---------------General Information --------------------------
    generalInput = tk.LabelFrame(gui,text="General information",background='White',width=800,height=100,borderwidth="2").grid(row=1,column=0,columnspan=2,rowspan=3)
    gI_StartRow =1
    #Prefix =tk.StringVar()
    #Prefix.set("JS")
    #tk.Label(generalInput,text="Measurement Name Prefix:").grid(row=1,column=1)
    #tk.Entry(generalInput,textvariable = Prefix).grid(row=1,column=2)
    
    Sample =tk.StringVar()
    Sample.set(initialDict["sample"])
    tk.Label(generalInput,text="Sample/Device:").grid(row=gI_StartRow,column=0)
    tk.Entry(generalInput,textvariable = Sample).grid(row=gI_StartRow,column=1)
    
    notes =tk.StringVar()
    notes.set(initialDict["notes"])
    tk.Label(generalInput,text="Notes").grid(row=gI_StartRow+1,column=0)
    Notes = tk.Entry(generalInput,textvariable = notes,width=40)
    Notes.grid(row=gI_StartRow+1,column=1,columnspan=1)
    
    #-----------------------SWEEP SETTINGS----------------------  
    startRow =5
    startColumn=0
    frameColSpan = 6
    sourceArrayInput = tk.LabelFrame(gui,text="Source input - Sweep Measurement",
                                     background='White',width=1300,height=150,borderwidth="2").grid(row=startRow,column=startColumn,
                                                                                             columnspan=frameColSpan,rowspan=4) #MAIN Container for Sweepparameters , instrument etc.
    SweepInstrument = tk.StringVar()
    SweepInstrument.set("Keithley2401")
    sweepInstr = tk.OptionMenu(sourceArrayInput, SweepInstrument,*instrumentTuple)
    sweepInstr.grid(row=startRow+1,column=startColumn)
    
    #[testVarList[0].get('name'),testVarList[0].type],#[testVarList[1].get('name'),testVarList[1].type]
    
    SourceVarName = tk.StringVar()
    SourceVarName.set(initialDict["sourceVarName"][0])# default value
    sourceVarName = tk.Entry(sourceArrayInput, textvariable=SourceVarName)
    sourceVarName.grid(row=startRow+1,column=(startColumn+1))
    
    #First set of values: Start, Target1, Step1
    Vstart = tk.StringVar()
    Vstart.set(initialDict['startValue']) #default values
    tk.Label(sourceArrayInput,text="Start: ").grid(row=startRow+1,column=startColumn+2)
    VgStartEntry = tk.Entry(sourceArrayInput,textvariable = Vstart,width=8)
    VgStartEntry.grid(row=startRow+1, column=startColumn+3)
   
    Vend = tk.StringVar()
    Vend.set(initialDict['targetValue1'])
    tk.Label(sourceArrayInput,text="Target #1:").grid(row=startRow+2,column=startColumn+2)
    VgEndEntry = tk.Entry(sourceArrayInput,textvariable = Vend,width=8)
    VgEndEntry.grid(row=startRow+2,column=startColumn+3)

    Stepsize = tk.StringVar()
    Stepsize.set(initialDict['step1'])
    tk.Label(sourceArrayInput,text="Stepsize #1:").grid(row=startRow+2,column=startColumn+4)
    StepSizeEntry = tk.Entry(sourceArrayInput,textvariable = Stepsize,width=8)
    StepSizeEntry.grid(row=startRow+2,column=startColumn+5)

    Target2 = tk.StringVar()
    Target2.set(initialDict['targetValue2'])
    tk.Label(sourceArrayInput,text="Target #2:").grid(row=startRow+3,column=startColumn+2)
    Target2Entry = tk.Entry(sourceArrayInput,textvariable = Target2,width=8)
    Target2Entry.grid(row=startRow+3,column=startColumn+3)
    
    Stepsize2 = tk.StringVar()
    Stepsize2.set(initialDict['step2']) #this will have to be set better in the future
    tk.Label(sourceArrayInput,text="Stepsize #2:").grid(row=startRow+3,column=startColumn+4)
    StepSizeEntry2 = tk.Entry(sourceArrayInput,textvariable = Stepsize2,width=8)
    StepSizeEntry2.grid(row=startRow+3,column=startColumn+5)
    #mybutton = tk.Button(root1,text="Print input",command = lambda: showfunc(Vstart))
    Target3 = tk.StringVar()
    Target3.set(initialDict['targetValue3'])
    tk.Label(sourceArrayInput,text="Target #3:").grid(row=startRow+4,column=startColumn+2)
    Target3Entry = tk.Entry(sourceArrayInput,textvariable = Target3,width=8)
    Target3Entry.grid(row=startRow+4,column=startColumn+3)
    
    Stepsize3 = tk.StringVar()
    Stepsize3.set(initialDict['step3']) #this will have to be set better in the future
    tk.Label(sourceArrayInput,text="Stepsize #3:").grid(row=startRow+4,column=startColumn+4)
    StepSizeEntry3 = tk.Entry(sourceArrayInput,textvariable = Stepsize3,width=8)
    StepSizeEntry3.grid(row=startRow+4,column=startColumn+5)
    
#    UpDownSweepBool = tk.IntVar()
#    UpDownSweep = tk.Checkbutton(sourceArrayInput,text = "Sweep back to the initial value",variable=UpDownSweepBool)
#    UpDownSweep.grid(row=startRow+5,column=startColumn,sticky="E")
 
    updateButton = tk.Button(sourceArrayInput,text="Update",width=20,command = lambda: update(Vstart,Vend,Stepsize,
                                                                                     Target2,Stepsize2,Target3,Stepsize3,
                                                                                     canvas,line))
    updateButton.grid(row=startRow+1,column=startColumn+4,columnspan=2)
         
    fig = Figure(figsize=(4,3))
    a= fig.add_subplot(111)
    #a.plot([0],[0],'ro')
    line, = a.plot(0,0,'ro',markersize=1)
    canvas = FigureCanvasTkAgg(fig,master = gui)
    canvas.draw()#canvas.show() previously
    canvas.get_tk_widget().grid(row=startRow,rowspan=5,column=startColumn+frameColSpan,columnspan=3,padx=10,pady=10)
    
    #-----------------------END  Sweep SETTINGS----------------------
    
    update(Vstart,Vend,Stepsize,Target2,Stepsize2,Target3,Stepsize3,canvas,line) #This calls the update function in the very beginning once so that the Figure is updated with the default values
    
    #--------------------------Finish Button---------------
    mybutton = tk.Button(gui,text="Done",width=50,command =gui.destroy )#exitGui(gui)
    mybutton.grid(row=12,column=0,columnspan=5,rowspan=2)
    
   #--------------------------END    Finish Button---------Vstart  Vend Stepsize
    gui.mainloop()
    
    return returnFunction(folderPath,Sample,notes,SourceVarName,Vstart,Vend,Stepsize,Target2,Target3,Stepsize2,Stepsize3)

def update(start,target1,step,target2,step2,target3,step3,figHandle,lineHandle):
    #plt.plot(xdata,ydata)
    [xdata,ydata] = appendTargetArrays(start,target1,step,target2,step2,target3,step3)
    
    lineHandle.set_ydata(ydata)
    lineHandle.set_xdata(xdata)
    
    ax = figHandle.figure.axes[0]
    try:#catches the case when the array is empty and it cant do it.
        ax.set_xlim(min(xdata)-0.1*max(xdata),1.1*max(xdata))
        ax.set_ylim(min(ydata)-0.1*max(abs(ydata)),max(ydata)+0.1*max(abs(ydata)))
    except:
        pass
    #print('Current setter instrument is:'+str(testVarList))
    figHandle.draw()
    figHandle.flush_events()

def appendTargetArrays(start,target1,step,target2,step2,target3,step3):
    
    try:
        startVal = float(start.get())
        target1Val = float(target1.get())
        step1Val = float(step.get())    
        ydata = array(startVal,target1Val,step1Val)
        xdata = list(range(len(ydata)))
        
    except ValueError:
        print("First target/step is no a usable value and was ignored")
        startVal,target1Val,step1Val=float('nan')
    try:
        float(target2.get())
        ydata2 = array(float(target1.get()),float(target2.get()),float(step2.get()))
        
        ydata = np.concatenate((ydata, ydata2))

        xdata = list(range(len(ydata)))

    except ValueError:
        
        print("Second target/step is no a usable value and was ignored")
    
    try:
        float(target3.get()) and float(step3.get())
        ydata3 = array(float(target2.get()),float(target3.get()),float(step3.get()))    
        ydata = np.concatenate((ydata, ydata3))
             
        xdata = list(range(len(ydata)))
        
    except ValueError:
        print("Third target/step is no a usable value and was ignored")
        
    return [xdata,ydata]  

def returnSetpoints(start,target1,step,target2,step2,target3,step3):
    results = []
    for element in [start,target1,step,target2,step2,target3,step3]:
        try:
            results.append(float(element.get()))
        except ValueError:
            results.append(float('nan'))
    return results
    
def browseFile(initialFolder,storeDict,folderPath):
    filePath= askdirectory(initialdir = initialFolder)
    
    folderPath.set(filePath)
    storeDict['filePath'] = filePath
    
    return filePath

def returnFunction(folderPath,Sample,Notes,SourceVarName,
                   Vgstart,Vgend,Vstep,Target2,Target3,Stepsize2,Stepsize3):
    
    sweepArray = appendTargetArrays(Vgstart,Vgend,Vstep,Target2,Stepsize2,Target3,Stepsize3)[1]#Step 1) get the final sweep array, same as plottet in the update() function
    
    resList = [] #Step 2: retrieve all the other misc values set in the GUI like folder path or sample name.
    for e in [folderPath,Sample,Notes,SourceVarName]:
        try:
            resList.append(e.get())
        except ValueError :
            print('Value Error when assigning the misc variables')
    [filePath,sample,notes,sourceVarName] = resList[:]
      
    [start,end,step,Target2,Target3,Stepsize2,Stepsize3] = returnSetpoints(Vgstart,Vgend,Vstep,Target2,Target3,Stepsize2,Stepsize3) #Step 3> Get all the numveric target set and step points.
     

    returnDic = {'filePath':filePath,"sample":sample,"sweepArray":sweepArray.tolist(),"sourceVarName":[sourceVarName],'notes':notes,
                     'startValue':start,'targetValue1':end,'step1':step,'targetValue2':Target2,'targetValue3':Target3,'step2':Stepsize2,'step3':Stepsize3}
        
    writeOptions(returnDic)
    return returnDic 
    
#    except ValueError:
#        print("Please enter float numbers only")
    
def readOptions(optionFile):
    with open(optionFile) as json_file:  
        jason_Dict = json.load(json_file)
    return jason_Dict

def writeOptions(optionsDict,fileName='tempOptions'):    
    with open(fileName+'.json', 'w') as outfile:
        json.dump(optionsDict, outfile,indent=4, sort_keys=True)
