# PyNE-probe documentation (v1.0.0) -- Adam to update

A package for simple electrical measurements using the National Instruments (NI) VISA standard. Developed by Jakob Seidl and coworkers at the Nanoelectronics group at the University of New South Wales, Sydney. It was originally written in Python 2.7 and later adapted for modern Python 3.

The package is divided into two sub-units: Instruments and utility functions that help carry out a electronic measurement.
It allows you to connect to various electronic measurement equipment in a few lines of code.

Currently implemented instruments include:

1. Keithley 2400 series source measure units (SMUs)
2. Keithley 2000 series digital multimeters
3. Keithley 6517 'Electrometer'
4. Stanford Instruments SRS830 Lock-in amplifier
5. National Instruments USB6216 data acquisition card (NiDAQ)
6. Yokogawa GS200 source measure unit

It is easy to write you own instrument classes by using existing intrument classes and replacing the 
required GPIB SCPI commands commonly supplied in the intrument's handbook.

In addition, this code was also used to control Oxford Instruments superconducting magnet power supplies and
read out the status of Oxford instruments Heliox cryostats. This code is available from the author upon request.
## A: Quickstart guide
### A.1 Installing PyNE-probe:
Case A: from the online repository PyPi:

`$ pip install PyNE-probe` 

Case B: from a local PyNE-probe folder on your PC:

`$ pip install -e local/Path/PyNE-probe/.`   the `-e` flag allows to make changes to the original files in the folder,
useful if you want to tweak the code while working. Enclose you path like this if it contains whitespace: "local Path/with whitespace/SourceDirectory".\
You can download the sourcecode (.zip) from github under
https://github.com/AdMico/PyNE-probe

