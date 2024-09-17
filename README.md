# PyNE-kiwi v1.0.0 (Updated 17SEP24 APM)

**Written by:** Adam Micolich

**Purpose:** Software for electronic measurements for the insect olfactory receptors project (NZ Royal Society Marsden Fund 21-VUW-122 & Australian Research Council DP210102085).

*Developed and tested using Python 3.12 and PyCharm 2024.2.1*

## Structure

Top level has two folders -- *code* and *data*. The *code* folder has all the active software at the top level. There are two sub-folders -- *debugging* and *purgatory*. The *debugging* folder has pieces of code that are used for debugging and connection checking for the various bits of hardware used in the measurements. The *purgatory* folder has pieces of old code that will be deleted in future releases but are kept for now just in case they are useful. The *data* folder is where the software will place experimental data, it will put these in automatically created folders with naming based on the global measurement ID (GMID) and the date/time. Files inside these subfolders will be automatically named accordingly, based also on the corresponding device measured.

## Program Components

There are three main functional components `Gate Sweep.py`, `Time Sweep.py` and `Basic Hardware Test.py` , everything else is a subroutine.

The software runs an electrical measurement system consisting of a Keysight B1500 SPA, a Keysight B2201 switch mainframe, a Keithley 2401 SMU and some custom electronics that measure devices that each contain eight liquid-gated carbon nanotube field-effect transistors.

`Gate Sweep.py`: The Main GUI for running gate sweeps on the electrical setup. There are presently 5 buttons. The first is *start odd sweep*, which starts a pair of sweeps, one forward and one back again, for just the odd devices on the chip (i.e., 1, 3, 5 & 7). The gate voltage range, step size and settling time are specified in `config.py` (see more below). The second is *start even sweep*, which does the same for the even devices on the chip (i.e., 2, 4, 6 & 8). The third is *start odd+even sweep*, which just runs the odd and even sweeps above sequentially. These three options are there for test purposes in this version and will be deprecated in a future release. The fourth button is *start switched sweep*, which runs a single sweep, forward and then backward, that alternates between the odd and even configurations at each voltage step using the B2201 and custom electronics. This is a permanent feature, with additional 'switched sweeps' to be added in future updates. The fifth and final button *End GateSweeper* brings the instruments back to a safe state, closes the GUI and increments the GMID so that data from future runs ends up in its own new folder.

`Time Sweep.py`: The Main GUI for running time sweeps on the electrical setup. There are presently 3 buttons. The first is *start time sweep*, which starts a time sweep with data taken at the increment specified in `Config.py`. The device connection alternates between the odd and even configurations at each time step using the B2201 and custom electronics. This is a permanent feature, with additional 'switched sweeps' to be added in future updates. The second button *stop time sweep* button brings the time sweep to an end at the end of the current iteration. The third button *End TimeSweeper* brings the instruments back to a safe state, closes the GUI and increments the GMID so that data from future runs ends up in its own new folder. Each time sweep has a maximum duration set in `Config.py`, currently this value is set to 5 hours. The sweep (but not the GUI itself) will terminate automatically once the maximum duration is reached to prevent array over-run and GUI crash.

Both of these programs can be run for multiple sweeps in a single run instance of the GUI, which opens a folder of the form `<date>_<GMID>`, where a text based log file and comma separated value (.csv) data files are stored. Each csv data file is given a name containing the GMID and the sweep number in the series used for that instance of the GUI. If closed correctly, using the end button, each new instance will open a new folder as the GMID is incremented in the finalisation routine for the GUI. However, if exit from the GUI occurs via other means, e.g., crash, ctrl+c, etc, care should be taken as the GMID will not be updated and the next run of the GUI will use the same folder and progressively overwrite the files already there.


`Basic Hardware Test.py`: This is a non-GUI basic test of the hardware configuration for test/debug purposes. It has been kept at the top level (not placed in `/debugging`) for now but will be moved in a later update. The software reports only at the PyCharm run terminal showing hardware connection details (B1500, B2201, K2401) and simple *I-V* traces at 0.0V, 0.1V, 0.2V and 0.3V for all four B1500 SMUs under all four standard B2201 configurations (odd, even, ground and clear). The K2401 is active and held at 1V during this. At the end of the four *I-V* sweeps the instruments are all returned to a safe state and the software ends. If the 100kOhm test chip is in place, a current corresponding to this resistance (i.e., 1uA per 0.1V) should be obtained for all four SMU channels in the even and odd configurations (but not clear and ground). There is an option at the bottom of `Config.py` that enables the *I-V* sweep to be slowed down so that SMU output tests can be performed (by connecting a multimeter to the corresponding port on the back of the B2201). The default is the 'fast' option, as it enables a quick hardware test (takes about 20 seconds start to finish) at any point it is needed. 

### Subroutines

