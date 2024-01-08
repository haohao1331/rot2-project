import sensor, image, time, mjpeg
from pid import PID
import time
from pyb import UART

#from helpers.gc_streamer import GcodeStreamer
#import helpers.camera as cam


import sensor, image, math
from machine import Pin, Signal

def wakeup():
    sensor.reset()
    sensor.set_pixformat(sensor.RGB565)
    sensor.set_framesize(sensor.QVGA)
    sensor.skip_frames(time = 2000)
    sensor.set_auto_gain(False) # must be turned off for color tracking
    sensor.set_auto_whitebal(False) # must be turned off for color tracking
    return

def tracking(thresholds, pixels_threshold=200, area_threshold=200):
    img = sensor.snapshot()
    blobs = img.find_blobs(thresholds, pixels_threshold=pixels_threshold, area_threshold=area_threshold, merge=True)
    while len(blobs) == 0:
        blobs = img.find_blobs(thresholds, pixels_threshold=pixels_threshold, area_threshold=area_threshold, merge=True)
    blob = max(blobs, key = lambda x: x.compactness())    # from readout control>>100_fps_ir_led_tracking.py
    img.draw_rectangle(blob.rect())
    img.draw_cross(blob.cx(), blob.cy())
    cx, cy = blob.cx(), blob.cy() # measured output
    return cx, cy, img

def set_LED(pin):
    led1_pin = Pin(pin, Pin.OUT)
    led1 = Signal(led1_pin, invert=False)
    led1.on()
    return led1

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

def control_loop(params, uart):
    m = mjpeg.Mjpeg("example.mjpeg")
    led1 = set_LED('P7')

    clock = time.clock()
    thresholds = [(0, 24, -128, 127, -128, 127)]
    rx, ry = 160, 120 # desired output for QVGA
    sf = 1 # scaling factor = n unit length in grbl per pixel length

    # initialize pid
    pidx = PID(p=params[2], i=params[3], d=params[4], imax=90)
    pidy = PID(p=params[5], i=params[6], d=params[7], imax=90)

    params = [str(x) for x in params]
    fname = '_'.join(params)
    fname = '/' + fname + '.txt'
    f = open(fname, 'w')
    t = time.ticks_ms()

    fps = 0
    count = 0
    cum_err_x = 0
    cum_err_y = 0

    while(True):
        clock.tick()
        t0 = time.ticks_ms()
        [x0, y0, z0] = uart.get_mpos()
        # [x0, y0, z0] = uart.wait_until_Idle()
        cx, cy, img = tracking(thresholds, pixels_threshold=75, area_threshold=75)
        m.add_frame(img)

        # get control signal from error
        ux = pidx.get_pid(cx-rx, 1)
        uy = pidy.get_pid(ry-cy, 1)
        if abs(ux)<=60 and abs(uy)<=60 and (abs(ux)>=7.5 or abs(uy)>=7.5):
            uart.send_gcode('G00' + ' X' + str(x0+ux*sf) + ' Y' + str(y0+uy*sf))
        else:
            print(ux, uy)
        t1 = time.ticks_ms()
        f.write(str(cx-rx) + ' ' + str(cy-ry) + ' ' + str(time.ticks_diff(t1, t)) + ', ')
        cum_err_x += abs(cx-rx)
        cum_err_y += abs(cy-ry)
        # print(time.ticks_diff(t1, t0))
        fps += clock.fps()
        count += 1
        if time.ticks_diff(t1, t) >= 60*1000:
            break

    print(fps/count)
    f.close()
    led1.off()
    m.close(clock.fps())
    return cum_err_x, cum_err_y, count

def main():
    params = ['220524', 0, 1.2, 0, 0.05, 1.2, 0, 0.05, 8000, 750]
    uart = setup(params[8], params[9])
    control_loop(params, uart)

main()
