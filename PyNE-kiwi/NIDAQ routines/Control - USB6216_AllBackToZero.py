"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Adam Micolich

NIDAQ USB-6216 program that simply drives outputs to zero and stops. Designed for recovery
from an emergency (ctrl-c) stop of another program. Can be used also for quick spin-up.
"""

import os
os.chdir('..\\')
from Imports import *

GateGoTo = 0.0
SourceGoTo = 0.0

# 1) Initialize Instruments
#---- NIDAQ Output Port for Source --------------
daqout_S = USB6216Out(0)
daqout_S.setOptions({
    "feedBack":"Int",
    "extPort":6, # Can be any number 0-7 if in 'Int'  
    "scaleFactor":1
})

#---- NIDAQ Output Port for Gate --------------
daqout_G = USB6216Out(1)
daqout_G.setOptions({
    "feedBack":"Int",
    "extPort":7, # Can be any number 0-7 if in 'Int'  
    "scaleFactor":1
})

daqout_G.goTo(GateGoTo,stepsize=0.01,delay=0.01)
daqout_S.goTo(SourceGoTo,stepsize=0.01,delay=0.01)