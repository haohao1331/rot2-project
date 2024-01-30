import sensor
import omv
import utils
import time

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=2000)

omv.disable_fb(True)

log = utils.Log()
gantry = utils.Gantry()

red_threshold = [(0, 100, 50, 127, -128, 127)]
green_threshold = [(0, 100, -128, -16, -128, 127)]
roi = [116, 57, 23, 44]

delay = 20
speed = 120
distance = 0.3
prev = time.ticks_ms()
prev_direction = None

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
        print(f'{now} : red')
        cur_direction = 0
        if cur_direction != prev_direction:
            gantry.send(f'G01 X0 Y-{distance} F{speed}')
        # gantry.send('G01 X0 Y-{distance} F60')
    else:
        print(f'{now} : green')
        cur_direction = 1
        if cur_direction != prev_direction:
            gantry.send(f'G01 X0 Y{distance} F{speed}')
        # gantry.send('G01 X0 Y{distance} F60')

    #print('')

