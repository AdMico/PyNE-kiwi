"""
Brought to PyNE-kiwi v1.0.0 on Mon Sep 2 2024 by APM

@developers: Adam Micolich

@author: Adam Micolich

A set of higher level routines for B2201 (i.e., above the usual instrument level for PyNE)
"""

import pyvisa

class B2201():
    def __init__(self):
        super(B2201, self).__init__()
        self.dev = pyvisa.ResourceManager().open_resource("GPIB0::22::INSTR")
        print((self.dev.query("*IDN?"))) # Probably should query and check we have the right device
        self.type ="B2201"  #We can check each instrument for its type and react accordingly

    def B2201_init(self):
        # Set B2201 Settings
        self.dev.write(":ROUT:FUNC NCON")
        self.dev.write(":ROUT:CONN:RULE 1,FREE")
        self.dev.write(":ROUT:CONN:SEQ 1,BBM")
        # Set B2201 to all relays open
        self.dev.write(":ROUT:OPEN:CARD 1")

    def B2201_even(self):
        self.dev.write(":ROUT:OPEN:CARD 1") # Need to reset card before setting new values -- APM 08SEP24
        self.dev.write(":ROUT:CLOS (@11001,10102,11003,10204,11005,10306,11007,10408,10909,10910,10911,10912)")

    def B2201_odd(self):
        self.dev.write(":ROUT:OPEN:CARD 1")  # Need to reset card before setting new values -- APM 08SEP24
        self.dev.write(":ROUT:CLOS (@10101,11002,10203,11004,10305,11006,10407,11008,10909,10910,10911,10912)")

    def B2201_ground(self):
        self.dev.write(":ROUT:OPEN:CARD 1")  # Need to reset card before setting new values -- APM 08SEP24
        self.dev.write(":ROUT:CLOS (@11001,11002,11003,11004,11005,11006,11007,11008,10909,10910,10911,10912)")

    def B2201_clear(self):
        self.dev.write(":ROUT:OPEN:CARD 1")
