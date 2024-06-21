"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Jakob Seidl

This module reads, supplies and updates the current 'measurement ID', a running number on each setup.
A two letter identifier of each setup, e.g., AT for Attocube, Pr for probe station, He for Heliox  etc. is also saved in this file.
Both are read in the sweep function sweepAndSave() each time a measurement is done.
"""

IDpath='GlobalMeasIDBinary'
currentSetup = "Pr"  # Change this depending on what setup you use.

def readCurrentID():
        IDTXT = open(IDpath,"r")
        ID = int(IDTXT.read())
        IDTXT.close()
        return(ID) 
    
def increaseID():
        ID = readCurrentID()
        IDTXT = open(IDpath,"w")
        IDTXT.write(str(ID + 1))
        IDTXT.close() #Line added APM 6/8/19 to resolve unclosed file ResourceWarning.
     
def readCurrentSetup():
    return currentSetup
        
def init():
    """Creates a new ID file at the path specified in variable 'Idpath'. Should only be called if the ID file was deleted etc. """
    IDTXT = open(IDpath,"w")
    IDTXT.write(str(0))
    IDTXT.close() #Line added APM 6/8/19 to resolve unclosed file ResourceWarning.