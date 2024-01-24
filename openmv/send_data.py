import omv
import sensor
import struct
import pyb
import time

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=2000)

omv.disable_fb(True)

class Log():
    def __init__(self) -> None:
        self.log = open(f'log{time.time()}.txt', 'w+')
        self.write('log opened\n')

    def write(self, s):
        self.log.write(s)

    def flush(self):
        self.log.flush()

    def close(self):
        self.log.close()

def blink_led(a):
    led = pyb.LED(a)
    led.on()
    pyb.delay(200)
    led.off()
    return

log = Log()

class VCP():
    def __init__(self) -> None:
        #for i in range(100):
            #try:
                #self.vcp = pyb.USB_VCP(i)
                #assert self.vcp.isconnected()
                #log.write(f'vcp {i} created\n')
                #break
            #except:
                #log.write(f'vcp {i} failed\n')
        self.vcp = pyb.USB_VCP(0)
        log.write('vcp created\n')
        # assert self.vcp.isconnected() # for some reason this simply doesn't work without the IDE
        # log.write('vcp connected\n')

    def write(self, buf):
        self.vcp.write(buf)
        log.write(f'wrote {buf}\n')
        log.flush()

blink_led(3)
pyb.delay(1000)

vcp = VCP()

blink_led(3)
pyb.delay(1000)

red_threshold = [(0, 100, 50, 127, -128, 127)]
green_threshold = [(0, 100, -128, -16, -128, 127)]
roi = [116, 57, 23, 44]

delay = 20
prev = time.ticks_ms()

while True:
    now = time.ticks_ms()
    if time.ticks_diff(now, prev) < delay:
        continue
    diff = time.ticks_diff(now, prev)
    prev = now
    img = sensor.snapshot()
    red_blobs = img.find_blobs(red_threshold, roi=roi)
    #green_blobs = img.find_blobs(green_threshold, roi=roi)
    #print(f'red: {len(red_blobs)}')
    if len(red_blobs) > 0:
        vcp.write(f's{diff} : 1e')
    else:
        vcp.write(f's{diff} : 0e')

    #print('')
