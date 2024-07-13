"""
Brought to PyNE-wells v1.1.0 on Wed Apr 17 2024 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

This class sets up the Pi to be controlled remotely. The truth table is that of the multiplexer.
"""
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
from Config import PiBox, MuxMode
import pigpio
import time

class PiMUX:

    def __init__(self):
        if PiBox == 'MeasureOne':
            IP = '149.171.105.34' #IP changed for Lowy APM 25MAR24, was 129.94.163.203 on VLAN334 (Physics)
        if PiBox == 'MeasureTwo':
            IP = '129.94.163.167'
        if PiBox == 'MeasureThree':
            IP = '129.94.163.75'
        self.IP = IP
        #print(IP) -- For PiBox testing
        self.PiFactory = PiGPIOFactory(host=self.IP)

        #DeviceTable format: Device: [A3,A2,A1,A0,EN1,EN2,EN3,EN4], #MUX <number> Pin <number> (Mx <number> out of 16)
        self.DeviceTable = {0: [0, 0, 0, 0, 0, 0, 0, 0],  # OFF state
                            1: [0, 0, 0, 0, 1, 0, 0, 0],  # MUX 1 Pin 19 (Mx1)
                            2: [0, 0, 0, 1, 1, 0, 0, 0],  # MUX 1 Pin 20 (Mx2)
                            3: [0, 0, 1, 0, 1, 0, 0, 0],  # MUX 1 Pin 21 (Mx3)
                            4: [0, 0, 1, 1, 1, 0, 0, 0],  # MUX 1 Pin 22 (Mx4)
                            5: [0, 1, 0, 0, 1, 0, 0, 0],  # MUX 1 Pin 23 (Mx5)
                            6: [0, 1, 0, 1, 1, 0, 0, 0],  # MUX 1 Pin 24 (Mx6)
                            7: [0, 1, 1, 0, 1, 0, 0, 0],  # MUX 1 Pin 25 (Mx7)
                            8: [0, 1, 1, 1, 1, 0, 0, 0],  # MUX 1 Pin 26 (Mx8)
                            9: [1, 0, 0, 0, 1, 0, 0, 0],  # MUX 1 Pin 11 (Mx9)
                            10: [1, 0, 0, 1, 1, 0, 0, 0],  # MUX 1 Pin 10 (Mx10)
                            11: [1, 0, 1, 0, 1, 0, 0, 0],  # MUX 1 Pin 9 (Mx11)
                            12: [1, 0, 1, 1, 1, 0, 0, 0],  # MUX 1 Pin 8 (Mx12)
                            13: [1, 1, 0, 0, 1, 0, 0, 0],  # MUX 1 Pin 7 (Mx13)
                            14: [0, 0, 0, 0, 0, 1, 0, 0],  # MUX 2 Pin 19 (Mx1)
                            15: [0, 0, 0, 1, 0, 1, 0, 0],  # MUX 2 Pin 20 (Mx2)
                            16: [0, 0, 1, 0, 0, 1, 0, 0],  # MUX 2 Pin 21 (Mx3)
                            17: [0, 0, 1, 1, 0, 1, 0, 0],  # MUX 2 Pin 22 (Mx4)
                            18: [0, 1, 0, 0, 0, 1, 0, 0],  # MUX 2 Pin 23 (Mx5)
                            19: [0, 1, 0, 1, 0, 1, 0, 0],  # MUX 2 Pin 24 (Mx6)
                            20: [0, 1, 1, 0, 0, 1, 0, 0],  # MUX 2 Pin 25 (Mx7)
                            21: [0, 1, 1, 1, 0, 1, 0, 0],  # MUX 2 Pin 26 (Mx8)
                            22: [1, 0, 0, 0, 0, 1, 0, 0],  # MUX 2 Pin 11 (Mx9)
                            23: [1, 0, 0, 1, 0, 1, 0, 0],  # MUX 2 Pin 10 (Mx10)
                            24: [1, 0, 1, 0, 0, 1, 0, 0],  # MUX 2 Pin 9 (Mx11)
                            25: [1, 0, 1, 1, 0, 1, 0, 0],  # MUX 2 Pin 8 (Mx12)
                            26: [1, 1, 0, 0, 0, 1, 0, 0],  # MUX 2 Pin 7 (Mx13)
                            27: [0, 0, 0, 0, 0, 0, 1, 0],  # MUX 3 Pin 19 (Mx1)
                            28: [0, 0, 0, 1, 0, 0, 1, 0],  # MUX 3 Pin 20 (Mx2)
                            29: [0, 0, 1, 0, 0, 0, 1, 0],  # MUX 3 Pin 21 (Mx3)
                            30: [0, 0, 1, 1, 0, 0, 1, 0],  # MUX 3 Pin 22 (Mx4)
                            31: [0, 1, 0, 0, 0, 0, 1, 0],  # MUX 3 Pin 23 (Mx5)
                            32: [0, 1, 0, 1, 0, 0, 1, 0],  # MUX 3 Pin 24 (Mx6)
                            33: [0, 1, 1, 0, 0, 0, 1, 0],  # MUX 3 Pin 25 (Mx7)
                            34: [0, 1, 1, 1, 0, 0, 1, 0],  # MUX 3 Pin 26 (Mx8)
                            35: [1, 0, 0, 0, 0, 0, 1, 0],  # MUX 3 Pin 11 (Mx9)
                            36: [1, 0, 0, 1, 0, 0, 1, 0],  # MUX 3 Pin 10 (Mx10)
                            37: [1, 0, 1, 0, 0, 0, 1, 0],  # MUX 3 Pin 9 (Mx11)
                            38: [1, 0, 1, 1, 0, 0, 1, 0],  # MUX 3 Pin 8 (Mx12)
                            39: [1, 1, 0, 0, 0, 0, 1, 0],  # MUX 3 Pin 7 (Mx13)
                            40: [0, 0, 0, 0, 0, 0, 0, 1],  # MUX 4 Pin 19 (Mx1)
                            41: [0, 0, 0, 1, 0, 0, 0, 1],  # MUX 4 Pin 20 (Mx2)
                            42: [0, 0, 1, 0, 0, 0, 0, 1],  # MUX 4 Pin 21 (Mx3)
                            43: [0, 0, 1, 1, 0, 0, 0, 1],  # MUX 4 Pin 22 (Mx4)
                            44: [0, 1, 0, 0, 0, 0, 0, 1],  # MUX 4 Pin 23 (Mx5)
                            45: [0, 1, 0, 1, 0, 0, 0, 1],  # MUX 4 Pin 24 (Mx6)
                            46: [0, 1, 1, 0, 0, 0, 0, 1],  # MUX 4 Pin 25 (Mx7)
                            47: [0, 1, 1, 1, 0, 0, 0, 1],  # MUX 4 Pin 26 (Mx8)
                            48: [1, 0, 0, 0, 0, 0, 0, 1],  # MUX 4 Pin 11 (Mx9)
                            49: [1, 0, 0, 1, 0, 0, 0, 1],  # MUX 4 Pin 10 (Mx10)
                            50: [1, 0, 1, 0, 0, 0, 0, 1],  # MUX 4 Pin 9 (Mx11)
                            51: [1, 0, 1, 1, 0, 0, 0, 1],  # MUX 4 Pin 8 (Mx12)
                            52: [1, 1, 0, 0, 0, 0, 0, 1]}  # MUX 4 Pin 7 (Mx13)

        # RowTable format: Row: [A3,A2,A1,A0,EN1,EN2,EN3,EN4], #Dev <number>/<number> MUX <number> & <number>
        self.RowTable = {0: [0, 0, 0, 0, 0, 0, 0, 0],  # OFF state
                         1: [0, 0, 0, 0, 1, 0, 1, 0],  # Dev 1/27 MUX 1-19 & 3-19
                         2: [0, 0, 0, 1, 1, 0, 1, 0],  # Dev 2/28 MUX 1-20 & 3-20
                         3: [0, 0, 1, 0, 1, 0, 1, 0],  # Dev 3/29 MUX 1-21 & 3-21
                         4: [0, 0, 1, 1, 1, 0, 1, 0],  # Dev 4/30 MUX 1-22 & 3-22
                         5: [0, 1, 0, 0, 1, 0, 1, 0],  # Dev 5/31 MUX 1-23 & 3-23
                         6: [0, 1, 0, 1, 1, 0, 1, 0],  # Dev 6/32 MUX 1-24 & 3-24
                         7: [0, 1, 1, 0, 1, 0, 1, 0],  # Dev 7/33 MUX 1-25 & 3-25
                         8: [0, 1, 1, 1, 1, 0, 1, 0],  # Dev 8/34 MUX 1-26 & 3-26
                         9: [1, 0, 0, 0, 1, 0, 1, 0],  # Dev 9/35 MUX 1-11 & 3-11
                         10: [1, 0, 0, 1, 1, 0, 1, 0],  # Dev 10/36 MUX 1-10 & 3-10
                         11: [1, 0, 1, 0, 1, 0, 1, 0],  # Dev 11/37 MUX 1-9 & 3-9
                         12: [1, 0, 1, 1, 1, 0, 1, 0],  # Dev 12/38 MUX 1-8 & 3-8
                         13: [1, 1, 0, 0, 1, 0, 1, 0],  # Dev 13/39 MUX 1-7 & 3-7
                         14: [0, 0, 0, 0, 0, 1, 0, 1],  # Dev 14/40 MUX 2-19 & 4-19
                         15: [0, 0, 0, 1, 0, 1, 0, 1],  # Dev 15/41 MUX 2-20 & 4-20
                         16: [0, 0, 1, 0, 0, 1, 0, 1],  # Dev 16/42 MUX 2-21 & 4-21
                         17: [0, 0, 1, 1, 0, 1, 0, 1],  # Dev 17/43 MUX 2-22 & 4-22
                         18: [0, 1, 0, 0, 0, 1, 0, 1],  # Dev 18/44 MUX 2-23 & 4-23
                         19: [0, 1, 0, 1, 0, 1, 0, 1],  # Dev 19/45 MUX 2-24 & 4-24
                         20: [0, 1, 1, 0, 0, 1, 0, 1],  # Dev 20/46 MUX 2-25 & 4-25
                         21: [0, 1, 1, 1, 0, 1, 0, 1],  # Dev 21/47 MUX 2-26 & 4-26
                         22: [1, 0, 0, 0, 0, 1, 0, 1],  # Dev 22/48 MUX 2-11 & 4-11
                         23: [1, 0, 0, 1, 0, 1, 0, 1],  # Dev 23/49 MUX 2-10 & 4-10
                         24: [1, 0, 1, 0, 0, 1, 0, 1],  # Dev 24/50 MUX 2-9 & 4-9
                         25: [1, 0, 1, 1, 0, 1, 0, 1],  # Dev 25/51 MUX 2-8 & 4-8
                         26: [1, 1, 0, 0, 0, 1, 0, 1]}  # Dev 26/52 MUX 2-7 & 4-7

        #Define what GPIO pins are connected to the selector pins on the MUX

        self.E1_pin = LED(6,pin_factory = self.PiFactory)
        self.E2_pin = LED(13,pin_factory = self.PiFactory)
        self.E3_pin = LED(19,pin_factory = self.PiFactory)
        self.E4_pin = LED(26,pin_factory = self.PiFactory)

        self.A0_pin = LED(12,pin_factory = self.PiFactory)
        self.A1_pin = LED(16,pin_factory = self.PiFactory)
        self.A2_pin = LED(20,pin_factory = self.PiFactory)
        self.A3_pin = LED(21,pin_factory = self.PiFactory)

        self.ROn_pin = LED(7,pin_factory = self.PiFactory)
        self.ROff_pin = LED(8,pin_factory = self.PiFactory)

        self.listPins = [self.A3_pin,self.A2_pin,self.A1_pin,self.A0_pin,self.E1_pin,self.E2_pin,self.E3_pin,self.E4_pin]

        #Uses truthtables to set GPIO pin voltages to activate desired output.

    def setMuxToOutput(self, desiredOutput):
        if MuxMode == 'Test':
            for index, item in enumerate(self.listPins):
                if self.DeviceTable[desiredOutput][index]:
                    item.on()
                else:
                    item.off()
        elif MuxMode == 'Run':
            for index, item in enumerate(self.listPins):
                if self.RowTable[desiredOutput][index]:
                    item.on()
                else:
                    item.off()

    def setRelayToOn(self): # Turns the power circuit relay on to power up the MUXes -- APM 26FEB24
        self.ROn_pin.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.ROn_pin.off()

    def setRelayToOff(self): # Turns the power circuit relay off to power down the MUXes -- APM 26FEB24
        self.ROff_pin.on()
        time.sleep(0.001) # Tested at 1ms wait being ok APM 26Feb24
        self.ROff_pin.off()

if __name__ == "__main__": # execute only if this script is run, not when it's being imported -- Code will switch on the power relay, set the MUX to the disconnected state and switch the power relay back off.
    my_pi = PiMUX()
    my_pi.setRelayToOn() # comment to switch on/off as needed.
    my_pi.setMuxToOutput(0) #0 here will disconnect, can specify other truth-table settings for direct connection accordingly.
    my_pi.setRelayToOff() # comment to switch on/off as needed.