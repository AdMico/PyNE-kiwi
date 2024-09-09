"""
Brought to PyNE-kiwi v1.0.0 on Mon Sep 2 2024 by APM

@developers: Adam Micolich

@author: Adam Micolich

A set of higher level routines for B2201 (i.e., above the usual instrument level for PyNE)
"""

import pyvisa
from Config import Diags

@B2201.Initialisation
def B2201_init():
    # Hook up instrument communications connection
    rm = pyvisa.ResourceManager()
    B2201 = rm.open_resource('GPIB0::22::INSTR')
    # Get ID from B2201 to check communications function
    if Diags == "Verbose":
        print('B2201 ID: ',B2201.query("*IDN?"))
    # Set B2201 Settings
    B2201.write(":ROUT:FUNC NCON")
    B2201.write(":ROUT:CONN:RULE 1,FREE")
    B2201.write(":ROUT:CONN:SEQ 1,BBM")
    # Set B2201 to all relays open
    B2201.write(":ROUT:OPEN:CARD 1")

@B2201.even
def B2201_even():
    B2201.write(":ROUT:OPEN:CARD 1") # Need to reset card before setting new values -- APM 08SEP24
    B2201.write(":ROUT:CLOS (@11001,10102,11003,10204,11005,10306,11007,10408,10909,10910,10911,10912)")

@B2201.odd
def B2201_odd():
    B2201.write(":ROUT:OPEN:CARD 1")  # Need to reset card before setting new values -- APM 08SEP24
    B2201.write(":ROUT:CLOS (@10101,11002,10203,11004,10305,11006,10407,11008,10909,10910,10911,10912)")

@B2201.ground
def B2201_ground():
    B2201.write(":ROUT:OPEN:CARD 1")  # Need to reset card before setting new values -- APM 08SEP24
    B2201.write(":ROUT:CLOS (@11001,11002,11003,11004,11005,11006,11007,11008,10909,10910,10911,10912)")

@B2201.clear
def B2201_clear():
    B2201.write(":ROUT:OPEN:CARD 1")
