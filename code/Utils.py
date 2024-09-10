"""
Brought to PyNE-kiwi v1.0.0 on Mon Sep 2 2024 by APM

@developers: Adam Micolich

@author: Jakob Seidl

A bunch of useful utility functions for various handling tasks in PyNE -- Possible future deprecation 10SEP24 APM
"""

import numpy as np

def array(start,target,stepsize):
    """Helper function that creates single 1D array from start to stop. Used in targetArray()"""
    sign = 1 if (target>start) else -1
    sweepArray = np.arange(start,np.round(target+sign*stepsize,decimals=5),sign*stepsize) #The rounding makes function more predictable
    return sweepArray

def targetArray(targetList,stepsize):
    """Convenient way of creating a linearly-spaced array of floats of type np.ndarray().
    Parameters
    ----------
        targetList : list of target floats
                    E.g. [0.0,1.2,-0.3]
        stepsize : float
    Returns
    -------
        sweepArray : np.ndarray (1D)

    """
    arrayList = []
    stepsize = float(stepsize)
    for index, item in enumerate(targetList):
        if index == 0:
             pass
        elif index == 1:
            arrayList.append(array(targetList[index - 1], targetList[index], stepsize))
        elif (index > 1):
            arrayList.append(array(targetList[index-1],targetList[index],stepsize)[1:]) # slice [1:] in order to avoid duplicating numbers
    return np.concatenate((arrayList))