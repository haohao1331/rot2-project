import sensor
import omv
import time
import utils
import pyb

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time=2000)

sensor.set_contrast(3)
sensor.set_saturation(3)
sensor.set_brightness(0)

omv.disable_fb(True)
utils.blink_led(3)
pyb.delay(1000)


# top left, top right, bottom right, bottom left
points = [(46, 6), (293, 10), (286, 240), (50, 226)]    # for QVGA
#points = [(24, 4), (145, 4), (142, 118), (25, 114)]     # for QQVGA

black_filter = (0, 30, -128, 127, -128, 127)
red_filter = (0, 100, 29, 127, -128, 127)

delay = 20
max_speed = 4000
distance = 0.3
prev = time.ticks_ms()
prev_direction = None

log = utils.Log()

vcp = utils.VCP(log)
utils.blink_led(3)


while True:
    now = time.ticks_ms()
    if time.ticks_diff(now, prev) < delay:
        continue
    diff = time.ticks_diff(now, prev)
    img = sensor.snapshot().lens_corr(1.5).rotation_corr(corners=points)

    chips = img.find_blobs([black_filter])
    reds = img.find_blobs([red_filter])

    if len(chips) > 0:
        chip_x, chip_y = chips[0].cx(), chips[0].cy()
    else:
        chip_x, chip_y = -1, -1

    if len(reds) > 0:
        red_x, red_y = reds[0].cx(), reds[0].cy()
    else:
        red_x, red_y = -1, -1

    #print(f'chip: {chip_x}, {chip_y} | red: {red_x}, {red_y}')

    vcp.write(f's{chip_x},{chip_y},{red_x},{red_y}e')


