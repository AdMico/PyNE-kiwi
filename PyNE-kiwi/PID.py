"""
Brought to v4.0.0 on Tue May 09 2023 by APM

@author: Adam Micolich via various GitHub sources

Software PID controller system
"""

import time

class PID:
    "PID Controller"

    def __init__(self, P=0.2, I=0.0, D=0.0, current_time=None):
        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.current_time = current_time if current_time is not None else time.time()
        self.last_time = self.current_time
        self.reset()

    def reset(self):
        "Reset PID to starting configuration"
        self.SetPoint = 0.0
        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0
        self.output = 0.0

    def setKp(self, proportional_gain):
        "Proportional Gain"
        self.Kp = proportional_gain

    def setKi(self, integral_gain):
        "Integral Gain"
        self.Ki = integral_gain

    def setKd(self, derivative_gain):
        "Derivative Gain"
        self.Kd = derivative_gain
        
    def setSetPoint(self, set_point): 
        "Inputs the setpoint for the PID system"
        self.SetPoint = set_point

    def update(self, feedback_value, current_time=None):
        "Calculates PID value for given reference feedback using u(t) = K_p e(t) + K_i \int_{0}^{t} e(t)dt + K_d {de}/{dt}"

        error = self.SetPoint - feedback_value
        self.current_time = current_time if current_time is not None else time.time()
        delta_time = self.current_time - self.last_time
        delta_error = error - self.last_error

        self.PTerm = self.Kp * error
        self.ITerm += error * delta_time
        if delta_time > 0:
            self.DTerm = delta_error / delta_time
        else:
            self.DTerm = 0.0
        self.last_time = self.current_time
        self.last_error = error

        self.output = self.PTerm + (self.Ki * self.ITerm) + (self.Kd * self.DTerm)