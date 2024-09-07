"""
Brought to PyNE-kiwi v1.0.0 on Mon Sep 2 2024 by APM

@developers: Adam Micolich

@author: Adam Micolich

A set of higher level routines for B1500 (i.e., above the usual instrument level for PyNE)
"""

from Config import Diags
import KeysightB1500A

@B1500.Initialisation
def B1500_init():
    # Hook up instrument communications connection
    B1500 = KeysightB1500A('USB0::0x0957::0x0001::0001::INSTR', read_termination='\r\n', write_termination='\r\n', timeout=3000)
    # Get ID from B1500 to check communications function
    if Diags == "Verbose":
        print('B1500 ID: ',B1500.id)
    # SMU initialization is required to be able to address single SMUs
    B1500.initialize_all_smus()
    # Ensure all four SMUs are zeroed
    B1500.smu1.force('Voltage','Auto Ranging',0.0)
    B1500.smu2.force('Voltage','Auto Ranging',0.0)
    B1500.smu3.force('Voltage','Auto Ranging',0.0)
    B1500.smu4.force('Voltage','Auto Ranging',0.0)
    # Enable all four SMUs
    B1500.smu1.enable()
    B1500.smu2.enable()
    B1500.smu3.enable()
    B1500.smu4.enable()