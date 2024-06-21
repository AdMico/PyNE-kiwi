"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Jakob Seidl

This module's entire purpose is to load all required modules in the user's actual control script.
This is then done via 'from Imports import *'. The star imports all functions defined in various modules into one namespace so that you can call any function directly.
"""

import numpy as np
import time
import json
from itertools import product
#import matplotlib as mpl #Deactivated for V3.1 by APM due to conflicts -- 10Oct19
#mpl.use('TkAgg') #Deactivated for V3.1 by APM due to conflicts -- 10Oct19
import matplotlib.pyplot as plt

from SweepFunction import sweepAndSave
from Instrument import closeInstruments
from GUIs import fileDialog, initialize
from Keithley2401 import Keithley2401
from SRS830 import SRS830
from Electrometer import Keithley6517A
from YokogawaGS200 import YokogawaGS200
from TimeMeas import TimeMeas
from AttoReader import AttoReader
from USB6216In import USB6216In
from USB6216Out import USB6216Out
from pHMeter import pHMeter