Install the package in a virtual environment (see e.g. [this guide](https://realpython.com/python-virtual-environments-a-primer/)) or in your
global Python 3 installation, whatever works best for your use-case.

Check if the installation was successful:\
`$ pip list` returns a list of packages that should contain
```$ pip  20.3
PyNE-probe           1.0.0    
```
if you installed it from the internet (Case A) or 
```$ pip  20.3
PyNE-probe           /Path/To/Local/SourceDirectory    
```
if you installed PyNE-probe from a local folder, e.g., after downloading the source code from gitHub (Case B).\
You can then try loading the package as described in the following section.

### A.2 Non-python drivers and hardware you'll need

IMPORTANT: In order to use commercial GPIB-controlled instruments such as Keithley source-measure units,
you need to install the proprietary National Instruments VISA/USB-H bundle driver 
[here](https://www.ni.com/en-au/support/downloads/drivers/download.ni-488-2.html#306147). Possibly, this could be
replaced by a fully open-source
library such as [pyvisa-py](https://pyvisa-py.readthedocs.io/en/latest/) that supplies the back-end.
For using the National Instruments Data Acquisition cards (NIDaQ), you need the corresponding [NIDaQ driver](https://www.ni.com/en-au/support/downloads/drivers/download.ni-daqmx.html#288239). 
 
For both we recommend not choosing the latest version but simpler, earlier versions.

### A.3 Loading and testing PyNE-probe:
In your python console type:
```python:
>>> import PyNE-probe.Instruments as I
>>> import PyNE-probe.utility as U
```
If this works, you can run a test measurement using 'virtual' instruments to check weather 
plotting and data storage works fine:
```
>>> U.runTest()
```
should open a plot window with simulated linear and sinusoidal noise signals measured over time. 
A progress bar should indicated the status of the measurement.
In the console, you should see a notification that a folder has been created where the data will be stored.
```
Out: Created data storage directory: TempDat/
/>>>>>> Finished measurement A1 | Duration: 9.4 seconds = 0.2 min  <<<<<<<
```

Setting up any basic measurement requires three steps: 
1. Setting up all required instruments and configuring them (see A.4)
2. Defining the sweep-array and designating which instrument should sweep a variable and which instrument(s)
 should just read/measure (see A.5).
3. Call the sweep function 'sweep()' from PyNE-probe.utility using the Instrument parameters defined in 2, see A.5.

### A.4 Initializing instruments:
We recommend using an IDE such as PyCharm that supports code completion. E.g., type 'I.' 
(or any other alias you imported PyNE-probe.Instruments as) and all implemented Instruments will appear in a drop-down list. Use TAB-completion when typing in the console. Let's use a Keithley 2401 source-measure unit:
```
>>> myKeithley = I.Keithley2401(10)  #  Initializes a Keithely2401 instrument at GPIB port 10
KEITHLEY INSTRUMENTS INC., MODEL nnnn, xxxxxxx, yyyyy/zzzzz /a/d  #  Parameters on the right depend on exact model/firmware
```
The `'KEITHLEY INSTRUMENTS INC.'` message is the instrument's response to the typical '*IDN?' query and indicates that the instrument has been successfully initiated.
Most instruments have internal options that can be set before the measurement. E.g., the Keithley source-measure
unit can be set to source voltage (and measure its output current) or to source a current instead. Every instrument has a set() and  setOptions() method:
E.g. 
```
>>> myKeithley.set('name','myKeithleyInstrumentName) # Every instrument can have a unique 'name'
>>> myKeithley.setOptions({'sourceMode':'voltage, # sourcing voltage
                      'sourceRange':20})      # Using high source range of up to 20 Volts
```
For a list of all instrument options and possible values, see [XX].
### A.5 Using the sweep() function 


In this example we define a simple current vs. voltage sweep with a single Keithley instrument. 
We define a empty dictionary that holds all relevant data. After defining `'basePath'` and `'fileName'`
under which the data will be stored, we define the `'setter'` and `'getters'` fields. They determine,
which instrument actively set (outputs) a value, e.g. a gate voltage, and which instruments measure the
resulting variables, e.g., input voltages, currents. Here we use the same Keithley instrument to do both.
The values we want to sweep over, in this case source-drain voltages, are defined in the `'sweepArray` field.
Here we use the `targetArray()` function, but standard lists or numpy.arrays can be used as well. 
In the last step, we call the `sweep()` function with the required `Dct` parameter and two optional parameters, `delay` and `plotVars`. 
Note that the name `Dct` of the dictionary may be changed but the keywords such as `'setter'` and `'sweepArray'` need to be exactly used as displayed here.
```
myScript.py
-----------
Dct = {} # Define empty dictionary as container
Dct['basePath'] = "Data/" # Relative to your current working directory
Dct['fileName'] = 'SampleA' # Sets the file name under which data will be saved and logged.

Dct['setters'] = {myKeithley:    'V_SD'} # Set the variable called 'V_SD' with our 'myKeithley' object
Dct['readers'] = {myKeithley:    'I_SD'} # Measure the variable called 'I_SD' with our 'myKeithley' object

Dct['sweepArray'] = U.targetArray([0,1,0],stepsize=0.1) # Define values from 0V -> 1V -> 0V in 0.1V steps
                                                        # targetArray is a utility function provided

df = U.sweep(Dct,                          # call sweep function and provide the Dct dictionary defined
             delay=0.2,                    # seconds wait time in between points
             plotVars = [('V_SD','I_SD')]) # plot 'I_SD' (y-axis) over 'V_SD (x-axis)'      
                                                                   
```
This should open a live-plot that shows `'I_SD'` vs. `'V_SD'`. The data is saved under "Data/"
 (folder is created if it doesn't exist, see console output). Per measurement, four files are saved:
  The data is saved in .tsv format (blank text), in .mat matlab data format. In addition, a log.tsv file is created that logs 
  important information of the measurement run, such as instruments used etc. When plotting is enabled, the plot is also saved as .png.
  Note that each measurement has unique measurement ID consisting of a letter prefix and a running number. 
  This is e.g., displayed in the plot title and each saved data file is preceded by it. This also prevents data 
  from being overwritten even when the user uses the same `fileName` repeatedly. The `sweep()` function 
  returns a `pandas.DataFrame`, here assigned to `df`, that holds the acquired data with column labels corresponding to the variable names provided.
  This can be useful if the user wants to use the acquired data immediately during the measurement routine.
```
>>> df
Out:
      V_SD      I_SD     
0        .         .    
1        .         .  
2        .         .   
..     ...       ... 

>>> df.plot(x = 'V_SD', y ='I_SD') # A simple way of plotting the data                                                        
```
### A.5 finding help
1 Remember that in Python, you can call the help() function on any method or object. E.g., if you want
to find out about the `sweep()` function, try calling
```
>>> help(U.sweep) # No brackets here as we don't want to call the function
```
Note: Doc-strings are currently being implemented, so help() might not yet work for all methods/classes.

2 If you can't remember, which attributes you can set with the myInstrument.set(), just call 
those methods with a clearly wrong argument:
```
>>> noiseGenerator = I.LinearNoiseGenerator()

>>> noiseGenerator.set('wrong',1)
ValueError: 
"wrong is not a valid option. dict_keys(['sourceLevel', 'name'])
 are available"
```
,which means only the keys `'sourceLevel` and `'name` can be set for this instrument.

3 If you remember the key attribute but not the possible numerical ranges, you can call set() 
with a clearly wrong numerical argument
```
>>> keithley = I.Keithley2401(10)

>>> keithley.set('sourceRange',3000)
ValueError: 
"3000 is not a valid voltage source range for the Keithley2401.
Valid voltage ranges are: 20, 10, 1, 0.1, 0.01 and 0.001 Volts and
equivalent exponential representations."
```
  
## B   Example scripts/ Tutorials
### B.1 Two variables: A gate-sweep measurement
```
gateSweepScript.py
------------------

Vgate_Keithley = I.Keithley2401(10)
VBias_Keithley = I.Keithley2401(11)

[Set options either manually or with .setOptions({'key':argument}) method]

Dct = {} # Define empty dictionary as container
Dct['basePath'] = "Data/" 


Dct['setters'] = {Vgate_Keithley:    'V_G'} 

Dct['readers'] = {  VBias_Keithley:    'I_SD',
                    Vgate_Keithley:    'I_LeakGate'} 


gateLow = -1; gateHigh = 1.5
Dct['sweepArray'] = U.targetArray([0, gateLow, gateHigh, 0], stepsize = 0.05) 
          
sourceDrainBiases = [0.05, 0.1, 0.5] #  volt

for bias in sourceDrainBiases:
    
    Dct['fileName'] = f'SampleA_{bias}_volt' # data for each bias will have the bias in the filename for convenience, e.g. SampleA_0.5_volt'
    
    VBias_Keithley.goTo(bias,0.01,0.2) # Go to the desired bias, then execute gate sweep.  
    U.sweep(Dct, delay=0.2, plotVars = [('V_G','I_SD'), ('V_G','I_LeakGate')])
                            
                                                     
```
### B.2 Measure instruments over time
```
timeMeasScript.py
-----------------

myKeith = I.Keithley2401(11)
myTimeInst = I.TimeMeas()  # virtual instrument

[Set myKeith options if desired ...]
                                   
Dct['basePath'] = "Data/" 
Dct['fileName'] = 'SampleB_currOverTime'

Dct['setters'] = {myTimeInst:    'dummyPoints'} 

Dct['readers'] = {  myKeith:    'I_d',
                    myTimeInst:    'time'}    

Dct['sweepArray'] = range(100) # measure over 100 datapoints

df = U.sweep(Dct, delay=0.2, # The delay here determines roughly how often we measure per unit time.
        plotVars = [('time','I_d')],
        breakCondition = ('time','>',50)) # optionally we can terminate the measurement after a certain time period if desired.

                            
```
### B.3 Simple I-V measurements with the NIDaq
```
simpleNiDaQ.py
--------------

DaqIn = USB6216In(2,usbPort = 'Dev1') # Using Analog Input AI2. usbPort depends on the usb port windows assigns to the nidaq
DaqOut = USB6216Out(1,usbPort = 'Dev1') # Using Analog Output AO1

DaqOut.setOptions({
    "feedBack":"Int",
    "extPort":6, # Can be any number 0-7 if in 'Int'
    "scaleFactor":1
})

DaqIn.set("scaleFactor",1) # If we don't use an amplifier, gain =1)

myTime = TimeMeas()

Dct = {} # Define empty dictionary as container
Dct['basePath'] = "Data/" 
Dct['fileName'] = 'SampleC_IV'


Dct['setters'] = {DaqOut:    'V_SD'} 

Dct['readers'] = {  DaqIn:    'I_SD',
                    myTime:    'time'} 

targetLow = 0; targetHigh = 1.5
Dct['sweepArray'] = U.targetArray([targetLow, targetHigh, targetLow], stepsize = 0.01) 

df = U.sweep(Dct, # No plotting and 'delay' here to speed up the nidaq aquisition.
saveCounter = 100) # Only save data every 100th read to increase speed.
                                                        
```
### B.4 Example using lock-in amplifiers
```
lockIn_HallScript.py
--------------------
lockIn_ISD = I.SRS830(8)
lockIn_VSD = I.SRS830(10)
lockIn_VHall = I.SRS830(11)  
keith_Vg = I.Keithley2401(13)


# You could set all these manually on the instrument,
# except 'scaleFactor' and 'autoSensitivity'

lockIn_ISD.setOptions({
      'frequency':77, 
      'amplitude':0.004,
      'input':'I1',
      'scaleFactor':1,
      'phase':180,
      'autoSensitivity':False })
        

[.. set other options as desired...]


Dct = {} # Define empty dictionary as container
Dct['basePath'] = "Data/" 
Dct['fileName'] = 'SampleC_IV'

myComments = """
        Hall bar measurement at B = +2 T @ 4K
        We measure the current through device with lockIn_ISD
        and the voltage across the device with lockIn_VSD. The third lock in,
        lockIn_VHall, measures the Hall voltage. We sweep the gate-voltage with 
        a Keithley2400 (keith_Vg). """

Dct['setters'] = {keith_Vg:    'V_g'} 

Dct['readers'] = {  lockIn_ISD:    ['Isd_X','Isd_Y'],  # The lock-in puts out TWO read-values
                    lockIn_VSD:    ['Vsd_X','Vsd_Y'],  # We put them together in brackets 
                    lockIn_VH:    ['VHall_X','VHall_Y'],
                    keith_Vg:    'I_gateLeak'          # Instruments that only yield single values
            }                                          # don't need brackets.


targetLow = 0; targetHigh = 1.5
Dct['sweepArray'] = U.targetArray([targetLow, targetHigh, targetLow], stepsize = 0.01) 

lockIn_ISD.goTo(2,0.2,0.2) # got to a excitation amplitude of 2 V (usually into a voltage divider)                                                             

data = U.sweep(Dct,
               plotVars = [('V_g','I_sd_X),
                            ('V_g','V_Hall_X),
                            ('V_g','VHall_Y)]),
               plotParams = [('b-','linear-log'), # Sets the plot appearance and lin-log x-y scale
                              ('go','linear-linear')  #linear-linear scale (default)
                              ('ro--','linear-linear')],
               comments = myComments
               )
```     
### B.5 Abruptly changing signals - sourcing step functions with SMU's
```
square_transients.py
--------------------
Vgate_Keithley = I.Keithley2401(10)
VBias_Keithley = I.Keithley2401(11)
myTime = TimeMeas()

Dct = {} # Define empty dictionary as container
Dct['basePath'] = "Data/" 
Dct['fileName'] = 'SampleD_GateTransient'

VgHigh = 0.5  # volt
VgLow = -0.1 
# Creates a Low-HIgh-Low-High square wave gate potential:  
Dct['sweepArray'] = [VgLow]*50 + [VgHigh]*150 + [VgLow]*50 + [VgHigh]*150


Dct['setters'] = {Vgate_Keithley:      'V_G'} 

Dct['readers'] = {  VBias_Keithley:    'I_SD',
                    Vgate_Keithley:    'I_LeakGate'
                    myTime:            'time'} 

df = U.sweep(Dct,
        plotVars = [('time','I_SD'),
                    ('time','V_G')]
            )                                                      
```
### B.6 Reading current instrument setter status to dynamically define next sweeps
```
breakGateSweep.py
------------------
import pandas as pd # Required later for dataframe operations

Vgate_Keithley = I.Keithley2401(10)
VBias_Keithley = I.Keithley2401(11)

[Set options either manually or with .setOptions({'key':argument}) method]

Dct = {} # Define empty dictionary as container
Dct['basePath'] = "Data/" 

Dct['setters'] = {Vgate_Keithley:    'V_G'} 

Dct['readers'] = {  VBias_Keithley:    'I_SD',
                    Vgate_Keithley:    'I_LeakGate'} 

gateLow = -1; gateHigh = 1.5
Dct['sweepArray'] = U.targetArray([0, gateLow, gateHigh, 0], stepsize = 0.05) 
          
sourceDrainBiase = 0.1 #  volt

Dct['fileName'] = 'gateSweep_01V'

VBias_Keithley.goTo(bias,0.01,0.2) # Go to the desired bias, then execute gate sweep.  

# This gatesweep breaks if the gate leakge current ever surpasses 10 nA.
df = U.sweep(Dct, delay=0.2,
        plotVars = [('V_G','I_SD'), ('V_G','I_LeakGate')],
        breakCondition=('I_LeakGate','>',10E-9))
            

#Check if the measurement was broken by the breakCondition:
# If measurement was stopped, measure from the current gate voltage back to 0.

if len(df) < len(Dct['sweepArray']):
    currentVg = Vgate_Keithley.get('sourceLevel') # At what VG did the gate leakage exceed out limit?
    Dct['sweepArray'] = U.targetArray([currentVg,0], stepsize = 0.05) # overwrite previous array
    
    # Finally carry out measurement
    dfBack = U.sweep(Dct, delay=0.2,
                     plotVars = [('V_G','I_SD'), ('V_G','I_LeakGate')]) 
    
# It can be useful to concatenate the data from both measurements into one dataframe .
This can be more convenient than the separate saved data files, which were created for each measurement.


dataFull = pd.concat([df,dfBack],ignore_index=True)
dataFull.plot(x='V_G',y='I_SD')
                                                        
```


---
## C   Documentation of instrument parameters
Upon creation, these Instruments need to be prefixed by the PyNE-probe.Instrument alias (`I.` in the example scripts.)
##### Most if the following properties can be set, as well as queried with the get/set methods.
#### C.1 Keithley 2400 series
Source/measure unit supplying either voltage or current.

`'outputEnable'`: Boolean, Turns instrument output on (True or 1) or off (False or 0). 
`outputEnable = True` is required for instrument operation.
Example: `>>> myKeithley.set('outputEnable',False)` 

`'sourceMode'`, String, can be `'voltage'` or `'current'` for sourcing a voltage or current respectively.
The instrument will also measure the flowing current (when sourcing `'voltage'`) or the resulting voltage (when sourcing a `'current'`).
When a Keithley2400 instrument is created, it will internally check the current source mode of the instrument, so `'sourceMode'` can be set in hardware or software.

`'sourceRange': ` Float, sets overall source range of instrument. Highest value you want to put out need to be below this limit.
When sourcing `'voltage'`, possible limits are: ` (20,10,1,0.1,0.01,0.001)` (in volts). When sourcing 
`'current'`, possible limits are: `(1,0.1,0.01,0.001,1E-4,1E-5,1E-6)`(in amperes). 

`'name''` String, Optional unique name of the instrument to distinguish between various instruments of the same type.

`'sourceLevel'`, Float, set or get method. Directly sets the output (voltage or current) to the set value. We do not recommend using this directly, especially not for sensitive nanoscale samples.
Use `myInstrument.goTo(target,stepSize,delay)` instead to slowly approach the desired setpoint.

`'senseLevel'` Returns float, get method only. Returns the current voltage/current reading.

`'senseRange'`, when sourcing `'voltage': (1.05E-4,1.05E-5,1.05E-6)` amperes.
 OR when sourcing `'current': (21.0,2.1,0.21)` volts

`compliance`, Float, Hard limit of highest current the instrument supplies when sourcing `'voltage'`
or highest voltage when sourcing `'current'`. Must lie below the highest value the instrument can measure, see `'senseRange'`.

`'scaleFactor'` Float, scales the measured values form the instrument. Defaults to 1 and does not usually have to be set. 

---
#### C.2 Keithley 2000 series
Versatile amp/voltmeter.

`'senseMode'`, String, determines whether the instrument reads current or voltage as input. Can be `'voltage'` or `'current'`.

`'senseRange'` Float, sets the input range. Allowed voltage ranges are: `(100E-3,1,10,100,1000) #  volts.`
Allowed current ranges are: `(10E-3,100E-3,1,3) #  amps.`

`'senseLevel'`, Returns float, get method only. Returns reading of input voltage/current.

`'scaleFactor'` Float, scales the measured values form the instrument. Useful when current or voltage preamps are used and the output is read by the Keithley 2000. 

---

#### C.3 Keithley 6517A Electrometer
Very sensitive amp/voltmeter.

`'zeroCheck'` Boolean, `True` enables zerocheck mode, which protects the instrument when not in use.
 Needs to be disabled (`False`) before a measurement.
 
`senseMode'`, String, determines whether the instrument reads current or voltage as input. Can be `'voltage'` or `'current'`.

`'senseLevel'`, Returns float, get method only. Returns reading of input voltage/current.

`'senseRange'` Float, when measuring current: `[20E-12,200E-12,2E-9,20E-9,200E-9,2E-6,20E-6,200E-6,2E-3,20E-3] # amperes.`
When measuring voltage: `[2,20,200] #  volts.`


`'autoRange'`, Boolean. When `True`, the instrument will try to adjust its `'senseLevel'` according to its input readings.

`'NPLC'`, Float between 0.1 & 10. Sets the integration time during a measurement in 'power line cycles'. Default is 1. 
Reduce this if your overall sweep velocity is too fast for the instrument to catch up, increase `'NPLC'` if you need slow, high precision readings of low currents. 

---


#### C.4 SRS830 lock-in amplifier

For a detailed look at the lock-in specific parameters, please refer to the excellent [manual of the SRS830](https://www.thinksrs.com/downloads/pdfs/manuals/SR830m.pdf).

`'frequency':` Float between 0.1 Hz & 100 kHz. Sets the operation frequency.

`'amplitude':` Float between 0.004 V & 5 V. Sets the root-mean-square amplitude of the sinusoidal
output voltage of the amplifier.

`'input'` String, can be `"A","A-B","I1" or "I2"` corresponding to a simple voltage measurement `"A"`, 
a differential voltage measurement `"A-B"` or a current measurement with two different gains `"I1"/"I2""` 

`'timeConst' :` Float or int. Sets the time constant of the lock-in amplifier. Allowed inputs are: `[10E-6,30E-6,100E-6,300E-6,1E-3,3E-3,10E-3,30E-3,100E-3,300E-3,1,3,10,30,100,300] #  seconds`

`'phase'` Float, sets the phase-parameter of the lock-in amplifier in degrees. Can range from 0 to 360 degrees. 

`'sweepParameter'` String, can be `"frequency" or "amplitude"`. When the lock-in is used as a setter in the sweep() function, 
you can choose whether you want to sweep the RMS amplitude (default) or output frequency. Sweeping the frequency can e.g. be used to
determine which drive frequency generates low noise background

`'sourceLevel'`, Float, set method only. Directly sets the output amplitude (or frequency) to the set value. We do not recommend using this directly.
Use `myInstrument.goTo(target,stepSize,delay)` instead to slowly approach the desired setpoint.

`'senseLevel'` Tuple of floats `(Xreading, Yreading)`, get method only. Returns the X- and Y-component of the voltage/current reading.

`'senseRange'` Float, `[1E-9,2E-9,5E-9,10E-9,20E-9,50E-9,100E-9,200E-9,500E-9,1E-6,2E-6,5E-6,10E-6,20E-6,50E-6,100E-6,200E-6,500E-6,1E-3,2E-3,5E-3,10E-3,20E-3,50E-3,100E-3,200E-3,500E-3,1] # volts`
These voltage ranges directly correspond to current ranges, as written on the amplifier front panel.

`'autoSensitivity'` Boolean. When `True`, the instrument will try to adjust its `'senseLevel'` according to its input readings. Note
that this is not fully mature at the moment and should be properly tested prior to use in a real experiment. Defaults to `False.` 

`'name'` String, Optional unique name of the instrument to distinguish between various instruments of the same type.

#### C.5 YokogawaGS200
Voltage/current source unit.

`outputEnable`, Boolean, `True` is required for instrument operation.

`'sourceMode'`, String, can be `'voltage'` or `'current'` for sourcing a voltage or current, respectively.

`'sourceRange': ` Float, sets overall source range of instrument. Highest value you want to put out needs to be below this limit.
When sourcing `'voltage'`, possible limits are: ` (30,10,1,0.1,0.01)` (in volts). When sourcing 
`'current'`, possible limits are: `(0.2,0.1,0.01,0.001)`(in amperes). 

`'sourceLevel'`, Float, set or get method. Directly sets the output amplitude to the set value. We do not recommend using this directly.
Use `myInstrument.goTo(target,stepSize,delay)` instead to slowly approach the desired setpoint.

`'name'` String, optional. Unique name of the instrument to distinguish between various instruments of the same type.

`compliance`, Float, Hard limit of highest current the instrument supplies when sourcing `'voltage'`
or highest voltage when sourcing `'current'`. 

#### C.6 National Instruments NiDaQ (USB6216) 
Data acquisition device that can carry out fast (up to 200kHz) transient measurements. 
Consists of a arbitrary function generator part (Out) and various Analog-to-digital converter inputs (IN).
These are realized by the `USB6216Out()` and `USB6216In()` classes, respectively.

1. `USB6216Out(outputPort,usbPort)`

`outputPort` int, required upon initialization. Can be 0: (port AO0) or 1: (port AO1)  

`usbPort` int, required upon initialization. Internal device port of the NiDaQ. Is usually 1 (Dev1) or 2 (Dev).
                Will throw an error when outputting a voltage. Device number can be found e.g. using NI MAX.  

`feedback` int, optional. Default: `'Int'` (internal). External feedback (`'Ext'`) not tested yet.

`extPort` int, optional. If `feedback` is set to `'Int'`, it can be any number from 0-7, without any effect. 
Testing required when `feedback` is set to `'Ext'`.

2. `USB6216In(inputPort,usbPort)`

`inputPort` int, required upon initialization. Can range from 0: (port AI0) to 7: (port AI7)  

`usbPort` int, required upon initialization. Internal device port of the NiDaQ. Is usually 1 (Dev1) or 2 (Dev).
                Will throw an error when outputting a voltage. Device number can be found e.g. using NI MAX.  

`scaleFactor` float, optional. Scales the measured voltages by this factor. Used when the measured 
voltages are amplified by an amplifier of known gain. 


## D   Documentation of utility functions
To access these functions, use the PyNE-probe.utility alias (`U.` in the example scripts.)
#### D.1 The `sweep()` function
Common usage: See example script above.


Parameters:

`delay` Float, wait time in seconds after a value has been set and before instruments are read out. Default=0.0

`comments` String, Comments on experiment, sample etc. Is stored in the .log file together with
 the saved data. Useful for data not measured by instruments. Example: `"SampleA, I-V, T= 77K"`

`plotVars` list of `('xVar','yVar')` tuples to be plotted. Example: `[ ('V_SD', 'I_SD') ]` from above.

`plotParams` list of `('plotString','XAxisScale-YAxisScale')` tuples. `'plotString'` contains color, line and marker info. 
See the [Matplotlib documentation](https://matplotlib.org/3.3.3/api/_as_gen/matplotlib.pyplot.plot.html) under Notes. 
'XAxisScale-YAxisScale' can be e.g. `'linear-linear'` or `'linear-log'` or any combination.
 Example: `[ ('go-', 'linear-linear') ]`
 
`plotAlpha` Float, Transparency of markers: 1= no transparency, 0 = fully transparent. Default = 0.8

`plotCounter` Integer, After how many datapoints do you want to update the plot.  plotCounter > 1 helps speed up plotting. Default = 1

`plotSize` Tuple of two floats `(xSize,ySize)`, size of plot window in cm. Default = (10,10)

`saveCounter` Integer, After how many datapoints do you want to save data to disc. 
Can help speed up the measurement slightly. Default = 10

`breakCondition` Tuple, `('Variable','comparisonOperator',Value)`. Allows to stop a measurement when a certain condition is met.
 `'Variable'` is compared against `Value` using `'comparisonOperator'`. 
`'comparisonOperator'` can be `'<'` or `'>'` at the moment. Example: `breakCondition = ('I_SD','>',1E-6)` will end the
 measurement when `'I_SD'` reaches a value above 1 microampere.
 
`extraInstruments` List of instrument objects, used to keep track of instruments that are not directly used as setter or reader but you still want to see logged in the .log file.

`saveEnable` Boolean, Defines whether saving the data is desired. Default = True. In the current version, `saveEnable = False` also disables plotting.

#### D.2 The `targetArray([targetList],stepSize)` function
Convenient way of creating a linearly-spaced array of floats of type np.arange(). Easier than concatenating np.arange() or np.linspace().

E.g. `targetArray([0.0,1.0,-1.3,0.0],0.2)` creates an array from 0.0 -> 1.0 -> -1.3 -> 0.0 in 0.2 steps.

`targetList` list of floats. E.g. `[0.0,1.0,-1.3,0.0]`

`stepSize` float. E.g. 0.2. IMPORTANT: If the targets can't be reached with the specified stepsize, e.g., a
target of 0.3 with a stepsize of 0.2, the last datapoint will overshoot the setpoint.
 `>>> targetArray([0,0.3],0.2)` returns `array([0.,0.2,0.4])` NOT containing 0.3! If possible, choose stepsizes
 that match the desired setpoints to avoid this.
#### D.3 Managing the unique measurement identifiers
Every measurement performed with the sweep() identifier displayed as
the plot title that is also part of all saved file names. It consist of a unique prefix + running ID number (int). 
This assures that no measurement will eve rbe overwritten and that you have a unique reference to each measurement, useful for
logging data in a database.

How do I access and manipulate this identifier?

You can list all currently defined identifiers using (assuming you imported PyNE-probe.utility as U)
```
>>> U.listIDs()
Currently used Prefix/Setup: A  --> ID = 1
-------------------------------------------- 
Other available Setups/Prefixes are: #none at the moment
```
Currently only one prefix ('A') is defined. It's running ID is 1, which would increment when running a measurement.

'A' is the standard prefix out of the box. You can create more meaningful prefixes like so:
```
>>> U.addPrefix('test')
```
Checking the identifier with `listIDs()` now shows the new prefix with a ID of 0. However 'A' is still the active prefix.
This means, when carrying out a measurement, only the ID of 'A' is increased. This can be useful, if more than
one scientist works on the same setup but wants to get their data indexed separately, e.g., prefixed by initials.
```
>>> U.listIDs()
Currently used Prefix/Setup: A  --> ID = 1
-------------------------------------------- 
Other available Setups/Prefixes are: 
Prefix/Setup: test  --> ID = 0
```
We can make 'test' the active setup by typing:
```
>>> setCurrentSetup('test')
Succesfully changed preFix/Setup from: A ---> test

>>> U.listIDs()
Currently used Prefix/Setup: test  --> ID = 0
--------------------------------------------- 
Other available Setups/Prefixes are: 
Prefix/Setup: A  --> ID = 1
```

We can directly access the current prefix (string) and ID by with:
```
>>> U.readCurrentSetup()
'test'
>>> U.readCurrentID()
0
```
This is useful if you want to log the measurement ID together with the dataframe
output of the sweep function, i.e., if you're not using the data files saved by sweep().

Lastly, you can clear all current identifiers and start with the default values
```
U.initID()
``` 
however, be aware that this removes all user information and should only be used as a last resort.
### Beyond the sweep() function: Using instruments in a custom for-loop
The sweep() function is a convenient way of carrying out many standard electronic measurements, while facilitating live plotting.
However, in its current form, it cannot cater for more complex measurements, such as multi-parameter sweeps. By accessing instruments directly, you can
create custom procedures that are more versatile. The fundamental methods to set an instrument's output (e.g. output voltage) 
or access its current reading (e.g. input current) are `myInstr.set('sourceLevel',outputLevel)` and `myInstrument.read()` methods, respectively.

In the following example, we will replicate a simple (virtual) noise over time measurement, but this should work accordingly 
for any instrument.

``` 
import time
import PyNE-probe.Instruments as I
import PyNE-probe.utility as U
import matplotlib.pyplot as plt

T = I.TimeMeas()
Noi = I.LinearNoiseGenerator()

points = range(50)

data= {}
data['noise'] = []
data['time'] = []

delay = 0.2 # in seconds

for point in points:

    Noi.set('sourceLevel', point) # This does not do anything with this virtual instrument.
    # Using this on a real instrument would output e.g. a voltage.
    
    time.sleep(delay) # wait between measurements
    
    data['time'].append(T.read()) # Read the current time and write to list
    data['noise'].append(Noi.read()) # Reads current (virtual) noise level and write to list

plt.plot(data['time'],data['noise'],'-o')
plt.xlabel('time');
plt.ylabel('Noise')
plt.show()

``` 
In principle, this for-loop can be a lot more complex and behave differently, 
depending on readings from various instruments or user input.