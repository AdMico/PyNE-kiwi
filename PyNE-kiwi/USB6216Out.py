"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Adam Micolich

This module does the output handling for the USB-6216, which is effectively a pair of analog outputs
and a set of 8 analog inputs. The input handling is done by a separate .py. There is a settable option for 
where the voltage feedback comes from. The default feedback is internal, i.e., USB-6216 reads back what it
is putting out via an internal connection. The alternative is to T- off to a spare input (e.g., ai7) and 
direct read. 
"""

import Instrument
import nidaqmx as nmx
import time
import numpy as np

@Instrument.enableOptions
class USB6216Out(Instrument.Instrument):
    # Default options to set/get when the instrument is passed into the sweeper
    defaultInput = "outputLevel"
    defaultOutput = "outputLevel"
    defaultFeedBack = "Int"

    def __init__(self, address):
        super(USB6216Out, self).__init__()
        self.dev = address
        self.type ="USB6216"  #We can check each instrument for its type and react accordingly
        self.name = "myUSB6216"
        if self.dev == 0:
            self.port = "Dev1/ao0"
            self.fbp = "Dev1/_ao0_vs_aognd"
        elif self.dev == 1:
            self.port = "Dev1/ao1"
            self.fbp = "Dev1/_ao1_vs_aognd"
        
    @Instrument.addOptionSetter("name")
    def _setName(self,instrumentName):
         self.name = instrumentName
         
    @Instrument.addOptionGetter("name")
    def _getName(self):
        return self.name

    @Instrument.addOptionSetter("outputLevel")
    def _setOutputLevel(self,outputLevel):
        if (10.0 >= outputLevel and outputLevel >= -10.0):
            self.output = outputLevel
            with nmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(self.port)
                task.write(outputLevel)
        else:
            raise ValueError("Output outside 10V range available".format(outputLevel))
                
    @Instrument.addOptionGetter("outputLevel")
    def _getOutputLevel(self):
        with nmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(self.fbp)
            outputLevel = task.read()
        return outputLevel
        
    @Instrument.addOptionGetter("feedBack")
    def _getScaleFactor(self):
        return self.feedBack

    @Instrument.addOptionSetter("feedBack")
    def _setFeedBack(self,feedBack):
        self.feedBack = feedBack
    
    @Instrument.addOptionSetter("extPort")
    def _setExtPort(self,extPort):
        self.extPort = extPort
        if self.feedBack == "Int":
            if self.dev == 0:
                self.fbp = "Dev1/_ao0_vs_aognd"
            elif self.dev == 1:
                self.fbp = "Dev1/_ao1_vs_aognd"
        elif self.feedBack == "Ext":
            if self.extPort == 0:
                self.fbp = "Dev1/ai0"
            elif self.extPort == 1:
                self.fbp = "Dev1/ai1"
            elif self.extPort == 2:
                self.fbp = "Dev1/ai2"
            elif self.extPort == 3:
                self.fbp = "Dev1/ai3"
            elif self.extPort == 4:
                self.fbp = "Dev1/ai4"
            elif self.extPort == 5:
                self.fbp = "Dev1/ai5"
            elif self.extPort == 6:
                self.fbp = "Dev1/ai6"
            elif self.extPort == 7:
                self.fbp = "Dev1/ai7"

    @Instrument.addOptionGetter("extPort")
    def _getExtPort(self):
        return self.fbp

    @Instrument.addOptionGetter("scaleFactor")
    def _getScaleFactor(self):
        return self.scaleFactor
    
    @Instrument.addOptionSetter("scaleFactor")
    def _setScaleFactor(self,scaleFactor):
        self.scaleFactor = scaleFactor
            
    def goTo(self,target,stepsize = 0.01,delay = 0.001): # Modified from usual as APM likes linspace better
        currentOutput = self.get("outputLevel")
        count = int(abs(target-currentOutput)/stepsize) + 1
        sweepArray = np.linspace(currentOutput,target,count,endpoint=True)
        if count < 3: #Option to avoid pointless sweeps, if you're close enough, just go direct
            with nmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(self.port)
                task.write(target)
        else:
            for point in sweepArray:
                with nmx.Task() as task:
                    task.ao_channels.add_ao_voltage_chan(self.port)
                    task.write(point)
                time.sleep(delay)
            with nmx.Task() as task:
                task.ao_channels.add_ao_voltage_chan(self.port)
                task.write(target)
            
    def close(self):
        pass