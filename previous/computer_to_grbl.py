"""
Send G-code to gantry from computer.
This is a modified version of https://github.com/grbl/grbl/blob/master/doc/script/simple_stream.py.
"""
# Go to folder
# pip install -e .
#%%
import serial
import serial.tools.list_ports
import numpy as np
import time
import sys
import tqdm.auto as tqdm
from tests import trajectory as tj

# f = tj.from_file(r'C:\git\mouse-tracker\tests\tests\linear.gcode')
# f = tj.variable_feed_circle(30, 100, 20, 1)
# f, feeds = tj.fake_mouse('B1', 100, 1)

for port, desc, hwid in sorted(serial.tools.list_ports.comports()):
    print("{}: {} [{}]".format(port, desc, hwid))

# Wake up grbl
s = serial.Serial('COM5',115200)
s.write(bytes('\r\n\r\n', 'UTF-8'))
time.sleep(5)   # Wait for grbl to initialize
s.flushInput()  # Flush startup text in serial input

# Set parameters
# Speed(s) to move, in/min
FEED_RATES = 120


# Number of cycles
CYC = 30

# Square
FILLET_RADIUS = 0.4
SIDE_LENGTH=2.5

# f = tj.variable_feed_filleted_square(
#      SIDE_LENGTH, FEED_RATES, FILLET_RADIUS, CYC)


# Lissajous
f = tj.variable_feed_lissajous(2, 3, np.pi/2,  120, CYC)

for line in tqdm.tqdm(f):
    l = line.strip() # Strip all EOL characters for consistency
    # print('Sending: ' + l)
    s.write(bytes(l + '\n', 'UTF-8')) # Send g-code block to grbl
    grbl_out = str(s.readline()) # Wait for grbl response with carriage return
    print(' : ' + grbl_out.strip())



# Close serial port
s.close()
#%%
# For when you interrupt
s.close()

# %%
import serial.tools.list_ports
ports = serial.tools.list_ports.comports()

for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))

#%%


# Constants
from math import sin, pi

L = 100.0       # Length in the X direction
A = 5.0         # Amplitude of the sine function
f1 = 0.01       # Start frequency in Hz
f2 = 0.1        # End frequency in Hz
deltaX = 0.1    # Step size

gcode_output = tj.chirp(L, A, f1, f2, deltaX)

for line in gcode_output:
    l = line.strip() # Strip all EOL characters for consistency
    print('Sending: ' + l)
    s.write(bytes(l + '\n', 'UTF-8')) # Send g-code block to grbl
    grbl_out = str(s.readline()) # Wait for grbl response with carriage return
    print(' : ' + grbl_out.strip())

# %%
