"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Jakob Seidl
"""

from collections import Iterable
# Checks if val is iterable, but not a string

def isIterable(val):
    return isinstance(val, Iterable) and not isinstance(val, str)

def flatten(iterable):
    flattenedList = []
    for e1 in iterable:
        if isIterable(e1):
            for e2 in e1:
                flattenedList.append(e2)
        else:
            flattenedList.append(e1)
    return flattenedList

# Converts one element lists to just the element itself (e.g., ["a"] -> "a"),
# while leaving everything else untouched. This way we can have an "intuitive"
# format for options that only take a single argument, but still preserve
# support for multiple argument options
def unwrap(args):
    if isIterable(args) and len(args) == 1:
        return args[0]
    return args

class Instrument(object):
    # This contains all the available options an instrument has. This is
    # populated automatically for each individual instrument class with the
    # @addOptionSetter/Getter and @enableOptions decorators defined later in the file.
    # The key is the option name, while the values are: {
    #     "order": The relative order the option should be set in, when setting
    #              multiple options at once (only for _optionSetters)
    #     "fn": The actual class member function that sets the option
    # }
    _optionSetters = {}
    _optionGetters = {}

    def __init__(self):
        self._options = {}

    def get(self, option, forceCached = False):
        if not forceCached and option in type(self)._optionGetters:
            return unwrap(self._optionGetters[option]["fn"](self))
        elif option in type(self)._optionSetters:
            return unwrap(self._options[option])
        else:
            raise ValueError(
                "{} is not a valid option to get. {} are available".format(
                    option,
                    set(list(type(self)._optionSetters.keys()) + list(type(self)._optionGetters.keys()))
                )
            )

    def set(self, option, *args):
        if not option in type(self)._optionSetters:
            raise ValueError("{} is not a valid option. {} are available".format(option, list(type(self)._optionSetters.keys())))

        type(self)._optionSetters[option]["fn"](self, *args)
        self._options[option] = args

    def getOptions(self):
        options = self._options.copy()
        for option, args in list(options.items()):
            options[option] = unwrap(args)
        for option in type(self)._optionGetters:
            options[option] = self.get(option)
        return options

    def setOptions(self, options):
        # First check all options exist
        options = list(options.items())
        for option, _ in options:
            if not option in type(self)._optionSetters:
                raise ValueError("{} is not a valid option. {} are available".format(option, list(type(self)._optionSetters.keys())))

        # Sort the options so they're set in the correct order
        options = sorted(options, key = lambda option: type(self)._optionSetters[option[0]]["order"])

        # Actually set the options
        for option, args in options:
            if not isIterable(args):
                args = (args,)
            self.set(option, *args)

# Having a "totalOptions" variable lets us assign a total order to the options,
# by giving each option an unique number. This way we can ensure an order to
# setting the options when setting multiple options at once, since some options
# might require being set before others
            
totalOptions = 0
def addOptionSetter(name):
    def decorator(optionSetter):
        global totalOptions
        totalOptions += 1
        optionSetter.optionInfo = {"name": name, "order": totalOptions}
        return optionSetter
    return decorator

def addOptionGetter(name):
    def decorator(optionGetter):
        optionGetter.optionInfo = {"name": name, "isGetter": True}
        return optionGetter
    return decorator

# Since we can't access the class until it's finished being created, we have to
# have a separate decorator over the entire class, so we can then set the
# _optionsSetters property with the available options
    
def enableOptions(instrument):
    instrument._optionSetters = {}
    instrument._optionGetters = {}

    for option in list(instrument.__dict__.values()):
        if not hasattr(option, "optionInfo"):
            continue
        info = option.optionInfo
        if "isGetter" in info:
            instrument._optionGetters[info["name"]] = {"fn": option}
        else:
            instrument._optionSetters[info["name"]] = {"order": info["order"], "fn": option}

    return instrument

def closeInstruments(instrumentList1,instrumentList2=None):
    if instrumentList2 != None:
        List = flatten([instrumentList1,instrumentList2])
    else: List = instrumentList1

    for instrument in List:
        try:
            instrument.close()
        except:
            continue
        
# Defining a new instrument
# ------------------------
# import Instrument
#
# @Instrument.enableOptions # Actually populate _optionSetters
# class Keithley2401(Instrument.Instrument):
#    def __init__(self, address):
#        super(Keithley2401, self).__init__() # Call Instrument's __init__
#        # Other initialisation stuff, like connecting to the instrument
#
#    @Instrument.addOptionSetter("beepEnable")
#    def _setBeepEnable(self, enable):
#        # Actually enable or disable beep here
#
#    @Instrument.addOptionSetter("option2")
#    def _setOption2(self, value):
#        # etc
#
# # By defining "beepEnable" before "option2", "beepEnable" is guaranteed to be
# # set before "option2", when both options are passed into setOptions().
# # Basically, the order the @addOption appear in define the order they are set
# # when they appear in setOptions()

# Saving/loading options
# ----------------------
# How options are saved/loaded is up to the user (though we could add a default
# way of doing so to sweeper.defaultWriter)
#
# For example, we could save two instruments' options as JSON:
# import json
# options = open("options.json", "w")
# options.write(json.dumps(
#     {"keithley": keithley.getOptions(), "lockin": lockin.getOptions()},
#     indent = 4, sort_keys = True
# ))
#
# To load the values back:
# import json
# options = open("options.json", "r")
# options = json.loads(options.read())
# keithley.setOptions(options["keithley"])
# lockin.setOptions(options["lockin"])