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
points = [(46, 10), (291, 6), (287, 235), (52, 228)]    # for QVGA
#points = [(24, 4), (145, 4), (142, 118), (25, 114)]     # for QQVGA


mouse_filter = (0, 26, -35, 42, -32, 43)
black_filter = (0, 30, -128, 127, -128, 127)
debug_black_filter = (0, 38, -128, 8, -128, 127)
red_filter = (0, 100, 25, 127, -128, 127)

delay = 20
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
    chips = img.find_blobs([red_filter], area_threshold=10, merge=True)

    chip_x, chip_y = -1, -1
    for i in range(len(chips)):
        if 200 >= chips[i].area() >= 10:
            chip_x, chip_y = chips[i].cx(), chips[i].cy()
            break

    mouse_x, mouse_y = -1, -1
    for i in range(len(mouse)):
        if 1500 >= mouse[i].area() >= 300:
            mouse_x, mouse_y = mouse[i].cx(), mouse[i].cy()
            break
        # if 200 >= mouse[i].area() >= 10:
        #     mouse_x, mouse_y = mouse[i].cx(), mouse[i].cy()
        #     break

    #print(f'chip: {chip_x}, {chip_y} | mouse: {mouse_x}, {mouse_y}')

    vcp.write(f's{mouse_x},{mouse_y},{chip_x},{chip_y}e')


