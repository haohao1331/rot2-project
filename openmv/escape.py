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


mouse_filter = (0, 26, -35, 42, -32, 43)
black_filter = (0, 30, -128, 127, -128, 127)
red_filter = (0, 100, 25, 127, -128, 127)

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

    mouse = img.find_blobs([mouse_filter])
    chips = img.find_blobs([red_filter])

    if len(chips) > 0:
        chip_x, chip_y = chips[0].cx(), chips[0].cy()
    else:
        chip_x, chip_y = -1, -1

    if len(mouse) > 0:
        mouse_x, mouse_y = mouse[0].cx(), mouse[0].cy()
    else:
        mouse_x, mouse_y = -1, -1

    #print(f'chip: {chip_x}, {chip_y} | mouse: {mouse_x}, {mouse_y}')

    vcp.write(f's{mouse_x},{mouse_y},{chip_x},{chip_y}e')


