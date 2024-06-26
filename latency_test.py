# a crude version of the latency test, where the entire image is sent
import io
from pathlib import Path
from time import perf_counter
from PIL import Image
import time
import numpy as np
from gantry import Gantry
from openmv import OpenMV
import cv2
from red_or_green import analyze_image_for_red_green


# output_dir = Path(r'C:\git\rot2-project\data\2024-01-15_camera_pics1')
delta = 1
div = 10    # this is so that delta and cur_pos stay as int
speed = 60
cur_pos = 0

gt = Gantry()
omv = OpenMV()

now = perf_counter()
a, b, c, d = 0, 0, 0, 0

while(True):
    now = perf_counter()
    print(f'\nwait: {(now - d)*1000}')

    img = omv.snapshot()
    if img is None:
        continue
    
    a = perf_counter()
    print(f'snapshot: {(a - now)*1000}')
    img = cv2.imdecode(np.frombuffer(img, dtype=np.uint8), -1)

    b = perf_counter()
    print(f'imdecode: {(b - a)*1000}')
    # print(type(img))


    dominant_color, red_count, green_count, mask_red, mask_green = analyze_image_for_red_green(img)

    c = perf_counter()
    print(f'analyze: {(c - b)*1000}')
    print(f'{dominant_color}')

    cur_pos += delta if dominant_color == 'red' else -delta

    gt.move_y(cur_pos / div, speed)
    d = perf_counter()
    print(f'move: {(d - c)*1000}')

    # if dominant_color == 'red':
    #     gt.move_x(distance, speed)
    # else:
    #     gt.move_x(-distance, speed)

    # img.save(output_dir / f'{now}.jpg')
    # np.save(output_dir / f'test.jpg', img)
    # break