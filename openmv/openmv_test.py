import sensor, image, time, mjpeg, math
import time
import pyb
from pyb import UART
from machine import Pin, Signal

class GcodeStreamer(UART):
    def wakeup(self):
        self.write(bytes('\r\n\r\n', 'UTF-8'))
        time.sleep(2)   # Wait for grbl to initialize
        self.read()
        blink_led(2)
        self.read()
        blink_led(3)
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

def wakeup():
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time = 2000)
    sensor.set_auto_gain(False) # must be turned off for color tracking
    sensor.set_auto_whitebal(False) # must be turned off for color tracking
    return

def blink_led(a):
    led = pyb.LED(a)
    led.on()
    pyb.delay(1000)
    led.off()
    return

def setup(max_rate, accel):
    # setup sensor
    wakeup()

    # initialize grbl
    uart = GcodeStreamer(3, 115200)
    uart.wakeup()
    uart.send_gcode('G17 G21 G90') # XY plane selection, programming in millimeters (mm), absolute coordinates
    uart.send_gcode('$110=' + str(max_rate))
    uart.send_gcode('$111=' + str(max_rate))
    uart.send_gcode('$120=' + str(accel))
    uart.send_gcode('$121=' + str(accel))
    return uart

def main():
    # wakeup()
    # pyb.delay(1000)
    blink_led(1)

    uart = GcodeStreamer(3, 115200)
    uart.wakeup()

    distance = 0.5
    g = []
    # g.append('G17 G20 G90 G94') # inches
    # g.append(f'G01 X0 Y0 F60')
    # g.append(f'G01 X{distance} Y0 F60')
    # g.append(f'G01 X0 Y0 F60')
    # g.append(f'G01 X0 Y{distance} F60')
    # g.append(f'G01 X0 Y0 F60')
    # g.append(f'G01 X-{distance} Y0 F60')
    # g.append(f'G01 X0 Y0 F60')
    # g.append(f'G01 X0 Y-{distance} F60')
    # g.append(f'G01 X0 Y0 F60')
    # g.append('$$')

    msg = '$$'
    print('Sending: ' + msg)
    uart.send_gcode(msg + '\n') # Send g-code block to grbl
    for i in range(10):
        grbl_out = str(uart.readline())
        print(' : ' + grbl_out.strip())
    # for msg in g:
    #     print('Sending: ' + msg)
    #     uart.send_gcode(msg + '\n') # Send g-code block to grbl
    #     grbl_out = str(uart.readline())
    #     print(' : ' + grbl_out.strip())


main()
