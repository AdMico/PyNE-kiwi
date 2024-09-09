"""
Brought to PyNE-kiwi v1.0.0 on Fri Aug 30 2024 by APM

@developers: Adam Micolich

@author: Adam Micolich

This informs various parts of the software about aspects of your bench setup. Edit as needed for your setup.
"""

from qcodes.instrument_drivers.Keysight.keysightb1500 import constants

## IMPORTANT -- You need to set PiBox correctly before you first use the software to avoid controlling someone else's hardware by mistake -- see main README.md file
# Information about which Raspberry Pi you are using (MeasureOne, MeasureTwo, etc)
# Details for the various Pis are in Pi_control.py
PiBox = 'WellyPi'

# Code Diagnostics Switch
# Use "Verbose" for information prints on and "Silent" to suppress.
Diags = "Verbose"

# PyNE-kiwi settings
basePath = '../data'

# B1500 Settings -- Global
B1500AutoZero = True
B1500ADCSet = "HighSpeed" #Alternatives are HighSpeed and HighRes
B1500NPLC = 1 #Takes values from 1 to 100 (Int)

# B1500 Settings -- SMU1 Specific
VS_SMU1 = 0.5 # Source bias for SMU 1 in volts for gate sweeps
B1500ICOM1 = 1e-3 #Compliance current in amps
B1500VMR1 = constants.VMeasRange.FIX_2V #Ideally AUTO, FIX_2V, FIX_0V5 or FIX_0V2 -- other values in constants but know what you're doing first
B1500IMR1 = constants.IMeasRange.AUTO #Ideally AUTO or MIN_100nA -- other values in constants but know what you're doing first
B1500VOR1 = constants.VOutputRange.AUTO #AUTO seems only good selection here as the MIN settings cap downwards not upward
B1500MCR1 = constants.IOutputRange.AUTO #Leave as AUTO
B1500MM1 = constants.MM.Mode.SPOT #Can't see any reasons to change from SPOT
B1500CMM1 = constants.CMM.Mode.COMPLIANCE_SIDE #COMPLIANCE_SIDE, FORCE_SIDE, CURRENT, VOLTAGE, CURRENT_AND_VOLTAGE are possible, best option to be determined
B1500Filt1 = False #Default is False, other option is True

# B1500 Settings -- SMU2 Specific
VS_SMU2 = 0.5 # Source bias for SMU 1 in volts for gate sweeps
B1500ICOM2 = 1e-3 #Compliance current in amps
B1500VMR2 = constants.VMeasRange.FIX_2V #Ideally AUTO, FIX_2V, FIX_0V5 or FIX_0V2 -- other values in constants but know what you're doing first
B1500IMR2 = constants.IMeasRange.AUTO #Ideally AUTO or MIN_100nA -- other values in constants but know what you're doing first
B1500VOR2 = constants.VOutputRange.AUTO #AUTO seems only good selection here as the MIN settings cap downwards not upward
B1500MCR2 = constants.IOutputRange.AUTO #Leave as AUTO
B1500MM2 = constants.MM.Mode.SPOT #Can't see any reasons to change from SPOT
B1500CMM2 = constants.CMM.Mode.COMPLIANCE_SIDE #COMPLIANCE_SIDE, FORCE_SIDE, CURRENT, VOLTAGE, CURRENT_AND_VOLTAGE are possible, best option to be determined
B1500Filt2 = False #Default is False, other option is True

# B1500 Settings -- SMU3 Specific
VS_SMU3 = 0.5 # Source bias for SMU 1 in volts for gate sweeps
B1500ICOM3 = 1e-3 #Compliance current in amps
B1500VMR3 = constants.VMeasRange.FIX_2V #Ideally AUTO, FIX_2V, FIX_0V5 or FIX_0V2 -- other values in constants but know what you're doing first
B1500IMR3 = constants.IMeasRange.AUTO #Ideally AUTO or MIN_100nA -- other values in constants but know what you're doing first
B1500VOR3 = constants.VOutputRange.AUTO #AUTO seems only good selection here as the MIN settings cap downwards not upward
B1500MCR3 = constants.IOutputRange.AUTO #Leave as AUTO
B1500MM3 = constants.MM.Mode.SPOT #Can't see any reasons to change from SPOT
B1500CMM3 = constants.CMM.Mode.COMPLIANCE_SIDE #COMPLIANCE_SIDE, FORCE_SIDE, CURRENT, VOLTAGE, CURRENT_AND_VOLTAGE are possible, best option to be determined
B1500Filt3 = False #Default is False, other option is True

# B1500 Settings -- SMU4 Specific
VS_SMU4 = 0.5 # Source bias for SMU 1 in volts for gate sweeps
B1500ICOM4 = 1e-3 #Compliance current in amps
B1500VMR4 = constants.VMeasRange.FIX_2V #Ideally AUTO, FIX_2V, FIX_0V5 or FIX_0V2 -- other values in constants but know what you're doing first
B1500IMR4 = constants.IMeasRange.AUTO #Ideally AUTO or MIN_100nA -- other values in constants but know what you're doing first
B1500VOR4 = constants.VOutputRange.AUTO #AUTO seems only good selection here as the MIN settings cap downwards not upward
B1500MCR4 = constants.IOutputRange.AUTO #Leave as AUTO
B1500MM4 = constants.MM.Mode.SPOT #Can't see any reasons to change from SPOT
B1500CMM4 = constants.CMM.Mode.COMPLIANCE_SIDE #COMPLIANCE_SIDE, FORCE_SIDE, CURRENT, VOLTAGE, CURRENT_AND_VOLTAGE are possible, best option to be determined
B1500Filt4 = False #Default is False, other option is True

# K2401 Settings -- Gate Electrode Specific
K2401sourceRange = 1
K2401senseRange = 1.05e-6
K2401compl = 1.0E-8