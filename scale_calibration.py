from __future__ import print_function
import serial
# import keyboard
import time
import pigpio
import os
import pandas as pd
import statistics as stats
import sys
from datetime import datetime
import numpy as np
import qwiic_tca9548a
import qwiic_rfid
import PyNAU7802
import smbus2

#init scale
# Create the bus
bus = smbus2.SMBus(1)
# Create the scale and initialize it.. hardware defined address is 0x2A. mux required for multiple
scale = PyNAU7802.NAU7802()
if scale.begin(bus):
    print("Scale connected!\n")
else:
    print("Can't find the scale, exiting ...\n")
    exit()
# Calculate the zero offset
print("Calculating scale zero offset...")
scale.calculateZeroOffset()
print("The zero offset is : {0}\n".format(scale.getZeroOffset()))
print("Put a known mass on the scale.")
cal = float(input("Mass in kg? "))
# Calculate the calibration factor
print("Calculating the calibration factor...")
scale.calculateCalibrationFactor(cal)
print("The calibration factor is : {0:0.3f}\n".format(scale.getCalibrationFactor()))

n=scale.getWeight() * 1000
print("Acquired Mass is {0:0.3f} g".format(n))