`Config.py`: This contains all the key configuration details for your instance of the software. The individual parameters are explained in the comments. The most crucial one to note is the `PiBox` parameter. You need to ensure this matches the Raspberry Pi you are using in your hardware set-up, otherwise when you run the GUI, all the multiplexer commands will be going to another set-up, which may be running at the time. This file also contains the key settings for `Gate Sweep.py` and `Time Sweep.py`, along with important default hardware settings (e.g., range values, compliance settings, etc). These are also detailed in the comments for the program.

`GlobalMeasID.py`: This contains all the code for setting, reading and incrementing the Global Measurement ID (GMID) used to trace data files to hardware-setup and owner. A user will only need to interact with this program to initialise the GMID for their setup. This is done at the `initID` function by setting the desired prefix (ideally 2 letter string, but can be more) and ID number. If this file is run (and the Reset switch at the top = 1) then the GMID will reinitialise to the value you set in `initID`. Can be useful to leave Reset = 0 once you've initialised the first time, just to prevent accidental loss of GMID value, but it ships with Reset = 1 as that's the most common usage case.

`GlobalMeasIDBinary`: Binary file containing the GMID. Automatically incremented by the software via routines in `GlobalMeasID.py`.

`Imports.py`: Master import file to simplify code. Doesn't need edits unless you add new library calls to the software (if you do, please update `requirements.txt` accordingly).

`B1500.py`: Contains the software for interfacing with the Keysight B1500 to set/get voltages and get current values amongst other things. Uses the Keysight B1500 instrument from `qcodes` library for hardware interfacing.

`B2201.py`: Contains the software for interfacing with the Keysight B2201 to set the various source side switch configurations. This instrument is engaged using conventional SCPI command set over GPIB.

`K2401.py`: Contains the software for interfacing with the Keithley K2401. Contains old instrument architecture from `PyNE-probe` software and will be cleaned up in a future release.

`Pi_control.py`: This controls all the hardware interactions with the Raspberry Pi that controls the drain relay system in the custom electronics. This includes setting the respective IP address, and switching the relays to correctly connect the measure circuit to a given set of device. Further details of the custom electronics for this project can be found in a future GitHub repository for the hardware design. Instance can be run as main to enable direct debugging control of the multiplexers (i.e., test that they switch correctly), see bottom of code for details.

`stop.txt`: Software stop button, that is currently used in `Time Sweep.py`, and will be used in future as an 'abort sweep' button in `Gate Sweep.py`.

`Instrument.py`: This appears to be legacy from PyNE-probe, likely to be deprecated in a future version of PyNE-kiwi.

## Planned updates for next version

- Deprecate `Instrument.py` if none of its functions are used (i.e., is true legacy).
- Implement 'abort sweep' button in `Gate Sweep.py`.
- Clean up ilocs in `Gate Sweep.py` and implement gate voltage arrays as pandas dataframes.
- Clean up the B1500, B2201 and K2401 instrument programs to simplify the code to essentials.
- Implement 'switched' sweep set with a B1500 SMU each on the source and the drain.
- Add a feature to add short notes to the log file.
- Add a live graph of the current sweep for the GUIs in `Gate Sweep.py` and `Time Sweep.py`.
- Clean up file structure (e.g. empty purgatory).
- APM to create github repo for the hardware and link to it here for context.

## Installation

APM currently runs this software in PyCharm, you may need to change accordingly for use in another IDE.

1. In PyCharm set up a new Python project called `PyNE-kiwi`(or similar) and ensure it is configured as Project venv and using your Python 3.12 interpreter.
2. Navigate using GitBash to the folder where the project is (typically `C:/Users/.../PyCharmProjects/PyNE-kiwi/`).
3. Initialise the folder using `git init`.
4. (If needed) Switch the default branch from `master` to `main` using `git branch -m master main`, as an option, you might also set this as a default using `git config --global init.defaultBranch main`.
5. Connect to the PyNE-kiwi repo using `git remote add origin https://github.com/AdMico/PyNE-kiwi/`.
6. Pull the repo using `git pull origin main`. Ensure you use the main branch for functional software, other branches are for development only.
7. Install the requirements for the package as specified in `requirements.txt` (If you are using terminal, you want to `pip install` the following: `setuptools`, `wheel`, `numpy`, `matplotlib`, `scipy`, `pyvisa`, `visa`, `deprecation`, `pandas`, `pandastable`, `easygui`, `colorzero`, `gpiozero`, `pigpio`, `qcodes`, `pyvisa-py` and `pyqt5`. This install set will auto-include dependencies to fully cover `requirements.txt`. As part of this you may be invited to update `pip`, feel free to do so.
8. Go to `Config.py` file and adjust the sweep and hardware parameter settings as needed.
9. Go to `GlobalMeasID.py` and initialise the GMID for your particular instance.
10. You are ready to run, and starting with a run of `Basic Hardware Test.py` is a smart place to start to ensure the hardware is working properly and the other programs won't crash for hardware issues. After this, you probably only need to use `Gate Sweep.py` and `Time Sweep.py` for your measurements.

Further information in the repo for the electrical set-up, which is coming in the near future.