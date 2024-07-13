"""
Brought to PyNE-wells v1.0.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

This class sets up the Pi to be controlled remotely. The truth table is that of the multiplexer.
"""
from gpiozero import LED
from gpiozero.pins.pigpio import PiGPIOFactory
from Config import PiBox, MuxMode

class PiMUX:

    def __init__(self):
        if PiBox == 'MeasureOne':
            IP = '129.94.163.203'
        if PiBox == 'MeasureTwo':
            IP = '129.94.163.167'
        self.IP = IP
        #print(IP) -- For PiBox testing
        self.PiFactory = PiGPIOFactory(host=self.IP)

        #DeviceTable format: Device: [A3,A2,A1,A0,EN1,EN2,EN3,EN4], #MUX <number> Pin <number> (Mx <number> out of 16)
        self.DeviceTable = {0: [0, 0, 0, 0, 0, 0, 0, 0],  #OFF state
                           1: [1, 1, 0, 0, 0, 1, 0, 0],  # MUX 2 Pin 7 (Mx13)
                           2: [1, 0, 1, 1, 0, 1, 0, 0],  # MUX 2 Pin 8 (Mx12)
                           3: [1, 0, 1, 0, 0, 1, 0, 0],  # MUX 2 Pin 9 (Mx11)
                           4: [1, 0, 0, 1, 0, 1, 0, 0],  # MUX 2 Pin 10 (Mx10)
                           5: [1, 0, 0, 0, 0, 1, 0, 0],  # MUX 2 Pin 11 (Mx9)
                           6: [0, 1, 1, 1, 0, 1, 0, 0],  # MUX 2 Pin 26 (Mx8)
                           7: [0, 1, 1, 0, 0, 1, 0, 0],  # MUX 2 Pin 25 (Mx7)
                           8: [0, 1, 0, 1, 0, 1, 0, 0],  # MUX 2 Pin 24 (Mx6)
                           9: [0, 1, 0, 0, 0, 1, 0, 0],  # MUX 2 Pin 23 (Mx5)
                           10: [0, 0, 1, 1, 0, 1, 0, 0],  # MUX 2 Pin 22 (Mx4)
                           11: [0, 0, 1, 0, 0, 1, 0, 0],  # MUX 2 Pin 21 (Mx3)
                           12: [0, 0, 0, 1, 0, 1, 0, 0],  # MUX 2 Pin 20 (Mx2)
                           13: [0, 0, 0, 0, 0, 1, 0, 0],  # MUX 2 Pin 19 (Mx1)
                           14: [1, 1, 0, 0, 1, 0, 0, 0],  # MUX 1 Pin 7 (Mx13)
                           15: [1, 0, 1, 1, 1, 0, 0, 0],  # MUX 1 Pin 8 (Mx12)
                           16: [1, 0, 1, 0, 1, 0, 0, 0],  # MUX 1 Pin 9 (Mx11)
                           17: [1, 0, 0, 1, 1, 0, 0, 0],  # MUX 1 Pin 10 (Mx10)
                           18: [1, 0, 0, 0, 1, 0, 0, 0],  # MUX 1 Pin 11 (Mx9)
                           19: [0, 1, 1, 1, 1, 0, 0, 0],  # MUX 1 Pin 26 (Mx8)
                           20: [0, 1, 1, 0, 1, 0, 0, 0],  # MUX 1 Pin 25 (Mx7)
                           21: [0, 1, 0, 1, 1, 0, 0, 0],  # MUX 1 Pin 24 (Mx6)
                           22: [0, 1, 0, 0, 1, 0, 0, 0],  # MUX 1 Pin 23 (Mx5)
                           23: [0, 0, 1, 1, 1, 0, 0, 0],  # MUX 1 Pin 22 (Mx4)
                           24: [0, 0, 1, 0, 1, 0, 0, 0],  # MUX 1 Pin 21 (Mx3)
                           25: [0, 0, 0, 1, 1, 0, 0, 0],  # MUX 1 Pin 20 (Mx2)
                           26: [0, 0, 0, 0, 1, 0, 0, 0],  # MUX 1 Pin 19 (Mx1)
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
                        1: [1, 1, 0, 0, 0, 1, 0, 1],  # Dev 1/52 MUX 2-7 & 4-7
                        2: [1, 0, 1, 1, 0, 1, 0, 1],  # Dev 2/51 MUX 2-8 & 4-8
                        3: [1, 0, 1, 0, 0, 1, 0, 1],  # Dev 3/50 MUX 2-9 & 4-9
                        4: [1, 0, 0, 1, 0, 1, 0, 1],  # Dev 4/49 MUX 2-10 & 4-10
                        5: [1, 0, 0, 0, 0, 1, 0, 1],  # Dev 5/48 MUX 2-11 & 4-11
                        6: [0, 1, 1, 1, 0, 1, 0, 1],  # Dev 6/47 MUX 2-26 & 4-26
                        7: [0, 1, 1, 0, 0, 1, 0, 1],  # Dev 7/46 MUX 2-25 & 4-25
                        8: [0, 1, 0, 1, 0, 1, 0, 1],  # Dev 8/45 MUX 2-24 & 4-24
                        9: [0, 1, 0, 0, 0, 1, 0, 1],  # Dev 9/44 MUX 2-23 & 4-23
                        10: [0, 0, 1, 1, 0, 1, 0, 1],  # Dev 10/43 MUX 2-22 & 4-22
                        11: [0, 0, 1, 0, 0, 1, 0, 1],  # Dev 11/42 MUX 2-21 & 4-21
                        12: [0, 0, 0, 1, 0, 1, 0, 1],  # Dev 12/41 MUX 2-20 & 4-20
                        13: [0, 0, 0, 0, 0, 1, 0, 1],  # Dev 13/40 MUX 2-19 & 4-19
                        14: [1, 1, 0, 0, 1, 0, 1, 0],  # Dev 14/39 MUX 1-7 & 3-7
                        15: [1, 0, 1, 1, 1, 0, 1, 0],  # Dev 15/38 MUX 1-8 & 3-8
                        16: [1, 0, 1, 0, 1, 0, 1, 0],  # Dev 16/37 MUX 1-9 & 3-9
                        17: [1, 0, 0, 1, 1, 0, 1, 0],  # Dev 17/36 MUX 1-10 & 3-10
                        18: [1, 0, 0, 0, 1, 0, 1, 0],  # Dev 18/35 MUX 1-11 & 3-11
                        19: [0, 1, 1, 1, 1, 0, 1, 0],  # Dev 19/34 MUX 1-26 & 3-26
                        20: [0, 1, 1, 0, 1, 0, 1, 0],  # Dev 20/33 MUX 1-25 & 3-25
                        21: [0, 1, 0, 1, 1, 0, 1, 0],  # Dev 21/32 MUX 1-24 & 3-24
                        22: [0, 1, 0, 0, 1, 0, 1, 0],  # Dev 22/31 MUX 1-23 & 3-23
                        23: [0, 0, 1, 1, 1, 0, 1, 0],  # Dev 23/30 MUX 1-22 & 3-22
                        24: [0, 0, 1, 0, 1, 0, 1, 0],  # Dev 24/29 MUX 1-21 & 3-21
                        25: [0, 0, 0, 1, 1, 0, 1, 0],  # Dev 25/28 MUX 1-20 & 3-20
                        26: [0, 0, 0, 0, 1, 0, 1, 0]}  # Dev 26/27 MUX 1-19 & 3-19

        #Define what GPIO pins are connected to the selector pins on the MUX

        self.E1_pin = LED(6,pin_factory = self.PiFactory)
        self.E2_pin = LED(13,pin_factory = self.PiFactory)
        self.E3_pin = LED(19,pin_factory = self.PiFactory)
        self.E4_pin = LED(26,pin_factory = self.PiFactory)

        self.A0_pin = LED(12,pin_factory = self.PiFactory)
        self.A1_pin = LED(16,pin_factory = self.PiFactory)
        self.A2_pin = LED(20,pin_factory = self.PiFactory)
        self.A3_pin = LED(21,pin_factory = self.PiFactory)

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

if __name__ == "__main__": # execute only if this script is run, not when it's being imported
    my_pi = PiMUX()
    my_pi.setMuxToOutput(0)