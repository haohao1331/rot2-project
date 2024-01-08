"""
Send G-code to gantry from OpenMV camera.
This is a modified version of https://github.com/grbl/grbl/blob/master/doc/script/simple_stream.py.
"""

import time
#from helpers.gc_streamer import GcodeStreamer
import time
from pyb import UART

class GcodeStreamer(UART):
    def wakeup(self):
        self.write(bytes('\r\n\r\n', 'UTF-8'))
        time.sleep(2)   # Wait for grbl to initialize
        self.read()
        return

    def send_gcode(self, l):
        l = l.strip() # Strip all EOL characters for consistency
        self.write(bytes(l + '\n', 'UTF-8')) # Send g-code block to grbl
        time.sleep_ms(50)
        grbl_out = str(self.read()) # Wait for grbl response with carriage return
        # print(' : ' + grbl_out.strip())
        return

    def get_mpos(self):
        self.write(bytes('?', 'UTF-8'))
        time.sleep_ms(50)
        m = str(self.read())
        m = str(m).split(':')[1].split(',')
        return [float(m) for m in m[:-1]]

    def wait_until_Idle(self):
        self.write(bytes('?', 'UTF-8'))
        time.sleep_ms(50)
        m = str(self.read())
        while(True):
            self.write(bytes('?', 'UTF-8'))
            time.sleep_ms(50)
            m = str(self.read())
            if 'Idle' in m: break

        m = str(m).split(':')[1].split(',')
        return [float(m) for m in m[:-1]]

uart = GcodeStreamer(3, 115200)
uart.wakeup()

f = ['G17 G20 G90', 'G00 X1 Y0', 'G00 X1 Y1']
for line in f:
    uart.send_gcode(line)

time.sleep(15)
uart.deinit()
