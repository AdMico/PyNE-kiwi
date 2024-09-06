"""
Brought to PyNE-kiwi v1.0.0 on Fri Aug 30 2024 by APM

@developers: Adam Micolich

@author: Jan Gluschke & Adam Micolich

This class sets up the Pi to be controlled remotely for running the switch relays on the probe-arm.
"""
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
from Config import PiBox
import time

class PiMUX:

    def __init__(self):
        if PiBox == 'MeasureThree':
            IP = '129.94.163.75'
        if PiBox == 'WellyPi':
            IP = '10.155.128.34'
        self.IP = IP
        self.PiFactory = PiGPIOFactory(host=self.IP)

        #Define the GPIO pin to raise to switch the given device onto SMB connector

        self.DP9 = LED(8,pin_factory = self.PiFactory)  #Will activate D9 and deactivate D10 to SMB #9 -- Revert to Pin 7 at V2 Hardware update APM 30AUG24
        self.DP10 = LED(7,pin_factory = self.PiFactory) #Will activate D10 and deactivate D9 to SMB #9 -- Revert to Pin 8 at V2 Hardware update APM 30AUG24
        self.DP11 = LED(6,pin_factory = self.PiFactory) #Will activate D11 and deactivate D12 to SMB #10 -- Revert to Pin 5 at V2 Hardware update APM 30AUG24
        self.DP12 = LED(5,pin_factory = self.PiFactory) #Will activate D12 and deactivate D11 to SMB #10 -- Revert to Pin 6 at V2 Hardware update APM 30AUG24
        self.DP13 = LED(4,pin_factory = self.PiFactory) #Will activate D13 and deactivate D14 to SMB #11 -- Revert to Pin 3 at V2 Hardware update APM 30AUG24
        self.DP14 = LED(3,pin_factory = self.PiFactory) #Will activate D14 and deactivate D13 to SMB #11 -- Revert to Pin 4 at V2 Hardware update APM 30AUG24
        self.DP15 = LED(2,pin_factory = self.PiFactory) #Will activate D15 and deactivate D16 to SMB #12 -- Revert to Pin 9 at V2 Hardware update APM 30AUG24
        self.DP16 = LED(9,pin_factory = self.PiFactory) #Will activate D16 and deactivate D15 to SMB #12 -- Revert to Pin 2 at V2 Hardware update APM 30AUG24

        self.listPins = [self.DP9,self.DP10,self.DP11,self.DP12,self.DP13,self.DP14,self.DP15,self.DP16] #May not have use -- consider deprecating.

    def DP9on(self): # Switches the connection to SMB #9 to Device Pin 9 -- APM 30AUG24
        self.DP9.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.DP9.off()

    def DP10on(self): # Switches the connection to SMB #9 to Device Pin 10 -- APM 30AUG24
        self.DP10.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.DP10.off()

    def DP11on(self): # Switches the connection to SMB #10 to Device Pin 11 -- APM 30AUG24
        self.DP11.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.DP11.off()

    def DP12on(self): # Switches the connection to SMB #10 to Device Pin 12 -- APM 30AUG24
        self.DP12.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.DP12.off()

    def DP13on(self): # Switches the connection to SMB #11 to Device Pin 13 -- APM 30AUG24
        self.DP13.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.DP13.off()

    def DP14on(self): # Switches the connection to SMB #11 to Device Pin 14 -- APM 30AUG24
        self.DP14.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.DP14.off()

    def DP15on(self): # Switches the connection to SMB #12 to Device Pin 15 -- APM 30AUG24
        self.DP15.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.DP15.off()

    def DP16on(self): # Switches the connection to SMB #12 to Device Pin 16 -- APM 30AUG24
        self.DP16.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.DP16.off()

    def DP_Odd(self): # Switches all the odd device pins to SMBs
        self.DP9on()
        self.DP11on()
        self.DP13on()
        self.DP15on()

    def DP_Even(self): # Switches all the even device pins to SMBs
        self.DP10on()
        self.DP12on()
        self.DP14on()
        self.DP16on()

if __name__ == "__main__": # execute only if this script is run, not when it's being imported
    my_pi = PiMUX()
    time.sleep(1.0)
    my_pi.DP_Odd() # comment to switch on/off as needed.
    time.sleep(1.5)
    my_pi.DP_Even()
    time.sleep(1.5)
    my_pi.DP_Odd()  # comment to switch on/off as needed.
    time.sleep(1.5)
    my_pi.DP_Even()
    time.sleep(1.5)
    my_pi.DP_Odd()  # comment to switch on/off as needed.
    time.sleep(1.5)
    my_pi.DP_Even()
    time.sleep(1.5)
    my_pi.DP_Odd()  # comment to switch on/off as needed.
    time.sleep(1.5)
    my_pi.DP_Even()