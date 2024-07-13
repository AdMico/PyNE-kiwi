"""
Brought to PyNE-wells v1.1.0 on Thu Nov 1 2023 by APM

@developers: Adam Micolich, Jan Gluschke & Shuji Kojima

@author: Jakob Seidl

This module reads, supplies and updates the current 'measurement ID', a running number on each setup.
A two letter identifier of each setup, e.g., EL for Electronics Lab, MS for Microscope, is also saved in this file.
Both are read in the sweep function sweepAndSave() each time a measurement is done.
"""

import os
import json

# This has to be set every time pyNe is installed on a new system. It denotes the path where the unique number is saved.
relPath = os.path.realpath(__file__)[:-15] #Giving the full path without the GlobalMeasID.py script ending
filePath =  relPath + 'GlobalMeasIDBinary'

Reset = 1 #Switch to enable/disable running of this .py from reseting the ID number. Default as 1 for code download but you probably want to set to 0 once you've initialised the GMID to prevent accidental GMID reset.

def initID(preFix = 'TE',ID= 1): ## Routine initialises the Global Measurement ID (GMID). See bottom of code for running as main. The string and starting number are specified here though.
    """ Initializes a new preFix dictionary with the default prefix 'EL' and a running ID of zero."""
    with open(filePath, 'w') as file:
     file.write(json.dumps({'currentPreFix':preFix,preFix:ID
                           }))

def  addPrefix(newPreFix):
    with open(filePath, 'r') as file:
        inputDic=  json.loads(file.read())
        inputDic = {newPreFix:0,**inputDic}
    with open(filePath, 'w') as file:
        file.write(json.dumps(inputDic))
        print(f'Succesfully added the new measurement preFix/Setup: {newPreFix}')

def readCurrentID():
    """ Reads current measurement ID running number.
    Returns
    ----------
    ID : int
    """
    with open(filePath, 'r') as file:
        Dict = json.loads(file.read())
        return Dict[Dict['currentPreFix']]

def listIDs():
    """ Lists all available measurement ID prefixes and running numbers. """

    with open(filePath, 'r') as file:
        Dict = json.loads(file.read())
        current = f"Currently used Prefix/Setup: {Dict['currentPreFix']}  --> ID = {Dict[Dict['currentPreFix']]}"
        print(current+f"\n{'-'*len(current)} \nOther available Setups/Prefixes are: ")
        retString = ''
        retString = retString.join(current+'\n')
        for key,item in Dict.items():
            if (key !='currentPreFix' and key != Dict['currentPreFix']):
                print(f"Prefix/Setup: {key}  --> ID = {item}")
                retString = retString.join(f"Prefix/Setup: {key}  --> ID = {item}\n")

def increaseID():
    """ Increments currently used measurement ID (int) by one. """
    with open(filePath, 'r') as file:
        inputDic=  json.loads(file.read())
        inputDic[inputDic['currentPreFix']] = str(int(inputDic[inputDic['currentPreFix']]) + 1)
    with open(filePath, 'w') as file:
        file.write(json.dumps(inputDic))

def setCurrentSetup(preFix):
    """ Sets currently used measurement prefix to preFix.

     Parameters
     ----------
     preFix : str
              Must be a string prefix that has previously been defined via the addPrefix('preFix') method.

     """
    with open(filePath, 'r') as file:
        Dict = json.loads(file.read())
        previousPrefix = Dict['currentPreFix']
    if preFix in Dict.keys():

        if previousPrefix == preFix:
            print(f'Using current Id/Prefix: {previousPrefix}')
            pass
        else:
            Dict['currentPreFix'] = preFix
            with open(filePath, 'w') as file:
                file.write(json.dumps(Dict))
                print(f'Succesfully changed preFix/Setup from: {previousPrefix} ---> {preFix}')
    else:
        print(listIDs())
        raise Exception(f'Prefix not defined!!\n Currently defined prefixes can be listed by usign the listIDs() function.\n Define the desired prefix first using the addPrefix(newPrefix) method')

def readCurrentSetup():
    """ Reads current measurement prefix

    Returns
    ----------
    preFix : str
    """
    with open(filePath, 'r') as file:
        Dict=  json.loads(file.read())
        return Dict['currentPreFix']

if __name__ == "__main__": # Code below will run if this file is run as main (i.e., it will initialise the GMID to your specified values at the function definition if Reset = 1)
    if Reset == 1:
        initID()