"""
Brought to PyNE-kiwi v1.0.0 on Fri Aug 30 2024 by APM

@developers: Adam Micolich

This informs various parts of the software about aspects of your bench setup. Edit as needed for your setup.
"""

## IMPORTANT -- You need to set PiBox correctly before you first use the software to avoid controlling someone else's hardware by mistake -- see main README.md file
# Information about which Raspberry Pi you are using (MeasureOne, MeasureTwo, etc)
# Details for the various Pis are in Pi_control.py
PiBox = 'MeasureThree'

# Code Diagnostics Switch
# Use "Verbose" for information prints on and "Silent" to suppress.
Diags = "Verbose"

# Settings for Measurement Biases -- Update later APM 30AUG24
#VSource = float(0.5)
#VGate = float(0.0)

# AssayRun settingsm -- Update later APM 30AUG24
#basePath = '../data'