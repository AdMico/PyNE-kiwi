"""
Brought to PyNE-kiwi v1.0.0 on Mon Sep 2 2024 by APM

@developers: Adam Micolich

@author: Adam Micolich

A set of higher level routines for B1500 -- Deprecated 10SEP24 APM remove in next major update
"""

from Config import B1500AutoZero,B1500ADCSet,B1500NPLC
from Config import B1500MM1,B1500MM2,B1500MM3,B1500MM4
from Config import B1500CMM1,B1500CMM2,B1500CMM3,B1500CMM4
from Config import B1500VOR1,B1500VOR2,B1500VOR3,B1500VOR4
from Config import B1500ICOM1,B1500ICOM2,B1500ICOM3,B1500ICOM4
from Config import B1500MCR1,B1500MCR2,B1500MCR3,B1500MCR4
from Config import B1500Filt1,B1500Filt2,B1500Filt3,B1500Filt4
from Config import B1500VMR1,B1500VMR2,B1500VMR3,B1500VMR4
from Config import B1500IMR1,B1500IMR2,B1500IMR3,B1500IMR4
from qcodes.instrument_drivers.Keysight import KeysightB1500

#B1500 = KeysightB1500("SPA", address="USB0::0x0957::0x0001::0001::INSTR")

def B1500_init():
    # Hook up instrument communications connection
    B1500 = KeysightB1500("SPA", address="USB0::0x0957::0x0001::0001::INSTR")
    # B1500 AutoZero
    B1500.autozero_enabled(B1500AutoZero)
    # B1500 Measurement Mode
    B1500.smu1.measurement_mode(B1500MM1)
    B1500.smu2.measurement_mode(B1500MM2)
    B1500.smu3.measurement_mode(B1500MM3)
    B1500.smu4.measurement_mode(B1500MM4)
    # B1500 Compliance Measure Mode
    B1500.smu1.measurement_operation_mode(B1500CMM1)
    B1500.smu2.measurement_operation_mode(B1500CMM2)
    B1500.smu3.measurement_operation_mode(B1500CMM3)
    B1500.smu4.measurement_operation_mode(B1500CMM4)
    # B1500 Source Configuration
    B1500.smu1.source_config(output_range=B1500VOR1,compliance=B1500ICOM1,compl_polarity=None,min_compliance_range=B1500MCR1)
    B1500.smu2.source_config(output_range=B1500VOR2,compliance=B1500ICOM2,compl_polarity=None,min_compliance_range=B1500MCR2)
    B1500.smu3.source_config(output_range=B1500VOR3,compliance=B1500ICOM3,compl_polarity=None,min_compliance_range=B1500MCR3)
    B1500.smu4.source_config(output_range=B1500VOR4,compliance=B1500ICOM4,compl_polarity=None,min_compliance_range=B1500MCR4)
    # B1500 Voltage Measure Range Setting
    B1500.smu1.v_measure_range_config(v_measure_range=B1500VMR1)
    B1500.smu2.v_measure_range_config(v_measure_range=B1500VMR2)
    B1500.smu3.v_measure_range_config(v_measure_range=B1500VMR3)
    B1500.smu4.v_measure_range_config(v_measure_range=B1500VMR4)
    # B1500 Current Measure Range Setting
    B1500.smu1.i_measure_range_config(i_measure_range=B1500IMR1)
    B1500.smu2.i_measure_range_config(i_measure_range=B1500IMR2)
    B1500.smu3.i_measure_range_config(i_measure_range=B1500IMR3)
    B1500.smu4.i_measure_range_config(i_measure_range=B1500IMR4)
    # B1500 Filter Settings
    B1500.smu1.enable_filter(B1500Filt1)
    B1500.smu2.enable_filter(B1500Filt2)
    B1500.smu3.enable_filter(B1500Filt3)
    B1500.smu4.enable_filter(B1500Filt4)
    # B1500 Analog-Digital Converter Settings
    if B1500ADCSet == "HighSpeed":
        B1500.use_nplc_for_high_speed_adc(n=B1500NPLC)
        B1500.smu1.use_high_speed_adc()
        B1500.smu2.use_high_speed_adc()
        B1500.smu3.use_high_speed_adc()
        B1500.smu4.use_high_speed_adc()
    elif B1500ADCSet == "HighRes":
        B1500.use_nplc_for_high_resolution_adc(n=B1500NPLC)
        B1500.smu1.use_high_resolution_adc()
        B1500.smu2.use_high_resolution_adc()
        B1500.smu3.use_high_resolution_adc()
        B1500.smu4.use_high_resolution_adc()
    # Enable all four SMUs -- Moved to before settings of zero due to gate sweep software error 10SEP24 APM
    B1500.smu1.enable_outputs()
    B1500.smu2.enable_outputs()
    B1500.smu3.enable_outputs()
    B1500.smu4.enable_outputs()
    # Ensure all four SMUs are zeroed
    B1500.smu1.voltage(0.0)
    B1500.smu2.voltage(0.0)
    B1500.smu3.voltage(0.0)
    B1500.smu4.voltage(0.0)
