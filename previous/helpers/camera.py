# Helper functions for interacting with OpenMV camera

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
